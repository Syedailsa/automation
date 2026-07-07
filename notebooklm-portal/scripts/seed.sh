#!/bin/bash
set -e

echo "Seeding database with test data..."

cd "$(dirname "$0")/../backend"

if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found. Run 'make setup' first."
    exit 1
fi

source venv/bin/activate

python scripts/seed.py
