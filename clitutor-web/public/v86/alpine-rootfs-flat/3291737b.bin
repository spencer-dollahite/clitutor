#!/bin/bash
# health_check.sh - Fleet service health checker
# Runs via cron every 5 minutes

LOGFILE="/var/log/health.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOAD_THRESHOLD="1.5"

check_service() {
    local svc="$1"
    local pid
    pid=$(pgrep -x "$svc" 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        echo "$TIMESTAMP [OK] $svc: running (pid $pid)" >> "$LOGFILE"
    else
        echo "$TIMESTAMP [FAIL] $svc: not running" >> "$LOGFILE"
    fi
}

check_load() {
    local load
    load=$(awk '{print $1}' /proc/loadavg)
    if awk "BEGIN {exit !($load > $LOAD_THRESHOLD)}"; then
        echo "$TIMESTAMP [WARN] load: $load (threshold $LOAD_THRESHOLD)" >> "$LOGFILE"
    fi
}

check_disk() {
    local usage
    usage=$(df / | awk 'NR==2 {print $5}' | tr -d '%')
    echo "$TIMESTAMP [OK] disk: ${usage}% used" >> "$LOGFILE"
}

# Run checks
check_service sshd
check_service nginx
check_load
check_disk
