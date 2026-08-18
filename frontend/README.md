# eInvoice Frontend

React + TypeScript + Vite SPA for invoice upload and review.

## Run

```bash
npm install
npm run dev
```

Dev server proxies `/api` to `http://127.0.0.1:8000`.

## Layout

- `src/api` — HTTP client to backend
- `src/types` — API DTOs generated from FastAPI OpenAPI (`openapi.ts`) plus aliases in `invoice.ts`
- `src/components` — UI building blocks (e.g. drag-and-drop upload)
- `src/pages` — screens (landing `/`, upload `/upload`)

After backend DTO changes run `python ../backend/scripts/export_openapi.py` (or `npm run sync:api`).
