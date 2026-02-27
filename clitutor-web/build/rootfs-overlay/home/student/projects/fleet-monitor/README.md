# Fleet Monitor

A Python-based monitoring tool for fleet shore station infrastructure.

## Overview

Fleet Monitor checks the health and availability of networked systems across
shore stations and afloat units. It collects metrics, parses logs, and generates
status reports.

## Usage

```bash
# Check all hosts
python3 monitor.py --check-all

# Check specific host
python3 monitor.py --check shore-hq

# Parse auth logs for suspicious activity
python3 parse_logs.py /var/log/auth.log

# Run tests
make test
```

## Configuration

Edit `config.yaml` to add hosts or adjust thresholds.

## Files

| File | Purpose |
|------|---------|
| monitor.py | Main monitoring script |
| parse_logs.py | Log analysis and reporting |
| config.yaml | Host and threshold configuration |
| Makefile | Build and test automation |

## TODO

- [ ] Add email alerting for critical status
- [ ] Implement log rotation
- [ ] Add Grafana dashboard export
- [ ] Support for SNMP polling
