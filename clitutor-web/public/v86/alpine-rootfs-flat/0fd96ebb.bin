#!/usr/bin/env python3
"""Parse SSH auth logs for suspicious activity."""

import re
import sys
from collections import Counter

FAILED_PATTERN = re.compile(
    r'Failed password for (?:invalid user )?(\S+) from (\S+) port (\d+)'
)

def parse_auth_log(filepath):
    """Parse auth log and return failed attempt details."""
    attempts = []
    with open(filepath, 'r') as f:
        for line in f:
            match = FAILED_PATTERN.search(line)
            if match:
                user, ip, port = match.groups()
                attempts.append({"user": user, "ip": ip, "port": int(port)})
    return attempts

def report(attempts):
    """Print a summary report of failed login attempts."""
    if not attempts:
        print("No failed login attempts found.")
        return

    ip_counts = Counter(a["ip"] for a in attempts)
    user_counts = Counter(a["user"] for a in attempts)

    print(f"\nTotal failed attempts: {len(attempts)}")
    print(f"\nTop source IPs:")
    for ip, count in ip_counts.most_common(5):
        print(f"  {ip:20s} {count} attempts")
    print(f"\nTargeted usernames:")
    for user, count in user_counts.most_common(10):
        print(f"  {user:20s} {count} attempts")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <logfile>")
        sys.exit(1)
    attempts = parse_auth_log(sys.argv[1])
    report(attempts)
