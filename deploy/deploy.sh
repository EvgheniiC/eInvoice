#!/usr/bin/env bash
# Deploy eInvoice on the production host (erechnung-smart).
#
# Default layout:
#   Repo:     /opt/eInvoice
#   Frontend: /var/www/erechnung-smart  (nginx root)
#   API:      systemd unit einvoice-api
#
# Usage (as root on the server):
#   ./deploy/deploy.sh
#   ./deploy/deploy.sh --frontend-only
#   ./deploy/deploy.sh --backend-only
#   ./deploy/deploy.sh --skip-pull
#   ./deploy/deploy.sh --rollback
#
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/eInvoice}"
FRONTEND_DIR="${FRONTEND_DIR:-${APP_ROOT}/frontend}"
WEB_ROOT="${WEB_ROOT:-/var/www/erechnung-smart}"
API_SERVICE="${API_SERVICE:-einvoice-api}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/api/health/ready}"
WEB_USER="${WEB_USER:-www-data}"
WEB_GROUP="${WEB_GROUP:-www-data}"
PREVIOUS_SHA_FILE="${PREVIOUS_SHA_FILE:-${APP_ROOT}/.deploy-previous-sha}"

DO_PULL=1
DO_BACKEND=1
DO_FRONTEND=1
DO_ROLLBACK=0
SAVED_SHA=""

usage() {
  cat <<'EOF'
Usage: deploy.sh [options]

  --skip-pull       Do not run git pull
  --frontend-only   Build and publish frontend only
  --backend-only    Restart API only (after optional git pull)
  --rollback        Restore the git revision saved before the last pull, then redeploy
  -h, --help        Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-pull) DO_PULL=0 ;;
    --frontend-only) DO_BACKEND=0; DO_FRONTEND=1 ;;
    --backend-only) DO_BACKEND=1; DO_FRONTEND=0 ;;
    --rollback) DO_ROLLBACK=1; DO_PULL=0 ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if [[ "$(id -u)" -ne 0 ]]; then
  echo "Run as root (needed for systemctl, nginx, and ${WEB_ROOT})." >&2
  exit 1
fi

if [[ ! -d "${APP_ROOT}/.git" ]]; then
  echo "APP_ROOT is not a git repo: ${APP_ROOT}" >&2
  exit 1
fi

echo "==> App root: ${APP_ROOT}"
cd "${APP_ROOT}"

wait_for_live() {
  local ok=0
  local _
  for _ in $(seq 1 20); do
    if curl -fsS "${HEALTH_URL}" >/dev/null; then
      ok=1
      break
    fi
    sleep 0.5
  done
  if [[ "${ok}" -ne 1 ]]; then
    return 1
  fi
  return 0
}

restore_previous_sha() {
  local sha="${1:-}"
  if [[ -z "${sha}" ]]; then
    echo "No previous revision available for rollback." >&2
    return 1
  fi
  echo "==> rollback git to ${sha}"
  git checkout -f "${sha}"
}

if [[ "${DO_ROLLBACK}" -eq 1 ]]; then
  if [[ ! -f "${PREVIOUS_SHA_FILE}" ]]; then
    echo "Missing ${PREVIOUS_SHA_FILE}. Cannot rollback." >&2
    exit 1
  fi
  SAVED_SHA="$(tr -d '[:space:]' < "${PREVIOUS_SHA_FILE}")"
  restore_previous_sha "${SAVED_SHA}"
elif [[ "${DO_PULL}" -eq 1 ]]; then
  SAVED_SHA="$(git rev-parse HEAD)"
  echo "${SAVED_SHA}" > "${PREVIOUS_SHA_FILE}"
  echo "==> git pull (previous ${SAVED_SHA})"
  git pull --ff-only
else
  echo "==> skip git pull"
fi

