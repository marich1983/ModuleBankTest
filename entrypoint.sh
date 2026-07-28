#!/bin/sh

set -e

echo "Running migrations..."
alembic upgrade head

if [ "$1" = "worker" ]; then
    echo "Starting worker..."
    exec python -m app.worker.sender
else
    echo "Starting API..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8080
fi