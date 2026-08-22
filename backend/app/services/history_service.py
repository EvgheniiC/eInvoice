"""Opt-in invoice history. Writes nothing unless the organization consented."""

from __future__ import annotations

import hashlib
import logging
import shutil
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.clock import as_utc, usage_timezone, utc_now
from app.core.config import settings
from app.core.error_events import log_event, safe_filename
from app.db.models import InvoiceHistory, Organization
from app.schemas.history import HistoryItemResponse, HistoryItemStatus, HistoryListResponse, HistorySource
from app.schemas.invoice import (
    DuplicateMatch,
    DuplicateMatchKind,
    InvoiceParseResponse,
    ParseStatus,
    ValidationStatus,
)
from app.services.auth_service import OrgContext
from app.services.export_service import ExportService, invoice_is_exportable

HISTORY_FORBIDDEN_DETAIL: str = (
    "Verlauf ist in Plus enthalten. "
    "Mit Plus speichern Sie Metadaten geprüfter Rechnungen."
)
ORIGINALS_GONE_DETAIL: str = (
    "Die Originaldatei ist nicht mehr verfügbar. Bitte die Rechnung erneut hochladen."
)
NO_EXPORTABLE_DETAIL: str = "Diese Rechnung kann nicht erneut exportiert werden."
NOT_FOUND_DETAIL: str = "Eintrag nicht gefunden."
DUPLICATE_MESSAGE_TEMPLATE: str = "Diesen Beleg haben Sie bereits am {date} verarbeitet."

_export_service: ExportService = ExportService()


def hash_file_bytes(content: bytes) -> str:
    """SHA-256 hex digest of the uploaded bytes. Used for later duplicate detection."""
    return hashlib.sha256(content).hexdigest()


def format_duplicate_date(processed_at: datetime) -> str:
    """Calendar day in Europe/Berlin for the user-facing duplicate sentence."""
    local: datetime = as_utc(processed_at).astimezone(usage_timezone())
    return local.strftime("%d.%m.%Y")


def duplicate_message(processed_at: datetime) -> str:
    return DUPLICATE_MESSAGE_TEMPLATE.format(date=format_duplicate_date(processed_at))


def attach_duplicate_hint(
    session: Optional[Session],
    *,
    organization_id: Optional[UUID],
    content: bytes,
    response: InvoiceParseResponse,
) -> InvoiceParseResponse:
    """Annotate a parse result when the org already processed this Beleg."""
    if session is None or organization_id is None:
        return response
    match: Optional[DuplicateMatch] = find_prior_duplicate(
        session,
        organization_id=organization_id,
        content=content,
        response=response,
    )
    if match is None:
        return response
    response.duplicate = match
    return response


def find_prior_duplicate(
    session: Session,
    *,
    organization_id: UUID,
    content: bytes,
    response: InvoiceParseResponse,
) -> Optional[DuplicateMatch]:
    """Exact file first (cheap), then seller + number + date + brutto."""
    organization: Optional[Organization] = session.get(Organization, organization_id)
    if organization is None or not organization.history_enabled:
        return None
    if organization.plan is None or not organization.plan.allows_history:
        return None
    file_row: Optional[InvoiceHistory] = _latest_file_match(
        session,
        organization_id=organization_id,
        file_hash=hash_file_bytes(content),
    )
    if file_row is not None:
        return _to_duplicate_match(file_row, "file")
    content_row: Optional[InvoiceHistory] = _latest_content_match(
        session,
        organization_id=organization_id,
        response=response,
    )
    if content_row is not None:
        return _to_duplicate_match(content_row, "content")
    return None


def require_history_plan(org_context: Optional[OrgContext]) -> OrgContext:
    if org_context is None or not org_context.allows_history:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=HISTORY_FORBIDDEN_DETAIL,
        )
    return org_context