if [[ "${DO_BACKEND}" -eq 1 ]]; then
  BACKEND_DIR="${APP_ROOT}/backend"
  if [[ ! -x "${BACKEND_DIR}/.venv/bin/pip" ]]; then
    echo "Missing ${BACKEND_DIR}/.venv/bin/pip" >&2
    exit 1
  fi
  echo "==> pip install backend deps"
  (
    cd "${BACKEND_DIR}"
    .venv/bin/pip install -r requirements.txt
    .venv/bin/pip install -e .
  )
  if [[ -f "${BACKEND_DIR}/.env" ]] && grep -qE '^DATABASE_URL=.+' "${BACKEND_DIR}/.env"; then
    echo "==> alembic upgrade head"
    (
      cd "${BACKEND_DIR}"
      .venv/bin/alembic upgrade head
    )
  else
    echo "    skip alembic (DATABASE_URL not set in backend/.env)"
  fi

  echo "==> install systemd units"
  install -d -m 700 -o "${WEB_USER}" -g "${WEB_GROUP}" /var/lib/einvoice/batch-tmp
  install -d -m 700 -o "${WEB_USER}" -g "${WEB_GROUP}" /var/lib/einvoice/history-originals
  if [[ -d /etc/systemd/system ]]; then
    cp "${APP_ROOT}/deploy/einvoice-api.service" /etc/systemd/system/einvoice-api.service
    cp "${APP_ROOT}/deploy/einvoice-worker.service" /etc/systemd/system/einvoice-worker.service
    systemctl daemon-reload
  fi

  echo "==> restart ${API_SERVICE}"
  systemctl restart "${API_SERVICE}"
  systemctl --no-pager --full status "${API_SERVICE}" | sed -n '1,12p'

  echo "==> restart einvoice-worker"
  systemctl enable einvoice-worker
  systemctl restart einvoice-worker
  systemctl --no-pager --full status einvoice-worker | sed -n '1,12p'

  echo "==> production readiness check ${HEALTH_URL}"
  if ! wait_for_live; then
    echo "API health check failed: ${HEALTH_URL}" >&2
    if [[ "${DO_ROLLBACK}" -eq 0 && -n "${SAVED_SHA}" ]]; then
      restore_previous_sha "${SAVED_SHA}"
      systemctl restart "${API_SERVICE}"
      wait_for_live || true
    fi
    exit 1
  fi
  echo "    API ready"

  if systemctl cat einvoice-alerts.timer >/dev/null 2>&1; then
    echo "==> enable einvoice-alerts.timer"
    systemctl enable --now einvoice-alerts.timer
  else
    echo "    hint: copy deploy/einvoice-alerts.{service,timer} to systemd for 5xx/timeout/parse/API alerts"
  fi
fi

if [[ "${DO_FRONTEND}" -eq 1 ]]; then
  if [[ ! -d "${FRONTEND_DIR}" ]]; then
    echo "Frontend directory missing: ${FRONTEND_DIR}" >&2
    exit 1
  fi

  echo "==> npm install + build"
  cd "${FRONTEND_DIR}"
  if [[ -f package-lock.json ]]; then
    npm ci
  else
    npm install
  fi
  npm run build

  if [[ ! -f dist/index.html ]]; then
    echo "Build failed: dist/index.html missing" >&2
    exit 1
  fi

  if ! grep -Rqs "Rechnung hochladen\|PDF ausblenden\|Paket für Steuerberater\|eInvoice" dist/assets/; then
    echo "Warning: expected UI strings not found in dist/assets (check build)." >&2
  fi

  echo "==> publish to ${WEB_ROOT}"
  mkdir -p "${WEB_ROOT}"
  rsync -a --delete "${FRONTEND_DIR}/dist/" "${WEB_ROOT}/"
  chown -R "${WEB_USER}:${WEB_GROUP}" "${WEB_ROOT}"

  echo "==> reload nginx"
  nginx -t
  systemctl reload nginx
  echo "    frontend published"
fi

echo "==> deploy done"
