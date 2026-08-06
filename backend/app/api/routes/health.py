from fastapi import APIRouter
from pydantic import BaseModel

from app.core.config import settings

router: APIRouter = APIRouter()


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str
    app_name: str
    version: str


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Return basic service health information."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
    )
