"""Database engine and session factory. Optional: guest Empfang works without it."""

from __future__ import annotations

from typing import Iterator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.db.models import Base

_engine: Optional[Engine] = None
_session_factory: Optional[sessionmaker[Session]] = None


def configure_engine(url: str) -> Engine:
    """Create (or replace) the process-wide engine."""
    global _engine, _session_factory
    dispose_engine()
    connect_args: dict[str, object] = {}
    engine_kwargs: dict[str, object] = {"future": True, "pool_pre_ping": True}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
        if url in {"sqlite://", "sqlite:///:memory:"}:
            engine_kwargs["poolclass"] = StaticPool
    _engine = create_engine(url, connect_args=connect_args, **engine_kwargs)
    _session_factory = sessionmaker(bind=_engine, autoflush=False, autocommit=False, future=True)
    return _engine


def dispose_engine() -> None:
    """Drop the process-wide engine (tests)."""
    global _engine, _session_factory
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _session_factory = None


def get_engine() -> Optional[Engine]:
    return _engine


def get_session_factory() -> Optional[sessionmaker[Session]]:
    return _session_factory


def create_schema() -> None:
    """Create tables (SQLite tests/dev). Production uses Alembic."""
    engine: Optional[Engine] = _engine
    if engine is None:
        return
    Base.metadata.create_all(engine)


def ping_database() -> bool:
    """Return True if SELECT 1 succeeds."""
    engine: Optional[Engine] = _engine
    if engine is None:
        return False
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def session_scope() -> Iterator[Session]:
    """Open a short-lived session. Caller commits writes."""
    factory: Optional[sessionmaker[Session]] = _session_factory
    if factory is None:
        raise RuntimeError("database_not_configured")
    session: Session = factory()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
