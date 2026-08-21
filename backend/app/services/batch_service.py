"""Postgres-backed batch queue. API enqueues; einvoice-worker parses one file at a time."""

from __future__ import annotations

import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select, update
from sqlalchemy.engine import Result
from sqlalchemy.orm import Session, selectinload, sessionmaker

from app.core.clock import utc_now
from app.core.config import settings
from app.core.error_events import log_event, safe_filename
from app.db.models import BatchItem, BatchJob
from app.schemas.batch import (
    BatchItemResponse,
    BatchItemStatus,
    BatchJobResponse,
    BatchJobStatus,
)
from app.schemas.invoice import InvoiceParseResponse, ParseStatus, ValidationStatus
from app.services.auth_service import OrgContext
from app.services.invoice_service import InvoiceService
from app.services.plan_limits import PlanLimits
from app.services.quota_service import (
    assert_upload_size,
    consume_parse_count,
    limits_for_context,
    refund_parse_count,
)

BATCH_FORBIDDEN_DETAIL: str = (
    "Batch-Upload ist in Plus enthalten. "
    "Mit Plus prüfen Sie mehrere Rechnungen auf einmal."
)
ZIP_NOT_READY_DETAIL: str = (
    "ZIP-Upload folgt in einem nächsten Schritt. "
    "Bitte einzelne XML- oder PDF-Dateien wählen."
)
TERMINAL_ITEM_STATUSES: frozenset[str] = frozenset(
    {
        BatchItemStatus.GUELTIG.value,
        BatchItemStatus.PRUEFEN.value,
        BatchItemStatus.ABLEHNEN.value,
    }
)

_invoice_service: InvoiceService = InvoiceService()


def require_batch_plan(org_context: Optional[OrgContext]) -> OrgContext:
    if org_context is None or not org_context.allows_batch:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=BATCH_FORBIDDEN_DETAIL,
        )
    return org_context


async def enqueue_batch(
    session: Session,
    org_context: OrgContext,
    uploads: list[UploadFile],
) -> BatchJobResponse:
    limits: PlanLimits = limits_for_context(org_context)
    payloads: list[tuple[str, bytes]] = await _read_uploads(uploads, limits)
    consume_parse_count(session, org_context, len(payloads))
    job: BatchJob = BatchJob(
        organization_id=org_context.organization_id,
        created_by_user_id=org_context.user_id,
        status=BatchJobStatus.QUEUED.value,
        item_count=len(payloads),
    )
    session.add(job)
    session.flush()
    try:
        _write_items(session, job, payloads)
        session.commit()
    except Exception:
        session.rollback()
        refund_parse_count(session, org_context, len(payloads))
        shutil.rmtree(settings.resolved_batch_temp_dir / str(job.id), ignore_errors=True)
        raise
    log_event(
        logging.INFO,
        "batch_enqueued",
        fields={
            "organization_id": str(org_context.organization_id),
            "job_id": str(job.id),
            "item_count": len(payloads),
            "plan": org_context.plan_code,
        },
    )
    loaded: BatchJob = _load_job(session, job.id)
    return to_response(loaded)


def get_batch(
    session: Session,
    org_context: OrgContext,
    job_id: UUID,
) -> BatchJobResponse:
    job: Optional[BatchJob] = session.scalar(
        select(BatchJob)
        .where(BatchJob.id == job_id, BatchJob.organization_id == org_context.organization_id)
        .options(selectinload(BatchJob.items))
    )
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auftrag nicht gefunden.")
    return to_response(job)


def process_next_item() -> bool:
    """Claim one queued file, parse it, store metadata, delete the original. False if idle."""
    from app.db.session import get_session_factory

    factory: Optional[sessionmaker[Session]] = get_session_factory()
    if factory is None:
        return False
    session: Session = factory()
    try:
        _reclaim_stale_items(session)
        item_id: Optional[UUID] = _claim_item(session)
        if item_id is None:
            return False
    finally:
        session.close()
    _process_claimed_item(item_id)
    return True


def drain_queue() -> int:
    """Process queued items until the queue is empty. Used by tests and `--once`."""
    processed: int = 0
    while process_next_item():
        processed += 1
    return processed


def to_response(job: BatchJob) -> BatchJobResponse:
    items: list[BatchItemResponse] = [_item_response(item) for item in job.items]
    done_count: int = sum(1 for item in items if item.status.value in TERMINAL_ITEM_STATUSES)
    return BatchJobResponse(
        id=job.id,
        status=BatchJobStatus(job.status),
        item_count=job.item_count,
        done_count=done_count,
        items=items,
        export_package_available=False,
    )


