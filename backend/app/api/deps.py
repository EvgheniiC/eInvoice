"""FastAPI dependencies for database and optional org context."""

from __future__ import annotations

import hmac
from typing import Collection, Iterator, Optional

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.session import get_session_factory
from app.services.auth_service import OrgContext, resolve_session

AUTH_UNAVAILABLE: str = "Kontofunktionen sind nicht konfiguriert."


def get_db() -> Iterator[Session]:
    factory: Optional[sessionmaker[Session]] = get_session_factory()
    if factory is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=AUTH_UNAVAILABLE)
    session: Session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_optional_db() -> Iterator[Optional[Session]]:
    factory: Optional[sessionmaker[Session]] = get_session_factory()
    if factory is None:
        yield None
        return
    session: Session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def read_session_cookie(request: Request) -> Optional[str]:
    return request.cookies.get(settings.auth_cookie_name)


def get_optional_org_context(
    request: Request,
    db: Optional[Session] = Depends(get_optional_db),
) -> Optional[OrgContext]:
    if db is None:
        return None
    return resolve_session(db, read_session_cookie(request))


def get_current_org(
    request: Request,
    db: Session = Depends(get_db),
) -> OrgContext:
    context: Optional[OrgContext] = resolve_session(db, read_session_cookie(request))
    if context is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bitte anmelden.",
        )
    return context


def require_org_role(context: OrgContext, allowed_roles: Collection[str]) -> OrgContext:
    """Reject organization actions that are outside the membership role."""
    if context.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ihre Rolle erlaubt diese Aktion nicht.",
        )
    return context


def require_admin_token(request: Request) -> None:
    expected: Optional[str] = settings.admin_api_token
    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Admin-API ist nicht konfiguriert.",
        )
    provided: str = request.headers.get("x-admin-token", "")
    if not hmac.compare_digest(provided, expected):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Ungültiges Admin-Token.")
