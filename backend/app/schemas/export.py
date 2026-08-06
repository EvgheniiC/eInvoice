from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.invoice import InvoiceParseResponse


class ExportFormat(str, Enum):
    """Supported accounting export formats."""

    CSV = "csv"
    EXCEL = "excel"
    DATEV = "datev"


class ExportRequest(BaseModel):
    """Request body: parsed invoice DTO to export."""

    format: ExportFormat = ExportFormat.CSV
    invoice: InvoiceParseResponse


# Stable column schema for CSV / Excel (one row per line item).
EXPORT_COLUMNS: List[str] = [
    "invoice_number",
    "issue_date",
    "due_date",
    "seller_name",
    "seller_vat_id",
    "seller_iban",
    "buyer_name",
    "buyer_vat_id",
    "currency",
    "net",
    "tax",
    "gross",
    "payment_reference",
    "line_position",
    "line_description",
    "line_quantity",
    "line_unit",
    "line_unit_price",
    "line_tax_rate",
    "line_net_amount",
]

# Minimal DATEV Buchungsstapel-compatible columns (semicolon CSV, DE decimals).
DATEV_COLUMNS: List[str] = [
    "Umsatz",
    "Soll/Haben-Kennzeichen",
    "WKZ Umsatz",
    "Kurs",
    "Basis-Umsatz",
    "WKZ Basis-Umsatz",
    "Konto",
    "Gegenkonto (ohne BU-Schlüssel)",
    "BU-Schlüssel",
    "Belegdatum",
    "Belegfeld 1",
    "Belegfeld 2",
    "Skonto",
    "Buchungstext",
]


class ExportMappingDoc(BaseModel):
    """Human-readable mapping description for Steuerberater."""

    format: ExportFormat
    description: str
    columns: List[str]
    notes: Optional[str] = None


EXPORT_DOCS: List[ExportMappingDoc] = [
    ExportMappingDoc(
        format=ExportFormat.CSV,
        description="Stable UTF-8 CSV (comma) with one row per line item.",
        columns=EXPORT_COLUMNS,
        notes="Missing optional fields are empty. Decimals use dot (en-US).",
    ),
    ExportMappingDoc(
        format=ExportFormat.EXCEL,
        description="XLSX workbook: sheet 'Invoice' = header summary, 'Lines' = positions.",
        columns=EXPORT_COLUMNS,
        notes="Same field mapping as CSV.",
    ),
    ExportMappingDoc(
        format=ExportFormat.DATEV,
        description="Minimal DATEV-compatible booking CSV (semicolon, DE decimals, CP1252).",
        columns=DATEV_COLUMNS,
        notes=(
            "One booking line for the gross amount (Soll). "
            "Konto/Gegenkonto left empty for the accountant to fill. "
            "Belegfeld 1 = invoice number; Buchungstext = seller + invoice number."
        ),
    ),
]
