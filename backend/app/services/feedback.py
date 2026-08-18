from __future__ import annotations

import logging
import re
from typing import Optional

import requests

from app.core.config import settings
from app.core.error_events import log_event
from app.core.logging_config import sanitize_log_text

_IBAN_RE: re.Pattern[str] = re.compile(
    r"(?<![A-Z0-9])[A-Z]{2}\d{2}[A-Z0-9]{10,30}(?![A-Z0-9])"
)
_EMAIL_RE: re.Pattern[str] = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_FORBIDDEN_SNIPPETS: tuple[str, ...] = (
    "<?xml",
    "<invoice",
    "<creditnote",
    "<rsm:",
    "%pdf-",
)
_WEBHOOK_TIMEOUT_SECONDS: float = 5.0


class FeedbackRejected(ValueError):
    """User-facing German rejection for unsafe or empty feedback."""


def submit_feedback(
    *,
    message: str,
    contact_email: Optional[str],
    request_id: Optional[str],
) -> str:
    """Validate text-only feedback, never persist an invoice file."""
    cleaned: str = _normalize_message(message)
    _assert_safe_message(cleaned)
    email: Optional[str] = _normalize_email(contact_email)

    log_event(
        logging.INFO,
        "feedback_received",
        fields={
            "request_id": request_id,
            "char_count": len(cleaned),
            "has_contact": email is not None,
        },
    )

    webhook: Optional[str] = settings.feedback_webhook_url
    if webhook:
        _post_webhook(
            webhook_url=webhook,
            message=cleaned,
            contact_email=email,
            request_id=request_id,
        )
        return "Vielen Dank. Ihre Nachricht wurde übermittelt."

    log_event(
        logging.INFO,
        "feedback_stored_in_log",
        fields={
            "request_id": request_id,
            "preview": sanitize_log_text(cleaned, max_len=240),
        },
    )
    return (
        "Vielen Dank. Ihre Nachricht wurde aufgenommen. "
        "Bitte keine Rechnungsdatei nachreichen."
    )


def _normalize_message(message: str) -> str:
    text: str = message.strip()
    if len(text) < 10:
        raise FeedbackRejected("Bitte beschreiben Sie Ihr Anliegen etwas genauer.")
    max_chars: int = settings.feedback_max_chars
    if len(text) > max_chars:
        raise FeedbackRejected(f"Die Nachricht ist zu lang. Maximum: {max_chars} Zeichen.")
    return text


def _assert_safe_message(message: str) -> None:
    lowered: str = message.lower()
    for snippet in _FORBIDDEN_SNIPPETS:
        if snippet in lowered:
            raise FeedbackRejected(
                "Bitte keine Rechnungsdatei und keinen XML- oder PDF-Inhalt einfügen."
            )
    compacted: str = re.sub(r"\s+", "", message)
    if _IBAN_RE.search(message) is not None or _IBAN_RE.search(compacted) is not None:
        raise FeedbackRejected("Bitte keine IBAN oder anderen Rechnungsinhalt einfügen.")


def _normalize_email(contact_email: Optional[str]) -> Optional[str]:
    if contact_email is None:
        return None
    value: str = contact_email.strip()
    if not value:
        return None
    if len(value) > 254 or _EMAIL_RE.match(value) is None:
        raise FeedbackRejected("Bitte eine gültige E-Mail-Adresse angeben oder das Feld leer lassen.")
    return value


def _post_webhook(
    *,
    webhook_url: str,
    message: str,
    contact_email: Optional[str],
    request_id: Optional[str],
) -> None:
    try:
        response: requests.Response = requests.post(
            webhook_url,
            json={
                "source": "einvoice-feedback",
                "message": message,
                "contact_email": contact_email,
                "request_id": request_id,
            },
            timeout=_WEBHOOK_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException:
        log_event(
            logging.ERROR,
            "feedback_webhook_failed",
            fields={"request_id": request_id},
        )
        raise FeedbackRejected(
            "Der Feedback-Kanal ist gerade nicht erreichbar. Bitte versuchen Sie es später erneut."
        ) from None
