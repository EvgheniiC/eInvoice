import unittest
from pathlib import Path

from app.schemas.invoice import (
    InvoiceParseResponse,
    InvoiceTotals,
    LineItem,
    PartyInfo,
    ParseStatus,
    ValidationStatus,
)
from app.services.en16931_validator import validate_invoice
from app.services.invoice_service import InvoiceService
from app.services.zugferd_consistency import (
    _compare_amount,
    _compare_iban,
    _compare_invoice_number,
)


class TestValidationAndMismatch(unittest.TestCase):
    def setUp(self) -> None:
        self.service: InvoiceService = InvoiceService()
        self.fixtures: Path = Path(__file__).parent / "xml_files"

    def test_parse_includes_validation_status(self) -> None:
        xml_path: Path = self.fixtures / "xml_text_from_zugpferd.xml"
        result = self.service.parse_upload(filename=xml_path.name, content=xml_path.read_bytes())
        self.assertNotEqual(result.validation_status, ValidationStatus.NOT_CHECKED)
        self.assertTrue(any(issue.code == "KOSIT_NOT_CONFIGURED" for issue in result.validation_issues))
        self.assertGreater(len(result.next_steps), 0)

    def test_business_validator_flags_missing_invoice_number(self) -> None:
        parsed: InvoiceParseResponse = InvoiceParseResponse(
            status=ParseStatus.PARTIAL,
            message="partial",
            filename="x.xml",
            file_type="xrechnung_xml",
            invoice_number=None,
            issue_date="2025-01-31",
            seller=PartyInfo(name="Seller GmbH"),
            buyer=PartyInfo(name="Buyer AG"),
            totals=InvoiceTotals(net=100.0, tax=19.0, gross=119.0, currency="EUR"),
            line_items=[
                LineItem(position=1, description="Service", quantity=1, net_amount=100.0, tax_rate=19.0)
            ],
        )
        xml_text: str = (
            '<?xml version="1.0"?><Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2">'
            "<CustomizationID>urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0"
            "</CustomizationID></Invoice>"
        )
        result = validate_invoice(xml_text=xml_text, parsed=parsed)
        self.assertEqual(result.status, ValidationStatus.INVALID)
        self.assertTrue(any(issue.code == "BT-1_MISSING" for issue in result.issues))

    def test_field_comparators_match_german_formats(self) -> None:
        pdf_text: str = "Rechnung 2025/10294 vom 31.01.2025 Brutto 270,73 EUR MwSt 43,23 IBAN DE95 7004 0041 0228 8405 00"
        number = _compare_invoice_number(pdf_text=pdf_text, xml_value="2025/10294")
        gross = _compare_amount(pdf_text=pdf_text, xml_value=270.73, field_name="gross", label="Brutto")
        tax = _compare_amount(pdf_text=pdf_text, xml_value=43.23, field_name="tax", label="MwSt")
        iban = _compare_iban(pdf_text=pdf_text, xml_value="DE95700400410228840500")
        self.assertTrue(number.matched)
        self.assertTrue(gross.matched)
        self.assertTrue(tax.matched)
        self.assertTrue(iban.matched)

    def test_field_comparators_detect_mismatch(self) -> None:
        pdf_text: str = "Rechnung 999 vom 01.01.2020 Summe 10,00"
        number = _compare_invoice_number(pdf_text=pdf_text, xml_value="2025/10294")
        gross = _compare_amount(pdf_text=pdf_text, xml_value=270.73, field_name="gross", label="Brutto")
        self.assertFalse(number.matched)
        self.assertFalse(gross.matched)


if __name__ == "__main__":
    unittest.main()
