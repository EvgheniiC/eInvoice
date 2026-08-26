"""Checkout stub: return URL applies the selected plan without a real payment."""

from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select

from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.models import BillingCheckoutSession, Membership, Organization, Plan
from app.db.session import dispose_engine, session_scope
from app.main import create_app

ADMIN_HEADERS: dict[str, str] = {"X-Admin-Token": "admin-test-token"}


class TestBillingCheckout(unittest.TestCase):
    def setUp(self) -> None:
        self._patches: list[Any] = [
            patch.object(settings, "database_url", "sqlite://"),
            patch.object(settings, "auth_secret_key", "test-secret-key"),
            patch.object(settings, "environment", "development"),
            patch.object(settings, "admin_api_token", "admin-test-token"),
            patch.object(settings, "billing_provider", "stub"),
            patch.object(settings, "public_app_url", "http://localhost:5173"),
            patch.object(settings, "rate_limit_per_minute", 200),
            patch.object(settings, "account_rate_limit_per_minute", 200),
            patch.object(settings, "admin_rate_limit_per_minute", 200),
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

    def test_checkout_requires_authentication(self) -> None:
        response: Response = self.client.post(
            "/api/billing/checkout",
            json={"requested_plan": "plus"},
        )
        self.assertEqual(response.status_code, 401)

    def test_only_inhaber_can_start_checkout(self) -> None:
        self._register_and_verify("office-bill@example.com")
        for db_session in session_scope():
            membership: Membership | None = db_session.scalar(select(Membership))
            self.assertIsNotNone(membership)
            assert membership is not None
            membership.role = "buero"
            db_session.commit()
        response: Response = self.client.post(
            "/api/billing/checkout",
            json={"requested_plan": "plus"},
        )
        self.assertEqual(response.status_code, 403)

    def test_same_plan_is_rejected(self) -> None:
        self._register_and_verify("same-plan@example.com")
        activated: Response = self.client.post(
            "/api/admin/plans",
            headers=ADMIN_HEADERS,
            json={"email": "same-plan@example.com", "plan_code": "plus"},
        )
        self.assertEqual(activated.status_code, 200)
        response: Response = self.client.post(
            "/api/billing/checkout",
            json={"requested_plan": "plus"},
        )
        self.assertEqual(response.status_code, 400)

    def test_stub_return_activates_plan(self) -> None:
        self._register_and_verify("paid@example.com")
        created: Response = self.client.post(
            "/api/billing/checkout",
            json={"requested_plan": "plus"},
        )
        self.assertEqual(created.status_code, 201)
        payload: dict[str, str] = created.json()
        self.assertEqual(payload["provider"], "stub")
        parsed = urlparse(payload["checkout_url"])
        self.assertEqual(parsed.path, "/tarife")
        query: dict[str, list[str]] = parse_qs(parsed.query)
        self.assertEqual(query["checkout"], ["success"])
        session_token: str = query["session"][0]
        self.assertEqual(payload["session_id"], session_token)

        completed: Response = self.client.post(
            "/api/billing/complete",
            json={"session": session_token},
        )
        self.assertEqual(completed.status_code, 200)
        self.assertEqual(completed.json()["plan_code"], "plus")
        self.assertEqual(self.client.get("/api/me").json()["plan"]["code"], "plus")

        again: Response = self.client.post(
            "/api/billing/complete",
            json={"session": session_token},
        )
        self.assertEqual(again.status_code, 200)
        self.assertEqual(again.json()["plan_code"], "plus")
        for db_session in session_scope():
            rows: list[BillingCheckoutSession] = list(
                db_session.scalars(select(BillingCheckoutSession)).all()
            )
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0].status, "completed")
            organization: Organization | None = db_session.get(Organization, rows[0].organization_id)
            self.assertIsNotNone(organization)
            assert organization is not None
            plan: Plan | None = db_session.get(Plan, organization.plan_id)
            self.assertIsNotNone(plan)
            assert plan is not None
            self.assertEqual(plan.code, "plus")

    def test_unknown_session_is_not_found(self) -> None:
        self._register_and_verify("missing@example.com")
        response: Response = self.client.post(
            "/api/billing/complete",
            json={"session": "stub_does-not-exist-token"},
        )
        self.assertEqual(response.status_code, 404)

    def _register_and_verify(self, email: str) -> None:
        register: Response = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "sicher-passwort-1",
                "organization_name": "Billing GmbH",
            },
        )
        token: str = str(register.json()["verification_token"])
        verified: Response = self.client.post(
            "/api/auth/verify-email",
            json={"token": token},
        )
        self.assertEqual(verified.status_code, 200)


if __name__ == "__main__":
    unittest.main()
