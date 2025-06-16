import unittest
from scr.invoice_handler.xml_pdf_extraction import get_pdf_file
from .test_helper import xml_from_pdf_extraction


class TestXmlPDFExtraction(unittest.TestCase):
    def test_get_xml_pdf_extraction_all(self):
        m_cn_id = "123456"
        file: dict = get_pdf_file(m_cn_id, xml_from_pdf_extraction)
        self.assertEqual(file, [{'M_CN_ID': '123456',
                                 'ATTACHMENT': 'JVBERi0xLjUNCiW1tbW1DQoxIDAgb2JqDQo8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFIvTGFuZyhkZS1ERSkgL1N0cnVjdFRyZWVSb290IDEwIDAgUi9NYXJrSW5mbzw8L01hcmtlZCB0cnVlPj4wvU2l6ZSAyMC9Sb290IDEgMCBPDVEMjQ1NTY4ODNFQ0FBNDFCMDM0N0E2RjAzMjFBNDBDPjw1RDI0NTU2ODgzRUNBQTQxQjAzNDdBNkYwMzIxQTQwQz5dIC9QcmV2IDE0OTM5MC9YUmVmU3RtIDE0OTExMz4+DQpzdGFydHhyZWYNCjE0OTk0Nw0KJSVFT0Y=',
                                 'FILE_NAME': '01_15_Anhang_01.pdf', 'FILE_TYPE': 'pdf'}]
                         )
