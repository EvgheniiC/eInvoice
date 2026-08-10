import logging
from typing import Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status

from app.core.config import settings
from app.core.error_events import log_api_error, safe_filename
from app.core.middleware import get_request_id
from app.schemas.invoice import InvoiceParseResponse
from app.services.invoice_service import InvoiceService

router: APIRouter = APIRouter()
invoice_service: InvoiceService = InvoiceService()


@router.post("/parse", response_model=InvoiceParseResponse)
async def parse_invoice(
    request: Request,
    file: UploadFile = File(...),
) -> InvoiceParseResponse:
    """
    Accept an XRechnung XML or ZUGFeRD PDF and return a structured parse result.
    """
    request_id: Optional[str] = get_request_id(request)

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
        log_api_error(
            event="upload_too_large",
            method=request.method,
            path=request.url.path,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            request_id=request_id,
            detail=f"filename={safe_filename(file.filename)} size_bytes={len(content)}",
            level=logging.WARNING,
        )
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Datei ist zu groß. Maximum: {settings.max_upload_size_mb} MB.",
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datei ist leer.",
        )

    return invoice_service.parse_upload(
        filename=file.filename,
        content=content,
        request_id=request_id,
    )
