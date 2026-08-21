import logging
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_optional_db, get_optional_org_context
from app.core.config import settings
from app.core.error_events import log_api_error, log_event, safe_filename
from app.core.middleware import get_request_id
from app.schemas.invoice import InvoiceParseResponse
from app.services.auth_service import OrgContext
from app.services.invoice_service import InvoiceService
from app.services.quota_service import enforce_parse

router: APIRouter = APIRouter()
invoice_service: InvoiceService = InvoiceService()


@router.post("/parse", response_model=InvoiceParseResponse)
async def parse_invoice(
    request: Request,
    file: UploadFile = File(...),
    org_context: Optional[OrgContext] = Depends(get_optional_org_context),
    db: Optional[Session] = Depends(get_optional_db),
) -> InvoiceParseResponse:
    """
    Accept an XRechnung XML or ZUGFeRD PDF and return a structured parse result.
    Guest upload stays unauthenticated and does not persist the file.
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
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Datei ist leer.",
        )

    if org_context is not None:
        log_event(
            logging.INFO,
            "parse_with_org",
            fields={
                "request_id": request_id,
                "organization_id": str(org_context.organization_id),
                "plan": org_context.plan_code,
            },
        )

    try:
        with enforce_parse(request, db, org_context, len(content)):
            return invoice_service.parse_upload(
                filename=file.filename,
                content=content,
                request_id=request_id,
            )
    except HTTPException as exc:
        if exc.status_code == status.HTTP_413_REQUEST_ENTITY_TOO_LARGE:
            log_api_error(
                event="upload_too_large",
                method=request.method,
                path=request.url.path,
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                request_id=request_id,
                detail=f"filename={safe_filename(file.filename)} size_bytes={len(content)}",
                level=logging.WARNING,
            )
        raise
