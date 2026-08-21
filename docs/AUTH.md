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
- `GET /api/me` and `GET/PATCH /api/org` carry org context
- Quotas are returned on the plan object with `quotas_enforced: false`
- Guest parse with a session only logs `organization_id` + plan; still no invoice archive

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

- `/anmelden` `/registrieren` `/bestaetigen?token=` `/organisation`
- Magic-link consume: `/bestaetigen?kind=magic&token=`
