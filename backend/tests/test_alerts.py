"""Alert evaluation for 5xx, timeouts, parse failures, and API availability."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from app.core.alerts import (
    FIVE_XX_INCREASE,
    PARSE_FAILED_INCREASE,
    TIMEOUT_INCREASE,
    AlertThresholds,
    MetricsSnapshot,
    append_sample,
    evaluate_alerts,
    parse_prometheus_counters,
    snapshot_from_probes,
)


def _snap(
    ts: float,
    *,
    live_ok: bool = True,
    ready_ok: bool = True,
    metrics_ok: bool = True,
    http_5xx: float = 0.0,
    http_requests: float = 0.0,
    timeouts: float = 0.0,
    parse_failed_errors: float = 0.0,
) -> MetricsSnapshot:
    return MetricsSnapshot(
        scraped_at=ts,
        live_ok=live_ok,
        ready_ok=ready_ok,
        metrics_ok=metrics_ok,
        http_5xx=http_5xx,
        http_requests=http_requests,
        timeouts=timeouts,
        parse_failed_errors=parse_failed_errors,
    )


class TestParsePrometheusCounters(unittest.TestCase):
    def test_sums_labeled_counters_and_ignores_expected_parse_codes(self) -> None:
        text: str = """
# TYPE einvoice_http_5xx_total counter
einvoice_http_5xx_total{method="POST",path="/api/invoices/parse"} 2.0
einvoice_http_5xx_total{method="GET",path="other"} 1.0
# TYPE einvoice_http_requests_total counter
einvoice_http_requests_total{method="GET",path="/api/health",status="200"} 10.0
# TYPE einvoice_timeouts_total counter
einvoice_timeouts_total{component="kosit"} 2.0
einvoice_timeouts_total{component="http_request"} 1.0
# TYPE einvoice_errors_total counter
einvoice_errors_total{event="parse_failed"} 4.0
einvoice_errors_total{event="unhandled_exception"} 1.0
# TYPE einvoice_parse_failures_total counter
einvoice_parse_failures_total{code="UNSUPPORTED_TYPE"} 99.0
"""
        counters: dict[str, float] = parse_prometheus_counters(text)
        self.assertEqual(counters["http_5xx"], 3.0)
        self.assertEqual(counters["http_requests"], 10.0)
        self.assertEqual(counters["timeouts"], 3.0)
        self.assertEqual(counters["parse_failed_errors"], 4.0)

    def test_snapshot_from_probes_without_metrics(self) -> None:
        snapshot: MetricsSnapshot = snapshot_from_probes(
            scraped_at=1.0,
            live_ok=False,
            ready_ok=False,
            metrics_text=None,
        )
        self.assertFalse(snapshot.metrics_ok)
        self.assertFalse(snapshot.live_ok)


class TestAvailabilityAlerts(unittest.TestCase):
    def test_single_live_failure_does_not_fire(self) -> None:
        evaluation = evaluate_alerts((_snap(100.0, live_ok=False, ready_ok=False, metrics_ok=False),))
        self.assertEqual(evaluation.firing, frozenset())
        self.assertEqual(evaluation.events, tuple())

    def test_live_failure_for_threshold_fires_and_recovers(self) -> None:
        first: MetricsSnapshot = _snap(100.0, live_ok=False, ready_ok=False, metrics_ok=False)
        second: MetricsSnapshot = _snap(160.0, live_ok=False, ready_ok=False, metrics_ok=False)
        firing = evaluate_alerts((first, second))
        self.assertEqual(firing.firing, frozenset({"EinvoiceApiDown"}))
        self.assertEqual(firing.events[0].status, "firing")
        self.assertEqual(firing.events[0].severity, "critical")

        recovered: MetricsSnapshot = _snap(220.0, live_ok=True)
        resolved = evaluate_alerts(
            (first, second, recovered),
            previously_firing={"EinvoiceApiDown"},
        )
        self.assertEqual(resolved.firing, frozenset())
        self.assertEqual(resolved.events[0].name, "EinvoiceApiDown")
        self.assertEqual(resolved.events[0].status, "resolved")

    def test_not_ready_requires_sustained_failure(self) -> None:
        start: MetricsSnapshot = _snap(0.0, ready_ok=False)
        early: MetricsSnapshot = _snap(120.0, ready_ok=False)
        pending = evaluate_alerts((start, early))
        self.assertNotIn("EinvoiceApiNotReady", pending.firing)

        later: MetricsSnapshot = _snap(300.0, ready_ok=False)
        firing = evaluate_alerts((start, early, later))
        self.assertIn("EinvoiceApiNotReady", firing.firing)

    def test_dead_api_does_not_also_fire_not_ready(self) -> None:
        samples = (
            _snap(0.0, live_ok=False, ready_ok=False, metrics_ok=False),
            _snap(300.0, live_ok=False, ready_ok=False, metrics_ok=False),
        )
        evaluation = evaluate_alerts(samples)
        self.assertEqual(evaluation.firing, frozenset({"EinvoiceApiDown"}))


class TestIncreaseAlerts(unittest.TestCase):
    def test_first_scrape_does_not_fire_increase_alerts(self) -> None:
        evaluation = evaluate_alerts((_snap(0.0, http_5xx=99.0, timeouts=99.0, parse_failed_errors=99.0),))
        self.assertEqual(evaluation.firing, frozenset())

    def test_5xx_increase_fires_critical(self) -> None:
        samples = (
            _snap(0.0, http_5xx=1.0),
            _snap(300.0, http_5xx=1.0 + FIVE_XX_INCREASE),
        )
        evaluation = evaluate_alerts(samples)
        self.assertIn("EinvoiceHigh5xx", evaluation.firing)
        self.assertEqual(evaluation.events[0].severity, "critical")
        self.assertGreaterEqual(evaluation.events[0].value, FIVE_XX_INCREASE)

    def test_timeout_and_parse_failure_increases_fire_warnings(self) -> None:
        samples = (
            _snap(0.0, timeouts=0.0, parse_failed_errors=0.0),
            _snap(
                300.0,
                timeouts=TIMEOUT_INCREASE,
                parse_failed_errors=PARSE_FAILED_INCREASE,
            ),
        )
        evaluation = evaluate_alerts(samples)
        self.assertEqual(
            evaluation.firing,
            frozenset({"EinvoiceTimeouts", "EinvoiceParseFailures"}),
        )
        by_name: dict[str, str] = {event.name: event.severity for event in evaluation.events}
        self.assertEqual(by_name["EinvoiceTimeouts"], "warning")
        self.assertEqual(by_name["EinvoiceParseFailures"], "warning")

    def test_expected_unsupported_uploads_do_not_count_as_parse_alert(self) -> None:
        samples = (
            _snap(0.0, parse_failed_errors=0.0, http_requests=5.0),
            _snap(300.0, parse_failed_errors=0.0, http_requests=20.0),
        )
        evaluation = evaluate_alerts(samples)
        self.assertNotIn("EinvoiceParseFailures", evaluation.firing)

    def test_counter_reset_does_not_use_pre_restart_baseline(self) -> None:
        samples = (
            _snap(0.0, http_5xx=50.0),
            _snap(60.0, http_5xx=1.0),
        )
        evaluation = evaluate_alerts(samples)
        self.assertNotIn("EinvoiceHigh5xx", evaluation.firing)

    def test_missing_metrics_skip_increase_alerts(self) -> None:
        samples = (
            _snap(0.0, http_5xx=0.0),
            _snap(300.0, metrics_ok=False, http_5xx=0.0),
        )
        evaluation = evaluate_alerts(samples)
        self.assertNotIn("EinvoiceHigh5xx", evaluation.firing)

    def test_still_firing_does_not_re_emit(self) -> None:
        samples = (
            _snap(0.0, http_5xx=0.0),
            _snap(300.0, http_5xx=FIVE_XX_INCREASE),
        )
        evaluation = evaluate_alerts(samples, previously_firing={"EinvoiceHigh5xx"})
        self.assertEqual(evaluation.firing, frozenset({"EinvoiceHigh5xx"}))
        self.assertEqual(evaluation.events, tuple())

    def test_append_sample_bounds_history(self) -> None:
        history = tuple(_snap(float(index)) for index in range(25))
        bounded = append_sample(history[:-1], history[-1], max_samples=20)
        self.assertEqual(len(bounded), 20)
        self.assertEqual(bounded[-1].scraped_at, 24.0)


class TestWatchdogState(unittest.TestCase):
    def test_state_roundtrip_has_no_invoice_fields(self) -> None:
        from app.core.alerts import snapshot_from_dict, snapshot_to_dict

        samples = (
            _snap(10.0, http_5xx=2.0, parse_failed_errors=1.0),
            _snap(70.0, http_5xx=4.0, parse_failed_errors=1.0),
        )
        payload: dict[str, object] = {
            "samples": [snapshot_to_dict(item) for item in samples],
            "firing": ["EinvoiceHigh5xx"],
        }
        with tempfile.TemporaryDirectory() as tmp:
            path: Path = Path(tmp) / "state.json"
            text: str = json.dumps(payload, indent=2)
            path.write_text(text + "\n", encoding="utf-8")
            self.assertNotIn("<Invoice>", text)
            self.assertNotIn("IBAN", text)
            raw: dict[str, object] = json.loads(path.read_text(encoding="utf-8"))
            samples_raw: object = raw["samples"]
            self.assertIsInstance(samples_raw, list)
            loaded: list[MetricsSnapshot] = []
            if isinstance(samples_raw, list):
                for item in samples_raw:
                    self.assertIsInstance(item, dict)
                    if isinstance(item, dict):
                        loaded.append(snapshot_from_dict(item))
            self.assertEqual(loaded[-1].http_5xx, 4.0)
            self.assertEqual(raw["firing"], ["EinvoiceHigh5xx"])

    def test_watchdog_save_and_load_state(self) -> None:
        import importlib.util
        from types import ModuleType

        script: Path = Path(__file__).resolve().parents[1] / "scripts" / "alert_watchdog.py"
        spec = importlib.util.spec_from_file_location("einvoice_alert_watchdog", script)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module: ModuleType = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(module)
        samples: tuple[MetricsSnapshot, ...] = (_snap(10.0, http_5xx=2.0), _snap(70.0, http_5xx=5.0))
        with tempfile.TemporaryDirectory() as tmp:
            path: Path = Path(tmp) / "state.json"
            module.save_state(path, samples, frozenset({"EinvoiceHigh5xx"}))
            loaded_samples, firing = module.load_state(path)
            self.assertEqual(firing, frozenset({"EinvoiceHigh5xx"}))
            self.assertEqual(len(loaded_samples), 2)
            self.assertEqual(loaded_samples[-1].http_5xx, 5.0)
            disk: str = path.read_text(encoding="utf-8")
            self.assertNotIn("<Invoice>", disk)

    def test_webhook_payload_is_counter_metadata_only(self) -> None:
        from app.core.alerts import AlertEvent

        event: AlertEvent = AlertEvent(
            name="EinvoiceHigh5xx",
            severity="critical",
            status="firing",
            summary="HTTP 5xx responses increased.",
            value=3.0,
        )
        payload: dict[str, object] = {
            "service": "eInvoice",
            "alert": event.name,
            "severity": event.severity,
            "status": event.status,
            "summary": event.summary,
            "value": event.value,
        }
        encoded: str = json.dumps(payload)
        self.assertIn("EinvoiceHigh5xx", encoded)
        self.assertNotIn("filename", encoded)
        self.assertNotIn("invoice", encoded.lower().replace("einvoice", ""))


class TestPrometheusRuleFile(unittest.TestCase):
    def test_committed_rules_cover_required_alerts(self) -> None:
        rules_path: Path = (
            Path(__file__).resolve().parents[2] / "deploy" / "prometheus" / "einvoice-alerts.yml"
        )
        text: str = rules_path.read_text(encoding="utf-8")
        for name in (
            "EinvoiceApiDown",
            "EinvoiceApiNotReady",
            "EinvoiceHigh5xx",
            "EinvoiceTimeouts",
            "EinvoiceParseFailures",
        ):
            self.assertIn(name, text)
        self.assertIn(f">= {int(FIVE_XX_INCREASE)}", text)
        self.assertIn(f">= {int(TIMEOUT_INCREASE)}", text)
        self.assertIn(f">= {int(PARSE_FAILED_INCREASE)}", text)
        thresholds: AlertThresholds = AlertThresholds()
        self.assertEqual(thresholds.five_xx_increase, FIVE_XX_INCREASE)


if __name__ == "__main__":
    unittest.main()
