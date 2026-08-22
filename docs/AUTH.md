# Accounts (Stage 1)

Guest Empfang stays unchanged: `POST /api/invoices/parse` does not require a
session and does not persist the file.

Accounts are optional. Set `DATABASE_URL` to enable them.

## Production

PostgreSQL only. Accounts stay off until `DATABASE_URL` is in `backend/.env`.
`alembic upgrade head` without that variable is an error (it must not create SQLite).

Create the database once:

```bash
sudo -u postgres psql -c "CREATE USER einvoice WITH PASSWORD 'choose-a-password';"
sudo -u postgres psql -c "CREATE DATABASE einvoice OWNER einvoice;"
```

Add to `backend/.env` (do not use SQLite):

```
ENVIRONMENT=production
DATABASE_URL=postgresql+psycopg://einvoice:choose-a-password@127.0.0.1:5432/einvoice
AUTH_SECRET_KEY=long-random-string
ADMIN_API_TOKEN=long-random-string
PUBLIC_APP_URL=https://your-public-host
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=noreply@your-public-host
SMTP_PASSWORD=choose-a-password
SMTP_FROM=noreply@your-public-host
SMTP_STARTTLS=true
```

Generate secrets with `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
Then `alembic upgrade head` and `systemctl restart einvoice-api`.

Install account packages into the existing venv (after pull), then apply schema:

```bash
cd backend
.venv/bin/pip install -r requirements.txt
.venv/bin/pip install -e .
alembic upgrade head
```

`deploy/deploy.sh` does this before restarting the API.

SQLite is for tests and local development. Production readiness fails if
accounts are enabled without Postgres, without `AUTH_SECRET_KEY`, or without
SMTP (`EMAIL_BACKEND=smtp` plus host and from-address).

`EMAIL_BACKEND=log` is for local development: the confirmation URL is written
to API logs (`auth_email_token_dev`) and is not mailed.

After changing SMTP settings: `systemctl restart einvoice-api`. Quote
`SMTP_PASSWORD` if it contains `#`, spaces, or `$`. With GMX 2FA use the
application-specific password, not the mailbox password. Probe with:

```bash
cd /opt/eInvoice/backend
sudo -u www-data .venv/bin/python scripts/test_smtp.py --to you@example.com
journalctl -u einvoice-api -n 80 --no-pager | grep auth_email
```

## Flows

- Register: email + password + organization name → Inhaber membership on a **Free** plan
- Verify email: SMTP when `EMAIL_BACKEND=smtp`. After register the UI goes to `/anmelden`.
- Verify: `POST /api/auth/verify-email` with the mailed token (dev responses include the token)
- Login: password or magic link → httpOnly session cookie `einv_session`
- Forgot password: `POST /api/auth/forgot-password` emails a one-time reset
  link (the current password is hashed and is never mailed). Unknown or
  unverified addresses get the same generic response.
- Reset: `POST /api/auth/reset-password` with the mailed token and a new
  password; all sessions are revoked
- `GET /api/me` and `GET/PATCH /api/org` carry org context
- Org profile (Inhaber): name, Steuernummer, USt-IdNr, IBAN, Steuerberater email.
  Empty values clear the field. Invalid IBAN / USt-IdNr / email return HTTP 400.
  When set, the authenticated Steuerberater ZIP includes `mandant.txt` and a
  Mandant block in `summary.txt`. Guest packages stay without firm data.
  Letter / one-time Kanzlei link is stage 4 (B7), not this endpoint.
- Quotas are enforced: daily parse/export, plan upload size, parse parallelism
- Guest parse without a session still works (no archive); it counts against the guest IP quota
- Authenticated parse/export counts against the organization
- Plus/Team batch: `POST /api/invoices/batch` queues XML/PDF files or a ZIP of those
  types (zip-bomb limits apply). `GET /api/invoices/batch/{id}` returns progress.
  `POST /api/invoices/batch/{id}/accountant-package` returns one Steuerberater ZIP
  (combined Excel + DATEV + originals) while temp files still exist.
  Guest and Free receive HTTP 403 with a Plus hint.
  `POST /api/invoices/parse` stays one file and is unchanged.
- Worker: `python -m app.worker` (systemd `einvoice-worker`). Reads short-lived
  originals from `BATCH_TEMP_DIR` (not `/tmp` — systemd `PrivateTmp`), calls
  `InvoiceService.parse_upload`, stores metadata/result JSON, and keeps the original
  until the accountant ZIP is downloaded or `BATCH_ORIGINAL_TTL_SECONDS` (default 2 h).
  Each extracted file counts as one daily parse. The batch package counts as one export.

## Quotas (Stage 2)

Guest Empfang stays one file per request without login. Limits are enforced:

| | Guest (no login) | Free | Plus | Team |
|--|------------------|------|------|------|
| Parse / day | 10 | 10 | 100 | 500 |
| Export / day | 10 | 10 | 100 | 500 |
| Max file | 10 MB | 10 MB | 25 MB | 50 MB |
| Parallel parse | 1 | 1 | 2 | 4 |
| Batch files / job | — | — | 20 | 50 |
| Requests / minute | `RATE_LIMIT_PER_MINUTE` (30) | `ACCOUNT_RATE_LIMIT_PER_MINUTE` (60) | 60 | 60 |

Exhausted daily quota returns HTTP 429 with a German message and a Plus/Team hint.
Validation report download does not count as an export. Guest parse still does not
store files. Plus batch originals live only in `BATCH_TEMP_DIR` until the package
TTL, not in the database.
Plus/Team history is off until the Inhaber opts in under Organisation. Default
storage is metadata + SHA-256 file hash. `Dateien merken` keeps the original in
`HISTORY_ORIGINAL_DIR` for `HISTORY_ORIGINAL_RETENTION_DAYS` (30) so the
accountant package can be downloaded again. Without consent nothing is written.
Plan catalog numbers are reapplied on API start (`seed_plans`). After pull: `alembic upgrade head`.
Production also needs `einvoice-worker`, `BATCH_TEMP_DIR=/var/lib/einvoice/batch-tmp`
and `HISTORY_ORIGINAL_DIR=/var/lib/einvoice/history-originals`
(shared by API and worker; `PrivateTmp` must not isolate these directories).

## Pilot Plus

```bash
cd backend
python scripts/set_plan.py --email meister@example.com --plan plus
```

Or `POST /api/admin/plans` with header `X-Admin-Token`.

## Delete an account

```bash
cd backend
python scripts/delete_user.py --email meister@example.com
```

Removes the user, sessions, email tokens, and the organization if nobody else remains.

## UI

- `/anmelden` `/registrieren` `/passwort-vergessen` `/bestaetigen?token=` `/organisation`
- Magic-link consume: `/bestaetigen?kind=magic&token=`
- Password reset consume: `/passwort-zuruecksetzen?token=`
