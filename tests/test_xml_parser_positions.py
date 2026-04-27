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
        print(xml_invoice_positions.get_xml_postions_map())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 1,
                           'M_IP_POSITIONSTEXT': 'Arbeitspreis Zahlpunkt DE00721470565MU000000000000799440 Zahlernummer 21342703',
                           'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.09995, 'M_IP_TOTALNETPRICE': 135.13, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 2,
                           'M_IP_POSITIONSTEXT': 'Stromsteuer Zahlpunkt DE00721470565MU000000000000799440 Zahlernummer 21342703',
                           'M_IP_QUANTITY': 1352.0, 'M_IP_SINGLENETPRICE': 0.0205,
                           'M_IP_TOTALNETPRICE': 27.72, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                           'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 3,
                           'M_IP_POSITIONSTEXT': 'Arbeitspreis Netz Zahlpunkt DE00721470565MU000000000000799440 Zahlernummer 21342703',
                           'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.0762, 'M_IP_TOTALNETPRICE': 103.02, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 4,
                           'M_IP_POSITIONSTEXT': 'Leistungspreis Netz Zahlpunkt DE00721470565MU000000000000799440 Zahlernummer 21342703',
                           'M_IP_QUANTITY': 7.0,
                           'M_IP_SINGLENETPRICE': 22.36, 'M_IP_TOTALNETPRICE': 13.29, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 5,
                           'M_IP_POSITIONSTEXT': 'Messkosten Zahlpunkt DE00721470565MU000000000000799440 Zahlernummer 21342703',
                           'M_IP_QUANTITY': 31.0, 'M_IP_SINGLENETPRICE': 98.5,
                           'M_IP_TOTALNETPRICE': 8.37, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                           'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 6,
                           'M_IP_POSITIONSTEXT': 'Entgelt fur Messstellenbetrieb,Messung Zahlpunkt DE00721470565MU000000000000799440 Zahlernummer 21342703',
                           'M_IP_QUANTITY': 31.0,
                           'M_IP_SINGLENETPRICE': 330.27, 'M_IP_TOTALNETPRICE': 28.05, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 7,
                           'M_IP_POSITIONSTEXT': 'Kraft-Warme-Kopplung (KWK) Zahlpunkt DE00721470565MU000000000000799440 Zahlernummer 21342703',
                           'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.00277, 'M_IP_TOTALNETPRICE': 3.75, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 8,
                           'M_IP_POSITIONSTEXT': 'Aufschlag fur besondere Netznutzung Zahlpunkt DE00721470565MU000000000000799440 Zahlernummer 21342703',
                           'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.01558, 'M_IP_TOTALNETPRICE': 21.06, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 9,
                           'M_IP_POSITIONSTEXT': 'Offshore-Umlage Zahlpunkt DE00721470565MU000000000000799440 Zahlernummer 21342703',
                           'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.00816, 'M_IP_TOTALNETPRICE': 11.03, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '6983825', 'M_IP_ITEMPOS': 10,
                           'M_IP_POSITIONSTEXT': 'Konzessionsabgabe Sonderkunde Zahlpunkt DE00721470565MU000000000000799440 Zahlernummer 21342703',
                           'M_IP_QUANTITY': 1352.0,
                           'M_IP_SINGLENETPRICE': 0.0011, 'M_IP_TOTALNETPRICE': 1.49, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''}]
                         )

    def test_get_xml_positions_HW_5938_description_from_item(self):
        """HW-5938: position description is built from Item Name + all AdditionalItemProperty Name/Value."""
        m_cn_id = "HW5938"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_text = read_xml_file_to_str('xml_files/ergenzungen_HW-5938.xml')
        self.assertIsNotNone(xml_text, "ergenzungen_HW-5938.xml should be readable")
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_text,
            xml_invoice_data=xml_invoice_header, logger=Mock())
        positions = xml_invoice_positions.get_xml_postions_map()
        self.assertGreater(len(positions), 0, "At least one position expected")
        expected_description = (
            "6357AGACMOVZ Marque de véhicule OPEL Modèle de véhicule FRONTERA "
            "Plaque d'immatriculation de véhicule 2 HWV 031 Numéro de châssis de véhicule VXKCSHPY7ST250531 "
            "Kilométrage de véhicule 5281\n6357AGACMOVZ"
        )
        self.assertEqual(positions[0]['M_IP_POSITIONSTEXT'], expected_description)
        self.assertLessEqual(len(positions[0]['M_IP_POSITIONSTEXT']), 1000,
                             "description_text must be at most 1000 characters")

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
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '8894354944', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 2,
                           'M_IP_POSITIONSTEXT': 'Klebesatz', 'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 33.61,
                           'M_IP_TOTALNETPRICE': 33.61, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                           'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 3,
                           'M_IP_POSITIONSTEXT': 'Primer', 'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 15.0,
                           'M_IP_TOTALNETPRICE': 15.0, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                           'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 4,
                           'M_IP_POSITIONSTEXT': 'Montage-Arbeitswerte [12AW=1 Std.]', 'M_IP_QUANTITY': 23.5,
                           'M_IP_SINGLENETPRICE': 8.33, 'M_IP_TOTALNETPRICE': 195.76, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 5,
                           'M_IP_POSITIONSTEXT': 'Altglasentsorgung PKW\nBundes- & Landesentsorgungs-\nverordnung / KFZ-Verbundglas',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 4.31, 'M_IP_TOTALNETPRICE': 4.31,
                           'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 6,
                           'M_IP_POSITIONSTEXT': 'FSP', 'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 5.0,
                           'M_IP_TOTALNETPRICE': 5.0, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                           'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 7,
                           'M_IP_POSITIONSTEXT': 'Schadennummer 9074743424', 'M_IP_QUANTITY': 1.0,
                           'M_IP_SINGLENETPRICE': 0.0, 'M_IP_TOTALNETPRICE': 0.0, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 8,
                           'M_IP_POSITIONSTEXT': 'Auftragsnummer 9307162373', 'M_IP_QUANTITY': 1.0,
                           'M_IP_SINGLENETPRICE': 0.0, 'M_IP_TOTALNETPRICE': 0.0, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 9,
                           'M_IP_POSITIONSTEXT': 'Durchgefuhrt am 17.02.25', 'M_IP_QUANTITY': 1.0,
                           'M_IP_SINGLENETPRICE': 0.0, 'M_IP_TOTALNETPRICE': 0.0, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '65478963', 'M_IP_ITEMPOS': 10,
                           'M_IP_POSITIONSTEXT': 'Rabatt', 'M_IP_QUANTITY': 1, 'M_IP_SINGLENETPRICE': -441.5,
                           'M_IP_TOTALNETPRICE': -441.5, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': None,
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                           'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''}]
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
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': 'RPB',
                           'M_IP_POSITIONSTEXT': 'Bezeichung Artikel Farbe blau Gre XL\nBezeichung Artikel\n456',
                           'M_IP_QUANTITY': 10.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 1000.0,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 7.0,
                           'M_IP_TOTALNETPRICE': 10000.0,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '65478963',
                           'M_IP_ARTICLENUMBER': None,
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 2,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': '',
                           'M_IP_POSITIONSTEXT': 'description_text',
                           'M_IP_QUANTITY': 1,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': -2500.0,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 7.0,
                           'M_IP_TOTALNETPRICE': -2500.0,
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
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'Wartung BPM inspire',
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
        xml_positions_false = read_xml_file_to_str('xml_files/xm_positions_false.xml')

        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions_false,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        positions = xml_invoice_positions.get_xml_postions_map()
        # HW-5938: description is now built from Item Name + AdditionalItemProperty (Name/Value)
        expected_starts = [
            'Auftragsnummer: 9307392455',
            'Kennzeichen: M-ZX 5526',
            'Schadennummer:',
            '2 Rder aus- u.einbauen',
            '2 Bremsscheiben vorn ersetzen',
            'SCHRAUBE',
            'BREMSSCHEI',
            'BREMSBELAG',
            'Ihr Serviceberater, Sven Warczecha, bedankt sich fr Ihren Auftrag',
            '(06) Volkswagen Original Teil  / Zubehr Geprfte Qualitt',
            'Grund der Stornierung: Falsche Auftragsnummer hinterlegt',
        ]
        expected_prices = [
            (0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.75, 22.5), (0.75, 60.0),
            (1.12, 1.1), (107.06, 120.98), (103.0, 58.2), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0),
        ]
        self.assertEqual(len(positions), 11)
        for i, pos in enumerate(positions):
            self.assertTrue(pos['M_IP_POSITIONSTEXT'].startswith(expected_starts[i]),
                            f"Position {i + 1} text should start with {expected_starts[i]!r}")
            self.assertEqual(pos['M_IP_ITEMPOS'], i + 1)
            self.assertEqual(pos['M_IP_SINGLENETPRICE'], expected_prices[i][0])
            self.assertEqual(pos['M_IP_TOTALNETPRICE'], expected_prices[i][1])

    # SWFM-5489
    def test_get_xml_positions_85018982(self):
        m_cn_id = "7339081"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/85018982AutohausBabelsberg.xml')

        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        positions = xml_invoice_positions.get_xml_postions_map()
        expected_prefixes = [
            'Auftragsnummer:9307398735 Schadennummer:9075989566 Kennzeichen:M-FZ 4615 WVGZZZA14SV135590 Huttenstr.50',
            'ABDECKUNG',
            'Ihr Team vom Teiledienst Volkswagen bedankt sich fr den Auftrag',
            'Elektrische Bauteile und Sonderbestellungen sind vom Umtausch / Rckgabe ausgeschlossen.',
            '(04) Original Teile / Zubehr Geprfte Qualitt, auf die Sie sich verlassen knnen.',
        ]
        expected_quantity_price = [(0.0, 0.0, 0.0), (1.0, 111.56, 97.62), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0),
                                   (0.0, 0.0, 0.0)]
        self.assertEqual(len(positions), 5)
        for i, pos in enumerate(positions):
            self.assertTrue(pos['M_IP_POSITIONSTEXT'].startswith(expected_prefixes[i]),
                            f"Position {i + 1} should start with expected prefix")
            self.assertEqual(pos['M_IP_QUANTITY'], expected_quantity_price[i][0])
            self.assertEqual(pos['M_IP_SINGLENETPRICE'], expected_quantity_price[i][1])
            self.assertEqual(pos['M_IP_TOTALNETPRICE'], expected_quantity_price[i][2])

    # SWFM-5489
    def test_get_xml_positions_85018982_part2(self):
        m_cn_id = "7339081"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/85018982_head.xml')

        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        positions = xml_invoice_positions.get_xml_postions_map()
        expected_prefixes = [
            'Auftragsnummer: 9307393345',
            'DISS MELDUNG',
            'GW-ABFRAGE',
            'GFS/GEFHRTE FUNKTION',
            'GFS/GEFHRTE FUNKTION',
            'HV-Ladekabel prfen',
            'Ihr Serviceberaterin, Luisa Krger, bedankt sich fr Ihren Auftrag',
        ]
        expected_qty_price = [
            (0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (1.0, 0.0, 0.0), (20.0, 0.75, 15.0),
            (21.0, 0.75, 15.75), (10.0, 0.75, 7.5), (0.0, 0.0, 0.0),
        ]
        self.assertEqual(len(positions), 7)
        for i, pos in enumerate(positions):
            self.assertTrue(pos['M_IP_POSITIONSTEXT'].startswith(expected_prefixes[i]),
                            f"Position {i + 1} should start with expected prefix")
            self.assertEqual((pos['M_IP_QUANTITY'], pos['M_IP_SINGLENETPRICE'], pos['M_IP_TOTALNETPRICE']),
                             expected_qty_price[i])

    # SWFM-5490
    def test_get_xml_positions_SWFM_5490(self):
        m_cn_id = "7339081"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/xml_text_find_VIN_USTD_SWFM-5490.xml')

        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        positions = xml_invoice_positions.get_xml_postions_map()
        expected_prefixes = [
            'Auftragsnummer:9307398735 Schadennummer:9075989566 Kennzeichen:M-FZ 4615 WVGZZZA14SV135590 Huttenstr.50',
            'ABDECKUNG',
            'Ihr Team vom Teiledienst Volkswagen bedankt sich fr den Auftrag',
            'Elektrische Bauteile und Sonderbestellungen sind vom Umtausch / Rckgabe ausgeschlossen.',
            '(04) Original Teile / Zubehr Geprfte Qualitt, auf die Sie sich verlassen knnen.',
        ]
        expected_quantity_price = [(0.0, 0.0, 0.0), (1.0, 111.56, 97.62), (0.0, 0.0, 0.0), (0.0, 0.0, 0.0),
                                   (0.0, 0.0, 0.0)]
        self.assertEqual(len(positions), 5)
        for i, pos in enumerate(positions):
            self.assertTrue(pos['M_IP_POSITIONSTEXT'].startswith(expected_prefixes[i]),
                            f"Position {i + 1} should start with expected prefix")
            self.assertEqual(pos['M_IP_QUANTITY'], expected_quantity_price[i][0])
            self.assertEqual(pos['M_IP_SINGLENETPRICE'], expected_quantity_price[i][1])
            self.assertEqual(pos['M_IP_TOTALNETPRICE'], expected_quantity_price[i][2])

    # HW-5648 SAP BE
    def test_get_xml_positions_HW_5648(self):
        m_cn_id = "5209222"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/xml_text_SAP_BE_HW_5648.xml')

        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        positions = xml_invoice_positions.get_xml_postions_map()
        self.assertEqual(len(positions), 3)
        for i, pos in enumerate(positions):
            self.assertTrue(pos['M_IP_POSITIONSTEXT'].startswith('item name'),
                            f"Position {i + 1} should start with 'item name'")
        self.assertEqual(positions[0]['M_IP_QUANTITY'], 10.0)
        self.assertEqual(positions[0]['M_IP_SINGLENETPRICE'], 410.0)
        self.assertEqual(positions[0]['M_IP_TOTALNETPRICE'], 4000.0)
        self.assertEqual(positions[1]['M_IP_ORDERPOSID'], '124')
        self.assertEqual(positions[1]['M_IP_SINGLENETPRICE'], 200.0)
        self.assertEqual(positions[2]['M_IP_TOTALNETPRICE'], 900.0)

    # HW-5851
    def test_get_xml_positions_HW_5851(self):
        m_cn_id = "5209222"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/cc_budget_and_another.xml')

        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '5209222',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': '41872',
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': '* AIRLINE',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 203.09,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 0.0,
                           'M_IP_TOTALNETPRICE': 203.09,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '5209222',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': '41872',
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 2,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'Egencia fees Air Eur On line transaction (1)',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 7.0,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 0.0,
                           'M_IP_TOTALNETPRICE': 7.0,
                           'M_IP_TYP': 'ET'}]
                         )

    # HW-5851
    def test_get_xml_additional_positions_HW_5851(self):
        m_cn_id = "5209222"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/additional_description_pos.xml')

        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        positions = xml_invoice_positions.get_xml_postions_map()
        expected_prefixes = [
            '330506584',
            '331388481',
            '331976743',
        ]
        expected_total = [23.84, 25.44, 23.84]
        self.assertEqual(len(positions), 3)
        for i, pos in enumerate(positions):
            self.assertTrue(pos['M_IP_POSITIONSTEXT'].startswith(expected_prefixes[i]),
                            f"Position {i + 1} should start with expected prefix")
            self.assertEqual(pos['M_IP_TOTALNETPRICE'], expected_total[i])
            self.assertEqual(pos['M_IP_TAXRATE'], 21.0)

    # HW-5891
    def test_get_xml_negative_quantity(self):
        m_cn_id = "8026941"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/negative_quantity.xml')

        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '8026941',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'Forfaitaire bijdrage werknemers volgens pro rata '
                                                 'regeling',
                           'M_IP_QUANTITY': 11.17,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 97.67,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 0.0,
                           'M_IP_TOTALNETPRICE': 1090.97,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8026941',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 2,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'Reeds gefactureerde " Employee Assistance Program "',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 49.5,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 0.0,
                           'M_IP_TOTALNETPRICE': -49.5,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8026941',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 3,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'Employee Assistance Program ( New Basic ) voor 12 '
                                                 'maanden',
                           'M_IP_QUANTITY': 14.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 4.95,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 0.0,
                           'M_IP_TOTALNETPRICE': 69.3,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8026941',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 4,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'Reeds gefactureerde " forfaitaire bijdrage per '
                                                 'werknemer "',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 976.7,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 0.0,
                           'M_IP_TOTALNETPRICE': -976.7,
                           'M_IP_TYP': 'ET'}]
                         )

    # HW-5945
    def test_get_xml_negative_positions(self):
        m_cn_id = "8089021"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/negative_positions_HW-5945.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        positions = xml_invoice_positions.get_xml_postions_map()
        expected_prefixes = [
            'DSL - Korting lange termijn',
            'DSL - Korting lange termijn',
            'Premium SLA.',
            'Internet Pro+',
            'Call Connect Dect Ip-Phone handset W52H',
            'Call Connect Dect Ip-Phone set W52P',
            'Call Connect Dect Ip-Phone set W52P',
            'Call Connect Executive Ip-Phone T48G',
            'Forum fanless 8p 10/100 switch with PoE',
        ]
        expected_totals = [-1.0, -9.69, 10.0, 96.9, 3.29, 4.52, 4.52, 9.47, 6.49]
        self.assertEqual(len(positions), 9)
        for i, pos in enumerate(positions):
            self.assertTrue(pos['M_IP_POSITIONSTEXT'].startswith(expected_prefixes[i]),
                            f"Position {i + 1} should start with expected prefix")
            self.assertEqual(pos['M_IP_TOTALNETPRICE'], expected_totals[i])

    # HW-5945
    def test_get_xml_add_positions(self):
        m_cn_id = "8004483"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/AllowanceTotalAmount_HW-5945.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None, 'M_CN_INVOICEID': '8004483', 'M_IP_ITEMPOS': 1,
                           'M_IP_POSITIONSTEXT': 'Meldkamerabonnement (inclusief onderhoudspakket) 01.02.2026 - 28.02.2026',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 60.54, 'M_IP_TOTALNETPRICE': 60.54,
                           'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8004483', 'M_IP_ITEMPOS': 2,
                           'M_IP_POSITIONSTEXT': 'Meldkamerabonnement (inclusief onderhoudspakket) 01.02.2026 - 28.02.2026',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 64.87, 'M_IP_TOTALNETPRICE': 64.87,
                           'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8004483', 'M_IP_ITEMPOS': 3,
                           'M_IP_POSITIONSTEXT': 'Meldkamerabonnement (inclusief onderhoudspakket) 01.02.2026 - 28.02.2026',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 72.41, 'M_IP_TOTALNETPRICE': 72.41,
                           'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8004483', 'M_IP_ITEMPOS': 4,
                           'M_IP_POSITIONSTEXT': 'Meldkamerabonnement (inclusief onderhoudspakket) 01.02.2026 - 28.02.2026',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 60.54, 'M_IP_TOTALNETPRICE': 60.54,
                           'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8004483', 'M_IP_ITEMPOS': 5,
                           'M_IP_POSITIONSTEXT': 'Meldkamerabonnement (inclusief onderhoudspakket) 01.02.2026 - 28.02.2026',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 60.54, 'M_IP_TOTALNETPRICE': 60.54,
                           'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8004483', 'M_IP_ITEMPOS': 6,
                           'M_IP_POSITIONSTEXT': 'Meldkamerabonnement (inclusief onderhoudspakket) 01.02.2026 - 28.02.2026',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 63.78, 'M_IP_TOTALNETPRICE': 63.78,
                           'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8004483', 'M_IP_ITEMPOS': 7,
                           'M_IP_POSITIONSTEXT': 'Meldkamerabonnement (inclusief onderhoudspakket) 01.02.2026 - 28.02.2026',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 60.54, 'M_IP_TOTALNETPRICE': 60.54,
                           'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8004483', 'M_IP_ITEMPOS': 8,
                           'M_IP_POSITIONSTEXT': 'Meldkamerabonnement (inclusief onderhoudspakket) 01.02.2026 - 28.02.2026',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 57.46, 'M_IP_TOTALNETPRICE': 57.46,
                           'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8004483', 'M_IP_ITEMPOS': 9,
                           'M_IP_POSITIONSTEXT': 'Meldkamerabonnement (inclusief onderhoudspakket) 01.02.2026 - 28.02.2026',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 57.3, 'M_IP_TOTALNETPRICE': 57.3,
                           'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8004483', 'M_IP_ITEMPOS': 10,
                           'M_IP_POSITIONSTEXT': 'description_text', 'M_IP_QUANTITY': 1, 'M_IP_SINGLENETPRICE': -61.33,
                           'M_IP_TOTALNETPRICE': -61.33, 'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': None,
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': '',
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''}]

                         )

    def test_get_xml_add_positions_discount(self):
        m_cn_id = "8041064"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/discount_new_position.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None, 'M_CN_INVOICEID': '8041064', 'M_IP_ITEMPOS': 1,
                           'M_IP_POSITIONSTEXT': 'Water 19L (2026-01-23 a 2026-01-23)', 'M_IP_QUANTITY': 8.0,
                           'M_IP_SINGLENETPRICE': 13.13, 'M_IP_TOTALNETPRICE': 105.04, 'M_IP_TAXRATE': 6.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''}, {'M_CN_ID': None, 'M_CN_INVOICEID': '8041064', 'M_IP_ITEMPOS': 2,
                                                'M_IP_POSITIONSTEXT': 'Milk (200caps X 7g) (2026-01-23 a 2026-01-23)',
                                                'M_IP_QUANTITY': 2.0, 'M_IP_SINGLENETPRICE': 25.6,
                                                'M_IP_TOTALNETPRICE': 51.2, 'M_IP_TAXRATE': 6.0,
                                                'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                                                'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                                                'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                                                'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                                                'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                                                'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                                                'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8041064', 'M_IP_ITEMPOS': 3,
                           'M_IP_POSITIONSTEXT': 'Packaging charge 18,9L bottle', 'M_IP_QUANTITY': 8.0,
                           'M_IP_SINGLENETPRICE': 0.27, 'M_IP_TOTALNETPRICE': 2.16, 'M_IP_TAXRATE': 6.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''}, {'M_CN_ID': None, 'M_CN_INVOICEID': '8041064', 'M_IP_ITEMPOS': 4,
                                                'M_IP_POSITIONSTEXT': 'Kilometer charge', 'M_IP_QUANTITY': 1.0,
                                                'M_IP_SINGLENETPRICE': 1.5, 'M_IP_TOTALNETPRICE': 1.5,
                                                'M_IP_TAXRATE': 6.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                                                'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                                                'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                                                'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                                                'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                                                'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                                                'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8041064', 'M_IP_ITEMPOS': 5,
                           'M_IP_POSITIONSTEXT': 'Empties water 18.9L', 'M_IP_QUANTITY': 2.0,
                           'M_IP_SINGLENETPRICE': 12.8, 'M_IP_TOTALNETPRICE': -25.6, 'M_IP_TAXRATE': 0.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''}]
                         )

    # HW-5979
    def test_get_xml_minus_in_positions(self):
        m_cn_id = "8117534"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/minus_in_positions_HW-5979.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '8117534',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'ARBEIDSLOON WERKPLAATS VIN ZCFCE35A30D789845 license '
                                                 'plate 2HME510 mileage 26223\n'
                                                 'ARBEIDSLOON WERKPLAATS',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 391.98,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 391.98,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8117534',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 2,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'GLOEILAMP VIN ZCFCE35A30D789845 license plate 2HME510 '
                                                 'mileage 26223\n'
                                                 'GLOEILAMP',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 1.14,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 1.03,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8117534',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 3,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'ARBEIDSLOON WERKPLAATS VIN ZCFCE35A30D789845 license '
                                                 'plate 2HME510 mileage 26223\n'
                                                 'ARBEIDSLOON WERKPLAATS',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 391.98,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': -391.98,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8117534',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 4,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'ARBEIDSLOON WERKPLAATS VIN ZCFCE35A30D789845 license '
                                                 'plate 2HME510 mileage 26223\n'
                                                 'ARBEIDSLOON WERKPLAATS',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 18.8,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 18.8,
                           'M_IP_TYP': 'ET'}]
                         )

    # HW-5979
    def test_get_xml_minus_in_positions_2(self):
        m_cn_id = "8139641"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/minus_pos.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '8139641',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'T 180 L2\n42086513_0001',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 39157.0,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 39157.0,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8139641',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 2,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'REMISE VEHICULE\nREMISE',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 12257.0,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': -12257.0,
                           'M_IP_TYP': 'ET'}]
                         )

    # HW-6052
    def test_get_xml_minus_in_positions_3(self):
        m_cn_id = "8139641"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/no_text_position.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None, 'M_CN_INVOICEID': '8139641', 'M_IP_ITEMPOS': 1,
                           'M_IP_POSITIONSTEXT': 'OAPP DEPOT',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 24598.0, 'M_IP_TOTALNETPRICE': 24598.0,
                           'M_IP_TAXRATE': 21.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''}]
                         )

    # HW-5954
    def test_get_xml_first_FR(self):
        m_cn_id = "8139641"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/first_frankreich.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '8139641',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': '245/45R19 102Y HANKOOK',
                           'M_IP_QUANTITY': 2.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 141.0,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 20.0,
                           'M_IP_TOTALNETPRICE': 282.0,
                           'M_IP_TYP': 'ET'}]
                         )

    # HW-6170
    def test_get_xml_HW_6170(self):
        m_cn_id = "8139641"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/HW-6170.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '8139641',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': '00010',
                           'M_IP_POSITIONSTEXT': 'PORTIERSPIEGEL RE\n1093324104',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 415.95,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 415.95,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8139641',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 2,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': '00020',
                           'M_IP_POSITIONSTEXT': 'SPIEGELGLAS RE\n1093324124',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 114.97,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 114.97,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8139641',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 3,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': '',
                           'M_IP_POSITIONSTEXT': 'Brandstof toeslag.',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 1.39,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 1.39,
                           'M_IP_TYP': 'ET'}]
                         )

    # HW-6192
    def test_get_xml_HW_6192(self):
        m_cn_id = "8356614"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/HW-6192.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 1,
                           'M_IP_POSITIONSTEXT': '51 31 4 A0C 494', 'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 896.65,
                           'M_IP_TOTALNETPRICE': 896.65, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                           'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 2,
                           'M_IP_POSITIONSTEXT': 'Leisten/Clipse / ABDECKLEISTE-OBEN / WLO\nBMW X 5 G05',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 21.26, 'M_IP_TOTALNETPRICE': 21.26,
                           'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 3,
                           'M_IP_POSITIONSTEXT': 'Leisten/Clipse / BLENDE A-SULE LINKS / WLL\nBMW X 5 G05',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 55.89, 'M_IP_TOTALNETPRICE': 55.89,
                           'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 4,
                           'M_IP_POSITIONSTEXT': 'Leisten/Clipse / BLENDE A-SULE RECHTS / WLR\nBMW X 5 G05',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 55.89, 'M_IP_TOTALNETPRICE': 55.89,
                           'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 5,
                           'M_IP_POSITIONSTEXT': 'Zusatz-AW [12]   / KAMERA ASSI / WAWS\nZUSATZARBEIT KAMERA',
                           'M_IP_QUANTITY': 5.0, 'M_IP_SINGLENETPRICE': 8.33, 'M_IP_TOTALNETPRICE': 41.65,
                           'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 6,
                           'M_IP_POSITIONSTEXT': 'Leisten/Clipse / PUFFER 4-TLG / WZBH\nBMW ZUBEHR',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 7.96, 'M_IP_TOTALNETPRICE': 7.96,
                           'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 7,
                           'M_IP_POSITIONSTEXT': 'Leisten/Clipse / CLIP / WZBH\nBMW ZUBEHR', 'M_IP_QUANTITY': 1.0,
                           'M_IP_SINGLENETPRICE': 1.18, 'M_IP_TOTALNETPRICE': 1.18, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''}, {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 8,
                                                'M_IP_POSITIONSTEXT': 'Dichtgummi / SCHALLISOLIERUNG WINDLAUF+2.N / WZBH\nBMW ZUBEHR FRONTSCHEIBE',
                                                'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 111.54,
                                                'M_IP_TOTALNETPRICE': 111.54, 'M_IP_TAXRATE': 19.0,
                                                'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                                                'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                                                'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                                                'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                                                'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                                                'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                                                'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 9,
                           'M_IP_POSITIONSTEXT': 'Klebesatz / SET SCHEIBENVERKLEBUNG (2.KAR) / WKL\nBMW REPARATURSET',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 77.54, 'M_IP_TOTALNETPRICE': 77.54,
                           'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 10,
                           'M_IP_POSITIONSTEXT': 'Montage-Arbeitswerte [12 AW=1 Std.]', 'M_IP_QUANTITY': 26.0,
                           'M_IP_SINGLENETPRICE': 8.33, 'M_IP_TOTALNETPRICE': 216.58, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''}, {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 11,
                                                'M_IP_POSITIONSTEXT': 'Altglasentsorgung PKW\nBundes- & Landesentsorgungs-\nverordnung / KFZ-Verbundglas',
                                                'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 4.31,
                                                'M_IP_TOTALNETPRICE': 4.31, 'M_IP_TAXRATE': 19.0,
                                                'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                                                'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                                                'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                                                'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                                                'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                                                'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                                                'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 12,
                           'M_IP_POSITIONSTEXT': 'Klein-/Verbrauchsmaterial (Anteil des Mat. ) [2%]',
                           'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 6.63, 'M_IP_TOTALNETPRICE': 6.63,
                           'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                           'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None,
                           'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                           'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None,
                           'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 13,
                           'M_IP_POSITIONSTEXT': 'FSP', 'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 5.0,
                           'M_IP_TOTALNETPRICE': 5.0, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                           'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 14,
                           'M_IP_POSITIONSTEXT': 'Schadennummer 9077426399', 'M_IP_QUANTITY': 1.0,
                           'M_IP_SINGLENETPRICE': 0.0, 'M_IP_TOTALNETPRICE': 0.0, 'M_IP_TAXRATE': 19.0,
                           'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None,
                           'M_IP_ARTICLENUMBER': '', 'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_TAXCODE': None, 'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_ECLASS': ''}, {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 15,
                                                'M_IP_POSITIONSTEXT': 'Auftragsnummer 9600757787', 'M_IP_QUANTITY': 1.0,
                                                'M_IP_SINGLENETPRICE': 0.0, 'M_IP_TOTALNETPRICE': 0.0,
                                                'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None, 'M_IP_KOSTENTRAEGER': '',
                                                'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                                                'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None,
                                                'M_IP_QUANTITYUNIT': None, 'M_IP_TYP': 'ET',
                                                'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                                                'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '',
                                                'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 16,
                           'M_IP_POSITIONSTEXT': 'Durchgefhrt am', 'M_IP_QUANTITY': 1.0, 'M_IP_SINGLENETPRICE': 0.0,
                           'M_IP_TOTALNETPRICE': 0.0, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                           'M_IP_ORDERPOSID': None, 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''},
                          {'M_CN_ID': None, 'M_CN_INVOICEID': '8356614', 'M_IP_ITEMPOS': 17,
                           'M_IP_POSITIONSTEXT': 'Rabatt', 'M_IP_QUANTITY': 1, 'M_IP_SINGLENETPRICE': -781.08,
                           'M_IP_TOTALNETPRICE': -781.08, 'M_IP_TAXRATE': 19.0, 'M_IP_COSTCENTER': None,
                           'M_IP_KOSTENTRAEGER': '', 'M_IP_INVENTORYACC': None, 'M_IP_ARTICLENUMBER': None,
                           'M_IP_ARTICLENUMBER2': None, 'M_IP_DISCOUNTAMOUNT': None, 'M_IP_QUANTITYUNIT': None,
                           'M_IP_TYP': 'ET', 'M_IP_DISCOUNTPERCENT': None, 'M_IP_TAXCODE': None,
                           'M_IP_ORDERPOSID': '', 'M_IP_GOODSINWARDPOSID': '', 'M_IP_ECLASS': ''}]
                         )

    # HW-6052
    def test_get_xml_HW_6052(self):
        m_cn_id = "8200889"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/HW-6052.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '8200889',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'OAPP DEPOT',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 24598.0,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 24598.0,
                           'M_IP_TYP': 'ET'}]
                         )

    # HW-6052
    def test_get_xml_HW_6052_15030735(self):
        m_cn_id = "8155357"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/HW-6052_15030735.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '8155357',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': '(1h30/semaine - tarif mensuel)',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 284.52,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 0.0,
                           'M_IP_TOTALNETPRICE': 284.52,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8155357',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 2,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': '(1h/mois)',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 53.48,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 0.0,
                           'M_IP_TOTALNETPRICE': 53.48,
                           'M_IP_TYP': 'ET'}]
                         )

    # HW-6052
    def test_get_xml_HW_6052_15044267(self):
        m_cn_id = "8155357"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/HW-6052_15044267.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '8155357',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'vast recht',
                           'M_IP_QUANTITY': 1.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 16.3212,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 16.32,
                           'M_IP_TYP': 'ET'},
                          {'M_CN_ID': None,
                           'M_CN_INVOICEID': '8155357',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 2,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': 'elektriciteitsverbruik - dag',
                           'M_IP_QUANTITY': 88.0,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 0.1265,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 11.13,
                           'M_IP_TYP': 'ET'}]
                         )

    # HW-6189
    def test_get_xml_HW_6189(self):
        m_cn_id = "8155357"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id)
        xml_positions = read_xml_file_to_str('xml_files/HW-6189_gu_positive.xml')
        xml_invoice_positions = get_xml_positions(
            xml_text=xml_positions,
            xml_invoice_data=xml_invoice_header, logger=Mock())

        self.assertEqual(xml_invoice_positions.get_xml_postions_map(),
                         [{'M_CN_ID': None,
                           'M_CN_INVOICEID': '8155357',
                           'M_IP_ARTICLENUMBER': '',
                           'M_IP_ARTICLENUMBER2': None,
                           'M_IP_COSTCENTER': None,
                           'M_IP_DISCOUNTAMOUNT': None,
                           'M_IP_DISCOUNTPERCENT': None,
                           'M_IP_ECLASS': '',
                           'M_IP_GOODSINWARDPOSID': '',
                           'M_IP_INVENTORYACC': None,
                           'M_IP_ITEMPOS': 1,
                           'M_IP_KOSTENTRAEGER': '',
                           'M_IP_ORDERPOSID': None,
                           'M_IP_POSITIONSTEXT': '2HWC701 / /1203894916\n1185659695',
                           'M_IP_QUANTITY': 1,
                           'M_IP_QUANTITYUNIT': None,
                           'M_IP_SINGLENETPRICE': 187.02,
                           'M_IP_TAXCODE': None,
                           'M_IP_TAXRATE': 21.0,
                           'M_IP_TOTALNETPRICE': 187.02,
                           'M_IP_TYP': 'ET'}]
                         )


if __name__ == '__main__':
    unittest.main()
