"""HTTP security middleware: headers, rate limit, and request timeout."""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.error_events import log_event, log_timeout
from app.core.middleware import get_request_id

_RATE_LIMITED_PREFIXES: tuple[str, ...] = (
    "/api/invoices",
    "/api/feedback",
    "/api/telemetry",
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach conservative security headers to every HTTP response."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response: Response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'",
        )
        if settings.is_production:
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        if request.method.upper() in {"POST", "PUT", "PATCH", "DELETE"}:
            response.headers.setdefault("Cache-Control", "no-store")
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory per-IP sliding window for invoice upload/export endpoints."""

    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        limit: int = settings.rate_limit_per_minute
        if limit <= 0 or request.method.upper() == "OPTIONS":
            return await call_next(request)
        if not _is_rate_limited_path(request.url.path):
            return await call_next(request)

        now: float = time.monotonic()
        window_start: float = now - 60.0
        client_key: str = _client_key(request)
        bucket: Deque[float] = self._hits[client_key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= limit:
            log_event(
                logging.WARNING,
                "rate_limited",
                fields={
                    "path": request.url.path,
                    "method": request.method,
                    "request_id": get_request_id(request),
                },
            )
            return JSONResponse(
                status_code=429,
                content={"detail": "Zu viele Anfragen. Bitte warten Sie einen Moment."},
                headers={"Retry-After": "60"},
            )
        bucket.append(now)
        return await call_next(request)


class RequestTimeoutMiddleware(BaseHTTPMiddleware):
    """Fail long-running requests instead of tying up a worker indefinitely."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        timeout_seconds: float = float(settings.request_timeout_seconds)
        if timeout_seconds <= 0:
            return await call_next(request)
        try:
            return await asyncio.wait_for(call_next(request), timeout=timeout_seconds)
        except asyncio.TimeoutError:
            log_timeout(
                component="http_request",
                request_id=get_request_id(request),
                timeout_seconds=settings.request_timeout_seconds,
                detail=f"{request.method} {request.url.path}",
            )
            return JSONResponse(
                status_code=504,
                content={"detail": "Die Verarbeitung hat zu lange gedauert."},
            )


def _is_rate_limited_path(path: str) -> bool:
    return any(path == prefix or path.startswith(prefix + "/") for prefix in _RATE_LIMITED_PREFIXES)


def _client_key(request: Request) -> str:
    forwarded: Optional[str] = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip() or "unknown"
    if request.client is not None and request.client.host:
        return request.client.host
    return "unknown"
