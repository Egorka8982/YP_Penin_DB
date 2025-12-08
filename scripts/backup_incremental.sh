#!/usr/bin/env bash
set -euo pipefail

# Архивирование WAL — требуются archive_mode=on и archive_command в postgresql.conf
WAL_DIR=${WAL_DIR:-/backups/wal}
mkdir -p "$WAL_DIR"
echo "WAL archive directory: $WAL_DIR"
echo "Configure in postgresql.conf: archive_mode=on, archive_command='test ! -f $WAL_DIR/%f && cp %p $WAL_DIR/%f'"

