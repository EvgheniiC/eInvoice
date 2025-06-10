import unittest
from scr.invoice_handler.client_parser import get_einvoice_client_data
from .test_helper import xml_text_none, xml_text_from_zugpferd, xml_text_from_xml, xml_test_iban_none
from unittest.mock import Mock


# TODO can i find supplier?
class TestClientParser(unittest.TestCase):
    def test_get_einvoice_client_data(self):
        m_cn_id = "5208214"
        clients_data, supplier = get_einvoice_client_data(m_cn_id=m_cn_id, xml_text=xml_text_from_xml, logger=Mock())
        self.assertEqual(clients_data, {'M_CN_ID': '5208214', 'S_KR_NAME1': '[Seller name]',
                                        'S_KR_STRASSE': '[Seller address line 1]', 'S_KR_ORT': '[Seller city]',
                                        'S_KR_POSTLEITZAHL': '12345', 'S_KR_LAND': 'DE', 'S_KR_USTID': 'DE 123456789',
                                        'S_KR_IBAN': 'DE75512108001245126199'})
        self.assertEqual(supplier, None)

    def test_get_einvoice_client_data_none(self):
        m_cn_id = "5208215"
        clients_data, supplier = get_einvoice_client_data(m_cn_id=m_cn_id, xml_text=xml_text_none,  logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5208215', 'S_KR_NAME1': None, 'S_KR_STRASSE': None, 'S_KR_ORT': None,
                          'S_KR_POSTLEITZAHL': None, 'S_KR_LAND': None, 'S_KR_USTID': None, 'S_KR_IBAN': None}
                         )
        self.assertEqual(supplier, None)

    def test_get_einvoice_client_data_all_data(self):
        m_cn_id = "5207492"
        clients_data, supplier = get_einvoice_client_data(m_cn_id=m_cn_id, xml_text=xml_text_from_zugpferd,  logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492', 'S_KR_NAME1': 'KMLZ Rechtsanwaltsges. mbH',
                          'S_KR_STRASSE': 'Unterer Anger 3', 'S_KR_ORT': 'Munchen', 'S_KR_POSTLEITZAHL': '80331',
                          'S_KR_LAND': 'DE', 'S_KR_USTID': 'DE814742004', 'S_KR_IBAN': 'DE95700400410228840500'}
                         )
        self.assertEqual(supplier, None)
        # TODO potential supplier
        # self.assertEqual(supplier, '85089740')

    def test_get_einvoice_client_data_no(self):
        m_cn_id = "5207492"
        clients_data, supplier = get_einvoice_client_data(m_cn_id=m_cn_id, xml_text=xml_test_iban_none,  logger=Mock())
        self.assertEqual(clients_data,
                         {'M_CN_ID': '5207492', 'S_KR_NAME1': 'E.ON Energie Deutschland GmbH',
                          'S_KR_STRASSE': 'Postfach 14 75', 'S_KR_ORT': 'Landshut', 'S_KR_POSTLEITZAHL': '84001',
                          'S_KR_LAND': 'DE', 'S_KR_USTID': 'DE259922663', 'S_KR_IBAN': None}
                         )
        self.assertEqual(supplier, '')


if __name__ == '__main__':
    unittest.main()
