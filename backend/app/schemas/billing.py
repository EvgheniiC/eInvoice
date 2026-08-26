"""API schemas for Checkout. Provider is stub until Stripe/Mollie is wired."""

from typing import Literal

from pydantic import Field

from app.schemas.invoice import ApiModel
from app.schemas.plan_request import RequestedPlan

BillingProvider = Literal["stub"]


class BillingCheckoutCreate(ApiModel):
    requested_plan: RequestedPlan


class BillingCheckoutResponse(ApiModel):
    checkout_url: str
    session_id: str
    provider: BillingProvider


class BillingCompleteRequest(ApiModel):
    session: str = Field(min_length=8, max_length=128)


class BillingCompleteResponse(ApiModel):
    accepted: bool
    provider: BillingProvider
    plan_code: str
    plan_name: str
    message: str
