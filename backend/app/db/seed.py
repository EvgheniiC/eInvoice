"""Seed built-in plans. Idempotent."""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Plan

_PLAN_ROWS: Sequence[tuple[str, str, int, bool, bool]] = (
    ("free", "Free", 10, False, False),
    ("plus", "Plus", 25, True, True),
    ("team", "Team", 50, True, True),
)


def seed_plans(session: Session) -> None:
    """Insert free/plus/team if missing. Quota fields stay null (stub)."""
    for code, name, max_mb, batch, history in _PLAN_ROWS:
        existing: Optional[Plan] = session.scalar(select(Plan).where(Plan.code == code))
        if existing is not None:
            continue
        session.add(
            Plan(
                code=code,
                name=name,
                parse_per_day=None,
                export_per_day=None,
                max_upload_size_mb=max_mb,
                allows_batch=batch,
                allows_history=history,
            )
        )
    session.commit()
