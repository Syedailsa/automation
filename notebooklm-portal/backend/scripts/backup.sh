#!/usr/bin/env bash
# Database backup script for NotebookLM Portal
# Usage: ./scripts/backup.sh
# Env vars: PGHOST, PGPORT, PGUSER, PGPASSWORD, PGDATABASE

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/notebooklm_${TIMESTAMP}.sql.gz"

# Defaults (override via env)
export PGHOST="${PGHOST:-localhost}"
export PGPORT="${PGPORT:-5432}"
export PGUSER="${PGUSER:-notebooklm}"
export PGPASSWORD="${GPASSWORD:-notebooklm_secret}"
export PGDATABASE="${PGDATABASE:-notebooklm_portal}"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting backup of ${PGDATABASE}..."

pg_dump -h "$PGHOST" -p "$PGPORT" -U "$PGUSER" -d "$PGDATABASE" \
    --format=custom --compress=9 \
    > "$BACKUP_FILE"

FILESIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "[$(date)] Backup created: ${BACKUP_FILE} (${FILESIZE})"

# Cleanup old backups
echo "[$(date)] Cleaning backups older than ${RETENTION_DAYS} days..."
find "$BACKUP_DIR" -name "notebooklm_*.sql.gz" -mtime +"$RETENTION_DAYS" -delete

REMAINING=$(find "$BACKUP_DIR" -name "notebooklm_*.sql.gz" | wc -l)
echo "[$(date)] Backup complete. ${REMAINING} backup(s) retained."
