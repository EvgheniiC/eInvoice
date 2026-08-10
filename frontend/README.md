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
- `src/types` — shared DTOs (mirrors backend schemas)
- `src/components` — UI building blocks (e.g. drag-and-drop upload)
- `src/pages` — screens (landing `/`, upload `/upload`)
