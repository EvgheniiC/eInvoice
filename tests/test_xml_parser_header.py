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
        xml_text_from_zugpferd = read_xml_file_to_str('xml_files/xml_text_from_zugpferd.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text_from_zugpferd,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'M_CN_ID': '6983825', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None,
                          'HIGHWAY_ZEITSTEMPEL': None, 'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KREDITOR': None, 'M_IV_LICENSE_NUMBER': None, 'M_IV_MANDANT': None,
                          'M_IV_CONTRACTID': 'SX-00855',
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
                          'TRIGGER_HIGHWAY': '0', 'M_CN_MAIL_ID': None, 'EMAIL_NAME': None, 'SIXT_VAT_ID': None}
                         )

    def test_get_xml_header_all_none(self):
        m_cn_id = "6983825"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_test_iban_none = read_xml_file_to_str('xml_files/xml_test_iban_none.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_test_iban_none,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'M_CN_ID': '6983825', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf', 'M_IV_LICENSE_NUMBER': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None, 'HIGHWAY_ZEITSTEMPEL': None,
                          'M_IV_INVOICETYPE': 'EKS', 'M_IV_KREDITOR': '9903323000007', 'M_IV_MANDANT': None,
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
                          'M_CN_MAIL_ID': None, 'EMAIL_NAME': None, 'SIXT_VAT_ID': None}

                         )

    def test_get_xml_header_iban(self):
        m_cn_id = "6983825"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_test_header = read_xml_file_to_str('xml_files/xml_test_header.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_test_header,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'M_CN_ID': '6983825', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf', 'M_IV_LICENSE_NUMBER': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None, 'HIGHWAY_ZEITSTEMPEL': None,
                          'M_IV_INVOICETYPE': 'EKS', 'M_IV_KREDITOR': None, 'M_IV_MANDANT': None,
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
                          'TRIGGER_HIGHWAY': '0', 'M_CN_MAIL_ID': None, 'EMAIL_NAME': None, 'SIXT_VAT_ID': None}
                         )

    def test_get_xml_header_orderid_930(self):
        m_cn_id = "6769729"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_test_header_order_930 = read_xml_file_to_str('xml_files/xml_test_header_order_930.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_test_header_order_930,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'M_CN_ID': '6769729', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf', 'M_IV_LICENSE_NUMBER': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None, 'HIGHWAY_ZEITSTEMPEL': None,
                          'M_IV_INVOICETYPE': 'EKS', 'M_IV_KREDITOR': None, 'M_IV_MANDANT': None,
                          'M_IV_CONTRACTID': None, 'M_IV_ORDERID': '9307162373', 'M_IV_IBAN': 'DE24590501010074280249',
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
                          'M_CN_MAIL_ID': None, 'EMAIL_NAME': None, 'SIXT_VAT_ID': None}
                         )

    def test_get_xml_header_orderid_false(self):
        m_cn_id = "7053580"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_test_header_kst = read_xml_file_to_str('xml_files/xml_test_header_kst.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_test_header_kst,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        # print(xml_invoice_data.get_xml_header_attributes())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'M_CN_ID': '7053580', 'M_IV_BARCODE': '1234567', 'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail', 'M_IV_IMAGEPATH': '1234567.pdf', 'M_IV_LICENSE_NUMBER': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice', 'M_IV_MAIL_SUBJECT': None, 'HIGHWAY_ZEITSTEMPEL': None,
                          'M_IV_INVOICETYPE': 'EKS', 'M_IV_KREDITOR': '9903323000007', 'M_IV_MANDANT': None,
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
                          'M_CN_MAIL_ID': None, 'EMAIL_NAME': None, 'SIXT_VAT_ID': None}

                         )

    def test_get_xml_header_bad_case(self):
        xml_invoice_header = XmlInvoiceHeader()
        xml_test_header_kst = read_xml_file_to_str('xml_files/xml_test_header_kst.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_test_header_kst,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': None,
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': None,
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': None,
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': None,
                          'M_IV_DELIVERYDATE_BIS': None,
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': None,
                          'M_IV_IMAGEPATH': None,
                          'M_IV_INVOICEAMOUNT': None,
                          'M_IV_INVOICEDATE': None,
                          'M_IV_INVOICENUMBER': None,
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': None,
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': None,
                          'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': None,
                          'M_IV_TAXRATE2': None,
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': None,
                          'M_IV_TOTALTAXAMOUNT': None,
                          'M_IV_VIN': None,
                          'TRIGGER_HIGHWAY': '0', 'SIXT_VAT_ID': None}
                         )

    # if we get only XML File (not from zugpferd)
    def test_get_xml_header_from_xml_file(self):
        m_cn_id = "7053580"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        clear_xml_from_gerd = read_xml_file_to_str('xml_files/clear_xml_from_gerd.xml')
        xml_invoice_data = get_xml_header(xml_text=clear_xml_from_gerd,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7053580',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '1234567',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2025, 1, 1, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 12, 31, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'DE13664900000023969700',
                          'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_INVOICEAMOUNT': '48105.0',
                          'M_IV_INVOICEDATE': datetime(2025, 1, 24, 0, 0),
                          'M_IV_INVOICENUMBER': '3250124002',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': 'SIXT-000000025218',
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '9139.95',
                          'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '19.00',
                          'M_IV_TAXRATE2': None,
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '57244.95',
                          'M_IV_TOTALTAXAMOUNT': '9139.95',
                          'M_IV_VIN': None,
                          'TRIGGER_HIGHWAY': '0', 'SIXT_VAT_ID': 'DE234567890'}
                         )

    # if we get XML File, but we don't have tags
    def test_get_xml_header_from_xml_file_with_no_header_data(self):
        m_cn_id = "7053580"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xm_positions_false = read_xml_file_to_str('xml_files/xm_positions_false.xml')
        xml_invoice_data = get_xml_header(xml_text=xm_positions_false,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7053580',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '1234567',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2025, 8, 21, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 8, 21, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'DE55160500003504000405',
                          'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_INVOICEAMOUNT': '262.78',
                          'M_IV_INVOICEDATE': datetime(2025, 8, 21, 0, 0),
                          'M_IV_INVOICENUMBER': '110015297',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'GU',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': '9307392455',
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '49.93',
                          'M_IV_TAXAMOUNT2': '0.00',
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '19.00',
                          'M_IV_TAXRATE2': '0.00',
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '312.71',
                          'M_IV_TOTALTAXAMOUNT': '49.93',
                          'M_IV_VIN': 'WVGZZZCSZPY011005',
                          'TRIGGER_HIGHWAY': '0', 'SIXT_VAT_ID': 'DE223999470'}
                         )

    def test_get_xml_header_from_xml_file_85018982(self):
        m_cn_id = "7053580"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xm_positions_false = read_xml_file_to_str('xml_files/85018982_head.xml')
        xml_invoice_data = get_xml_header(xml_text=xm_positions_false,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7053580',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '1234567',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2025, 8, 28, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 8, 28, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'DE55160500003504000405',
                          'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_INVOICEAMOUNT': '38.25',
                          'M_IV_INVOICEDATE': datetime(2025, 8, 28, 0, 0),
                          'M_IV_INVOICENUMBER': '110015584',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': '9307393345',
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '7.27',
                          'M_IV_TAXAMOUNT2': '0.00',
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '19.00',
                          'M_IV_TAXRATE2': '0.00',
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '45.52',
                          'M_IV_TOTALTAXAMOUNT': '7.27',
                          'M_IV_VIN': 'WAUZZZGH5SA015309',
                          'TRIGGER_HIGHWAY': '0', 'SIXT_VAT_ID': 'DE223999470'}
                         )

    def test_get_xml_header_from_xml_file_SWFM_5490(self):
        m_cn_id = "7053580"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/xml_text_find_VIN_USTD_SWFM-5490.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7053580',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '1234567',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2025, 8, 21, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 8, 21, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'DE55160500003504000405',
                          'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_INVOICEAMOUNT': '97.62',
                          'M_IV_INVOICEDATE': datetime(2025, 8, 21, 0, 0),
                          'M_IV_INVOICENUMBER': '112003938',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': '9307398735',
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '18.55',
                          'M_IV_TAXAMOUNT2': '0.00',
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '19.00',
                          'M_IV_TAXRATE2': '0.00',
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '116.17',
                          'M_IV_TOTALTAXAMOUNT': '18.55',
                          'M_IV_VIN': None,
                          'TRIGGER_HIGHWAY': '0', 'SIXT_VAT_ID': None}
                         )

    def test_get_xml_header_from_xml_file_new_VIN(self):
        m_cn_id = "7053580"
        barcode = "1234567"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/xml__new_vin.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7053580',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '1234567',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2025, 9, 15, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 9, 15, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'DE55160500003504000405',
                          'M_IV_IMAGEPATH': '1234567.pdf',
                          'M_IV_INVOICEAMOUNT': '2464.06',
                          'M_IV_INVOICEDATE': datetime(2025, 9, 15, 0, 0),
                          'M_IV_INVOICENUMBER': '110016263',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '510.62',
                          'M_IV_TAXAMOUNT2': '0.00',
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '19.00',
                          'M_IV_TAXRATE2': '0.00',
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '2974.68',
                          'M_IV_TOTALTAXAMOUNT': '510.62',
                          'M_IV_VIN': 'WVGZZZC11SY078194',
                          'TRIGGER_HIGHWAY': '0', 'SIXT_VAT_ID': 'DE223999470'}
                         )

    # SWFM-5639
    def test_get_xml_header_from_xml_85000159(self):
        m_cn_id = "7697763"
        barcode = "44073860"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/85000159.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7697763',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '44073860',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2025, 11, 9, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 11, 9, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'DE36512500000001178040',
                          'M_IV_IMAGEPATH': '44073860.pdf',
                          'M_IV_INVOICEAMOUNT': '142.40',
                          'M_IV_INVOICEDATE': datetime(2025, 11, 9, 0, 0),
                          'M_IV_INVOICENUMBER': 'ofr2517108',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '27.06',
                          'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '19.00',
                          'M_IV_TAXRATE2': None,
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '169.46',
                          'M_IV_TOTALTAXAMOUNT': '27.06',
                          'M_IV_VIN': None,
                          'TRIGGER_HIGHWAY': '0', 'SIXT_VAT_ID': None}
                         )

    # HW-5648
    def test_get_xml_header_HW_5648(self):
        m_cn_id = "5209222"
        barcode = "13449562"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/xml_text_SAP_BE_HW_5648.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '5209222',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '13449562',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2023, 11, 1, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2032, 12, 31, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': None,
                          'M_IV_IMAGEPATH': '13449562.pdf',
                          'M_IV_INVOICEAMOUNT': '4900.0',
                          'M_IV_INVOICEDATE': datetime(2023, 12, 19, 0, 0),
                          'M_IV_INVOICENUMBER': 'tickstarapbis3test01',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': '99887766',
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'SIXT_VAT_ID': 'SE4598375937',
                          'M_IV_TAXAMOUNT1': '1225',
                          'M_IV_TAXAMOUNT2': '0',
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '25',
                          'M_IV_TAXRATE2': '0',
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '7125',
                          'M_IV_TOTALTAXAMOUNT': '1225.00',
                          'M_IV_VIN': None,
                          'TRIGGER_HIGHWAY': '0'}
                         )

    def test_get_sixt_vat_id(self):
        m_cn_id = "5209222"
        barcode = "13449562"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/SIXT_VAT_ID.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '5209222',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '13449562',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2023, 11, 1, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2032, 12, 31, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': None,
                          'M_IV_IMAGEPATH': '13449562.pdf',
                          'M_IV_INVOICEAMOUNT': '4900.0',
                          'M_IV_INVOICEDATE': datetime(2023, 12, 19, 0, 0),
                          'M_IV_INVOICENUMBER': 'tickstarapbis3test01',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': '80152120',
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'SIXT_VAT_ID': 'BE0465341266',
                          'M_IV_TAXAMOUNT1': '1225',
                          'M_IV_TAXAMOUNT2': '0',
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '25',
                          'M_IV_TAXRATE2': '0',
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '7125',
                          'M_IV_TOTALTAXAMOUNT': '1225.00',
                          'M_IV_VIN': None,
                          'TRIGGER_HIGHWAY': '0'}
                         )

    def test_get_sap_data(self):
        m_cn_id = "5209222"
        barcode = "13449562"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/first_sap.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '5209222',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '13449562',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2026, 1, 2, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2026, 1, 2, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'BE64734003185952',
                          'M_IV_IMAGEPATH': '13449562.pdf',
                          'M_IV_INVOICEAMOUNT': '147974.37',
                          'M_IV_INVOICEDATE': datetime(2026, 1, 2, 0, 0),
                          'M_IV_INVOICENUMBER': '44123713',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '0',
                          'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '0',
                          'M_IV_TAXRATE2': None,
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '147974.37',
                          'M_IV_TOTALTAXAMOUNT': '0.00',
                          'M_IV_VIN': None,
                          'SIXT_VAT_ID': 'BE0465341266',
                          'TRIGGER_HIGHWAY': '0'}
                         )

    # HW-5823
    def test_get_gu(self):
        m_cn_id = "7952984"
        barcode = "14961075"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/GU.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7952984',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '14961075',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2026, 1, 6, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2026, 1, 6, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'BE36733023702281',
                          'M_IV_IMAGEPATH': '14961075.pdf',
                          'M_IV_INVOICEAMOUNT': '-66.14',
                          'M_IV_INVOICEDATE': datetime(2026, 1, 6, 0, 0),
                          'M_IV_INVOICENUMBER': '3557959',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'GU',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': '9600511022',
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '-13.89',
                          'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '21',
                          'M_IV_TAXRATE2': None,
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '-80.03',
                          'M_IV_TOTALTAXAMOUNT': '-13.89',
                          'M_IV_VIN': None,
                          'SIXT_VAT_ID': 'BE0465341266',
                          'TRIGGER_HIGHWAY': '0'}
                         )

    # HW - 5794
    def test_get_delivery_date(self):
        m_cn_id = "7952945"
        barcode = "14961036"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/deliveryDateIsEmpty.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7952945',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '14961036',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2025, 12, 16, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 12, 16, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'BE69393042417078',
                          'M_IV_IMAGEPATH': '14961036.pdf',
                          'M_IV_INVOICEAMOUNT': '155.02',
                          'M_IV_INVOICEDATE': datetime(2025, 12, 30, 0, 0),
                          'M_IV_INVOICENUMBER': '35125129621184',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': '9600517150',
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '32.55',
                          'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '21',
                          'M_IV_TAXRATE2': None,
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '187.57',
                          'M_IV_TOTALTAXAMOUNT': '32.55',
                          'M_IV_VIN': None,
                          'SIXT_VAT_ID': 'BE0465341266',
                          'TRIGGER_HIGHWAY': '0'}
                         )

    # HW-5812
    def test_get_two_tax(self):
        m_cn_id = "7953030"
        barcode = "14961121"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/twoTax.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7953030',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '14961121',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2025, 11, 22, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2025, 12, 24, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'BE46000325448336',
                          'M_IV_IMAGEPATH': '14961121.pdf',
                          'M_IV_INVOICEAMOUNT': '605.51',
                          'M_IV_INVOICEDATE': datetime(2026, 1, 6, 0, 0),
                          'M_IV_INVOICENUMBER': '708253075596',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '126.89',
                          'M_IV_TAXAMOUNT2': '0.00',
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '21',
                          'M_IV_TAXRATE2': '0',
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '732.4',
                          'M_IV_TOTALTAXAMOUNT': '126.89',
                          'M_IV_VIN': None,
                          'SIXT_VAT_ID': 'BE0465341266',
                          'TRIGGER_HIGHWAY': '0'}
                         )

    # HW-5852
    def test_get_coupaPO(self):
        m_cn_id = "7980175"
        barcode = "14968910"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/coupaPO.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7980175',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '14968910',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2026, 1, 13, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2026, 1, 13, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': None,
                          'M_IV_IMAGEPATH': '14968910.pdf',
                          'M_IV_INVOICEAMOUNT': '145.00',
                          'M_IV_INVOICEDATE': datetime(2026, 1, 13, 0, 0),
                          'M_IV_INVOICENUMBER': '260034',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': 'SIXT-000000323914',
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '30.45',
                          'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '21.00',
                          'M_IV_TAXRATE2': None,
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '175.45',
                          'M_IV_TOTALTAXAMOUNT': '30.45',
                          'M_IV_VIN': None,
                          'SIXT_VAT_ID': 'BE0465341266',
                          'TRIGGER_HIGHWAY': '0'}
                         )

    # HW-5851
    def test_get_cc_budget(self):
        m_cn_id = "7980166"
        barcode = "14968901"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/cc_budget_and_another.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7980166',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '14968901',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': '41872',
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2026, 1, 12, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2026, 1, 12, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': None,
                          'M_IV_IMAGEPATH': '14968901.pdf',
                          'M_IV_INVOICEAMOUNT': '210.09',
                          'M_IV_INVOICEDATE': datetime(2026, 1, 12, 0, 0),
                          'M_IV_INVOICENUMBER': 'bei2401642',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': '35',
                          'M_IV_ORDERID': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '0.00',
                          'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '0.00',
                          'M_IV_TAXRATE2': None,
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '210.09',
                          'M_IV_TOTALTAXAMOUNT': '0.00',
                          'M_IV_VIN': None,
                          'SIXT_VAT_ID': 'BE0465341266',
                          'TRIGGER_HIGHWAY': '0'}
                         )

    def test_get_false_order(self):
        m_cn_id = "7980166"
        barcode = "14968901"
        xml_invoice_header = XmlInvoiceHeader(m_cn_id=m_cn_id, barcode=barcode)
        xml_text = read_xml_file_to_str('xml_files/order_flase.xml')
        xml_invoice_data = get_xml_header(xml_text=xml_text,
                                          xml_invoice_data=xml_invoice_header, logger=Mock())
        self.assertEqual(xml_invoice_data.get_xml_header_attributes(),
                         {'EMAIL_NAME': None,
                          'HIGHWAY_ZEITSTEMPEL': None,
                          'M_CN_ID': '7980166',
                          'M_CN_MAIL_ID': None,
                          'M_IV_BARCODE': '14968901',
                          'M_IV_CONTRACTID': None,
                          'M_IV_CONTRACT_END': None,
                          'M_IV_CONTRACT_START': None,
                          'M_IV_COSTCENTER': None,
                          'M_IV_CURRENCY': 'EUR',
                          'M_IV_DAMAGENUMBER': None,
                          'M_IV_DELIVERYDATE': datetime(2026, 1, 12, 0, 0),
                          'M_IV_DELIVERYDATE_BIS': datetime(2026, 1, 12, 0, 0),
                          'M_IV_EMPFAENGER': None,
                          'M_IV_IBAN': 'BE62260003045061',
                          'M_IV_IMAGEPATH': '14968901.pdf',
                          'M_IV_INVOICEAMOUNT': '330.15',
                          'M_IV_INVOICEDATE': datetime(2026, 1, 12, 0, 0),
                          'M_IV_INVOICENUMBER': '1spi26010375',
                          'M_IV_INVOICETYPE': 'EKS',
                          'M_IV_KINDOFINVOICE': 'RE',
                          'M_IV_KREDITOR': None,
                          'M_IV_LICENSE_NUMBER': None,
                          'M_IV_MAIL_SUBJECT': None,
                          'M_IV_MANDANT': None,
                          'M_IV_ORDERID': None,
                          'M_IV_QUELLSYSTEM': 'eInvoice',
                          'M_IV_RECEIPTDATE': None,
                          'M_IV_SCANLOCATION': 'E-Mail',
                          'M_IV_TAXAMOUNT1': '69.33',
                          'M_IV_TAXAMOUNT2': None,
                          'M_IV_TAXAMOUNT3': None,
                          'M_IV_TAXAMOUNT4': None,
                          'M_IV_TAXAMOUNT5': None,
                          'M_IV_TAXRATE1': '21.0',
                          'M_IV_TAXRATE2': None,
                          'M_IV_TAXRATE3': None,
                          'M_IV_TAXRATE4': None,
                          'M_IV_TAXRATE5': None,
                          'M_IV_TOTALAMOUNT': '399.48',
                          'M_IV_TOTALTAXAMOUNT': '69.33',
                          'M_IV_VIN': None,
                          'SIXT_VAT_ID': 'BE0465341266',
                          'TRIGGER_HIGHWAY': '0'}
                         )


if __name__ == '__main__':
    unittest.main()
