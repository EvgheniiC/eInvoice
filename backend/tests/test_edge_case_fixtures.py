"""Regression checks for generated local edge-case fixtures."""

from __future__ import annotations

import unittest
from pathlib import Path

from app.schemas.invoice import ParseStatus, ValidationStatus
from app.services.invoice_service import InvoiceService


class TestEdgeCaseFixtures(unittest.TestCase):
    def setUp(self) -> None:
        self.service: InvoiceService = InvoiceService()
        self.xml_dir: Path = Path(__file__).parent / "xml_files"
        self.pdf_dir: Path = Path(__file__).parent / "pdf_files"

    def _require(self, path: Path) -> Path:
        if not path.exists():
            self.skipTest(
                f"missing local fixture {path.name}; "
                "run: python backend/scripts/generate_edge_case_fixtures.py"
            )
        return path

    def test_invalid_xr_missing_invoice_id(self) -> None:
        path: Path = self._require(self.xml_dir / "Invalid_XR_missing_invoice_id.xml")
        result = self.service.parse_upload(path.name, path.read_bytes())
        self.assertEqual(result.status, ParseStatus.ERROR)
        self.assertEqual(result.validation_status, ValidationStatus.INVALID)
        self.assertTrue(
            any(issue.code == "BT-1_MISSING" for issue in result.validation_issues)
        )

    def test_invalid_xr_missing_issue_date(self) -> None:
        path: Path = self._require(self.xml_dir / "Invalid_XR_missing_issue_date.xml")
        result = self.service.parse_upload(path.name, path.read_bytes())
        self.assertIn(result.status, (ParseStatus.PARTIAL, ParseStatus.ERROR))
        self.assertEqual(result.validation_status, ValidationStatus.INVALID)
        self.assertTrue(
            any(issue.code == "BT-2_MISSING" for issue in result.validation_issues)
        )

    def test_invalid_xr_inconsistent_totals(self) -> None:
        path: Path = self._require(self.xml_dir / "Invalid_XR_inconsistent_totals.xml")
        result = self.service.parse_upload(path.name, path.read_bytes())
        self.assertEqual(result.status, ParseStatus.PARTIAL)
        self.assertEqual(result.validation_status, ValidationStatus.INVALID)
        self.assertTrue(
            any(issue.code == "AMOUNT_INCONSISTENT" for issue in result.validation_issues)
        )

    def test_invalid_xr_not_well_formed(self) -> None:
        path: Path = self._require(self.xml_dir / "Invalid_XR_not_well_formed.xml")
        result = self.service.parse_upload(path.name, path.read_bytes())
        self.assertEqual(result.status, ParseStatus.ERROR)
        self.assertEqual(result.validation_status, ValidationStatus.INVALID)

    def test_mismatch_invoice_no_and_amount(self) -> None:
        path: Path = self._require(
            self.pdf_dir / "Mismatch_invoice_no_amount_1096393995.pdf"
        )
        result = self.service.parse_upload(path.name, path.read_bytes())
        self.assertEqual(result.status, ParseStatus.PARTIAL)
        self.assertEqual(result.invoice_number, "MISMATCH-99999")
        mismatched: set[str] = {
            field.field for field in result.mismatch_fields if not field.matched
        }
        self.assertIn("invoice_number", mismatched)
        self.assertTrue({"gross", "tax"} & mismatched)

    def test_mismatch_iban(self) -> None:
        path: Path = self._require(self.pdf_dir / "Mismatch_iban_1096393995.pdf")
        result = self.service.parse_upload(path.name, path.read_bytes())
        self.assertEqual(result.status, ParseStatus.PARTIAL)
        self.assertEqual(result.invoice_number, "1096393995")
        iban_fields = [f for f in result.mismatch_fields if f.field == "iban"]
        self.assertEqual(len(iban_fields), 1)
        self.assertFalse(iban_fields[0].matched)

    def test_broken_embedded_xml(self) -> None:
        path: Path = self._require(self.pdf_dir / "Broken_embedded_xml_1096393995.pdf")
        result = self.service.parse_upload(path.name, path.read_bytes())
        self.assertEqual(result.status, ParseStatus.ERROR)
        self.assertEqual(result.file_type, "zugferd_pdf")
        self.assertTrue(
            any(
                issue.code in {"PARSE_EXCEPTION", "XML_NOT_WELL_FORMED", "ZUGFERD_XML_EXTRACT_FAILED"}
                for issue in result.validation_issues
            )
        )


if __name__ == "__main__":
    unittest.main()
