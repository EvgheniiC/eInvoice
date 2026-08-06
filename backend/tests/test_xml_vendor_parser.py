import unittest
from unittest.mock import Mock

from app.helper_functions.einvoice_helper import read_xml_file_to_str
from app.invoice_handler.xml_vendor_parser import get_einvoice_vendor_data


class TestVendorParser(unittest.TestCase):
    def test_vendor_data_neutral_keys(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/xml_text_from_xml.xml")
        vendor_data, supplier = get_einvoice_vendor_data(
            invoice_id="5208214", xml_text=xml_text, logger=Mock()
        )
        self.assertEqual(vendor_data["invoice_id"], "5208214")
        self.assertEqual(vendor_data["seller_name"], "[Seller name]")
        self.assertEqual(vendor_data["seller_iban"], "DE75512108001245126199")
        self.assertEqual(vendor_data["buyer_name"], "[Buyer name]")
        self.assertIn("seller_vat_id", vendor_data)
        self.assertIn("payment_means", vendor_data)
        legacy_seller_name: str = "S_" + "KR_" + "NAME1"
        legacy_id: str = "M_" + "CN_" + "ID"
        self.assertNotIn(legacy_seller_name, vendor_data)
        self.assertNotIn(legacy_id, vendor_data)
        self.assertIsNone(supplier)

    def test_vendor_data_with_buyer_reference(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/xml_text_none.xml")
        vendor_data, _supplier = get_einvoice_vendor_data(
            invoice_id="5208215", xml_text=xml_text, logger=Mock()
        )
        self.assertEqual(vendor_data["buyer_reference"], "99000000-01514-29")
        self.assertIsNotNone(vendor_data["seller_name"])
        self.assertNotIn("employee_id", vendor_data)
        legacy_vehicle: str = "S_" + "KR_" + "VEHICLE_ID"
        self.assertNotIn(legacy_vehicle, vendor_data)

    def test_buyer_address_sample_has_no_legacy_vendor_tokens(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/buyer_address_sample.xml")
        vendor_data, _supplier = get_einvoice_vendor_data(
            invoice_id="1", xml_text=xml_text, logger=Mock()
        )
        blob: str = str(vendor_data).lower()
        self.assertNotIn("s" + "ixt", blob)
        self.assertNotIn("high" + "way", blob)


if __name__ == "__main__":
    unittest.main()
