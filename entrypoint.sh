#!/bin/sh
set -e

echo "Run Alembic migration..."
alembic upgrade head 

echo "Start Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
