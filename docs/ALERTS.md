# Alerts

Operational alerts for 5xx growth, timeouts, severe parse failures, and API
unavailability. Notifications never include invoice XML/PDF, filenames, or IBANs.

The production host does not need Prometheus. A systemd timer scrapes
`127.0.0.1:8000` every minute. Prometheus rule files are included for when a
scraper is added later.

## What fires

| Alert | When | Severity |
|-------|------|----------|
| `EinvoiceApiDown` | `/api/health/live` fails for ≥ 60s | critical |
| `EinvoiceApiNotReady` | `/api/health/ready` fails for ≥ 5 min (KoSIT/Java missing) | critical |
| `EinvoiceHigh5xx` | ≥ 3 HTTP 5xx in 5 min | critical |
| `EinvoiceTimeouts` | ≥ 2 timeouts in 5 min (HTTP or KoSIT) | warning |
| `EinvoiceParseFailures` | ≥ 3 **severe** parse errors in 5 min (`PARSE_EXCEPTION`, unsafe XML/PDF, …) | warning |

Expected rejects (`UNSUPPORTED_TYPE`, empty file, wrong extension) increment
parse-failure metrics but **do not** fire `EinvoiceParseFailures`.

## Enable on the host

```bash
sudo cp /opt/eInvoice/deploy/einvoice-alerts.service /etc/systemd/system/
sudo cp /opt/eInvoice/deploy/einvoice-alerts.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now einvoice-alerts.timer
```

Optional webhook (Slack / ntfy / email gateway). JSON body has only alert name,
severity, status, and a counter value:

```
ALERT_WEBHOOK_URL=https://example.invalid/hooks/einvoice
```

in `backend/.env` (loaded by the unit via `EnvironmentFile`).

```bash
journalctl -u einvoice-alerts -f
journalctl -u einvoice-alerts --since "1 hour ago" | grep -E 'alert_firing|alert_resolved|alert_live_probe_failed'
```

## Prometheus (optional)

- Scrape: `deploy/prometheus/einvoice-scrape.yml` (`127.0.0.1:8000/metrics`)
- Rules: `deploy/prometheus/einvoice-alerts.yml` (same thresholds as the watchdog)

Do not proxy `/metrics` through nginx.
