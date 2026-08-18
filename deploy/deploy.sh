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
#
set -euo pipefail

APP_ROOT="${APP_ROOT:-/opt/eInvoice}"
FRONTEND_DIR="${FRONTEND_DIR:-${APP_ROOT}/frontend}"
WEB_ROOT="${WEB_ROOT:-/var/www/erechnung-smart}"
API_SERVICE="${API_SERVICE:-einvoice-api}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:8000/api/health/live}"
WEB_USER="${WEB_USER:-www-data}"
WEB_GROUP="${WEB_GROUP:-www-data}"

DO_PULL=1
DO_BACKEND=1
DO_FRONTEND=1

usage() {
  cat <<'EOF'
Usage: deploy.sh [options]

  --skip-pull       Do not run git pull
  --frontend-only   Build and publish frontend only
  --backend-only    Restart API only (after optional git pull)
  -h, --help        Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-pull) DO_PULL=0 ;;
    --frontend-only) DO_BACKEND=0; DO_FRONTEND=1 ;;
    --backend-only) DO_BACKEND=1; DO_FRONTEND=0 ;;
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

if [[ "${DO_PULL}" -eq 1 ]]; then
  echo "==> git pull"
  git pull --ff-only
else
  echo "==> skip git pull"
fi

if [[ "${DO_BACKEND}" -eq 1 ]]; then
  echo "==> restart ${API_SERVICE}"
  systemctl restart "${API_SERVICE}"
  systemctl --no-pager --full status "${API_SERVICE}" | sed -n '1,12p'

  echo "==> health check ${HEALTH_URL}"
  ok=0
  for _ in $(seq 1 20); do
    if curl -fsS "${HEALTH_URL}" >/dev/null; then
      ok=1
      break
    fi
    sleep 0.5
  done
  if [[ "${ok}" -ne 1 ]]; then
    echo "API health check failed: ${HEALTH_URL}" >&2
    exit 1
  fi
  echo "    API OK"
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
