from datetime import date, datetime, timezone, tzinfo
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_BERLIN: str = "Europe/Berlin"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime) -> datetime:
    """SQLite may return naive UTC timestamps; treat them as UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def usage_timezone() -> tzinfo:
    """Europe/Berlin for daily quotas; UTC if tzdata is missing."""
    try:
        return ZoneInfo(_BERLIN)
    except ZoneInfoNotFoundError:
        return timezone.utc


def usage_date_today() -> date:
    """Calendar day used for parse/export counters."""
    return utc_now().astimezone(usage_timezone()).date()
