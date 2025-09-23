import unittest
from scr.invoice_handler.xml_vendor_parser import get_einvoice_vendor_data
from unittest.mock import Mock
from scr.helper_functions.einvoice_helper import read_xml_file_to_str


# TODO can i find supplier?
class TestClientParser(unittest.TestCase):
    def test_get_einvoice_client_data(self):
        m_cn_id = "5208214"
        xml_text_from_xml = read_xml_file_to_str('xml_files/xml_text_from_xml.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_text_from_xml, logger=Mock())
        self.assertEqual(clients_data, {'M_CN_ID': '5208214', 'S_KR_NAME1': '[Seller name]',
                                        'S_KR_STRASSE': '[Seller address line 1]', 'S_KR_ORT': '[Seller city]',
                                        'S_KR_POSTLEITZAHL': '12345', 'S_KR_LAND': 'DE', 'S_KR_USTID': 'DE 123456789',
                                        'S_KR_IBAN': 'DE75512108001245126199','S_KR_CLIENT_NAME': '[Buyer name]'})
        self.assertEqual(supplier, None)

    def test_get_einvoice_client_data_none(self):
        m_cn_id = "5208215"
        xml_text_none = read_xml_file_to_str('xml_files/xml_text_none.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_text_none, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5208215',
                          'S_KR_CLIENT_NAME': 'Abweichender Handelsname Rechnungsempfnger',
                          'S_KR_IBAN': None,
                          'S_KR_LAND': 'DK',
                          'S_KR_NAME1': 'EntServ Deutschland GmbH',
                          'S_KR_ORT': 'Ort Rechnungssteller',
                          'S_KR_POSTLEITZAHL': '12345',
                          'S_KR_STRASSE': 'Strae Rechnungssteller 1',
                          'S_KR_USTID': 'ATU13585627'}
                         )
        self.assertEqual(supplier, None)

    def test_get_einvoice_client_data_all_data(self):
        m_cn_id = "5207492"
        xml_text_from_zugpferd = read_xml_file_to_str('xml_files/xml_text_from_zugpferd.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_text_from_zugpferd,
                                                          logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492', 'S_KR_NAME1': 'KMLZ Rechtsanwaltsges. mbH',
                          'S_KR_STRASSE': 'Unterer Anger 3', 'S_KR_ORT': 'Munchen', 'S_KR_POSTLEITZAHL': '80331',
                          'S_KR_LAND': 'DE', 'S_KR_USTID': 'DE814742004', 'S_KR_IBAN': 'DE95700400410228840500', 'S_KR_CLIENT_NAME': 'Sixt SE',}
                         )
        self.assertEqual(supplier, None)
        # TODO potential supplier
        # self.assertEqual(supplier, '85089740')

    def test_get_einvoice_client_data_no(self):
        m_cn_id = "5207492"
        xml_test_iban_none = read_xml_file_to_str('xml_files/xml_test_iban_none.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=xml_test_iban_none, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492', 'S_KR_NAME1': 'E.ON Energie Deutschland GmbH',
                          'S_KR_STRASSE': 'Postfach 14 75', 'S_KR_ORT': 'Landshut', 'S_KR_POSTLEITZAHL': '84001',
                          'S_KR_LAND': 'DE', 'S_KR_USTID': 'DE259922663', 'S_KR_IBAN': None, 'S_KR_CLIENT_NAME': 'Sixt GmbH & Co. Autovermietung KG',}
                         )
        self.assertEqual(supplier, None)

    # not zugpferd, only XML file
    def test_get_einvoice_client_data_not_zugpferd(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/clear_xml_from_gerd.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_IBAN': 'DE13664900000023969700',
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'Inspire Technologies GmbH',
                          'S_KR_ORT': 'St. Georgen',
                          'S_KR_POSTLEITZAHL': '78112',
                          'S_KR_STRASSE': 'Leopoldstr. 1',
                          'S_KR_USTID': 'DE260569738',
                          'S_KR_CLIENT_NAME': None,})

        self.assertEqual(supplier, None)

    def test_get_einvoice_client_10(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/xml_test_mandant_10.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_IBAN': 'DE95700400410228840500',
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'KMLZ Rechtsanwaltsges. mbH',
                          'S_KR_ORT': 'Munchen',
                          'S_KR_POSTLEITZAHL': '80331',
                          'S_KR_STRASSE': 'Unterer Anger 3',
                          'S_KR_USTID': 'DE814742004',
                          'S_KR_CLIENT_NAME': 'Sixt SE'})

        self.assertEqual(supplier, None)


    def test_get_einvoice_SWFM_5490(self):
        m_cn_id = "5207492"
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/xml_text_find_VIN_USTD_SWFM-5490.xml')
        clients_data, supplier = get_einvoice_vendor_data(m_cn_id=m_cn_id, xml_text=clear_xml_from_gerd, logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492',
                          'S_KR_CLIENT_NAME': 'Sixt GmbH & Co Autovermietg.KG Reparaturzentrum Berlin',
                          'S_KR_IBAN': 'DE55160500003504000405',
                          'S_KR_LAND': 'DE',
                          'S_KR_NAME1': 'Autohaus Babelsberg  GmbH & Co.KG',
                          'S_KR_ORT': 'Potsdam',
                          'S_KR_POSTLEITZAHL': '14482',
                          'S_KR_STRASSE': 'Fritz-Zubeil-Strae 70-78',
                          'S_KR_USTID': 'DE138410797'})

        self.assertEqual(supplier, None)

if __name__ == '__main__':
    unittest.main()
