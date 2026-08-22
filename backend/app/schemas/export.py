from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from pydantic import Field

from app.schemas.invoice import ApiModel, InvoiceParseResponse

MANDANT_MEMBER: str = "mandant.txt"


@dataclass(frozen=True)
class OrgProfile:
    """Firm details copied into the Steuerberater ZIP. Later also Kanzlei letter/link."""

    name: str
    tax_number: Optional[str] = None
    vat_id: Optional[str] = None
    iban: Optional[str] = None
    accountant_email: Optional[str] = None

# Frozen accounting export schema. Bump major when columns/semantics break Kanzlei imports.
EXPORT_FORMAT_VERSION: str = "1.0"

DATEV_LIMITATIONS: str = (
    "Minimaler DATEV-Buchungsstapel-CSV (Semikolon, deutsche Dezimalzahlen, CP1252). "
    "Das ist kein DATEVconnect und kein nativer Import in DATEV Unternehmen online. "
    "Eine Soll-/Haben-Zeile über den Bruttobetrag; Konto, Gegenkonto, Beraternummer "
    "und Mandant bleiben leer und müssen in der Kanzlei ergänzt werden. "
    "Vor dem Live-Import in DATEV Kanzlei-Rechnungswesen prüfen."
)


class ExportFormat(str, Enum):
    """Supported accounting export formats."""

    CSV = "csv"
    EXCEL = "excel"
    DATEV = "datev"


class ExportRequest(ApiModel):
    """Request body: parsed invoice DTO to export."""

    format: ExportFormat = ExportFormat.CSV
    invoice: InvoiceParseResponse


class ValidationReportRequest(ApiModel):
    """Request body: parsed invoice DTO to render as a validation report."""

    invoice: InvoiceParseResponse


class ViewPdfRequest(ApiModel):
    """Request body: parsed invoice DTO to render as a working-copy PDF."""

    invoice: InvoiceParseResponse


class AccountantPackageRequest(ApiModel):
    """ZIP package for Steuerberater: original + summary + report + Excel + DATEV."""

    invoice: InvoiceParseResponse
    pdf_base64: Optional[str] = Field(
        default=None,
        description="Original ZUGFeRD PDF (with embedded XML) as base64.",
    )
    pdf_filename: Optional[str] = Field(
        default=None,
        description="Original PDF filename when pdf_base64 is set.",
    )
    xml_base64: Optional[str] = Field(
        default=None,
        description="Original XRechnung / extracted invoice XML as base64.",
    )
    xml_filename: Optional[str] = Field(
        default=None,
        description="Original XML filename when xml_base64 is set.",
    )


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


class ExportMappingDoc(ApiModel):
    """Human-readable mapping description for Steuerberater."""

    format: ExportFormat
    version: str
    description: str
    columns: List[str]
    encoding: str
    delimiter: str
    decimal_separator: str
    date_format: str
    notes: Optional[str] = None
    limitations: Optional[str] = None


EXPORT_DOCS: List[ExportMappingDoc] = [
    ExportMappingDoc(
        format=ExportFormat.CSV,
        version=EXPORT_FORMAT_VERSION,
        description=(
            "Stable UTF-8 CSV for Kanzlei import: one row per line item, "
            "German locale (semicolon, decimal comma, DD.MM.YYYY)."
        ),
        columns=EXPORT_COLUMNS,
        encoding="utf-8-sig",
        delimiter=";",
        decimal_separator=",",
        date_format="DD.MM.YYYY",
        notes="Missing optional fields are empty. Header names stay stable within this version.",
    ),
    ExportMappingDoc(
        format=ExportFormat.EXCEL,
        version=EXPORT_FORMAT_VERSION,
        description=(
            "XLSX workbook: sheet 'Invoice' = header summary, 'Lines' = positions "
            "with native numbers, 'Flat' = same columns as CSV."
        ),
        columns=EXPORT_COLUMNS,
        encoding="utf-8",
        delimiter="",
        decimal_separator=",",
        date_format="DD.MM.YYYY",
        notes=(
            "Invoice sheet includes export_format_version. "
            "Lines amounts are Excel numbers (displayed per Excel locale)."
        ),
    ),
    ExportMappingDoc(
        format=ExportFormat.DATEV,
        version=EXPORT_FORMAT_VERSION,
        description=(
            "DATEV-compatible Buchungsstapel CSV (semicolon, German decimals, CP1252). "
            "Not DATEVconnect."
        ),
        columns=DATEV_COLUMNS,
        encoding="cp1252",
        delimiter=";",
        decimal_separator=",",
        date_format="DDMMYYYY",
        notes=(
            "One booking line for the gross amount. "
            "Soll (S) for invoices, Haben (H) for credit notes. "
            "Belegfeld 1 = invoice number; Buchungstext = seller + invoice number."
        ),
        limitations=DATEV_LIMITATIONS,
    ),
]
