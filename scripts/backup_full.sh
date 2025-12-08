#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR=${BACKUP_DIR:-/backups}
FILE="$BACKUP_DIR/full_$(date +%F).dump"

mkdir -p "$BACKUP_DIR"
pg_dump -U postgres -F c -d hospital_mis -f "$FILE"
echo "Full backup created: $FILE"

