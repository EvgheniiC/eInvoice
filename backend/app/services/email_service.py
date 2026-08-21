"""Transactional auth emails. Invoice payloads are never attached."""

from __future__ import annotations

import logging
import re
import smtplib
import ssl
from email.message import EmailMessage
from typing import Match, Optional
from urllib.parse import quote

from app.core.config import settings
from app.core.error_events import log_event
from app.core.logging_config import sanitize_log_text

PURPOSE_VERIFY: str = "verify_email"
PURPOSE_MAGIC: str = "magic_link"
PURPOSE_RESET: str = "reset_password"
_ANGLE_EMAIL_RE: re.Pattern[str] = re.compile(r"<([^<>@\s]+@[^<>@\s]+)>")


class EmailDeliveryError(ValueError):
    """User-facing German error when the confirmation mail cannot be sent."""


def auth_link_url(*, purpose: str, token: str) -> str:
    """Public SPA URL that consumes the emailed token."""
    base: str = settings.public_app_url.rstrip("/")
    encoded: str = quote(token, safe="")
    if purpose == PURPOSE_MAGIC:
        return f"{base}/bestaetigen?kind=magic&token={encoded}"
    if purpose == PURPOSE_RESET:
        return f"{base}/passwort-zuruecksetzen?token={encoded}"
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
    subject: str
    body: str
    if purpose == PURPOSE_MAGIC:
        subject = "eInvoice: Anmeldelink"
        body = (
            "Guten Tag,\n\n"
            "melden Sie sich bei eInvoice über diesen Link an:\n\n"
            f"{url}\n\n"
            f"Der Link ist {hours} Stunden gültig.\n\n"
            "Wenn Sie keinen Anmeldelink angefordert haben, ignorieren Sie diese E-Mail.\n\n"
            "eInvoice\n"
        )
        return subject, body
    if purpose == PURPOSE_RESET:
        subject = "eInvoice: Passwort zurücksetzen"
        body = (
            "Guten Tag,\n\n"
            "Sie können Ihr eInvoice-Passwort über diesen Link neu setzen:\n\n"
            f"{url}\n\n"
            f"Der Link ist {hours} Stunden gültig.\n\n"
            "Wenn Sie kein neues Passwort angefordert haben, ignorieren Sie diese E-Mail.\n\n"
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
        raise EmailDeliveryError("E-Mail-Versand ist nicht eingerichtet.")
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
    sender: str = _smtp_address(settings.smtp_sender)
    username: str = _smtp_address(settings.smtp_username)
    password: str = _clean_secret(settings.smtp_password)
    if not username or not password or "@" not in sender:
        raise EmailDeliveryError("E-Mail-Versand ist nicht eingerichtet.")
    message: EmailMessage = EmailMessage()
    message["Subject"] = subject
    message["From"] = sender
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
                _authenticate_and_send(
                    client,
                    message,
                    username=username,
                    password=password,
                    sender=sender,
                    to_email=to_email,
                )
            return
        with smtplib.SMTP(
            host,
            settings.smtp_port,
            timeout=settings.smtp_timeout_seconds,
        ) as client:
            client.ehlo()
            if settings.smtp_starttls:
                client.starttls(context=ssl.create_default_context())
                client.ehlo()
            _authenticate_and_send(
                client,
                message,
                username=username,
                password=password,
                sender=sender,
                to_email=to_email,
            )
    except smtplib.SMTPAuthenticationError as exc:
        log_event(
            logging.ERROR,
            "auth_email_auth_failed",
            fields={"error": type(exc).__name__, "smtp_code": exc.smtp_code},
        )
        raise EmailDeliveryError(
            "Die SMTP-Anmeldung ist fehlgeschlagen. Bitte Benutzername und App-Passwort prüfen."
        ) from exc
    except smtplib.SMTPSenderRefused as exc:
        log_event(
            logging.ERROR,
            "auth_email_sender_refused",
            fields={
                "error": type(exc).__name__,
                "smtp_code": exc.smtp_code,
                "detail": _smtp_detail(exc),
                "from_domain": _email_domain(sender),
            },
        )
        raise EmailDeliveryError(
            "Der Absender wurde vom Mailserver abgelehnt. SMTP_FROM muss genau dem GMX-Konto entsprechen."
        ) from exc
    except (OSError, smtplib.SMTPException) as exc:
        log_event(
            logging.ERROR,
            "auth_email_failed",
            fields={
                "error": type(exc).__name__,
                "detail": _smtp_detail(exc),
            },
        )
        raise EmailDeliveryError(
            "Die Bestätigungs-E-Mail konnte nicht gesendet werden. Bitte später erneut versuchen."
        ) from exc


def _authenticate_and_send(
    client: smtplib.SMTP,
    message: EmailMessage,
    *,
    username: str,
    password: str,
    sender: str,
    to_email: str,
) -> None:
    client.login(username, password)
    client.sendmail(sender, [to_email], message.as_bytes())


def _smtp_address(value: Optional[str]) -> str:
    cleaned: str = _clean_secret(value)
    match: Optional[Match[str]] = _ANGLE_EMAIL_RE.search(cleaned)
    if match is not None:
        return match.group(1)
    return cleaned


def _smtp_detail(exc: BaseException) -> str:
    """Keep SMTP text loggable; angle brackets would be stripped as XML."""
    return sanitize_log_text(str(exc).replace("<", "(").replace(">", ")"), max_len=160)


def _clean_secret(value: Optional[str]) -> str:
    raw: str = (value or "").strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in {"'", '"'}:
        return raw[1:-1]
    return raw


def _email_domain(email: str) -> str:
    if "@" not in email:
        return "unknown"
    return email.rsplit("@", 1)[-1]
