# Service level objectives

Operational targets for the guest Empfang service. These are internal
objectives, not a contractual SLA. Alerts in `ALERTS.md` enforce the same
windows.

Invoice content is never part of SLO measurement.

## Objectives

| SLO | Target | Measured by |
|-----|--------|-------------|
| Availability | Process answers `/api/health/live` except during planned deploys | `EinvoiceApiDown` if live fails ≥ 60s |
| Readiness (production) | KoSIT JAR, scenarios, and Java present | `EinvoiceApiNotReady` if `/api/health/ready` fails ≥ 5 min |
| Processing time | HTTP request ≤ 90s; KoSIT CLI ≤ 60s | `request_timeout_seconds`, `kosit_timeout_seconds`; `EinvoiceTimeouts` |
| Server errors | Fewer than 3 HTTP 5xx in 5 minutes | `EinvoiceHigh5xx` |
| Severe parse failures | Fewer than 3 unexpected parse errors in 5 minutes | `EinvoiceParseFailures` (not expected format rejects) |

Expected rejects (wrong type, empty file, oversize) are user errors and do
not consume the parse-failure error budget.

## Product funnel (no invoice payload)

Prometheus counter `einvoice_funnel_total{step=...}`:

1. `landing` — start page viewed
2. `upload` — Empfang page viewed
3. `parse_success` — readable invoice (`success` or `partial`)
4. `export` — CSV / Excel / DATEV / Steuerberater-Paket downloaded

KPI definitions (measure after the Handwerk pilot starts):

- Time-to-understand: time from upload to a visible outcome (client-side, later)
- Parse success rate: `parse_success / upload`
- Export rate: `export / parse_success`
- Returning users: not measured in guest mode (no account)

## When an SLO is missed

Follow [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md). If KoSIT/Java is the
cause, follow the fallback section in [VALIDATION.md](VALIDATION.md).
