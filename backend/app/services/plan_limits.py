"""Built-in plan catalog. Guest limits come from settings; org plans from this table."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class PlanLimits:
    """Numeric and feature limits for one plan code."""

    code: str
    name: str
    parse_per_day: int
    export_per_day: int
    max_upload_size_mb: int
    max_parallel: int
    allows_batch: bool
    allows_history: bool


PLAN_CATALOG: dict[str, PlanLimits] = {
    "free": PlanLimits(
        code="free",
        name="Free",
        parse_per_day=10,
        export_per_day=10,
        max_upload_size_mb=10,
        max_parallel=1,
        allows_batch=False,
        allows_history=False,
    ),
    "plus": PlanLimits(
        code="plus",
        name="Plus",
        parse_per_day=100,
        export_per_day=100,
        max_upload_size_mb=25,
        max_parallel=2,
        allows_batch=True,
        allows_history=True,
    ),
    "team": PlanLimits(
        code="team",
        name="Team",
        parse_per_day=500,
        export_per_day=500,
        max_upload_size_mb=50,
        max_parallel=4,
        allows_batch=True,
        allows_history=True,
    ),
}


def limits_for_plan_code(code: str) -> PlanLimits:
    """Return catalog limits; unknown codes fall back to Free."""
    return PLAN_CATALOG.get(code, PLAN_CATALOG["free"])


def guest_limits() -> PlanLimits:
    """Unauthenticated Empfang limits. Size follows MAX_UPLOAD_SIZE_MB."""
    return PlanLimits(
        code="guest",
        name="Gast",
        parse_per_day=settings.guest_parse_per_day,
        export_per_day=settings.guest_export_per_day,
        max_upload_size_mb=settings.max_upload_size_mb,
        max_parallel=settings.guest_max_parallel,
        allows_batch=False,
        allows_history=False,
    )


def merge_plan_row(
    *,
    code: str,
    name: str,
    parse_per_day: int | None,
    export_per_day: int | None,
    max_upload_size_mb: int | None,
    max_parallel: int | None,
    allows_batch: bool,
    allows_history: bool,
) -> PlanLimits:
    """Prefer stored plan columns; fill gaps from the catalog."""
    catalog: PlanLimits = limits_for_plan_code(code)
    return PlanLimits(
        code=code,
        name=name or catalog.name,
        parse_per_day=parse_per_day if parse_per_day is not None else catalog.parse_per_day,
        export_per_day=export_per_day if export_per_day is not None else catalog.export_per_day,
        max_upload_size_mb=(
            max_upload_size_mb if max_upload_size_mb is not None else catalog.max_upload_size_mb
        ),
        max_parallel=max_parallel if max_parallel is not None else catalog.max_parallel,
        allows_batch=allows_batch,
        allows_history=allows_history,
    )


def upgrade_cta(plan_code: str) -> str:
    """German CTA appended to daily-quota messages."""
    if plan_code in {"guest", "free"}:
        return " Mit Plus stehen höhere Kontingente zur Verfügung."
    if plan_code == "plus":
        return " Mit Team stehen höhere Kontingente zur Verfügung."
    return " Bitte morgen erneut versuchen."