def record_parse_history(
    session: Optional[Session],
    org_context: Optional[OrgContext],
    *,
    filename: str,
    content: bytes,
    response: InvoiceParseResponse,
    source: HistorySource = "parse",
    batch_job_id: Optional[UUID] = None,
    commit: bool = True,
) -> Optional[InvoiceHistory]:
    """Persist metadata when the org opted in. Never blocks the parse result."""
    if session is None or org_context is None or not org_context.allows_history:
        return None
    return record_history_for_organization(
        session,
        organization_id=org_context.organization_id,
        user_id=org_context.user_id,
        filename=filename,
        content=content,
        response=response,
        source=source,
        batch_job_id=batch_job_id,
        commit=commit,
    )


def record_history_for_organization(
    session: Session,
    *,
    organization_id: UUID,
    user_id: Optional[UUID],
    filename: str,
    content: bytes,
    response: InvoiceParseResponse,
    source: HistorySource,
    batch_job_id: Optional[UUID] = None,
    commit: bool = True,
) -> Optional[InvoiceHistory]:
    organization: Optional[Organization] = session.get(Organization, organization_id)
    if organization is None or not organization.history_enabled:
        return None
    if organization.plan is None or not organization.plan.allows_history:
        return None
    purge_expired_originals(session)
    record: InvoiceHistory = InvoiceHistory(
        organization_id=organization_id,
        created_by_user_id=user_id,
        processed_at=utc_now(),
        filename=filename[:255],
        file_hash=hash_file_bytes(content),
        seller_name=_clip(response.seller.name if response.seller is not None else None, 255),
        invoice_number=_clip(response.invoice_number, 128),
        issue_date=_clip(response.issue_date, 32),
        gross_amount=_gross_amount(response),
        currency=_clip(response.totals.currency if response.totals is not None else None, 8),
        status=_history_status(response),
        source=source,
        batch_job_id=batch_job_id,
    )
    session.add(record)
    session.flush()
    if organization.store_originals_enabled and content:
        _store_original(record, filename, content, response)
    if commit:
        session.commit()
    log_event(
        logging.INFO,
        "history_recorded",
        fields={
            "organization_id": str(organization_id),
            "history_id": str(record.id),
            "source": source,
            "stored_original": record.original_storage_path is not None,
        },
    )
    return record


def list_history(
    session: Session,
    org_context: OrgContext,
    *,
    limit: int,
    offset: int,
) -> HistoryListResponse:
    require_history_plan(org_context)
    purge_expired_originals(session)
    organization: Organization = _require_organization(session, org_context.organization_id)
    safe_limit: int = min(max(limit, 1), 100)
    safe_offset: int = max(offset, 0)
    total: int = int(
        session.scalar(
            select(func.count()).select_from(InvoiceHistory).where(
                InvoiceHistory.organization_id == org_context.organization_id
            )
        )
        or 0
    )
    rows: list[InvoiceHistory] = list(
        session.scalars(
            select(InvoiceHistory)
            .where(InvoiceHistory.organization_id == org_context.organization_id)
            .order_by(InvoiceHistory.processed_at.desc())
            .limit(safe_limit)
            .offset(safe_offset)
        ).all()
    )
    return HistoryListResponse(
        items=[_item_response(row) for row in rows],
        total=total,
        history_enabled=organization.history_enabled,
        store_originals_enabled=organization.store_originals_enabled,
        original_retention_days=settings.history_original_retention_days,
    )


