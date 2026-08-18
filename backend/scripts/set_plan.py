"""Manually set an organization plan (pilot Plus). Does not store invoices."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from app.core.config import settings
from app.db.bootstrap import init_account_store
from app.db.session import get_session_factory, session_scope
from app.services.auth_service import AuthError, set_plan_for_email


def main(argv: Optional[list[str]] = None) -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Set plan=plus|team|free for a pilot organization (by Inhaber email).",
    )
    parser.add_argument("--email", required=True, help="Inhaber email")
    parser.add_argument("--plan", required=True, choices=["free", "plus", "team"])
    args: argparse.Namespace = parser.parse_args(argv)
    if not settings.auth_enabled:
        print("DATABASE_URL is not set.", file=sys.stderr)
        return 1
    init_account_store()
    if get_session_factory() is None:
        print("Database is not ready.", file=sys.stderr)
        return 1
    try:
        for session in session_scope():
            organization = set_plan_for_email(session, email=args.email, plan_code=args.plan)
            print(f"{organization.name} -> {args.plan}")
    except AuthError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
