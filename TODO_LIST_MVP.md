# MVP TODO List — eInvoice Receiver for Handwerk / SME

Status updated: August 2026.

- `[x]` — implemented and confirmed in the current repository
- `[ ]` — not implemented, only partially implemented, or requires external validation

## Goal
Simple web utility for German B2B SMEs (workshops, craftsmen):
drag & drop XRechnung XML or ZUGFeRD PDF → readable invoice + validation status + export for accounting.

Primary pain: **receiving**, not sending.

Out of scope for MVP: PEPPOL, outbound invoicing, full ERP replacement, multi-tenant SaaS billing complexity.

---

## Product principle
One happy path:
Upload → Parse → Validate → Show human-readable invoice → Warn on PDF/XML mismatch (ZUGFeRD) → Export CSV/DATEV/Excel.

Legal disclaimer (must be visible):
validation checks schema/standard compliance; acceptance for Vorsteuerabzug remains with the user / Steuerberater.

---

## Current codebase baseline (already available)
- [x] XML parsing helpers (`einvoice_helper.py`)
- [x] Header parser (`xml_parser_header.py`)
- [x] Positions parser (`xml_parser_positions.py`)
- [x] Equipment / vehicle-related parsing
- [x] Vendor data extraction (`xml_vendor_parser.py`)
- [x] PDF attachment extraction from XML (`xml_pdf_extraction.py`)
- [x] Basic ZUGFeRD PDF detection (`is_zugpferd_pdf`)
- [x] Unit tests for parsers
- [x] Product UI (React SPA: landing, upload and invoice result)
- [x] EN 16931 / XRechnung validation service integration (business rules + optional KoSIT)
- [x] ZUGFeRD XML extraction + PDF↔XML field comparison
- [x] Accounting export (CSV / DATEV / Excel)
- [x] End-user web upload flow

---

## Phase 0 — Foundation (1 week)
### 0.1 Product / scope freeze
- [x] Freeze MVP persona: workshop owner + Steuerberater helper
- [x] Freeze supported input types:
  - [x] XRechnung XML (UBL Invoice/CreditNote and CII)
  - [x] ZUGFeRD / Factur-X PDF with embedded EN 16931 XML
- [x] Freeze export targets for v1:
  - [x] Human-readable HTML view
  - [x] Excel/CSV
  - [x] DATEV-compatible CSV (minimal profile)
- [x] Write non-goals list (PEPPOL, sending, public API productization — later)

### 0.2 Engineering baseline
- [x] Define clean public service API over existing parsers (facade, neutral naming in UI layer)
- [x] Normalize parsed result into one DTO:
  - seller, buyer, invoice number, dates
  - net / tax / gross
  - line items
  - payment means (IBAN etc.)
  - validation status
  - mismatch warnings
- [x] Collect local sample corpus (60+ XML, ZUGFeRD PDFs, plain `No_Valid*` PDFs, openTRANS pairs) — **local only, gitignored** (`backend/tests/xml_files/`, `backend/tests/pdf_files/`); remaining gaps in `TODO_LIST_TEST.md`
- [x] Local fixture dirs wired into tests/parsers — files stay on disk, not in git; tests skip optional fixtures if absent
- [x] Decide stack for thin web app (FastAPI + React)

- [ ] EU data handling policy draft (process & delete vs short archive)

---

## Phase 1 — Solution 1: Converter & Visualizer (core MVP)
### 1.1 Upload & ingest
- [x] Web page: drag-and-drop + file picker
- [x] Accept `.xml`, `.pdf`
- [x] Detect file type (XML vs ZUGFeRD PDF vs unsupported)
- [x] Size/type limits and clear error messages in German (UI language)
- [x] Return structured parse result to UI

### 1.2 Parse pipeline
- [x] Reuse existing XML parsers behind facade
- [x] Map parser output → UI DTO
- [x] Clear German errors for unsupported formats (openTRANS, non-EN16931 XML, plain PDF without embedded XML)
- [ ] Handle remaining vendor quirks with user-friendly errors
- [x] For ZUGFeRD PDF:
  - [x] Extract embedded XML
  - [x] Parse embedded XML with same pipeline
  - [x] Keep visual PDF available for side-by-side reference

### 1.3 Validation (P0)
- [x] Implement KoSIT EN 16931 / XRechnung validator integration
- [ ] Make KoSIT mandatory and verify its configuration in production
- [x] Show status: valid / invalid / warning
- [x] Show plain-language reasons for failures (German)
- [x] Distinguish "schema invalid" vs "business warning"
- [x] Never claim tax deductibility guarantee

### 1.4 Human-readable invoice view (P0)
- [x] Render invoice screen from XML data (not from PDF OCR)
- [x] Show:
  - [x] Supplier name, address, VAT ID
  - [x] Invoice number, issue date, due date
  - [x] Line items (qty, price, tax, totals)
  - [x] Net / VAT / Gross
  - [x] IBAN / payment reference if present
