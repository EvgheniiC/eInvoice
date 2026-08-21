"""Auth email composition and SMTP delivery."""

from __future__ import annotations

import smtplib
import unittest
from typing import Optional
from unittest.mock import MagicMock, patch

from app.core.config import settings
from app.services.email_service import (
    EmailDeliveryError,
    auth_link_url,
    send_auth_email,
)


class _FakeSMTP:
    def __init__(self, *args: object, **kwargs: object) -> None:
        self.started_tls: bool = False
        self.login_user: Optional[str] = None
        self.sent_from: Optional[str] = None
        self.sent_to: Optional[object] = None
        self.sent_payload: Optional[bytes] = None

    def __enter__(self) -> "_FakeSMTP":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def ehlo(self, name: str = "") -> None:
        return None

    def starttls(self, *, context: object = None) -> None:
        self.started_tls = True

    def login(self, username: str, _password: str) -> None:
        self.login_user = username

    def sendmail(
        self,
        from_addr: str,
        to_addrs: object,
        msg: bytes,
        mail_options: object = (),
        rcpt_options: object = (),
    ) -> dict[str, tuple[int, bytes]]:
        self.sent_from = from_addr
        self.sent_to = to_addrs
        self.sent_payload = msg
        return {}


class TestAuthLinkUrl(unittest.TestCase):
    def test_verify_and_magic_urls(self) -> None:
        with patch.object(settings, "public_app_url", "https://app.example/"):
            self.assertEqual(
                auth_link_url(purpose="verify_email", token="abc+1"),
                "https://app.example/bestaetigen?token=abc%2B1",
            )
            self.assertEqual(
                auth_link_url(purpose="magic_link", token="tok"),
                "https://app.example/bestaetigen?kind=magic&token=tok",
            )


class TestSendAuthEmail(unittest.TestCase):
    def test_log_backend_does_not_open_smtp(self) -> None:
        with patch.object(settings, "email_backend", "log"), patch.object(
            settings, "environment", "development"
        ), patch("app.services.email_service.smtplib.SMTP") as smtp_cls:
            send_auth_email(to_email="meister@example.com", purpose="verify_email", token="dev-token")
            smtp_cls.assert_not_called()

    def test_log_backend_fails_in_production(self) -> None:
        with patch.object(settings, "email_backend", "log"), patch.object(
            settings, "environment", "production"
        ):
            with self.assertRaises(EmailDeliveryError):
                send_auth_email(
                    to_email="meister@example.com",
                    purpose="verify_email",
                    token="secret-token",
                )

    def test_smtp_sends_plaintext_message(self) -> None:
        fake: _FakeSMTP = _FakeSMTP()
        with patch.object(settings, "email_backend", "smtp"), patch.object(
            settings, "smtp_host", "smtp.example.com"
        ), patch.object(settings, "smtp_port", 587), patch.object(
            settings, "smtp_username", "mailer@example.com"
        ), patch.object(settings, "smtp_password", "secret"), patch.object(
            settings, "smtp_from", "noreply@example.com"
        ), patch.object(settings, "smtp_starttls", True), patch.object(
            settings, "smtp_ssl", False
        ), patch.object(settings, "public_app_url", "https://app.example"), patch(
            "app.services.email_service.smtplib.SMTP", return_value=fake
        ):
            send_auth_email(to_email="meister@example.com", purpose="verify_email", token="tok-1")

        self.assertTrue(fake.started_tls)
        self.assertEqual(fake.login_user, "mailer@example.com")
        self.assertEqual(fake.sent_from, "noreply@example.com")
        self.assertEqual(fake.sent_to, ["meister@example.com"])
        self.assertIsNotNone(fake.sent_payload)
        payload: bytes = fake.sent_payload  # type: ignore[assignment]
        self.assertIn(b"From: noreply@example.com", payload)
        self.assertIn(b"https://app.example/bestaetigen?token=tok-1", payload)

    def test_smtp_error_becomes_delivery_error(self) -> None:
        failing: MagicMock = MagicMock()
        failing.__enter__.side_effect = smtplib.SMTPConnectError(421, b"down")
        with patch.object(settings, "email_backend", "smtp"), patch.object(
            settings, "smtp_host", "smtp.example.com"
        ), patch.object(settings, "smtp_from", "noreply@example.com"), patch.object(
            settings, "smtp_username", "mailer@example.com"
        ), patch.object(settings, "smtp_password", "secret"), patch(
            "app.services.email_service.smtplib.SMTP", return_value=failing
        ):
            with self.assertRaises(EmailDeliveryError):
                send_auth_email(
                    to_email="meister@example.com",
                    purpose="verify_email",
                    token="tok-1",
                )

    def test_smtp_sender_refused_is_mapped(self) -> None:
        fake: _FakeSMTP = _FakeSMTP()

        def _refuse(
            from_addr: str,
            to_addrs: object,
            msg: bytes,
            mail_options: object = (),
            rcpt_options: object = (),
        ) -> dict[str, tuple[int, bytes]]:
            raise smtplib.SMTPSenderRefused(553, b"Sender address rejected", from_addr)

        fake.sendmail = _refuse  # type: ignore[method-assign]
        with patch.object(settings, "email_backend", "smtp"), patch.object(
            settings, "smtp_host", "smtp.example.com"
        ), patch.object(settings, "smtp_port", 587), patch.object(
            settings, "smtp_username", "mailer@example.com"
        ), patch.object(settings, "smtp_password", "secret"), patch.object(
            settings, "smtp_from", "noreply@example.com"
        ), patch.object(settings, "smtp_starttls", True), patch.object(
            settings, "smtp_ssl", False
        ), patch("app.services.email_service.smtplib.SMTP", return_value=fake):
            with self.assertRaises(EmailDeliveryError) as ctx:
                send_auth_email(
                    to_email="meister@example.com",
                    purpose="verify_email",
                    token="tok-1",
                )
        self.assertIn("Absender", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
