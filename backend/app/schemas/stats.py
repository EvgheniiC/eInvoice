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


class AdminStatsResponse(ApiModel):
    """Daily visitors and the number of people on Plus or Team."""

    visits_today: int
    visits_by_day: List[VisitDayStat]
    paid_plan_users: int
