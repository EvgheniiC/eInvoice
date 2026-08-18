# Future TODO List — eInvoice Receiver (post-MVP)

Ideas beyond the MVP scope in `TODO_LIST_MVP.md`.
Not committed for the first pilot; revisit after MVP exit criteria are met.

---

## openTRANS support (candidate expansion)

### Why
Some German suppliers still send invoices as:
- visual PDF (no embedded ZUGFeRD XML) **plus**
- a separate **openTRANS 2.1** XML (`http://www.opentrans.org/XMLSchema/2.1`, often with BMECat party fields)

These are valid B2B documents for the supplier workflow, but they are **not** XRechnung / ZUGFeRD / EN 16931.
MVP correctly rejects them today. Supporting them would reduce manual handling for workshops that receive this format.

### Evidence from fixtures
Local sample pairs (not in git): `*RECHNUNG1.xml` + matching `*RECHNUNG1.pdf`
- XML root: `<INVOICE version="2.1">` (openTRANS)
- PDF: plain PDF without embedded invoice XML
- Current behaviour: XML → parse error / unreadable; PDF → `NOT_ZUGFERD`

### Possible scope (if we expand)
- [ ] Detect openTRANS XML (namespace / root) and show a clear German message vs EN 16931 formats
- [ ] Parse openTRANS 2.1 → same public invoice DTO (seller, buyer, number, dates, totals, lines, VAT)
- [ ] Map companion PDF + openTRANS XML as a pair (optional upload of both, or folder/batch)
- [ ] Human-readable invoice view reused from MVP UI
- [ ] Export CSV / Excel / DATEV from mapped DTO (same export engine)
- [ ] Regression fixtures for openTRANS (valid + edge cases), kept local / anonymized
- [ ] Docs: supported formats list updated (XRechnung, ZUGFeRD, openTRANS)

### Explicit non-goals for a first openTRANS slice
- Full openTRANS catalog / order / dispatch advice coverage
- Claiming EN 16931 / XRechnung / Vorsteuer validation for openTRANS documents
- Treating openTRANS PDF+XML as ZUGFeRD consistency-check equivalents without a clear product rule

### Decision checklist before building
- [ ] Confirm real demand from pilot workshops / Steuerberater
- [ ] Decide UX: accept openTRANS as first-class format vs only “detected, not supported” guidance
- [ ] Estimate effort vs PEPPOL / Lexware / email-ingest alternatives

---

## PDF → E-Rechnung converter (outbound)

### Goal
Allow an invoice issuer to upload an existing plain PDF, review the extracted data, and download a compliant E-Rechnung for sending.

### Possible scope
- [ ] Extract invoice fields and line items from text-based PDFs; evaluate OCR separately for scanned documents
- [ ] Show an editable review step and require explicit user confirmation before generation
- [ ] Check required invoice fields and tax calculations
- [ ] Generate XRechnung XML and/or ZUGFeRD PDF with embedded EN 16931 XML
- [ ] Validate generated documents with KoSIT before download
- [ ] Clearly identify the generated structured document as authoritative
- [ ] Add German guidance explaining that only the invoice issuer may convert and send the invoice
- [ ] Never claim that automatic extraction alone guarantees legal or tax compliance

### Product positioning
Keep this as a separate `PDF → E-Rechnung` flow rather than presenting the product as accounting software or a full invoice editor.

---

## Other post-MVP candidates (from MVP backlog)

- [ ] **Pilot with Steuerberater / workshops** (deferred from MVP Phase 2.3 / 3.2)
  - [ ] Pilot with 1–2 Steuerberater offices — validate DATEV/Excel ZIP package on live invoices
  - [ ] Recruit 5–10 workshops and/or 1–2 tax advisors
  - [ ] Track: time-to-understand invoice, % parse success, real supplier validation issues, export usefulness
  - [ ] Fix top 10 real-world parse/validation issues from pilot feedback
- [ ] Optional short retention of last N uploads for paid plan
- [ ] Public API productization
- [ ] Email inbox auto-ingest
- [ ] PEPPOL access point
- [ ] Deep integrations (Lexware, sevDesk, DATEV Unternehmen online native APIs)
- [ ] Multi-company Steuerberater portal (full)
- [ ] Mobile native apps
