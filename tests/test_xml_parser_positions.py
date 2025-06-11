import unittest
from scr.invoice_handler.xml_parser_positions import get_xml_positions
from .test_helper import xml_text_none, xml_text_from_zugpferd, xml_test_iban_none, xml_test_header, \
    xml_test_header_order_930, xml_test_header_kst
from scr.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from unittest.mock import Mock


class TestXmlParserHeader(unittest.TestCase):
    def test_get_xml_header_with_orderid(self):
        m_cn_id = "6983825"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_invoice_positions = get_xml_positions(m_cn_id=xml_invoice_header.m_cn_id, xml_text=xml_test_header_kst,
                                                  xml_invoice_data=xml_invoice_header, logger=Mock())

        print(xml_invoice_positions.get_xml_postions_map())
        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 1,
                           'M_IP_POSITIONSTEXT': 'Arbeitspreis', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.09995, 'M_IP_TOTALNETPRICE': 135.13, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 2,
                           'M_IP_POSITIONSTEXT': 'Stromsteuer', 'M_IP_QUANTITY': 1352.0, 'M_IP_SINGLENETPRICE': 0.0205,
                           'M_IP_TOTALNETPRICE': 27.72, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': '',
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '',
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 3,
                           'M_IP_POSITIONSTEXT': 'Arbeitspreis Netz', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.0762, 'M_IP_TOTALNETPRICE': 103.02, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 4,
                           'M_IP_POSITIONSTEXT': 'Leistungspreis Netz', 'M_IP_QUANTITY': 7.0,
                           'M_IP_SINGLENETPRICE': 22.36, 'M_IP_TOTALNETPRICE': 13.29, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 5,
                           'M_IP_POSITIONSTEXT': 'Messkosten', 'M_IP_QUANTITY': 31.0, 'M_IP_SINGLENETPRICE': 98.5,
                           'M_IP_TOTALNETPRICE': 8.37, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': '',
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '',
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 6,
                           'M_IP_POSITIONSTEXT': 'Entgelt fur Messstellenbetrieb,Messung', 'M_IP_QUANTITY': 31.0,
                           'M_IP_SINGLENETPRICE': 330.27, 'M_IP_TOTALNETPRICE': 28.05, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 7,
                           'M_IP_POSITIONSTEXT': 'Kraft-Warme-Kopplung (KWK)', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.00277, 'M_IP_TOTALNETPRICE': 3.75, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 8,
                           'M_IP_POSITIONSTEXT': 'Aufschlag fur besondere Netznutzung', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.01558, 'M_IP_TOTALNETPRICE': 21.06, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 9,
                           'M_IP_POSITIONSTEXT': 'Offshore-Umlage', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.00816, 'M_IP_TOTALNETPRICE': 11.03, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 10,
                           'M_IP_POSITIONSTEXT': 'Konzessionsabgabe Sonderkunde', 'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.0011, 'M_IP_TOTALNETPRICE': 1.49, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''}]
                         )


if __name__ == '__main__':
    unittest.main()
