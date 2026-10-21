"""Authenticated Checkout endpoints. Stub until BILLING_PROVIDER=stripe."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import get_current_org, get_db, require_org_role
from app.schemas.billing import (
    BillingCheckoutCreate,
    BillingCheckoutResponse,
    BillingCompleteRequest,
    BillingCompleteResponse,
    BillingConfigResponse,
    BillingPortalResponse,
)
from app.services.auth_service import OrgContext, ROLE_INHABER
from app.services.billing_service import (
    STUB_PROVIDER,
    BillingError,
    BillingNotFoundError,
    BillingSignatureError,
    CheckoutStart,
    billing_provider_name,
    complete_checkout_session,
    create_billing_portal,
    create_checkout_session,
    handle_stripe_webhook,
)

router: APIRouter = APIRouter()


@router.get("/billing/config", response_model=BillingConfigResponse)
def get_billing_config() -> BillingConfigResponse:
    """Tell the Tarife page whether checkout charges through Stripe."""
    return BillingConfigResponse(provider=billing_provider_name())


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
        started: CheckoutStart = create_checkout_session(
            db,
            organization_id=context.organization_id,
            requested_by_user_id=context.user_id,
            requested_plan=body.requested_plan,
        )
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return BillingCheckoutResponse(
        checkout_url=started.checkout_url,
        session_id=started.session_id,
        provider=started.provider,
    )


@router.post("/billing/portal", response_model=BillingPortalResponse)
def post_billing_portal(
    db: Session = Depends(get_db),
    context: OrgContext = Depends(get_current_org),
) -> BillingPortalResponse:
    require_org_role(context, {ROLE_INHABER})
    try:
        portal_url: str = create_billing_portal(db, organization_id=context.organization_id)
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return BillingPortalResponse(portal_url=portal_url)


@router.post("/billing/webhook")
async def post_billing_webhook(request: Request) -> Response:
    """Stripe fulfillment. The browser success page does not activate the plan."""
    payload: bytes = await request.body()
    signature: str = request.headers.get("stripe-signature", "")
    try:
        handle_stripe_webhook(payload, signature)
    except BillingSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except BillingError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_200_OK)


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
