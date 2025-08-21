import unittest
from scr.invoice_handler.xml_parser_positions import get_xml_positions
from scr.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from unittest.mock import Mock
from scr.helper_functions.einvoice_helper import read_xml_file_to_str


class TestXmlParserHeader(unittest.TestCase):
    def test_get_xml_positions_many_positions(self):
        m_cn_id = "6983825"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_test_header_kst = read_xml_file_to_str('xml_files/xml_test_header_kst.xml')
        xml_invoice_positions = get_xml_positions(xml_text=xml_test_header_kst,
                                                  xml_invoice_data=xml_invoice_header, logger=Mock())

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

    def test_get_xml_positions_bad_positionstext(self):
        m_cn_id = "65478963"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_test_header_order_930 = read_xml_file_to_str('xml_files/xml_test_header_order_930.xml')
        xml_invoice_positions = get_xml_positions(xml_text=xml_test_header_order_930,
                                                  xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 1,
                           'M_IP_POSITIONSTEXT': 'WSS OE 8894354944', 'M_IP_QUANTITY': 1.0,
                           'M_IP_SINGLENETPRICE': 595.36, 'M_IP_TOTALNETPRICE': 595.36, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '8894354944', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 2,
                           'M_IP_POSITIONSTEXT': 'Klebesatz', 'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 33.61,
                           'M_IP_TOTALNETPRICE': 33.61, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': '',
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '',
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 3,
                           'M_IP_POSITIONSTEXT': 'Primer', 'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 15.0,
                           'M_IP_TOTALNETPRICE': 15.0, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': '',
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '',
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 4,
                           'M_IP_POSITIONSTEXT': 'Montage-Arbeitswerte [12AW=1 Std.]', 'M_IP_QUANTITY': 23.5,
                           'M_IP_SINGLENETPRICE': 8.33, 'M_IP_TOTALNETPRICE': 195.76, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 5,
                           'M_IP_POSITIONSTEXT': 'Altglasentsorgung PKW\nBundes- & Landesentsorgungs-\nverordnung / KFZ-Verbundglas',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 4.31, 'M_IP_TOTALNETPRICE': 4.31,
                           'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '',
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 6,
                           'M_IP_POSITIONSTEXT': 'FSP', 'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 5.0,
                           'M_IP_TOTALNETPRICE': 5.0, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': '',
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '',
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 7,
                           'M_IP_POSITIONSTEXT': 'Schadennummer 9074743424', 'M_IP_QUANTITY': 1.0,
                           'M_IP_SINGLENETPRICE': 0.0, 'M_IP_TOTALNETPRICE': 0.0, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 8,
                           'M_IP_POSITIONSTEXT': 'Auftragsnummer 9307162373', 'M_IP_QUANTITY': 1.0,
                           'M_IP_SINGLENETPRICE': 0.0, 'M_IP_TOTALNETPRICE': 0.0, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 9,
                           'M_IP_POSITIONSTEXT': 'Durchgefuhrt am 17.02.25', 'M_IP_QUANTITY': 1.0,
                           'M_IP_SINGLENETPRICE': 0.0, 'M_IP_TOTALNETPRICE': 0.0, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': '', 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''}]
                         )

    def test_get_xml_positions_one_position(self):
        m_cn_id = "65478963"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_text_none = read_xml_file_to_str('xml_files/xml_text_none.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_text_none,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '65478963',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': '',
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': '',
                           'M_IP_POSITIONSTEXT': 'Beschreibung Artikel',
                           'M_IP_QUANTITY': 10.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 1000.0,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 7.0,
                           'M_IP_TOTALNETPRICE': 10000.0,
                           'M_IP_TYP': 'ET'}]
                         )

    # if we got clear XML file
    def test_get_xml_positions_from_xml_file(self):
        m_cn_id = "65478963"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_text_none = read_xml_file_to_str('xml_files/clear_xml_from_gerd.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_text_none,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '65478963',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': '',
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': '',
                           'M_IP_POSITIONSTEXT': 'Softwarepflegeschein 6140414001 / 005',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 48105.0,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 19.0,
                           'M_IP_TOTALNETPRICE': 48105.0,
                           'M_IP_TYP': 'ET'}]
                         )

    # if we got XML file without correctly positions tags
    def test_get_xml_positions_from_xml_file_porscheinformatik(self):
        m_cn_id = "7339081"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xm_positions_false = read_xml_file_to_str('xml_files/xm_positions_false.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xm_positions_false,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),[])

if __name__ == '__main__':
    unittest.main()
