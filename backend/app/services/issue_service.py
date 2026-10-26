"""Create XRechnung and ZUGFeRD files from a confirmed draft. Files are not stored."""

from __future__ import annotations

import base64
from typing import List, Optional

from app.schemas.invoice import (
    InvoiceParseResponse,
    InvoiceTotals,
    LineItem,
    ParseStatus,
    PartyInfo,
    TaxBreakdown,
    ValidationIssue,
    ValidationStatus,
)
from app.schemas.issue import (
    IssueArtifact,
    IssueArtifactFormat,
    IssueBuildRequest,
    IssueBuildResponse,
    IssueDraftResponse,
)
from app.services.en16931_validator import ValidationResult, validate_invoice
from app.services.issue_draft import PreparedIssue, ReadyInvoice, SellerSeed, extract_draft_from_pdf, prepare_invoice
from app.services.issue_pdf import IssueEmbedError, embed_facturx
from app.services.issue_xml import CiiProfile, render_cii, safe_invoice_filename

_NOT_READY: str = (
    "Die E-Rechnung ist noch nicht freigegeben. "
    "Bitte die markierten Angaben korrigieren. Ein Download bleibt geschlossen, "
    "bis die KoSIT-Prüfung gültig abgeschlossen ist."
)
_READY: str = (
    "KoSIT hat die Datei als gültig abgeschlossen. "
    "Maßgeblich ist die XML, nicht das sichtbare PDF."
)


def draft_from_pdf(
    content: bytes,
    filename: str,
    seller: Optional[SellerSeed] = None,
) -> IssueDraftResponse:
    """Read text from a plain PDF into a draft the issuer still has to confirm."""
    return extract_draft_from_pdf(content, filename, seller=seller)


def build_issue(request: IssueBuildRequest, pdf_bytes: Optional[bytes]) -> IssueBuildResponse:
    """Validate the draft, render CII, and attach bytes only after a valid KoSIT run."""
    prepared: PreparedIssue = prepare_invoice(request.draft, confirmed=request.confirmed)
    if prepared.invoice is None:
        return IssueBuildResponse(ready=False, message=_NOT_READY, blocking_issues=prepared.blocking)

    invoice: ReadyInvoice = prepared.invoice
    artifacts: List[IssueArtifact] = [
        _xml_artifact(
            invoice=invoice,
            profile="xrechnung",
            artifact_format="xrechnung",
            media_type="application/xml",
            suffix="-xrechnung.xml",
            gaps=prepared.xrechnung_gaps,
        ),
        _xml_artifact(
            invoice=invoice,
            profile="facturx",
            artifact_format="zugferd_xml",
            media_type="application/xml",
            suffix="-zugferd.xml",
            gaps=[],
        ),
    ]
    artifacts.append(_zugferd_pdf_artifact(invoice, pdf_bytes, artifacts[1]))
    ready: bool = any(item.download_allowed for item in artifacts)
    return IssueBuildResponse(
        ready=ready,
        message=_READY if ready else _NOT_READY,
        blocking_issues=[],
        artifacts=artifacts,
    )


def _xml_artifact(
    *,
    invoice: ReadyInvoice,
    profile: CiiProfile,
    artifact_format: IssueArtifactFormat,
    media_type: str,
    suffix: str,
    gaps: List[ValidationIssue],
) -> IssueArtifact:
    filename: str = safe_invoice_filename(invoice.invoice_number, suffix)
    if gaps:
        return IssueArtifact(
            format=artifact_format,
            filename=filename,
            media_type=media_type,
            content_base64=None,
            download_allowed=False,
            validation_status=ValidationStatus.INVALID,
            validation_issues=gaps,
        )
    xml_text: str = render_cii(invoice, profile)
    result: ValidationResult = validate_invoice(
        xml_text,
        _parsed_view(invoice),
    )
    allowed: bool = result.full_check_completed and result.status == ValidationStatus.VALID
    content: Optional[str] = base64.b64encode(xml_text.encode("utf-8")).decode("ascii") if allowed else None
    return IssueArtifact(
        format=artifact_format,
        filename=filename,
        media_type=media_type,
        content_base64=content,
        download_allowed=allowed,
        validation_status=result.status,
        validation_issues=result.issues,
    )


def _zugferd_pdf_artifact(
    invoice: ReadyInvoice,
    pdf_bytes: Optional[bytes],
    xml_artifact: IssueArtifact,
) -> IssueArtifact:
    filename: str = safe_invoice_filename(invoice.invoice_number, "-zugferd.pdf")
    if pdf_bytes is None:
        return IssueArtifact(
            format="zugferd_pdf",
            filename=filename,
            media_type="application/pdf",
            content_base64=None,
            download_allowed=False,
            validation_status=ValidationStatus.NOT_CHECKED,
            validation_issues=[
                ValidationIssue(
                    level="error",
                    category="business",
                    code="PDF_MISSING",
                    message="Für ZUGFeRD wird die ursprüngliche PDF-Datei benötigt.",
                    field="pdf",
                )
            ],
        )
    if not xml_artifact.download_allowed or not xml_artifact.content_base64:
        return IssueArtifact(
            format="zugferd_pdf",
            filename=filename,
            media_type="application/pdf",
            content_base64=None,
            download_allowed=False,
            validation_status=xml_artifact.validation_status,
            validation_issues=xml_artifact.validation_issues,
        )
    xml_bytes: bytes = base64.b64decode(xml_artifact.content_base64)
    try:
        embedded: bytes = embed_facturx(pdf_bytes, xml_bytes)
    except IssueEmbedError as exc:
        return IssueArtifact(
            format="zugferd_pdf",
            filename=filename,
            media_type="application/pdf",
            content_base64=None,
            download_allowed=False,
            validation_status=ValidationStatus.INVALID,
            validation_issues=[
                ValidationIssue(
                    level="error",
                    category="business",
                    code="ZUGFERD_EMBED_FAILED",
                    message=str(exc),
                    field="pdf",
                )
            ],
        )
    return IssueArtifact(
        format="zugferd_pdf",
        filename=filename,
        media_type="application/pdf",
        content_base64=base64.b64encode(embedded).decode("ascii"),
        download_allowed=True,
        validation_status=ValidationStatus.VALID,
        validation_issues=[],
    )


def _parsed_view(invoice: ReadyInvoice) -> InvoiceParseResponse:
    """Shape the outgoing invoice like a parsed one so the shared KoSIT gate can run."""
    return InvoiceParseResponse(
        status=ParseStatus.SUCCESS,
        message="Erstellt",
        filename=safe_invoice_filename(invoice.invoice_number, ".xml"),
        invoice_number=invoice.invoice_number,
        issue_date=invoice.issue_date.isoformat(),
        seller=PartyInfo(name=invoice.seller_name, vat_id=invoice.seller_vat_id, iban=invoice.seller_iban),
        buyer=PartyInfo(name=invoice.buyer_name),
        totals=InvoiceTotals(
            net=invoice.line_total,
            tax=invoice.tax_total,
            gross=invoice.grand_total,
            currency=invoice.currency,
            tax_breakdown=[
                TaxBreakdown(rate=group.rate, amount=group.amount) for group in invoice.tax_groups
            ],
        ),
        line_items=[
            LineItem(
                position=int(line.line_id),
                description=line.description,
                quantity=line.quantity,
                unit=line.unit_code,
                unit_price=line.unit_price,
                tax_rate=line.tax_rate,
                net_amount=line.line_net,
            )
            for line in invoice.lines
        ],
    )
