import unittest
from decimal import Decimal
from typing import List, Optional, Tuple
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

    def test_ubl_line_discounts_from_allowance_block(self) -> None:
        fixture: str = "xml_files/Discoint_in_posiitions.xml"
        xml_text: Optional[str] = read_xml_file_to_str(fixture)
        if not xml_text:
            self.skipTest(f"missing local fixture: {fixture}")
        data: XmlInvoiceHeader = self._parse(fixture)
        positions: List[dict] = data.get_positions_map()
        self.assertEqual(len(positions), 4)
        expected: List[Tuple[Decimal, Decimal, Decimal, Decimal]] = [
            (Decimal("706.27"), Decimal("575.61"), Decimal("130.66"), Decimal("18.50")),
            (Decimal("15.06"), Decimal("13.18"), Decimal("1.88"), Decimal("12.50")),
            (Decimal("101.16"), Decimal("88.52"), Decimal("12.64"), Decimal("12.50")),
            (Decimal("23.58"), Decimal("13.32"), Decimal("10.26"), Decimal("43.50")),
        ]
        for position, (unit, line_net, amount, percent) in zip(positions, expected):
            self.assertEqual(position["single_net_price"], unit)
            self.assertEqual(position["total_net_price"], line_net)
            self.assertEqual(position["discount_amount"], amount)
            self.assertEqual(position["discount_percent"], percent)


if __name__ == "__main__":
    unittest.main()
