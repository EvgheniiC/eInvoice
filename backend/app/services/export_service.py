import base64
import binascii
import csv
import io
import re
import zipfile
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from app.schemas.export import DATEV_COLUMNS, EXPORT_COLUMNS, ExportFormat
from app.schemas.invoice import InvoiceParseResponse, LineItem, MismatchField, ValidationMeta
from app.services.validation_report import (
    build_validation_report,
    build_validation_report_filename,
)

MAX_PACKAGE_PDF_BYTES: int = 12 * 1024 * 1024


class ExportService:
    """Build CSV / Excel / DATEV files from the public invoice DTO."""

    def export(self, invoice: InvoiceParseResponse, export_format: ExportFormat) -> Tuple[bytes, str, str]:
        """
        Return (file_bytes, media_type, download_filename).
        """
        filename: str = build_export_filename(invoice=invoice, export_format=export_format)

        if export_format == ExportFormat.CSV:
            return self._to_csv(invoice), "text/csv; charset=utf-8", filename
        if export_format == ExportFormat.EXCEL:
            return (
                self._to_excel(invoice),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename,
            )
        if export_format == ExportFormat.DATEV:
            return self._to_datev(invoice), "text/csv; charset=cp1252", filename
        raise ValueError(f"Unsupported export format: {export_format}")

    def build_accountant_package(
        self,
        invoice: InvoiceParseResponse,
        pdf_bytes: Optional[bytes] = None,
        pdf_filename: Optional[str] = None,
    ) -> Tuple[bytes, str, str]:
        """
        ZIP for Steuerberater: summary.txt + Prüfbericht + Excel + DATEV + optional visual PDF.
        Returns (zip_bytes, media_type, download_filename).
        """
        if pdf_bytes is not None and len(pdf_bytes) > MAX_PACKAGE_PDF_BYTES:
            raise ValueError(
                f"PDF zu groß für das Paket (max. {MAX_PACKAGE_PDF_BYTES // (1024 * 1024)} MB)."
            )

        buffer: io.BytesIO = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("summary.txt", build_package_summary(invoice))
            archive.writestr(
                build_validation_report_filename(invoice),
                build_validation_report(invoice),
            )

            excel_bytes, _, excel_name = self.export(invoice, ExportFormat.EXCEL)
            archive.writestr(excel_name, excel_bytes)

            datev_bytes, _, datev_name = self.export(invoice, ExportFormat.DATEV)
            archive.writestr(datev_name, datev_bytes)

            if pdf_bytes:
                member_name: str = _package_pdf_member_name(invoice, pdf_filename)
                archive.writestr(member_name, pdf_bytes)

        zip_name: str = build_package_filename(invoice)
        return buffer.getvalue(), "application/zip", zip_name

    def _to_csv(self, invoice: InvoiceParseResponse) -> bytes:
        buffer: io.StringIO = io.StringIO()
        writer: csv.DictWriter = csv.DictWriter(
            buffer,
            fieldnames=EXPORT_COLUMNS,
            extrasaction="ignore",
            lineterminator="\n",
        )
        writer.writeheader()
        for row in build_flat_rows(invoice):
            writer.writerow(row)
        # UTF-8 BOM helps Excel on Windows open umlauts correctly
        return ("\ufeff" + buffer.getvalue()).encode("utf-8")

    def _to_excel(self, invoice: InvoiceParseResponse) -> bytes:
        workbook: Workbook = Workbook()
        header_sheet: Worksheet = workbook.active
        header_sheet.title = "Invoice"

        header_rows: List[Tuple[str, Optional[str]]] = [
            ("invoice_number", invoice.invoice_number),
            ("issue_date", invoice.issue_date),
            ("due_date", invoice.due_date),
            ("seller_name", invoice.seller.name if invoice.seller else None),
            ("seller_vat_id", invoice.seller.vat_id if invoice.seller else None),
            ("seller_iban", invoice.seller.iban if invoice.seller else None),
            ("buyer_name", invoice.buyer.name if invoice.buyer else None),
            ("buyer_vat_id", invoice.buyer.vat_id if invoice.buyer else None),
            ("currency", invoice.totals.currency if invoice.totals else None),
            ("net", _num_str(invoice.totals.net if invoice.totals else None)),
            ("tax", _num_str(invoice.totals.tax if invoice.totals else None)),
            ("gross", _num_str(invoice.totals.gross if invoice.totals else None)),
            ("payment_reference", invoice.payment_reference),
        ]
        header_sheet.append(["field", "value"])
        for key, value in header_rows:
            header_sheet.append([key, value if value is not None else ""])

        lines_sheet: Worksheet = workbook.create_sheet("Lines")
        lines_sheet.append(
            [
                "position",
                "description",
                "quantity",
                "unit",
                "unit_price",
                "tax_rate",
                "net_amount",
                "gross_amount",
            ]
        )
        for item in invoice.line_items:
            lines_sheet.append(
                [
                    item.position,
                    item.description or "",
                    item.quantity,
                    item.unit or "",
                    item.unit_price,
                    item.tax_rate,
                    item.net_amount,
                    item.gross_amount,
                ]
            )

        flat_sheet: Worksheet = workbook.create_sheet("Flat")
        flat_sheet.append(EXPORT_COLUMNS)
        for row in build_flat_rows(invoice):
            flat_sheet.append([row.get(col, "") for col in EXPORT_COLUMNS])

        output: io.BytesIO = io.BytesIO()
        workbook.save(output)
        return output.getvalue()

    def _to_datev(self, invoice: InvoiceParseResponse) -> bytes:
        """
        Minimal DATEV Buchungsstapel CSV:
        - semicolon separator
        - German decimal comma
        - CP1252 encoding
        - one Soll line for gross amount
        """
        buffer: io.StringIO = io.StringIO()
        writer: csv.DictWriter = csv.DictWriter(
            buffer,
            fieldnames=DATEV_COLUMNS,
            delimiter=";",
            extrasaction="ignore",
            lineterminator="\r\n",
            quoting=csv.QUOTE_MINIMAL,
        )
        writer.writeheader()
        writer.writerow(build_datev_row(invoice))
        return buffer.getvalue().encode("cp1252", errors="replace")


