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
            (Decimal("575.61"), Decimal("575.61"), Decimal("130.66"), Decimal("18.50")),
            (Decimal("13.18"), Decimal("13.18"), Decimal("1.88"), Decimal("12.50")),
            (Decimal("88.52"), Decimal("88.52"), Decimal("12.64"), Decimal("12.50")),
            (Decimal("13.32"), Decimal("13.32"), Decimal("10.26"), Decimal("43.50")),
        ]
        for position, (unit, line_net, amount, percent) in zip(positions, expected):
            self.assertEqual(position["single_net_price"], unit)
            self.assertEqual(position["total_net_price"], line_net)
            self.assertEqual(position["single_net_price"] * position["quantity"], line_net)
            self.assertEqual(position["discount_amount"], amount)
            self.assertEqual(position["discount_percent"], percent)
        self.assertEqual(data.invoice_number, "112008206")
        self.assertEqual(data.invoice_amount, Decimal("690.63"))
        self.assertEqual(data.total_tax_amount, Decimal("131.22"))
        self.assertEqual(data.total_amount, Decimal("821.85"))

    def test_ubl_line_discounts_invoice_112008208(self) -> None:
        fixture: str = "xml_files/112008208_babelsberg.xml"
        xml_text: Optional[str] = read_xml_file_to_str(fixture)
        if not xml_text:
            self.skipTest(f"missing local fixture: {fixture}")
        data: XmlInvoiceHeader = self._parse(fixture)
        positions: List[dict] = data.get_positions_map()
        self.assertEqual(len(positions), 15)
        expected: List[Tuple[str, Decimal, Decimal]] = [
            ("DICHTUNG", Decimal("41.61"), Decimal("5.94")),
            ("FUEHRUNG", Decimal("14.18"), Decimal("2.02")),
            ("FUEHRUNG", Decimal("14.18"), Decimal("2.02")),
            ("VERKLEID.", Decimal("341.25"), Decimal("48.75")),
            ("FUEHRUNG", Decimal("13.66"), Decimal("1.95")),
            ("FUEHRUNG", Decimal("13.66"), Decimal("1.95")),
            ("VERKLEID.", Decimal("525.00"), Decimal("75.00")),
            ("STREBE", Decimal("21.88"), Decimal("3.12")),
            ("STREBE", Decimal("21.88"), Decimal("3.12")),
            ("DICHTUNG", Decimal("18.17"), Decimal("2.59")),
            ("DAEMPFUNG", Decimal("5.87"), Decimal("0.84")),
            ("RAHMEN", Decimal("1622.25"), Decimal("231.75")),
            ("TUER", Decimal("1105.27"), Decimal("157.90")),
            ("ABDECKUNG", Decimal("4.67"), Decimal("0.67")),
            ("LEISTE", Decimal("23.63"), Decimal("3.37")),
        ]
        line_sum: Decimal = Decimal("0")
        for position, (name, line_net, amount) in zip(positions, expected):
            self.assertIn(name, position["position_text"])
            self.assertEqual(position["quantity"], Decimal("1.0000"))
            self.assertEqual(position["single_net_price"], line_net)
            self.assertEqual(position["total_net_price"], line_net)
            self.assertEqual(position["discount_amount"], amount)
            self.assertEqual(position["discount_percent"], Decimal("12.50"))
            line_sum += line_net
        self.assertEqual(line_sum, Decimal("3787.16"))
        self.assertEqual(data.invoice_number, "112008208")
        self.assertEqual(data.invoice_amount, Decimal("3787.16"))
        self.assertEqual(data.total_tax_amount, Decimal("719.56"))
        self.assertEqual(data.total_amount, Decimal("4506.72"))


if __name__ == "__main__":
    unittest.main()
