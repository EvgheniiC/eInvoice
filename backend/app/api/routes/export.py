from typing import List, Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response

from app.core.error_events import format_safe_stack, log_api_error
from app.core.middleware import get_request_id
from app.schemas.export import (
    EXPORT_DOCS,
    AccountantPackageRequest,
    ExportMappingDoc,
    ExportRequest,
    ValidationReportRequest,
)
from app.schemas.invoice import InvoiceParseResponse, ParseStatus
from app.services.export_service import (
    ExportService,
    assert_xml_bytes,
    decode_base64_payload,
    decode_pdf_base64,
)
from app.services.validation_report import (
    build_validation_report,
    build_validation_report_filename,
)

router: APIRouter = APIRouter()
export_service: ExportService = ExportService()


@router.get("/export/mapping", response_model=List[ExportMappingDoc])
def export_mapping_docs() -> List[ExportMappingDoc]:
    """Document DTO → export column mapping for Steuerberater."""
    return EXPORT_DOCS


@router.post("/export")
def export_invoice(body: ExportRequest, request: Request) -> Response:
    """
    Export a previously parsed invoice DTO as CSV, Excel, or DATEV CSV.
    """
    _assert_exportable(body.invoice)

    try:
        content, media_type, filename = export_service.export(
            invoice=body.invoice,
            export_format=body.format,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
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


@router.post("/export/accountant-package")
def export_accountant_package(body: AccountantPackageRequest, request: Request) -> Response:
    """
    ZIP for Steuerberater: original XML/PDF + summary + Prüfbericht + Excel + DATEV.
    """
    _assert_exportable(body.invoice)

    pdf_bytes: Optional[bytes] = _optional_pdf_bytes(body.pdf_base64)
    xml_bytes: Optional[bytes] = _optional_xml_bytes(body.xml_base64)

    try:
        content, media_type, filename = export_service.build_accountant_package(
            invoice=body.invoice,
            pdf_bytes=pdf_bytes,
            pdf_filename=body.pdf_filename,
            xml_bytes=xml_bytes,
            xml_filename=body.xml_filename,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
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
    if invoice.status == ParseStatus.ERROR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fehlerhafte Rechnung kann nicht exportiert werden.",
        )
    if not invoice.invoice_number and not (invoice.totals and invoice.totals.gross):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zu wenige Daten für den Export (Nummer/Betrag fehlen).",
        )
