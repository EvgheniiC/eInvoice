import base64
import csv
import io
import unittest
import zipfile
from pathlib import Path

from fastapi.testclient import TestClient
from openpyxl import load_workbook

from app.main import app
from app.schemas.export import EXPORT_COLUMNS, ExportFormat
from app.schemas.invoice import (
    InvoiceParseResponse,
    InvoiceTotals,
    LineItem,
    MismatchField,
    PartyInfo,
    ParseStatus,
    ValidationStatus,
)
from app.services.export_service import (
    ExportService,
    build_export_filename,
    build_flat_rows,
    build_package_filename,
    build_package_summary,
)


def _sample_invoice() -> InvoiceParseResponse:
    return InvoiceParseResponse(
        status=ParseStatus.SUCCESS,
        message="ok",
        filename="sample.xml",
        file_type="xrechnung_xml",
        invoice_number="2025/10294",
        issue_date="2025-01-31",
        due_date="2025-01-31",
        seller=PartyInfo(
            name="KMLZ Rechtsanwaltsges. mbH",
            vat_id="DE814742004",
            iban="DE95700400410228840500",
        ),
        buyer=PartyInfo(name="Buyer AG", vat_id="DE123"),
        totals=InvoiceTotals(net=227.5, tax=43.23, gross=270.73, currency="EUR"),
        line_items=[
            LineItem(
                position=1,
                description="Beratung",
                quantity=1,
                unit_price=227.5,
                tax_rate=19.0,
                net_amount=227.5,
            )
        ],
        payment_reference="REF-1",
    )


class TestExportService(unittest.TestCase):
    def setUp(self) -> None:
        self.service: ExportService = ExportService()
        self.invoice: InvoiceParseResponse = _sample_invoice()

    def test_filename_convention(self) -> None:
        name: str = build_export_filename(self.invoice, ExportFormat.CSV)
        self.assertTrue(name.endswith(".csv"))
        self.assertIn("2025", name)
        self.assertIn("20250131", name)
        self.assertIn("KMLZ", name)

    def test_csv_columns_and_row(self) -> None:
        content, media, filename = self.service.export(self.invoice, ExportFormat.CSV)
        self.assertIn("text/csv", media)
        self.assertTrue(filename.endswith(".csv"))
        text: str = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        self.assertEqual(list(reader.fieldnames or []), EXPORT_COLUMNS)
        rows = list(reader)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["invoice_number"], "2025/10294")
        self.assertEqual(rows[0]["gross"], "270.73")
        self.assertEqual(rows[0]["line_description"], "Beratung")

    def test_excel_sheets(self) -> None:
        content, media, filename = self.service.export(self.invoice, ExportFormat.EXCEL)
        self.assertIn("spreadsheetml", media)
        self.assertTrue(filename.endswith(".xlsx"))
        workbook = load_workbook(io.BytesIO(content))
        self.assertEqual(set(workbook.sheetnames), {"Invoice", "Lines", "Flat"})
        self.assertGreaterEqual(workbook["Lines"].max_row, 2)

    def test_datev_german_decimal_and_encoding(self) -> None:
        content, media, filename = self.service.export(self.invoice, ExportFormat.DATEV)
        self.assertTrue(filename.startswith("datev_"))
        text: str = content.decode("cp1252")
        self.assertIn("270,73", text)
        self.assertIn("2025/10294", text)
        self.assertIn("S;", text.replace("\r\n", "\n") or "S")

    def test_empty_optional_fields_safe(self) -> None:
        invoice: InvoiceParseResponse = InvoiceParseResponse(
            status=ParseStatus.PARTIAL,
            message="partial",
            filename="x.xml",
            invoice_number="1",
            totals=InvoiceTotals(gross=10.0, currency="EUR"),
            line_items=[],
        )
        rows = build_flat_rows(invoice)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["seller_name"], "")
        self.assertEqual(rows[0]["line_description"], "")

    def test_accountant_package_zip_contents(self) -> None:
        pdf_bytes: bytes = b"%PDF-1.4 minimal test pdf"
        content, media, filename = self.service.build_accountant_package(
            invoice=self.invoice,
            pdf_bytes=pdf_bytes,
            pdf_filename="Beleg_Test.PDF",
        )
        self.assertEqual(media, "application/zip")
        self.assertTrue(filename.startswith("buchhaltung_"))
        self.assertTrue(filename.endswith(".zip"))

        with zipfile.ZipFile(io.BytesIO(content)) as archive:
            names: list[str] = sorted(archive.namelist())
            self.assertIn("summary.txt", names)
            self.assertTrue(any(name.endswith(".xlsx") for name in names))
            self.assertTrue(any(name.startswith("datev_") for name in names))
            self.assertIn("Beleg_Test.pdf", names)
            summary: str = archive.read("summary.txt").decode("utf-8")
            self.assertIn("2025/10294", summary)
            self.assertIn("270,73", summary)

    def test_package_summary_mismatch_line(self) -> None:
        invoice: InvoiceParseResponse = _sample_invoice()
        invoice.file_type = "zugferd_pdf"
        invoice.validation_status = ValidationStatus.WARNING
        invoice.mismatch_fields = [
            MismatchField(
                field="gross",
                label="Brutto",
                xml_value="100.00",
                pdf_value="99.00",
                matched=False,
            )
        ]
        text: str = build_package_summary(invoice)
        self.assertIn("Abweichung (Brutto)", text)
        self.assertEqual(
            build_package_filename(invoice),
            "buchhaltung_KMLZ_Rechtsanwaltsges_mbH_2025_10294_20250131.zip",
        )


class TestExportApi(unittest.TestCase):
    def setUp(self) -> None:
        self.client: TestClient = TestClient(app)

    def test_export_csv_endpoint(self) -> None:
        response = self.client.post(
            "/api/invoices/export",
            json={"format": "csv", "invoice": _sample_invoice().model_dump(mode="json")},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/csv", response.headers["content-type"])
        self.assertIn("attachment", response.headers.get("content-disposition", ""))

    def test_export_mapping_docs(self) -> None:
        response = self.client.get("/api/invoices/export/mapping")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertGreaterEqual(len(data), 3)

    def test_parse_then_export_roundtrip(self) -> None:
        fixtures: Path = Path(__file__).parent / "xml_files" / "xml_text_from_zugpferd.xml"
        parse_response = self.client.post(
            "/api/invoices/parse",
            files={"file": ("sample.xml", fixtures.read_bytes(), "application/xml")},
        )
        self.assertEqual(parse_response.status_code, 200)
        invoice = parse_response.json()
        export_response = self.client.post(
            "/api/invoices/export",
            json={"format": "excel", "invoice": invoice},
        )
        self.assertEqual(export_response.status_code, 200)
        self.assertTrue(len(export_response.content) > 100)

    def test_accountant_package_endpoint(self) -> None:
        pdf_b64: str = base64.b64encode(b"%PDF-1.4 package").decode("ascii")
        response = self.client.post(
            "/api/invoices/export/accountant-package",
            json={
                "invoice": _sample_invoice().model_dump(mode="json"),
                "pdf_base64": pdf_b64,
                "pdf_filename": "original.pdf",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/zip", response.headers["content-type"])
        self.assertIn("buchhaltung_", response.headers.get("content-disposition", ""))
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            self.assertIn("summary.txt", archive.namelist())
            self.assertIn("original.pdf", archive.namelist())


if __name__ == "__main__":
    unittest.main()
