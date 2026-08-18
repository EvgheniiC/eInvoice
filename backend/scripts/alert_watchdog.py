"""Localhost alert watchdog: health probes + Prometheus counters.

Run by systemd timer (deploy/einvoice-alerts.timer). Never logs invoice bodies.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Optional

BACKEND_ROOT: Path = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.alerts import (  # noqa: E402
    AlertEvaluation,
    AlertEvent,
    AlertThresholds,
    MetricsSnapshot,
    append_sample,
    evaluate_alerts,
    snapshot_from_dict,
    snapshot_from_probes,
    snapshot_to_dict,
)
from app.core.config import settings  # noqa: E402
from app.core.error_events import log_event  # noqa: E402
from app.core.logging_config import configure_logging  # noqa: E402


def main(argv: Optional[list[str]] = None) -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Evaluate eInvoice alerts from localhost health and /metrics.",
    )
    parser.add_argument(
        "--state-path",
        default="",
        help="JSON state file (default: ALERT_STATE_PATH or ./alert_state.json).",
    )
    parser.add_argument(
        "--base-url",
        default="",
        help="API base URL (default: ALERT_BASE_URL).",
    )
    args: argparse.Namespace = parser.parse_args(argv if argv is not None else sys.argv[1:])

    configure_logging(settings.log_level, settings.log_format)
    base_url: str = (args.base_url or settings.alert_base_url).rstrip("/")
    state_path: Path = Path(args.state_path or settings.alert_state_path)

    snapshot: MetricsSnapshot = scrape_snapshot(
        base_url=base_url,
        timeout_seconds=float(settings.alert_scrape_timeout_seconds),
        scraped_at=time.time(),
    )
    previous_samples, previously_firing = load_state(state_path)
    samples = append_sample(previous_samples, snapshot)
    evaluation: AlertEvaluation = evaluate_alerts(
        samples,
        previously_firing=previously_firing,
        thresholds=AlertThresholds(),
    )
    save_state(state_path, evaluation.samples, evaluation.firing)
    emit_events(evaluation.events)
    notify_webhook(evaluation.events, webhook_url=settings.alert_webhook_url)
    return 0


def scrape_snapshot(*, base_url: str, timeout_seconds: float, scraped_at: float) -> MetricsSnapshot:
    """Probe liveness, readiness, and /metrics on the local API process."""
    live_ok: bool = _probe_ok(f"{base_url}/api/health/live", timeout_seconds)
    ready_ok: bool = False
    if live_ok:
        ready_ok = _probe_ok(f"{base_url}/api/health/ready", timeout_seconds)
    metrics_text: Optional[str] = None
    if live_ok:
        metrics_text = _get_text(f"{base_url}/metrics", timeout_seconds)
        if metrics_text is None:
            log_event(
                logging.WARNING,
                "alert_metrics_scrape_failed",
                fields={"base_url": base_url},
            )
    if not live_ok:
        log_event(
            logging.ERROR,
            "alert_live_probe_failed",
            fields={"base_url": base_url},
        )
    return snapshot_from_probes(
        scraped_at=scraped_at,
        live_ok=live_ok,
        ready_ok=ready_ok,
        metrics_text=metrics_text,
    )


def load_state(path: Path) -> tuple[tuple[MetricsSnapshot, ...], frozenset[str]]:
    if not path.is_file():
        return tuple(), frozenset()
    try:
        raw: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        log_event(logging.WARNING, "alert_state_unreadable", fields={"path": path.name})
        return tuple(), frozenset()
    if not isinstance(raw, dict):
        return tuple(), frozenset()
    samples_raw: Any = raw.get("samples", [])
    firing_raw: Any = raw.get("firing", [])
    samples: list[MetricsSnapshot] = []
    if isinstance(samples_raw, list):
        for item in samples_raw:
            if isinstance(item, dict):
                samples.append(snapshot_from_dict(item))
    firing: set[str] = set()
    if isinstance(firing_raw, list):
        for name in firing_raw:
            if isinstance(name, str) and name:
                firing.add(name)
    return tuple(samples), frozenset(firing)


def save_state(
    path: Path,
    samples: tuple[MetricsSnapshot, ...],
    firing: frozenset[str],
) -> None:
    payload: dict[str, Any] = {
        "samples": [snapshot_to_dict(item) for item in samples],
        "firing": sorted(firing),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def emit_events(events: tuple[AlertEvent, ...]) -> None:
    for event in events:
        level: int = logging.INFO
        log_name: str = "alert_resolved"
        if event.status == "firing":
            log_name = "alert_firing"
            level = logging.ERROR if event.severity == "critical" else logging.WARNING
        log_event(
            level,
            log_name,
            fields={
                "alert": event.name,
                "severity": event.severity,
                "status": event.status,
                "summary": event.summary,
                "value": event.value,
            },
        )


def notify_webhook(events: tuple[AlertEvent, ...], *, webhook_url: Optional[str]) -> None:
    if not webhook_url or not events:
        return
    for event in events:
        body: dict[str, Any] = {
            "service": "eInvoice",
            "environment": settings.environment,
            "alert": event.name,
            "severity": event.severity,
            "status": event.status,
            "summary": event.summary,
            "value": event.value,
        }
        encoded: bytes = json.dumps(body).encode("utf-8")
        request: urllib.request.Request = urllib.request.Request(
            webhook_url,
            data=encoded,
            method="POST",
            headers={"Content-Type": "application/json", "User-Agent": "einvoice-alert-watchdog"},
        )
        try:
            with urllib.request.urlopen(request, timeout=5) as response:
                _body: bytes = response.read()
        except (urllib.error.URLError, TimeoutError, OSError):
            log_event(
                logging.WARNING,
                "alert_webhook_failed",
                fields={"alert": event.name, "status": event.status},
            )


def _probe_ok(url: str, timeout_seconds: float) -> bool:
    status, _body = _http_get(url, timeout_seconds)
    return status == 200


def _get_text(url: str, timeout_seconds: float) -> Optional[str]:
    status, body = _http_get(url, timeout_seconds)
    if status != 200 or body is None:
        return None
    return body


def _http_get(url: str, timeout_seconds: float) -> tuple[int, Optional[str]]:
    request: urllib.request.Request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "einvoice-alert-watchdog", "Accept": "application/json, text/plain"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            status: int = int(getattr(response, "status", 200))
            body: str = response.read().decode("utf-8", errors="replace")
            return status, body
    except urllib.error.HTTPError as exc:
        return int(exc.code), None
    except (urllib.error.URLError, TimeoutError, OSError):
        return 0, None


if __name__ == "__main__":
    sys.exit(main())
