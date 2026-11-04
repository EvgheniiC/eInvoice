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

FIXTURE: str = "xml_files/FR6DFJXABEY_amazon_business_eu.xml"
SELLER_NAME: str = "Amazon Business EU S.à.r.l, Succursale Française"
SELLER_VAT_ID: str = "FR78843272238"
SELLER_STREET: str = "67 Boulevard du General Leclerc"
BUYER_NAME: str = "Sixt SAS"
BUYER_VAT_ID: str = "FR74411207012"
BUYER_STREET: str = "EuroAirport Aeroport de Basel-Mulhouse-Freiburg"
DELIVERY_NAME: str = "Cecilia Vicente SIXT +33478189201"
DELIVERY_STREET: str = "8 avenue Pompidou"
IBAN: str = "GB04DEUT40508122660212"
ORDER_ID: str = "SIXT-000000386209"


class TestAmazonBusinessEuAddresses(unittest.TestCase):
    """UBL invoice FR6DFJXABEY: seller, billing and delivery parties, plus header notes."""

    def _xml(self) -> str:
        xml_text: Optional[str] = read_xml_file_to_str(FIXTURE)
        self.assertIsNotNone(xml_text)
        assert xml_text is not None
        return xml_text

    def test_header_reads_invoice_and_order(self) -> None:
        xml_text: str = self._xml()
        header: XmlInvoiceHeader = XmlInvoiceHeader(invoice_id="FR6DFJXABEY")
        parsed: XmlInvoiceHeader = get_xml_header(
            xml_text=xml_text, xml_invoice_data=header, logger=Mock()
        )
        self.assertEqual(parsed.invoice_number, "FR6DFJXABEY")
        self.assertEqual(parsed.order_id, ORDER_ID)
        self.assertEqual(parsed.invoice_amount, Decimal("7705.8"))
        self.assertEqual(parsed.total_amount, Decimal("9246.96"))
        self.assertEqual(parsed.total_tax_amount, Decimal("1541.16"))
        self.assertEqual(parsed.currency, "EUR")

    def test_vendor_billing_and_delivery_parties(self) -> None:
        xml_text: str = self._xml()
        vendor_data, _vendor = get_einvoice_vendor_data(
            invoice_id="FR6DFJXABEY", xml_text=xml_text, logger=Mock()
        )
        self.assertEqual(vendor_data["seller_name"], SELLER_NAME)
        self.assertEqual(vendor_data["seller_street"], SELLER_STREET)
        self.assertEqual(vendor_data["seller_postcode"], "92110")
        self.assertEqual(vendor_data["seller_city"], "Clichy")
        self.assertEqual(vendor_data["seller_country"], "FR")
        self.assertEqual(vendor_data["seller_vat_id"], SELLER_VAT_ID)
        self.assertEqual(vendor_data["seller_iban"], IBAN)

        self.assertEqual(vendor_data["buyer_name_billing"], BUYER_NAME)
        self.assertEqual(vendor_data["buyer_street_billing"], BUYER_STREET)
        self.assertEqual(vendor_data["buyer_postcode_billing"], "68300")
        self.assertEqual(vendor_data["buyer_city_billing"], "Saint-Louis")
        self.assertEqual(vendor_data["buyer_country_billing"], "FR")
        self.assertEqual(vendor_data["buyer_vat_id"], BUYER_VAT_ID)

        self.assertEqual(vendor_data["buyer_name_delivery"], DELIVERY_NAME)
        self.assertEqual(vendor_data["buyer_street_delivery"], DELIVERY_STREET)
        self.assertEqual(vendor_data["buyer_postcode_delivery"], "69003")
        self.assertEqual(vendor_data["buyer_city_delivery"], "Lyon")
        self.assertEqual(vendor_data["buyer_country_delivery"], "FR")

        notes: Optional[str] = vendor_data["buyer_notes"]
        self.assertIsNotNone(notes)
        assert notes is not None
        self.assertIn("Albane Cusin", notes)
        self.assertIn(f"PONumber: {ORDER_ID}", notes)
        self.assertIn("#AAB# Aucun escompte accordé", notes)
        self.assertNotIn("Paiement dû à Amazon", notes)

    def test_parse_upload_assigns_seller_and_buyer(self) -> None:
        xml_text: str = self._xml()
        result: InvoiceParseResponse = InvoiceService().parse_upload(
            filename="FR6DFJXABEY_amazon_business_eu.xml",
            content=xml_text.encode("utf-8"),
        )
        self.assertIsNotNone(result.seller)
        assert result.seller is not None
        self.assertEqual(result.seller.name, SELLER_NAME)
        self.assertEqual(result.seller.vat_id, SELLER_VAT_ID)
        self.assertEqual(result.seller.iban, IBAN)
        self.assertEqual(
            result.seller.address,
            "67 Boulevard du General Leclerc, 92110 Clichy, FR",
        )
        self.assertIsNotNone(result.buyer)
        assert result.buyer is not None
        self.assertEqual(result.buyer.name, BUYER_NAME)
        self.assertEqual(result.buyer.vat_id, BUYER_VAT_ID)
        self.assertEqual(
            result.buyer.address,
            "EuroAirport Aeroport de Basel-Mulhouse-Freiburg, 68300 Saint-Louis, FR",
        )
        self.assertEqual(result.invoice_number, "FR6DFJXABEY")


if __name__ == "__main__":
    unittest.main()
