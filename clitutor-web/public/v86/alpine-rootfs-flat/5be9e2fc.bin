#!/bin/bash
# check_services.sh - Quick service status check
# Usage: check_services.sh

SERVICES="sshd nginx crond"

echo "Service Status Report"
echo "====================="
echo ""

for svc in $SERVICES; do
    pid=$(pgrep -x "$svc" 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        printf "  %-12s  [RUNNING]  pid %s\n" "$svc" "$pid"
    else
        printf "  %-12s  [STOPPED]\n" "$svc"
    fi
done

echo ""
echo "Listening ports:"
ss -tlnp 2>/dev/null | grep -E "LISTEN" | awk '{printf "  %s %s\n", $4, $6}'
