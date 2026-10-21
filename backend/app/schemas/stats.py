"""Administrator statistics. No visitor identifiers leave this API."""

from datetime import date
from typing import List

from app.schemas.invoice import ApiModel

PAID_PLAN_CODES: tuple[str, ...] = ("plus", "team")
VISIT_HISTORY_DAYS: int = 14


class VisitDayStat(ApiModel):
    """Unique browsers on one calendar day."""

    visit_date: date
    visitors: int


class ActionDayStat(ApiModel):
    """Visitors plus action counts for one calendar day. No invoice content."""

    event_date: date
    visitors: int
    landing: int
    upload: int
    parse_success: int
    accountant_package: int
    export: int


class AdminStatsResponse(ApiModel):
    """Daily visitors, product actions, and people on Plus or Team."""

    visits_today: int
    parses_today: int
    packages_today: int
    exports_today: int
    visits_by_day: List[VisitDayStat]
    actions_by_day: List[ActionDayStat]
    paid_plan_users: int
