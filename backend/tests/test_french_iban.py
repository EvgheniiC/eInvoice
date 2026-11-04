import unittest
from typing import Optional
from unittest.mock import Mock

from app.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from app.helper_functions.einvoice_helper import read_xml_file_to_str
from app.invoice_handler.xml_parser_header import get_xml_header
from app.invoice_handler.xml_vendor_parser import get_einvoice_vendor_data

FIXTURE: str = "xml_files/12415598_masa.xml"
COMPACT_IBAN: str = "FR7610096181020002416790151"
SPACED_IBAN: str = "FR76 1009 6181 0200 0241 6790 151"


class TestFrenchIban(unittest.TestCase):
    def _xml(self, iban: Optional[str] = None) -> str:
        xml_text: Optional[str] = read_xml_file_to_str(FIXTURE)
        self.assertIsNotNone(xml_text)
        assert xml_text is not None
        if iban is None:
            return xml_text
        return xml_text.replace(COMPACT_IBAN, iban)

    def _header(self, xml_text: str) -> XmlInvoiceHeader:
        header: XmlInvoiceHeader = XmlInvoiceHeader(invoice_id="12415598")
        return get_xml_header(xml_text=xml_text, xml_invoice_data=header, logger=Mock())

    def test_compact_french_iban_is_extracted(self) -> None:
        xml_text: str = self._xml()
        header: XmlInvoiceHeader = self._header(xml_text)
        self.assertEqual(header.invoice_number, "12415598")
        self.assertEqual(header.iban, COMPACT_IBAN)

        vendor_data, _vendor = get_einvoice_vendor_data(
            invoice_id="12415598", xml_text=xml_text, logger=Mock()
        )
        self.assertEqual(vendor_data["seller_iban"], COMPACT_IBAN)
        self.assertEqual(vendor_data["payment_means"][0]["AccountID"], COMPACT_IBAN)

    def test_spaced_french_iban_is_normalized(self) -> None:
        xml_text: str = self._xml(SPACED_IBAN)
        header: XmlInvoiceHeader = self._header(xml_text)
        self.assertEqual(header.iban, COMPACT_IBAN)

        vendor_data, _vendor = get_einvoice_vendor_data(
            invoice_id="12415598", xml_text=xml_text, logger=Mock()
        )
        self.assertEqual(vendor_data["seller_iban"], COMPACT_IBAN)


if __name__ == "__main__":
    unittest.main()
