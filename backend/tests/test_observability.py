"""Liveness/readiness, structured JSON logs, request id, and Prometheus metrics."""

from __future__ import annotations

import json
import logging
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from prometheus_client import REGISTRY

from app.core.logging_config import JsonLogFormatter
from app.main import create_app
from app.schemas.invoice import InvoiceParseResponse
from app.services.invoice_service import InvoiceService


def _counter_value(metric_name: str, labels: dict[str, str]) -> float:
    """Read a Prometheus counter sample by exposition name and labels."""
    for collected in REGISTRY.collect():
        for sample in collected.samples:
            if sample.name != metric_name:
                continue
            if all(sample.labels.get(key) == value for key, value in labels.items()):
                return float(sample.value)
    return 0.0


class TestHealthProbes(unittest.TestCase):
    def test_liveness_is_always_ok(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.get("/api/health/live")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertTrue(response.headers.get("X-Request-ID"))

    def test_readiness_ok_when_kosit_not_required(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.get("/api/health/ready")
        self.assertEqual(response.status_code, 200)
        payload: dict[str, object] = response.json()
        self.assertTrue(payload["ready"])
        self.assertEqual(payload["status"], "ok")
        self.assertIsInstance(payload["checks"], list)

    def test_readiness_503_when_required_kosit_missing(self) -> None:
        with patch("app.core.health.settings") as mock_settings:
            mock_settings.require_kosit = True
            mock_settings.kosit_ready = False
            mock_settings.kosit_java_bin = "java-not-installed-xyz"
            client: TestClient = TestClient(create_app())
            response = client.get("/api/health/ready")
        self.assertEqual(response.status_code, 503)
        payload: dict[str, object] = response.json()
        self.assertFalse(payload["ready"])
        self.assertEqual(payload["status"], "not_ready")

    def test_detailed_health_stays_http_200(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        payload: dict[str, object] = response.json()
        self.assertIn(payload["status"], {"ok", "degraded"})
        self.assertIn("ready", payload)
        names: list[str] = [str(item["name"]) for item in payload["checks"]]  # type: ignore[index]
        self.assertIn("process", names)
        self.assertIn("kosit", names)


class TestJsonLogs(unittest.TestCase):
    def test_formatter_emits_event_and_request_id(self) -> None:
        formatter: JsonLogFormatter = JsonLogFormatter()
        record: logging.LogRecord = logging.LogRecord(
            name="app.errors",
            level=logging.WARNING,
            pathname=__file__,
            lineno=1,
            msg="event=parse_failed code=UNSUPPORTED_TYPE",
            args=(),
            exc_info=None,
        )
        record.structured = {
            "event": "parse_failed",
            "code": "UNSUPPORTED_TYPE",
            "request_id": "req-json-1",
        }
        line: str = formatter.format(record)
        payload: dict[str, object] = json.loads(line)
        self.assertEqual(payload["event"], "parse_failed")
        self.assertEqual(payload["code"], "UNSUPPORTED_TYPE")
        self.assertEqual(payload["request_id"], "req-json-1")
        self.assertEqual(payload["level"], "WARNING")

    def test_formatter_strips_xml_fragments(self) -> None:
        formatter: JsonLogFormatter = JsonLogFormatter()
        record: logging.LogRecord = logging.LogRecord(
            name="app.errors",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="secret",
            args=(),
            exc_info=None,
        )
        record.structured = {
            "event": "unhandled_exception",
            "detail": "Error near <Invoice><IBAN>DE89370400440532013000</IBAN></Invoice>",
        }
        line: str = formatter.format(record)
        self.assertNotIn("DE89370400440532013000", line)
        self.assertNotIn("<Invoice>", line)
        payload: dict[str, object] = json.loads(line)
        self.assertEqual(payload["detail"], "Error near")


class TestMetricsAndErrorTracking(unittest.TestCase):
    def test_metrics_endpoint_is_prometheus_text(self) -> None:
        client: TestClient = TestClient(create_app())
        client.get("/api/health")
        response = client.get("/metrics")
        self.assertEqual(response.status_code, 200)
        body: str = response.text
        self.assertIn("einvoice_http_requests_total", body)
        self.assertIn("/api/health", body)
        self.assertIn("einvoice_kosit_ready", body)
        self.assertIn("einvoice_ready", body)
        self.assertNotIn("<Invoice>", body)

    def test_parse_failure_increments_parse_and_error_metrics(self) -> None:
        before_results: float = _counter_value("einvoice_parse_results_total", {"status": "error"})
        before_failures: float = _counter_value(
            "einvoice_parse_failures_total",
            {"code": "UNSUPPORTED_TYPE"},
        )
        service: InvoiceService = InvoiceService()
        result: InvoiceParseResponse = service.parse_upload(
            filename="note.txt",
            content=b"secret-invoice-body-should-not-appear",
            request_id="req-metrics-1",
        )
        self.assertEqual(result.status.value, "error")
        after_results: float = _counter_value("einvoice_parse_results_total", {"status": "error"})
        after_failures: float = _counter_value(
            "einvoice_parse_failures_total",
            {"code": "UNSUPPORTED_TYPE"},
        )
        self.assertEqual(after_results, before_results + 1.0)
        self.assertEqual(after_failures, before_failures + 1.0)

        client: TestClient = TestClient(create_app())
        metrics_body: str = client.get("/metrics").text
        self.assertIn("einvoice_parse_failures_total", metrics_body)
        self.assertIn("UNSUPPORTED_TYPE", metrics_body)
        self.assertNotIn("secret-invoice-body-should-not-appear", metrics_body)

    def test_unhandled_exception_increments_5xx_metric(self) -> None:
        app = create_app()

        @app.get("/api/_test_metrics_boom")
        def _boom() -> None:
            raise RuntimeError("boom-payload-<Invoice>leak</Invoice>")

        client: TestClient = TestClient(app, raise_server_exceptions=False)
        response = client.get("/api/_test_metrics_boom")
        self.assertEqual(response.status_code, 500)
        body: str = client.get("/metrics").text
        self.assertIn("einvoice_http_5xx_total", body)
        self.assertIn("einvoice_errors_total", body)
        self.assertIn("unhandled_exception", body)
        self.assertNotIn("leak", body)
        self.assertNotIn("<Invoice>", body)


if __name__ == "__main__":
    unittest.main()
