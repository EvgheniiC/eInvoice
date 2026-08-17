# eInvoice

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

Options: `--frontend-only`, `--backend-only`, `--skip-pull`.  
Override paths via env: `APP_ROOT`, `WEB_ROOT`, `API_SERVICE`.

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

Logging (no invoice bodies): set `LOG_LEVEL=INFO` (default). On production, errors go to journald:

```bash
journalctl -u einvoice-api -f
journalctl -u einvoice-api --since "1 hour ago" | grep -E 'parse_failed|unhandled_exception|timeout|http_exception'
```

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

## API (MVP)

- `GET /api/health` — health check
- `POST /api/invoices/parse` — upload `.xml` / `.pdf`
- `POST /api/invoices/export` — export parsed DTO as `csv` / `excel` / `datev`
- `POST /api/invoices/export/accountant-package` — ZIP: original XML/PDF + summary + Prüfbericht + Excel + DATEV
- `GET /api/invoices/export/mapping` — versioned column mapping for Steuerberater

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
