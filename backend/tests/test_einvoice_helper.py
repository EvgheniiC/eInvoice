import os
import unittest
from xml.etree.ElementTree import Element

from app.helper_functions.einvoice_helper import (
    string_to_float,
    find_data_with_regex,
    find_data_within_element,
    find_data_within_element_with_len,
    get_xml_tree,
    read_xml_file_to_str,
    is_zugpferd_pdf,
    find_tax_data,
    get_tags_from_json,
    build_description_from_item,
)


class TestEinvoiceHelper(unittest.TestCase):
    def test_string_to_float_comma(self) -> None:
        self.assertEqual(12.012, string_to_float("12,012"))

    def test_string_to_float_without_comma(self) -> None:
        self.assertEqual(12012.0, string_to_float("12012"))

    def test_string_to_float_with_dot(self) -> None:
        self.assertEqual(12012.02, string_to_float("12012.02"))

    def test_find_data_with_regex(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/xml_test_header_order_ref.xml")
        xml_tree: Element = get_xml_tree(xml_text)
        xml_supplier_data: Element = xml_tree.find("./SupplyChainTradeTransaction")
        order_id: str = find_data_with_regex(xml_supplier_data, r"930\d{7}|960\d{7}")
        self.assertEqual("9307162373", order_id)

    def test_find_data_within_element_invoice_number(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/xml_test_header_order_ref.xml")
        xml_tree: Element = get_xml_tree(xml_text)
        xml_exchanged_document: Element = xml_tree.find("./ExchangedDocument")
        invoice_number: str = find_data_within_element(xml_exchanged_document, ["./ID"])
        self.assertEqual("22247", invoice_number)

    def test_find_iban_length_22(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/xml_test_header_order_ref.xml")
        xml_tree: Element = get_xml_tree(xml_text)
        xml_supplier_data: Element = xml_tree.find("./SupplyChainTradeTransaction")
        tags: list = [
            "./ApplicableHeaderTradeAgreement/BuyerTradeParty/ID",
            "./ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementPaymentMeans/"
            "PayeePartyCreditorFinancialAccount/IBANID",
        ]
        iban_raw = find_data_within_element_with_len(xml_supplier_data, tags, 22)
        iban = iban_raw.replace(" ", "") if iban_raw else None
        self.assertEqual("DE24590501010074280249", iban)

    def test_is_zugpferd_pdf_false(self) -> None:
        path: str = os.path.dirname(os.path.abspath(__file__)) + "/pdf_files/notEinvoiceFormat.pdf"
        self.assertEqual(False, is_zugpferd_pdf(path))

    def test_is_zugpferd_pdf_true(self) -> None:
        path: str = os.path.dirname(os.path.abspath(__file__)) + "/pdf_files/RE_202512245.pdf"
        self.assertEqual(True, is_zugpferd_pdf(path))

    def test_find_tax_data(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/buyer_vat_id_sample.xml")
        xml_tree: Element = get_xml_tree(xml_text)
        tags: list = get_tags_from_json("tags_to_search_tax_amount1")
        tax_amount: dict = find_tax_data(xml_tree, tags, "tax_amount")
        self.assertEqual(
            {
                "tax_amount1": "1225",
                "tax_amount2": "0",
                "tax_amount3": None,
                "tax_amount4": None,
                "tax_amount5": None,
            },
            tax_amount,
        )

    def test_build_description_from_item_ubl(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/additional_item_properties.xml")
        self.assertIsNotNone(xml_text)
        xml_tree: Element = get_xml_tree(xml_text)
        invoice_line = xml_tree.find(".//InvoiceLine")
        self.assertIsNotNone(invoice_line)
        result = build_description_from_item(invoice_line)
        self.assertIsNotNone(result)
        self.assertIn("Marque de véhicule", result)

    def test_build_description_placeholder_uses_description(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/placeholder_item_name.xml")
        xml_tree: Element = get_xml_tree(xml_text)
        invoice_line = xml_tree.find(".//InvoiceLine")
        self.assertIsNotNone(invoice_line)
        result = build_description_from_item(invoice_line)
        self.assertEqual(result, "OAPP DEPOT")


if __name__ == "__main__":
    unittest.main()
