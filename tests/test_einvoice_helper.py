import unittest
from .test_helper import xml_test_header_order_930, xml_test_header_kst
from scr.helper_functions.einvoice_helper import string_to_float, find_data_with_regex, find_data_within_element, \
    find_data_within_element_with_len, get_xml_tree
from xml.etree.ElementTree import Element


class TestXmlParserHeader(unittest.TestCase):
    def test_string_to_float_comma(self):
        string_value: str = "12,012"
        float_value: float = string_to_float(string_value)
        self.assertEqual(12.012, float_value)

    def test_string_to_float_without_comma(self):
        string_value: str = "12012"
        float_value: float = string_to_float(string_value)
        self.assertEqual(12012.0, float_value)

    def test_string_to_float_without_dot(self):
        string_value: str = "12012.02"
        float_value: float = string_to_float(string_value)
        self.assertEqual(12012.02, float_value)

    def test_find_data_with_regex(self):
        xml_tree: Element = get_xml_tree(xml_test_header_order_930)
        xml_supplier_data: Element = xml_tree.find("./SupplyChainTradeTransaction")
        order_id:str = find_data_with_regex(xml_supplier_data, "930\d{7}|960\d{7}")
        self.assertEqual("9307162373", order_id)

    def test_find_data_find_data_within_element(self):
        xml_tree: Element = get_xml_tree(xml_test_header_order_930)
        xml_exchanged_document: Element = xml_tree.find("./ExchangedDocument")
        tags_to_search_invoice_number: list = ['./ID']
        invoice_number: str = find_data_within_element(xml_exchanged_document,
                                                                        tags_to_search_invoice_number)
        self.assertEqual("22247", invoice_number)

    def test_find_data_find_data_within_element_with_len_None(self):
        xml_tree: Element = get_xml_tree(xml_test_header_order_930)
        xml_supplier_data: Element = xml_tree.find("./SupplyChainTradeTransaction")
        tags_to_search_iban: list = ['./ApplicableHeaderTradeAgreement/BuyerTradeParty/ID',
                                     './ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementPaymentMeans/PayeePartyCreditorFinancialAccount/IBANID']
        iban = find_data_within_element_with_len(xml_supplier_data, tags_to_search_iban, 22).replace(" ","") if find_data_within_element_with_len(
            xml_supplier_data, tags_to_search_iban, 22) else None

        self.assertEqual(None, iban)

    def test_find_data_find_data_within_element_with_len_IBAN(self):
        xml_tree: Element = get_xml_tree(xml_test_header_kst)
        xml_supplier_data: Element = xml_tree.find("./SupplyChainTradeTransaction")
        tags_to_search_iban: list = ['./ApplicableHeaderTradeAgreement/BuyerTradeParty/ID',
                                     './ApplicableHeaderTradeSettlement/SpecifiedTradeSettlementPaymentMeans/PayeePartyCreditorFinancialAccount/IBANID']
        iban = find_data_within_element_with_len(xml_supplier_data, tags_to_search_iban, 22).replace(" ","") if find_data_within_element_with_len(
            xml_supplier_data, tags_to_search_iban, 22) else None

        self.assertEqual('DE04700202700062004312', iban)


if __name__ == '__main__':
    unittest.main()
