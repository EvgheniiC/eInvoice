from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_org, get_db
from app.db.models import Organization
from app.schemas.auth import OrgResponse, OrgUpdateRequest, PlanInfo
from app.services.auth_service import AuthError, OrgContext, update_organization
from app.services.quota_service import build_plan_info

router: APIRouter = APIRouter()


def _org_payload(db: Session, organization: Organization, context: OrgContext) -> OrgResponse:
    plan: PlanInfo = build_plan_info(db, context)
    return OrgResponse(
        organization_id=organization.id,
        name=organization.name,
        role=context.role,
        plan=plan,
        created_at=organization.created_at,
        history_enabled=organization.history_enabled,
        store_originals_enabled=organization.store_originals_enabled,
        tax_number=organization.tax_number,
        vat_id=organization.vat_id,
        iban=organization.iban,
        accountant_email=organization.accountant_email,
    )


@router.get("/org", response_model=OrgResponse)
def get_organization(
    db: Session = Depends(get_db),
    context: OrgContext = Depends(get_current_org),
) -> OrgResponse:
    organization: Organization | None = db.get(Organization, context.organization_id)
    if organization is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation nicht gefunden.")
    return _org_payload(db, organization, context)


@router.patch("/org", response_model=OrgResponse)
def patch_organization(
    body: OrgUpdateRequest,
    db: Session = Depends(get_db),
    context: OrgContext = Depends(get_current_org),
) -> OrgResponse:
    try:
        fields_set: set[str] = set(body.model_fields_set)
        organization: Organization = update_organization(
            db,
            organization_id=context.organization_id,
            role=context.role,
            allows_history=context.allows_history,
            name=body.name,
            history_enabled=body.history_enabled,
            store_originals_enabled=body.store_originals_enabled,
            tax_number=body.tax_number,
            vat_id=body.vat_id,
            iban=body.iban,
            accountant_email=body.accountant_email,
            update_tax_number="tax_number" in fields_set,
            update_vat_id="vat_id" in fields_set,
            update_iban="iban" in fields_set,
            update_accountant_email="accountant_email" in fields_set,
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
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
        max_parallel=context.max_parallel,
        allows_batch=context.allows_batch,
        allows_history=context.allows_history,
    )
    return _org_payload(db, organization, refreshed)
