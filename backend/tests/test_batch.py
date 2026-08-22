"""Plus/Team batch queue: enqueue, worker drain, summary. Guest parse stays unchanged."""

from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.session import dispose_engine
from app.main import create_app
from app.schemas.invoice import InvoiceParseResponse, InvoiceTotals, PartyInfo, ParseStatus
from app.services.batch_service import BATCH_FORBIDDEN_DETAIL, drain_queue
from app.services.quota_service import reset_quota_runtime


class TestBatchPaywall(unittest.TestCase):
    def test_guest_without_account_store_gets_plus_text(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.post(
            "/api/invoices/batch",
            files=[("files", ("a.xml", b"<Invoice/>", "application/xml"))],
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("Plus", response.json()["detail"])
        parse = client.post(
            "/api/invoices/parse",
            files={"file": ("a.xml", b"<Invoice/>", "application/xml")},
        )
        self.assertEqual(parse.status_code, 200)


class TestBatchQueue(unittest.TestCase):
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

    def test_free_plan_is_forbidden(self) -> None:
        self._register_and_verify("free-batch@example.com")
        response = self.client.post(
            "/api/invoices/batch",
            files=[
                ("files", ("a.xml", b"<Invoice/>", "application/xml")),
                ("files", ("b.xml", b"<Invoice/>", "application/xml")),
            ],
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], BATCH_FORBIDDEN_DETAIL)

    def test_plus_enqueues_and_worker_fills_summary(self) -> None:
        self._register_plus("plus-batch@example.com")
        created = self.client.post(
            "/api/invoices/batch",
            files=[
                ("files", ("one.xml", b"<Invoice/>", "application/xml")),
                ("files", ("two.xml", b"<Invoice/>", "application/xml")),
            ],
        )
        self.assertEqual(created.status_code, 202)
        payload: dict[str, object] = created.json()
        job_id: str = str(payload["id"])
        self.assertEqual(payload["status"], "queued")
        self.assertEqual(payload["item_count"], 2)
        self.assertEqual(payload["done_count"], 0)
        self.assertFalse(payload["export_package_available"])
        items: list[dict[str, object]] = payload["items"]  # type: ignore[assignment]
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["filename"], "one.xml")
        self.assertEqual(items[0]["status"], "queued")

        me = self.client.get("/api/me")
        self.assertEqual(me.json()["plan"]["parse_used_today"], 2)

        processed: int = drain_queue()
        self.assertEqual(processed, 2)

        listed = self.client.get(f"/api/invoices/batch/{job_id}")
        self.assertEqual(listed.status_code, 200)
        done: dict[str, object] = listed.json()
        self.assertEqual(done["status"], "completed")
        self.assertEqual(done["done_count"], 2)
        done_items: list[dict[str, object]] = done["items"]  # type: ignore[assignment]
        self.assertTrue(all(str(item["status"]) in {"gueltig", "pruefen", "ablehnen"} for item in done_items))
        self.assertTrue(all(item.get("invoice") is not None for item in done_items))
        leftover: list[Path] = list(Path(self._temp.name).rglob("*"))
        files_left: list[Path] = [path for path in leftover if path.is_file()]
        self.assertEqual(len(files_left), 2)

        parse_still_works = self.client.post(
            "/api/invoices/parse",
            files={"file": ("single.xml", b"<Invoice/>", "application/xml")},
        )
        self.assertEqual(parse_still_works.status_code, 200)

    def test_zip_expands_xml_members(self) -> None:
        self._register_plus("zip-batch@example.com")
        archive: bytes = _xml_zip([("one.xml", b"<Invoice>1</Invoice>"), ("two.xml", b"<Invoice>2</Invoice>")])
        response = self.client.post(
            "/api/invoices/batch",
            files=[("files", ("pack.zip", archive, "application/zip"))],
        )
        self.assertEqual(response.status_code, 202)
        payload: dict[str, object] = response.json()
        self.assertEqual(payload["item_count"], 2)
        items: list[dict[str, object]] = payload["items"]  # type: ignore[assignment]
        names: list[str] = [str(item["filename"]) for item in items]
        self.assertEqual(names, ["one.xml", "two.xml"])
        me = self.client.get("/api/me")
        self.assertEqual(me.json()["plan"]["parse_used_today"], 2)

    def test_corrupt_zip_is_rejected(self) -> None:
        self._register_plus("zip-bad@example.com")
        response = self.client.post(
            "/api/invoices/batch",
            files=[("files", ("pack.zip", b"PK\x03\x04", "application/zip"))],
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("ZIP", response.json()["detail"])

    def test_too_many_files_rejected(self) -> None:
        self._register_plus("many-batch@example.com")
        files: list[tuple[str, tuple[str, bytes, str]]] = [
            ("files", (f"file{index}.xml", b"<Invoice/>", "application/xml"))
            for index in range(21)
        ]
        response = self.client.post("/api/invoices/batch", files=files)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Maximal 20", response.json()["detail"])

    def test_quota_covers_every_file(self) -> None:
        self._register_plus("quota-batch@example.com")
        with patch(
            "app.services.quota_service.limits_for_context",
        ) as mocked_limits:
            from app.services.plan_limits import PLAN_CATALOG

            plus = PLAN_CATALOG["plus"]
            mocked_limits.return_value = type(plus)(
                code=plus.code,
                name=plus.name,
                parse_per_day=1,
                export_per_day=plus.export_per_day,
                max_upload_size_mb=plus.max_upload_size_mb,
                max_parallel=plus.max_parallel,
                allows_batch=True,
                allows_history=True,
                max_batch_files=20,
            )
            response = self.client.post(
                "/api/invoices/batch",
                files=[
                    ("files", ("a.xml", b"<Invoice/>", "application/xml")),
                    ("files", ("b.xml", b"<Invoice/>", "application/xml")),
                ],
            )
        self.assertEqual(response.status_code, 429)
        self.assertIn("Tageslimit für Prüfungen", response.json()["detail"])

    def test_other_org_cannot_read_job(self) -> None:
        self._register_plus("owner-batch@example.com")
        created = self.client.post(
            "/api/invoices/batch",
            files=[("files", ("a.xml", b"<Invoice/>", "application/xml"))],
        )
        job_id: str = str(created.json()["id"])
        self.client.post("/api/auth/logout")
        self._register_plus("other-batch@example.com")
        hidden = self.client.get(f"/api/invoices/batch/{job_id}")
        self.assertEqual(hidden.status_code, 404)

    def test_accountant_package_contains_originals_and_combined_exports(self) -> None:
        self._register_plus("zip-package@example.com")
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

        listed = self.client.get(f"/api/invoices/batch/{job_id}")
        self.assertEqual(listed.status_code, 200)
        self.assertTrue(listed.json()["export_package_available"])

        package = self.client.post(f"/api/invoices/batch/{job_id}/accountant-package")
        self.assertEqual(package.status_code, 200)
        self.assertIn("application/zip", package.headers["content-type"])
        self.assertIn("buchhaltung_paket_", package.headers.get("content-disposition", ""))
        with zipfile.ZipFile(io.BytesIO(package.content)) as archive:
            names: list[str] = archive.namelist()
            self.assertIn("summary.txt", names)
            self.assertIn("export_manifest.txt", names)
            self.assertIn("datev_hinweise.txt", names)
            self.assertIn("pruefbericht_paket.txt", names)
            self.assertTrue(any(name.endswith(".xlsx") for name in names))
            self.assertTrue(any(name.startswith("datev_rechnungen_") for name in names))
            originals: list[str] = [name for name in names if name.startswith("original/")]
            self.assertEqual(len(originals), 2)
            self.assertTrue(any(name.endswith(".xml") for name in originals))

        me = self.client.get("/api/me")
        self.assertEqual(me.json()["plan"]["export_used_today"], 1)

    def test_accountant_package_gone_after_ttl(self) -> None:
        self._register_plus("zip-ttl@example.com")
        created = self.client.post(
            "/api/invoices/batch",
            files=[("files", ("one.xml", b"<Invoice/>", "application/xml"))],
        )
        job_id: str = str(created.json()["id"])
        with patch(
            "app.services.batch_service._invoice_service.parse_upload",
            side_effect=_parsed_invoice,
        ):
            self.assertEqual(drain_queue(), 1)
        future: datetime = datetime.now(timezone.utc) + timedelta(hours=3)
        with patch("app.services.batch_service.utc_now", return_value=future):
            listed = self.client.get(f"/api/invoices/batch/{job_id}")
            self.assertEqual(listed.status_code, 200)
            self.assertFalse(listed.json()["export_package_available"])
            gone = self.client.post(f"/api/invoices/batch/{job_id}/accountant-package")
        self.assertEqual(gone.status_code, 410)
        files_left: list[Path] = [path for path in Path(self._temp.name).rglob("*") if path.is_file()]
        self.assertEqual(files_left, [])

    def test_other_org_cannot_download_package(self) -> None:
        self._register_plus("owner-pack@example.com")
        created = self.client.post(
            "/api/invoices/batch",
            files=[("files", ("a.xml", b"<Invoice/>", "application/xml"))],
        )
        job_id: str = str(created.json()["id"])
        with patch(
            "app.services.batch_service._invoice_service.parse_upload",
            side_effect=_parsed_invoice,
        ):
            drain_queue()
        self.client.post("/api/auth/logout")
        self._register_plus("other-pack@example.com")
        hidden = self.client.post(f"/api/invoices/batch/{job_id}/accountant-package")
        self.assertEqual(hidden.status_code, 404)

    def test_incomplete_job_rejects_package(self) -> None:
        self._register_plus("queued-pack@example.com")
        created = self.client.post(
            "/api/invoices/batch",
            files=[("files", ("a.xml", b"<Invoice/>", "application/xml"))],
        )
        job_id: str = str(created.json()["id"])
        blocked = self.client.post(f"/api/invoices/batch/{job_id}/accountant-package")
        self.assertEqual(blocked.status_code, 409)

    def _register_and_verify(self, email: str) -> None:
        register = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "sicher-passwort-1",
                "organization_name": "Batch GmbH",
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
        self.assertTrue(plus.json()["plan"]["allows_batch"])
        self.assertEqual(plus.json()["plan"]["max_batch_files"], 20)


def _xml_zip(members: list[tuple[str, bytes]]) -> bytes:
    buffer: io.BytesIO = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, payload in members:
            archive.writestr(name, payload)
    return buffer.getvalue()


def _parsed_invoice(filename: str, content: bytes, request_id: Optional[str] = None) -> InvoiceParseResponse:
    invoice: InvoiceParseResponse = InvoiceParseResponse(
        status=ParseStatus.SUCCESS,
        message="ok",
        filename=filename,
        file_type="xrechnung_xml",
        invoice_number=f"RE-{filename}",
        issue_date="2026-08-22",
        seller=PartyInfo(name="Muster GmbH"),
        totals=InvoiceTotals(net=100, tax=19, gross=119, currency="EUR"),
    )
    return invoice


if __name__ == "__main__":
    unittest.main()
