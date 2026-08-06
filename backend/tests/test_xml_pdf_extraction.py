import unittest

from app.helper_functions.einvoice_helper import read_xml_file_to_str
from app.invoice_handler.xml_pdf_extraction import get_pdf_file


class TestXmlPdfExtraction(unittest.TestCase):
    def test_extract_single_attachment(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/xmls_attachment.xml")
        files: list = get_pdf_file("123456", xml_text)
        self.assertIsNotNone(files)
        self.assertGreaterEqual(len(files), 1)
        first: dict = files[0]
        self.assertEqual(first["invoice_id"], "123456")
        self.assertIn("attachment", first)
        self.assertIn("file_name", first)
        self.assertIn("file_type", first)
        legacy_id: str = "M_" + "CN_" + "ID"
        self.assertNotIn(legacy_id, first)
        self.assertTrue(first["attachment"])

    def test_no_attachment_returns_empty_or_none(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/xml_text_from_zugpferd.xml")
        files = get_pdf_file("1", xml_text)
        self.assertTrue(files is None or files == [])


if __name__ == "__main__":
    unittest.main()
