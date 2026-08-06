import unittest
from pathlib import Path

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
        self.assertAlmostEqual(result.totals.gross or 0.0, 270.73, places=2)
        self.assertGreater(len(result.line_items), 0)

    def test_parse_unsupported_extension(self) -> None:
        result = self.service.parse_upload(filename="note.txt", content=b"hello")
        self.assertEqual(result.status.value, "error")
        self.assertEqual(result.file_type, "unsupported")


if __name__ == "__main__":
    unittest.main()
