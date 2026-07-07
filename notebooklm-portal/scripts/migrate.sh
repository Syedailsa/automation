#!/bin/bash
set -e

echo "Running database migrations..."

cd "$(dirname "$0")/../backend"

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run 'make setup' first."
    exit 1
fi

source venv/bin/activate

if [ "$1" = "create" ]; then
    if [ -z "$2" ]; then
        echo "Usage: ./scripts/migrate.sh create 'migration message'"
        exit 1
    fi
    echo "Creating migration: $2"
    alembic revision --autogenerate -m "$2"
else
    echo "Applying migrations..."
    alembic upgrade head
    echo "Migrations applied successfully"
fi
