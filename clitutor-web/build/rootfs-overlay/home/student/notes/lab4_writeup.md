# Lab 4: Network Reconnaissance and Service Enumeration

## Objective
Identify running services and open ports on the fleet lab network.

## Methodology

### 1. Host Discovery
Used ping sweep to find active hosts:
```bash
for ip in $(seq 1 20); do ping -c1 -W1 10.0.1.$ip 2>/dev/null | grep "bytes from"; done
```

### 2. Port Scanning
Scanned discovered hosts for common services:
```bash
nmap -sT -p 22,80,443,3306,5432 10.0.1.10-12
```

### 3. Service Identification
Results summary:
- shore-hq (10.0.1.10): SSH(22), HTTP(80), filtered SMTP(25), filtered MySQL(3306)
- shore-ops (10.0.1.11): SSH(22), HTTP(80)
- shore-comms (10.0.1.12): SSH(22) only - HTTP appears down

### 4. Web Content Analysis
```bash
curl -s http://10.0.1.10/ | head -20
curl -s http://10.0.1.10/api/status.json | jq .
```

## Findings
- All hosts running SSH on port 22
- shore-hq has filtered ports suggesting firewall rules
- shore-comms missing HTTP service (degraded status confirmed)
- cvn78-ops completely unreachable

## Recommendations
1. Investigate filtered ports on shore-hq — are MySQL/SMTP intentionally exposed?
2. Restore nginx on shore-comms
3. Schedule maintenance window for cvn78-ops recovery
