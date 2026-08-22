"""Organization firm profile (A6): persist details and copy them into the ZIP."""

from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from typing import Optional
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.session import dispose_engine
from app.main import create_app
from app.schemas.invoice import InvoiceParseResponse, InvoiceTotals, PartyInfo, ParseStatus
from app.services.batch_service import drain_queue
from app.services.quota_service import reset_quota_runtime

VALID_IBAN: str = "DE89370400440532013000"


class TestOrgProfile(unittest.TestCase):
    def setUp(self) -> None:
        reset_quota_runtime()
        self._temp: tempfile.TemporaryDirectory[str] = tempfile.TemporaryDirectory()
        self._patches = [
            patch.object(settings, "database_url", "sqlite://"),
            patch.object(settings, "auth_secret_key", "test-secret-key"),
            patch.object(settings, "environment", "development"),
            patch.object(settings, "admin_api_token", "admin-test-token"),
            patch.object(settings, "batch_temp_dir", self._temp.name),
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

    def test_profile_roundtrip_and_clear(self) -> None:
        self._register_and_verify("profil@example.com")
        saved = self.client.patch(
            "/api/org",
            json={
                "name": "Muster Handwerk GmbH",
                "tax_number": "12/345/67890",
                "vat_id": "de123456789",
                "iban": "DE89 3704 0044 0532 0130 00",
                "accountant_email": "kanzlei@example.de",
            },
        )
        self.assertEqual(saved.status_code, 200)
        body: dict[str, object] = saved.json()
        self.assertEqual(body["name"], "Muster Handwerk GmbH")
        self.assertEqual(body["tax_number"], "12/345/67890")
        self.assertEqual(body["vat_id"], "DE123456789")
        self.assertEqual(body["iban"], VALID_IBAN)
        self.assertEqual(body["accountant_email"], "kanzlei@example.de")

        loaded = self.client.get("/api/org")
        self.assertEqual(loaded.status_code, 200)
        self.assertEqual(loaded.json()["iban"], VALID_IBAN)

        cleared = self.client.patch("/api/org", json={"iban": "", "accountant_email": ""})
        self.assertEqual(cleared.status_code, 200)
        self.assertIsNone(cleared.json()["iban"])
        self.assertIsNone(cleared.json()["accountant_email"])
        self.assertEqual(cleared.json()["tax_number"], "12/345/67890")

    def test_invalid_iban_and_email_are_rejected(self) -> None:
        self._register_and_verify("bad-profil@example.com")
        bad_iban = self.client.patch("/api/org", json={"iban": "DE00000000000000000000"})
        self.assertEqual(bad_iban.status_code, 400)
        self.assertEqual(bad_iban.json()["detail"], "IBAN ist ungültig.")

        bad_vat = self.client.patch("/api/org", json={"vat_id": "123"})
        self.assertEqual(bad_vat.status_code, 400)
        self.assertEqual(bad_vat.json()["detail"], "USt-IdNr. ist ungültig.")

        bad_email = self.client.patch("/api/org", json={"accountant_email": "nicht-email"})
        self.assertEqual(bad_email.status_code, 400)
        self.assertEqual(bad_email.json()["detail"], "E-Mail des Steuerberaters ist ungültig.")

    def test_non_inhaber_cannot_change_profile(self) -> None:
        self._register_and_verify("inhaber-profil@example.com")
        from sqlalchemy import select

        from app.db.models import Membership
        from app.db.session import session_scope

        for db_session in session_scope():
            membership: Membership | None = db_session.scalar(select(Membership))
            self.assertIsNotNone(membership)
            assert membership is not None
            membership.role = "buero"
            db_session.commit()

        denied = self.client.patch("/api/org", json={"iban": VALID_IBAN})
        self.assertEqual(denied.status_code, 403)

    def test_batch_package_contains_mandant_sheet(self) -> None:
        self._register_plus("zip-profil@example.com")
        saved = self.client.patch(
            "/api/org",
            json={
                "tax_number": "11/222/33333",
                "vat_id": "DE814742004",
                "iban": VALID_IBAN,
                "accountant_email": "sb@kanzlei.de",
            },
        )
        self.assertEqual(saved.status_code, 200)

        created = self.client.post(
            "/api/invoices/batch",
            files=[
                ("files", ("one.xml", b"<Invoice>1</Invoice>", "application/xml")),
                ("files", ("two.xml", b"<Invoice>2</Invoice>", "application/xml")),
            ],
        )
        self.assertEqual(created.status_code, 202)
        job_id: str = str(created.json()["id"])
        with patch(
            "app.services.batch_service._invoice_service.parse_upload",
            side_effect=_parsed_invoice,
        ):
            self.assertEqual(drain_queue(), 2)

        package = self.client.post(f"/api/invoices/batch/{job_id}/accountant-package")
        self.assertEqual(package.status_code, 200)
        with zipfile.ZipFile(io.BytesIO(package.content)) as archive:
            names: list[str] = archive.namelist()
            self.assertIn("mandant.txt", names)
            mandant: str = archive.read("mandant.txt").decode("utf-8")
            self.assertIn("11/222/33333", mandant)
            self.assertIn("DE814742004", mandant)
            self.assertIn(VALID_IBAN, mandant)
            self.assertIn("sb@kanzlei.de", mandant)
            summary: str = archive.read("summary.txt").decode("utf-8")
            self.assertIn("Mandant:", summary)
            self.assertIn(VALID_IBAN, summary)
            manifest: str = archive.read("export_manifest.txt").decode("utf-8")
            self.assertIn("mandant.txt", manifest)

    def _register_and_verify(self, email: str) -> None:
        register = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "sicher-passwort-1",
                "organization_name": "Profil GmbH",
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
        seller=PartyInfo(name="Lieferant GmbH"),
        totals=InvoiceTotals(net=100, tax=19, gross=119, currency="EUR"),
    )


if __name__ == "__main__":
    unittest.main()
