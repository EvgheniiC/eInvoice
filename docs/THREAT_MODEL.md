# Threat model — eInvoice

Lightweight STRIDE review for the public upload utility
(XRechnung / ZUGFeRD parse → validate → export). This is **not** an independent
security audit. An external review is still required before processing real
client invoices in production.

Scope: browser SPA + FastAPI on localhost behind nginx, one file per request,
no invoice archive. Two processing models:

| Model | Persistence | Legal basis (planned) | Status |
|-------|-------------|----------------------|--------|
| Guest | File lives only in the request / temp dir | Art. 6(1)(b)/(f) DSGVO for the parse/export request | Active |
| Account | Email, password hash, org membership, session. Plus batch originals in `BATCH_TEMP_DIR` until package TTL. | Art. 6 DSGVO + AVV; originals are operational temp, not an archive | Account tables exist; batch originals have a short TTL |

Billing, object storage, and invoice history remain future trust-boundary expansions.

## Assets

| Asset | Why it matters |
|-------|----------------|
| Uploaded XML/PDF | Personal and financial data (names, IBAN, amounts, VAT IDs) |
| Parsed invoice DTO | Same data in JSON during the request |
| Application logs | Must never become a shadow archive |
| KoSIT Java subprocess | Untrusted XML on disk for the duration of validation |
| Export files | Leave the server only as the HTTP response |

## Trust boundaries

1. Browser → nginx (TLS) → FastAPI (`127.0.0.1:8000`)
2. FastAPI → temp files → KoSIT / OpenJDK
3. Operators with journald / host access

Untrusted: every upload, every JSON export body, every `X-Forwarded-For` header
unless nginx overwrites it (the API snippet sets `X-Forwarded-For $remote_addr`).

## Threats and mitigations

| ID | Threat | Mitigation in code / deploy |
|----|--------|-----------------------------|
| S1 | Spoofed file type (PDF/XML mismatch) | Signature + extension checks in `InvoiceService` |
| S2 | XXE / DTD / entity expansion | `defusedxml`, reject `DOCTYPE`/`ENTITY`, complexity limits |
| S3 | Malicious PDF (JS, Launch, encryption, huge page count) | `assert_pdf_safe` |
| S4 | Resource exhaustion (huge file, nested XML, slow KoSIT, zip-bomb) | 10 MB cap (plan size), rate limit, request timeout, JVM `-Xmx`, systemd `MemoryMax`, nginx `limit_req`; ZIP ingest checks listed sizes, ratio, member cap, xml/pdf only |
| T1 | Invoice data in logs | Sanitized structured logs; parsers must not log IBAN/XML |
| T2 | Temp file leftover | `TemporaryDirectory` for PDF probe and KoSIT; `PrivateTmp=true`; batch originals in `BATCH_TEMP_DIR` until accountant ZIP or TTL, then deleted |
| T4 | Zip-slip / nested ZIP | Reject `..` and absolute paths; skip nested `.zip` members |
| T3 | Error detail leak | Generic 500/422 to clients; no traceback in JSON |
| I1 | Cross-origin abuse | Explicit CORS origins, no credentialed wildcard, nginx same-origin `/api` |
| I2 | Clickjacking / MIME sniffing | Security headers (app + nginx) |
| E1 | KoSIT running with extra privileges | Dedicated JVM flags, POSIX rlimits, systemd hardening, Java not on a public port |
| D1 | Denial of service via many uploads | nginx + in-app rate limit, timeouts |
| D2 | Feedback used to exfiltrate or inject invoice data | No file upload; reject XML/PDF/IBAN-like text; rate limit `/api/feedback` |
| I3 | Funnel/telemetry as a tracking profile | Step name only, no cookie, no invoice id |
| I4 | Session theft | httpOnly cookie, hashed token, password change revokes sessions |

## Residual risk (must stay open)

- No independent pentest / code audit yet
- In-app rate limit is per process (one uvicorn worker); nginx is the edge control
- Google Fonts (if enabled on the SPA) send visitor IPs to Google until self-hosted
- Operator/hosting identity and AVV counterparties are not filled in yet
- KoSIT is a large Java attack surface; keep the JAR and JRE patched

## Review checklist before real invoices

- [ ] External security review of this document and the running deployment
- [ ] Confirm TLS, security snippets, and `ENVIRONMENT=production` on the host
- [ ] Confirm journald does not capture request bodies (app never logs them)
- [ ] Fill Impressum / Verantwortlicher and sign AVV with the hoster
