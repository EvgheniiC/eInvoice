import unittest
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.schemas.invoice import ParseStatus, ValidationStatus
from app.services.en16931_validator import ValidationResult
from app.services.invoice_service import InvoiceService


class TestInvoiceService(unittest.TestCase):
    def setUp(self) -> None:
        self.service: InvoiceService = InvoiceService()
        self.fixtures: Path = Path(__file__).parent / "xml_files"

    def test_parse_xml_sample_success_or_partial(self) -> None:
        xml_path: Path = self.fixtures / "xml_text_from_zugpferd.xml"
        content: bytes = xml_path.read_bytes()
        result = self.service.parse_upload(filename=xml_path.name, content=content)

        self.assertIn(result.status.value, ("success", "partial"))
        self.assertEqual(result.file_type, "xrechnung_xml")
        self.assertEqual(result.invoice_number, "2025/10294")
        self.assertIsNotNone(result.totals)
        self.assertEqual(result.totals.currency, "EUR")
        self.assertEqual(result.totals.gross, Decimal("270.73"))
        self.assertGreater(len(result.line_items), 0)

    @patch("app.services.invoice_service.validate_invoice")
    def test_parse_returns_every_embedded_file(self, validate: MagicMock) -> None:
        validate.return_value = ValidationResult(status=ValidationStatus.NOT_CHECKED)
        content: bytes = """<?xml version="1.0" encoding="UTF-8"?>
<Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"
 xmlns:cac="urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
 xmlns:cbc="urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2">
  <cbc:ID>RE-ATT</cbc:ID>
  <cac:AdditionalDocumentReference>
    <cac:Attachment>
      <cbc:EmbeddedDocumentBinaryObject mimeCode="application/pdf" filename="rechnung.pdf">JVBERi0xLjQKdGVzdA==</cbc:EmbeddedDocumentBinaryObject>
    </cac:Attachment>
  </cac:AdditionalDocumentReference>
  <cac:AdditionalDocumentReference>
    <cac:Attachment>
      <cbc:EmbeddedDocumentBinaryObject mimeCode="image/png" filename="foto.png">iVBORw0KGgo=</cbc:EmbeddedDocumentBinaryObject>
    </cac:Attachment>
  </cac:AdditionalDocumentReference>
</Invoice>
""".encode("utf-8")
        result = self.service.parse_upload(filename="with-attachment.xml", content=content)
        self.assertIn(result.status, {ParseStatus.SUCCESS, ParseStatus.PARTIAL})
        self.assertEqual(
            [item.filename for item in result.embedded_documents],
            ["rechnung.pdf", "foto.png"],
        )
        self.assertEqual(result.embedded_documents[0].media_type, "application/pdf")
        self.assertEqual(result.embedded_documents[0].content_base64, "JVBERi0xLjQKdGVzdA==")
        self.assertEqual(result.embedded_documents[1].media_type, "image/png")
        self.assertTrue(result.embedded_documents[1].content_base64)

    def test_parse_unsupported_extension(self) -> None:
        result = self.service.parse_upload(filename="note.txt", content=b"hello")
        self.assertEqual(result.status.value, "error")
        self.assertEqual(result.file_type, "unsupported")

    def test_opentrans_xml_rejected_with_clear_message(self) -> None:
        xml_path: Path = self.fixtures / "0426477394-207600RECHNUNG1.xml"
        if not xml_path.exists():
            self.skipTest("local openTRANS fixture not present")

        result = self.service.parse_upload(
            filename=xml_path.name,
            content=xml_path.read_bytes(),
        )
        self.assertEqual(result.status, ParseStatus.ERROR)
        self.assertEqual(result.file_type, "opentrans_xml")
        self.assertTrue(
            any(issue.code == "UNSUPPORTED_OPENTRANS" for issue in result.validation_issues)
        )
        self.assertIn("openTRANS", result.message)
        self.assertTrue(
            any("openTRANS" in step for step in result.next_steps),
            msg=result.next_steps,
        )

    def test_unknown_xml_format_rejected_with_clear_message(self) -> None:
        content: bytes = (
            b'<?xml version="1.0" encoding="UTF-8"?>\n'
            b"<CustomInvoice><Id>1</Id></CustomInvoice>\n"
        )
        result = self.service.parse_upload(filename="custom.xml", content=content)
        self.assertEqual(result.status, ParseStatus.ERROR)
        self.assertEqual(result.file_type, "unsupported_xml")
        self.assertTrue(
            any(issue.code == "UNSUPPORTED_XML_FORMAT" for issue in result.validation_issues)
        )
        self.assertIn("XRechnung", result.message)


if __name__ == "__main__":
    unittest.main()
