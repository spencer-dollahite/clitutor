#!/usr/bin/env python3
"""Fleet Monitor - Shore station health checker."""

import argparse
import json
import socket
import sys
from datetime import datetime

# Configuration
DEFAULT_CONFIG = "config.yaml"
TIMEOUT = 5  # seconds

def check_host(hostname, port=22):
    """Check if a host is reachable on the given port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((hostname, port))
        sock.close()
        return result == 0
    except socket.gaierror:
        return False
    except socket.timeout:
        return False

def get_status(hostname):
    """Get comprehensive status for a host."""
    ssh_up = check_host(hostname, 22)
    http_up = check_host(hostname, 80)

    status = {
        "host": hostname,
        "timestamp": datetime.utcnow().isoformat(),
        "ssh": "up" if ssh_up else "down",
        "http": "up" if http_up else "down",
        "overall": "online" if (ssh_up and http_up) else "degraded"
    }

    if not ssh_up and not http_up:
        status["overall"] = "offline"

    return status

def print_report(statuses):
    """Print a formatted status report."""
    print(f"\n{'='*50}")
    print(f"  Fleet Status Report - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"{'='*50}\n")

    for s in statuses:
        indicator = "OK" if s["overall"] == "online" else "!!"
        print(f"  [{indicator}] {s['host']:20s} SSH:{s['ssh']:4s}  HTTP:{s['http']:4s}  -> {s['overall']}")

    online = sum(1 for s in statuses if s["overall"] == "online")
    total = len(statuses)
    print(f"\n  Summary: {online}/{total} hosts online\n")

def main():
    parser = argparse.ArgumentParser(description="Fleet Monitor")
    parser.add_argument("--check", metavar="HOST", help="Check specific host")
    parser.add_argument("--check-all", action="store_true", help="Check all configured hosts")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    # TODO: Add --config flag to specify alternate config file
    args = parser.parse_args()

    if args.check:
        status = get_status(args.check)
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print_report([status])
    elif args.check_all:
        # TODO: Read hosts from config.yaml
        hosts = ["shore-hq", "shore-ops", "shore-comms", "ddg71-cic", "cvn78-cic"]
        statuses = [get_status(h) for h in hosts]
        if args.json:
            print(json.dumps(statuses, indent=2))
        else:
            print_report(statuses)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
