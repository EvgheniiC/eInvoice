from fastapi import APIRouter

from app.core.config import settings
from app.schemas.invoice import ApiModel

router: APIRouter = APIRouter()


class HealthResponse(ApiModel):
    """Health check response payload."""

    status: str
    app_name: str
    version: str
    environment: str
    kosit_required: bool
    kosit_ready: bool


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return service health, including whether KoSIT validation is ready."""
    kosit_ready: bool = settings.kosit_ready
    degraded: bool = settings.require_kosit and not kosit_ready
    return HealthResponse(
        status="degraded" if degraded else "ok",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        kosit_required=settings.require_kosit,
        kosit_ready=kosit_ready,
    )
