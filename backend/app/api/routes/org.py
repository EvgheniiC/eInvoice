from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_org, get_db
from app.db.models import Organization
from app.schemas.auth import OrgResponse, OrgUpdateRequest, PlanInfo
from app.services.auth_service import AuthError, OrgContext, rename_organization

router: APIRouter = APIRouter()


def _org_payload(organization: Organization, context: OrgContext) -> OrgResponse:
    return OrgResponse(
        organization_id=organization.id,
        name=organization.name,
        role=context.role,
        plan=PlanInfo(
            code=context.plan_code,
            name=context.plan_name,
            parse_per_day=context.parse_per_day,
            export_per_day=context.export_per_day,
            max_upload_size_mb=context.max_upload_size_mb,
            allows_batch=context.allows_batch,
            allows_history=context.allows_history,
            quotas_enforced=False,
        ),
        created_at=organization.created_at,
    )


@router.get("/org", response_model=OrgResponse)
def get_organization(
    db: Session = Depends(get_db),
    context: OrgContext = Depends(get_current_org),
) -> OrgResponse:
    organization: Organization | None = db.get(Organization, context.organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation nicht gefunden.")
    return _org_payload(organization, context)


@router.patch("/org", response_model=OrgResponse)
def patch_organization(
    body: OrgUpdateRequest,
    db: Session = Depends(get_db),
    context: OrgContext = Depends(get_current_org),
) -> OrgResponse:
    try:
        organization: Organization = rename_organization(
            db,
            organization_id=context.organization_id,
            role=context.role,
            name=body.name,
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    refreshed: OrgContext = OrgContext(
        user_id=context.user_id,
        email=context.email,
        email_verified=context.email_verified,
        organization_id=organization.id,
        organization_name=organization.name,
        role=context.role,
        plan_code=context.plan_code,
        plan_name=context.plan_name,
        parse_per_day=context.parse_per_day,
        export_per_day=context.export_per_day,
        max_upload_size_mb=context.max_upload_size_mb,
        allows_batch=context.allows_batch,
        allows_history=context.allows_history,
    )
    return _org_payload(organization, refreshed)
