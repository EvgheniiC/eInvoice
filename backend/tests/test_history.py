"""Plus/Team invoice history: opt-in metadata, optional originals, guest stays stateless."""

from __future__ import annotations

import hashlib
import tempfile
import unittest
import zipfile
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path
from typing import Optional
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.session import dispose_engine
from app.main import create_app
from app.schemas.invoice import InvoiceParseResponse, InvoiceTotals, PartyInfo, ParseStatus
from app.services.batch_service import drain_queue
from app.services.history_service import HISTORY_FORBIDDEN_DETAIL, ORIGINALS_GONE_DETAIL
from app.services.quota_service import reset_quota_runtime


class TestHistoryPaywall(unittest.TestCase):
    def test_guest_cannot_list_history(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.get("/api/invoices/history")
        self.assertEqual(response.status_code, 403)
        self.assertIn("Plus", response.json()["detail"])


class TestInvoiceHistory(unittest.TestCase):
    def setUp(self) -> None:
        reset_quota_runtime()
        self._temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self._patches = [
            patch.object(settings, "database_url", "sqlite://"),
            patch.object(settings, "auth_secret_key", "test-secret-key"),
            patch.object(settings, "environment", "development"),
            patch.object(settings, "admin_api_token", "admin-test-token"),
            patch.object(settings, "batch_temp_dir", self._temp.name),
            patch.object(settings, "history_original_dir", str(Path(self._temp.name) / "history")),
            patch.object(settings, "history_original_retention_days", 30),
            patch.object(settings, "rate_limit_per_minute", 200),
            patch.object(settings, "account_rate_limit_per_minute", 200),
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
        self._temp.cleanup()

    def test_free_plan_cannot_enable_or_list(self) -> None:
        self._register_and_verify("free-hist@example.com")
        denied = self.client.patch("/api/org", json={"history_enabled": True})
        self.assertEqual(denied.status_code, 403)
        listed = self.client.get("/api/invoices/history")
        self.assertEqual(listed.status_code, 403)
        self.assertEqual(listed.json()["detail"], HISTORY_FORBIDDEN_DETAIL)

    def test_plus_does_not_record_without_consent(self) -> None:
        self._register_plus("plus-off@example.com")
        with patch(
            "app.api.routes.invoices.invoice_service.parse_upload",
            side_effect=_parsed_invoice,
        ):
            parsed = self.client.post(
                "/api/invoices/parse",
                files={"file": ("a.xml", b"<Invoice/>", "application/xml")},
            )
        self.assertEqual(parsed.status_code, 200)
        listed = self.client.get("/api/invoices/history")
        self.assertEqual(listed.status_code, 200)
        body: dict[str, object] = listed.json()
        self.assertFalse(body["history_enabled"])
        self.assertEqual(body["total"], 0)
        self.assertEqual(body["items"], [])

    def test_plus_records_metadata_and_hash_only(self) -> None:
        self._register_plus("plus-meta@example.com")
        enabled = self.client.patch("/api/org", json={"history_enabled": True})
        self.assertEqual(enabled.status_code, 200)
        self.assertTrue(enabled.json()["history_enabled"])
        self.assertFalse(enabled.json()["store_originals_enabled"])
        payload: bytes = b"<Invoice id='one'/>"
        with patch(
            "app.api.routes.invoices.invoice_service.parse_upload",
            side_effect=_parsed_invoice,
        ):
            parsed = self.client.post(
                "/api/invoices/parse",
                files={"file": ("one.xml", payload, "application/xml")},
            )
        self.assertEqual(parsed.status_code, 200)
        listed = self.client.get("/api/invoices/history")
        self.assertEqual(listed.status_code, 200)
        items: list[dict[str, object]] = listed.json()["items"]
        self.assertEqual(len(items), 1)
        row: dict[str, object] = items[0]
        self.assertEqual(row["filename"], "one.xml")
        self.assertEqual(row["seller_name"], "Muster GmbH")
        self.assertEqual(row["invoice_number"], "RE-one.xml")
        self.assertEqual(row["gross_amount"], "119")
        self.assertEqual(row["currency"], "EUR")
        self.assertEqual(row["status"], "pruefen")
        self.assertEqual(row["file_hash"], hashlib.sha256(payload).hexdigest())
        self.assertFalse(row["original_available"])
        blocked = self.client.post(f"/api/invoices/history/{row['id']}/accountant-package")
        self.assertEqual(blocked.status_code, 410)
        self.assertEqual(blocked.json()["detail"], ORIGINALS_GONE_DETAIL)
        leftover: list[Path] = list((Path(self._temp.name) / "history").rglob("*"))
        files_left: list[Path] = [path for path in leftover if path.is_file()]
        self.assertEqual(files_left, [])

    def test_dateien_merken_allows_package_until_ttl(self) -> None:
        self._register_plus("plus-files@example.com")
        consent = self.client.patch(
            "/api/org",
            json={"history_enabled": True, "store_originals_enabled": True},
        )
        self.assertEqual(consent.status_code, 200)
        self.assertTrue(consent.json()["store_originals_enabled"])
        with patch(
            "app.api.routes.invoices.invoice_service.parse_upload",
            side_effect=_parsed_invoice,
        ):
            parsed = self.client.post(
                "/api/invoices/parse",
                files={"file": ("pack.xml", b"<Invoice/>", "application/xml")},
            )
        self.assertEqual(parsed.status_code, 200)
        listed = self.client.get("/api/invoices/history")
        row: dict[str, object] = listed.json()["items"][0]
        self.assertTrue(row["original_available"])
        package = self.client.post(f"/api/invoices/history/{row['id']}/accountant-package")
        self.assertEqual(package.status_code, 200)
        archive: zipfile.ZipFile = zipfile.ZipFile(BytesIO(package.content))
        names: list[str] = archive.namelist()
        self.assertTrue(any(name.endswith(".xlsx") for name in names))
        self.assertTrue(any("pack.xml" in name or name.endswith(".xml") for name in names))

        future: datetime = datetime.now(timezone.utc) + timedelta(days=31)
        with patch("app.services.history_service.utc_now", return_value=future):
            expired = self.client.get("/api/invoices/history")
            self.assertFalse(expired.json()["items"][0]["original_available"])
            gone = self.client.post(f"/api/invoices/history/{row['id']}/accountant-package")
            self.assertEqual(gone.status_code, 410)

    def test_guest_parse_still_writes_nothing(self) -> None:
        self._register_plus("plus-guest@example.com")
        self.client.patch("/api/org", json={"history_enabled": True})
        self.client.post("/api/auth/logout")
        with patch(
            "app.api.routes.invoices.invoice_service.parse_upload",
            side_effect=_parsed_invoice,
        ):
            parsed = self.client.post(
                "/api/invoices/parse",
                files={"file": ("guest.xml", b"<Invoice/>", "application/xml")},
            )
        self.assertEqual(parsed.status_code, 200)
        login = self.client.post(
            "/api/auth/login",
            json={"email": "plus-guest@example.com", "password": "sicher-passwort-1"},
        )
        self.assertEqual(login.status_code, 200)
        listed = self.client.get("/api/invoices/history")
        self.assertEqual(listed.json()["total"], 0)

    def test_org_isolation_and_batch_record(self) -> None:
        self._register_plus("hist-a@example.com")
        self.client.patch(
            "/api/org",
            json={"history_enabled": True, "store_originals_enabled": True},
        )
        with patch(
            "app.services.batch_service._invoice_service.parse_upload",
            side_effect=_parsed_invoice,
        ):
            created = self.client.post(
                "/api/invoices/batch",
                files=[("files", ("batch.xml", b"<Invoice/>", "application/xml"))],
            )
            self.assertEqual(created.status_code, 202)
            drain_queue()
        listed_a = self.client.get("/api/invoices/history")
        self.assertEqual(listed_a.json()["total"], 1)
        record_id: str = str(listed_a.json()["items"][0]["id"])

        self.client.post("/api/auth/logout")
        self._register_plus("hist-b@example.com")
        self.client.patch("/api/org", json={"history_enabled": True})
        hidden = self.client.get("/api/invoices/history")
        self.assertEqual(hidden.json()["total"], 0)
        stolen = self.client.post(f"/api/invoices/history/{record_id}/accountant-package")
        self.assertEqual(stolen.status_code, 404)

    def test_disable_originals_purges_files(self) -> None:
        self._register_plus("purge@example.com")
        self.client.patch(
            "/api/org",
            json={"history_enabled": True, "store_originals_enabled": True},
        )
        with patch(
            "app.api.routes.invoices.invoice_service.parse_upload",
            side_effect=_parsed_invoice,
        ):
            self.client.post(
                "/api/invoices/parse",
                files={"file": ("keep.xml", b"<Invoice/>", "application/xml")},
            )
        self.client.patch("/api/org", json={"store_originals_enabled": False})
        listed = self.client.get("/api/invoices/history")
        self.assertEqual(listed.json()["total"], 1)
        self.assertFalse(listed.json()["items"][0]["original_available"])
        leftover: list[Path] = list((Path(self._temp.name) / "history").rglob("*"))
        files_left: list[Path] = [path for path in leftover if path.is_file()]
        self.assertEqual(files_left, [])

    def _register_and_verify(self, email: str) -> None:
        register = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "sicher-passwort-1",
                "organization_name": "History GmbH",
            },
        )
        token: Optional[str] = register.json().get("verification_token")
        self.assertTrue(token)
        self.client.post("/api/auth/verify-email", json={"token": token})

    def _register_plus(self, email: str) -> None:
        self._register_and_verify(email)
        plus = self.client.post(
            "/api/admin/plans",
            headers={"X-Admin-Token": "admin-test-token"},
            json={"email": email, "plan_code": "plus"},
        )
        self.assertEqual(plus.status_code, 200)


def _parsed_invoice(filename: str, content: bytes, request_id: Optional[str] = None) -> InvoiceParseResponse:
    return InvoiceParseResponse(
        status=ParseStatus.SUCCESS,
        message="ok",
        filename=filename,
        file_type="xrechnung_xml",
        invoice_number=f"RE-{filename}",
        issue_date="2026-08-22",
        seller=PartyInfo(name="Muster GmbH"),
        totals=InvoiceTotals(net=100, tax=19, gross=119, currency="EUR"),
    )


if __name__ == "__main__":
    unittest.main()
