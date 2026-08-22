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

from app.core.clock import as_utc, utc_now
from app.core.config import settings
from app.core.error_events import log_event, safe_filename
from app.db.models import BatchItem, BatchJob
from app.helper_functions.safe_zip import ZipIngestError, extract_invoice_files_from_zip
from app.schemas.batch import (
    BatchItemResponse,
    BatchItemStatus,
    BatchJobResponse,
    BatchJobStatus,
)
from app.schemas.invoice import InvoiceParseResponse, ParseStatus, ValidationStatus
from app.services.auth_service import OrgContext
from app.services.export_service import (
    BatchPackageEntry,
    ExportService,
    invoice_is_exportable,
)
from app.services.invoice_service import InvoiceService
from app.services.plan_limits import PlanLimits
from app.services.quota_service import (
    assert_upload_size,
    consume_parse_count,
    limits_for_context,
    refund_parse_count,
)
from app.services.view_pdf_service import ViewPdfService, invoice_is_viewable

BATCH_FORBIDDEN_DETAIL: str = (
    "Batch-Upload ist in Plus enthalten. "
    "Mit Plus prüfen Sie mehrere Rechnungen auf einmal."
)
JOB_NOT_COMPLETE_DETAIL: str = "Auftrag ist noch nicht abgeschlossen."
ORIGINALS_GONE_DETAIL: str = (
    "Originaldateien sind nicht mehr verfügbar. Bitte den Auftrag erneut hochladen."
)
NO_EXPORTABLE_DETAIL: str = "Keine exportierbare Rechnung in diesem Auftrag."
NO_VIEWABLE_DETAIL: str = "Keine lesbare Rechnung in diesem Auftrag."
TERMINAL_ITEM_STATUSES: frozenset[str] = frozenset(
    {
        BatchItemStatus.GUELTIG.value,
        BatchItemStatus.PRUEFEN.value,
        BatchItemStatus.ABLEHNEN.value,
    }
)

_invoice_service: InvoiceService = InvoiceService()
_export_service: ExportService = ExportService()
_view_pdf_service: ViewPdfService = ViewPdfService()


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
    purge_expired_originals(session)
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
    purge_expired_originals(session)
    job: Optional[BatchJob] = session.scalar(
        select(BatchJob)
        .where(BatchJob.id == job_id, BatchJob.organization_id == org_context.organization_id)
        .options(selectinload(BatchJob.items))
    )
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auftrag nicht gefunden.")
    return to_response(job)


def build_batch_accountant_package(
    session: Session,
    org_context: OrgContext,
    job_id: UUID,
) -> tuple[bytes, str, str]:
    """Build one Steuerberater ZIP from a completed job while originals still exist."""
    entries, completed_at = _package_entries_for_job(session, org_context, job_id)
    return _export_service.build_batch_accountant_package(entries, completed_at)


def assert_batch_package_ready(
    session: Session,
    org_context: OrgContext,
    job_id: UUID,
) -> None:
    """Raise HTTPException if the job cannot produce an accountant ZIP yet."""
    _package_entries_for_job(session, org_context, job_id)


def build_batch_view_pdf_package(
    session: Session,
    org_context: OrgContext,
    job_id: UUID,
) -> tuple[bytes, str, str]:
    """Build a ZIP of working-copy PDFs from stored parse results."""
    invoices, completed_at = _viewable_invoices_for_job(session, org_context, job_id)
    return _view_pdf_service.render_batch(invoices, completed_at)


def assert_batch_view_pdfs_ready(
    session: Session,
    org_context: OrgContext,
    job_id: UUID,
) -> None:
    """Raise HTTPException if the job cannot produce working-copy PDFs yet."""
    _viewable_invoices_for_job(session, org_context, job_id)


def _package_entries_for_job(
    session: Session,
    org_context: OrgContext,
    job_id: UUID,
) -> tuple[list[BatchPackageEntry], datetime]:
    purge_expired_originals(session)
    job: Optional[BatchJob] = session.scalar(
        select(BatchJob)
        .where(BatchJob.id == job_id, BatchJob.organization_id == org_context.organization_id)
        .options(selectinload(BatchJob.items))
    )
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auftrag nicht gefunden.")
    if job.status != BatchJobStatus.COMPLETED.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=JOB_NOT_COMPLETE_DETAIL)
    if not _has_live_originals(job):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=ORIGINALS_GONE_DETAIL)

    entries: list[BatchPackageEntry] = []
    for item in job.items:
        invoice: Optional[InvoiceParseResponse] = None
        if item.result_json:
            invoice = InvoiceParseResponse.model_validate(item.result_json)
        original_bytes: Optional[bytes] = None
        if item.storage_path:
            path: Path = Path(item.storage_path)
            if path.is_file():
                original_bytes = path.read_bytes()
        entries.append(
            BatchPackageEntry(
                filename=item.filename,
                original_bytes=original_bytes,
                invoice=invoice,
            )
        )
    if not any(entry.invoice is not None and invoice_is_exportable(entry.invoice) for entry in entries):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=NO_EXPORTABLE_DETAIL)

    completed_at: datetime = as_utc(job.completed_at) if job.completed_at is not None else utc_now()
    return entries, completed_at


