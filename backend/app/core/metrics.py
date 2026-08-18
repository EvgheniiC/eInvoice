"""In-process Prometheus metrics. Never labels with filenames, IBANs, or payloads."""

from __future__ import annotations

import os
from typing import Final, Mapping, Optional

os.environ.setdefault("PROMETHEUS_DISABLE_CREATED_SERIES", "true")

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

METRICS_CONTENT_TYPE: Final[str] = CONTENT_TYPE_LATEST

_KNOWN_PATHS: Final[frozenset[str]] = frozenset(
    {
        "/api/health",
        "/api/health/live",
        "/api/health/ready",
        "/api/invoices/parse",
        "/api/invoices/export",
        "/api/invoices/export/mapping",
        "/api/invoices/export/validation-report",
        "/api/invoices/export/accountant-package",
        "/metrics",
    }
)

_SKIP_PATHS: Final[frozenset[str]] = frozenset({"/metrics"})

_DURATION_BUCKETS: Final[tuple[float, ...]] = (
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
    30.0,
    60.0,
    90.0,
)

APP_INFO: Info = Info(
    "einvoice_app",
    "eInvoice process metadata (no request data).",
)

_APP_INFO_SET: bool = False

HTTP_REQUESTS_TOTAL: Counter = Counter(
    "einvoice_http_requests_total",
    "HTTP requests by method, low-cardinality path, and status class.",
    ["method", "path", "status"],
)

HTTP_REQUEST_DURATION_SECONDS: Histogram = Histogram(
    "einvoice_http_request_duration_seconds",
    "HTTP request duration in seconds.",
    ["method", "path"],
    buckets=_DURATION_BUCKETS,
)

HTTP_5XX_TOTAL: Counter = Counter(
    "einvoice_http_5xx_total",
    "HTTP 5xx responses.",
    ["method", "path"],
)

ERRORS_TOTAL: Counter = Counter(
    "einvoice_errors_total",
    "Tracked application errors by event name (no payloads).",
    ["event"],
)

PARSE_RESULTS_TOTAL: Counter = Counter(
    "einvoice_parse_results_total",
    "Invoice parse outcomes.",
    ["status"],
)

PARSE_FAILURES_TOTAL: Counter = Counter(
    "einvoice_parse_failures_total",
    "Invoice parse failures by stable error code.",
    ["code"],
)

TIMEOUTS_TOTAL: Counter = Counter(
    "einvoice_timeouts_total",
    "Timeouts by component (http_request, kosit, …).",
    ["component"],
)

KOSIT_READY: Gauge = Gauge(
    "einvoice_kosit_ready",
    "1 if KoSIT JAR and scenarios are present, else 0.",
)

READY: Gauge = Gauge(
    "einvoice_ready",
    "1 if the process is ready to receive traffic, else 0.",
)


def normalize_path(path: str) -> str:
    """Map request paths to a fixed label set (no user-controlled cardinality)."""
    if path in _KNOWN_PATHS:
        return path
    return "other"


def observe_http_request(
    *,
    method: str,
    path: str,
    status_code: int,
    duration_seconds: float,
) -> None:
    """Record one finished HTTP request. Skips the scrape endpoint itself."""
    if path in _SKIP_PATHS:
        return
    method_label: str = method.upper() if method else "GET"
    path_label: str = normalize_path(path)
    status_label: str = str(status_code)
    try:
        HTTP_REQUESTS_TOTAL.labels(method_label, path_label, status_label).inc()
        HTTP_REQUEST_DURATION_SECONDS.labels(method_label, path_label).observe(
            max(duration_seconds, 0.0)
        )
        if status_code >= 500:
            HTTP_5XX_TOTAL.labels(method_label, path_label).inc()
    except Exception:
        return


def observe_error(event: str) -> None:
    """Increment the error-tracking counter for a named event."""
    label: str = event.strip() or "unknown"
    try:
        ERRORS_TOTAL.labels(label).inc()
    except Exception:
        return


def observe_parse_result(status: str) -> None:
    """Record a parse pipeline outcome (success / partial / error)."""
    label: str = status.strip() or "unknown"
    try:
        PARSE_RESULTS_TOTAL.labels(label).inc()
    except Exception:
        return


def observe_parse_failure(code: str) -> None:
    """Record a parse failure by stable application code."""
    label: str = code.strip() or "unknown"
    try:
        PARSE_FAILURES_TOTAL.labels(label).inc()
    except Exception:
        return


def observe_timeout(component: str) -> None:
    """Record a timeout for a named component."""
    label: str = component.strip() or "unknown"
    try:
        TIMEOUTS_TOTAL.labels(label).inc()
    except Exception:
        return


def set_readiness_gauges(*, kosit_ready: bool, ready: bool) -> None:
    """Update scrape-time readiness gauges."""
    try:
        KOSIT_READY.set(1.0 if kosit_ready else 0.0)
        READY.set(1.0 if ready else 0.0)
    except Exception:
        return


def set_app_info(fields: Mapping[str, str]) -> None:
    """Set process info labels once (version, environment)."""
    global _APP_INFO_SET
    if _APP_INFO_SET:
        return
    try:
        APP_INFO.info({str(key): str(value) for key, value in fields.items()})
        _APP_INFO_SET = True
    except Exception:
        _APP_INFO_SET = True


def render_metrics() -> bytes:
    """Prometheus text exposition (no invoice data)."""
    return generate_latest()


def safe_event_label(event: Optional[str]) -> str:
    """Clamp an event name to a short, non-payload label."""
    if not event:
        return "unknown"
    text: str = event.strip()
    if len(text) > 64:
        return text[:64]
    return text or "unknown"
