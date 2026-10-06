"""Administrator statistics: daily visitors and Plus/Team headcount."""

from __future__ import annotations

import unittest
from datetime import date, timedelta
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.core.clock import usage_date_today
from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.models import Membership, Organization, Plan, User
from app.db.session import dispose_engine, get_session_factory
from app.main import create_app

ADMIN_EMAIL: str = "admin@example.com"
PASSWORD: str = "sicher-passwort-1"


class TestAdminStats(unittest.TestCase):
    def setUp(self) -> None:
        self._patches = [
            patch.object(settings, "database_url", "sqlite://"),
            patch.object(settings, "auth_secret_key", "test-secret-key"),
            patch.object(settings, "environment", "development"),
            patch.object(settings, "admin_api_token", "admin-test-token"),
            patch.object(settings, "admin_emails", "Admin@Example.com"),
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

    def test_paid_users_count_each_person_once(self) -> None:
        self._verify("plus@example.com")
        self._verify("team@example.com")
        self._verify("free@example.com")
        self._verify(ADMIN_EMAIL)
        headers: dict[str, str] = {"X-Admin-Token": "admin-test-token"}
        plus = self.client.post(
            "/api/admin/plans",
            headers=headers,
            json={"email": "plus@example.com", "plan_code": "plus"},
        )
        team = self.client.post(
            "/api/admin/plans",
            headers=headers,
            json={"email": "team@example.com", "plan_code": "team"},
        )
        self.assertEqual(plus.status_code, 200)
        self.assertEqual(team.status_code, 200)
        self._add_team_membership("plus@example.com")
        self._login(ADMIN_EMAIL)

        me = self.client.get("/api/me")
        self.assertEqual(me.status_code, 200)
        self.assertTrue(me.json()["is_admin"])

        stats = self.client.get("/api/admin/stats")
        self.assertEqual(stats.status_code, 200)
        body: dict[str, object] = stats.json()
        self.assertEqual(body["paid_plan_users"], 2)
        visits_by_day: list[dict[str, object]] = body["visits_by_day"]  # type: ignore[assignment]
        self.assertEqual(len(visits_by_day), 14)

    def test_other_accounts_cannot_read_stats(self) -> None:
        self._verify("other@example.com")
        self._login("other@example.com")
        me = self.client.get("/api/me")
        self.assertFalse(me.json()["is_admin"])
        denied = self.client.get("/api/admin/stats")
        self.assertEqual(denied.status_code, 403)

        self.client.post("/api/auth/logout")
        anonymous = self.client.get("/api/admin/stats")
        self.assertEqual(anonymous.status_code, 401)

    def test_guests_count_once_per_day_and_health_checks_do_not(self) -> None:
        self._verify(ADMIN_EMAIL)
        self._login(ADMIN_EMAIL)
        admin_cookies: list[tuple[str, str]] = list(self.client.cookies.items())
        today: date = usage_date_today()
        yesterday: date = today - timedelta(days=1)

        self.client.cookies.clear()
        with patch("app.services.site_stats_service.usage_date_today", return_value=yesterday):
            first = self.client.get("/api/capabilities")
            repeat_yesterday = self.client.get("/api/capabilities")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(repeat_yesterday.status_code, 200)
        self.assertIn("einv_visitor", self.client.cookies)

        today_visit = self.client.get("/api/capabilities")
        self.assertEqual(today_visit.status_code, 200)
        self.client.get("/api/capabilities")

        self.client.cookies.clear()
        self.assertEqual(self.client.get("/api/health").status_code, 200)
        self.assertEqual(self.client.get("/api/health/live").status_code, 200)
        self.assertNotIn("einv_visitor", self.client.cookies)

        self.client.cookies.clear()
        for name, value in admin_cookies:
            self.client.cookies.set(name, value)

        stats = self.client.get("/api/admin/stats")
        self.assertEqual(stats.status_code, 200)
        body: dict[str, object] = stats.json()
        self.assertEqual(body["visits_today"], 2)
        visits_by_day: list[dict[str, object]] = body["visits_by_day"]  # type: ignore[assignment]
        yesterday_row: dict[str, object] = next(
            item for item in visits_by_day if item["visit_date"] == yesterday.isoformat()
        )
        self.assertEqual(yesterday_row["visitors"], 1)

    def _verify(self, email: str) -> None:
        registered = self.client.post(
            "/api/auth/register",
            json={
                "email": email,
                "password": PASSWORD,
                "organization_name": "Muster Handwerk",
            },
        )
        self.assertEqual(registered.status_code, 200)
        token: str = str(registered.json()["verification_token"])
        verified = self.client.post("/api/auth/verify-email", json={"token": token})
        self.assertEqual(verified.status_code, 200)

    def _login(self, email: str) -> None:
        logged_in = self.client.post(
            "/api/auth/login",
            json={"email": email, "password": PASSWORD},
        )
        self.assertEqual(logged_in.status_code, 200)

    def _add_team_membership(self, email: str) -> None:
        factory: sessionmaker[Session] | None = get_session_factory()
        self.assertIsNotNone(factory)
        assert factory is not None
        session: Session = factory()
        try:
            user: User | None = session.scalar(select(User).where(User.email == email))
            plan: Plan | None = session.scalar(select(Plan).where(Plan.code == "team"))
            self.assertIsNotNone(user)
            self.assertIsNotNone(plan)
            assert user is not None and plan is not None
            organization: Organization = Organization(name="Zweite Firma", plan_id=plan.id)
            session.add(organization)
            session.flush()
            session.add(
                Membership(
                    user_id=user.id,
                    organization_id=organization.id,
                    role="buero",
                )
            )
            session.commit()
        finally:
            session.close()
