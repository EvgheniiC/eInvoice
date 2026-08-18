# Accounts (Stage 1)

Guest Empfang stays unchanged: `POST /api/invoices/parse` does not require a
session and does not persist the file.

Accounts are optional. Set `DATABASE_URL` to enable them.

## Production

PostgreSQL only:

```
DATABASE_URL=postgresql+psycopg://einvoice:secret@127.0.0.1:5432/einvoice
AUTH_SECRET_KEY=long-random-string
ADMIN_API_TOKEN=long-random-string
PUBLIC_APP_URL=https://example.invalid
```

Apply schema:

```bash
cd backend
alembic upgrade head
```

SQLite is for tests and local development. Production readiness fails if
accounts are enabled without Postgres or without `AUTH_SECRET_KEY`.

## Flows

- Register: email + password + organization name → Inhaber membership on a **Free** plan
- Verify: `POST /api/auth/verify-email` with the mailed token (dev responses include the token)
- Login: password or magic link → httpOnly session cookie `einv_session`
- `GET /api/me` and `GET/PATCH /api/org` carry org context
- Quotas are returned on the plan object with `quotas_enforced: false`
- Guest parse with a session only logs `organization_id` + plan; still no invoice archive

## Pilot Plus

```bash
cd backend
python scripts/set_plan.py --email meister@example.com --plan plus
```

Or `POST /api/admin/plans` with header `X-Admin-Token`.

## UI

- `/anmelden` `/registrieren` `/bestaetigen?token=` `/organisation`
- Magic-link consume: `/bestaetigen?kind=magic&token=`
