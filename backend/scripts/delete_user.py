"""Remove an account by email (user, tokens, sessions, empty organization)."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.session import get_session_factory, session_scope
from app.services.auth_service import AuthError, delete_user_by_email


def main(argv: Optional[list[str]] = None) -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Delete a user account and its empty organization.",
    )
    parser.add_argument("--email", required=True, help="Account email to delete")
    args: argparse.Namespace = parser.parse_args(argv)
    if not settings.auth_enabled:
        print("DATABASE_URL is not set.", file=sys.stderr)
        return 1
    init_account_store()
    if get_session_factory() is None:
        print("Database is not ready.", file=sys.stderr)
        return 1
    try:
        deleted: str = ""
        for session in session_scope():
            deleted = delete_user_by_email(session, email=args.email)
        print(f"deleted {deleted}")
    except AuthError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
