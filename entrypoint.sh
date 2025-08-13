#!/bin/sh
set -e

echo "Run Alembic migration..."
alembic upgrade head  # direct, pas docker exec

echo "Seed database..."
python seed.py  # direct, pas docker exec

echo "Start Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
