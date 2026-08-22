# Export mapping

Stable accounting export contract for eInvoice **format version 1.0**.

Use this document together with `GET /api/invoices/export/mapping`.
Column names and DATEV field names in 1.x stay additive: new optional columns may
appear only in a new minor version; renamed or removed columns require a new major version.

## Formats

| Format | Encoding | Delimiter | Decimal | Date | File |
|--------|----------|-----------|---------|------|------|
| CSV | UTF-8 with BOM | `;` | `,` | `DD.MM.YYYY` | `supplier_invoice_YYYYMMDD.csv` |
| Excel | UTF-8 (OOXML) | — | Excel locale | `DD.MM.YYYY` on Invoice/Flat | `supplier_invoice_YYYYMMDD.xlsx` |
| DATEV CSV | Windows-1252 (CP1252) | `;` | `,` | `DDMMYYYY` | `datev_supplier_invoice_YYYYMMDD.csv` |

Filenames are ASCII-safe: German umlauts are transliterated (`ä` → `ae`), other
non-word characters become `_`.

CSV, Excel and DATEV are produced from the same parsed invoice DTO. They do **not**
re-parse the original file.

## CSV / Excel columns (Flat)

One row per line item. Header fields are repeated on every row. If the invoice has
no positions, one row with empty `line_*` fields is written.

| Column | Source | Notes |
|--------|--------|-------|
| `invoice_number` | BT-1 | |
| `issue_date` | BT-2 | CSV/Excel: `DD.MM.YYYY` |
| `due_date` | BT-9 | CSV/Excel: `DD.MM.YYYY` |
| `seller_name` | BT-27 | |
| `seller_vat_id` | BT-31 | |
| `seller_iban` | BT-84 | |
| `buyer_name` | BT-44 | |
| `buyer_vat_id` | BT-48 | |
| `currency` | BT-5 | ISO code, e.g. `EUR` |
| `net` | BT-109 | 2 decimal places |
| `tax` | BT-110 | 2 decimal places |
| `gross` | BT-112 | 2 decimal places |
| `payment_reference` | BT-83 | |
| `line_position` | BT-126 | |
| `line_description` | BT-153 | |
| `line_quantity` | BT-129 | 2 decimal places |
| `line_unit` | BT-130 | |
| `line_unit_price` | BT-146 | 2 decimal places |
| `line_tax_rate` | BT-151 | 2 decimal places |
| `line_net_amount` | BT-131 | 2 decimal places |

Missing optional fields are empty strings.

Excel workbook sheets:

- `Invoice` — header fields plus `export_format_version`
- `Lines` — positions with native Excel numbers
- `Flat` — same columns as CSV (German dates and decimal commas)

## DATEV CSV

This is a **minimal Buchungsstapel-compatible CSV**, not DATEVconnect and not a native
DATEV Unternehmen online import.

| Field | Value |
|-------|--------|
| `Umsatz` | Absolute gross amount, German decimal comma |
| `Soll/Haben-Kennzeichen` | `S` for invoices, `H` for credit notes (or negative gross) |
| `WKZ Umsatz` | Currency, default `EUR` |
| `Konto` | Empty — Kanzlei fills SKR account |
| `Gegenkonto (ohne BU-Schlüssel)` | Empty |
| `BU-Schlüssel` | Empty |
| `Belegdatum` | `DDMMYYYY` from issue date |
| `Belegfeld 1` | Invoice number (max. 36) |
| `Buchungstext` | Seller + invoice number (max. 60) |

Empty DATEV columns (`Kurs`, `Basis-Umsatz`, `Skonto`, …) are reserved for the Kanzlei.

### Limitations (public)

- No DATEVconnect / DATEV API session
- No EXTF header, consultant number, client number, or fiscal year
- No SKR account mapping
- One booking line for the invoice gross amount, not per VAT rate or line item
- Must be checked in DATEV Kanzlei-Rechnungswesen before live import

The same text is shipped as `datev_hinweise.txt` inside the Steuerberater ZIP.

## Steuerberater package

`POST /api/invoices/export/accountant-package` returns a ZIP:

| Member | Purpose |
|--------|---------|
| `export_manifest.txt` | Format version and file list |
| `datev_hinweise.txt` | DATEV limitations (not DATEVconnect) |
| `summary.txt` | Short German invoice summary |
| `mandant.txt` | Optional 1.x: firm profile from Org-Einstellungen (name, Steuernummer, USt-IdNr, IBAN, Steuerberater email) |
| `pruefbericht_*.txt` | Validation report |
| `*.xlsx` | Excel export |
| `datev_*.csv` | DATEV-compatible CSV |
| `original/*.xml` | Original XRechnung XML, or XML extracted from ZUGFeRD |
| `original/*.pdf` | Original ZUGFeRD PDF with embedded XML |

The UI sends the uploaded source file with the package request. The backend does not
keep invoice files after the guest request.

### Batch package (Plus / Team)

`POST /api/invoices/batch/{job_id}/accountant-package` returns one ZIP for N invoices
from a completed batch while originals still exist in `BATCH_TEMP_DIR` (short TTL):

| Member | Purpose |
|--------|---------|
| `export_manifest.txt` | Format version and file list |
| `datev_hinweise.txt` | DATEV limitations (not DATEVconnect) |
| `summary.txt` | German batch overview |
| `mandant.txt` | Optional 1.x: firm profile of the uploading organization |
| `pruefbericht_paket.txt` | Concatenated validation reports |
| `rechnungen_*.xlsx` | Excel: Invoice table + Lines + Flat (same columns as CSV) |
| `datev_rechnungen_*.csv` | DATEV-compatible CSV, one booking line per invoice |
| `original/NN_*.xml` / `original/NN_*.pdf` | Source files from the batch |

This is a 1.x addition (optional ZIP members). Column names stay on version **1.0**.

## Versioning

Current version: **1.0**

- **Patch / product UI changes** do not bump this version
- **1.x** may add optional columns or ZIP members
- **2.0** is required if a column is renamed, removed, or changes meaning
  (for example decimal separator or DATEV `Belegdatum` layout)

The version is written to `export_manifest.txt`, the Excel `Invoice` sheet, and
`GET /api/invoices/export/mapping`.
