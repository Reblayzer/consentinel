#!/bin/sh
# Apply database migrations, then start the API. Running migrations on boot keeps
# the container's schema in lock-step with the deployed code.
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Starting API..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
