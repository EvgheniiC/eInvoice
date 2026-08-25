"""Start or stop the optional account database."""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.error_events import log_event
from app.db.seed import seed_plans
from app.db.session import configure_engine, create_schema, dispose_engine, get_session_factory


def init_account_store() -> None:
    """Connect and seed plans when DATABASE_URL is set. Guest parse does not need this."""
    if not settings.auth_enabled:
        dispose_engine()
        return
    if settings.is_production and not settings.uses_postgres:
        log_event(
            logging.ERROR,
            "database_sqlite_forbidden_in_production",
            fields={"event": "database_sqlite_forbidden_in_production"},
        )
        raise RuntimeError("Production accounts require PostgreSQL.")
    if settings.is_production and settings.auth_secret_key == "dev-only-change-me":
        log_event(
            logging.ERROR,
            "auth_secret_unconfigured",
            fields={"event": "auth_secret_unconfigured"},
        )
        raise RuntimeError("AUTH_SECRET_KEY must be configured for production accounts.")
    url: str = (settings.database_url or "").strip()
    configure_engine(url)
    if not settings.uses_postgres:
        create_schema()
    factory: sessionmaker[Session] | None = get_session_factory()
    if factory is None:
        return
    session: Session = factory()
    try:
        seed_plans(session)
    finally:
        session.close()
    log_event(logging.INFO, "account_store_ready", fields={"postgres": settings.uses_postgres})
