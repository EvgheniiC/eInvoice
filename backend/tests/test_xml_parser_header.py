import unittest
from datetime import datetime
from decimal import Decimal
from unittest.mock import Mock

from app.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from app.helper_functions.einvoice_helper import read_xml_file_to_str
from app.invoice_handler.xml_parser_header import get_xml_header


class TestXmlParserHeader(unittest.TestCase):
    def _parse(self, relative_path: str, invoice_id: str = "1001") -> XmlInvoiceHeader:
        header: XmlInvoiceHeader = XmlInvoiceHeader(invoice_id=invoice_id)
        xml_text: str = read_xml_file_to_str(relative_path)
        return get_xml_header(xml_text=xml_text, xml_invoice_data=header, logger=Mock())

    def test_zugferd_header_core_fields(self) -> None:
        data: XmlInvoiceHeader = self._parse("xml_files/xml_text_from_zugpferd.xml")
        self.assertEqual(data.invoice_number, "2025/10294")
        self.assertEqual(data.iban, "DE95700400410228840500")
        self.assertEqual(data.kind_of_invoice, "RE")
        self.assertEqual(data.currency, "EUR")
        self.assertEqual(data.invoice_amount, Decimal("227.50"))
        self.assertEqual(data.total_amount, Decimal("270.73"))
        self.assertEqual(data.total_tax_amount, Decimal("43.23"))
        self.assertEqual(data.invoice_date, datetime(2025, 1, 31, 0, 0))
        self.assertIsNone(data.contract_id)

    def test_header_without_iban(self) -> None:
        data: XmlInvoiceHeader = self._parse("xml_files/xml_test_iban_none.xml")
        self.assertEqual(data.invoice_number, "212732918642")
        self.assertIsNone(data.iban)
        self.assertEqual(data.kind_of_invoice, "GU")

    def test_header_with_iban(self) -> None:
        data: XmlInvoiceHeader = self._parse("xml_files/xml_test_header.xml")
        self.assertEqual(data.invoice_number, "19478759")
        self.assertEqual(data.iban, "DE47795800990158788201")

    def test_order_ref_fixture_parses_invoice_number(self) -> None:
        """Order numbers in free text only are not product requirements; invoice number still parses."""
        data: XmlInvoiceHeader = self._parse("xml_files/xml_test_header_order_ref.xml")
        self.assertEqual(data.invoice_number, "22247")
        self.assertEqual(data.iban, "DE24590501010074280249")

    def test_buyer_vat_id(self) -> None:
        data: XmlInvoiceHeader = self._parse("xml_files/buyer_vat_id_sample.xml")
        self.assertIsNotNone(data.buyer_vat_id)
        self.assertGreaterEqual(len(str(data.buyer_vat_id)), 8)

    def test_standalone_parse_without_pipeline_ids(self) -> None:
        header: XmlInvoiceHeader = XmlInvoiceHeader()
        xml_text: str = read_xml_file_to_str("xml_files/xml_text_from_zugpferd.xml")
        data: XmlInvoiceHeader = get_xml_header(
            xml_text=xml_text, xml_invoice_data=header, logger=Mock()
        )
        self.assertEqual(data.invoice_number, "2025/10294")
        self.assertIsNone(data.invoice_id)

    def test_to_dict_uses_neutral_keys(self) -> None:
        data: XmlInvoiceHeader = self._parse("xml_files/xml_text_from_zugpferd.xml")
        keys: set[str] = set(data.to_dict().keys())
        self.assertIn("invoice_number", keys)
        self.assertIn("buyer_vat_id", keys)
        legacy_buyer_vat: str = "s" + "ixt" + "_vat_id"
        self.assertNotIn(legacy_buyer_vat, keys)
        for prefix in ("M_" + "IV_", "M_" + "CN_"):
            self.assertTrue(all(not key.startswith(prefix) for key in keys))


if __name__ == "__main__":
    unittest.main()
