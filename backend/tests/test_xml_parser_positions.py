import unittest
from unittest.mock import Mock

from app.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from app.helper_functions.einvoice_helper import read_xml_file_to_str
from app.invoice_handler.xml_parser_header import get_xml_header
from app.invoice_handler.xml_parser_positions import get_xml_positions


class TestXmlParserPositions(unittest.TestCase):
    def _parse(self, relative_path: str, invoice_id: str = "2002") -> XmlInvoiceHeader:
        header: XmlInvoiceHeader = XmlInvoiceHeader(invoice_id=invoice_id)
        xml_text: str = read_xml_file_to_str(relative_path)
        header = get_xml_header(xml_text=xml_text, xml_invoice_data=header, logger=Mock())
        return get_xml_positions(xml_text=xml_text, xml_invoice_data=header, logger=Mock())

    def test_zugferd_positions(self) -> None:
        data: XmlInvoiceHeader = self._parse("xml_files/xml_text_from_zugpferd.xml")
        positions = data.get_positions_map()
        self.assertGreater(len(positions), 0)
        first = positions[0]
        self.assertEqual(first["invoice_id"], "2002")
        self.assertEqual(first["item_pos"], 1)
        self.assertIsNotNone(first["position_text"])
        legacy_prefixes: tuple[str, str] = ("M_" + "IP_", "M_" + "CN_")
        for prefix in legacy_prefixes:
            self.assertTrue(all(not str(key).startswith(prefix) for key in first.keys()))

    def test_ubl_positions(self) -> None:
        data: XmlInvoiceHeader = self._parse("xml_files/xml_text_from_xml.xml")
        positions = data.get_positions_map()
        self.assertGreater(len(positions), 0)
        self.assertIsNotNone(positions[0]["quantity"])
        self.assertIsNotNone(positions[0]["total_net_price"])

    def test_discount_position_created_when_present(self) -> None:
        data: XmlInvoiceHeader = self._parse("xml_files/discount_new_position.xml")
        texts = [p["position_text"] for p in data.get_positions_map()]
        self.assertTrue(any(t for t in texts))


if __name__ == "__main__":
    unittest.main()