- [x] Mobile-friendly readable layout
- [ ] Optional: download "view PDF" generated from structured data

### 1.5 ZUGFeRD consistency check (P1, still MVP-critical)
- [x] Compare key fields PDF-visible vs XML:
  - [x] invoice number
  - [x] dates
  - [x] gross amount
  - [x] VAT amount
  - [x] IBAN (if extractable)
- [x] UI banner: match / mismatch
- [x] On mismatch: highlight fields and recommend contacting supplier

### 1.6 UX copy & trust
- [x] German UI strings for all main states
- [x] Empty / error / success states
- [x] Disclaimer footer about validation vs accounting responsibility
- [x] "What should I do next?" hints (pay / ask supplier / export to accountant)

**Phase 1 exit criteria**
- [x] User can upload XML or ZUGFeRD and see amount and parties in one flow
- [x] Invalid invoices show why
- [x] Mismatched ZUGFeRD is explicitly flagged
- [ ] Validate the "< 30 seconds" target with real pilot users

---

## Phase 2 — Solution 2: One-click accounting export
### 2.1 Export engine
- [x] Export button on invoice view
- [x] CSV export (stable column schema)
- [x] Excel export (`.xlsx`)
- [x] DATEV-compatible export (implemented minimal profile)
- [ ] Validate DATEV import and mapping with a real Steuerberater workflow
- [x] Filename convention: `supplier_invoiceNo_date.ext`

### 2.2 Field mapping
- [x] Map DTO → export columns
- [x] Document mapping for Steuerberater
- [x] Handle missing optional fields safely
- [x] Preserve decimals / DE number formats where needed

### 2.3 Accountant workflow
- [x] "Paket für Steuerberater": summary + Excel + DATEV + optional source PDF
- [ ] Include source XML and a separate validation report in the accountant package
- [ ] Optional short retention of last N uploads for paid plan → see `TODO_LIST_FUTURE.md`
- [ ] Pilot with 1–2 Steuerberater offices → deferred to `TODO_LIST_FUTURE.md`

**Phase 2 exit criteria**
- [x] Core invoice fields are exported without manual retyping
- [ ] Accountant confirms import without retyping core fields
- [ ] At least one real bookkeeping tool path works end-to-end

---

## Phase 3 — Hardening & pilot
### 3.1 Quality
- [x] Golden-file tests for samples (`tests/test_golden_files.py` + `tests/goldens/`)
- [ ] Validation false-positive/negative review
- [ ] Performance check for typical file sizes
- [x] Security review: no XML XXE / entity bomb (`defusedxml`, `UNSAFE_XML`); remaining: malware/type sniffing later
- [ ] Security review: upload malware/type sniffing (post-XXE)
- [x] Stateless request flow with no database or invoice archive
- [ ] Publish and verify privacy/deletion policy for temporary processing files

### 3.2 Pilot
- [ ] Recruit / track / fix from real users → deferred to `TODO_LIST_FUTURE.md` (Steuerberater + workshops pilot)

### 3.3 Packaging
- [x] Simple deploy (single web service) — `deploy/deploy.sh` (+ existing `einvoice-api.service`)
- [x] Basic logging/monitoring without storing invoice bodies longer than needed
- [x] Landing page text: problem → demo → upload CTA (`/` → `/upload`)
- [ ] Pricing hypothesis (free limited / paid unlimited + export)

**Phase 3 exit criteria**
- [ ] Pilot users use it weekly without hand-holding
- [ ] Clear go/no-go for public beta

---

## Explicitly later (not MVP)
- [ ] Public API productization (Solution 3)
- [ ] Email inbox auto-ingest
- [ ] PEPPOL access point
- [ ] Outbound XRechnung / ZUGFeRD generation
- [ ] Deep integrations (Lexware, sevDesk, DATEV Unternehmen online native APIs)
- [ ] Multi-company Steuerberater portal (full)
- [ ] Mobile native apps

---

## Suggested milestone order
1. Facade DTO + sample corpus
2. Upload + parse + readable view
3. Validation integration
4. ZUGFeRD extract + mismatch warnings
5. CSV/Excel export
6. DATEV export
7. Pilot + harden

---

## Definition of Done (MVP)
- [x] Workshop user can process a supplier XRechnung without opening raw XML
- [x] Workshop user can process a ZUGFeRD PDF and see XML/PDF mismatches
- [x] User sees validation result in plain German
- [x] User can export data for accounting in one click
- [x] No PEPPOL/sending scope creep included
- [x] Disclaimer present; no false Vorsteuer guarantee
- [ ] Full KoSIT validation is guaranteed in production
- [ ] DATEV workflow is confirmed by a real Steuerberater pilot
- [ ] Datenschutz/legal pages and deletion policy are published
- [ ] Public beta go/no-go is confirmed from pilot results
