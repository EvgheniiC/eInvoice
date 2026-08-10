"""Application logging setup for production observability.

Privacy rule: never log invoice XML/PDF bodies, payment details, or raw upload bytes.
"""

from __future__ import annotations

import logging
import re
import sys
from typing import Any, Mapping, Optional

_WHITESPACE_RE: re.Pattern[str] = re.compile(r"\s+")

_CONFIGURED: bool = False


def configure_logging(level: str = "INFO") -> None:
    """Configure root logging once (stdout → journald under systemd)."""
    global _CONFIGURED
    if _CONFIGURED:
        return

    resolved_level: int = getattr(logging, level.upper(), logging.INFO)
    root: logging.Logger = logging.getLogger()
    root.setLevel(resolved_level)

    if not root.handlers:
        handler: logging.StreamHandler[Any] = logging.StreamHandler(stream=sys.stdout)
        handler.setLevel(resolved_level)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)s [%(name)s] %(message)s",
                datefmt="%Y-%m-%dT%H:%M:%S%z",
            )
        )
        root.addHandler(handler)
    else:
        root.setLevel(resolved_level)
        for existing in root.handlers:
            existing.setLevel(resolved_level)

    # Keep noisy libraries quieter unless debugging.
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
    """Render key=value fields for easy journalctl grepping."""
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
