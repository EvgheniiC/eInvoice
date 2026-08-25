"""HTTP security headers, rate limiting, and KoSIT process hardening."""

from __future__ import annotations

import unittest
from typing import Callable, Optional
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import create_app
from app.services.en16931_validator import build_kosit_command, kosit_preexec_fn


class TestSecurityHeaders(unittest.TestCase):
    def test_health_sets_security_headers(self) -> None:
        client: TestClient = TestClient(create_app())
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(response.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(response.headers.get("Referrer-Policy"), "no-referrer")
        self.assertIn("default-src 'none'", response.headers.get("Content-Security-Policy", ""))
        self.assertIsNone(response.headers.get("Strict-Transport-Security"))

    def test_production_adds_hsts(self) -> None:
        with patch.object(settings, "environment", "production"):
            client: TestClient = TestClient(create_app())
            response = client.get("/api/health")
        self.assertEqual(
            response.headers.get("Strict-Transport-Security"),
            "max-age=31536000; includeSubDomains",
        )


class TestRateLimit(unittest.TestCase):
    def test_invoice_parse_returns_429_when_limit_exceeded(self) -> None:
        with patch.object(settings, "rate_limit_per_minute", 2):
            client: TestClient = TestClient(create_app())
            files: dict[str, tuple[str, bytes, str]] = {
                "file": ("note.txt", b"not-an-invoice", "text/plain"),
            }
            first = client.post("/api/invoices/parse", files=files)
            second = client.post("/api/invoices/parse", files=files)
            third = client.post("/api/invoices/parse", files=files)
        self.assertEqual(first.status_code, 400)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(third.status_code, 429)
        self.assertEqual(third.json()["detail"], "Zu viele Anfragen. Bitte warten Sie einen Moment.")
        self.assertNotIn("not-an-invoice", third.text)

    def test_health_is_not_rate_limited(self) -> None:
        with patch.object(settings, "rate_limit_per_minute", 1):
            client: TestClient = TestClient(create_app())
            first = client.get("/api/health")
            second = client.get("/api/health")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)


class TestKositHardening(unittest.TestCase):
    def test_command_puts_heap_limit_before_jar(self) -> None:
        command: list[str] = build_kosit_command(
            java_bin="java",
            jar="/opt/validator.jar",
            scenarios="/opt/scenarios.xml",
            output_dir="/tmp/kosit",
            xml_path="/tmp/kosit/invoice.xml",
            max_heap_mb=512,
        )
        jar_index: int = command.index("-jar")
        self.assertTrue(any(item.startswith("-Xmx") for item in command[:jar_index]))
        self.assertEqual(command[jar_index + 1], "/opt/validator.jar")
        self.assertIn("-Djava.awt.headless=true", command)

    def test_preexec_is_posix_only(self) -> None:
        hook: Optional[Callable[[], None]] = kosit_preexec_fn(timeout_seconds=60)
        if hook is None:
            self.assertTrue(True)
            return
        import resource

        setrlimit_mock: MagicMock
        with patch.object(resource, "setrlimit") as setrlimit_mock:
            hook()

        resources: list[int] = [call.args[0] for call in setrlimit_mock.call_args_list]
        self.assertIn(resource.RLIMIT_CPU, resources)
        self.assertIn(resource.RLIMIT_CORE, resources)
        self.assertNotIn(resource.RLIMIT_AS, resources)


if __name__ == "__main__":
    unittest.main()
