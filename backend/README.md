# eInvoice Backend

FastAPI service for parsing and validating XRechnung / ZUGFeRD invoices.

## Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
uvicorn app.main:app --reload --port 8000
```

## Layout

- `app/api` — HTTP endpoints
- `app/services` — facade over parsers (public contract for UI)
- `app/schemas` — Pydantic DTOs
- `app/invoice_handler` — XML / PDF parsers (existing logic)
- `app/helper_functions` — shared XML helpers + config JSON
- `app/data_class` — internal domain models

## Validation

Official KoSIT EN 16931 / XRechnung checks are required in production.
See [docs/VALIDATION.md](../docs/VALIDATION.md).

## Observability

- `GET /api/health` — detailed status (`ok` / `degraded`)
- `GET /api/health/live` — liveness
- `GET /api/health/ready` — readiness (503 when KoSIT is required but missing)
- `GET /metrics` — Prometheus scrape (localhost; nginx does not proxy this path)

JSON logs (`LOG_FORMAT=json`) include `event` and `request_id`. Parse failures, timeouts, and 5xx are counted as metrics. Invoice bodies are never logged or labeled.

Regression snapshots for `parse_upload` live in `tests/goldens/` (JSON).
Invoice fixture bytes stay local under `tests/xml_files/` and `tests/pdf_files/`.

```bash
pytest tests/test_golden_files.py
# after intentional parse changes:
# Windows PowerShell:
$env:UPDATE_GOLDENS=1; pytest tests/test_golden_files.py
# Linux/macOS:
UPDATE_GOLDENS=1 pytest tests/test_golden_files.py
```
