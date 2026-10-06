"""Administrator allowlist based on server settings, not an organization role."""

from __future__ import annotations

from app.core.config import settings


def is_admin_email(email: str) -> bool:
    """Return True when the login email is on the server allowlist."""
    normalized: str = email.strip().casefold()
    if not normalized:
        return False
    return normalized in settings.admin_email_set
