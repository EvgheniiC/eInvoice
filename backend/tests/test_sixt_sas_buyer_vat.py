import unittest
from decimal import Decimal
from typing import Optional
from unittest.mock import Mock

from app.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from app.helper_functions.einvoice_helper import read_xml_file_to_str
from app.invoice_handler.xml_parser_header import get_xml_header
from app.invoice_handler.xml_vendor_parser import get_einvoice_vendor_data
from app.schemas.invoice import InvoiceParseResponse
from app.services.invoice_service import InvoiceService

FIXTURE: str = "xml_files/RE538779_sixt_sas.xml"
BUYER_VAT_ID: str = "FR74411207012"
SELLER_VAT_ID: str = "DE206863576"
IBAN: str = "DE14700700100200209500"


class TestSixtSasBuyerVat(unittest.TestCase):
    """Buyer is Sixt SAS (FR VAT). Seller VAT and the shared IBAN stay German."""

    def _xml(self) -> str:
        xml_text: Optional[str] = read_xml_file_to_str(FIXTURE)
        self.assertIsNotNone(xml_text)
        assert xml_text is not None
        return xml_text

    def test_header_reads_invoice_iban_and_order(self) -> None:
        xml_text: str = self._xml()
        header: XmlInvoiceHeader = XmlInvoiceHeader(invoice_id="RE538779")
        parsed: XmlInvoiceHeader = get_xml_header(
            xml_text=xml_text, xml_invoice_data=header, logger=Mock()
        )
        self.assertEqual(parsed.invoice_number, "RE538779")
        self.assertEqual(parsed.iban, IBAN)
        self.assertEqual(parsed.order_id, "SIXT-000000373840")
        self.assertEqual(parsed.invoice_amount, Decimal("101.89"))
        self.assertEqual(parsed.total_amount, Decimal("101.89"))
        self.assertEqual(parsed.total_tax_amount, Decimal("0.00"))
        self.assertEqual(parsed.currency, "EUR")

    def test_vendor_data_uses_french_buyer_vat(self) -> None:
        xml_text: str = self._xml()
        vendor_data, _vendor = get_einvoice_vendor_data(
            invoice_id="RE538779", xml_text=xml_text, logger=Mock()
        )
        self.assertEqual(vendor_data["buyer_name"], "Sixt SAS")
        self.assertEqual(vendor_data["buyer_vat_id"], BUYER_VAT_ID)
        self.assertEqual(vendor_data["buyer_country_billing"], "FR")
        self.assertEqual(vendor_data["seller_name"], "products & more GmbH")
        self.assertEqual(vendor_data["seller_vat_id"], SELLER_VAT_ID)
        self.assertEqual(vendor_data["seller_iban"], IBAN)
        self.assertEqual(vendor_data["payment_means"][0]["AccountID"], IBAN)

    def test_parse_upload_assigns_french_buyer(self) -> None:
        xml_text: str = self._xml()
        result: InvoiceParseResponse = InvoiceService().parse_upload(
            filename="RE538779_sixt_sas.xml",
            content=xml_text.encode("utf-8"),
        )
        self.assertIsNotNone(result.buyer)
        assert result.buyer is not None
        self.assertEqual(result.buyer.name, "Sixt SAS")
        self.assertEqual(result.buyer.vat_id, BUYER_VAT_ID)
        self.assertIsNotNone(result.seller)
        assert result.seller is not None
        self.assertEqual(result.seller.vat_id, SELLER_VAT_ID)
        self.assertEqual(result.seller.iban, IBAN)
        self.assertEqual(result.invoice_number, "RE538779")


if __name__ == "__main__":
    unittest.main()
