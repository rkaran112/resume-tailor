#!/bin/sh
# Boot sequence: ensure the output dir exists, bring the schema up to head
# (idempotent — safe to run on every deploy/restart), then serve. Binds the
# port the platform assigns via $PORT (Render), defaulting to 8000 locally.
set -e

mkdir -p generated/resumes

echo "running database migrations..."
alembic upgrade head

echo "starting API on port ${PORT:-8000}"
exec uvicorn app.main:create_app --factory --host 0.0.0.0 --port "${PORT:-8000}"
