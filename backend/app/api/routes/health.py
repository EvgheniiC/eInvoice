from typing import List, Optional

from fastapi import APIRouter, Response

from app.core.config import settings
from app.core.health import HealthCheckResult, HealthSnapshot, build_health_snapshot
from app.schemas.invoice import ApiModel

router: APIRouter = APIRouter()


class HealthCheck(ApiModel):
    """One named dependency check."""

    name: str
    status: str
    detail: Optional[str] = None


class LivenessResponse(ApiModel):
    """Liveness probe: process is running."""

    status: str


class ReadinessResponse(ApiModel):
    """Readiness probe: process can receive traffic."""

    status: str
    ready: bool
    checks: List[HealthCheck]


class HealthResponse(ApiModel):
    """Detailed health check response payload."""

    status: str
    ready: bool
    app_name: str
    version: str
    environment: str
    kosit_required: bool
    kosit_ready: bool
    checks: List[HealthCheck]


def _map_checks(results: List[HealthCheckResult]) -> List[HealthCheck]:
    mapped: List[HealthCheck] = []
    for item in results:
        mapped.append(HealthCheck(name=item.name, status=item.status, detail=item.detail))
    return mapped


@router.get("/health/live", response_model=LivenessResponse)
def liveness_check() -> LivenessResponse:
    """Return 200 as long as this process can answer HTTP."""
    return LivenessResponse(status="ok")


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ReadinessResponse}},
)
def readiness_check(response: Response) -> ReadinessResponse:
    """Return 503 when a required dependency (KoSIT in production) is missing."""
    snapshot: HealthSnapshot = build_health_snapshot()
    if not snapshot.ready:
        response.status_code = 503
    return ReadinessResponse(
        status="ok" if snapshot.ready else "not_ready",
        ready=snapshot.ready,
        checks=_map_checks(snapshot.checks),
    )


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return service health, including whether KoSIT validation is ready."""
    snapshot: HealthSnapshot = build_health_snapshot()
    return HealthResponse(
        status=snapshot.status,
        ready=snapshot.ready,
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
        kosit_required=snapshot.kosit_required,
        kosit_ready=snapshot.kosit_ready,
        checks=_map_checks(snapshot.checks),
    )
