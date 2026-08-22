"""einvoice-worker: drain batch_items one file at a time via InvoiceService.parse_upload.

Originals stay in BATCH_TEMP_DIR until the accountant ZIP is downloaded or TTL expires.
"""

from __future__ import annotations

import argparse
import logging
import signal
import sys
import time
from typing import Optional

from app.core.config import settings
from app.core.error_events import format_safe_stack, log_event
from app.core.logging_config import configure_logging
from app.db.bootstrap import init_account_store
from app.services.batch_service import drain_queue, process_next_item

_stop: bool = False


def main(argv: Optional[list[str]] = None) -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="eInvoice batch worker")
    parser.add_argument(
        "--once",
        action="store_true",
        help="Process the current queue and exit.",
    )
    args: argparse.Namespace = parser.parse_args(argv)

    configure_logging(settings.log_level, settings.log_format, force=True)
    init_account_store()
    if not settings.auth_enabled:
        log_event(logging.ERROR, "batch_worker_no_database")
        print("DATABASE_URL is not set. The batch worker cannot start.", file=sys.stderr)
        return 1

    log_event(logging.INFO, "batch_worker_started", fields={"once": bool(args.once)})
    if args.once:
        processed: int = drain_queue()
        log_event(logging.INFO, "batch_worker_once_done", fields={"processed": processed})
        print(f"Processed {processed} queued file(s).", flush=True)
        return 0

    print("eInvoice batch worker is running. Waiting for jobs. Stop with Ctrl+C.", flush=True)

    signal.signal(signal.SIGTERM, _request_stop)
    signal.signal(signal.SIGINT, _request_stop)
    while not _stop:
        try:
            did_work: bool = process_next_item()
        except Exception as exc:
            log_event(
                logging.ERROR,
                "batch_worker_loop_error",
                fields={"exc_type": type(exc).__name__, "stack": format_safe_stack(exc)},
            )
            did_work = False
        if _stop:
            break
        if not did_work:
            time.sleep(max(0.2, settings.batch_poll_seconds))
    log_event(logging.INFO, "batch_worker_stopped")
    return 0


def _request_stop(_signum: int, _frame: object) -> None:
    global _stop
    _stop = True


if __name__ == "__main__":
    sys.exit(main())
