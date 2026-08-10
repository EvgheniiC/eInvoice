"""Golden-file regression for parse_upload on the local fixture corpus.

Invoice bytes stay local (gitignored). Committed snapshots live in tests/goldens/.

Regenerate after intentional parser changes:
  UPDATE_GOLDENS=1 pytest tests/test_golden_files.py
"""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

from app.schemas.invoice import InvoiceParseResponse
from app.services.invoice_service import InvoiceService
from golden_utils import assert_matches_golden, snapshot_parse_response

# (relative path under tests/, golden name without .json)
GOLDEN_CASES: List[Tuple[str, str]] = [
    # Happy-path XML
    ("xml_files/xml_text_from_zugpferd.xml", "xml_text_from_zugpferd"),
    ("xml_files/xml_text_from_xml.xml", "xml_text_from_xml"),
    ("xml_files/xml_test_header_order_ref.xml", "xml_test_header_order_ref"),
    ("xml_files/discount_new_position.xml", "discount_new_position"),
    ("xml_files/buyer_vat_id_sample.xml", "buyer_vat_id_sample"),
    ("xml_files/credit_note_positive_amounts.xml", "credit_note_positive_amounts"),
    # Invalid XRechnung / edge XML
    ("xml_files/Invalid_XR_missing_invoice_id.xml", "Invalid_XR_missing_invoice_id"),
    ("xml_files/Invalid_XR_missing_issue_date.xml", "Invalid_XR_missing_issue_date"),
    ("xml_files/Invalid_XR_inconsistent_totals.xml", "Invalid_XR_inconsistent_totals"),
    ("xml_files/Invalid_XR_not_well_formed.xml", "Invalid_XR_not_well_formed"),
    # Explicit unsupported format
    ("xml_files/0426477394-207600RECHNUNG1.xml", "opentrans_0426477394"),
    # ZUGFeRD PDF happy + mismatch / broken
    ("pdf_files/Rechnung_1096393995.pdf", "Rechnung_1096393995"),
    ("pdf_files/Mismatch_iban_1096393995.pdf", "Mismatch_iban_1096393995"),
    (
        "pdf_files/Mismatch_invoice_no_amount_1096393995.pdf",
        "Mismatch_invoice_no_amount_1096393995",
    ),
    ("pdf_files/Broken_embedded_xml_1096393995.pdf", "Broken_embedded_xml_1096393995"),
    ("pdf_files/notEinvoiceFormat.pdf", "notEinvoiceFormat"),
]


class TestGoldenFiles(unittest.TestCase):
    def setUp(self) -> None:
        self.service: InvoiceService = InvoiceService()
        self.tests_dir: Path = Path(__file__).parent

    def _assert_case(self, relative_path: str, golden_name: str) -> None:
        fixture_path: Path = self.tests_dir / relative_path
        if not fixture_path.exists():
            self.skipTest(f"missing local fixture: {relative_path}")

        result: InvoiceParseResponse = self.service.parse_upload(
            filename=fixture_path.name,
            content=fixture_path.read_bytes(),
        )
        snapshot: Dict[str, Any] = snapshot_parse_response(result)
        assert_matches_golden(golden_name, snapshot)


def _make_test(relative_path: str, golden_name: str) -> Callable[[TestGoldenFiles], None]:
    def _test(self: TestGoldenFiles) -> None:
        self._assert_case(relative_path, golden_name)

    _test.__name__ = f"test_golden_{golden_name}"
    _test.__doc__ = f"Golden snapshot for {relative_path}"
    return _test


for _relative_path, _golden_name in GOLDEN_CASES:
    setattr(
        TestGoldenFiles,
        f"test_golden_{_golden_name}",
        _make_test(_relative_path, _golden_name),
    )


if __name__ == "__main__":
    unittest.main()
