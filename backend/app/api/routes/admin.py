from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, require_admin_token
from app.db.models import Organization, Plan
from app.schemas.auth import OrgResponse, PlanInfo, SetPlanByEmailRequest, SetPlanRequest
from app.services.auth_service import AuthError, set_plan, set_plan_for_email

router: APIRouter = APIRouter()


def _response(db: Session, organization: Organization, role: str = "inhaber") -> OrgResponse:
    plan: Plan | None = db.get(Plan, organization.plan_id)
    if plan is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Tarif fehlt.")
    return OrgResponse(
        organization_id=organization.id,
        name=organization.name,
        role=role,
        plan=PlanInfo(
            code=plan.code,
            name=plan.name,
            parse_per_day=plan.parse_per_day,
            export_per_day=plan.export_per_day,
            max_upload_size_mb=plan.max_upload_size_mb,
            allows_batch=plan.allows_batch,
            allows_history=plan.allows_history,
            quotas_enforced=False,
        ),
        created_at=organization.created_at,
    )


@router.post(
    "/admin/organizations/{organization_id}/plan",
    response_model=OrgResponse,
    dependencies=[Depends(require_admin_token)],
)
def admin_set_plan(
    organization_id: UUID,
    body: SetPlanRequest,
    db: Session = Depends(get_db),
) -> OrgResponse:
    try:
        organization: Organization = set_plan(
            db, organization_id=organization_id, plan_code=body.plan_code
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _response(db, organization)


@router.post(
    "/admin/plans",
    response_model=OrgResponse,
    dependencies=[Depends(require_admin_token)],
)
def admin_set_plan_by_email(
    body: SetPlanByEmailRequest,
    db: Session = Depends(get_db),
) -> OrgResponse:
    try:
        organization: Organization = set_plan_for_email(
            db, email=str(body.email), plan_code=body.plan_code
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _response(db, organization)
