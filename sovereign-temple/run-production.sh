#!/bin/bash
# ============================================================
# SOV3 Production Launch — Gunicorn with worker recycling
# Workers recycle after 1000 requests (prevents memory leaks)
# Auto-restart on crash via launchd
# ============================================================

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Source environment
if [[ -f .env ]]; then
  set -a
  source .env
  set +a
fi

export PORT=${PORT:-3100}
export HOST=${HOST:-0.0.0.0}
export PYTHONUNBUFFERED=1

echo "🚀 Starting SOV3 in production mode..."
echo "   Workers: 2 (UvicornWorker)"
echo "   Max requests: 1000 (then recycle)"
echo "   Timeout: 120s"
echo "   Port: $PORT"

exec gunicorn sovereign-mcp-server:app \
  --worker-class uvicorn.workers.UvicornWorker \
  --workers 2 \
  --bind "${HOST}:${PORT}" \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --timeout 120 \
  --graceful-timeout 30 \
  --access-logfile /tmp/sov3-access.log \
  --error-logfile /tmp/sov3-error.log \
  --log-level info
