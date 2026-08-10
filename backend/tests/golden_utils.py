"""Helpers for golden-file regression snapshots of InvoiceParseResponse."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.schemas.invoice import InvoiceParseResponse, LineItem, ValidationIssue

GOLDENS_DIR: Path = Path(__file__).parent / "goldens"
UPDATE_ENV: str = "UPDATE_GOLDENS"

# KoSIT availability differs by machine; exclude from committed snapshots.
_VOLATILE_ISSUE_PREFIXES: tuple[str, ...] = ("KOSIT_",)


def should_update_goldens() -> bool:
    return os.environ.get(UPDATE_ENV, "").strip() in {"1", "true", "TRUE", "yes", "YES"}


def _round_money(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    return round(float(value), 2)


def _line_sort_key(item: LineItem) -> tuple[int, int]:
    if item.position is None:
        return (1, 0)
    return (0, int(item.position))


def _issue_sort_key(issue: Dict[str, Optional[str]]) -> tuple[str, str, str]:
    return (
        issue.get("level") or "",
        issue.get("category") or "",
        issue.get("code") or "",
    )


def _is_stable_issue(issue: ValidationIssue) -> bool:
    code: str = issue.code or ""
    return not any(code.startswith(prefix) for prefix in _VOLATILE_ISSUE_PREFIXES)


def snapshot_parse_response(response: InvoiceParseResponse) -> Dict[str, Any]:
    """Stable subset of the public parse DTO for regression comparison."""
    line_items: List[Dict[str, Any]] = []
    for item in sorted(response.line_items, key=_line_sort_key):
        line_items.append(
            {
                "position": item.position,
                "description": item.description,
                "quantity": _round_money(item.quantity),
                "unit": item.unit,
                "unit_price": _round_money(item.unit_price),
                "tax_rate": _round_money(item.tax_rate),
                "net_amount": _round_money(item.net_amount),
                "gross_amount": _round_money(item.gross_amount),
            }
        )

    validation_issues: List[Dict[str, Optional[str]]] = []
    for issue in response.validation_issues:
        if not _is_stable_issue(issue):
            continue
        validation_issues.append(
            {
                "level": issue.level,
                "category": issue.category,
                "code": issue.code,
            }
        )
    validation_issues.sort(key=_issue_sort_key)

    mismatch_fields: List[Dict[str, Any]] = []
    for field in response.mismatch_fields:
        mismatch_fields.append(
            {
                "field": field.field,
                "xml_value": field.xml_value,
                "pdf_value": field.pdf_value,
                "matched": field.matched,
            }
        )
    mismatch_fields.sort(key=lambda row: str(row.get("field") or ""))

    seller: Optional[Dict[str, Optional[str]]] = None
    if response.seller is not None:
        seller = response.seller.model_dump()

    buyer: Optional[Dict[str, Optional[str]]] = None
    if response.buyer is not None:
        buyer = response.buyer.model_dump()

    totals: Optional[Dict[str, Any]] = None
    if response.totals is not None:
        totals = {
            "net": _round_money(response.totals.net),
            "tax": _round_money(response.totals.tax),
            "gross": _round_money(response.totals.gross),
            "currency": response.totals.currency,
        }

    return {
        "status": response.status.value,
        "file_type": response.file_type,
        "invoice_number": response.invoice_number,
        "issue_date": response.issue_date,
        "due_date": response.due_date,
        "seller": seller,
        "buyer": buyer,
        "totals": totals,
        "line_items": line_items,
        "payment_reference": response.payment_reference,
        "validation_status": response.validation_status.value,
        "validation_issues": validation_issues,
        "mismatch_fields": mismatch_fields,
    }


def golden_path(name: str) -> Path:
    return GOLDENS_DIR / f"{name}.json"


def load_golden(name: str) -> Dict[str, Any]:
    path: Path = golden_path(name)
    with path.open(encoding="utf-8") as handle:
        data: Any = json.load(handle)
    if not isinstance(data, dict):
        raise TypeError(f"golden {path} must be a JSON object")
    return data


def write_golden(name: str, snapshot: Dict[str, Any]) -> Path:
    GOLDENS_DIR.mkdir(parents=True, exist_ok=True)
    path: Path = golden_path(name)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(snapshot, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def assert_matches_golden(name: str, snapshot: Dict[str, Any]) -> None:
    """Compare snapshot to committed golden, or rewrite when UPDATE_GOLDENS=1."""
    path: Path = golden_path(name)
    if should_update_goldens():
        write_golden(name, snapshot)
        return

    if not path.exists():
        raise AssertionError(
            f"missing golden {path.name}. Generate with: "
            f"{UPDATE_ENV}=1 pytest tests/test_golden_files.py"
        )

    expected: Dict[str, Any] = load_golden(name)
    if snapshot != expected:
        actual_path: Path = GOLDENS_DIR / f"{name}.actual.json"
        with actual_path.open("w", encoding="utf-8", newline="\n") as handle:
            json.dump(snapshot, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
        raise AssertionError(
            f"golden mismatch for {name}.json\n"
            f"  expected: {path}\n"
            f"  actual:   {actual_path}\n"
            f"Update with: {UPDATE_ENV}=1 pytest tests/test_golden_files.py"
        )
