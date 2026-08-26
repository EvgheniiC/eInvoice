"""Authenticated and administrative plan request endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_org, get_db, require_admin_token, require_org_role
from app.db.models import PlanUpgradeRequest
from app.schemas.plan_request import (
    PlanRequestCreate,
    PlanRequestListFilter,
    PlanRequestResponse,
    PlanRequestStatusUpdate,
)
from app.services.auth_service import OrgContext, ROLE_INHABER
from app.services.plan_request_service import (
    PlanRequestConflictError,
    PlanRequestError,
    PlanRequestNotFoundError,
    create_plan_request,
    list_plan_requests,
    update_plan_request_status,
)

router: APIRouter = APIRouter()


@router.post(
    "/plan-requests",
    response_model=PlanRequestResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_plan_request(
    body: PlanRequestCreate,
    db: Session = Depends(get_db),
    context: OrgContext = Depends(get_current_org),
) -> PlanRequestResponse:
    require_org_role(context, {ROLE_INHABER})
    try:
        request: PlanUpgradeRequest = create_plan_request(
            db,
            organization_id=context.organization_id,
            requested_by_user_id=context.user_id,
            requested_plan=body.requested_plan,
            message=body.message,
        )
    except PlanRequestError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _response(request)


@router.get(
    "/admin/plan-requests",
    response_model=list[PlanRequestResponse],
    dependencies=[Depends(require_admin_token)],
)
def get_plan_requests(
    request_status: PlanRequestListFilter = Query(default="pending", alias="status"),
    db: Session = Depends(get_db),
) -> list[PlanRequestResponse]:
    requests: list[PlanUpgradeRequest] = list_plan_requests(
        db,
        pending_only=request_status == "pending",
    )
    return [_response(request) for request in requests]


@router.patch(
    "/admin/plan-requests/{request_id}",
    response_model=PlanRequestResponse,
    dependencies=[Depends(require_admin_token)],
)
def patch_plan_request_status(
    request_id: UUID,
    body: PlanRequestStatusUpdate,
    db: Session = Depends(get_db),
) -> PlanRequestResponse:
    try:
        request: PlanUpgradeRequest = update_plan_request_status(
            db,
            request_id=request_id,
            new_status=body.status,
        )
    except PlanRequestNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except PlanRequestConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _response(request)


def _response(request: PlanUpgradeRequest) -> PlanRequestResponse:
    return PlanRequestResponse(
        id=request.id,
        organization_id=request.organization_id,
        requested_by_user_id=request.requested_by_user_id,
        requested_plan=request.requested_plan,
        status=request.status,
        message=request.message,
        created_at=request.created_at,
        updated_at=request.updated_at,
    )