def build_history_accountant_package(
    session: Session,
    org_context: OrgContext,
    record_id: UUID,
) -> tuple[bytes, str, str]:
    require_history_plan(org_context)
    purge_expired_originals(session)
    record: InvoiceHistory = _require_record(session, org_context.organization_id, record_id)
    if not _original_is_available(record):
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=ORIGINALS_GONE_DETAIL)
    if not record.result_json:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=ORIGINALS_GONE_DETAIL)
    invoice: InvoiceParseResponse = InvoiceParseResponse.model_validate(record.result_json)
    if not invoice_is_exportable(invoice):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=NO_EXPORTABLE_DETAIL)
    content: bytes = Path(str(record.original_storage_path)).read_bytes()
    pdf_bytes: Optional[bytes]
    xml_bytes: Optional[bytes]
    pdf_bytes, xml_bytes = _split_original(record.filename, content)
    return _export_service.build_accountant_package(
        invoice=invoice,
        pdf_bytes=pdf_bytes,
        pdf_filename=record.filename if pdf_bytes is not None else None,
        xml_bytes=xml_bytes,
        xml_filename=record.filename if xml_bytes is not None else None,
    )


def purge_expired_originals(session: Session) -> None:
    now: datetime = utc_now()
    rows: list[InvoiceHistory] = list(
        session.scalars(
            select(InvoiceHistory).where(
                InvoiceHistory.original_storage_path.is_not(None),
                InvoiceHistory.original_expires_at.is_not(None),
                InvoiceHistory.original_expires_at <= now,
            )
        ).all()
    )
    if not rows:
        return
    for row in rows:
        _clear_original(row)
    session.commit()
    log_event(logging.INFO, "history_originals_purged", fields={"count": len(rows)})


def purge_originals_for_organization(session: Session, organization_id: UUID) -> None:
    """Withdrawn «Dateien merken»: drop originals and parse snapshots, keep metadata."""
    rows: list[InvoiceHistory] = list(
        session.scalars(
            select(InvoiceHistory).where(InvoiceHistory.organization_id == organization_id)
        ).all()
    )
    for row in rows:
        _clear_original(row)
    org_dir: Path = settings.resolved_history_original_dir / str(organization_id)
    shutil.rmtree(org_dir, ignore_errors=True)


def purge_history_for_organization(session: Session, organization_id: UUID) -> None:
    """Remove files before the organization row is deleted."""
    purge_originals_for_organization(session, organization_id)
    rows: list[InvoiceHistory] = list(
        session.scalars(
            select(InvoiceHistory).where(InvoiceHistory.organization_id == organization_id)
        ).all()
    )
    for row in rows:
        session.delete(row)


def _store_original(
    record: InvoiceHistory,
    filename: str,
    content: bytes,
    response: InvoiceParseResponse,
) -> None:
    suffix: str = Path(filename).suffix.lower()
    if suffix not in {".xml", ".pdf"}:
        suffix = ".bin"
    path: Path = (
        settings.resolved_history_original_dir / str(record.organization_id) / f"{record.id}{suffix}"
    )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    except OSError as exc:
        log_event(
            logging.ERROR,
            "history_original_write_failed",
            fields={
                "history_id": str(record.id),
                "filename": safe_filename(filename),
                "exc_type": type(exc).__name__,
            },
        )
        return
    record.original_storage_path = str(path)
    record.original_expires_at = utc_now() + timedelta(days=settings.history_original_retention_days)
    record.result_json = response.model_dump(mode="json")


def _clear_original(row: InvoiceHistory) -> None:
    stored: Optional[str] = row.original_storage_path
    if stored:
        path: Path = Path(stored)
        path.unlink(missing_ok=True)
        parent: Path = path.parent
        try:
            if parent.is_dir() and not any(parent.iterdir()):
                parent.rmdir()
        except OSError:
            pass
    row.original_storage_path = None
    row.original_expires_at = None
    row.result_json = None


def _original_is_available(record: InvoiceHistory) -> bool:
    if not record.original_storage_path:
        return False
    if record.original_expires_at is not None and as_utc(record.original_expires_at) <= utc_now():
        return False
    return Path(record.original_storage_path).is_file()


def _item_response(row: InvoiceHistory) -> HistoryItemResponse:
    return HistoryItemResponse(
        id=row.id,
        processed_at=row.processed_at,
        filename=row.filename,
        file_hash=row.file_hash,
        seller_name=row.seller_name,
        invoice_number=row.invoice_number,
        issue_date=row.issue_date,
        gross_amount=row.gross_amount,
        currency=row.currency,
        status=row.status,  # type: ignore[arg-type]
        source=row.source,  # type: ignore[arg-type]
        original_available=_original_is_available(row),
        original_expires_at=row.original_expires_at,
    )


