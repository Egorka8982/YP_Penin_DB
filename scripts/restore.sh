#!/usr/bin/env bash
set -euo pipefail

BACKUP_FILE=${1:? "Укажите путь к .dump"}
TARGET_DB=${TARGET_DB:-hospital_mis_restored}

createdb -U postgres "$TARGET_DB" || echo "DB $TARGET_DB already exists"
pg_restore -U postgres -d "$TARGET_DB" "$BACKUP_FILE"
echo "Restored into $TARGET_DB"

