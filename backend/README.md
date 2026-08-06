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