def build_flat_rows(invoice: InvoiceParseResponse) -> List[Dict[str, Any]]:
    """One export row per line item; header fields repeated. Empty line if no positions."""
    base: Dict[str, Any] = {
        "invoice_number": invoice.invoice_number or "",
        "issue_date": invoice.issue_date or "",
        "due_date": invoice.due_date or "",
        "seller_name": invoice.seller.name if invoice.seller and invoice.seller.name else "",
        "seller_vat_id": invoice.seller.vat_id if invoice.seller and invoice.seller.vat_id else "",
        "seller_iban": invoice.seller.iban if invoice.seller and invoice.seller.iban else "",
        "buyer_name": invoice.buyer.name if invoice.buyer and invoice.buyer.name else "",
        "buyer_vat_id": invoice.buyer.vat_id if invoice.buyer and invoice.buyer.vat_id else "",
        "currency": invoice.totals.currency if invoice.totals and invoice.totals.currency else "",
        "net": _num_str(invoice.totals.net if invoice.totals else None),
        "tax": _num_str(invoice.totals.tax if invoice.totals else None),
        "gross": _num_str(invoice.totals.gross if invoice.totals else None),
        "payment_reference": invoice.payment_reference or "",
    }

    items: List[LineItem] = invoice.line_items
    if not items:
        row: Dict[str, Any] = dict(base)
        row.update(
            {
                "line_position": "",
                "line_description": "",
                "line_quantity": "",
                "line_unit": "",
                "line_unit_price": "",
                "line_tax_rate": "",
                "line_net_amount": "",
            }
        )
        return [row]

    rows: List[Dict[str, Any]] = []
    for item in items:
        row = dict(base)
        row.update(
            {
                "line_position": item.position if item.position is not None else "",
                "line_description": item.description or "",
                "line_quantity": _num_str(item.quantity),
                "line_unit": item.unit or "",
                "line_unit_price": _num_str(item.unit_price),
                "line_tax_rate": _num_str(item.tax_rate),
                "line_net_amount": _num_str(item.net_amount),
            }
        )
        rows.append(row)
    return rows


