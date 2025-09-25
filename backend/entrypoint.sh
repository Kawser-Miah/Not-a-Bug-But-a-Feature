#!/usr/bin/env bash
set -euo pipefail

echo "[entrypoint] Starting container for Developer Guidance System"

if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "[entrypoint] Using DATABASE_URL=${DATABASE_URL}"
else
  echo "[entrypoint] DATABASE_URL not set, defaulting (sqlite)"
fi

echo "[entrypoint] Running Alembic migrations..."
alembic upgrade head
echo "[entrypoint] Migrations complete."

echo "[entrypoint] Launching application: $*"
exec "$@"
