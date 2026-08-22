"""Working-copy PDF from parsed invoice DTO."""

from __future__ import annotations

import io
import unittest
import zipfile
from datetime import datetime, timezone
from typing import Optional

from PyPDF2 import PdfReader
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.invoice import (
    InvoiceParseResponse,
    InvoiceTotals,
    LineItem,
    PartyInfo,
    ParseStatus,
    TaxBreakdown,
    ValidationIssue,
    ValidationStatus,
)
from app.services.view_pdf_service import (
    ViewPdfService,
    build_batch_view_pdf_filename,
    build_view_pdf_filename,
    invoice_is_viewable,
)


def _sample_invoice() -> InvoiceParseResponse:
    return InvoiceParseResponse(
        status=ParseStatus.SUCCESS,
        message="ok",
        filename="sample.xml",
        file_type="xrechnung_xml",
        document_type="invoice",
        invoice_number="2025/10294",
        issue_date="2025-01-31",
        due_date="2025-02-14",
        seller=PartyInfo(
            name="KMLZ Rechtsanwaltsges. mbH",
            address="Musterstraße 1, 80331 München",
            vat_id="DE814742004",
            iban="DE95700400410228840500",
        ),
        buyer=PartyInfo(name="Buyer AG", vat_id="DE123"),
        totals=InvoiceTotals(
            net=227.5,
            tax=43.23,
            gross=270.73,
            currency="EUR",
            tax_breakdown=[TaxBreakdown(rate=19, amount=43.23)],
        ),
        line_items=[
            LineItem(
                position=1,
                description="Beratung",
                quantity=1,
                unit="HUR",
                unit_price=227.5,
                tax_rate=19.0,
                net_amount=227.5,
                gross_amount=270.73,
            )
        ],
        payment_reference="REF-1",
        validation_status=ValidationStatus.VALID,
    )


def _pdf_text(content: bytes) -> str:
    reader: PdfReader = PdfReader(io.BytesIO(content))
    pages: list[str] = []
    for page in reader.pages:
        extracted: Optional[str] = page.extract_text()
        if extracted:
            pages.append(extracted)
    return "\n".join(pages)


class TestViewPdfService(unittest.TestCase):
    def setUp(self) -> None:
        self.service: ViewPdfService = ViewPdfService()
        self.invoice: InvoiceParseResponse = _sample_invoice()

    def test_filename_convention(self) -> None:
        name: str = build_view_pdf_filename(self.invoice)
        self.assertTrue(name.startswith("lesbare_"))
        self.assertTrue(name.endswith(".pdf"))
        self.assertIn("KMLZ", name)
        self.assertIn("20250131", name)

    def test_error_invoice_is_not_viewable(self) -> None:
        invoice: InvoiceParseResponse = InvoiceParseResponse(
            status=ParseStatus.ERROR,
            message="unreadable",
            filename="bad.xml",
        )
        self.assertFalse(invoice_is_viewable(invoice))
        with self.assertRaises(ValueError):
            self.service.render(invoice)

    def test_pdf_contains_readable_fields_and_disclaimer(self) -> None:
        content, media, filename = self.service.render(self.invoice)
        self.assertEqual(media, "application/pdf")
        self.assertTrue(filename.endswith(".pdf"))
        self.assertTrue(content.startswith(b"%PDF"))
        text: str = _pdf_text(content)
        self.assertIn("EINVOICE", text.replace(" ", ""))
        self.assertIn("keine Originalrechnung", text)
        self.assertIn("2025/10294", text)
        self.assertIn("KMLZ", text)
        self.assertIn("Beratung", text)
        self.assertIn("270,73", text)
        self.assertIn("DE95 7004 0041 0228 8405 00", text)

    def test_invalid_invoice_still_renders(self) -> None:
        invoice: InvoiceParseResponse = _sample_invoice()
        invoice.status = ParseStatus.PARTIAL
        invoice.validation_status = ValidationStatus.INVALID
        invoice.validation_issues = [
            ValidationIssue(
                level="error",
                category="business",
                code="BT-1_MISSING",
                message="Rechnungsnummer fehlt.",
            )
        ]
        content, media, _filename = self.service.render(invoice)
        self.assertEqual(media, "application/pdf")
        text: str = _pdf_text(content)
        self.assertIn("ungültig", text)

    def test_batch_zip_contains_one_pdf_per_invoice(self) -> None:
        second: InvoiceParseResponse = _sample_invoice()
        second.invoice_number = "2025/10295"
        second.filename = "two.xml"
        content, media, filename = self.service.render_batch(
            [self.invoice, second],
            datetime(2026, 8, 22, tzinfo=timezone.utc),
        )
        self.assertEqual(media, "application/zip")
        self.assertEqual(filename, build_batch_view_pdf_filename(datetime(2026, 8, 22, tzinfo=timezone.utc), 2))
        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            names: list[str] = archive.namelist()
            self.assertEqual(len(names), 2)
            self.assertTrue(all(name.endswith(".pdf") for name in names))
            self.assertTrue(archive.read(names[0]).startswith(b"%PDF"))


class TestViewPdfApi(unittest.TestCase):
    def setUp(self) -> None:
        self.client: TestClient = TestClient(app)

    def test_view_pdf_endpoint(self) -> None:
        response = self.client.post(
            "/api/invoices/export/view-pdf",
            json={"invoice": _sample_invoice().model_dump(mode="json")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response.headers["content-type"])
        self.assertIn("lesbare_", response.headers.get("content-disposition", ""))
        self.assertTrue(response.content.startswith(b"%PDF"))

    def test_error_invoice_is_rejected(self) -> None:
        invoice: InvoiceParseResponse = InvoiceParseResponse(
            status=ParseStatus.ERROR,
            message="unreadable",
            filename="bad.xml",
            validation_status=ValidationStatus.INVALID,
        )
        response = self.client.post(
            "/api/invoices/export/view-pdf",
            json={"invoice": invoice.model_dump(mode="json")},
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
