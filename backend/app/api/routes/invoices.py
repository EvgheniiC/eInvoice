from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.config import settings
from app.schemas.invoice import InvoiceParseResponse, ParseStatus
from app.services.invoice_service import InvoiceService

router: APIRouter = APIRouter()
invoice_service: InvoiceService = InvoiceService()


@router.post("/parse", response_model=InvoiceParseResponse)
async def parse_invoice(file: UploadFile = File(...)) -> InvoiceParseResponse:
    """
    Accept an XRechnung XML or ZUGFeRD PDF and return a structured parse result.

    Full parsing pipeline will be wired in Phase 1; this endpoint validates
    upload constraints and returns a stub response for frontend integration.
    """
    if file.filename is None or file.filename.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dateiname fehlt.",
        )

    filename_lower: str = file.filename.lower()
    allowed: bool = any(filename_lower.endswith(ext) for ext in settings.allowed_extensions)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Nicht unterstützter Dateityp. Erlaubt: {', '.join(settings.allowed_extensions)}",
        )

    content: bytes = await file.read()
    max_bytes: int = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Datei ist zu groß. Maximum: {settings.max_upload_size_mb} MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datei ist leer.",
        )

    return invoice_service.parse_upload(filename=file.filename, content=content)
