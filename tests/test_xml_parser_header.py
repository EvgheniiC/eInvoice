import unittest
from scr.invoice_handler.xml_parser_header import get_xml_header
from scr.data_class.XmlInvoiceHeader import XmlInvoiceHeader
from datetime import datetime
from unittest.mock import Mock
from scr.helper_functions.einvoice_helper import read_xml_file_to_str


class TestXmlParserHeader(unittest.TestCase):
    def test_get_xml_header_with_contract_id(self):
        m_cn_id = "6983825"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text_from_zugpferd = read_xml_file_to_str('xml_text_from_zugpferd.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text_from_zugpferd,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'M_CN_ID': '6983825', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None,
                          'HIGHWAY_ZEITSTEMPEL': None, 'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KREDITOR': None, 'M_IV_MANDANT': '1', 'M_IV_CONTRACTID': 'SX-00855',
                          'M_IV_ORDERID': None, 'M_IV_IBAN': 'DE95700400410228840500',
                          'M_IV_KINDOFINVOICE': 'RE', 'M_IV_INVOICENUMBER': '202510294',
                          'M_IV_COSTCENTER': None, 'M_IV_DAMAGENUMBER': None,
                          'M_IV_INVOICEDATE': datetime(2025, 1, 31, 0, 0),
                          'M_IV_DELIVERYDATE': datetime(2025, 1, 31, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 1, 31, 0, 0),
                          'M_IV_INVOICEAMOUNT': '227.50', 'M_IV_TOTALAMOUNT': '270.73',
                          'M_IV_TOTALTAXAMOUNT': '43.23', 'M_IV_TAXRATE1': '19.00',
                          'M_IV_TAXAMOUNT1': '43.23', 'M_IV_TAXRATE2': None, 'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXRATE3': None, 'M_IV_TAXAMOUNT3': None, 'M_IV_TAXRATE4': None,
                          'M_IV_TAXAMOUNT4': None, 'M_IV_TAXRATE5': None, 'M_IV_TAXAMOUNT5': None,
                          'M_IV_CURRENCY': 'EUR', 'M_IV_VIN': None, 'M_IV_EMPFAENGER': None,
                          'M_IV_CONTRACT_START': None, 'M_IV_CONTRACT_END': None,
                          'TRIGGER_HIGHWAY': '0', 'M_CN_MAIL_ID': None, 'EMAIL_NAME': None}
                         )

    def test_get_xml_header_all_none(self):
        m_cn_id = "6983825"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_test_iban_none = read_xml_file_to_str('xml_test_iban_none.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_test_iban_none,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'M_CN_ID': '6983825', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None, 'HIGHWAY_ZEITSTEMPEL': None,
                          'M_IV_INVOICETYPE': 'EKS', 'M_IV_KREDITOR': '9903323000007', 'M_IV_MANDANT': '1',
                          'M_IV_CONTRACTID': None, 'M_IV_ORDERID': None, 'M_IV_IBAN': None,
                          'M_IV_KINDOFINVOICE': 'GU', 'M_IV_INVOICENUMBER': '212732918642', 'M_IV_COSTCENTER': None,
                          'M_IV_DAMAGENUMBER': None, 'M_IV_INVOICEDATE': datetime(2025, 4, 15, 0, 0),
                          'M_IV_DELIVERYDATE': datetime(2024, 1, 1, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2024, 12, 31, 0, 0),
                          'M_IV_INVOICEAMOUNT': '239.85', 'M_IV_TOTALAMOUNT': '285.42', 'M_IV_TOTALTAXAMOUNT': '45.57',
                          'M_IV_TAXRATE1': '19.00', 'M_IV_TAXAMOUNT1': '45.57', 'M_IV_TAXRATE2': None,
                          'M_IV_TAXAMOUNT2': None, 'M_IV_TAXRATE3': None, 'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXRATE4': None, 'M_IV_TAXAMOUNT4': None, 'M_IV_TAXRATE5': None,
                          'M_IV_TAXAMOUNT5': None, 'M_IV_CURRENCY': 'EUR', 'M_IV_VIN': None, 'M_IV_EMPFAENGER': None,
                          'M_IV_CONTRACT_START': None, 'M_IV_CONTRACT_END': None, 'TRIGGER_HIGHWAY': '0',
                          'M_CN_MAIL_ID': None, 'EMAIL_NAME': None}

                         )

    def test_get_xml_header_iban(self):
        m_cn_id = "6983825"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_test_header = read_xml_file_to_str('xml_test_header.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_test_header,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'M_CN_ID': '6983825', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None, 'HIGHWAY_ZEITSTEMPEL': None,
                          'M_IV_INVOICETYPE': 'EKS', 'M_IV_KREDITOR': None, 'M_IV_MANDANT': '1',
                          'M_IV_CONTRACTID': None, 'M_IV_ORDERID': None, 'M_IV_IBAN': 'DE47795800990158788201',
                          'M_IV_KINDOFINVOICE': 'RE', 'M_IV_INVOICENUMBER': '19478759', 'M_IV_COSTCENTER': None,
                          'M_IV_DAMAGENUMBER': None, 'M_IV_INVOICEDATE': datetime(2025, 5, 7, 0, 0),
                          'M_IV_DELIVERYDATE': datetime(2025, 5, 1, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 5, 7, 0, 0),
                          'M_IV_INVOICEAMOUNT': '18219.38', 'M_IV_TOTALAMOUNT': '18219.38',
                          'M_IV_TOTALTAXAMOUNT': '0.00', 'M_IV_TAXRATE1': '0', 'M_IV_TAXAMOUNT1': '0.00',
                          'M_IV_TAXRATE2': None, 'M_IV_TAXAMOUNT2': None, 'M_IV_TAXRATE3': None,
                          'M_IV_TAXAMOUNT3': None, 'M_IV_TAXRATE4': None, 'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXRATE5': None, 'M_IV_TAXAMOUNT5': None, 'M_IV_CURRENCY': 'EUR', 'M_IV_VIN': None,
                          'M_IV_EMPFAENGER': None, 'M_IV_CONTRACT_START': None, 'M_IV_CONTRACT_END': None,
                          'TRIGGER_HIGHWAY': '0', 'M_CN_MAIL_ID': None, 'EMAIL_NAME': None}
                         )

    def test_get_xml_header_orderid_930(self):
        m_cn_id = "6769729"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_test_header_order_930 = read_xml_file_to_str('xml_test_header_order_930.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_test_header_order_930,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'M_CN_ID': '6769729', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None, 'HIGHWAY_ZEITSTEMPEL': None,
                          'M_IV_INVOICETYPE': 'EKS', 'M_IV_KREDITOR': None, 'M_IV_MANDANT': '1',
                          'M_IV_CONTRACTID': None, 'M_IV_ORDERID': '9307162373', 'M_IV_IBAN': None,
                          'M_IV_KINDOFINVOICE': 'RE', 'M_IV_INVOICENUMBER': '22247', 'M_IV_COSTCENTER': None,
                          'M_IV_DAMAGENUMBER': None, 'M_IV_INVOICEDATE': datetime(2025, 2, 19, 0, 0),
                          'M_IV_DELIVERYDATE': datetime(2025, 2, 19, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 2, 19, 0, 0), 'M_IV_INVOICEAMOUNT': '407.53',
                          'M_IV_TOTALAMOUNT': '484.96', 'M_IV_TOTALTAXAMOUNT': '77.43', 'M_IV_TAXRATE1': '19.00',
                          'M_IV_TAXAMOUNT1': '77.43', 'M_IV_TAXRATE2': None, 'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXRATE3': None, 'M_IV_TAXAMOUNT3': None, 'M_IV_TAXRATE4': None,
                          'M_IV_TAXAMOUNT4': None, 'M_IV_TAXRATE5': None, 'M_IV_TAXAMOUNT5': None,
                          'M_IV_CURRENCY': 'EUR', 'M_IV_VIN': None, 'M_IV_EMPFAENGER': None,
                          'M_IV_CONTRACT_START': None, 'M_IV_CONTRACT_END': None, 'TRIGGER_HIGHWAY': '0',
                          'M_CN_MAIL_ID': None, 'EMAIL_NAME': None}
                         )

    def test_get_xml_header_orderid_false(self):
        m_cn_id = "7053580"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_test_header_kst = read_xml_file_to_str('xml_test_header_kst.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_test_header_kst,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        # print(xml_invoice_data.get_xml_header_attributes())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'M_CN_ID': '7053580', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None, 'HIGHWAY_ZEITSTEMPEL': None,
                          'M_IV_INVOICETYPE': 'EKS', 'M_IV_KREDITOR': '9903323000007', 'M_IV_MANDANT': '1',
                          'M_IV_CONTRACTID': None, 'M_IV_ORDERID': None, 'M_IV_IBAN': 'DE04700202700062004312',
                          'M_IV_KINDOFINVOICE': 'RE', 'M_IV_INVOICENUMBER': '211680763808', 'M_IV_COSTCENTER': None,
                          'M_IV_DAMAGENUMBER': None, 'M_IV_INVOICEDATE': datetime(2025, 6, 3, 0, 0),
                          'M_IV_DELIVERYDATE': datetime(2025, 5, 1, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 5, 31, 0, 0), 'M_IV_INVOICEAMOUNT': '352.91',
                          'M_IV_TOTALAMOUNT': '419.96', 'M_IV_TOTALTAXAMOUNT': '67.05', 'M_IV_TAXRATE1': '19.00',
                          'M_IV_TAXAMOUNT1': '67.05', 'M_IV_TAXRATE2': None, 'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXRATE3': None, 'M_IV_TAXAMOUNT3': None, 'M_IV_TAXRATE4': None,
                          'M_IV_TAXAMOUNT4': None, 'M_IV_TAXRATE5': None, 'M_IV_TAXAMOUNT5': None,
                          'M_IV_CURRENCY': 'EUR', 'M_IV_VIN': None, 'M_IV_EMPFAENGER': None,
                          'M_IV_CONTRACT_START': None, 'M_IV_CONTRACT_END': None, 'TRIGGER_HIGHWAY': '0',
                          'M_CN_MAIL_ID': None, 'EMAIL_NAME': None}

                         )


if __name__ == '__main__':
    unittest.main()
