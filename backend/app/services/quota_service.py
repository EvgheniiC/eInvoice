"""Daily parse/export quotas, upload size, and parse parallelism."""

from __future__ import annotations

import hashlib
import logging
import threading
from collections import defaultdict
from contextlib import contextmanager
from datetime import date, datetime, time, timedelta, tzinfo
from typing import Iterator, Optional
from uuid import UUID

from fastapi import HTTPException, Request, status
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.clock import usage_date_today, usage_timezone, utc_now
from app.core.config import settings
from app.core.error_events import log_event
from app.core.http_security import client_key
from app.db.models import Plan, UsageCounter
from app.schemas.auth import PlanInfo
from app.services.auth_service import OrgContext
from app.services.plan_limits import (
    PlanLimits,
    guest_limits,
    merge_plan_row,
    upgrade_cta,
)

ACTION_PARSE: str = "parse"
ACTION_EXPORT: str = "export"
SUBJECT_GUEST: str = "guest"
SUBJECT_ORG: str = "org"
PARALLEL_RETRY_AFTER_SECONDS: int = 10

_memory_lock: threading.Lock = threading.Lock()
_memory_counts: dict[tuple[str, str, date, str], int] = {}
_inflight_lock: threading.Lock = threading.Lock()
_inflight: dict[str, int] = defaultdict(int)


class QuotaExceededError(Exception):
    """Daily quota or parallelism exhausted. Converted to HTTP 429."""

    def __init__(self, detail: str, retry_after: int, event: str) -> None:
        super().__init__(detail)
        self.detail: str = detail
        self.retry_after: int = retry_after
        self.event: str = event


def reset_quota_runtime() -> None:
    """Clear in-memory counters and inflight slots (tests)."""
    with _memory_lock:
        _memory_counts.clear()
    with _inflight_lock:
        _inflight.clear()


def limits_for_context(org_context: Optional[OrgContext]) -> PlanLimits:
    if org_context is None:
        return guest_limits()
    return merge_plan_row(
        code=org_context.plan_code,
        name=org_context.plan_name,
        parse_per_day=org_context.parse_per_day,
        export_per_day=org_context.export_per_day,
        max_upload_size_mb=org_context.max_upload_size_mb,
        max_parallel=org_context.max_parallel,
        allows_batch=org_context.allows_batch,
        allows_history=org_context.allows_history,
    )


def subject_for(request: Request, org_context: Optional[OrgContext]) -> tuple[str, str]:
    if org_context is not None:
        return SUBJECT_ORG, str(org_context.organization_id)
    return SUBJECT_GUEST, _guest_subject_key(request)


def assert_upload_size(size_bytes: int, limits: PlanLimits) -> None:
    max_bytes: int = limits.max_upload_size_mb * 1024 * 1024
    if size_bytes <= max_bytes:
        return
    if limits.code in {"guest", "free"}:
        detail: str = (
            f"Datei ist zu groß. Maximum: {limits.max_upload_size_mb} MB."
            " Mit Plus sind größere Dateien möglich."
        )
    else:
        detail = f"Datei ist zu groß. Maximum für Ihren Tarif: {limits.max_upload_size_mb} MB."
    raise HTTPException(
        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        detail=detail,
    )


@contextmanager
def enforce_parse(
    request: Request,
    db: Optional[Session],
    org_context: Optional[OrgContext],
    size_bytes: int,
) -> Iterator[None]:
    """Check size, take a parallel slot, then consume one daily parse."""
    limits: PlanLimits = limits_for_context(org_context)
    assert_upload_size(size_bytes, limits)
    subject_type, subject_key = subject_for(request, org_context)
    try:
        with _parallel_slot(subject_key, limits.max_parallel):
            _consume(db, subject_type, subject_key, ACTION_PARSE, limits)
            yield
    except QuotaExceededError as exc:
        raise quota_http_exception(exc) from exc


