import logging
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import AUTH_UNAVAILABLE, get_optional_db, get_optional_org_context
from app.core.config import settings
from app.core.error_events import format_safe_stack, log_api_error, log_event, safe_filename
from app.core.metrics import observe_funnel
from app.core.middleware import get_request_id
from app.schemas.batch import BatchJobResponse
from app.schemas.history import HistoryListResponse
from app.schemas.invoice import InvoiceParseResponse
from app.services.auth_service import OrgContext
from app.services.batch_service import (
    assert_batch_package_ready,
    assert_batch_view_pdfs_ready,
    build_batch_accountant_package,
    build_batch_view_pdf_package,
    enqueue_batch,
    get_batch,
    require_batch_plan,
)
from app.services.history_service import (
    build_history_accountant_package,
    list_history,
    record_parse_history,
    require_history_plan,
)
from app.services.invoice_service import InvoiceService
from app.services.quota_service import enforce_export, enforce_parse

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
            result: InvoiceParseResponse = invoice_service.parse_upload(
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

    try:
        record_parse_history(
            db,
            org_context,
            filename=file.filename,
            content=content,
            response=result,
        )
    except Exception as exc:
        log_event(
            logging.ERROR,
            "history_record_failed",
            fields={
                "request_id": request_id,
                "exc_type": type(exc).__name__,
            },
        )
    return result


@router.get("/history", response_model=HistoryListResponse)
def get_invoice_history(
    limit: int = 50,
    offset: int = 0,
    org_context: Optional[OrgContext] = Depends(get_optional_org_context),
    db: Optional[Session] = Depends(get_optional_db),
) -> HistoryListResponse:
    """List opted-in parse metadata for the caller's organization."""
    context: OrgContext = require_history_plan(org_context)
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=AUTH_UNAVAILABLE,
        )
    return list_history(db, context, limit=limit, offset=offset)


@router.post("/history/{record_id}/accountant-package")
def export_history_accountant_package(
    record_id: UUID,
    request: Request,
    org_context: Optional[OrgContext] = Depends(get_optional_org_context),
    db: Optional[Session] = Depends(get_optional_db),
) -> Response:
    """Re-download the Steuerberater package while the opted-in original is in retention."""
    context: OrgContext = require_history_plan(org_context)
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=AUTH_UNAVAILABLE,
        )
    try:
        with enforce_export(request, db, context):
            content, media_type, filename = build_history_accountant_package(db, context, record_id)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        log_api_error(
            event="history_accountant_package_failed",
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


@router.post("/batch", response_model=BatchJobResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_invoice_batch(
    files: List[UploadFile] = File(...),
    org_context: Optional[OrgContext] = Depends(get_optional_org_context),
    db: Optional[Session] = Depends(get_optional_db),
) -> BatchJobResponse:
    """Queue several XML/PDF files or one ZIP (invoice members only) for Plus/Team."""
    context: OrgContext = require_batch_plan(org_context)
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=AUTH_UNAVAILABLE,
        )
    return await enqueue_batch(db, context, files)


@router.get("/batch/{job_id}", response_model=BatchJobResponse)
def get_invoice_batch(
    job_id: UUID,
    org_context: Optional[OrgContext] = Depends(get_optional_org_context),
    db: Optional[Session] = Depends(get_optional_db),
) -> BatchJobResponse:
    """Return batch progress and summary rows for the caller's organization."""
    context: OrgContext = require_batch_plan(org_context)
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=AUTH_UNAVAILABLE,
        )
    return get_batch(db, context, job_id)


@router.post("/batch/{job_id}/accountant-package")
def export_batch_accountant_package(
    job_id: UUID,
    request: Request,
    org_context: Optional[OrgContext] = Depends(get_optional_org_context),
    db: Optional[Session] = Depends(get_optional_db),
) -> Response:
    """
    One ZIP for the completed batch: originals + summary + Prüfbericht + Excel + DATEV.
    Originals must still be in the short-lived temp directory.
    """
    context: OrgContext = require_batch_plan(org_context)
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=AUTH_UNAVAILABLE,
        )
    assert_batch_package_ready(db, context, job_id)
    try:
        with enforce_export(request, db, context):
            content, media_type, filename = build_batch_accountant_package(db, context, job_id)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        log_api_error(
            event="batch_accountant_package_failed",
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


@router.post("/batch/{job_id}/view-pdfs")
def export_batch_view_pdfs(
    job_id: UUID,
    request: Request,
    org_context: Optional[OrgContext] = Depends(get_optional_org_context),
    db: Optional[Session] = Depends(get_optional_db),
) -> Response:
    """
    ZIP of working-copy PDFs for every readable invoice in the completed batch.
    Uses stored parse results; original files are not required.
    """
    context: OrgContext = require_batch_plan(org_context)
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=AUTH_UNAVAILABLE,
        )
    assert_batch_view_pdfs_ready(db, context, job_id)
    try:
        with enforce_export(request, db, context):
            content, media_type, filename = build_batch_view_pdf_package(db, context, job_id)
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        log_api_error(
            event="batch_view_pdf_failed",
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
