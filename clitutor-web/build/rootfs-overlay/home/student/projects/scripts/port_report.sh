#!/bin/bash
# port_report.sh - Audit listening ports and associated services
# Usage: port_report.sh

echo "Port Audit Report - $(date '+%Y-%m-%d %H:%M')"
echo "================================================"
echo ""

echo "TCP Listening:"
ss -tlnp 2>/dev/null | tail -n +2 | while read line; do
    port=$(echo "$line" | awk '{print $4}' | rev | cut -d: -f1 | rev)
    proc=$(echo "$line" | grep -oP 'users:\(\("\K[^"]+')
    printf "  Port %-6s  %s\n" "$port" "${proc:-unknown}"
done

echo ""
echo "Firewall rules:"
iptables -L -n 2>/dev/null | head -20 || echo "  (no iptables rules or permission denied)"
