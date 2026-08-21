"""Seed built-in plans. Idempotent; refreshes catalog quota columns."""

from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Plan
from app.services.plan_limits import PLAN_CATALOG, PlanLimits


def seed_plans(session: Session) -> None:
    """Insert or update free/plus/team from the catalog."""
    for limits in PLAN_CATALOG.values():
        existing: Optional[Plan] = session.scalar(select(Plan).where(Plan.code == limits.code))
        if existing is None:
            session.add(_plan_from_limits(limits))
            continue
        _apply_limits(existing, limits)
    session.commit()


def _plan_from_limits(limits: PlanLimits) -> Plan:
    return Plan(
        code=limits.code,
        name=limits.name,
        parse_per_day=limits.parse_per_day,
        export_per_day=limits.export_per_day,
        max_upload_size_mb=limits.max_upload_size_mb,
        max_parallel=limits.max_parallel,
        allows_batch=limits.allows_batch,
        allows_history=limits.allows_history,
    )


def _apply_limits(plan: Plan, limits: PlanLimits) -> None:
    plan.name = limits.name
    plan.parse_per_day = limits.parse_per_day
    plan.export_per_day = limits.export_per_day
    plan.max_upload_size_mb = limits.max_upload_size_mb
    plan.max_parallel = limits.max_parallel
    plan.allows_batch = limits.allows_batch
    plan.allows_history = limits.allows_history
