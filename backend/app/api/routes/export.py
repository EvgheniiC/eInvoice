from typing import List

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.schemas.export import EXPORT_DOCS, ExportFormat, ExportMappingDoc, ExportRequest
from app.schemas.invoice import ParseStatus
from app.services.export_service import ExportService

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
    if body.invoice.status == ParseStatus.ERROR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fehlerhafte Rechnung kann nicht exportiert werden.",
        )
    if not body.invoice.invoice_number and not (body.invoice.totals and body.invoice.totals.gross):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Zu wenige Daten für den Export (Nummer/Betrag fehlen).",
        )

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
