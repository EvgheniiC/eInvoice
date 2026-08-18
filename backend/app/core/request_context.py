"""Request-scoped identifiers for logs and error tracking."""

from __future__ import annotations

from contextvars import ContextVar
from typing import Optional

_request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def set_request_id(request_id: str) -> None:
    """Bind the current request id to this task/context."""
    _request_id_var.set(request_id)


def reset_request_id() -> None:
    """Clear the request id after the request finishes."""
    _request_id_var.set(None)


def current_request_id() -> Optional[str]:
    """Return the request id for the active context, if any."""
    return _request_id_var.get()