def build_datev_row(invoice: InvoiceParseResponse) -> Dict[str, str]:
    amount: Optional[Decimal] = invoice.totals.gross if invoice.totals else None
    seller_name: str = invoice.seller.name if invoice.seller and invoice.seller.name else "Lieferant"
    invoice_no: str = invoice.invoice_number or ""
    booking_text: str = f"{seller_name} {invoice_no}".strip()[:60]
    belegdatum: str = _datev_date(invoice.issue_date)
    currency: str = (
        invoice.totals.currency if invoice.totals and invoice.totals.currency else "EUR"
    )

    return {
        "Umsatz": _de_amount(amount),
        "Soll/Haben-Kennzeichen": "S",
        "WKZ Umsatz": currency,
        "Kurs": "",
        "Basis-Umsatz": "",
        "WKZ Basis-Umsatz": "",
        "Konto": "",
        "Gegenkonto (ohne BU-Schlüssel)": "",
        "BU-Schlüssel": "",
        "Belegdatum": belegdatum,
        "Belegfeld 1": invoice_no[:36],
        "Belegfeld 2": "",
        "Skonto": "",
        "Buchungstext": booking_text,
    }


def build_export_filename(invoice: InvoiceParseResponse, export_format: ExportFormat) -> str:
    """Filename convention: supplier_invoiceNo_date.ext"""
    supplier: str = _slug(invoice.seller.name if invoice.seller else None) or "supplier"
    number: str = _slug(invoice.invoice_number) or "invoice"
    date_part: str = (invoice.issue_date or "nodate").replace("-", "")
    extension: str = {
        ExportFormat.CSV: "csv",
        ExportFormat.EXCEL: "xlsx",
        ExportFormat.DATEV: "csv",
    }[export_format]
    prefix: str = "datev_" if export_format == ExportFormat.DATEV else ""
    return f"{prefix}{supplier}_{number}_{date_part}.{extension}"


def build_package_filename(invoice: InvoiceParseResponse) -> str:
    """ZIP filename: buchhaltung_supplier_invoiceNo_date.zip"""
    supplier: str = _slug(invoice.seller.name if invoice.seller else None) or "supplier"
    number: str = _slug(invoice.invoice_number) or "invoice"
    date_part: str = (invoice.issue_date or "nodate").replace("-", "")
    return f"buchhaltung_{supplier}_{number}_{date_part}.zip"


def build_package_summary(invoice: InvoiceParseResponse) -> str:
    """Short German summary for the accountant package."""
    currency: str = (
        invoice.totals.currency if invoice.totals and invoice.totals.currency else "EUR"
    )
    net: str = _de_amount(invoice.totals.net if invoice.totals else None) or "—"
    tax: str = _de_amount(invoice.totals.tax if invoice.totals else None) or "—"
    gross: str = _de_amount(invoice.totals.gross if invoice.totals else None) or "—"
    seller_name: str = invoice.seller.name if invoice.seller and invoice.seller.name else "—"
    seller_iban: str = invoice.seller.iban if invoice.seller and invoice.seller.iban else "—"
    buyer_name: str = invoice.buyer.name if invoice.buyer and invoice.buyer.name else "—"
    mismatch_line: str = _mismatch_summary_line(invoice)

    lines: List[str] = [
        "Buchhaltungspaket — eInvoice",
        "============================",
        "",
        f"Rechnung: {invoice.invoice_number or '—'}",
        f"Datum: {invoice.issue_date or '—'}",
        f"Fälligkeitsdatum: {invoice.due_date or '—'}",
        f"Zahlungsreferenz: {invoice.payment_reference or '—'}",
        f"Quelldatei: {invoice.filename}",
        f"Typ: {invoice.file_type or '—'}",
        "",
        f"Lieferant: {seller_name}",
        f"IBAN: {seller_iban}",
        f"Empfänger: {buyer_name}",
        "",
        f"Netto: {net} {currency}",
        f"MwSt: {tax} {currency}",
        f"Brutto: {gross} {currency}",
        "",
        f"Parse-Status: {invoice.status.value}",
        f"Prüfung: {invoice.validation_status.value}",
        f"Standard: {invoice.validation_meta.standard_version or '—'}",
        f"Profil: {invoice.validation_meta.profile or '—'}",
        f"Prüfengine: {_validation_engine_line(invoice)}",
        f"PDF↔XML: {mismatch_line}",
        "",
        "Inhalt dieses ZIP:",
        "- summary.txt (diese Datei)",
        "- Prüfbericht (für Lieferant oder Steuerberater)",
        "- Excel-Export (Übersicht + Positionen)",
        "- DATEV-Export (Buchungsvorschlag)",
        "- optionale visuelle PDF (bei ZUGFeRD)",
        "",
        "Hinweis: Die Prüfung betrifft Schema-/Standardkonformität.",
        "Die Entscheidung über den Vorsteuerabzug liegt beim Steuerberater.",
    ]

    if invoice.mismatch_warnings:
        lines.extend(["", "Abweichungen / Hinweise:"])
        for warning in invoice.mismatch_warnings:
            lines.append(f"- {warning}")

    if invoice.validation_issues:
        lines.extend(["", "Prüfungshinweise:"])
        for issue in invoice.validation_issues[:20]:
            bt: str = f" {issue.bt_code}" if issue.bt_code else ""
            lines.append(f"- [{issue.level}/{issue.category}{bt}] {issue.message}")
            if issue.explanation:
                lines.append(f"  {issue.explanation}")

    if invoice.next_steps:
        lines.extend(["", "Empfohlene nächste Schritte:"])
        for index, step in enumerate(invoice.next_steps, start=1):
            lines.append(f"{index}. {step}")

    lines.append("")
    return "\n".join(lines)


