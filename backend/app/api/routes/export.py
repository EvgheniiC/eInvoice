from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_optional_db, get_optional_org_context
from app.core.error_events import format_safe_stack, log_api_error
from app.core.metrics import observe_funnel
from app.core.middleware import get_request_id
from app.schemas.export import (
    EXPORT_DOCS,
    AccountantPackageRequest,
    ExportMappingDoc,
    ExportRequest,
    ValidationReportRequest,
    ViewPdfRequest,
)
from app.schemas.invoice import InvoiceParseResponse, ParseStatus
from app.services.auth_service import OrgContext, load_organization_profile
from app.services.export_service import (
    ExportService,
    assert_xml_bytes,
    decode_base64_payload,
    decode_pdf_base64,
    invoice_is_exportable,
)
from app.services.view_pdf_service import ViewPdfService, invoice_is_viewable
from app.services.quota_service import enforce_export
from app.services.validation_report import (
    build_validation_report,
    build_validation_report_filename,
)

router: APIRouter = APIRouter()
export_service: ExportService = ExportService()
view_pdf_service: ViewPdfService = ViewPdfService()


@router.get("/export/mapping", response_model=List[ExportMappingDoc])
def export_mapping_docs() -> List[ExportMappingDoc]:
    """Document DTO → export column mapping for Steuerberater."""
    return EXPORT_DOCS


@router.post("/export")
def export_invoice(
    body: ExportRequest,
    request: Request,
    org_context: Optional[OrgContext] = Depends(get_optional_org_context),
    db: Optional[Session] = Depends(get_optional_db),
) -> Response:
    """
    Export a previously parsed invoice DTO as CSV, Excel, or DATEV CSV.
    """
    _assert_exportable(body.invoice)

    try:
        with enforce_export(request, db, org_context):
            content, media_type, filename = export_service.export(
                invoice=body.invoice,
                export_format=body.format,
            )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        log_api_error(
            event="export_failed",
            method=request.method,
            path=request.url.path,
            status_code=500,
            request_id=get_request_id(request),
            detail=type(exc).__name__,
            exc_type=type(exc).__name__,
            stack=format_safe_stack(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Export fehlgeschlagen.",
        ) from exc

    headers: dict[str, str] = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    observe_funnel("export")
    return Response(content=content, media_type=media_type, headers=headers)


@router.post("/export/validation-report")
def export_validation_report(body: ValidationReportRequest) -> Response:
    """
    Download a German plain-text validation report for supplier or Steuerberater.
    Allowed even when the invoice is invalid — that is the intended use.
    """
    filename: str = build_validation_report_filename(body.invoice)
    content: bytes = ("\ufeff" + build_validation_report(body.invoice)).encode("utf-8")
    headers: dict[str, str] = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return Response(content=content, media_type="text/plain; charset=utf-8", headers=headers)


@router.post("/export/view-pdf")
def export_view_pdf(
    body: ViewPdfRequest,
    request: Request,
    org_context: Optional[OrgContext] = Depends(get_optional_org_context),
    db: Optional[Session] = Depends(get_optional_db),
) -> Response:
    """
    Working-copy PDF from parsed XML fields. Not an original invoice.
    Allowed for invalid invoices so the user can still print the readable view.
    """
    _assert_viewable(body.invoice)

    try:
        with enforce_export(request, db, org_context):
            content, media_type, filename = view_pdf_service.render(body.invoice)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        log_api_error(
            event="view_pdf_failed",
            method=request.method,
            path=request.url.path,
            status_code=500,
            request_id=get_request_id(request),
            detail=type(exc).__name__,
            exc_type=type(exc).__name__,
            stack=format_safe_stack(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Lesbare PDF fehlgeschlagen.",
        ) from exc

    headers: dict[str, str] = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    observe_funnel("export")
    return Response(content=content, media_type=media_type, headers=headers)


@router.post("/export/accountant-package")
def export_accountant_package(
    body: AccountantPackageRequest,
    request: Request,
    org_context: Optional[OrgContext] = Depends(get_optional_org_context),
    db: Optional[Session] = Depends(get_optional_db),
) -> Response:
    """
    ZIP for Steuerberater: original XML/PDF + summary + Prüfbericht + Excel + DATEV.
    """
    _assert_exportable(body.invoice)

    pdf_bytes: Optional[bytes] = _optional_pdf_bytes(body.pdf_base64)
    xml_bytes: Optional[bytes] = _optional_xml_bytes(body.xml_base64)

    try:
        with enforce_export(request, db, org_context):
            content, media_type, filename = export_service.build_accountant_package(
                invoice=body.invoice,
                pdf_bytes=pdf_bytes,
                pdf_filename=body.pdf_filename,
                xml_bytes=xml_bytes,
                xml_filename=body.xml_filename,
                org_profile=(
                    load_organization_profile(db, org_context.organization_id)
                    if db is not None and org_context is not None
                    else None
                ),
            )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        log_api_error(
            event="accountant_package_failed",
            method=request.method,
            path=request.url.path,
            status_code=500,
            request_id=get_request_id(request),
            detail=type(exc).__name__,
            exc_type=type(exc).__name__,
            stack=format_safe_stack(exc),
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Accountant-Paket fehlgeschlagen.",
        ) from exc

    headers: dict[str, str] = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    observe_funnel("export")
    return Response(content=content, media_type=media_type, headers=headers)


def _optional_pdf_bytes(pdf_base64: Optional[str]) -> Optional[bytes]:
    if not pdf_base64:
        return None
    try:
        pdf_bytes: bytes = decode_pdf_base64(pdf_base64)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    if not pdf_bytes.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Die angehängte Datei ist keine gültige PDF.",
        )
    return pdf_bytes


def _optional_xml_bytes(xml_base64: Optional[str]) -> Optional[bytes]:
    if not xml_base64:
        return None
    try:
        xml_bytes: bytes = decode_base64_payload(xml_base64)
        assert_xml_bytes(xml_bytes)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return xml_bytes


def _assert_exportable(invoice: InvoiceParseResponse) -> None:
    if not invoice_is_exportable(invoice):
        if invoice.status == ParseStatus.ERROR:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Fehlerhafte Rechnung kann nicht exportiert werden.",
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zu wenige Daten für den Export (Nummer/Betrag fehlen).",
        )


def _assert_viewable(invoice: InvoiceParseResponse) -> None:
    if not invoice_is_viewable(invoice):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fehlerhafte Rechnung kann nicht als PDF dargestellt werden.",
        )