def _history_status(response: InvoiceParseResponse) -> HistoryItemStatus:
    if response.status == ParseStatus.ERROR:
        return "ablehnen"
    if response.validation_status == ValidationStatus.VALID:
        return "gueltig"
    if response.validation_status == ValidationStatus.INVALID:
        return "ablehnen"
    return "pruefen"


def _gross_amount(response: InvoiceParseResponse) -> Optional[str]:
    if response.totals is None or response.totals.gross is None:
        return None
    return str(response.totals.gross)[:32]


def _clip(value: Optional[str], max_length: int) -> Optional[str]:
    if value is None:
        return None
    stripped: str = value.strip()
    if not stripped:
        return None
    return stripped[:max_length]


def _split_original(filename: str, content: bytes) -> tuple[Optional[bytes], Optional[bytes]]:
    if filename.lower().endswith(".pdf"):
        return content, None
    return None, content


def _require_organization(session: Session, organization_id: UUID) -> Organization:
    organization: Optional[Organization] = session.get(Organization, organization_id)
    if organization is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organisation nicht gefunden.",
        )
    return organization


def _require_record(session: Session, organization_id: UUID, record_id: UUID) -> InvoiceHistory:
    record: Optional[InvoiceHistory] = session.get(InvoiceHistory, record_id)
    if record is None or record.organization_id != organization_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=NOT_FOUND_DETAIL)
    return record


def _latest_file_match(
    session: Session,
    *,
    organization_id: UUID,
    file_hash: str,
) -> Optional[InvoiceHistory]:
    return session.scalar(
        select(InvoiceHistory)
        .where(
            InvoiceHistory.organization_id == organization_id,
            InvoiceHistory.file_hash == file_hash,
        )
        .order_by(InvoiceHistory.processed_at.desc())
        .limit(1)
    )


def _latest_content_match(
    session: Session,
    *,
    organization_id: UUID,
    response: InvoiceParseResponse,
) -> Optional[InvoiceHistory]:
    invoice_number: Optional[str] = _clip(response.invoice_number, 128)
    issue_date: Optional[str] = _clip(response.issue_date, 32)
    seller_name: Optional[str] = _clip(
        response.seller.name if response.seller is not None else None,
        255,
    )
    gross_amount: Optional[str] = _gross_amount(response)
    if invoice_number is None or issue_date is None or seller_name is None or gross_amount is None:
        return None
    candidates: list[InvoiceHistory] = list(
        session.scalars(
            select(InvoiceHistory)
            .where(
                InvoiceHistory.organization_id == organization_id,
                InvoiceHistory.invoice_number.is_not(None),
                func.lower(InvoiceHistory.invoice_number) == invoice_number.casefold(),
                InvoiceHistory.issue_date == issue_date,
            )
            .order_by(InvoiceHistory.processed_at.desc())
            .limit(25)
        ).all()
    )
    for row in candidates:
        if row.seller_name is None or row.seller_name.casefold() != seller_name.casefold():
            continue
        if not _amounts_equal(row.gross_amount, gross_amount):
            continue
        return row
    return None


def _to_duplicate_match(row: InvoiceHistory, kind: DuplicateMatchKind) -> DuplicateMatch:
    return DuplicateMatch(
        processed_at=as_utc(row.processed_at),
        message=duplicate_message(row.processed_at),
        match=kind,
        history_id=row.id,
    )


def _amounts_equal(stored: Optional[str], incoming: Optional[str]) -> bool:
    if stored is None or incoming is None:
        return False
    try:
        return Decimal(stored) == Decimal(incoming)
    except InvalidOperation:
        return stored == incoming
