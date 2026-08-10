"""Structured error/event helpers for API observability (no invoice bodies)."""

from __future__ import annotations

import logging
import traceback
from pathlib import Path
from typing import Any, Mapping, Optional

from app.core.logging_config import format_log_fields, sanitize_log_text

logger: logging.Logger = logging.getLogger("app.errors")


def safe_filename(filename: Optional[str]) -> str:
    """Keep only the basename so paths never leak into logs."""
    if not filename:
        return ""
    return Path(filename).name


def format_safe_stack(exc: BaseException, *, max_frames: int = 8) -> str:
    """Stack frames + sanitized exception text (no raw invoice payloads)."""
    frames: list[str] = []
    extracted: traceback.StackSummary = traceback.extract_tb(exc.__traceback__)
    for frame in extracted[-max_frames:]:
        frames.append(f"{Path(frame.filename).name}:{frame.lineno}:{frame.name}")
    summary: str = sanitize_log_text(str(exc), max_len=120)
    head: str = " > ".join(frames) if frames else "no-frames"
    if summary:
        return f"{head} | {type(exc).__name__}: {summary}"
    return f"{head} | {type(exc).__name__}"


def log_event(
    level: int,
    event: str,
    *,
    fields: Optional[Mapping[str, Any]] = None,
) -> None:
    """Emit a structured observability event without stdlib exc_info tracebacks."""
    payload: dict[str, Any] = {"event": event}
    if fields:
        payload.update(dict(fields))
    logger.log(level, format_log_fields(payload))


def log_parse_failure(
    *,
    code: str,
    filename: Optional[str],
    file_type: str,
    size_bytes: Optional[int] = None,
    request_id: Optional[str] = None,
    exc_type: Optional[str] = None,
    detail: Optional[str] = None,
    level: int = logging.WARNING,
) -> None:
    """Log a parse pipeline failure without the invoice payload."""
    fields: dict[str, Any] = {
        "code": code,
        "filename": safe_filename(filename),
        "file_type": file_type,
        "size_bytes": size_bytes,
        "request_id": request_id,
        "exc_type": exc_type,
        "detail": sanitize_log_text(detail, max_len=180) if detail else None,
    }
    log_event(level, "parse_failed", fields=fields)


def log_api_error(
    *,
    event: str,
    method: str,
    path: str,
    status_code: int,
    request_id: Optional[str] = None,
    detail: Optional[str] = None,
    exc_type: Optional[str] = None,
    stack: Optional[str] = None,
    level: int = logging.ERROR,
) -> None:
    """Log an HTTP API failure (5xx / unexpected)."""
    fields: dict[str, Any] = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "request_id": request_id,
        "exc_type": exc_type,
        "detail": sanitize_log_text(detail, max_len=180) if detail else None,
        "stack": stack,
    }
    log_event(level, event, fields=fields)


def log_timeout(
    *,
    component: str,
    request_id: Optional[str] = None,
    timeout_seconds: Optional[int] = None,
    detail: Optional[str] = None,
) -> None:
    """Log a timeout (e.g. KoSIT validator)."""
    fields: dict[str, Any] = {
        "component": component,
        "request_id": request_id,
        "timeout_seconds": timeout_seconds,
        "detail": sanitize_log_text(detail, max_len=180) if detail else None,
    }
    log_event(logging.ERROR, "timeout", fields=fields)
