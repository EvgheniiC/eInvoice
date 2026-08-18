"""Application logging setup for production observability.

Privacy rule: never log invoice XML/PDF bodies, payment details, or raw upload bytes.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from typing import Any, Mapping, Optional

from app.core.request_context import current_request_id

_WHITESPACE_RE: re.Pattern[str] = re.compile(r"\s+")

_CONFIGURED: bool = False


class JsonLogFormatter(logging.Formatter):
    """Emit one JSON object per line, including request_id when present."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
        }
        structured: object = getattr(record, "structured", None)
        if isinstance(structured, dict):
            for key, raw in structured.items():
                if raw is None:
                    continue
                payload[str(key)] = _json_safe_value(raw)
        else:
            message: str = sanitize_log_text(record.getMessage(), max_len=500)
            if message:
                payload["message"] = message

        request_id: Optional[str] = payload.get("request_id") or current_request_id()
        if request_id and "request_id" not in payload:
            payload["request_id"] = request_id

        if record.exc_info and record.exc_info[0] is not None:
            payload.setdefault("exc_type", record.exc_info[0].__name__)

        return json.dumps(payload, ensure_ascii=False, default=str)


class TextLogFormatter(logging.Formatter):
    """Human-readable lines for local debugging."""

    def __init__(self) -> None:
        super().__init__(
            fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )


def configure_logging(level: str = "INFO", log_format: str = "json", *, force: bool = False) -> None:
    """Configure root logging (stdout → journald under systemd)."""
    global _CONFIGURED
    if _CONFIGURED and not force:
        return

    resolved_level: int = getattr(logging, level.upper(), logging.INFO)
    resolved_format: str = log_format.strip().lower()
    formatter: logging.Formatter = (
        JsonLogFormatter() if resolved_format == "json" else TextLogFormatter()
    )

    root: logging.Logger = logging.getLogger()
    root.setLevel(resolved_level)

    if not root.handlers:
        handler: logging.StreamHandler[Any] = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(resolved_level)
        handler.setFormatter(formatter)
        root.addHandler(handler)
    else:
        for existing in root.handlers:
            existing.setLevel(resolved_level)
            existing.setFormatter(formatter)

    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)

    _CONFIGURED = True


def sanitize_log_text(value: Optional[str], *, max_len: int = 200) -> str:
    """Truncate and scrub text so invoice payloads never reach the log.

    Any angle-bracket content is treated as a potential XML/HTML fragment and dropped
    from the first '<' onward (keeps a short human-readable prefix only).
    """
    if not value:
        return ""
    cut_at: int = value.find("<")
    cleaned: str = value[:cut_at] if cut_at >= 0 else value
    cleaned = _WHITESPACE_RE.sub(" ", cleaned).strip()
    if len(cleaned) > max_len:
        return f"{cleaned[:max_len]}…"
    return cleaned


def format_log_fields(fields: Mapping[str, Any]) -> str:
    """Render key=value fields for easy journalctl grepping (text format / tests)."""
    parts: list[str] = []
    for key, raw in fields.items():
        if raw is None:
            continue
        text: str = sanitize_log_text(str(raw), max_len=120)
        if not text and isinstance(raw, str) and "<" in raw:
            continue
        if " " in text or "=" in text:
            text = text.replace('"', "'")
            parts.append(f'{key}="{text}"')
        else:
            parts.append(f"{key}={text}")
    return " ".join(parts)


def _json_safe_value(raw: Any) -> Any:
    if isinstance(raw, bool) or raw is None:
        return raw
    if isinstance(raw, (int, float)):
        return raw
    return sanitize_log_text(str(raw), max_len=180)
