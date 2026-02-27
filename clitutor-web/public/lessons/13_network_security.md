# Network Security Tools

This lesson covers three essential tools for network security: **nmap** for
reconnaissance, **iptables** for firewall management, and **tcpdump** for
packet capture. These are the same tools used by security professionals on
production systems worldwide.

Your system has nginx (port 80) and sshd (port 22) running -- you will scan,
monitor, and firewall real services.

## `nmap` -- Network Scanner

`nmap` discovers hosts and services on a network by sending packets and
analyzing responses:

```bash
nmap -sT localhost          # TCP connect scan on localhost
nmap -sT -p 1-1000 host    # scan specific port range
nmap -sV -sT localhost      # detect service versions
nmap -O host                # OS detection (requires root)
```

| Flag | Purpose |
|------|---------|
| `-sT` | TCP connect scan (full handshake) |
| `-sV` | Probe open ports for service version |
| `-p` | Port range (e.g., `-p 22,80` or `-p 1-1000`) |
| `-O` | OS detection |
| `-A` | Aggressive: OS + version + scripts + traceroute |

> **Ethics note:** Only scan systems you own or have written authorization to
> test. Unauthorized scanning may violate laws and policies.

<!-- exercise
id: ex01
title: Discover open ports
xp: 20
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: "80/tcp"
hints:
  - "Use nmap to scan the local machine for open TCP ports."
  - "A TCP connect scan (-sT) works without special privileges."
  - "Type: `nmap -sT localhost`"
-->
### Exercise 1: Discover open ports
Run a TCP connect scan on localhost to find which ports are open.

---

## Service Detection

Beyond finding open ports, nmap can identify what software is running on each
port by probing service banners:

```bash
nmap -sV -sT localhost      # version detection on all open ports
nmap -sV -sT -p 22 host    # version detection on a specific port
```

This tells you not just that port 80 is open, but that it is running nginx,
and not just that port 22 is open, but that it is running OpenSSH.

<!-- exercise
id: ex02
title: Detect service versions
xp: 20
difficulty: 2
sandbox_setup: null
validation_type: output_regex
expected: "nginx|OpenSSH"
hints:
  - "Add version detection to your nmap scan."
  - "Use -sV along with -sT to probe service banners."
  - "Type: `nmap -sV -sT localhost`"
-->
### Exercise 2: Detect service versions
Scan localhost with version detection to identify the software running on each
open port.

---

## `iptables` -- Firewall Rules

`iptables` is the traditional Linux firewall. It filters packets using chains
of rules:

| Chain | Purpose |
|-------|---------|
| `INPUT` | Packets arriving at this machine |
| `OUTPUT` | Packets leaving this machine |
| `FORWARD` | Packets being routed through this machine |

Each rule specifies match criteria and a **target** (action):

| Target | Action |
|--------|--------|
| `ACCEPT` | Allow the packet |
| `DROP` | Silently discard the packet |
| `REJECT` | Discard and send an error back |

```bash
iptables -L -n              # list all rules (numeric)
iptables -L INPUT -n        # list INPUT chain only
iptables -A INPUT -p tcp --dport 8080 -j DROP   # block port 8080
iptables -D INPUT 1         # delete rule #1 from INPUT
iptables -F                 # flush all rules
```

<!-- exercise
id: ex03
title: List firewall rules
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: "Chain INPUT"
hints:
  - "Use iptables to display the current firewall rules."
  - "The -L flag lists rules. Add -n for numeric output."
  - "Type: `iptables -L -n`"
-->
### Exercise 3: List firewall rules
Display the current iptables firewall rules for all chains.

---

## Adding Firewall Rules

Rules are evaluated top-to-bottom. The first match wins. Here is how to block
incoming traffic on a specific port:

```bash
# Block incoming TCP connections on port 8080
iptables -A INPUT -p tcp --dport 8080 -j DROP

# Verify the rule was added
iptables -L -n
```

The `-A` flag appends a rule to a chain. Use `-I` to insert at the top instead.

<!-- exercise
id: ex04
title: Add a firewall rule
xp: 20
difficulty: 3
sandbox_setup: null
validation_type: output_contains
expected: "8080"
hints:
  - "Add an iptables rule to block port 8080, then list the rules."
  - "Use -A INPUT to append to the INPUT chain, -p tcp --dport for the port, and -j DROP for the action."
  - "Type: `iptables -A INPUT -p tcp --dport 8080 -j DROP && iptables -L -n`"
-->
### Exercise 4: Add a firewall rule
Block incoming TCP traffic on port 8080 and then display the rules to confirm.

---

## `tcpdump` -- Packet Capture

`tcpdump` captures network traffic for analysis. It is the command-line
equivalent of Wireshark:

```bash
tcpdump -D                  # list available capture interfaces
tcpdump -i lo               # capture on loopback interface
tcpdump -i eth0 port 80     # capture HTTP traffic
tcpdump -c 10 -i lo         # capture 10 packets then stop
tcpdump -w capture.pcap     # write to file for later analysis
```

| Flag | Purpose |
|------|---------|
| `-D` | List available interfaces |
| `-i` | Specify interface |
| `-c` | Capture N packets then stop |
| `-w` | Write packets to a pcap file |
| `-n` | Don't resolve hostnames |
| `-v` | Verbose output |

<!-- exercise
id: ex05
title: List capture interfaces
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: lo
hints:
  - "Use tcpdump to list the network interfaces available for capture."
  - "The -D flag shows all capture interfaces."
  - "Type: `tcpdump -D`"
-->
### Exercise 5: List capture interfaces
Display the network interfaces available for packet capture.

---

## Putting It Together

Security professionals combine these tools in scripts to monitor systems.
A simple monitoring script might scan for open ports and check that a web
server is responding:

```bash
#!/bin/bash
echo "=== Port Scan ==="
nmap -sT -p 22,80 localhost
echo "=== Web Server Check ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost
echo ""
```

<!-- exercise
id: ex06
title: Write a monitoring script
xp: 30
difficulty: 3
sandbox_setup: null
validation_type: file_contains
expected: "monitor.sh::nmap"
hints:
  - "Create a shell script that uses nmap to scan localhost."
  - "The script should include an nmap command. Use echo and redirection or a heredoc."
  - "Type: `printf '#!/bin/bash\\nnmap -sT -p 22,80 localhost\\ncurl -s http://localhost\\n' > monitor.sh`"
-->
### Exercise 6: Write a monitoring script
Create a file called `monitor.sh` that uses `nmap` to scan localhost and `curl`
to check the web server.

---

## What You Learned

- **`nmap`** -- scan networks for open ports and identify services
- **`iptables`** -- configure Linux firewall rules (INPUT, OUTPUT, FORWARD chains)
- **`tcpdump`** -- capture and inspect network packets
- **Defense-in-depth** -- combine scanning, firewalling, and monitoring
