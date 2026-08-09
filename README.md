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
└── TODO_LIST_MVP.md
```

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

Optional full XRechnung Schematron (KoSIT) — set in `backend/.env`:

```
KOSIT_VALIDATOR_JAR=C:\path\to\validationtool.jar
KOSIT_SCENARIOS_XML=C:\path\to\scenarios.xml
KOSIT_JAVA_BIN=java
```

Without KoSIT the API still runs structural/business checks and labels them clearly.

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
# or, for legacy path-relative fixtures:
cd tests && python -m unittest discover -s . -v
```

## API (MVP)

- `GET /api/health` — health check
- `POST /api/invoices/parse` — upload `.xml` / `.pdf`
- `POST /api/invoices/export` — export parsed DTO as `csv` / `excel` / `datev`
- `POST /api/invoices/export/accountant-package` — ZIP: summary + Excel + DATEV + optional PDF
- `GET /api/invoices/export/mapping` — column mapping for Steuerberater

See [docs/EXPORT_MAPPING.md](docs/EXPORT_MAPPING.md).
