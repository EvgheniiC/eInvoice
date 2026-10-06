"""Unique daily visits and paid-plan headcount for administrators."""

from __future__ import annotations

import hashlib
import logging
import re
import secrets
import uuid
from datetime import date, timedelta
from typing import Optional, Sequence

from sqlalchemy import delete, distinct, func, select
from sqlalchemy.engine import Row
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings
from app.core.clock import usage_date_today
from app.core.error_events import log_event
from app.db.models import Membership, Organization, Plan, SiteVisit
from app.db.session import get_session_factory
from app.schemas.stats import PAID_PLAN_CODES, VISIT_HISTORY_DAYS, AdminStatsResponse, VisitDayStat

VISITOR_COOKIE_NAME: str = "einv_visitor"
VISIT_RETENTION_DAYS: int = 30
VISITOR_COOKIE_MAX_AGE_SECONDS: int = 400 * 24 * 60 * 60
_VISITOR_ID_RE: re.Pattern[str] = re.compile(r"^[a-f0-9]{32}$")
_SKIP_PREFIXES: tuple[str, ...] = ("/api/health", "/metrics")


def should_track_request(request: Request) -> bool:
    """Count page and API traffic, not probes that would invent visitors."""
    if not settings.auth_enabled:
        return False
    if request.method == "OPTIONS":
        return False
    path: str = request.url.path
    return not any(path == prefix or path.startswith(prefix + "/") for prefix in _SKIP_PREFIXES)


def resolve_visitor_id(request: Request) -> tuple[str, bool]:
    """Return the browser id and whether a new cookie must be set."""
    current: str = request.cookies.get(VISITOR_COOKIE_NAME, "")
    if _VISITOR_ID_RE.fullmatch(current):
        return current, False
    return secrets.token_hex(16), True


def apply_visitor_cookie(response: Response, raw_id: str) -> None:
    """Store a random browser id. The database keeps only its hash."""
    response.set_cookie(
        key=VISITOR_COOKIE_NAME,
        value=raw_id,
        httponly=True,
        samesite="lax",
        secure=settings.is_production,
        path="/",
        max_age=VISITOR_COOKIE_MAX_AGE_SECONDS,
    )


def visitor_storage_key(raw_id: str) -> str:
    """Hash the cookie so a database copy cannot be used as the cookie itself."""
    material: str = f"{settings.auth_secret_key}:visit:{raw_id}"
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:32]


def record_site_visit(raw_id: str) -> None:
    """Insert one row per browser per calendar day. Failures must not break the request."""
    factory: Optional[sessionmaker[Session]] = get_session_factory()
    if factory is None or not _VISITOR_ID_RE.fullmatch(raw_id):
        return
    today: date = usage_date_today()
    key: str = visitor_storage_key(raw_id)
    session: Session = factory()
    try:
        cutoff: date = today - timedelta(days=VISIT_RETENTION_DAYS)
        session.execute(delete(SiteVisit).where(SiteVisit.visit_date < cutoff))
        existing: Optional[uuid.UUID] = session.scalar(
            select(SiteVisit.id).where(
                SiteVisit.visit_date == today,
                SiteVisit.visitor_key == key,
            )
        )
        if existing is None:
            session.add(SiteVisit(visit_date=today, visitor_key=key))
        session.commit()
    except IntegrityError:
        session.rollback()
    except Exception:
        session.rollback()
        log_event(logging.WARNING, "site_visit_record_failed")
    finally:
        session.close()


def load_admin_stats(session: Session) -> AdminStatsResponse:
    """Visitors for the recent days and distinct people on Plus or Team."""
    today: date = usage_date_today()
    start: date = today - timedelta(days=VISIT_HISTORY_DAYS - 1)
    rows: Sequence[Row[tuple[date, int]]] = session.execute(
        select(SiteVisit.visit_date, func.count())
        .where(SiteVisit.visit_date >= start, SiteVisit.visit_date <= today)
        .group_by(SiteVisit.visit_date)
    ).all()
    counts: dict[date, int] = {row[0]: int(row[1]) for row in rows}
    days: list[VisitDayStat] = []
    for offset in range(VISIT_HISTORY_DAYS):
        day: date = today - timedelta(days=offset)
        days.append(VisitDayStat(visit_date=day, visitors=counts.get(day, 0)))
    paid_users: int = int(
        session.scalar(
            select(func.count(distinct(Membership.user_id)))
            .select_from(Membership)
            .join(Organization, Organization.id == Membership.organization_id)
            .join(Plan, Plan.id == Organization.plan_id)
            .where(Plan.code.in_(PAID_PLAN_CODES))
        )
        or 0
    )
    return AdminStatsResponse(
        visits_today=counts.get(today, 0),
        visits_by_day=days,
        paid_plan_users=paid_users,
    )