@contextmanager
def enforce_export(
    request: Request,
    db: Optional[Session],
    org_context: Optional[OrgContext],
) -> Iterator[None]:
    """Consume one daily export (CSV/Excel/DATEV or accountant ZIP)."""
    limits: PlanLimits = limits_for_context(org_context)
    subject_type, subject_key = subject_for(request, org_context)
    try:
        _consume(db, subject_type, subject_key, ACTION_EXPORT, limits)
        yield
    except QuotaExceededError as exc:
        raise quota_http_exception(exc) from exc


def consume_parse_count(
    db: Session,
    org_context: OrgContext,
    count: int,
) -> None:
    """Consume `count` daily parse slots for an organization (batch enqueue)."""
    if count <= 0:
        return
    limits: PlanLimits = limits_for_context(org_context)
    try:
        _consume(
            db,
            SUBJECT_ORG,
            str(org_context.organization_id),
            ACTION_PARSE,
            limits,
            amount=count,
        )
    except QuotaExceededError as exc:
        raise quota_http_exception(exc) from exc


def refund_parse_count(db: Session, org_context: OrgContext, count: int) -> None:
    """Undo a failed batch enqueue that already consumed parse slots."""
    if count <= 0:
        return
    today: date = usage_date_today()
    _db_add(db, SUBJECT_ORG, str(org_context.organization_id), ACTION_PARSE, today, -count)


def quota_http_exception(exc: QuotaExceededError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=exc.detail,
        headers={"Retry-After": str(exc.retry_after)},
    )


def build_plan_info(db: Optional[Session], context: OrgContext) -> PlanInfo:
    limits: PlanLimits = limits_for_context(context)
    used_parse: int = 0
    used_export: int = 0
    if db is not None:
        used_parse, used_export = read_usage(db, SUBJECT_ORG, str(context.organization_id))
    return _plan_info(limits, used_parse=used_parse, used_export=used_export)


def build_plan_info_for_org(db: Session, organization_id: UUID, plan: Plan) -> PlanInfo:
    limits: PlanLimits = merge_plan_row(
        code=plan.code,
        name=plan.name,
        parse_per_day=plan.parse_per_day,
        export_per_day=plan.export_per_day,
        max_upload_size_mb=plan.max_upload_size_mb,
        max_parallel=plan.max_parallel,
        allows_batch=plan.allows_batch,
        allows_history=plan.allows_history,
    )
    used_parse, used_export = read_usage(db, SUBJECT_ORG, str(organization_id))
    return _plan_info(limits, used_parse=used_parse, used_export=used_export)


def read_usage(db: Session, subject_type: str, subject_key: str) -> tuple[int, int]:
    today: date = usage_date_today()
    rows: list[UsageCounter] = list(
        db.scalars(
            select(UsageCounter).where(
                UsageCounter.subject_type == subject_type,
                UsageCounter.subject_key == subject_key,
                UsageCounter.usage_date == today,
            )
        ).all()
    )
    used_parse: int = 0
    used_export: int = 0
    for row in rows:
        if row.action == ACTION_PARSE:
            used_parse = row.count
        elif row.action == ACTION_EXPORT:
            used_export = row.count
    return used_parse, used_export


def _plan_info(limits: PlanLimits, *, used_parse: int, used_export: int) -> PlanInfo:
    return PlanInfo(
        code=limits.code,
        name=limits.name,
        parse_per_day=limits.parse_per_day,
        export_per_day=limits.export_per_day,
        max_upload_size_mb=limits.max_upload_size_mb,
        max_parallel=limits.max_parallel,
        allows_batch=limits.allows_batch,
        allows_history=limits.allows_history,
        max_batch_files=limits.max_batch_files,
        quotas_enforced=True,
        parse_used_today=used_parse,
        export_used_today=used_export,
    )


