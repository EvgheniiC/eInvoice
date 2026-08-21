"""Reset in-memory quota and parallel slots between tests."""

from __future__ import annotations

import pytest

from app.services.quota_service import reset_quota_runtime


@pytest.fixture(autouse=True)
def _reset_quota_runtime() -> None:
    reset_quota_runtime()
