#!/usr/bin/env bash
# run_dev_backend_and_worker.sh
# ──────────────────────────────────────────────────────────────────────────────
# Start the FastAPI backend and background worker together for development.
#
# Usage:
#   chmod +x scripts/run_dev_backend_and_worker.sh
#   ./scripts/run_dev_backend_and_worker.sh
#
# Environment variables (all optional – override via .env or export):
#   DATABASE_URL       default: postgresql://postgres:postgres@localhost:5432/jenan_biz
#   UVICORN_HOST       default: 0.0.0.0
#   UVICORN_PORT       default: 8000
#   WORKER_POLL_INTERVAL  default: 5  (seconds)
# ──────────────────────────────────────────────────────────────────────────────

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BACKEND_DIR="${REPO_ROOT}/backend"

export PYTHONPATH="${BACKEND_DIR}"

# Load .env if present
if [ -f "${BACKEND_DIR}/.env" ]; then
  set -a
  # shellcheck disable=SC1091
  source "${BACKEND_DIR}/.env"
  set +a
fi

UVICORN_HOST="${UVICORN_HOST:-0.0.0.0}"
UVICORN_PORT="${UVICORN_PORT:-8000}"

echo "==> Initialising database (startup)..."
cd "${BACKEND_DIR}"
python -c "from app.main import startup; startup()"

echo "==> Starting worker in background..."
python -m app.worker.run &
WORKER_PID=$!
echo "    Worker PID: ${WORKER_PID}"

echo "==> Starting FastAPI backend on ${UVICORN_HOST}:${UVICORN_PORT}..."
uvicorn app.asgi:app \
  --host "${UVICORN_HOST}" \
  --port "${UVICORN_PORT}" \
  --reload &
UVICORN_PID=$!
echo "    Uvicorn PID: ${UVICORN_PID}"

# Clean up on exit
cleanup() {
  echo "==> Shutting down..."
  kill "${WORKER_PID}" "${UVICORN_PID}" 2>/dev/null || true
  wait "${WORKER_PID}" "${UVICORN_PID}" 2>/dev/null || true
  echo "==> Done."
}
trap cleanup EXIT INT TERM

echo ""
echo "Backend : http://${UVICORN_HOST}:${UVICORN_PORT}"
echo "Analytics UI: http://localhost:${UVICORN_PORT}/analytics.html"
echo "API docs    : http://localhost:${UVICORN_PORT}/docs"
echo ""
echo "Press Ctrl+C to stop both processes."

wait
