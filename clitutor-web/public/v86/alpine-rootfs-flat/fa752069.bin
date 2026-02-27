#!/bin/bash
# banner.sh - System information banner
# Usage: banner.sh

echo "=================================="
echo "  Host:    $(hostname)"
echo "  Kernel:  $(uname -r)"
echo "  Uptime:  $(uptime -p 2>/dev/null || uptime)"
echo "  Memory:  $(free -m | awk 'NR==2{printf "%dM / %dM (%.0f%%)", $3, $2, $3/$2*100}')"
echo "  Disk:    $(df -h / | awk 'NR==2{printf "%s / %s (%s)", $3, $2, $5}')"
echo "  Load:    $(cat /proc/loadavg | awk '{print $1, $2, $3}')"
echo "=================================="
