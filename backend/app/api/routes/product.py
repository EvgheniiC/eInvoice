from typing import Optional

from fastapi import APIRouter, HTTPException, Request, status

from app.core.metrics import observe_funnel
from app.core.middleware import get_request_id
from app.schemas.product import (
    CapabilitiesResponse,
    FeedbackRequest,
    FeedbackResponse,
    FunnelEventRequest,
    FunnelEventResponse,
)
from app.services.capabilities import build_capabilities
from app.services.feedback import FeedbackRejected, submit_feedback

router: APIRouter = APIRouter()


@router.get("/capabilities", response_model=CapabilitiesResponse)
def get_capabilities() -> CapabilitiesResponse:
    """Public limits, formats, and guest processing model (no invoice data)."""
    return build_capabilities()


@router.post("/telemetry/funnel", response_model=FunnelEventResponse)
def record_funnel_event(body: FunnelEventRequest) -> FunnelEventResponse:
    """Count landing/upload without cookies or invoice payloads."""
    observe_funnel(body.step)
    return FunnelEventResponse(accepted=True)


@router.post("/feedback", response_model=FeedbackResponse)
def create_feedback(body: FeedbackRequest, request: Request) -> FeedbackResponse:
    """Accept text-only feedback. Invoice files are not accepted."""
    request_id: Optional[str] = get_request_id(request)
    try:
        ack: str = submit_feedback(
            message=body.message,
            contact_email=body.contact_email,
            request_id=request_id,
        )
    except FeedbackRejected as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return FeedbackResponse(accepted=True, message=ack)
