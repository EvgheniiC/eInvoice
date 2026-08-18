"""Tests for privacy-safe error logging (no invoice bodies in logs)."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.logging_config import sanitize_log_text
from app.main import create_app
from app.services.invoice_service import InvoiceService


class TestSanitizeLogText(unittest.TestCase):
    def test_strips_xml_tags(self) -> None:
        raw: str = 'Error near <Invoice><IBAN>DE89370400440532013000</IBAN></Invoice> end'
        cleaned: str = sanitize_log_text(raw)
        self.assertEqual(cleaned, "Error near")
        self.assertNotIn("DE89370400440532013000", cleaned)
        self.assertNotIn("<Invoice>", cleaned)


    def test_truncates_long_text(self) -> None:
        cleaned: str = sanitize_log_text("x" * 500, max_len=50)
        self.assertLessEqual(len(cleaned), 51)
        self.assertTrue(cleaned.endswith("…"))


class TestParseFailureLogging(unittest.TestCase):
    def test_unsupported_type_emits_parse_failed_without_body(self) -> None:
        service: InvoiceService = InvoiceService()
        with self.assertLogs("app.errors", level="WARNING") as captured:
            result = service.parse_upload(
                filename="note.txt",
                content=b"secret-invoice-body-should-not-appear",
                request_id="reqtest1",
            )
        self.assertEqual(result.status.value, "error")
        joined: str = "\n".join(captured.output)
        self.assertIn("parse_failed", joined)
        self.assertIn("UNSUPPORTED_TYPE", joined)
        self.assertIn("reqtest1", joined)
        self.assertNotIn("secret-invoice-body-should-not-appear", joined)

    def test_parse_exception_does_not_leak_exception_payload(self) -> None:
        service: InvoiceService = InvoiceService()
        xml_body: bytes = (
            b'<?xml version="1.0"?>'
            b'<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2">'
            b"<ID>1</ID></Invoice>"
        )

        with patch(
            "app.services.invoice_service.get_xml_header",
            side_effect=RuntimeError("<Secret>XML-BODY</Secret>"),
        ):
            with self.assertLogs("app.errors", level="ERROR") as captured:
                result = service.parse_upload(
                    filename="broken.xml",
                    content=xml_body,
                    request_id="reqtest2",
                )

        self.assertEqual(result.status.value, "error")
        self.assertTrue(
            any(issue.code == "PARSE_EXCEPTION" for issue in result.validation_issues)
        )
        joined = "\n".join(captured.output)
        self.assertIn("PARSE_EXCEPTION", joined)
        self.assertIn("RuntimeError", joined)
        self.assertNotIn("XML-BODY", joined)
        self.assertNotIn("<Secret>", joined)
        # API detail must stay generic (no raw exception / XML).
        self.assertEqual(
            result.validation_issues[0].message,
            "Unerwarteter Fehler beim Lesen der Datei.",
        )


class TestApiErrorHandlers(unittest.TestCase):
    def test_health_returns_request_id_header(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers.get("X-Request-ID"))
        payload: dict[str, object] = response.json()
        self.assertIn(payload["status"], {"ok", "degraded"})
        self.assertIn("kosit_ready", payload)
        self.assertIn("kosit_required", payload)
        self.assertIn("ready", payload)
        self.assertIsInstance(payload["checks"], list)

    def test_unhandled_exception_returns_500_and_logs(self) -> None:
        app = create_app()

        @app.get("/api/_test_boom")
        def _boom() -> None:
            raise RuntimeError("boom-payload-<Invoice>leak</Invoice>")

        client: TestClient = TestClient(app, raise_server_exceptions=False)
        with self.assertLogs("app.errors", level="ERROR") as captured:
            response = client.get("/api/_test_boom")
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "Interner Serverfehler.")
        joined: str = "\n".join(captured.output)
        self.assertIn("unhandled_exception", joined)
        self.assertNotIn("<Invoice>", joined)
        self.assertNotIn("leak", joined)



if __name__ == "__main__":
    unittest.main()