def decode_pdf_base64(value: str) -> bytes:
    """Decode raw or data-URL base64 PDF content."""
    raw: str = value.strip()
    if raw.startswith("data:") and "," in raw:
        raw = raw.split(",", 1)[1]
    try:
        return base64.b64decode(raw, validate=False)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("PDF konnte nicht gelesen werden (ungültiges Base64).") from exc


def _package_pdf_member_name(invoice: InvoiceParseResponse, pdf_filename: Optional[str]) -> str:
    if pdf_filename:
        base: str = pdf_filename.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        if base.lower().endswith(".pdf"):
            stem: str = _slug(base[:-4]) or "rechnung"
            return f"{stem}.pdf"
    supplier: str = _slug(invoice.seller.name if invoice.seller else None) or "supplier"
    number: str = _slug(invoice.invoice_number) or "invoice"
    return f"{supplier}_{number}.pdf"


def _validation_engine_line(invoice: InvoiceParseResponse) -> str:
    meta: ValidationMeta = invoice.validation_meta
    if meta.engine == "kosit":
        version: str = f" {meta.engine_version}" if meta.engine_version else ""
        scenarios: str = f" · {meta.scenarios_version}" if meta.scenarios_version else ""
        return f"KoSIT Validator{version}{scenarios}"
    return "interne Geschäftsregeln (keine volle KoSIT-Prüfung)"


def _mismatch_summary_line(invoice: InvoiceParseResponse) -> str:
    if invoice.file_type != "zugferd_pdf" or not invoice.mismatch_fields:
        return "nicht geprüft / nicht zutreffend"
    mismatches: List[MismatchField] = [
        item for item in invoice.mismatch_fields if item.xml_value and not item.matched
    ]
    if mismatches:
        labels: str = ", ".join(item.label for item in mismatches)
        return f"Abweichung ({labels})"
    return "übereinstimmend"


def _slug(value: Optional[str]) -> str:
    if not value:
        return ""
    cleaned: str = re.sub(r"[^\w\-]+", "_", value.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned[:40]


def _num_str(value: Optional[Decimal]) -> str:
    if value is None:
        return ""
    return f"{value:.2f}"


def _de_amount(value: Optional[Decimal]) -> str:
    if value is None:
        return ""
    return f"{value:.2f}".replace(".", ",")


def _datev_date(iso_date: Optional[str]) -> str:
    """DATEV Belegdatum often DDMM (current year implied) or DDMMYYYY — use DDMMYYYY."""
    if not iso_date or len(iso_date) < 10:
        return ""
    # YYYY-MM-DD -> DDMMYYYY
    year: str = iso_date[0:4]
    month: str = iso_date[5:7]
    day: str = iso_date[8:10]
    return f"{day}{month}{year}"
