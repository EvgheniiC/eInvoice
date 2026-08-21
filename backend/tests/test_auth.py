"""Account registration, sessions, org context, and guest parse coexistence."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.session import dispose_engine
from app.main import create_app


class TestAuthDisabled(unittest.TestCase):
    def test_guest_parse_works_without_database(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.post(
            "/api/invoices/parse",
            files={"file": ("note.txt", b"not-an-invoice", "text/plain")},
        )
        self.assertEqual(response.status_code, 400)
        me = client.get("/api/me")
        self.assertEqual(me.status_code, 503)

    def test_health_marks_database_not_required(self) -> None:
        client: TestClient = TestClient(create_app())
        payload: dict[str, object] = client.get("/api/health").json()
        names: list[str] = [str(item["name"]) for item in payload["checks"]]  # type: ignore[index]
        self.assertIn("database", names)


class TestAuthFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._patches = [
            patch.object(settings, "database_url", "sqlite://"),
            patch.object(settings, "auth_secret_key", "test-secret-key"),
            patch.object(settings, "environment", "development"),
            patch.object(settings, "admin_api_token", "admin-test-token"),
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

    def test_register_verify_login_org_and_manual_plus(self) -> None:
        register = self.client.post(
            "/api/auth/register",
            json={
                "email": "meister@example.com",
                "password": "sicher-passwort-1",
                "organization_name": "Muster Handwerk",
            },
        )
        self.assertEqual(register.status_code, 200)
        token: str | None = register.json().get("verification_token")
        self.assertTrue(token)

        blocked = self.client.post(
            "/api/auth/login",
            json={"email": "meister@example.com", "password": "sicher-passwort-1"},
        )
        self.assertEqual(blocked.status_code, 401)

        verified = self.client.post("/api/auth/verify-email", json={"token": token})
        self.assertEqual(verified.status_code, 200)
        self.assertEqual(verified.json()["organization_name"], "Muster Handwerk")
        self.assertEqual(verified.json()["role"], "inhaber")
        self.assertEqual(verified.json()["plan"]["code"], "free")
        self.assertTrue(verified.json()["plan"]["quotas_enforced"])
        self.assertEqual(verified.json()["plan"]["parse_per_day"], 10)
        self.assertEqual(verified.json()["plan"]["max_parallel"], 1)

        me = self.client.get("/api/me")
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], "meister@example.com")

        renamed = self.client.patch("/api/org", json={"name": "Muster GmbH"})
        self.assertEqual(renamed.status_code, 200)
        self.assertEqual(renamed.json()["name"], "Muster GmbH")

        plus = self.client.post(
            "/api/admin/plans",
            headers={"X-Admin-Token": "admin-test-token"},
            json={"email": "meister@example.com", "plan_code": "plus"},
        )
        self.assertEqual(plus.status_code, 200)
        self.assertEqual(plus.json()["plan"]["code"], "plus")

        me_plus = self.client.get("/api/me")
        self.assertEqual(me_plus.json()["plan"]["code"], "plus")
        self.assertTrue(me_plus.json()["plan"]["allows_batch"])
        self.assertEqual(me_plus.json()["plan"]["parse_per_day"], 100)
        self.assertEqual(me_plus.json()["plan"]["max_upload_size_mb"], 25)

        guest_style = self.client.post(
            "/api/invoices/parse",
            files={"file": ("note.txt", b"not-an-invoice", "text/plain")},
        )
        self.assertEqual(guest_style.status_code, 400)

        logout = self.client.post("/api/auth/logout")
        self.assertEqual(logout.status_code, 200)
        self.assertEqual(self.client.get("/api/me").status_code, 401)

        login = self.client.post(
            "/api/auth/login",
            json={"email": "meister@example.com", "password": "sicher-passwort-1"},
        )
        self.assertEqual(login.status_code, 200)

    def test_register_again_resends_when_unverified(self) -> None:
        payload: dict[str, str] = {
            "email": "retry@example.com",
            "password": "sicher-passwort-1",
            "organization_name": "Retry GmbH",
        }
        first = self.client.post("/api/auth/register", json=payload)
        second = self.client.post("/api/auth/register", json=payload)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        first_token: str | None = first.json().get("verification_token")
        second_token: str | None = second.json().get("verification_token")
        self.assertTrue(first_token)
        self.assertTrue(second_token)
        self.assertNotEqual(first_token, second_token)

    def test_register_smtp_misconfigured_returns_503(self) -> None:
        with patch.object(settings, "email_backend", "smtp"), patch.object(
            settings, "smtp_host", None
        ), patch.object(settings, "smtp_from", None), patch.object(
            settings, "smtp_username", None
        ):
            response = self.client.post(
                "/api/auth/register",
                json={"email": "smtp-fail@example.com", "password": "sicher-passwort-1"},
            )
        self.assertEqual(response.status_code, 503)
        self.assertIn("E-Mail", response.json()["detail"])

    def test_register_without_organization_uses_default_name(self) -> None:
        register = self.client.post(
            "/api/auth/register",
            json={"email": "solo@example.com", "password": "sicher-passwort-1"},
        )
        self.assertEqual(register.status_code, 200)
        token: str | None = register.json().get("verification_token")
        self.assertTrue(token)
        verified = self.client.post("/api/auth/verify-email", json={"token": token})
        self.assertEqual(verified.status_code, 200)
        self.assertEqual(verified.json()["organization_name"], "Meine Organisation")

    def test_magic_link_and_password_change(self) -> None:
        token: str = self._register_and_verify("buero@example.com")
        self.assertTrue(token)
        magic = self.client.post("/api/auth/magic-link", json={"email": "buero@example.com"})
        self.assertEqual(magic.status_code, 200)
        magic_token: str | None = magic.json().get("token")
        self.assertTrue(magic_token)
        self.client.post("/api/auth/logout")
        consumed = self.client.post(
            "/api/auth/magic-link/consume",
            json={"token": magic_token},
        )
        self.assertEqual(consumed.status_code, 200)

        changed = self.client.post(
            "/api/auth/change-password",
            json={
                "current_password": "sicher-passwort-1",
                "new_password": "anderes-passwort-9",
            },
        )
        self.assertEqual(changed.status_code, 200)
        self.assertEqual(self.client.get("/api/me").status_code, 401)
        old = self.client.post(
            "/api/auth/login",
            json={"email": "buero@example.com", "password": "sicher-passwort-1"},
        )
        self.assertEqual(old.status_code, 401)
        new = self.client.post(
            "/api/auth/login",
            json={"email": "buero@example.com", "password": "anderes-passwort-9"},
        )
        self.assertEqual(new.status_code, 200)

    def test_delete_user_allows_reregister(self) -> None:
        from app.db.session import session_scope
        from app.services.auth_service import delete_user_by_email

        self._register_and_verify("gone@example.com")
        for db_session in session_scope():
            deleted: str = delete_user_by_email(db_session, email="gone@example.com")
            self.assertEqual(deleted, "gone@example.com")
        again = self.client.post(
            "/api/auth/register",
            json={
                "email": "gone@example.com",
                "password": "sicher-passwort-1",
                "organization_name": "Neu GmbH",
            },
        )
        self.assertEqual(again.status_code, 200)
        self.assertTrue(again.json().get("verification_token"))

    def _register_and_verify(self, email: str) -> str:
        register = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "sicher-passwort-1",
                "organization_name": "Pilot GmbH",
            },
        )
        token: str = str(register.json()["verification_token"])
        self.client.post("/api/auth/verify-email", json={"token": token})
        return token


if __name__ == "__main__":
    unittest.main()