async def _read_uploads(
    uploads: list[UploadFile],
    limits: PlanLimits,
) -> list[tuple[str, bytes]]:
    if not uploads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keine Dateien übermittelt.",
        )
    if any(_is_zip_name(item.filename) for item in uploads):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ZIP_NOT_READY_DETAIL)
    if len(uploads) > limits.max_batch_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Maximal {limits.max_batch_files} Dateien pro Auftrag "
                f"in Ihrem Tarif {limits.name}."
            ),
        )
    payloads: list[tuple[str, bytes]] = []
    for upload in uploads:
        filename: str = _safe_filename(upload.filename)
        suffix: str = Path(filename).suffix.lower()
        if suffix not in settings.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nicht unterstützter Dateityp. Erlaubt: {', '.join(settings.allowed_extensions)}",
            )
        content: bytes = await upload.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Datei ist leer: {safe_filename(filename)}",
            )
        assert_upload_size(len(content), limits)
        payloads.append((filename, content))
    return payloads


def _write_items(session: Session, job: BatchJob, payloads: list[tuple[str, bytes]]) -> None:
    job_dir: Path = _job_dir(job.id)
    job_dir.mkdir(parents=True, exist_ok=True)
    for position, (filename, content) in enumerate(payloads):
        item_id: UUID = uuid4()
        suffix: str = Path(filename).suffix.lower()
        storage: Path = job_dir / f"{item_id}{suffix}"
        storage.write_bytes(content)
        session.add(
            BatchItem(
                id=item_id,
                job_id=job.id,
                position=position,
                filename=filename,
                storage_path=str(storage),
                status=BatchItemStatus.QUEUED.value,
            )
        )


def _claim_item(session: Session) -> Optional[UUID]:
    candidate: Optional[BatchItem] = session.scalar(
        select(BatchItem)
        .where(BatchItem.status == BatchItemStatus.QUEUED.value)
        .order_by(BatchItem.created_at.asc())
        .limit(1)
    )
    if candidate is None:
        return None
    result: Result[object] = session.execute(
        update(BatchItem)
        .where(
            BatchItem.id == candidate.id,
            BatchItem.status == BatchItemStatus.QUEUED.value,
        )
        .execution_options(synchronize_session="fetch")
        .values(status=BatchItemStatus.PROCESSING.value, claimed_at=utc_now())
    )
    if result.rowcount != 1:
        session.rollback()
        return None
    job: Optional[BatchJob] = session.get(BatchJob, candidate.job_id)
    if job is not None and job.status == BatchJobStatus.QUEUED.value:
        job.status = BatchJobStatus.PROCESSING.value
    session.commit()
    return candidate.id


def _process_claimed_item(item_id: UUID) -> None:
    from app.db.session import get_session_factory

    factory: Optional[sessionmaker[Session]] = get_session_factory()
    if factory is None:
        return
    session: Session = factory()
    try:
        item: Optional[BatchItem] = session.get(BatchItem, item_id)
        if item is None:
            return
        filename: str = item.filename
        storage_path: Optional[str] = item.storage_path
        session.expunge(item)
    finally:
        session.close()

    response: InvoiceParseResponse
    try:
        content: bytes = _read_original(storage_path)
        response = _invoice_service.parse_upload(filename=filename, content=content)
    except Exception as exc:
        log_event(
            logging.ERROR,
            "batch_item_failed",
            fields={"item_id": str(item_id), "exc_type": type(exc).__name__},
        )
        response = InvoiceParseResponse(
            status=ParseStatus.ERROR,
            message="Datei konnte nicht geprüft werden.",
            filename=filename,
            file_type="error",
        )

    session: Session = factory()
    try:
        item: Optional[BatchItem] = session.get(BatchItem, item_id)
        if item is None:
            return
        _apply_parse_result(item, response)
        _unlink_quietly(item.storage_path)
        item.storage_path = None
        session.commit()
        _maybe_complete_job(session, item.job_id)
        log_event(
            logging.INFO,
            "batch_item_done",
            fields={"item_id": str(item_id), "job_id": str(item.job_id), "status": item.status},
        )
    finally:
        session.close()


