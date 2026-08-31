# Incident response

Short operator playbook for the guest Empfang service. Do not collect or
forward invoice XML/PDF, IBANs, or upload bodies while investigating.

## Severity

| Level | Examples | First action |
|-------|----------|--------------|
| Critical | API down, TLS down, mass 5xx | Restore service (`systemctl restart einvoice-api` or `deploy/deploy.sh --rollback`) |
| High | KoSIT/Java missing, readiness 503, timeout spike | Keep Empfang up; never mark invoices gültig; restore validator files |
| Medium | Parse-failure spike, webhook/alerts failing | Inspect counters and recent deploys; no invoice logs |
| Low | Content/UX defect reported via `/hilfe` | Product fix; ask reporter not to send invoices |

## Detect

- systemd watchdog + `einvoice-alerts.timer` (see `ALERTS.md`)
- `/api/health`, `/api/health/live`, `/api/health/ready`, `/metrics`
- nginx 5xx logs (URLs and status only)

## Contain

1. Confirm live vs ready. If live fails, restart the API unit.
2. If a fresh deploy broke live checks, run `sudo ./deploy/deploy.sh --rollback`.
3. If ready fails because KoSIT/Java is missing, do **not** disable production
   KoSIT to “make it green”. Serve the degraded UI (no gültig) and restore the
   JAR/scenarios/JRE. See `VALIDATION.md`.
4. Rate-limit or block an abusive client at nginx if uploads exhaust workers.
   Do not dump request bodies.

## Personal data incidents

If invoice content may have leaked (log misconfiguration, backup of temp files,
support mailbox with an attached invoice):

1. Stop the leak (fix logging, delete temp files, quarantine the mailbox).
2. Record time, systems, and what category of data may be involved — not the
   invoice itself.
3. Notify the Verantwortlicher (Svetlana Costina, svetlana.costina@gmx.de)
   and follow Art. 33/34 DSGVO.
4. Do not request the original invoice again “for debugging”.

## Aftercare

- Write what fired, what changed, and the new counter values.
- Open a follow-up for missing SLO, dependency, or KoSIT pinning work.
- External security review remains required before Mandantenakten.
