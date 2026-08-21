# eInvoice

[![CI](https://github.com/EvgheniiC/eInvoice/actions/workflows/ci.yml/badge.svg)](https://github.com/EvgheniiC/eInvoice/actions/workflows/ci.yml)

Web utility for German B2B SMEs: upload XRechnung XML or ZUGFeRD PDF → readable invoice, validation, accounting export.

## Stack

| Layer    | Tech                          |
|----------|-------------------------------|
| Backend  | Python 3.13+, FastAPI         |
| Frontend | React 19 + TypeScript + Vite  |

## Project structure

```
eInvoice/
├── backend/                 # FastAPI API + parsers
│   ├── app/
│   │   ├── api/             # HTTP routes
│   │   ├── core/            # settings
│   │   ├── schemas/         # public API DTOs
│   │   ├── services/        # facade over parsers
│   │   ├── data_class/      # domain models
│   │   ├── helper_functions/
│   │   ├── invoice_handler/ # XML / ZUGFeRD parsers
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── frontend/                # React SPA
│   └── src/
│       ├── api/
│       ├── components/
│       ├── pages/
│       └── types/
├── docs/
├── deploy/                  # systemd unit + deploy.sh (prod)
└── TODO_LIST_MVP.md
```

## Deploy (production host)

On the server (paths match `erechnung-smart` defaults):

```bash
cd /opt/eInvoice
sudo ./deploy/deploy.sh
```

Options: `--frontend-only`, `--backend-only`, `--skip-pull`, `--rollback`.  
Override paths via env: `APP_ROOT`, `WEB_ROOT`, `API_SERVICE`.

`--rollback` restores the git revision saved before the last pull and repeats
the smoke check on `/api/health/live`. A failed live check after `git pull`
also attempts that rollback automatically.

## Setup

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

Optional full XRechnung Schematron (KoSIT). In **production** this is required
(`ENVIRONMENT=production`). Set in `backend/.env`:

```
ENVIRONMENT=production
KOSIT_VALIDATOR_JAR=C:\path\to\validationtool.jar
KOSIT_SCENARIOS_XML=C:\path\to\scenarios.xml
KOSIT_JAVA_BIN=java
```

Without KoSIT the API still runs structural/business checks. It never reports
the invoice as valid until a KoSIT run completes. See [docs/VALIDATION.md](docs/VALIDATION.md).

Optional accounts (Stage 1): PostgreSQL + `AUTH_SECRET_KEY`. Guest upload still
works without a login. Daily quotas for guest / Free / Plus / Team are enforced;
see [docs/AUTH.md](docs/AUTH.md).

Logging (no invoice bodies): set `LOG_LEVEL=INFO` (default). On production, errors go to journald:

```bash
journalctl -u einvoice-api -f
journalctl -u einvoice-api --since "1 hour ago" | grep -E 'parse_failed|unhandled_exception|timeout|http_exception'
journalctl -u einvoice-alerts --since "1 hour ago" | grep -E 'alert_firing|alert_resolved'
```

Alerts (5xx, timeout, severe parse failures, API down/not ready) run via
`einvoice-alerts.timer`. See [docs/ALERTS.md](docs/ALERTS.md).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI: http://127.0.0.1:5173 (proxies `/api` → backend)

### Tests

```bash
cd backend
pytest
# golden-file regression (needs local tests/xml_files + tests/pdf_files):
pytest tests/test_golden_files.py
# or, for legacy path-relative fixtures:
cd tests && python -m unittest discover -s . -v
```

Frontend checks (also used in CI):

```bash
cd frontend
npm run lint
npm run typecheck
npm test
npm run build
npm run test:e2e
```

`npm run test` is Vitest (unit/component). `npm run test:e2e` is Playwright: landing → upload → result → Steuerberater package, against a production preview with mocked API.

After changing backend Pydantic DTOs, refresh the OpenAPI snapshot and generated TypeScript types:

```bash
python backend/scripts/export_openapi.py
```

CI fails if `frontend/openapi.json` or `frontend/src/types/openapi.ts` drift from the live FastAPI schema.

## CI

GitHub Actions (`.github/workflows/ci.yml`) runs on every push to `main` and on pull requests:

- Backend: `pytest` on Python 3.13 (includes OpenAPI ↔ TypeScript contract check)
- Frontend: `oxlint`, TypeScript `tsc -b`, Vitest, Vite production build, and the Playwright happy-path test

Golden-file cases that need local `backend/tests/xml_files` or `backend/tests/pdf_files` are skipped when those fixtures are not present.

## API (MVP)

- `GET /api/health` — detailed health (`ok` / `degraded`), always HTTP 200
- `GET /api/health/live` — liveness probe (process is up)
- `GET /api/health/ready` — readiness probe (HTTP 503 if required KoSIT is missing)
- `GET /metrics` — Prometheus metrics on the API process (`127.0.0.1:8000`, not proxied by nginx)
- `POST /api/invoices/parse` — upload `.xml` / `.pdf`
- `POST /api/invoices/export` — export parsed DTO as `csv` / `excel` / `datev`
- `POST /api/invoices/export/accountant-package` — ZIP: original XML/PDF + summary + Prüfbericht + Excel + DATEV
- `GET /api/invoices/export/mapping` — versioned column mapping for Steuerberater

Logs are JSON lines (`LOG_FORMAT=json`) with `X-Request-ID` correlation. Application logs and metrics never contain invoice XML/PDF.

See [docs/EXPORT_MAPPING.md](docs/EXPORT_MAPPING.md). DATEV export is a Buchungsstapel CSV, not DATEVconnect.

## Privacy and legal pages

The SPA serves `/impressum` (Impressum and Datenschutzerklärung on one page;
`/datenschutz` opens the same view). Operator identity is intentionally
left blank until the public launch. Files are processed in memory and short-lived
temp directories, then deleted; application logs never contain invoice XML/PDF.

See [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md) and [docs/AVV_DPA.md](docs/AVV_DPA.md).

## Nginx (production)

On the HTTPS vhost, include:

```nginx
# inside http { }
include /opt/eInvoice/deploy/nginx-rate-limit-zone.conf;

# inside server { }
include /opt/eInvoice/deploy/nginx-security-snippet.conf;
include /opt/eInvoice/deploy/nginx-api-snippet.conf;
include /opt/eInvoice/deploy/nginx-spa-snippet.conf;
```

Terminate TLS on nginx. The API listens on `127.0.0.1:8000` only.
Set `CORS_ORIGINS` in `backend/.env` only if the SPA is on a different origin.
