#!/bin/bash
set -e

echo "Running Alembic migrations..."
alembic upgrade head

if [ "$ENV" = "prod" ]; then
  echo "Starting FastAPI app (PROD mode)..."
  exec gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
else
  echo "Starting FastAPI app (DEV mode)..."
  exec uvicorn main:app --host 0.0.0.0 --port 8000 --reload
fi