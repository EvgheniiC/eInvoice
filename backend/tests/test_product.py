"""Public capabilities, funnel telemetry, and text-only feedback."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from app.core.config import settings
from app.main import create_app
from app.schemas.invoice import (
    InvoiceParseResponse,
    InvoiceTotals,
    PartyInfo,
    ParseStatus,
)
from app.services.invoice_service import InvoiceService


def _funnel_value(step: str) -> float:
    for collected in REGISTRY.collect():
        for sample in collected.samples:
            if sample.name == "einvoice_funnel_total" and sample.labels.get("step") == step:
                return float(sample.value)
    return 0.0


def _exportable_invoice() -> dict[str, object]:
    invoice: InvoiceParseResponse = InvoiceParseResponse(
        status=ParseStatus.SUCCESS,
        message="ok",
        filename="sample.xml",
        file_type="xrechnung_xml",
        invoice_number="2025/10294",
        seller=PartyInfo(name="Muster GmbH"),
        totals=InvoiceTotals(gross=100, currency="EUR"),
    )
    return invoice.model_dump(mode="json")


class TestCapabilities(unittest.TestCase):
    def test_capabilities_describe_guest_limits_and_formats(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.get("/api/capabilities")
        self.assertEqual(response.status_code, 200)
        payload: dict[str, object] = response.json()
        self.assertEqual(payload["processing_model"], "guest")
        self.assertFalse(payload["stores_invoice_files"])
        self.assertFalse(payload["requires_account"])
        self.assertEqual(payload["max_files_per_request"], 1)
        self.assertEqual(payload["max_upload_size_mb"], settings.max_upload_size_mb)
        self.assertEqual(payload["parse_per_day"], settings.guest_parse_per_day)
        self.assertEqual(payload["export_per_day"], settings.guest_export_per_day)
        self.assertEqual(payload["max_parallel"], settings.guest_max_parallel)
        self.assertEqual(payload["account_rate_limit_per_minute"], settings.account_rate_limit_per_minute)
        self.assertIn(".xml", payload["allowed_extensions"])
        self.assertIn(".pdf", payload["allowed_extensions"])
        formats: list[dict[str, object]] = payload["formats"]  # type: ignore[assignment]
        ids: list[str] = [str(item["id"]) for item in formats]
        self.assertIn("ubl_invoice", ids)
        self.assertIn("zugferd_pdf", ids)
        self.assertTrue(payload["profiles"])
        self.assertTrue(payload["limitations"])


class TestFunnel(unittest.TestCase):
    def test_client_may_only_record_landing_and_upload(self) -> None:
        client: TestClient = TestClient(create_app())
        before_landing: float = _funnel_value("landing")
        ok = client.post("/api/telemetry/funnel", json={"step": "landing"})
        denied = client.post("/api/telemetry/funnel", json={"step": "parse_success"})
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(ok.json()["accepted"], True)
        self.assertEqual(denied.status_code, 422)
        self.assertEqual(_funnel_value("landing"), before_landing + 1.0)

    def test_rejected_parse_does_not_count_as_success(self) -> None:
        before: float = _funnel_value("parse_success")
        service: InvoiceService = InvoiceService()
        service.parse_upload(
            filename="note.txt",
            content=b"not-an-invoice",
            request_id="funnel-parse-1",
        )
        self.assertEqual(_funnel_value("parse_success"), before)

    def test_export_increments_funnel_but_report_does_not(self) -> None:
        client: TestClient = TestClient(create_app())
        invoice: dict[str, object] = _exportable_invoice()
        before: float = _funnel_value("export")
        export_response = client.post(
            "/api/invoices/export",
            json={"format": "csv", "invoice": invoice},
        )
        report_response = client.post(
            "/api/invoices/export/validation-report",
            json={"invoice": invoice},
        )
        self.assertEqual(export_response.status_code, 200)
        self.assertEqual(report_response.status_code, 200)
        self.assertEqual(_funnel_value("export"), before + 1.0)


class TestFeedback(unittest.TestCase):
    def test_accepts_text_without_invoice_payload(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.post(
            "/api/feedback",
            json={"message": "Die Export-Schaltflaeche war auf dem Handy schwer zu finden."},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["accepted"])
        self.assertNotIn("<Invoice>", response.text)

    def test_rejects_xml_and_iban(self) -> None:
        client: TestClient = TestClient(create_app())
        xml = client.post(
            "/api/feedback",
            json={"message": "Hier die Datei: <?xml version='1.0'?><Invoice></Invoice>"},
        )
        iban = client.post(
            "/api/feedback",
            json={"message": "Bitte pruefen: DE89370400440532013000 steht in der Datei."},
        )
        self.assertEqual(xml.status_code, 400)
        self.assertEqual(iban.status_code, 400)
        self.assertNotIn("DE89370400440532013000", iban.text)

    def test_feedback_is_rate_limited(self) -> None:
        with patch.object(settings, "rate_limit_per_minute", 1):
            client: TestClient = TestClient(create_app())
            first = client.post(
                "/api/feedback",
                json={"message": "Kurzes Feedback zur Bedienung der Seite."},
            )
            second = client.post(
                "/api/feedback",
                json={"message": "Noch ein kurzes Feedback zur Bedienung."},
            )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)


if __name__ == "__main__":
    unittest.main()
