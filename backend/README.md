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
