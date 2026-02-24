# Networking Tools

The command line provides powerful tools for network troubleshooting,
exploration, and data transfer. This lesson covers the essential networking
commands you will use daily as a systems administrator or security
professional.

## `ip` / `ifconfig` -- View Network Interfaces

The `ip` command (modern) or `ifconfig` (legacy) shows your network
configuration:

```bash
ip a                    # show all interfaces and addresses
ip addr show            # same thing
ip -4 addr              # IPv4 addresses only
ip link show            # interface status (up/down)
ip route                # show the routing table

# Legacy (may not be installed)
ifconfig                # show all interfaces
ifconfig eth0           # show specific interface
```

<!-- exercise
id: ex01
title: View your IP configuration
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: inet
hints:
  - "Use the modern command to view all network interfaces."
  - "The command is 'ip' with the 'a' (address) subcommand."
  - "Type: `ip a`"
-->
### Exercise 1: View your IP configuration
Display all network interfaces and their IP addresses.

---

## `ping` -- Test Connectivity

`ping` sends ICMP echo requests to test if a host is reachable:

```bash
ping -c 4 google.com       # send 4 pings then stop
ping -c 1 192.168.1.1      # single ping
ping -c 1 -W 2 10.0.0.1    # timeout after 2 seconds
```

> **Note:** Some networks block ICMP, so a failed ping does not always mean the
> host is down.

<!-- exercise
id: ex02
title: Ping localhost
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: "1 received"
hints:
  - "Ping the local machine with a limited count."
  - "Use -c to specify the number of pings. Localhost is 127.0.0.1."
  - "Type: `ping -c 1 127.0.0.1`"
-->
### Exercise 2: Ping localhost
Send a single ping to localhost (127.0.0.1) and confirm it is received.

---

## `curl` and `wget` -- Transfer Data

`curl` and `wget` download files and interact with web services:

```bash
# curl - transfer data from/to a server
curl https://example.com               # fetch a page
curl -o file.html https://example.com   # save to file
curl -I https://example.com             # headers only
curl -s https://api.example.com/data    # silent mode (no progress)

# wget - download files
wget https://example.com/file.tar.gz    # download a file
wget -q -O- https://example.com        # quiet, output to stdout
```

`curl` is especially useful for working with APIs:

```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"key":"value"}' \
     https://api.example.com/endpoint
```

<!-- exercise
id: ex03
title: Fetch HTTP headers
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: HTTP
hints:
  - "Use curl with a flag that shows only the response headers."
  - "The -I flag fetches HTTP headers only."
  - "Type: `curl -sI http://example.com`"
-->
### Exercise 3: Fetch HTTP headers
Fetch only the HTTP headers from `http://example.com` using curl.

---

## `nslookup` / `dig` -- DNS Lookups

DNS translates domain names to IP addresses. These tools let you query DNS
directly:

```bash
nslookup example.com              # simple DNS lookup
nslookup -type=MX example.com     # mail server records

dig example.com                    # detailed DNS query
dig +short example.com            # just the IP
dig example.com MX                # mail records
```

<!-- exercise
id: ex04
title: Look up a domain
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: Address
hints:
  - "Use a DNS lookup tool to resolve a domain name."
  - "nslookup is a simple DNS query tool."
  - "Type: `nslookup example.com`"
-->
### Exercise 4: Look up a domain
Perform a DNS lookup for `example.com`.

---

## `/etc/hosts` -- Local Name Resolution

Before querying DNS, your system checks `/etc/hosts` for local name mappings:

```
127.0.0.1   localhost
127.0.1.1   myhostname
192.168.1.10 devserver
```

This is useful for:
- Overriding DNS for testing
- Adding shortcuts to internal servers
- Blocking domains (point them to 127.0.0.1)

<!-- exercise
id: ex05
title: View the hosts file
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: localhost
hints:
  - "The hosts file is a system file that maps hostnames to IPs."
  - "It lives at /etc/hosts. Use cat to view it."
  - "Type: `cat /etc/hosts`"
-->
### Exercise 5: View the hosts file
Display the contents of the system hosts file.

---

## `ss` / `netstat` -- Network Connections

See what is listening and connected on your system:

```bash
ss -tlnp               # TCP listening ports with process info
ss -ulnp               # UDP listening ports
ss -a                  # all connections
ss -tn                 # established TCP connections

# Legacy
netstat -tlnp           # same as ss -tlnp (may need net-tools package)
```

| Flag | Meaning |
|------|---------|
| `-t` | TCP |
| `-u` | UDP |
| `-l` | Listening sockets only |
| `-n` | Numeric (don't resolve names) |
| `-p` | Show process using the socket |

<!-- exercise
id: ex06
title: List listening ports
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: State
hints:
  - "Use ss to show listening TCP sockets."
  - "Combine the -t (TCP) and -l (listening) flags."
  - "Type: `ss -tln`"
-->
### Exercise 6: List listening ports
Display all TCP ports that are currently in a listening state.

---

## `traceroute` -- Trace the Network Path

`traceroute` shows the path packets take to reach a destination, listing every
router (hop) along the way:

```bash
traceroute example.com
traceroute -n example.com     # numeric only (skip DNS)
```

Each line represents a hop. You will see the IP address and round-trip time for
each. Asterisks (`* * *`) mean the hop did not respond (likely filtered).

<!-- exercise
id: ex07
title: Write a local hosts entry
xp: 20
difficulty: 2
sandbox_setup: null
validation_type: file_contains
expected: my_hosts::127.0.0.1 myapp.local
hints:
  - "Create a file with a hosts-style entry mapping a hostname to an IP."
  - "Use echo with redirection to write the entry."
  - "Type: `echo '127.0.0.1 myapp.local' > my_hosts`"
-->
### Exercise 7: Write a local hosts entry
Create a file called `my_hosts` containing a hosts entry that maps `myapp.local` to `127.0.0.1`.

---

## What You Learned

- **`ip a`** / `ifconfig` -- view network interface configuration
- **`ping`** -- test host reachability
- **`curl`** / `wget` -- download files and interact with web services
- **`nslookup`** / `dig` -- DNS lookups
- **`/etc/hosts`** -- local hostname resolution
- **`ss`** / `netstat` -- view listening ports and connections
- **`traceroute`** -- trace the network path to a host
