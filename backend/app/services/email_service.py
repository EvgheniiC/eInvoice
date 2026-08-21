"""Transactional auth emails. Invoice payloads are never attached."""

from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage
from typing import Optional
from urllib.parse import quote

from app.core.config import settings
from app.core.error_events import log_event

PURPOSE_VERIFY: str = "verify_email"
PURPOSE_MAGIC: str = "magic_link"

_FROM_NAME: str = "eInvoice"


class EmailDeliveryError(ValueError):
    """User-facing German error when the confirmation mail cannot be sent."""


def auth_link_url(*, purpose: str, token: str) -> str:
    """Public SPA URL that consumes the emailed token."""
    base: str = settings.public_app_url.rstrip("/")
    encoded: str = quote(token, safe="")
    if purpose == PURPOSE_MAGIC:
        return f"{base}/bestaetigen?kind=magic&token={encoded}"
    return f"{base}/bestaetigen?token={encoded}"


def send_auth_email(*, to_email: str, purpose: str, token: str) -> None:
    """Send or log a verification / magic-link message. Never includes invoice data."""
    subject: str
    body: str
    subject, body = _compose_message(purpose=purpose, token=token)
    log_event(
        logging.INFO,
        "auth_email_queued",
        fields={"purpose": purpose, "domain": _email_domain(to_email)},
    )
    backend: str = settings.email_backend.strip().lower()
    if backend == "log":
        _log_dev_message(purpose=purpose, token=token)
        return
    if backend != "smtp":
        raise EmailDeliveryError("E-Mail-Versand ist nicht eingerichtet.")
    _send_smtp(to_email=to_email, subject=subject, body=body)
    log_event(
        logging.INFO,
        "auth_email_sent",
        fields={"purpose": purpose, "domain": _email_domain(to_email)},
    )


def _compose_message(*, purpose: str, token: str) -> tuple[str, str]:
    url: str = auth_link_url(purpose=purpose, token=token)
    hours: int = settings.auth_token_hours
    if purpose == PURPOSE_MAGIC:
        subject: str = "eInvoice: Anmeldelink"
        body: str = (
            "Guten Tag,\n\n"
            "melden Sie sich bei eInvoice über diesen Link an:\n\n"
            f"{url}\n\n"
            f"Der Link ist {hours} Stunden gültig.\n\n"
            "Wenn Sie keinen Anmeldelink angefordert haben, ignorieren Sie diese E-Mail.\n\n"
            "eInvoice\n"
        )
        return subject, body
    subject = "eInvoice: Konto bestätigen"
    body = (
        "Guten Tag,\n\n"
        "bitte bestätigen Sie Ihr eInvoice-Konto über diesen Link:\n\n"
        f"{url}\n\n"
        f"Der Link ist {hours} Stunden gültig. Danach können Sie sich anmelden.\n\n"
        "Wenn Sie kein Konto erstellt haben, ignorieren Sie diese E-Mail.\n\n"
        "eInvoice\n"
    )
    return subject, body


def _log_dev_message(*, purpose: str, token: str) -> None:
    if settings.is_production:
        log_event(
            logging.ERROR,
            "auth_email_log_backend_in_production",
            fields={"purpose": purpose},
        )
        raise EmailDeliveryError(
            "Die Bestätigungs-E-Mail konnte nicht gesendet werden. Bitte später erneut versuchen."
        )
    log_event(
        logging.INFO,
        "auth_email_token_dev",
        fields={
            "purpose": purpose,
            "token": token,
            "url": auth_link_url(purpose=purpose, token=token),
        },
    )


def _send_smtp(*, to_email: str, subject: str, body: str) -> None:
    if not settings.smtp_configured:
        raise EmailDeliveryError("E-Mail-Versand ist nicht eingerichtet.")
    host: str = (settings.smtp_host or "").strip()
    sender: str = settings.smtp_sender
    message: EmailMessage = EmailMessage()
    message["Subject"] = subject
    message["From"] = f"{_FROM_NAME} <{sender}>"
    message["To"] = to_email
    message.set_content(body)
    try:
        if settings.smtp_ssl:
            context: ssl.SSLContext = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                host,
                settings.smtp_port,
                timeout=settings.smtp_timeout_seconds,
                context=context,
            ) as client:
                _authenticate_and_send(client, message)
            return
        with smtplib.SMTP(
            host,
            settings.smtp_port,
            timeout=settings.smtp_timeout_seconds,
        ) as client:
            if settings.smtp_starttls:
                client.starttls(context=ssl.create_default_context())
            _authenticate_and_send(client, message)
    except (OSError, smtplib.SMTPException) as exc:
        log_event(
            logging.ERROR,
            "auth_email_failed",
            fields={"error": type(exc).__name__},
        )
        raise EmailDeliveryError(
            "Die Bestätigungs-E-Mail konnte nicht gesendet werden. Bitte später erneut versuchen."
        ) from exc


def _authenticate_and_send(client: smtplib.SMTP, message: EmailMessage) -> None:
    username: Optional[str] = settings.smtp_username
    password: Optional[str] = settings.smtp_password
    if username and password:
        client.login(username, password)
    client.send_message(message)


def _email_domain(email: str) -> str:
    if "@" not in email:
        return "unknown"
    return email.rsplit("@", 1)[-1]
