# Validation (EN 16931 / XRechnung / KoSIT)

eInvoice treats a file as **valid** only after the official KoSIT validator
completes a run against the current XRechnung scenarios. Structural and
business checks still run without KoSIT, but the status stays `not_checked`.

## Production requirement

Set in `backend/.env` or the systemd unit:

```
ENVIRONMENT=production
KOSIT_JAVA_BIN=/usr/bin/java
KOSIT_VALIDATOR_JAR=/opt/kosit/current/validator.jar
KOSIT_SCENARIOS_XML=/opt/kosit/current/scenarios.xml
KOSIT_REQUIRED=true
```

In production, KoSIT is mandatory. If the JAR or scenarios file is missing:

- `/api/health` returns `status: degraded` with `kosit_ready: false`
- `/api/health/ready` returns HTTP 503
- parse results stay `not_checked` and never show **gültig**
- the upload UI shows a German banner: full check unavailable, do not treat as valid

Local development may omit KoSIT. Business rules (required fields, amount
consistency, ZUGFeRD PDF↔XML) still run.

## Pinned production installation

The repository pins checksummed official artifacts:

- KoSIT Validator `1.6.3` (includes the fix for GHSA-hg2c-p2m3-q29m)
- XRechnung `3.0.2` validator configuration `2026-01-31`

On Debian/Ubuntu, install the runtime dependencies and run the installer:

```bash
apt-get update
apt-get install -y openjdk-17-jre-headless curl unzip ca-certificates
cd /opt/eInvoice
bash ./deploy/install-kosit.sh
```

Add the four values printed by the installer to `/opt/eInvoice/backend/.env`,
then deploy. The deployment script checks `/api/health/ready`, not only
liveness, so a production deployment fails while KoSIT is unavailable.

After restart:

```bash
systemctl is-active einvoice-api einvoice-worker
curl -i http://127.0.0.1:8000/api/health/ready
curl -sS http://127.0.0.1:8000/api/health
```

Expected: both services are `active`, readiness returns HTTP 200, and health
contains `"ready":true` and `"kosit_ready":true`.

## Fallback when KoSIT or Java is down

Do **not** turn off `ENVIRONMENT=production` or `KOSIT_REQUIRED` to hide the
outage. Empfang (read + business checks + export) may continue; the official
validity statement must not.

Operator steps:

1. Confirm `java -version` and that `KOSIT_VALIDATOR_JAR` / `KOSIT_SCENARIOS_XML` exist.
2. Restore the pinned JAR and scenarios from the last known-good copy on the host.
3. Restart `einvoice-api` and check `/api/health` (`kosit_ready: true`).
4. If a deploy caused the outage, `sudo ./deploy/deploy.sh --rollback`.
5. Tell users via the in-app banner; do not ask them to re-send invoices for debugging.

Alerts: `EinvoiceApiNotReady` (see `ALERTS.md`). Incident steps: `INCIDENT_RESPONSE.md`.

## How to update scenarios

Review at least every 90 days, and whenever KoSIT or the Koordinierungsstelle
publishes a new XRechnung configuration.

1. Download the current **validator** build from
   [itplr-kosit/validator](https://github.com/itplr-kosit/validator/releases).
2. Download the current **XRechnung scenarios** from
   [validator-configuration-xrechnung](https://github.com/itplr-kosit/validator-configuration-xrechnung/releases).
3. Point `KOSIT_VALIDATOR_JAR` and `KOSIT_SCENARIOS_XML` at the new files.
4. Update `backend/app/services/validation_scenarios_meta.json`
   (`xrechnung_version`, `pinned_at`).
5. Run `pytest` in `backend/` and a manual upload of a known-valid and a
   known-invalid XRechnung.
6. Confirm `/api/health` shows `kosit_ready: true` and the UI shows the new
   engine / scenario version.

Pinned metadata (not a substitute for the official files):

- Standard: EN 16931:2017
- XRechnung configuration target: 3.0.2 (see `validation_scenarios_meta.json`)

## Regression corpus

Committed golden snapshots live in `backend/tests/goldens/`. They cover:

| Class | Examples |
|-------|----------|
| Readable / typical | `xml_text_from_zugpferd`, `xml_text_from_xml`, `Rechnung_1096393995` |
| Invalid | missing invoice id / issue date, inconsistent totals, not well-formed XML |
| Edge | credit note, discount line, openTRANS reject, plain PDF, ZUGFeRD mismatches |

Invoice bytes stay local under `tests/xml_files/` and `tests/pdf_files/`.
Regenerate snapshots with `UPDATE_GOLDENS=1 pytest tests/test_golden_files.py`.
