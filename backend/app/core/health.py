"""Liveness and readiness snapshot (no invoice data)."""

from __future__ import annotations

import shutil
from dataclasses import dataclass
from typing import List, Optional

from app.core.config import settings


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
        ready: bool = True
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
        ready = kosit_files_ready and java_ok

    overall: str = "ok" if ready else "degraded"
    return HealthSnapshot(
        status=overall,
        ready=ready,
        kosit_required=kosit_required,
        kosit_ready=kosit_files_ready,
        checks=[process_check, kosit_check, java_check],
    )


def _java_available() -> bool:
    java_bin: str = settings.kosit_java_bin.strip() or "java"
    return shutil.which(java_bin) is not None
