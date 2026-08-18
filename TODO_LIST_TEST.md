# Test fixtures TODO — eInvoice Receiver

Local sample files live in:
- `backend/tests/xml_files/`
- `backend/tests/pdf_files/`

Do **not** commit PDF/XML (see `.gitignore`).

Regenerate synthetic edge cases:
```bash
python backend/scripts/generate_edge_case_fixtures.py
```

---

## Already covered (new batch)

- [x] Valid XRechnung XML
- [x] Valid ZUGFeRD / Factur-X PDF
- [x] Plain PDF without embedded XML (`No_Valid*`)
- [x] openTRANS PDF + XML pairs (`*RECHNUNG1`) — unsupported format, expected reject

## Corpus scan via `InvoiceService` (2026-08-06)

Local XML total ~66:

| Result | Count | Notes |
|--------|------:|-------|
| success / valid | 56 | UBL/CII parse OK |
| partial | 5 | business warnings (`LINE_SUM_MISMATCH`, `AMOUNT_INCONSISTENT`, `BT-2_MISSING`) — not silent empties |
| error | 5 | openTRANS `*RECHNUNG1.xml` — now `UNSUPPORTED_OPENTRANS` |

No silent “success with empty core fields” found in the local corpus.

---

## Synthetic edge cases (generated 2026-08-07)

Base samples: `xml_text_from_zugpferd.xml`, `Rechnung_1096393995.pdf`

| File | Expected | Result |
|------|----------|--------|
| `Invalid_XR_missing_invoice_id.xml` | BT-1 missing | `error` / `BT-1_MISSING` |
| `Invalid_XR_missing_issue_date.xml` | BT-2 missing | `partial` / `BT-2_MISSING` |
| `Invalid_XR_inconsistent_totals.xml` | net+tax ≠ gross | `partial` / `AMOUNT_INCONSISTENT` |
| `Invalid_XR_not_well_formed.xml` | broken XML | `error` / `PARSE_EXCEPTION` |
| `Mismatch_invoice_no_amount_1096393995.pdf` | PDF≠XML number/amounts | `partial` + mismatch invoice_number/gross/tax |
| `Mismatch_iban_1096393995.pdf` | PDF≠XML IBAN | `partial` + `MISMATCH_IBAN` |
| `Broken_embedded_xml_1096393995.pdf` | ZUGFeRD, corrupt XML | `error` / parse failure |

Regression tests: `backend/tests/test_edge_case_fixtures.py` (skip if fixtures absent).

- [x] 2–3 invalid XRechnung XML
- [x] 1–2 ZUGFeRD with real PDF↔XML mismatch
- [x] 1 ZUGFeRD with broken embedded XML

---

## Still useful later (optional / P1+)

- [ ] Real supplier CreditNote / Gutschrift
- [ ] Multi-VAT (7% + 19%) live sample
- [ ] Large ZUGFeRD (many line items / multi-MB)
- [ ] Export E2E review with Steuerberater on 3–5 live invoices
- [x] Security: XXE / entity bomb XML — `defusedxml` + `safe_xml.py`; reject DOCTYPE/ENTITY (`UNSAFE_XML`)
- [ ] Encrypted / password PDF
