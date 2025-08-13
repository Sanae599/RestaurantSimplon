#!/bin/sh
set -e  # stoppe si une commande échoue

echo "Run Alembic migration..."
cd /
alembic upgrade head
echo "Start Uvicorn server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
