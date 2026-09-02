import unittest
from typing import Optional

from app.helper_functions.einvoice_helper import read_xml_file_to_str
from app.invoice_handler.xml_pdf_extraction import get_pdf_file

# CII / XRechnung (CrossIndustryInvoice) stores supporting PDFs as
# ram:AdditionalReferencedDocument / ram:AttachmentBinaryObject — not the UBL
# AdditionalDocumentReference / EmbeddedDocumentBinaryObject path.
CII_WITH_PDF_ATTACHMENT: str = """<?xml version="1.0" encoding="utf-8"?>
<rsm:CrossIndustryInvoice
    xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100"
    xmlns:ram="urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100"
    xmlns:udt="urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100">
  <rsm:ExchangedDocument>
    <ram:ID>0090203385</ram:ID>
    <ram:TypeCode>380</ram:TypeCode>
  </rsm:ExchangedDocument>
  <rsm:SupplyChainTradeTransaction>
    <ram:ApplicableHeaderTradeAgreement>
      <ram:AdditionalReferencedDocument>
        <ram:IssuerAssignedID>0090203385-attch1</ram:IssuerAssignedID>
        <ram:TypeCode>916</ram:TypeCode>
        <ram:Name>timesheet.pdf</ram:Name>
        <ram:AttachmentBinaryObject mimeCode="application/pdf" filename="timesheet.pdf">JVBERi0xLjQKdGVzdA==</ram:AttachmentBinaryObject>
      </ram:AdditionalReferencedDocument>
    </ram:ApplicableHeaderTradeAgreement>
  </rsm:SupplyChainTradeTransaction>
</rsm:CrossIndustryInvoice>
"""


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

    def test_extract_cii_xrechnung_attachment(self) -> None:
        files: Optional[list] = get_pdf_file("123456", CII_WITH_PDF_ATTACHMENT)
        self.assertIsNotNone(files)
        self.assertGreaterEqual(len(files), 1)
        first: dict = files[0]
        self.assertEqual(first["invoice_id"], "123456")
        self.assertEqual(first["file_name"], "timesheet.pdf")
        self.assertEqual(first["file_type"], "pdf")
        self.assertEqual(first["attachment"], "JVBERi0xLjQKdGVzdA==")

    def test_extract_cii_attachment_from_sample_file(self) -> None:
        xml_text: Optional[str] = read_xml_file_to_str("xml_files/CIIAttachment.xml")
        if not xml_text or not xml_text.strip():
            self.skipTest("CIIAttachment.xml is empty; save the CII/XRechnung sample first")
        files: Optional[list] = get_pdf_file("123456", xml_text)
        self.assertIsNotNone(files)
        self.assertGreaterEqual(len(files), 1)
        first: dict = files[0]
        self.assertEqual(first["invoice_id"], "123456")
        self.assertIn("attachment", first)
        self.assertIn("file_name", first)
        self.assertIn("file_type", first)
        self.assertTrue(first["attachment"])
        self.assertEqual(first["file_type"], "pdf")

    def test_no_attachment_returns_empty_or_none(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/xml_text_from_zugpferd.xml")
        files: Optional[list] = get_pdf_file("1", xml_text)
        self.assertTrue(files is None or files == [])


if __name__ == "__main__":
    unittest.main()
