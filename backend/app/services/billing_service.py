"""Checkout sessions. Stub simulates a paid return; Stripe charges a subscription."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any, Final, Literal, Optional
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.core.clock import as_utc, utc_now
from app.core.config import settings
from app.core.error_events import log_event
from app.core.passwords import hash_token, new_token
from app.db.models import BillingCheckoutSession, Organization, Plan, PlanUpgradeRequest, User
from app.db.session import get_session_factory
from app.schemas.plan_request import RequestedPlan
from app.services.auth_service import set_plan
from app.services.plan_request_service import PENDING_STATUS, PLAN_RANKS

STUB_PROVIDER: Final[str] = "stub"
STRIPE_PROVIDER: Final[str] = "stripe"
PENDING_CHECKOUT: Final[str] = "pending"
COMPLETED_CHECKOUT: Final[str] = "completed"
EXPIRED_CHECKOUT: Final[str] = "expired"
BillingProviderName = Literal["stub", "stripe"]
_PAID_SUBSCRIPTION_STATUSES: Final[frozenset[str]] = frozenset({"active", "trialing"})
_ENDED_SUBSCRIPTION_STATUSES: Final[frozenset[str]] = frozenset(
    {"canceled", "unpaid", "incomplete_expired"}
)


class BillingError(ValueError):
    """User-facing billing rule violation."""


class BillingNotFoundError(BillingError):
    """Checkout session is missing or does not belong to this organization."""


class BillingSignatureError(BillingError):
    """Stripe webhook signature did not match."""


@dataclass(frozen=True)
class CheckoutStart:
    """One started checkout. session_id is a stub token or a Stripe id."""

    checkout: BillingCheckoutSession
    session_id: str
    checkout_url: str
    provider: BillingProviderName


def billing_provider_name() -> BillingProviderName:
    """Public provider label. Unknown values stay on the stub."""
    if settings.billing_provider.strip().lower() == STRIPE_PROVIDER:
        return STRIPE_PROVIDER
    return STUB_PROVIDER


def create_checkout_session(
    session: Session,
    *,
    organization_id: UUID,
    requested_by_user_id: UUID,
    requested_plan: RequestedPlan,
) -> CheckoutStart:
    """Start Checkout. Stripe charges; the stub returns to Tarife without a charge."""
    provider: BillingProviderName = billing_provider_name()
    if provider == STRIPE_PROVIDER:
        return _create_stripe_checkout(
            session,
            organization_id=organization_id,
            requested_by_user_id=requested_by_user_id,
            requested_plan=requested_plan,
        )
    return _create_stub_checkout(
        session,
        organization_id=organization_id,
        requested_by_user_id=requested_by_user_id,
        requested_plan=requested_plan,
    )


def checkout_return_url(raw_token: str) -> str:
    """Frontend return URL for the stub. Stripe uses its own success URL."""
    base: str = settings.public_app_url.rstrip("/")
    return f"{base}/tarife?checkout=success&session={raw_token}"


def create_billing_portal(session: Session, *, organization_id: UUID) -> str:
    """Open the Stripe Customer Portal for an organization that already pays."""
    if billing_provider_name() != STRIPE_PROVIDER:
        raise BillingError("Kundenportal ist nur mit Stripe verfügbar.")
    organization: Optional[Organization] = session.get(Organization, organization_id)
    if organization is None or not organization.stripe_customer_id:
        raise BillingError("Für diese Organisation gibt es noch kein Stripe-Kundenkonto.")
    stripe: Any = _stripe_module()
    portal: Any = stripe.billing_portal.Session.create(
        customer=organization.stripe_customer_id,
        return_url=f"{settings.public_app_url.rstrip('/')}/tarife",
    )
    url: str = str(portal["url"])
    if not url:
        raise BillingError("Kundenportal konnte nicht geöffnet werden.")
    return url


def complete_checkout_session(
    session: Session,
    *,
    organization_id: UUID,
    raw_token: str,
) -> tuple[str, str]:
    """Apply the paid plan after a stub Checkout return. Idempotent for the same session."""
    checkout: Optional[BillingCheckoutSession] = session.scalar(
        select(BillingCheckoutSession)
        .options(selectinload(BillingCheckoutSession.organization).selectinload(Organization.plan))
        .where(BillingCheckoutSession.token_hash == hash_token(raw_token))
    )
    if checkout is None or checkout.organization_id != organization_id:
        raise BillingNotFoundError("Zahlungsvorgang nicht gefunden.")
    if checkout.provider != STUB_PROVIDER:
        raise BillingError("Dieser Zahlungsvorgang wird von Stripe bestätigt.")
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


def handle_stripe_webhook(payload: bytes, signature: str) -> None:
    """Verify a Stripe event and apply the plan. Fulfillment does not use the success page."""
    secret: Optional[str] = settings.stripe_webhook_secret
    if billing_provider_name() != STRIPE_PROVIDER or not secret:
        raise BillingSignatureError("Zahlungsanbieter ist noch nicht eingerichtet.")
    stripe: Any = _stripe_module()
    try:
        event: Any = stripe.Webhook.construct_event(payload, signature, secret)
    except Exception as exc:
        raise BillingSignatureError("Signatur ungültig.") from exc
    factory = get_session_factory()
    if factory is None:
        raise BillingError("Datenbank ist nicht verfügbar.")
    db: Session = factory()
    try:
        _dispatch_stripe_event(db, event)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def _create_stub_checkout(
    session: Session,
    *,
    organization_id: UUID,
    requested_by_user_id: UUID,
    requested_plan: RequestedPlan,
) -> CheckoutStart:
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
    return CheckoutStart(
        checkout=checkout,
        session_id=raw_token,
        checkout_url=checkout_return_url(raw_token),
        provider=STUB_PROVIDER,
    )


def _create_stripe_checkout(
    session: Session,
    *,
    organization_id: UUID,
    requested_by_user_id: UUID,
    requested_plan: RequestedPlan,
) -> CheckoutStart:
    _assert_upgrade_allowed(session, organization_id=organization_id, requested_plan=requested_plan)
    price_id: str = _price_id_for_plan(requested_plan)
    organization: Optional[Organization] = session.get(Organization, organization_id)
    if organization is None:
        raise BillingError("Organisation nicht gefunden.")
    stripe: Any = _stripe_module()
    if organization.stripe_subscription_id:
        _change_stripe_price(
            stripe,
            subscription_id=organization.stripe_subscription_id,
            price_id=price_id,
            requested_plan=requested_plan,
        )
        _activate_paid_plan(
            session,
            organization=organization,
            plan_code=requested_plan,
            customer_id=organization.stripe_customer_id,
            subscription_id=organization.stripe_subscription_id,
            source="stripe_upgrade",
        )
        raw_token: str = f"stripe_upgrade_{new_token()}"
        checkout: BillingCheckoutSession = _store_checkout(
            session,
            organization_id=organization_id,
            requested_by_user_id=requested_by_user_id,
            requested_plan=requested_plan,
            provider=STRIPE_PROVIDER,
            provider_session_id=organization.stripe_subscription_id,
            raw_token=raw_token,
            status=COMPLETED_CHECKOUT,
        )
        return CheckoutStart(
            checkout=checkout,
            session_id=organization.stripe_subscription_id,
            checkout_url=f"{settings.public_app_url.rstrip('/')}/tarife?checkout=success",
            provider=STRIPE_PROVIDER,
        )

    user: Optional[User] = session.get(User, requested_by_user_id)
    params: dict[str, object] = {
        "mode": "subscription",
        "client_reference_id": str(organization_id),
        "line_items": [{"price": price_id, "quantity": 1}],
        "success_url": f"{settings.public_app_url.rstrip('/')}/tarife?checkout=success",
        "cancel_url": f"{settings.public_app_url.rstrip('/')}/tarife?checkout=cancel",
        "metadata": {
            "organization_id": str(organization_id),
            "requested_plan": requested_plan,
        },
        "subscription_data": {
            "metadata": {
                "organization_id": str(organization_id),
                "requested_plan": requested_plan,
            }
        },
    }
    if settings.stripe_automatic_tax:
        params["automatic_tax"] = {"enabled": True}
    if organization.stripe_customer_id:
        params["customer"] = organization.stripe_customer_id
    elif user is not None and user.email:
        params["customer_email"] = user.email
    created: Any = stripe.checkout.Session.create(**params)
    session_id: str = str(created["id"])
    checkout_url: str = str(created["url"])
    if not session_id or not checkout_url:
        raise BillingError("Zahlungsvorgang konnte nicht gestartet werden.")
    raw_token = f"stripe_{new_token()}"
    stored: BillingCheckoutSession = _store_checkout(
        session,
        organization_id=organization_id,
        requested_by_user_id=requested_by_user_id,
        requested_plan=requested_plan,
        provider=STRIPE_PROVIDER,
        provider_session_id=session_id,
        raw_token=raw_token,
        status=PENDING_CHECKOUT,
    )
    return CheckoutStart(
        checkout=stored,
        session_id=session_id,
        checkout_url=checkout_url,
        provider=STRIPE_PROVIDER,
    )


def _store_checkout(
    session: Session,
    *,
    organization_id: UUID,
    requested_by_user_id: UUID,
    requested_plan: RequestedPlan,
    provider: str,
    provider_session_id: Optional[str],
    raw_token: str,
    status: str,
) -> BillingCheckoutSession:
    now = utc_now()
    checkout: BillingCheckoutSession = BillingCheckoutSession(
        organization_id=organization_id,
        requested_by_user_id=requested_by_user_id,
        requested_plan=requested_plan,
        status=status,
        token_hash=hash_token(raw_token),
        provider=provider,
        provider_session_id=provider_session_id,
        created_at=now,
        expires_at=now + timedelta(minutes=max(1, settings.billing_checkout_minutes)),
        completed_at=now if status == COMPLETED_CHECKOUT else None,
    )
    session.add(checkout)
    session.commit()
    session.refresh(checkout)
    return checkout


def _dispatch_stripe_event(session: Session, event: Any) -> None:
    event_type: str = str(event["type"])
    data_object: Any = event["data"]["object"]
    if event_type in {"checkout.session.completed", "checkout.session.async_payment_succeeded"}:
        _apply_checkout_session(session, data_object)
        return
    if event_type == "customer.subscription.updated":
        _apply_subscription(session, data_object)
        return
    if event_type == "customer.subscription.deleted":
        _end_subscription(session, data_object)
        return
    if event_type in {
        "invoice.payment_failed",
        "charge.dispute.created",
        "charge.refunded",
        "radar.early_fraud_warning.created",
    }:
        _log_stripe_money_event(session, event_type=event_type, data_object=data_object)


def _apply_checkout_session(session: Session, checkout_session: Any) -> None:
    if str(checkout_session.get("mode") or "") != "subscription":
        return
    if str(checkout_session.get("payment_status") or "") not in {"paid", "no_payment_required"}:
        return
    reference: str = str(checkout_session.get("client_reference_id") or "")
    customer_id: Optional[str] = _stripe_id(checkout_session.get("customer"))
    organization: Optional[Organization] = _organization_by_reference(session, reference)
    if organization is None:
        organization = _organization_by_customer(session, customer_id)
    if organization is None:
        log_event(logging.WARNING, "stripe_checkout_org_missing")
        return
    subscription_id: Optional[str] = _stripe_id(checkout_session.get("subscription"))
    plan_code: Optional[str] = _plan_from_remote_subscription(subscription_id)
    if plan_code is None:
        plan_code = _plan_from_checkout(checkout_session)
    if plan_code not in {"plus", "team"} or subscription_id is None:
        log_event(logging.WARNING, "stripe_checkout_plan_missing")
        return
    paid_plan: RequestedPlan = "plus" if plan_code == "plus" else "team"
    provider_session_id: str = str(checkout_session.get("id") or "")
    if provider_session_id:
        pending: Optional[BillingCheckoutSession] = session.scalar(
            select(BillingCheckoutSession).where(
                BillingCheckoutSession.provider_session_id == provider_session_id
            )
        )
        if pending is not None and pending.status == PENDING_CHECKOUT:
            pending.status = COMPLETED_CHECKOUT
            pending.completed_at = utc_now()
    _mark_matching_requests_approved(
        session,
        organization_id=organization.id,
        requested_plan=paid_plan,
    )
    _activate_paid_plan(
        session,
        organization=organization,
        plan_code=paid_plan,
        customer_id=customer_id,
        subscription_id=subscription_id,
        source="stripe_webhook",
    )


def _apply_subscription(session: Session, subscription: Any) -> None:
    status: str = str(subscription.get("status") or "")
    organization: Optional[Organization] = _organization_for_subscription(session, subscription)
    if organization is None:
        log_event(logging.WARNING, "stripe_subscription_org_missing", fields={"status": status})
        return
    if status in _ENDED_SUBSCRIPTION_STATUSES:
        _end_subscription(session, subscription)
        return
    if status not in _PAID_SUBSCRIPTION_STATUSES:
        log_event(
            logging.INFO,
            "stripe_subscription_status",
            fields={"status": status, "organization_id": str(organization.id)},
        )
        return
    plan_code: Optional[str] = _plan_from_subscription(subscription)
    if plan_code is None:
        log_event(logging.WARNING, "stripe_subscription_price_unknown")
        return
    _activate_paid_plan(
        session,
        organization=organization,
        plan_code=plan_code,
        customer_id=_stripe_id(subscription.get("customer")),
        subscription_id=_stripe_id(subscription.get("id")),
        source="stripe_subscription",
    )


def _end_subscription(session: Session, subscription: Any) -> None:
    organization: Optional[Organization] = _organization_for_subscription(session, subscription)
    if organization is None:
        log_event(logging.WARNING, "stripe_subscription_end_org_missing")
        return
    organization.stripe_subscription_id = None
    if _stripe_id(subscription.get("customer")):
        organization.stripe_customer_id = _stripe_id(subscription.get("customer"))
    set_plan(
        session,
        organization_id=organization.id,
        plan_code="free",
        source="stripe_subscription_deleted",
    )


def _activate_paid_plan(
    session: Session,
    *,
    organization: Organization,
    plan_code: str,
    customer_id: Optional[str],
    subscription_id: Optional[str],
    source: str,
) -> None:
    if customer_id:
        organization.stripe_customer_id = customer_id
    if subscription_id:
        organization.stripe_subscription_id = subscription_id
    set_plan(
        session,
        organization_id=organization.id,
        plan_code=plan_code,
        source=source,
    )


def _log_stripe_money_event(session: Session, *, event_type: str, data_object: Any) -> None:
    """Record disputes, refunds, and fraud warnings without changing the plan automatically."""
    customer_id: Optional[str] = _stripe_id(data_object.get("customer"))
    organization: Optional[Organization] = _organization_by_customer(session, customer_id)
    log_event(
        logging.WARNING,
        "stripe_money_event",
        fields={
            "stripe_type": event_type,
            "organization_id": str(organization.id) if organization is not None else "",
        },
    )


def _organization_for_subscription(session: Session, subscription: Any) -> Optional[Organization]:
    subscription_id: Optional[str] = _stripe_id(subscription.get("id"))
    if subscription_id:
        found: Optional[Organization] = session.scalar(
            select(Organization).where(Organization.stripe_subscription_id == subscription_id)
        )
        if found is not None:
            return found
    customer_id: Optional[str] = _stripe_id(subscription.get("customer"))
    by_customer: Optional[Organization] = _organization_by_customer(session, customer_id)
    if by_customer is not None:
        return by_customer
    metadata: Any = subscription.get("metadata") or {}
    return _organization_by_reference(session, str(metadata.get("organization_id") or ""))


def _organization_by_reference(session: Session, reference: str) -> Optional[Organization]:
    if not reference:
        return None
    try:
        organization_id: UUID = UUID(reference)
    except ValueError:
        return None
    return session.get(Organization, organization_id)


def _organization_by_customer(session: Session, customer_id: Optional[str]) -> Optional[Organization]:
    if not customer_id:
        return None
    return session.scalar(select(Organization).where(Organization.stripe_customer_id == customer_id))


def _plan_from_remote_subscription(subscription_id: Optional[str]) -> Optional[str]:
    """Read the Price on the Subscription. Metadata is only a fallback."""
    if not subscription_id:
        return None
    try:
        remote: Any = _stripe_module().Subscription.retrieve(subscription_id)
    except Exception:
        log_event(logging.WARNING, "stripe_subscription_retrieve_failed")
        return None
    return _plan_from_subscription(remote)


def _plan_from_checkout(checkout_session: Any) -> Optional[str]:
    metadata: Any = checkout_session.get("metadata") or {}
    requested: str = str(metadata.get("requested_plan") or "")
    if requested in {"plus", "team"}:
        return requested
    return None


def _plan_from_subscription(subscription: Any) -> Optional[str]:
    items: Any = (subscription.get("items") or {}).get("data") or []
    if not items:
        metadata: Any = subscription.get("metadata") or {}
        requested: str = str(metadata.get("requested_plan") or "")
        return requested if requested in {"plus", "team"} else None
    price: Any = items[0].get("price")
    price_id: str = price if isinstance(price, str) else str((price or {}).get("id") or "")
    return _plan_code_for_price(price_id)


def _plan_code_for_price(price_id: str) -> Optional[str]:
    if price_id and price_id == (settings.stripe_price_plus or ""):
        return "plus"
    if price_id and price_id == (settings.stripe_price_team or ""):
        return "team"
    return None


def _price_id_for_plan(requested_plan: RequestedPlan) -> str:
    price_id: Optional[str] = (
        settings.stripe_price_plus if requested_plan == "plus" else settings.stripe_price_team
    )
    if not settings.stripe_secret_key or not price_id:
        raise BillingError("Zahlungsanbieter ist noch nicht eingerichtet.")
    return price_id


def _change_stripe_price(
    stripe: Any,
    *,
    subscription_id: str,
    price_id: str,
    requested_plan: RequestedPlan,
) -> None:
    current: Any = stripe.Subscription.retrieve(subscription_id)
    items: Any = (current["items"]["data"] if current.get("items") else []) or []
    if not items:
        raise BillingError("Das bestehende Abo hat keine Position.")
    stripe.Subscription.modify(
        subscription_id,
        items=[{"id": items[0]["id"], "price": price_id}],
        proration_behavior="create_prorations",
        metadata={"requested_plan": requested_plan},
    )


def _stripe_id(value: object) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned: str = value.strip()
        return cleaned or None
    if isinstance(value, dict):
        nested: object = value.get("id")
        return str(nested) if nested else None
    nested_id: object = getattr(value, "id", None)
    if nested_id:
        return str(nested_id)
    return None


def _stripe_module() -> Any:
    secret: Optional[str] = settings.stripe_secret_key
    if not secret:
        raise BillingError("Zahlungsanbieter ist noch nicht eingerichtet.")
    import stripe

    stripe.api_key = secret
    return stripe


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
    requested_plan: str,
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
