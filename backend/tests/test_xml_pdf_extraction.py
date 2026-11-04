import unittest
from typing import Optional

from app.helper_functions.einvoice_helper import read_xml_file_to_str
from unittest.mock import patch

from app.invoice_handler.xml_pdf_extraction import (
    MAX_EMBEDDED_DOCUMENT_BYTES,
    ExtractedEmbeddedFile,
    extract_embedded_files,
    get_pdf_file,
)

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

    def test_extracts_pdf_and_png_from_one_invoice(self) -> None:
        xml_text: str = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:ID>RE-1</cbc:ID>
  <cac:AdditionalDocumentReference>
    <cbc:ID>att-1</cbc:ID>
    <cac:Attachment>
      <cbc:EmbeddedDocumentBinaryObject mimeCode="application/pdf" filename="rechnung.pdf">JVBERi0xLjQKdGVzdA==</cbc:EmbeddedDocumentBinaryObject>
    </cac:Attachment>
  </cac:AdditionalDocumentReference>
  <cac:AdditionalDocumentReference>
    <cbc:ID>att-2</cbc:ID>
    <cac:Attachment>
      <cbc:EmbeddedDocumentBinaryObject mimeCode="image/png" filename="foto.png">iVBORw0KGgo=</cbc:EmbeddedDocumentBinaryObject>
    </cac:Attachment>
  </cac:AdditionalDocumentReference>
</Invoice>
"""
        files: list[ExtractedEmbeddedFile] = extract_embedded_files(xml_text)
        self.assertEqual(len(files), 2)
        self.assertEqual(files[0].filename, "rechnung.pdf")
        self.assertEqual(files[0].media_type, "application/pdf")
        self.assertEqual(files[0].content_base64, "JVBERi0xLjQKdGVzdA==")
        self.assertGreater(files[0].size_bytes, 0)
        self.assertEqual(files[1].filename, "foto.png")
        self.assertEqual(files[1].media_type, "image/png")
        self.assertEqual(files[1].content_base64, "iVBORw0KGgo=")

    def test_credit_note_attachment_is_read(self) -> None:
        xml_text: str = """<?xml version="1.0" encoding="UTF-8"?>
<CreditNote xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cac:AdditionalDocumentReference>
    <cac:Attachment>
      <cbc:EmbeddedDocumentBinaryObject mimeCode="text/csv" filename="liste.csv">QQ==</cbc:EmbeddedDocumentBinaryObject>
    </cac:Attachment>
  </cac:AdditionalDocumentReference>
</CreditNote>
"""
        files: list[ExtractedEmbeddedFile] = extract_embedded_files(xml_text)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].filename, "liste.csv")
        self.assertEqual(files[0].media_type, "text/csv")
        self.assertEqual(files[0].content_base64, "QQ==")

    def test_oversized_attachment_keeps_metadata_without_bytes(self) -> None:
        xml_text: str = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cac:AdditionalDocumentReference>
    <cac:Attachment>
      <cbc:EmbeddedDocumentBinaryObject mimeCode="application/pdf" filename="gross.pdf">JVBERi0xLjQKdGVzdA==</cbc:EmbeddedDocumentBinaryObject>
    </cac:Attachment>
  </cac:AdditionalDocumentReference>
</Invoice>
"""
        with patch(
            "app.invoice_handler.xml_pdf_extraction.MAX_EMBEDDED_DOCUMENT_BYTES",
            4,
        ):
            files: list[ExtractedEmbeddedFile] = extract_embedded_files(xml_text)
        self.assertEqual(len(files), 1)
        self.assertIsNone(files[0].content_base64)
        self.assertGreater(files[0].size_bytes, 4)
        self.assertEqual(files[0].filename, "gross.pdf")
        self.assertLess(files[0].size_bytes, MAX_EMBEDDED_DOCUMENT_BYTES)

    def test_no_attachment_returns_empty_or_none(self) -> None:
        xml_text: str = read_xml_file_to_str("xml_files/xml_text_from_zugpferd.xml")
        files: Optional[list] = get_pdf_file("1", xml_text)
        self.assertTrue(files is None or files == [])


if __name__ == "__main__":
    unittest.main()
