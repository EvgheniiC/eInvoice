"""Assert the committed golden corpus covers valid, invalid, and edge invoices."""

from __future__ import annotations

import unittest
from pathlib import Path
from typing import Dict, List

GOLDENS_DIR: Path = Path(__file__).parent / "goldens"

REQUIRED: Dict[str, List[str]] = {
    "valid": [
        "xml_text_from_zugpferd.json",
        "xml_text_from_xml.json",
        "Rechnung_1096393995.json",
    ],
    "invalid": [
        "Invalid_XR_missing_invoice_id.json",
        "Invalid_XR_missing_issue_date.json",
        "Invalid_XR_inconsistent_totals.json",
        "Invalid_XR_not_well_formed.json",
    ],
    "edge": [
        "credit_note_positive_amounts.json",
        "discount_new_position.json",
        "opentrans_0426477394.json",
        "notEinvoiceFormat.json",
        "Mismatch_iban_1096393995.json",
        "Mismatch_invoice_no_amount_1096393995.json",
        "Broken_embedded_xml_1096393995.json",
        "buyer_vat_id_sample.json",
    ],
}


class TestValidationCorpus(unittest.TestCase):
    def test_required_goldens_exist(self) -> None:
        missing: List[str] = []
        for group, names in REQUIRED.items():
            for name in names:
                path: Path = GOLDENS_DIR / name
                if not path.is_file():
                    missing.append(f"{group}/{name}")
        self.assertEqual(missing, [], msg=f"missing goldens: {missing}")

    def test_invalid_goldens_are_marked_invalid_or_error(self) -> None:
        for name in REQUIRED["invalid"]:
            path: Path = GOLDENS_DIR / name
            text: str = path.read_text(encoding="utf-8")
            self.assertTrue(
                '"validation_status": "invalid"' in text or '"status": "error"' in text,
                msg=f"{name} should represent an invalid or rejected invoice",
            )


if __name__ == "__main__":
    unittest.main()
