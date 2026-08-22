"""Account registration, sessions, and org context. Does not persist invoices."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.core.clock import as_utc, utc_now
from app.core.config import settings
from app.core.error_events import log_event
from app.core.passwords import hash_password, hash_token, new_token, normalize_email, verify_password
from app.db.models import AuthSession, EmailToken, Membership, Organization, Plan, UsageCounter, User
from app.schemas.auth import validated_accountant_email, validated_iban, validated_vat_id
from app.schemas.export import OrgProfile
from app.services.email_service import send_auth_email
from app.services.plan_limits import PlanLimits, merge_plan_row

ROLE_INHABER: str = "inhaber"
ROLE_BUERO: str = "buero"
ROLE_EXPORT: str = "export_only"
PURPOSE_VERIFY: str = "verify_email"
PURPOSE_MAGIC: str = "magic_link"
PURPOSE_RESET: str = "reset_password"
DEFAULT_ORGANIZATION_NAME: str = "Meine Organisation"


class AuthError(ValueError):
    """User-facing German auth error."""


@dataclass(frozen=True)
class OrgContext:
    """Authenticated request context. No invoice payload."""

    user_id: UUID
    email: str
    email_verified: bool
    organization_id: UUID
    organization_name: str
    role: str
    plan_code: str
    plan_name: str
    parse_per_day: Optional[int]
    export_per_day: Optional[int]
    max_upload_size_mb: int
    max_parallel: int
    allows_batch: bool
    allows_history: bool


def organization_profile(organization: Organization) -> OrgProfile:
    """Export-facing firm fields. Empty optional values stay None."""
    return OrgProfile(
        name=organization.name,
        tax_number=organization.tax_number,
        vat_id=organization.vat_id,
        iban=organization.iban,
        accountant_email=organization.accountant_email,
    )


def load_organization_profile(session: Session, organization_id: UUID) -> Optional[OrgProfile]:
    organization: Optional[Organization] = session.get(Organization, organization_id)
    if organization is None:
        return None
    return organization_profile(organization)


def resolved_organization_name(name: Optional[str]) -> str:
    """Use a typed name when provided; otherwise a German default for later editing."""
    stripped: str = (name or "").strip()
    if len(stripped) >= 2:
        return stripped[:120]
    return DEFAULT_ORGANIZATION_NAME


def register_user(
    session: Session,
    *,
    email: str,
    password: str,
    organization_name: Optional[str] = None,
) -> tuple[User, Optional[str]]:
    """Create user + organization + Inhaber membership. Returns (user, verify token)."""
    normalized: str = normalize_email(email)
    existing: Optional[User] = session.scalar(select(User).where(User.email == normalized))
    if existing is not None:
        log_event(logging.INFO, "register_email_exists", fields={"domain": _email_domain(normalized)})
        if existing.email_verified_at is None:
            token: str = _issue_email_token(session, user_id=existing.id, purpose=PURPOSE_VERIFY)
            session.commit()
            send_auth_email(to_email=normalized, purpose=PURPOSE_VERIFY, token=token)
            return existing, token if not settings.is_production else None
        return existing, None

    free: Plan = _require_plan(session, "free")
    user: User = User(
        email=normalized,
        password_hash=hash_password(password),
        email_verified_at=None,
    )
    organization: Organization = Organization(
        name=resolved_organization_name(organization_name),
        plan_id=free.id,
    )
    session.add(user)
    session.add(organization)
    session.flush()
    session.add(
        Membership(
            user_id=user.id,
            organization_id=organization.id,
            role=ROLE_INHABER,
        )
    )
    token: str = _issue_email_token(session, user_id=user.id, purpose=PURPOSE_VERIFY)
    session.commit()
    send_auth_email(to_email=normalized, purpose=PURPOSE_VERIFY, token=token)
    log_event(logging.INFO, "user_registered", fields={"user_id": str(user.id)})
    return user, token if not settings.is_production else None


def authenticate_password(session: Session, *, email: str, password: str) -> OrgContext:
    normalized: str = normalize_email(email)
    user: Optional[User] = session.scalar(select(User).where(User.email == normalized))
    if user is None or not user.password_hash or not verify_password(password, user.password_hash):
        raise AuthError("E-Mail oder Passwort ungültig.")
    if user.email_verified_at is None:
        raise AuthError("Bitte bestätigen Sie zuerst Ihre E-Mail-Adresse.")
    return _context_for_user(session, user)


def request_magic_link(session: Session, *, email: str) -> Optional[str]:
    normalized: str = normalize_email(email)
    user: Optional[User] = session.scalar(select(User).where(User.email == normalized))
    if user is None or user.email_verified_at is None:
        log_event(logging.INFO, "magic_link_ignored", fields={"domain": _email_domain(normalized)})
        return None
    token: str = _issue_email_token(session, user_id=user.id, purpose=PURPOSE_MAGIC)
    session.commit()
    send_auth_email(to_email=normalized, purpose=PURPOSE_MAGIC, token=token)
    return token if not settings.is_production else None


def request_password_reset(session: Session, *, email: str) -> Optional[str]:
    """Send a one-time reset link. Unknown or unverified addresses are ignored."""
    normalized: str = normalize_email(email)
    user: Optional[User] = session.scalar(select(User).where(User.email == normalized))
    if user is None or user.email_verified_at is None:
        log_event(logging.INFO, "password_reset_ignored", fields={"domain": _email_domain(normalized)})
        return None
    now: datetime = utc_now()
    for item in session.scalars(
        select(EmailToken).where(
            EmailToken.user_id == user.id,
            EmailToken.purpose == PURPOSE_RESET,
            EmailToken.consumed_at.is_(None),
        )
    ).all():
        item.consumed_at = now
    token: str = _issue_email_token(session, user_id=user.id, purpose=PURPOSE_RESET)
    session.commit()
    send_auth_email(to_email=normalized, purpose=PURPOSE_RESET, token=token)
    return token if not settings.is_production else None


def consume_email_token(session: Session, *, token: str, purpose: str) -> OrgContext:
    token_hash: str = hash_token(token)
    now: datetime = utc_now()
    row: Optional[EmailToken] = session.scalar(
        select(EmailToken).where(
            EmailToken.token_hash == token_hash,
            EmailToken.purpose == purpose,
        )
    )
    if row is None or row.consumed_at is not None or as_utc(row.expires_at) <= now:
        raise AuthError("Der Link ist ungültig oder abgelaufen.")
    user: Optional[User] = session.get(User, row.user_id)
    if user is None:
        raise AuthError("Der Link ist ungültig oder abgelaufen.")
    row.consumed_at = now
    if purpose == PURPOSE_VERIFY and user.email_verified_at is None:
        user.email_verified_at = now
    session.commit()
    if purpose == PURPOSE_MAGIC and user.email_verified_at is None:
        raise AuthError("Bitte bestätigen Sie zuerst Ihre E-Mail-Adresse.")
    return _context_for_user(session, user)


def create_session(session: Session, context: OrgContext) -> str:
    raw: str = new_token()
    now: datetime = utc_now()
    row: AuthSession = AuthSession(
        token_hash=hash_token(raw),
        user_id=context.user_id,
        organization_id=context.organization_id,
        expires_at=now + timedelta(days=settings.auth_session_days),
    )
    session.add(row)
    session.commit()
    return raw


def resolve_session(session: Session, raw_token: Optional[str]) -> Optional[OrgContext]:
    if not raw_token:
        return None
    now: datetime = utc_now()
    row: Optional[AuthSession] = session.scalar(
        select(AuthSession).where(AuthSession.token_hash == hash_token(raw_token))
    )
    if row is None or row.revoked_at is not None or as_utc(row.expires_at) <= now:
        return None
    user: Optional[User] = session.get(User, row.user_id)
    if user is None:
        return None
    context: OrgContext = _context_for_user(session, user, organization_id=row.organization_id)
    return context


def revoke_session(session: Session, raw_token: Optional[str]) -> None:
    if not raw_token:
        return
    row: Optional[AuthSession] = session.scalar(
        select(AuthSession).where(AuthSession.token_hash == hash_token(raw_token))
    )
    if row is None or row.revoked_at is not None:
        return
    row.revoked_at = utc_now()
    session.commit()


def change_password(
    session: Session,
    *,
    user_id: UUID,
    current_password: str,
    new_password: str,
) -> None:
    user: Optional[User] = session.get(User, user_id)
    if user is None or not user.password_hash or not verify_password(current_password, user.password_hash):
        raise AuthError("Das aktuelle Passwort ist ungültig.")
    _replace_password(session, user=user, new_password=new_password)


def reset_password(session: Session, *, token: str, new_password: str) -> None:
    """Consume a reset token and set a new password. All sessions are revoked."""
    token_hash: str = hash_token(token)
    now: datetime = utc_now()
    row: Optional[EmailToken] = session.scalar(
        select(EmailToken).where(
            EmailToken.token_hash == token_hash,
            EmailToken.purpose == PURPOSE_RESET,
        )
    )
    if row is None or row.consumed_at is not None or as_utc(row.expires_at) <= now:
        raise AuthError("Der Link ist ungültig oder abgelaufen.")
    user: Optional[User] = session.get(User, row.user_id)
    if user is None or user.email_verified_at is None:
        raise AuthError("Der Link ist ungültig oder abgelaufen.")
    row.consumed_at = now
    _replace_password(session, user=user, new_password=new_password)


def rename_organization(
    session: Session,
    *,
    organization_id: UUID,
    role: str,
    name: str,
) -> Organization:
    return update_organization(
        session,
        organization_id=organization_id,
        role=role,
        allows_history=False,
        name=name,
    )


def update_organization(
    session: Session,
    *,
    organization_id: UUID,
    role: str,
    allows_history: bool,
    name: Optional[str] = None,
    history_enabled: Optional[bool] = None,
    store_originals_enabled: Optional[bool] = None,
    tax_number: Optional[str] = None,
    vat_id: Optional[str] = None,
    iban: Optional[str] = None,
    accountant_email: Optional[str] = None,
    update_tax_number: bool = False,
    update_vat_id: bool = False,
    update_iban: bool = False,
    update_accountant_email: bool = False,
) -> Organization:
    if role != ROLE_INHABER:
        raise AuthError("Nur der Inhaber kann die Organisation ändern.")
    profile_touch: bool = (
        update_tax_number or update_vat_id or update_iban or update_accountant_email
    )
    if (
        name is None
        and history_enabled is None
        and store_originals_enabled is None
        and not profile_touch
    ):
        raise AuthError("Keine Änderung übermittelt.")
    organization: Optional[Organization] = session.get(Organization, organization_id)
    if organization is None:
        raise AuthError("Organisation nicht gefunden.")
    if name is not None:
        organization.name = name.strip()
    want_history: bool = organization.history_enabled if history_enabled is None else history_enabled
    want_originals: bool = (
        organization.store_originals_enabled
        if store_originals_enabled is None
        else store_originals_enabled
    )
    if want_originals and not want_history:
        raise AuthError("Dateien merken erfordert den Verlauf.")
    turning_on_history: bool = history_enabled is True and not organization.history_enabled
    turning_on_originals: bool = (
        store_originals_enabled is True and not organization.store_originals_enabled
    )
    if (turning_on_history or turning_on_originals) and not allows_history:
        raise AuthError(
            "Verlauf ist in Plus enthalten. Mit Plus speichern Sie Metadaten geprüfter Rechnungen."
        )
    originals_were_on: bool = organization.store_originals_enabled
    if history_enabled is not None:
        if history_enabled and not organization.history_enabled:
            organization.history_enabled_at = utc_now()
        organization.history_enabled = history_enabled
    organization.store_originals_enabled = want_originals
    if originals_were_on and not want_originals:
        from app.services.history_service import purge_originals_for_organization

        purge_originals_for_organization(session, organization.id)
    if update_tax_number:
        organization.tax_number = tax_number
    if update_vat_id:
        organization.vat_id = validated_vat_id(vat_id)
    if update_iban:
        organization.iban = validated_iban(iban)
    if update_accountant_email:
        organization.accountant_email = validated_accountant_email(accountant_email)
    session.commit()
    return organization


def set_plan_for_email(session: Session, *, email: str, plan_code: str) -> Organization:
    normalized: str = normalize_email(email)
    user: Optional[User] = session.scalar(select(User).where(User.email == normalized))
    if user is None:
        raise AuthError("Kein Konto mit dieser E-Mail.")
    membership: Optional[Membership] = session.scalar(
        select(Membership)
        .where(Membership.user_id == user.id, Membership.role == ROLE_INHABER)
        .order_by(Membership.created_at.asc())
    )
    if membership is None:
        raise AuthError("Kein Inhaber-Mandat für dieses Konto.")
    return set_plan(session, organization_id=membership.organization_id, plan_code=plan_code)


def set_plan(session: Session, *, organization_id: UUID, plan_code: str) -> Organization:
    plan: Plan = _require_plan(session, plan_code)
    organization: Optional[Organization] = session.get(Organization, organization_id)
    if organization is None:
        raise AuthError("Organisation nicht gefunden.")
    organization.plan_id = plan.id
    session.commit()
    log_event(
        logging.INFO,
        "plan_set_manual",
        fields={"organization_id": str(organization_id), "plan": plan_code},
    )
    return organization


def delete_user_by_email(session: Session, *, email: str) -> str:
    """Remove the user, tokens, sessions, and orgs that would be left empty."""
    normalized: str = normalize_email(email)
    user: Optional[User] = session.scalar(select(User).where(User.email == normalized))
    if user is None:
        raise AuthError("Kein Konto mit dieser E-Mail.")
    memberships: list[Membership] = list(
        session.scalars(select(Membership).where(Membership.user_id == user.id)).all()
    )
    organization_ids: list[UUID] = [item.organization_id for item in memberships]
    session.execute(delete(EmailToken).where(EmailToken.user_id == user.id))
    session.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
    session.execute(delete(Membership).where(Membership.user_id == user.id))
    for organization_id in organization_ids:
        leftover: Optional[Membership] = session.scalar(
            select(Membership).where(Membership.organization_id == organization_id)
        )
        if leftover is not None:
            continue
        session.execute(delete(AuthSession).where(AuthSession.organization_id == organization_id))
        session.execute(
            delete(UsageCounter).where(
                UsageCounter.subject_type == "org",
                UsageCounter.subject_key == str(organization_id),
            )
        )
        organization: Optional[Organization] = session.get(Organization, organization_id)
        if organization is not None:
            from app.services.history_service import purge_history_for_organization

            purge_history_for_organization(session, organization_id)
            session.delete(organization)
    session.delete(user)
    session.commit()
    log_event(logging.INFO, "user_deleted", fields={"domain": _email_domain(normalized)})
    return normalized


def resend_verification(session: Session, *, email: str) -> Optional[str]:
    normalized: str = normalize_email(email)
    user: Optional[User] = session.scalar(select(User).where(User.email == normalized))
    if user is None or user.email_verified_at is not None:
        return None
    token: str = _issue_email_token(session, user_id=user.id, purpose=PURPOSE_VERIFY)
    session.commit()
    send_auth_email(to_email=normalized, purpose=PURPOSE_VERIFY, token=token)
    return token if not settings.is_production else None


def _context_for_user(
    session: Session,
    user: User,
    *,
    organization_id: Optional[UUID] = None,
) -> OrgContext:
    stmt = (
        select(Membership)
        .where(Membership.user_id == user.id)
        .options(selectinload(Membership.organization).selectinload(Organization.plan))
        .order_by(Membership.created_at.asc())
    )
    memberships: list[Membership] = list(session.scalars(stmt).all())
    if not memberships:
        raise AuthError("Kein Organisationskontext.")
    chosen: Membership = memberships[0]
    if organization_id is not None:
        for item in memberships:
            if item.organization_id == organization_id:
                chosen = item
                break
    organization: Organization = chosen.organization
    plan: Plan = organization.plan
    limits: PlanLimits = merge_plan_row(
        code=plan.code,
        name=plan.name,
        parse_per_day=plan.parse_per_day,
        export_per_day=plan.export_per_day,
        max_upload_size_mb=plan.max_upload_size_mb,
        max_parallel=plan.max_parallel,
        allows_batch=plan.allows_batch,
        allows_history=plan.allows_history,
    )
    return OrgContext(
        user_id=user.id,
        email=user.email,
        email_verified=user.email_verified_at is not None,
        organization_id=organization.id,
        organization_name=organization.name,
        role=chosen.role,
        plan_code=limits.code,
        plan_name=limits.name,
        parse_per_day=limits.parse_per_day,
        export_per_day=limits.export_per_day,
        max_upload_size_mb=limits.max_upload_size_mb,
        max_parallel=limits.max_parallel,
        allows_batch=limits.allows_batch,
        allows_history=limits.allows_history,
    )


def _require_plan(session: Session, code: str) -> Plan:
    plan: Optional[Plan] = session.scalar(select(Plan).where(Plan.code == code))
    if plan is None:
        raise AuthError("Tarif ist nicht eingerichtet.")
    return plan


def _replace_password(session: Session, *, user: User, new_password: str) -> None:
    user.password_hash = hash_password(new_password)
    user.password_changed_at = utc_now()
    now: datetime = utc_now()
    for item in session.scalars(select(AuthSession).where(AuthSession.user_id == user.id)).all():
        if item.revoked_at is None:
            item.revoked_at = now
    session.commit()


def _issue_email_token(session: Session, *, user_id: UUID, purpose: str) -> str:
    raw: str = new_token()
    session.add(
        EmailToken(
            user_id=user_id,
            purpose=purpose,
            token_hash=hash_token(raw),
            expires_at=utc_now() + timedelta(hours=settings.auth_token_hours),
        )
    )
    return raw


def _email_domain(email: str) -> str:
    if "@" not in email:
        return "unknown"
    return email.rsplit("@", 1)[-1]
