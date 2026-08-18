"""Alert evaluation for 5xx, timeouts, parse failures, and API availability.

Privacy: snapshots and notifications contain only counters and probe booleans.
They never include filenames, invoice bodies, IBANs, or request payloads.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Optional, Sequence

WINDOW_SECONDS: int = 300
DOWN_FOR_SECONDS: int = 60
NOT_READY_FOR_SECONDS: int = 300
FIVE_XX_INCREASE: float = 3.0
TIMEOUT_INCREASE: float = 2.0
PARSE_FAILED_INCREASE: float = 3.0
MAX_SAMPLES: int = 20

_METRIC_LINE_RE: re.Pattern[str] = re.compile(
    r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(?:\{([^}]*)\})?\s+([0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)\s*$"
)
_LABEL_RE: re.Pattern[str] = re.compile(r'([a-zA-Z_][a-zA-Z0-9_]*)="([^"]*)"')


@dataclass(frozen=True)
class AlertThresholds:
    """Operational thresholds until formal SLOs are defined."""

    window_seconds: int = WINDOW_SECONDS
    down_for_seconds: int = DOWN_FOR_SECONDS
    not_ready_for_seconds: int = NOT_READY_FOR_SECONDS
    five_xx_increase: float = FIVE_XX_INCREASE
    timeout_increase: float = TIMEOUT_INCREASE
    parse_failed_increase: float = PARSE_FAILED_INCREASE


@dataclass(frozen=True)
class MetricsSnapshot:
    """One watchdog scrape. Counters are sums across low-cardinality labels."""

    scraped_at: float
    live_ok: bool
    ready_ok: bool
    metrics_ok: bool
    http_5xx: float
    http_requests: float
    timeouts: float
    parse_failed_errors: float


@dataclass(frozen=True)
class AlertEvent:
    """A status transition or pending condition. No invoice data."""

    name: str
    severity: str
    status: str
    summary: str
    value: float


@dataclass(frozen=True)
class AlertEvaluation:
    """Result of comparing the latest snapshot with recent history."""

    events: tuple[AlertEvent, ...]
    firing: frozenset[str]
    samples: tuple[MetricsSnapshot, ...]


def parse_prometheus_counters(text: str) -> dict[str, float]:
    """Sum selected eInvoice counters from Prometheus text exposition."""
    http_5xx: float = 0.0
    http_requests: float = 0.0
    timeouts: float = 0.0
    parse_failed_errors: float = 0.0
    for raw_line in text.splitlines():
        line: str = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        matched: Optional[re.Match[str]] = _METRIC_LINE_RE.match(line)
        if matched is None:
            continue
        name: str = matched.group(1)
        labels: dict[str, str] = _parse_labels(matched.group(2))
        value: float = float(matched.group(3))
        if name == "einvoice_http_5xx_total":
            http_5xx += value
        elif name == "einvoice_http_requests_total":
            http_requests += value
        elif name == "einvoice_timeouts_total":
            timeouts += value
        elif name == "einvoice_errors_total" and labels.get("event") == "parse_failed":
            parse_failed_errors += value
    return {
        "http_5xx": http_5xx,
        "http_requests": http_requests,
        "timeouts": timeouts,
        "parse_failed_errors": parse_failed_errors,
    }


def _parse_labels(raw: Optional[str]) -> dict[str, str]:
    if not raw:
        return {}
    labels: dict[str, str] = {}
    for matched in _LABEL_RE.finditer(raw):
        labels[matched.group(1)] = matched.group(2)
    return labels


def snapshot_from_probes(
    *,
    scraped_at: float,
    live_ok: bool,
    ready_ok: bool,
    metrics_text: Optional[str],
) -> MetricsSnapshot:
    """Build a snapshot from health probes and optional /metrics body."""
    if not metrics_text:
        return MetricsSnapshot(
            scraped_at=scraped_at,
            live_ok=live_ok,
            ready_ok=ready_ok,
            metrics_ok=False,
            http_5xx=0.0,
            http_requests=0.0,
            timeouts=0.0,
            parse_failed_errors=0.0,
        )
    counters: dict[str, float] = parse_prometheus_counters(metrics_text)
    return MetricsSnapshot(
        scraped_at=scraped_at,
        live_ok=live_ok,
        ready_ok=ready_ok,
        metrics_ok=True,
        http_5xx=counters["http_5xx"],
        http_requests=counters["http_requests"],
        timeouts=counters["timeouts"],
        parse_failed_errors=counters["parse_failed_errors"],
    )


def append_sample(
    history: Sequence[MetricsSnapshot],
    snapshot: MetricsSnapshot,
    *,
    max_samples: int = MAX_SAMPLES,
) -> tuple[MetricsSnapshot, ...]:
    """Keep a bounded ring of recent scrapes."""
    merged: list[MetricsSnapshot] = [item for item in history if item.scraped_at < snapshot.scraped_at]
    merged.append(snapshot)
    if len(merged) > max_samples:
        merged = merged[-max_samples:]
    return tuple(merged)


def evaluate_alerts(
    samples: Sequence[MetricsSnapshot],
    *,
    previously_firing: Iterable[str] = (),
    thresholds: AlertThresholds = AlertThresholds(),
) -> AlertEvaluation:
    """Evaluate availability and error-budget style increases. Transition events only."""
    previous: frozenset[str] = frozenset(previously_firing)
    if not samples:
        resolved: list[AlertEvent] = [
            _resolved_event(name) for name in sorted(previous)
        ]
        return AlertEvaluation(events=tuple(resolved), firing=frozenset(), samples=tuple())

    latest: MetricsSnapshot = samples[-1]
    now: float = latest.scraped_at
    active: dict[str, AlertEvent] = {}

    down_for: float = _failing_duration(samples, lambda item: not item.live_ok)
    if not latest.live_ok:
        event: AlertEvent = AlertEvent(
            name="EinvoiceApiDown",
            severity="critical",
            status="firing" if down_for >= float(thresholds.down_for_seconds) else "pending",
            summary="API liveness probe failed.",
            value=down_for,
        )
        if event.status == "firing":
            active[event.name] = event

    not_ready_for: float = _failing_duration(samples, lambda item: item.live_ok and not item.ready_ok)
    if latest.live_ok and not latest.ready_ok:
        ready_event: AlertEvent = AlertEvent(
            name="EinvoiceApiNotReady",
            severity="critical",
            status="firing" if not_ready_for >= float(thresholds.not_ready_for_seconds) else "pending",
            summary="API readiness probe failed (required dependency missing).",
            value=not_ready_for,
        )
        if ready_event.status == "firing":
            active[ready_event.name] = ready_event

    if latest.metrics_ok:
        five_xx_delta: float = _increase(samples, "http_5xx", now, thresholds.window_seconds)
        if five_xx_delta >= thresholds.five_xx_increase:
            active["EinvoiceHigh5xx"] = AlertEvent(
                name="EinvoiceHigh5xx",
                severity="critical",
                status="firing",
                summary="HTTP 5xx responses increased.",
                value=five_xx_delta,
            )

        timeout_delta: float = _increase(samples, "timeouts", now, thresholds.window_seconds)
        if timeout_delta >= thresholds.timeout_increase:
            active["EinvoiceTimeouts"] = AlertEvent(
                name="EinvoiceTimeouts",
                severity="warning",
                status="firing",
                summary="Request or KoSIT timeouts increased.",
                value=timeout_delta,
            )

        parse_delta: float = _increase(
            samples,
            "parse_failed_errors",
            now,
            thresholds.window_seconds,
        )
        if parse_delta >= thresholds.parse_failed_increase:
            active["EinvoiceParseFailures"] = AlertEvent(
                name="EinvoiceParseFailures",
                severity="warning",
                status="firing",
                summary="Severe invoice parse failures increased.",
                value=parse_delta,
            )

    firing: frozenset[str] = frozenset(active.keys())
    events: list[AlertEvent] = []
    for name in sorted(firing - previous):
        events.append(active[name])
    for name in sorted(previous - firing):
        events.append(_resolved_event(name))
    return AlertEvaluation(events=tuple(events), firing=firing, samples=tuple(samples))


def snapshot_to_dict(snapshot: MetricsSnapshot) -> dict[str, float | bool]:
    """JSON-safe snapshot (counters and probes only)."""
    return {
        "scraped_at": snapshot.scraped_at,
        "live_ok": snapshot.live_ok,
        "ready_ok": snapshot.ready_ok,
        "metrics_ok": snapshot.metrics_ok,
        "http_5xx": snapshot.http_5xx,
        "http_requests": snapshot.http_requests,
        "timeouts": snapshot.timeouts,
        "parse_failed_errors": snapshot.parse_failed_errors,
    }


def snapshot_from_dict(raw: Mapping[str, object]) -> MetricsSnapshot:
    """Restore a snapshot from the watchdog state file."""
    return MetricsSnapshot(
        scraped_at=float(raw.get("scraped_at", 0.0)),
        live_ok=bool(raw.get("live_ok", False)),
        ready_ok=bool(raw.get("ready_ok", False)),
        metrics_ok=bool(raw.get("metrics_ok", False)),
        http_5xx=float(raw.get("http_5xx", 0.0)),
        http_requests=float(raw.get("http_requests", 0.0)),
        timeouts=float(raw.get("timeouts", 0.0)),
        parse_failed_errors=float(raw.get("parse_failed_errors", 0.0)),
    )


def _resolved_event(name: str) -> AlertEvent:
    severity: str = "warning" if name in {"EinvoiceTimeouts", "EinvoiceParseFailures"} else "critical"
    return AlertEvent(
        name=name,
        severity=severity,
        status="resolved",
        summary="Alert cleared.",
        value=0.0,
    )


def _failing_duration(
    samples: Sequence[MetricsSnapshot],
    predicate: Callable[[MetricsSnapshot], bool],
) -> float:
    if not samples or not predicate(samples[-1]):
        return 0.0
    start: float = samples[-1].scraped_at
    for item in reversed(samples):
        if not predicate(item):
            break
        start = item.scraped_at
    return max(samples[-1].scraped_at - start, 0.0)


def _increase(
    samples: Sequence[MetricsSnapshot],
    field: str,
    now: float,
    window_seconds: int,
) -> float:
    metric_samples: list[MetricsSnapshot] = [item for item in samples if item.metrics_ok]
    if len(metric_samples) < 2:
        return 0.0
    current: float = float(getattr(metric_samples[-1], field))
    cutoff: float = now - float(window_seconds)
    baseline_item: MetricsSnapshot = metric_samples[0]
    for item in metric_samples:
        if item.scraped_at <= cutoff:
            baseline_item = item
        else:
            break
    baseline: float = float(getattr(baseline_item, field))
    if current < baseline:
        return current
    return current - baseline
