"""Count one visit per browser per day, including guests."""

from __future__ import annotations

from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.services.site_stats_service import (
    apply_visitor_cookie,
    record_site_visit,
    resolve_visitor_id,
    should_track_request,
)


class VisitTrackingMiddleware(BaseHTTPMiddleware):
    """Set a random visitor cookie and store a hashed daily visit."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        track: bool = should_track_request(request)
        raw_id: str = ""
        is_new: bool = False
        if track:
            raw_id, is_new = resolve_visitor_id(request)
        response: Response = await call_next(request)
        if not track or not raw_id:
            return response
        record_site_visit(raw_id)
        if is_new:
            apply_visitor_cookie(response, raw_id)
        return response
