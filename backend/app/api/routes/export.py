from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.schemas.export import (
    EXPORT_DOCS,
    AccountantPackageRequest,
    ExportMappingDoc,
    ExportRequest,
)
from app.schemas.invoice import InvoiceParseResponse, ParseStatus
from app.services.export_service import ExportService, decode_pdf_base64

router: APIRouter = APIRouter()
export_service: ExportService = ExportService()


@router.get("/export/mapping", response_model=List[ExportMappingDoc])
def export_mapping_docs() -> List[ExportMappingDoc]:
    """Document DTO → export column mapping for Steuerberater."""
    return EXPORT_DOCS


@router.post("/export")
def export_invoice(body: ExportRequest) -> Response:
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

    headers: dict[str, str] = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return Response(content=content, media_type=media_type, headers=headers)


@router.post("/export/accountant-package")
def export_accountant_package(body: AccountantPackageRequest) -> Response:
    """
    ZIP for Steuerberater: summary + Excel + DATEV + optional visual PDF.
    """
    _assert_exportable(body.invoice)

    pdf_bytes: Optional[bytes] = None
    if body.pdf_base64:
        try:
            pdf_bytes = decode_pdf_base64(body.pdf_base64)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        if not pdf_bytes.startswith(b"%PDF"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Die angehängte Datei ist keine gültige PDF.",
            )

    try:
        content, media_type, filename = export_service.build_accountant_package(
            invoice=body.invoice,
            pdf_bytes=pdf_bytes,
            pdf_filename=body.pdf_filename,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    headers: dict[str, str] = {
        "Content-Disposition": f'attachment; filename="{filename}"',
    }
    return Response(content=content, media_type=media_type, headers=headers)


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
