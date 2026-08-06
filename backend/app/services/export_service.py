import csv
import io
import re
from typing import Any, Dict, List, Optional, Tuple

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from app.schemas.export import DATEV_COLUMNS, EXPORT_COLUMNS, ExportFormat
from app.schemas.invoice import InvoiceParseResponse, LineItem


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
    amount: Optional[float] = invoice.totals.gross if invoice.totals else None
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


def _slug(value: Optional[str]) -> str:
    if not value:
        return ""
    cleaned: str = re.sub(r"[^\w\-]+", "_", value.strip(), flags=re.UNICODE)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned[:40]


def _num_str(value: Optional[float]) -> str:
    if value is None:
        return ""
    return f"{value:.2f}"


def _de_amount(value: Optional[float]) -> str:
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