def _viewable_invoices_for_job(
    session: Session,
    org_context: OrgContext,
    job_id: UUID,
) -> tuple[list[InvoiceParseResponse], datetime]:
    purge_expired_originals(session)
    job: Optional[BatchJob] = session.scalar(
        select(BatchJob)
        .where(BatchJob.id == job_id, BatchJob.organization_id == org_context.organization_id)
        .options(selectinload(BatchJob.items))
    )
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auftrag nicht gefunden.")
    if job.status != BatchJobStatus.COMPLETED.value:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=JOB_NOT_COMPLETE_DETAIL)

    invoices: list[InvoiceParseResponse] = []
    for item in job.items:
        if not item.result_json:
            continue
        invoice: InvoiceParseResponse = InvoiceParseResponse.model_validate(item.result_json)
        if invoice_is_viewable(invoice):
            invoices.append(invoice)
    if not invoices:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=NO_VIEWABLE_DETAIL)

    completed_at: datetime = as_utc(job.completed_at) if job.completed_at is not None else utc_now()
    return invoices, completed_at


def process_next_item() -> bool:
    """Claim one queued file, parse it, store metadata. Original stays until TTL. False if idle."""
    from app.db.session import get_session_factory

    factory: Optional[sessionmaker[Session]] = get_session_factory()
    if factory is None:
        return False
    session: Session = factory()
    try:
        purge_expired_originals(session)
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
        export_package_available=_export_package_available(job),
        view_pdf_package_available=_view_pdf_package_available(job),
    )


def purge_expired_originals(session: Session) -> int:
    """Delete temp originals after TTL. Metadata and result JSON stay."""
    jobs: list[BatchJob] = list(
        session.scalars(
            select(BatchJob)
            .where(BatchJob.status == BatchJobStatus.COMPLETED.value)
            .options(selectinload(BatchJob.items))
        ).all()
    )
    removed: int = 0
    purged_jobs: int = 0
    for job in jobs:
        if not _originals_expired(job):
            continue
        cleared: int = _clear_job_originals(job)
        if cleared:
            purged_jobs += 1
            removed += cleared
    if removed:
        session.commit()
        log_event(
            logging.INFO,
            "batch_originals_purged",
            fields={"jobs": purged_jobs, "files": removed},
        )
    return removed


async def _read_uploads(
    uploads: list[UploadFile],
    limits: PlanLimits,
) -> list[tuple[str, bytes]]:
    if not uploads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keine Dateien übermittelt.",
        )
    payloads: list[tuple[str, bytes]] = []
    for upload in uploads:
        filename: str = _safe_filename(upload.filename)
        suffix: str = Path(filename).suffix.lower()
        content: bytes = await upload.read()
        if len(content) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Datei ist leer: {safe_filename(filename)}",
            )
        assert_upload_size(len(content), limits)
        if suffix == ".zip":
            payloads.extend(_expand_zip(content, limits))
            continue
        if suffix not in settings.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Nicht unterstützter Dateityp. Erlaubt: {', '.join(settings.allowed_extensions)} und .zip",
            )
        payloads.append((filename, content))
    if not payloads:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keine XML- oder PDF-Dateien gefunden.",
        )
    if len(payloads) > limits.max_batch_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Maximal {limits.max_batch_files} Dateien pro Auftrag "
                f"in Ihrem Tarif {limits.name}."
            ),
        )
    return payloads


def _expand_zip(content: bytes, limits: PlanLimits) -> list[tuple[str, bytes]]:
    max_file_bytes: int = limits.max_upload_size_mb * 1024 * 1024
    plan_cap: int = max_file_bytes * max(1, limits.max_batch_files)
    settings_cap: int = settings.zip_max_uncompressed_mb * 1024 * 1024
    try:
        extracted: list[tuple[str, bytes]] = extract_invoice_files_from_zip(
            content,
            max_files=limits.max_batch_files,
            max_file_bytes=max_file_bytes,
            max_uncompressed_bytes=min(plan_cap, settings_cap),
            max_ratio=settings.zip_max_ratio,
            max_listed_entries=settings.zip_max_listed_entries,
        )
    except ZipIngestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.detail) from exc
    for filename, payload in extracted:
        member_bytes: bytes = payload
        assert_upload_size(len(member_bytes), limits)
        if filename.strip() == "":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dateiname fehlt.")
    return extracted


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

    session = factory()
    try:
        item = session.get(BatchItem, item_id)
        if item is None:
            return
        _apply_parse_result(item, response)
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


def _export_package_available(job: BatchJob) -> bool:
    if job.status != BatchJobStatus.COMPLETED.value:
        return False
    if not _has_live_originals(job):
        return False
    for item in job.items:
        if not item.result_json:
            continue
        invoice: InvoiceParseResponse = InvoiceParseResponse.model_validate(item.result_json)
        if invoice_is_exportable(invoice):
            return True
    return False


def _view_pdf_package_available(job: BatchJob) -> bool:
    if job.status != BatchJobStatus.COMPLETED.value:
        return False
    for item in job.items:
        if not item.result_json:
            continue
        invoice: InvoiceParseResponse = InvoiceParseResponse.model_validate(item.result_json)
        if invoice_is_viewable(invoice):
            return True
    return False


def _has_live_originals(job: BatchJob) -> bool:
    if _originals_expired(job):
        return False
    for item in job.items:
        if item.storage_path and Path(item.storage_path).is_file():
            return True
    return False


def _originals_expired(job: BatchJob) -> bool:
    if job.completed_at is None:
        return False
    expires_at: datetime = as_utc(job.completed_at) + timedelta(
        seconds=max(0, settings.batch_original_ttl_seconds)
    )
    return utc_now() >= expires_at


def _clear_job_originals(job: BatchJob) -> int:
    removed: int = 0
    for item in job.items:
        if not item.storage_path:
            continue
        _unlink_quietly(item.storage_path)
        item.storage_path = None
        removed += 1
    _remove_job_dir(job.id)
    return removed


def _safe_filename(name: Optional[str]) -> str:
    raw: str = (name or "").strip()
    base: str = Path(raw).name
    if not base or base in {".", ".."}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dateiname fehlt.")
    return base[:255]


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
