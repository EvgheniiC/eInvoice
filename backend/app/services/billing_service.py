"""Checkout sessions. Stub provider simulates a paid return; Stripe later."""

from __future__ import annotations

from datetime import timedelta
from typing import Final, Optional
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.core.clock import as_utc, utc_now
from app.core.config import settings
from app.core.passwords import hash_token, new_token
from app.db.models import BillingCheckoutSession, Organization, Plan, PlanUpgradeRequest
from app.schemas.plan_request import RequestedPlan
from app.services.auth_service import set_plan
from app.services.plan_request_service import PENDING_STATUS, PLAN_RANKS

STUB_PROVIDER: Final[str] = "stub"
PENDING_CHECKOUT: Final[str] = "pending"
COMPLETED_CHECKOUT: Final[str] = "completed"
EXPIRED_CHECKOUT: Final[str] = "expired"


class BillingError(ValueError):
    """User-facing billing rule violation."""


class BillingNotFoundError(BillingError):
    """Checkout session is missing or does not belong to this organization."""


def create_checkout_session(
    session: Session,
    *,
    organization_id: UUID,
    requested_by_user_id: UUID,
    requested_plan: RequestedPlan,
) -> tuple[BillingCheckoutSession, str]:
    """Create a pending Checkout session and return the raw return token."""
    if settings.billing_provider.strip().lower() != STUB_PROVIDER:
        raise BillingError("Zahlungsanbieter ist noch nicht eingerichtet.")
    _assert_upgrade_allowed(session, organization_id=organization_id, requested_plan=requested_plan)
    raw_token: str = f"stub_{new_token()}"
    now = utc_now()
    checkout: BillingCheckoutSession = BillingCheckoutSession(
        organization_id=organization_id,
        requested_by_user_id=requested_by_user_id,
        requested_plan=requested_plan,
        status=PENDING_CHECKOUT,
        token_hash=hash_token(raw_token),
        provider=STUB_PROVIDER,
        created_at=now,
        expires_at=now + timedelta(minutes=max(1, settings.billing_checkout_minutes)),
    )
    session.add(checkout)
    session.commit()
    session.refresh(checkout)
    return checkout, raw_token


def checkout_return_url(raw_token: str) -> str:
    """Frontend return URL, same shape Stripe will use later."""
    base: str = settings.public_app_url.rstrip("/")
    return f"{base}/tarife?checkout=success&session={raw_token}"


def complete_checkout_session(
    session: Session,
    *,
    organization_id: UUID,
    raw_token: str,
) -> tuple[str, str]:
    """Apply the paid plan after a Checkout return. Idempotent for the same session."""
    checkout: Optional[BillingCheckoutSession] = session.scalar(
        select(BillingCheckoutSession)
        .options(selectinload(BillingCheckoutSession.organization).selectinload(Organization.plan))
        .where(BillingCheckoutSession.token_hash == hash_token(raw_token))
    )
    if checkout is None or checkout.organization_id != organization_id:
        raise BillingNotFoundError("Zahlungsvorgang nicht gefunden.")
    if checkout.status == COMPLETED_CHECKOUT:
        plan: Plan = checkout.organization.plan
        return plan.code, plan.name
    if checkout.status != PENDING_CHECKOUT:
        raise BillingError("Zahlungsvorgang ist nicht mehr gültig.")
    if as_utc(checkout.expires_at) <= utc_now():
        checkout.status = EXPIRED_CHECKOUT
        session.commit()
        raise BillingError("Zahlungsvorgang ist abgelaufen. Bitte erneut starten.")

    _assert_upgrade_allowed(
        session,
        organization_id=organization_id,
        requested_plan=checkout.requested_plan,
    )
    checkout.status = COMPLETED_CHECKOUT
    checkout.completed_at = utc_now()
    _mark_matching_requests_approved(
        session,
        organization_id=organization_id,
        requested_plan=checkout.requested_plan,
    )
    organization: Organization = set_plan(
        session,
        organization_id=organization_id,
        plan_code=checkout.requested_plan,
        source="billing_stub",
    )
    session.refresh(organization)
    plan_row: Optional[Plan] = session.get(Plan, organization.plan_id)
    if plan_row is None:
        raise BillingError("Tarif konnte nicht geladen werden.")
    return plan_row.code, plan_row.name


def _assert_upgrade_allowed(
    session: Session,
    *,
    organization_id: UUID,
    requested_plan: RequestedPlan,
) -> None:
    organization: Optional[Organization] = session.get(Organization, organization_id)
    if organization is None:
        raise BillingError("Organisation nicht gefunden.")
    current_plan: Optional[Plan] = session.get(Plan, organization.plan_id)
    if current_plan is None:
        raise BillingError("Aktueller Tarif ist nicht eingerichtet.")
    current_rank: Optional[int] = PLAN_RANKS.get(current_plan.code)
    requested_rank: int = PLAN_RANKS[requested_plan]
    if current_rank is None or requested_rank <= current_rank:
        raise BillingError("Nur ein höherer Tarif kann gewählt werden.")


def _mark_matching_requests_approved(
    session: Session,
    *,
    organization_id: UUID,
    requested_plan: RequestedPlan,
) -> None:
    statement: Select[tuple[PlanUpgradeRequest]] = select(PlanUpgradeRequest).where(
        PlanUpgradeRequest.organization_id == organization_id,
        PlanUpgradeRequest.requested_plan == requested_plan,
        PlanUpgradeRequest.status == PENDING_STATUS,
    )
    now = utc_now()
    for request in session.scalars(statement).all():
        request.status = "approved"
        request.updated_at = now
