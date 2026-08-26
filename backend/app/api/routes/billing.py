"""Authenticated Checkout endpoints. Stub provider until Stripe/Mollie exists."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_org, get_db, require_org_role
from app.schemas.billing import (
    BillingCheckoutCreate,
    BillingCheckoutResponse,
    BillingCompleteRequest,
    BillingCompleteResponse,
)
from app.services.auth_service import OrgContext, ROLE_INHABER
from app.services.billing_service import (
    STUB_PROVIDER,
    BillingError,
    BillingNotFoundError,
    checkout_return_url,
    complete_checkout_session,
    create_checkout_session,
)

router: APIRouter = APIRouter()


@router.post(
    "/billing/checkout",
    response_model=BillingCheckoutResponse,
    status_code=status.HTTP_201_CREATED,
)
def post_billing_checkout(
    body: BillingCheckoutCreate,
    db: Session = Depends(get_db),
    context: OrgContext = Depends(get_current_org),
) -> BillingCheckoutResponse:
    require_org_role(context, {ROLE_INHABER})
    try:
        _checkout, raw_token = create_checkout_session(
            db,
            organization_id=context.organization_id,
            requested_by_user_id=context.user_id,
            requested_plan=body.requested_plan,
        )
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return BillingCheckoutResponse(
        checkout_url=checkout_return_url(raw_token),
        session_id=raw_token,
        provider=STUB_PROVIDER,
    )


@router.post("/billing/complete", response_model=BillingCompleteResponse)
def post_billing_complete(
    body: BillingCompleteRequest,
    db: Session = Depends(get_db),
    context: OrgContext = Depends(get_current_org),
) -> BillingCompleteResponse:
    require_org_role(context, {ROLE_INHABER})
    try:
        plan_code, plan_name = complete_checkout_session(
            db,
            organization_id=context.organization_id,
            raw_token=body.session,
        )
    except BillingNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return BillingCompleteResponse(
        accepted=True,
        provider=STUB_PROVIDER,
        plan_code=plan_code,
        plan_name=plan_name,
        message=f"Zahlung bestätigt. Ihr Tarif ist jetzt {plan_name}.",
    )
