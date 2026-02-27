#!/bin/bash
# backup_logs.sh - Archive and compress log files
# Usage: backup_logs.sh [target_dir]

TARGET="${1:-/tmp/log_backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE="logs_${TIMESTAMP}.tar.gz"

mkdir -p "$TARGET"

echo "Backing up logs to $TARGET/$ARCHIVE..."
tar czf "$TARGET/$ARCHIVE" \
    /var/log/auth.log \
    /var/log/syslog \
    /var/log/health.log \
    2>/dev/null

if [ $? -eq 0 ]; then
    echo "Backup complete: $TARGET/$ARCHIVE"
    ls -lh "$TARGET/$ARCHIVE"
else
    echo "ERROR: Backup failed!" >&2
    exit 1
fi
