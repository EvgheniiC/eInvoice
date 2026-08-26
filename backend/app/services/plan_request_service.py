"""Business rules for manual subscription upgrade requests."""

from __future__ import annotations

from typing import Final, Optional
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.clock import utc_now
from app.db.models import Organization, Plan, PlanUpgradeRequest
from app.schemas.plan_request import AdminPlanRequestStatus, RequestedPlan

PENDING_STATUS: Final[str] = "pending"
PLAN_RANKS: Final[dict[str, int]] = {"free": 0, "plus": 1, "team": 2}


class PlanRequestError(ValueError):
    """User-facing plan request rule violation."""


class PlanRequestConflictError(PlanRequestError):
    """Requested state transition conflicts with the current state."""


class PlanRequestNotFoundError(PlanRequestError):
    """Requested plan request does not exist."""


def create_plan_request(
    session: Session,
    *,
    organization_id: UUID,
    requested_by_user_id: UUID,
    requested_plan: RequestedPlan,
    message: Optional[str],
) -> PlanUpgradeRequest:
    """Create an upgrade request or return its pending equivalent."""
    organization: Optional[Organization] = session.get(Organization, organization_id)
    if organization is None:
        raise PlanRequestError("Organisation nicht gefunden.")
    current_plan: Optional[Plan] = session.get(Plan, organization.plan_id)
    if current_plan is None:
        raise PlanRequestError("Aktueller Tarif ist nicht eingerichtet.")
    current_rank: Optional[int] = PLAN_RANKS.get(current_plan.code)
    requested_rank: int = PLAN_RANKS[requested_plan]
    if current_rank is None or requested_rank <= current_rank:
        raise PlanRequestError("Nur ein höherer Tarif kann angefragt werden.")

    existing: Optional[PlanUpgradeRequest] = _pending_request(
        session,
        organization_id=organization_id,
        requested_plan=requested_plan,
    )
    if existing is not None:
        return existing

    request: PlanUpgradeRequest = PlanUpgradeRequest(
        organization_id=organization_id,
        requested_by_user_id=requested_by_user_id,
        requested_plan=requested_plan,
        status=PENDING_STATUS,
        message=message,
    )
    session.add(request)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        existing = _pending_request(
            session,
            organization_id=organization_id,
            requested_plan=requested_plan,
        )
        if existing is None:
            raise
        return existing
    session.refresh(request)
    return request


def list_plan_requests(
    session: Session,
    *,
    pending_only: bool,
) -> list[PlanUpgradeRequest]:
    """Return newest plan requests first."""
    statement: Select[tuple[PlanUpgradeRequest]] = select(PlanUpgradeRequest)
    if pending_only:
        statement = statement.where(PlanUpgradeRequest.status == PENDING_STATUS)
    statement = statement.order_by(PlanUpgradeRequest.created_at.desc())
    return list(session.scalars(statement).all())


def update_plan_request_status(
    session: Session,
    *,
    request_id: UUID,
    new_status: AdminPlanRequestStatus,
) -> PlanUpgradeRequest:
    """Finalize a pending request without changing the organization's plan."""
    request: Optional[PlanUpgradeRequest] = session.get(PlanUpgradeRequest, request_id)
    if request is None:
        raise PlanRequestNotFoundError("Tarifanfrage nicht gefunden.")
    if request.status != PENDING_STATUS:
        raise PlanRequestConflictError("Tarifanfrage wurde bereits bearbeitet.")
    request.status = new_status
    request.updated_at = utc_now()
    session.commit()
    session.refresh(request)
    return request


def _pending_request(
    session: Session,
    *,
    organization_id: UUID,
    requested_plan: RequestedPlan,
) -> Optional[PlanUpgradeRequest]:
    statement: Select[tuple[PlanUpgradeRequest]] = select(PlanUpgradeRequest).where(
        PlanUpgradeRequest.organization_id == organization_id,
        PlanUpgradeRequest.requested_plan == requested_plan,
        PlanUpgradeRequest.status == PENDING_STATUS,
    )
    return session.scalar(statement)
