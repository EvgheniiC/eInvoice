from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_org, get_db, read_session_cookie
from app.core.config import settings
from app.db.models import Membership, Organization
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    MagicLinkRequest,
    MeResponse,
    MembershipInfo,
    MessageResponse,
    PlanInfo,
    RegisterRequest,
    RegisterResponse,
    TokenRequest,
)
from app.services.auth_service import (
    PURPOSE_MAGIC,
    PURPOSE_VERIFY,
    AuthError,
    OrgContext,
    authenticate_password,
    change_password,
    consume_email_token,
    create_session,
    register_user,
    request_magic_link,
    resend_verification,
    revoke_session,
)
from sqlalchemy import select

router: APIRouter = APIRouter()


def _cookie_kwargs() -> dict[str, object]:
    return {
        "key": settings.auth_cookie_name,
        "httponly": True,
        "samesite": "lax",
        "secure": settings.is_production,
        "path": "/",
        "max_age": settings.auth_session_days * 24 * 60 * 60,
    }


def _set_session_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(value=raw_token, **_cookie_kwargs())


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(settings.auth_cookie_name, path="/")


def _plan_info(context: OrgContext) -> PlanInfo:
    return PlanInfo(
        code=context.plan_code,
        name=context.plan_name,
        parse_per_day=context.parse_per_day,
        export_per_day=context.export_per_day,
        max_upload_size_mb=context.max_upload_size_mb,
        allows_batch=context.allows_batch,
        allows_history=context.allows_history,
        quotas_enforced=False,
    )


def _me_payload(db: Session, context: OrgContext) -> MeResponse:
    memberships: list[Membership] = list(
        db.scalars(select(Membership).where(Membership.user_id == context.user_id)).all()
    )
    items: list[MembershipInfo] = []
    for membership in memberships:
        organization: Optional[Organization] = db.get(Organization, membership.organization_id)
        if organization is None:
            continue
        items.append(
            MembershipInfo(
                organization_id=organization.id,
                organization_name=organization.name,
                role=membership.role,
            )
        )
    return MeResponse(
        user_id=context.user_id,
        email=context.email,
        email_verified=context.email_verified,
        organization_id=context.organization_id,
        organization_name=context.organization_name,
        role=context.role,
        plan=_plan_info(context),
        memberships=items,
    )


@router.post("/auth/register", response_model=RegisterResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> RegisterResponse:
    _user, token = register_user(
        db,
        email=str(body.email),
        password=body.password,
        organization_name=body.organization_name,
    )
    return RegisterResponse(
        accepted=True,
        message="Bitte prüfen Sie Ihre E-Mail und bestätigen Sie das Konto.",
        verification_token=token,
    )


@router.post("/auth/login", response_model=MeResponse)
def login(
    body: LoginRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> MeResponse:
    try:
        context: OrgContext = authenticate_password(db, email=str(body.email), password=body.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc
    raw: str = create_session(db, context)
    _set_session_cookie(response, raw)
    return _me_payload(db, context)


@router.post("/auth/logout", response_model=MessageResponse)
def logout(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
) -> MessageResponse:
    revoke_session(db, read_session_cookie(request))
    _clear_session_cookie(response)
    return MessageResponse(accepted=True, message="Sie sind abgemeldet.")


@router.post("/auth/verify-email", response_model=MeResponse)
def verify_email(
    body: TokenRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> MeResponse:
    try:
        context: OrgContext = consume_email_token(db, token=body.token, purpose=PURPOSE_VERIFY)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    raw: str = create_session(db, context)
    _set_session_cookie(response, raw)
    return _me_payload(db, context)


@router.post("/auth/resend-verification", response_model=MessageResponse)
def resend(body: MagicLinkRequest, db: Session = Depends(get_db)) -> MessageResponse:
    token: Optional[str] = resend_verification(db, email=str(body.email))
    return MessageResponse(
        accepted=True,
        message="Wenn ein unbestätigtes Konto existiert, wurde eine E-Mail gesendet.",
        token=token,
    )


@router.post("/auth/magic-link", response_model=MessageResponse)
def magic_link(body: MagicLinkRequest, db: Session = Depends(get_db)) -> MessageResponse:
    token: Optional[str] = request_magic_link(db, email=str(body.email))
    return MessageResponse(
        accepted=True,
        message="Wenn ein bestätigtes Konto existiert, wurde ein Anmeldelink gesendet.",
        token=token,
    )


@router.post("/auth/magic-link/consume", response_model=MeResponse)
def consume_magic(
    body: TokenRequest,
    response: Response,
    db: Session = Depends(get_db),
) -> MeResponse:
    try:
        context: OrgContext = consume_email_token(db, token=body.token, purpose=PURPOSE_MAGIC)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    raw: str = create_session(db, context)
    _set_session_cookie(response, raw)
    return _me_payload(db, context)


@router.post("/auth/change-password", response_model=MessageResponse)
def update_password(
    body: ChangePasswordRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    context: OrgContext = Depends(get_current_org),
) -> MessageResponse:
    try:
        change_password(
            db,
            user_id=context.user_id,
            current_password=body.current_password,
            new_password=body.new_password,
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    revoke_session(db, read_session_cookie(request))
    _clear_session_cookie(response)
    return MessageResponse(accepted=True, message="Passwort geändert. Bitte erneut anmelden.")


@router.get("/me", response_model=MeResponse)
def me(db: Session = Depends(get_db), context: OrgContext = Depends(get_current_org)) -> MeResponse:
    return _me_payload(db, context)
