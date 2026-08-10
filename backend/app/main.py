import logging
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import api_router
from app.core.config import settings
from app.core.error_events import format_safe_stack, log_api_error
from app.core.logging_config import configure_logging
from app.core.middleware import RequestObservabilityMiddleware, get_request_id


def create_app() -> FastAPI:
    """Application factory for the eInvoice FastAPI backend."""
    configure_logging(settings.log_level)

    application: FastAPI = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # Outer-most for request handling after CORS: observability wraps the app.
    application.add_middleware(RequestObservabilityMiddleware)
    _register_exception_handlers(application)
    application.include_router(api_router, prefix="/api")
    return application


def _register_exception_handlers(application: FastAPI) -> None:
    """Log unexpected failures; never include request/invoice bodies in responses or logs."""

    @application.exception_handler(StarletteHTTPException)
    async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        if exc.status_code >= 500:
            log_api_error(
                event="http_exception",
                method=request.method,
                path=request.url.path,
                status_code=exc.status_code,
                request_id=get_request_id(request),
                detail=str(exc.detail),
                exc_type=type(exc).__name__,
            )
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=_request_id_headers(request),
        )

    @application.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        # Do not log request body / file contents from validation errors.
        log_api_error(
            event="request_validation_failed",
            method=request.method,
            path=request.url.path,
            status_code=422,
            request_id=get_request_id(request),
            detail=_validation_summary(exc),
            exc_type="RequestValidationError",
            level=logging.WARNING,
        )
        return JSONResponse(
            status_code=422,
            content={"detail": "Ungültige Anfrage."},
            headers=_request_id_headers(request),
        )

    @application.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
    ) -> JSONResponse:
        log_api_error(
            event="unhandled_exception",
            method=request.method,
            path=request.url.path,
            status_code=500,
            request_id=get_request_id(request),
            detail=str(exc),
            exc_type=type(exc).__name__,
            stack=format_safe_stack(exc),
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Interner Serverfehler."},
            headers=_request_id_headers(request),
        )


def _request_id_headers(request: Request) -> Dict[str, str]:
    request_id: Optional[str] = get_request_id(request)
    if not request_id:
        return {}
    return {"X-Request-ID": request_id}


def _validation_summary(exc: RequestValidationError) -> str:
    """Summarize validation errors without dumping uploaded payloads."""
    parts: list[str] = []
    for err in exc.errors()[:5]:
        loc: Any = err.get("loc", ())
        loc_safe: str = ".".join(str(item) for item in loc if item != "body")
        err_type: str = str(err.get("type", "error"))
        parts.append(f"{loc_safe}:{err_type}" if loc_safe else err_type)
    return ", ".join(parts) if parts else "validation_error"


app: FastAPI = create_app()
