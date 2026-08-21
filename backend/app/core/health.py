"""Liveness and readiness snapshot (no invoice data)."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import List, Optional

from app.core.config import settings
from app.db.session import ping_database


@dataclass(frozen=True)
class HealthCheckResult:
    """Single dependency check shown on health/readiness endpoints."""

    name: str
    status: str
    detail: Optional[str] = None


@dataclass(frozen=True)
class HealthSnapshot:
    """Computed process health used by /health, /health/live, and /health/ready."""

    status: str
    ready: bool
    kosit_required: bool
    kosit_ready: bool
    checks: List[HealthCheckResult]


def build_health_snapshot() -> HealthSnapshot:
    """Evaluate cheap readiness checks (filesystem / PATH only, no KoSIT run)."""
    process_check: HealthCheckResult = HealthCheckResult(name="process", status="ok")
    kosit_required: bool = settings.require_kosit
    kosit_files_ready: bool = settings.kosit_ready
    java_ok: bool = _java_available()
    database_check: HealthCheckResult = _database_check()
    database_ok: bool = database_check.status in {"ok", "not_required"}
    email_check: HealthCheckResult = _email_check()
    email_ok: bool = email_check.status in {"ok", "not_required"}

    if not kosit_required:
        kosit_check: HealthCheckResult = HealthCheckResult(
            name="kosit",
            status="not_required" if not kosit_files_ready else "ok",
            detail=None if kosit_files_ready else "KoSIT is optional in this environment.",
        )
        java_check: HealthCheckResult = HealthCheckResult(
            name="java",
            status="not_required" if not java_ok else "ok",
        )
        ready: bool = database_ok and email_ok
    else:
        kosit_check = HealthCheckResult(
            name="kosit",
            status="ok" if kosit_files_ready else "unavailable",
            detail=None if kosit_files_ready else "Validator JAR or scenarios XML is missing.",
        )
        java_check = HealthCheckResult(
            name="java",
            status="ok" if java_ok else "unavailable",
            detail=None if java_ok else "Java binary for KoSIT was not found on PATH.",
        )
        ready = kosit_files_ready and java_ok and database_ok and email_ok

    overall: str = "ok" if ready else "degraded"
    return HealthSnapshot(
        status=overall,
        ready=ready,
        kosit_required=kosit_required,
        kosit_ready=kosit_files_ready,
        checks=[process_check, kosit_check, java_check, database_check, email_check],
    )


def _email_check() -> HealthCheckResult:
    if not settings.auth_enabled:
        return HealthCheckResult(
            name="email",
            status="not_required",
            detail="Account store is off; guest Empfang only.",
        )
    if settings.email_ready:
        return HealthCheckResult(name="email", status="ok")
    if settings.uses_smtp_email:
        return HealthCheckResult(
            name="email",
            status="unavailable",
            detail="SMTP_HOST and SMTP_FROM (or SMTP_USERNAME) are required.",
        )
    return HealthCheckResult(
        name="email",
        status="unavailable",
        detail="Production accounts require EMAIL_BACKEND=smtp.",
    )


def _database_check() -> HealthCheckResult:
    if not settings.auth_enabled:
        return HealthCheckResult(
            name="database",
            status="not_required",
            detail="Account store is off; guest Empfang only.",
        )
    if settings.is_production and not settings.uses_postgres:
        return HealthCheckResult(
            name="database",
            status="unavailable",
            detail="Production requires PostgreSQL for accounts.",
        )
    if settings.is_production and settings.auth_secret_key == "dev-only-change-me":
        return HealthCheckResult(
            name="database",
            status="unavailable",
            detail="AUTH_SECRET_KEY is not set.",
        )
    if ping_database():
        return HealthCheckResult(name="database", status="ok")
    return HealthCheckResult(
        name="database",
        status="unavailable",
        detail="Database ping failed.",
    )


def _java_available() -> bool:
    java_bin: str = settings.kosit_java_bin.strip() or "java"
    return shutil.which(java_bin) is not None
