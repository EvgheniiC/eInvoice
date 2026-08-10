"""HTTP middleware: request id + slow-request warning (no bodies logged)."""

from __future__ import annotations

import logging
import time
import uuid
from typing import Callable, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.error_events import log_event
from app.core.logging_config import format_log_fields

logger: logging.Logger = logging.getLogger("app.request")

REQUEST_ID_HEADER: str = "X-Request-ID"
# Warn when a request is unusually slow (possible hang / upstream timeout).
SLOW_REQUEST_MS: int = 15_000


class RequestObservabilityMiddleware(BaseHTTPMiddleware):
    """Attach request_id and log slow / failed HTTP responses without bodies."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id: str = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:12]
        request.state.request_id = request_id

        started: float = time.perf_counter()
        response: Response = await call_next(request)
        elapsed_ms: int = int((time.perf_counter() - started) * 1000)
        response.headers[REQUEST_ID_HEADER] = request_id

        if elapsed_ms >= SLOW_REQUEST_MS:
            log_event(
                logging.WARNING,
                "slow_request",
                fields={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "request_id": request_id,
                    "duration_ms": elapsed_ms,
                },
            )

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                format_log_fields(
                    {
                        "event": "request_done",
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": response.status_code,
                        "request_id": request_id,
                        "duration_ms": elapsed_ms,
                    }
                )
            )
        return response


def get_request_id(request: Request) -> Optional[str]:
    """Read request_id from request.state if middleware ran."""
    value: object = getattr(request.state, "request_id", None)
    return str(value) if value is not None else None
