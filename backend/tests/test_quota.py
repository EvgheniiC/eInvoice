"""Plan quotas: guest vs plus/team parse/export limits, size, and rate class."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.session import dispose_engine
from app.main import create_app
from app.schemas.invoice import InvoiceParseResponse, InvoiceTotals, PartyInfo, ParseStatus
from app.services.plan_limits import PLAN_CATALOG, guest_limits
from app.services.quota_service import (
    QuotaExceededError,
    _parallel_slot,
    assert_upload_size,
    reset_quota_runtime,
)


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


class TestGuestQuotas(unittest.TestCase):
    def setUp(self) -> None:
        reset_quota_runtime()

    def test_guest_parse_without_login_still_works(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.post(
            "/api/invoices/parse",
            files={"file": ("note.xml", b"<Invoice/>", "application/xml")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Bitte anmelden", response.text)

    def test_guest_daily_parse_limit_returns_german_plus_cta(self) -> None:
        with patch.object(settings, "guest_parse_per_day", 2), patch.object(
            settings, "rate_limit_per_minute", 100
        ):
            client: TestClient = TestClient(create_app())
            files: dict[str, tuple[str, bytes, str]] = {
                "file": ("note.xml", b"<Invoice/>", "application/xml"),
            }
            first = client.post("/api/invoices/parse", files=files)
            second = client.post("/api/invoices/parse", files=files)
            third = client.post("/api/invoices/parse", files=files)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(third.status_code, 429)
        self.assertIn("Tageslimit für Prüfungen erreicht", third.json()["detail"])
        self.assertIn("Plus", third.json()["detail"])
        self.assertTrue(int(third.headers.get("Retry-After", "0")) >= 1)

    def test_wrong_type_does_not_consume_parse_quota(self) -> None:
        with patch.object(settings, "guest_parse_per_day", 1), patch.object(
            settings, "rate_limit_per_minute", 100
        ):
            client: TestClient = TestClient(create_app())
            denied = client.post(
                "/api/invoices/parse",
                files={"file": ("note.txt", b"not-an-invoice", "text/plain")},
            )
            allowed = client.post(
                "/api/invoices/parse",
                files={"file": ("note.xml", b"<Invoice/>", "application/xml")},
            )
        self.assertEqual(denied.status_code, 400)
        self.assertEqual(allowed.status_code, 200)

    def test_guest_export_limit_does_not_block_validation_report(self) -> None:
        invoice: dict[str, object] = _exportable_invoice()
        with patch.object(settings, "guest_export_per_day", 1), patch.object(
            settings, "rate_limit_per_minute", 100
        ):
            client: TestClient = TestClient(create_app())
            first = client.post(
                "/api/invoices/export",
                json={"format": "csv", "invoice": invoice},
            )
            second = client.post(
                "/api/invoices/export",
                json={"format": "csv", "invoice": invoice},
            )
            report = client.post(
                "/api/invoices/export/validation-report",
                json={"invoice": invoice},
            )
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 429)
        self.assertIn("Tageslimit für Exporte erreicht", second.json()["detail"])
        self.assertIn("Plus", second.json()["detail"])
        self.assertEqual(report.status_code, 200)

    def test_guest_file_size_mentions_plus(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            assert_upload_size(11 * 1024 * 1024, guest_limits())
        self.assertEqual(ctx.exception.status_code, 413)
        self.assertIn("Plus", str(ctx.exception.detail))


class TestPlanQuotas(unittest.TestCase):
    def setUp(self) -> None:
        reset_quota_runtime()
        self._patches = [
            patch.object(settings, "database_url", "sqlite://"),
            patch.object(settings, "auth_secret_key", "test-secret-key"),
            patch.object(settings, "environment", "development"),
            patch.object(settings, "admin_api_token", "admin-test-token"),
            patch.object(settings, "rate_limit_per_minute", 100),
        ]
        for item in self._patches:
            item.start()
        dispose_engine()
        init_account_store()
        self.client: TestClient = TestClient(create_app())

    def tearDown(self) -> None:
        self.client.close()
        dispose_engine()
        for item in reversed(self._patches):
            item.stop()
        reset_quota_runtime()

    def test_me_returns_enforced_free_quotas(self) -> None:
        self._register_and_verify("limits@example.com")
        me = self.client.get("/api/me")
        self.assertEqual(me.status_code, 200)
        plan: dict[str, object] = me.json()["plan"]
        self.assertTrue(plan["quotas_enforced"])
        self.assertEqual(plan["code"], "free")
        self.assertEqual(plan["parse_per_day"], PLAN_CATALOG["free"].parse_per_day)
        self.assertEqual(plan["export_per_day"], PLAN_CATALOG["free"].export_per_day)
        self.assertEqual(plan["max_upload_size_mb"], 10)
        self.assertEqual(plan["max_parallel"], 1)
        self.assertEqual(plan["parse_used_today"], 0)

    def test_org_quota_is_independent_from_guest_ip_quota(self) -> None:
        with patch.object(settings, "guest_parse_per_day", 1):
            guest_client: TestClient = TestClient(create_app())
            files: dict[str, tuple[str, bytes, str]] = {
                "file": ("note.xml", b"<Invoice/>", "application/xml"),
            }
            first = guest_client.post("/api/invoices/parse", files=files)
            blocked = guest_client.post("/api/invoices/parse", files=files)
            self.assertEqual(first.status_code, 200)
            self.assertEqual(blocked.status_code, 429)

            self._register_and_verify("org-quota@example.com")
            org_parse = self.client.post("/api/invoices/parse", files=files)
            self.assertEqual(org_parse.status_code, 200)
            me = self.client.get("/api/me")
            self.assertEqual(me.json()["plan"]["parse_used_today"], 1)

    def test_plus_plan_has_higher_catalog_limits(self) -> None:
        self._register_and_verify("plus-limits@example.com")
        plus = self.client.post(
            "/api/admin/plans",
            headers={"X-Admin-Token": "admin-test-token"},
            json={"email": "plus-limits@example.com", "plan_code": "plus"},
        )
        self.assertEqual(plus.status_code, 200)
        plan: dict[str, object] = plus.json()["plan"]
        self.assertEqual(plan["code"], "plus")
        self.assertEqual(plan["parse_per_day"], 100)
        self.assertEqual(plan["max_upload_size_mb"], 25)
        self.assertEqual(plan["max_parallel"], 2)
        self.assertTrue(plan["allows_batch"])

    def test_account_rate_limit_is_separate_from_guest(self) -> None:
        files: dict[str, tuple[str, bytes, str]] = {
            "file": ("note.txt", b"not-an-invoice", "text/plain"),
        }
        with patch.object(settings, "rate_limit_per_minute", 2), patch.object(
            settings, "account_rate_limit_per_minute", 10
        ):
            guest = TestClient(create_app())
            self.assertEqual(guest.post("/api/invoices/parse", files=files).status_code, 400)
            self.assertEqual(guest.post("/api/invoices/parse", files=files).status_code, 400)
            self.assertEqual(guest.post("/api/invoices/parse", files=files).status_code, 429)

            self._register_and_verify("rate@example.com")
            self.assertEqual(self.client.post("/api/invoices/parse", files=files).status_code, 400)
            self.assertEqual(self.client.post("/api/invoices/parse", files=files).status_code, 400)
            self.assertEqual(self.client.post("/api/invoices/parse", files=files).status_code, 400)

    def _register_and_verify(self, email: str) -> None:
        register = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "sicher-passwort-1",
                "organization_name": "Limit GmbH",
            },
        )
        token: str = str(register.json()["verification_token"])
        self.client.post("/api/auth/verify-email", json={"token": token})


class TestParallelSlots(unittest.TestCase):
    def setUp(self) -> None:
        reset_quota_runtime()

    def test_second_slot_is_rejected(self) -> None:
        with _parallel_slot("org-1", 1):
            with self.assertRaises(QuotaExceededError) as ctx:
                with _parallel_slot("org-1", 1):
                    pass
        self.assertIn("bereits eine Prüfung", ctx.exception.detail)

    def test_plus_size_message_has_no_guest_cta(self) -> None:
        with self.assertRaises(HTTPException) as ctx:
            assert_upload_size(26 * 1024 * 1024, PLAN_CATALOG["plus"])
        self.assertEqual(ctx.exception.status_code, 413)
        self.assertIn("Tarif", str(ctx.exception.detail))
        self.assertNotIn("Plus sind größere", str(ctx.exception.detail))


if __name__ == "__main__":
    unittest.main()
