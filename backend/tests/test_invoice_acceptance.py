from __future__ import annotations

import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

from app.helper_functions.pdf_security import UnsafePdfError, assert_pdf_safe
from app.schemas.invoice import InvoiceParseResponse, ParseStatus
from app.services.invoice_service import InvoiceService

UBL_INVOICE: str = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2">
  <cbc:ID>INV-DECIMAL-1</cbc:ID>
  <cbc:IssueDate>2026-08-17</cbc:IssueDate>
  <cbc:DueDate>2026-08-31</cbc:DueDate>
  <cbc:InvoiceTypeCode>380</cbc:InvoiceTypeCode>
  <cbc:DocumentCurrencyCode>EUR</cbc:DocumentCurrencyCode>
  <cac:AccountingSupplierParty><cac:Party><cac:PartyLegalEntity>
    <cbc:RegistrationName>Demo Supplier GmbH</cbc:RegistrationName>
  </cac:PartyLegalEntity></cac:Party></cac:AccountingSupplierParty>
  <cac:AccountingCustomerParty><cac:Party><cac:PartyLegalEntity>
    <cbc:RegistrationName>Demo Buyer GmbH</cbc:RegistrationName>
  </cac:PartyLegalEntity></cac:Party></cac:AccountingCustomerParty>
  <cac:TaxTotal><cbc:TaxAmount currencyID="EUR">0.03</cbc:TaxAmount>
    <cac:TaxSubtotal><cbc:TaxableAmount currencyID="EUR">0.30</cbc:TaxableAmount>
      <cbc:TaxAmount currencyID="EUR">0.03</cbc:TaxAmount>
      <cac:TaxCategory><cbc:Percent>10</cbc:Percent></cac:TaxCategory>
    </cac:TaxSubtotal>
  </cac:TaxTotal>
  <cac:LegalMonetaryTotal>
    <cbc:LineExtensionAmount currencyID="EUR">0.30</cbc:LineExtensionAmount>
    <cbc:TaxExclusiveAmount currencyID="EUR">0.30</cbc:TaxExclusiveAmount>
    <cbc:TaxInclusiveAmount currencyID="EUR">0.33</cbc:TaxInclusiveAmount>
  </cac:LegalMonetaryTotal>
  <cac:InvoiceLine>
    <cbc:ID>1</cbc:ID>
    <cbc:InvoicedQuantity unitCode="HUR">3</cbc:InvoicedQuantity>
    <cbc:LineExtensionAmount currencyID="EUR">0.30</cbc:LineExtensionAmount>
    <cac:Item><cbc:Name>Arbeitszeit</cbc:Name>
      <cac:ClassifiedTaxCategory><cbc:Percent>10</cbc:Percent></cac:ClassifiedTaxCategory>
    </cac:Item>
    <cac:Price><cbc:PriceAmount currencyID="EUR">0.10</cbc:PriceAmount></cac:Price>
  </cac:InvoiceLine>
</Invoice>
"""


class TestInvoiceAcceptance(unittest.TestCase):
    def setUp(self) -> None:
        self.service: InvoiceService = InvoiceService()

    def test_decimal_amounts_units_and_tax_breakdown(self) -> None:
        result: InvoiceParseResponse = self.service.parse_upload(
            "invoice.xml", UBL_INVOICE.encode("utf-8")
        )

        self.assertIn(result.status, (ParseStatus.SUCCESS, ParseStatus.PARTIAL))
        self.assertEqual(result.document_type, "invoice")
        self.assertEqual(result.due_date, "2026-08-31")
        self.assertEqual(result.totals.gross if result.totals else None, Decimal("0.33"))
        self.assertEqual(result.line_items[0].unit, "HUR")
        self.assertEqual(result.line_items[0].unit_price, Decimal("0.10"))
        self.assertEqual(result.line_items[0].gross_amount, Decimal("0.33"))
        self.assertEqual(result.totals.tax_breakdown[0].rate, Decimal("10"))

    def test_pdf_bytes_with_xml_extension_are_rejected(self) -> None:
        result: InvoiceParseResponse = self.service.parse_upload(
            "renamed.xml", b"%PDF-1.7\n%%EOF"
        )

        self.assertEqual(result.status, ParseStatus.ERROR)
        self.assertTrue(
            any(issue.code == "FILE_TYPE_MISMATCH" for issue in result.validation_issues)
        )

    def test_xml_bytes_with_pdf_extension_are_rejected(self) -> None:
        result: InvoiceParseResponse = self.service.parse_upload(
            "renamed.pdf", UBL_INVOICE.encode("utf-8")
        )

        self.assertEqual(result.status, ParseStatus.ERROR)
        self.assertTrue(
            any(issue.code == "FILE_TYPE_MISMATCH" for issue in result.validation_issues)
        )

    def test_active_pdf_is_rejected(self) -> None:
        with self.assertRaises(UnsafePdfError):
            assert_pdf_safe(b"%PDF-1.7\n/JavaScript (alert)\n%%EOF")

    def test_embedded_non_invoice_xml_is_rejected(self) -> None:
        pdf_path: Path = Path(__file__).parent / "pdf_files" / "RE_202512245.pdf"
        if not pdf_path.exists():
            self.skipTest("local ZUGFeRD fixture not present")

        with patch(
            "app.services.invoice_service.extract_embedded_xml_from_pdf",
            return_value="<CustomDocument><ID>1</ID></CustomDocument>",
        ):
            result: InvoiceParseResponse = self.service.parse_upload(
                pdf_path.name, pdf_path.read_bytes()
            )

        self.assertEqual(result.status, ParseStatus.ERROR)
        self.assertTrue(
            any(issue.code == "UNSUPPORTED_XML_FORMAT" for issue in result.validation_issues)
        )

    def test_ubl_credit_note_is_identified(self) -> None:
        xml_path: Path = Path(__file__).parent / "xml_files" / "credit_note_positive_amounts.xml"
        if not xml_path.exists():
            self.skipTest("local UBL CreditNote fixture not present")

        result: InvoiceParseResponse = self.service.parse_upload(
            xml_path.name, xml_path.read_bytes()
        )

        self.assertIn(result.status, (ParseStatus.SUCCESS, ParseStatus.PARTIAL))
        self.assertEqual(result.document_type, "credit_note")
        self.assertTrue(all((item.net_amount or Decimal("0")) >= 0 for item in result.line_items))

    def test_invoice_without_lines_does_not_get_placeholder_position(self) -> None:
        xml_without_lines: str = UBL_INVOICE.split("  <cac:InvoiceLine>", 1)[0] + "</Invoice>"

        result: InvoiceParseResponse = self.service.parse_upload(
            "without-lines.xml", xml_without_lines.encode("utf-8")
        )

        self.assertEqual(result.line_items, [])
        self.assertTrue(
            any(issue.code == "BG-25_MISSING" for issue in result.validation_issues)
        )


if __name__ == "__main__":
    unittest.main()