def _apply_parse_result(item: BatchItem, response: InvoiceParseResponse) -> None:
    item.status = _summary_status(response)
    item.invoice_number = response.invoice_number
    item.seller_name = response.seller.name if response.seller is not None else None
    if response.totals is not None and response.totals.gross is not None:
        item.gross_amount = str(response.totals.gross)
        item.currency = response.totals.currency
    item.message = response.message
    item.result_json = response.model_dump(mode="json")
    item.finished_at = utc_now()


def _summary_status(response: InvoiceParseResponse) -> str:
    if response.status == ParseStatus.ERROR:
        return BatchItemStatus.ABLEHNEN.value
    if response.validation_status == ValidationStatus.VALID:
        return BatchItemStatus.GUELTIG.value
    if response.validation_status == ValidationStatus.INVALID:
        return BatchItemStatus.ABLEHNEN.value
    return BatchItemStatus.PRUEFEN.value


def _maybe_complete_job(session: Session, job_id: UUID) -> None:
    job: Optional[BatchJob] = session.scalar(
        select(BatchJob).where(BatchJob.id == job_id).options(selectinload(BatchJob.items))
    )
    if job is None:
        return
    if any(item.status not in TERMINAL_ITEM_STATUSES for item in job.items):
        return
    job.status = BatchJobStatus.COMPLETED.value
    job.completed_at = utc_now()
    session.commit()
    _remove_job_dir(job.id)
    log_event(
        logging.INFO,
        "batch_completed",
        fields={"job_id": str(job.id), "item_count": job.item_count},
    )


def _reclaim_stale_items(session: Session) -> None:
    stale_before: datetime = utc_now() - timedelta(seconds=settings.batch_item_stale_seconds)
    stale: list[BatchItem] = list(
        session.scalars(
            select(BatchItem).where(
                BatchItem.status == BatchItemStatus.PROCESSING.value,
                BatchItem.claimed_at.is_not(None),
                BatchItem.claimed_at < stale_before,
            )
        ).all()
    )
    if not stale:
        return
    for item in stale:
        if item.storage_path and Path(item.storage_path).is_file():
            item.status = BatchItemStatus.QUEUED.value
            item.claimed_at = None
        else:
            item.status = BatchItemStatus.ABLEHNEN.value
            item.message = "Prüfung abgebrochen."
            item.finished_at = utc_now()
            item.storage_path = None
    session.commit()


def _read_original(storage_path: Optional[str]) -> bytes:
    if not storage_path:
        raise FileNotFoundError("batch_original_missing")
    path: Path = Path(storage_path)
    if not path.is_file():
        raise FileNotFoundError("batch_original_missing")
    return path.read_bytes()


def _item_response(item: BatchItem) -> BatchItemResponse:
    invoice: Optional[InvoiceParseResponse] = None
    if item.result_json:
        invoice = InvoiceParseResponse.model_validate(item.result_json)
    return BatchItemResponse(
        id=item.id,
        filename=item.filename,
        status=BatchItemStatus(item.status),
        invoice_number=item.invoice_number,
        seller_name=item.seller_name,
        gross_amount=item.gross_amount,
        currency=item.currency,
        message=item.message,
        invoice=invoice,
    )


def _load_job(session: Session, job_id: UUID) -> BatchJob:
    job: Optional[BatchJob] = session.scalar(
        select(BatchJob).where(BatchJob.id == job_id).options(selectinload(BatchJob.items))
    )
    if job is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Auftrag konnte nicht geladen werden.",
        )
    return job


def _safe_filename(name: Optional[str]) -> str:
    raw: str = (name or "").strip()
    base: str = Path(raw).name
    if not base or base in {".", ".."}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dateiname fehlt.")
    return base[:255]


def _is_zip_name(name: Optional[str]) -> bool:
    if not name:
        return False
    return Path(name).suffix.lower() == ".zip"


def _job_dir(job_id: UUID) -> Path:
    root: Path = settings.resolved_batch_temp_dir
    root.mkdir(parents=True, exist_ok=True)
    return root / str(job_id)


def _remove_job_dir(job_id: UUID) -> None:
    shutil.rmtree(settings.resolved_batch_temp_dir / str(job_id), ignore_errors=True)


def _unlink_quietly(path_value: Optional[str]) -> None:
    if not path_value:
        return
    try:
        Path(path_value).unlink(missing_ok=True)
    except OSError:
        log_event(logging.WARNING, "batch_temp_unlink_failed", fields={"present": True})