def _consume(
    db: Optional[Session],
    subject_type: str,
    subject_key: str,
    action: str,
    limits: PlanLimits,
    amount: int = 1,
) -> None:
    if amount <= 0:
        return
    limit: int = limits.parse_per_day if action == ACTION_PARSE else limits.export_per_day
    if limit <= 0:
        return
    today: date = usage_date_today()
    if db is not None:
        count: int = _db_add(db, subject_type, subject_key, action, today, amount)
    else:
        count = _memory_add(subject_type, subject_key, action, today, amount)
    if count <= limit:
        return
    if db is not None:
        _db_add(db, subject_type, subject_key, action, today, -amount)
    else:
        _memory_add(subject_type, subject_key, action, today, -amount)
    noun: str = "Prüfungen" if action == ACTION_PARSE else "Exporte"
    detail: str = (
        f"Tageslimit für {noun} erreicht ({limit} pro Tag)." + upgrade_cta(limits.code)
    )
    log_event(
        logging.WARNING,
        "quota_exceeded",
        fields={
            "action": action,
            "plan": limits.code,
            "subject_type": subject_type,
            "limit": limit,
        },
    )
    raise QuotaExceededError(
        detail=detail,
        retry_after=_seconds_until_next_usage_day(),
        event="quota_exceeded",
    )


@contextmanager
def _parallel_slot(subject_key: str, max_parallel: int) -> Iterator[None]:
    if max_parallel <= 0:
        yield
        return
    with _inflight_lock:
        current: int = _inflight[subject_key]
        if current >= max_parallel:
            log_event(
                logging.WARNING,
                "parallel_limit",
                fields={"subject_present": True, "limit": max_parallel},
            )
            raise QuotaExceededError(
                detail="Es läuft bereits eine Prüfung. Bitte warten Sie einen Moment.",
                retry_after=PARALLEL_RETRY_AFTER_SECONDS,
                event="parallel_limit",
            )
        _inflight[subject_key] = current + 1
    try:
        yield
    finally:
        with _inflight_lock:
            leftover: int = _inflight[subject_key] - 1
            if leftover <= 0:
                _inflight.pop(subject_key, None)
            else:
                _inflight[subject_key] = leftover


def _guest_subject_key(request: Request) -> str:
    material: str = f"{settings.auth_secret_key}:{client_key(request)}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def _memory_add(
    subject_type: str,
    subject_key: str,
    action: str,
    today: date,
    amount: int,
) -> int:
    key: tuple[str, str, date, str] = (subject_type, subject_key, today, action)
    with _memory_lock:
        _purge_memory(today)
        next_count: int = max(0, _memory_counts.get(key, 0) + amount)
        if next_count <= 0:
            _memory_counts.pop(key, None)
            return 0
        _memory_counts[key] = next_count
        return next_count


def _purge_memory(today: date) -> None:
    stale: list[tuple[str, str, date, str]] = [
        key for key in _memory_counts if key[2] < today
    ]
    for key in stale:
        _memory_counts.pop(key, None)


def _db_add(
    session: Session,
    subject_type: str,
    subject_key: str,
    action: str,
    today: date,
    amount: int,
) -> int:
    session.execute(
        delete(UsageCounter).where(
            UsageCounter.subject_type == subject_type,
            UsageCounter.subject_key == subject_key,
            UsageCounter.usage_date < today,
        )
    )
    row: Optional[UsageCounter] = _load_counter(session, subject_type, subject_key, action, today)
    if row is None:
        initial: int = max(0, amount)
        row = UsageCounter(
            subject_type=subject_type,
            subject_key=subject_key,
            usage_date=today,
            action=action,
            count=initial,
        )
        session.add(row)
        try:
            session.commit()
            return initial
        except IntegrityError:
            session.rollback()
            row = _load_counter(session, subject_type, subject_key, action, today)
            if row is None:
                return initial
    row.count = max(0, row.count + amount)
    session.commit()
    return row.count


def _load_counter(
    session: Session,
    subject_type: str,
    subject_key: str,
    action: str,
    today: date,
) -> Optional[UsageCounter]:
    return session.scalar(
        select(UsageCounter).where(
            UsageCounter.subject_type == subject_type,
            UsageCounter.subject_key == subject_key,
            UsageCounter.usage_date == today,
            UsageCounter.action == action,
        )
    )


def _seconds_until_next_usage_day() -> int:
    tz: tzinfo = usage_timezone()
    now: datetime = utc_now().astimezone(tz)
    tomorrow: datetime = datetime.combine(now.date() + timedelta(days=1), time.min, tzinfo=tz)
    return max(1, int((tomorrow - now).total_seconds()))
