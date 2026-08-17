"""Plain-text validation report for supplier or Steuerberater."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from app.schemas.invoice import (
    InvoiceParseResponse,
    ParseStatus,
    ValidationIssue,
    ValidationMeta,
    ValidationStatus,
)
from app.helper_functions.filenames import safe_filename_stem
from app.services.invoice_mapper import has_pdf_xml_mismatch


def build_validation_report(invoice: InvoiceParseResponse) -> str:
    """German UTF-8 report that can be forwarded without the original invoice file."""
    currency: str = (
        invoice.totals.currency if invoice.totals and invoice.totals.currency else "EUR"
    )
    seller_name: str = invoice.seller.name if invoice.seller and invoice.seller.name else "—"
    seller_iban: str = invoice.seller.iban if invoice.seller and invoice.seller.iban else "—"
    buyer_name: str = invoice.buyer.name if invoice.buyer and invoice.buyer.name else "—"
    net: str = _de_amount(invoice.totals.net if invoice.totals else None) or "—"
    tax: str = _de_amount(invoice.totals.tax if invoice.totals else None) or "—"
    gross: str = _de_amount(invoice.totals.gross if invoice.totals else None) or "—"
    mismatch: bool = has_pdf_xml_mismatch(invoice)

    lines: List[str] = [
        "Prüfbericht — eInvoice",
        "======================",
        "",
        "Dieser Bericht ist für Lieferanten oder Steuerberater bestimmt.",
        "Er beschreibt das technische Prüfergebnis, nicht die steuerliche Beurteilung.",
        "",
        f"Datei: {invoice.filename}",
        f"Typ: {_document_type_label(invoice)}",
        f"Rechnung: {invoice.invoice_number or '—'}",
        f"Rechnungsdatum: {_de_date(invoice.issue_date)}",
        f"Fälligkeitsdatum: {_de_date(invoice.due_date)}",
        f"Zahlungsreferenz: {invoice.payment_reference or '—'}",
        "",
        f"Lieferant: {seller_name}",
        f"IBAN: {seller_iban}",
        f"Empfänger: {buyer_name}",
        "",
        f"Netto: {net} {currency}",
        f"MwSt: {tax} {currency}",
        f"Brutto: {gross} {currency}",
        "",
        f"Parse-Status: {invoice.status.value}",
        f"Prüfung: {_validation_status_label(invoice.validation_status)}",
        f"Ergebnis: {_outcome_label(invoice, mismatch)}",
        f"Standard: {invoice.validation_meta.standard_version or '—'}",
        f"Profil: {invoice.validation_meta.profile or '—'}",
        f"Prüfengine: {_engine_line(invoice.validation_meta)}",
        f"PDF↔XML: {_mismatch_line(invoice, mismatch)}",
        "",
    ]

    if mismatch:
        lines.append("Empfehlung: Nicht zahlen. Lieferanten kontaktieren und Korrektur anfordern.")
        lines.append("")
    elif invoice.validation_status == ValidationStatus.INVALID or invoice.status == ParseStatus.ERROR:
        lines.append("Empfehlung: Nicht zahlen oder buchen, bevor die Fehler behoben sind.")
        lines.append("")

    errors: List[ValidationIssue] = [
        issue for issue in invoice.validation_issues if issue.level == "error"
    ]
    warnings: List[ValidationIssue] = [
        issue for issue in invoice.validation_issues if issue.level == "warning"
    ]
    infos: List[ValidationIssue] = [
        issue for issue in invoice.validation_issues if issue.level == "info"
    ]

    _append_issue_section(lines, "Fehler", errors)
    _append_issue_section(lines, "Warnungen", warnings)
    _append_issue_section(lines, "Hinweise", infos)

    if invoice.mismatch_fields:
        lines.extend(["PDF↔XML Abgleich:", ""])
        for item in invoice.mismatch_fields:
            status: str = "OK" if item.matched else "Abweichung"
            lines.append(
                f"- {item.label}: XML={item.xml_value or '—'} · "
                f"PDF={item.pdf_value or '—'} → {status}"
            )
        lines.append("")

    if invoice.next_steps:
        lines.extend(["Empfohlene nächste Schritte:", ""])
        for index, step in enumerate(invoice.next_steps, start=1):
            lines.append(f"{index}. {step}")
        lines.append("")

    lines.extend(
        [
            "Hinweis: Die Prüfung betrifft Schema- und Standardkonformität",
            "(EN 16931 / XRechnung). Die Entscheidung über den Vorsteuerabzug",
            "liegt beim Empfänger bzw. Steuerberater.",
            "",
        ]
    )
    return "\n".join(lines)


def build_validation_report_filename(invoice: InvoiceParseResponse) -> str:
    """Filename: pruefbericht_supplier_invoiceNo_date.txt"""
    supplier: str = safe_filename_stem(invoice.seller.name if invoice.seller else None) or "supplier"
    number: str = safe_filename_stem(invoice.invoice_number) or "invoice"
    date_part: str = (invoice.issue_date or "nodate").replace("-", "")
    return f"pruefbericht_{supplier}_{number}_{date_part}.txt"


def _append_issue_section(lines: List[str], title: str, issues: List[ValidationIssue]) -> None:
    if not issues:
        return
    lines.append(f"{title}:")
    for issue in issues:
        codes: List[str] = [issue.category]
        if issue.bt_code:
            codes.append(issue.bt_code)
        if issue.code:
            codes.append(issue.code)
        label: str = "/".join(codes)
        lines.append(f"- [{label}] {issue.message}")
        if issue.explanation:
            lines.append(f"  {issue.explanation}")
    lines.append("")


def _document_type_label(invoice: InvoiceParseResponse) -> str:
    kind: str = "Gutschrift" if invoice.document_type == "credit_note" else "Rechnung"
    file_type: str = invoice.file_type or "—"
    return f"{kind} · {file_type}"


def _validation_status_label(status: ValidationStatus) -> str:
    mapping: dict[ValidationStatus, str] = {
        ValidationStatus.VALID: "gültig",
        ValidationStatus.WARNING: "Warnung",
        ValidationStatus.INVALID: "ungültig",
        ValidationStatus.NOT_CHECKED: "nicht vollständig geprüft",
    }
    return mapping.get(status, status.value)


def _outcome_label(invoice: InvoiceParseResponse, mismatch: bool) -> str:
    if (
        invoice.status == ParseStatus.ERROR
        or invoice.validation_status == ValidationStatus.INVALID
        or any(issue.level == "error" for issue in invoice.validation_issues)
        or mismatch
    ):
        return "Korrektur anfordern"
    if (
        invoice.status == ParseStatus.PARTIAL
        or invoice.validation_status == ValidationStatus.WARNING
        or invoice.validation_status == ValidationStatus.NOT_CHECKED
    ):
        return "Bitte prüfen"
    return "Kann verarbeitet werden"


def _engine_line(meta: ValidationMeta) -> str:
    if meta.engine == "kosit":
        version: str = f" {meta.engine_version}" if meta.engine_version else ""
        scenarios: str = f" · {meta.scenarios_version}" if meta.scenarios_version else ""
        return f"KoSIT Validator{version}{scenarios}"
    return "interne Geschäftsregeln (keine volle KoSIT-Prüfung)"


def _mismatch_line(invoice: InvoiceParseResponse, mismatch: bool) -> str:
    if invoice.file_type != "zugferd_pdf" or not invoice.mismatch_fields:
        return "nicht geprüft / nicht zutreffend"
    if mismatch:
        labels: str = ", ".join(
            item.label
            for item in invoice.mismatch_fields
            if item.xml_value and not item.matched
        )
        return f"Abweichung ({labels})" if labels else "Abweichung"
    return "übereinstimmend"


def _de_amount(value: Optional[Decimal]) -> str:
    if value is None:
        return ""
    return f"{value:.2f}".replace(".", ",")


def _de_date(iso_date: Optional[str]) -> str:
    if not iso_date or len(iso_date) < 10:
        return iso_date or "—"
    return f"{iso_date[8:10]}.{iso_date[5:7]}.{iso_date[0:4]}"
