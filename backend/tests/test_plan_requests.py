"""Focused API tests for manual subscription upgrade requests."""

from __future__ import annotations

import unittest
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient
from httpx import Response
from sqlalchemy import select

from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.models import Membership, PlanUpgradeRequest
from app.db.session import dispose_engine, session_scope
from app.main import create_app

ADMIN_HEADERS: dict[str, str] = {"X-Admin-Token": "admin-test-token"}


class TestPlanRequests(unittest.TestCase):
    def setUp(self) -> None:
        self._patches: list[Any] = [
            patch.object(settings, "database_url", "sqlite://"),
            patch.object(settings, "auth_secret_key", "test-secret-key"),
            patch.object(settings, "environment", "development"),
            patch.object(settings, "admin_api_token", "admin-test-token"),
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

    def test_create_requires_authentication(self) -> None:
        response: Response = self.client.post(
            "/api/plan-requests",
            json={"requested_plan": "plus"},
        )
        self.assertEqual(response.status_code, 401)

    def test_only_inhaber_can_create_request(self) -> None:
        self._register_and_verify("office@example.com")
        for db_session in session_scope():
            membership: Membership | None = db_session.scalar(select(Membership))
            self.assertIsNotNone(membership)
            assert membership is not None
            membership.role = "buero"
            db_session.commit()

        response: Response = self.client.post(
            "/api/plan-requests",
            json={"requested_plan": "plus"},
        )
        self.assertEqual(response.status_code, 403)

    def test_requested_plan_is_validated_as_upgrade(self) -> None:
        self._register_and_verify("validation@example.com")
        invalid: Response = self.client.post(
            "/api/plan-requests",
            json={"requested_plan": "free"},
        )
        self.assertEqual(invalid.status_code, 422)

        activated: Response = self.client.post(
            "/api/admin/plans",
            headers=ADMIN_HEADERS,
            json={"email": "validation@example.com", "plan_code": "plus"},
        )
        self.assertEqual(activated.status_code, 200)
        same_plan: Response = self.client.post(
            "/api/plan-requests",
            json={"requested_plan": "plus"},
        )
        self.assertEqual(same_plan.status_code, 400)

    def test_duplicate_pending_request_is_idempotent(self) -> None:
        self._register_and_verify("duplicate@example.com")
        payload: dict[str, str] = {
            "requested_plan": "plus",
            "message": " Bitte freischalten. ",
        }
        first: Response = self.client.post("/api/plan-requests", json=payload)
        second: Response = self.client.post("/api/plan-requests", json=payload)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 201)
        self.assertEqual(first.json()["id"], second.json()["id"])
        self.assertEqual(first.json()["message"], "Bitte freischalten.")
        for db_session in session_scope():
            requests: list[PlanUpgradeRequest] = list(
                db_session.scalars(select(PlanUpgradeRequest)).all()
            )
            self.assertEqual(len(requests), 1)

    def test_admin_can_list_and_finalize_without_activating_plan(self) -> None:
        self._register_and_verify("admin-list@example.com")
        created: Response = self.client.post(
            "/api/plan-requests",
            json={"requested_plan": "team"},
        )
        request_id: str = str(created.json()["id"])

        unauthorized: Response = self.client.get("/api/admin/plan-requests")
        self.assertEqual(unauthorized.status_code, 401)
        pending: Response = self.client.get(
            "/api/admin/plan-requests",
            headers=ADMIN_HEADERS,
        )
        self.assertEqual(pending.status_code, 200)
        self.assertEqual([item["id"] for item in pending.json()], [request_id])

        approved: Response = self.client.patch(
            f"/api/admin/plan-requests/{request_id}",
            headers=ADMIN_HEADERS,
            json={"status": "approved"},
        )
        self.assertEqual(approved.status_code, 200)
        self.assertEqual(approved.json()["status"], "approved")
        self.assertEqual(self.client.get("/api/me").json()["plan"]["code"], "free")

        pending_after: Response = self.client.get(
            "/api/admin/plan-requests",
            headers=ADMIN_HEADERS,
        )
        all_requests: Response = self.client.get(
            "/api/admin/plan-requests?status=all",
            headers=ADMIN_HEADERS,
        )
        self.assertEqual(pending_after.json(), [])
        self.assertEqual(len(all_requests.json()), 1)
        repeated: Response = self.client.patch(
            f"/api/admin/plan-requests/{request_id}",
            headers=ADMIN_HEADERS,
            json={"status": "rejected"},
        )
        self.assertEqual(repeated.status_code, 409)

    def _register_and_verify(self, email: str) -> None:
        register: Response = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": "sicher-passwort-1",
                "organization_name": "Plan Request GmbH",
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
