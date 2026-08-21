"""Send one test message with the configured SMTP backend. No invoice data."""

from __future__ import annotations

import argparse
import sys
from typing import Optional

from app.core.config import settings
from app.services.email_service import EmailDeliveryError, send_auth_email


def main(argv: Optional[list[str]] = None) -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Send a one-off verification mail to check SMTP.",
    )
    parser.add_argument("--to", required=True, help="Recipient email")
    args: argparse.Namespace = parser.parse_args(argv)
    print(f"backend={settings.email_backend} host={settings.smtp_host} from={settings.smtp_sender}")
    try:
        send_auth_email(to_email=args.to.strip(), purpose="verify_email", token="smtp-test-token")
    except EmailDeliveryError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("sent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
