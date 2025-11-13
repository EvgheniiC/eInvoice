import unittest
from scr.invoice_handler.xml_vendor_parser import get_einvoice_vendor_data
from unittest.mock import Mock
from scr.helper_functions.einvoice_helper import read_xml_file_to_str


class TestClientParser(unittest.TestCase):
    def test_get_einvoice_client_data(self):
        m_cn_id = "5208214"
        xml_text_from_xml = read_xml_file_to_str('xml_files/xml_text_from_xml.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_text_from_xml, logger=Mock())
        self.assertEqual(clients_data, {'M_CN_ID': '5208214',
                                        'S_KR_CLIENT_NAME': '[Buyer name]',
                                        'S_KR_CLIENT_NAME_DELIVERY': None,
                                        'S_KR_IBAN': 'DE75512108001245126199',
                                        'S_KR_LAND': 'DE',
                                        'S_KR_NAME1': '[Seller name]',
                                        'S_KR_ORT': '[Seller city]',
                                        'S_KR_ORT_DELIVERY': None,
                                        'S_KR_POSTLEITZAHL': '12345',
                                        'S_KR_POSTLEITZAHL_DELIVERY': None,
                                        'S_KR_STRASSE': '[Seller address line 1]',
                                        'S_KR_STRASSE_DELIVERY': None,
                                        'S_KR_USTID': 'DE 123456789'})
        self.assertEqual(supplier, None)

    def test_get_einvoice_client_data_none(self):
        m_cn_id = "5208215"
        xml_text_none = read_xml_file_to_str('xml_files/xml_text_none.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_text_none, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5208215',
                          'S_KR_CLIENT_NAME': 'Abweichender Handelsname Rechnungsempfnger',
                          'S_KR_CLIENT_NAME_DELIVERY': 'Anderer Leistungsempfnger',
                          'S_KR_IBAN': 'DE84600400710561515801',
                          'S_KR_LAND': 'DK',
                          'S_KR_NAME1': 'EntServ Deutschland GmbH',
                          'S_KR_ORT': 'Ort Rechnungsempfnger',
                          'S_KR_ORT_DELIVERY': 'Anderer Leistungsempfnger Ort',
                          'S_KR_POSTLEITZAHL': '67890',
                          'S_KR_POSTLEITZAHL_DELIVERY': '45678',
                          'S_KR_STRASSE': 'Strae Rechnungsempfnger 1',
                          'S_KR_STRASSE_DELIVERY': 'Anderer Leistungsempfnger Strae 1',
                          'S_KR_USTID': 'ATU13585627'}
                         )
        self.assertEqual(supplier, None)

    def test_get_einvoice_client_data_all_data(self):
        m_cn_id = "5207492"
        xml_text_from_zugpferd = read_xml_file_to_str('xml_files/xml_text_from_zugpferd.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_text_from_zugpferd,
                                                          logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_CLIENT_NAME': 'Sixt SE',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_IBAN': 'DE95700400410228840500',
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'KMLZ Rechtsanwaltsges. mbH',
                          'S_KR_ORT': 'Munchen',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_POSTLEITZAHL': '80331',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Unterer Anger 3',
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_USTID': 'DE814742004'}
                         )
        self.assertEqual(supplier, None)
        # TODO potential supplier
        # self.assertEqual(supplier, '85089740')

    def test_get_einvoice_client_data_no(self):
        m_cn_id = "5207492"
        xml_test_iban_none = read_xml_file_to_str('xml_files/xml_test_iban_none.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_test_iban_none, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_IBAN': None,
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'E.ON Energie Deutschland GmbH',
                          'S_KR_ORT': 'Landshut',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_POSTLEITZAHL': '84001',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Postfach 14 75',
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_USTID': 'DE259922663'}
                         )
        self.assertEqual(supplier, None)

    # not zugpferd, only XML file
    def test_get_einvoice_client_data_not_zugpferd(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/clear_xml_from_gerd.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_CLIENT_NAME': None,
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_IBAN': 'DE13664900000023969700',
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'Inspire Technologies GmbH',
                          'S_KR_ORT': 'Pullach',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_POSTLEITZAHL': '82049',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Zugspitzstrasse 1',
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_USTID': 'DE260569738'})

        self.assertEqual(supplier, None)

    def test_get_einvoice_client_10(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/xml_test_mandant_10.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_CLIENT_NAME': 'Sixt SE',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_IBAN': 'DE95700400410228840500',
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'KMLZ Rechtsanwaltsges. mbH',
                          'S_KR_ORT': 'Munchen',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_POSTLEITZAHL': '80331',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Unterer Anger 3',
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_USTID': 'DE814742004'})

        self.assertEqual(supplier, None)

    def test_get_einvoice_SWFM_5490(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/xml_text_find_VIN_USTD_SWFM-5490.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum Berlin',
                          'S_KR_CLIENT_NAME_DELIVERY': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum '
                                                       'Berlin',
                          'S_KR_IBAN': 'DE55160500003504000405',
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'Autohaus Babelsberg  GmbH & Co.KG',
                          'S_KR_ORT': 'Schnefeld',
                          'S_KR_ORT_DELIVERY': 'Schnefeld',
                          'S_KR_POSTLEITZAHL': '12529',
                          'S_KR_POSTLEITZAHL_DELIVERY': '12529',
                          'S_KR_STRASSE': 'Am Airport 7',
                          'S_KR_STRASSE_DELIVERY': 'Am Airport 7',
                          'S_KR_USTID': 'DE138410797'})

        self.assertEqual(supplier, None)

    def test_get_einvoice_85018982AutohausBabelsberg(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/85018982AutohausBabelsberg.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum Berlin',
                          'S_KR_CLIENT_NAME_DELIVERY': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum '
                                                       'Berlin',
                          'S_KR_IBAN': 'DE55160500003504000405',
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'Autohaus Babelsberg  GmbH & Co.KG',
                          'S_KR_ORT': 'Schnefeld',
                          'S_KR_ORT_DELIVERY': 'Schnefeld',
                          'S_KR_POSTLEITZAHL': '12529',
                          'S_KR_POSTLEITZAHL_DELIVERY': '12529',
                          'S_KR_STRASSE': 'Am Airport 7',
                          'S_KR_STRASSE_DELIVERY': 'Am Airport 7',
                          'S_KR_USTID': 'DE138410797'})

        self.assertEqual(supplier, None)


    def test_get_einvoice_85000159(self):
        m_cn_id = "7697763"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/85000159.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '7697763',
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co. Autovermietung KG',
                          'S_KR_CLIENT_NAME_DELIVERY': None,
                          'S_KR_IBAN': 'DE36512500000001178040',
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'Abschleppdienst Offenbach GmbH',
                          'S_KR_ORT': 'Offenbach am Main',
                          'S_KR_ORT_DELIVERY': None,
                          'S_KR_POSTLEITZAHL': '63069',
                          'S_KR_POSTLEITZAHL_DELIVERY': None,
                          'S_KR_STRASSE': 'Sprendlinger Landstrae 167',
                          'S_KR_STRASSE_DELIVERY': None,
                          'S_KR_USTID': 'DE113527818'})

        self.assertEqual(supplier, None)


if __name__ == '__main__':
    unittest.main()
