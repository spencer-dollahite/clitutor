# SSH

**SSH** (Secure Shell) is the standard way to securely connect to remote
machines over a network. It encrypts all traffic, provides authentication, and
is used for remote administration, file transfer, and tunneling.

## Basic Connection

```bash
ssh admin@shore-server           # connect to remote host
ssh operator@172.16.50.10        # connect by IP
ssh -p 2222 admin@host           # use a non-standard port
```

The first time you connect to a host, SSH asks you to verify the host's
fingerprint. This protects against man-in-the-middle attacks.

<!-- exercise
id: ex01
title: Check if SSH client is installed
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: usage
hints:
  - "Run the ssh command with no arguments or a help flag to see if it is available."
  - "Try running ssh with no arguments -- it usually prints a usage summary."
  - "Type: `ssh 2>&1 | head -1`"
-->
### Exercise 1: Check if SSH client is installed
Verify that the SSH client is available on your system by printing its usage information.

---

## SSH Key Pairs

Instead of typing a password every time, you can use **key-based
authentication**. This is both more secure and more convenient.

A key pair consists of:
- **Private key** (`~/.ssh/id_ed25519`) -- kept secret, never shared
- **Public key** (`~/.ssh/id_ed25519.pub`) -- placed on remote servers

### Generate a Key Pair

```bash
ssh-keygen -t ed25519 -C "operator@fleet.mil"
```

You will be asked for a location (default is fine) and a passphrase (optional
but recommended for extra security).

### Copy Your Key to a Server

```bash
ssh-copy-id admin@shore-server
```

This adds your public key to `~/.ssh/authorized_keys` on the remote machine.

<!-- exercise
id: ex02
title: Generate an SSH key pair
xp: 15
difficulty: 2
sandbox_setup:
  - "mkdir -p .ssh"
validation_type: file_exists
expected: .ssh/fleet_access.pub
hints:
  - "Use ssh-keygen with options for key type and output file."
  - "Use -t for type, -f for filename, and -N '' for an empty passphrase."
  - "Type: `ssh-keygen -t ed25519 -f .ssh/fleet_access -N '' -q`"
-->
### Exercise 2: Generate an SSH key pair
Generate an Ed25519 key pair saved as `.ssh/fleet_access` (with an empty passphrase for this exercise).

---

## SSH Config File

The `~/.ssh/config` file lets you create shortcuts for frequently accessed
servers:

```
Host shore-server
    HostName 172.16.50.10
    User admin
    Port 22
    IdentityFile ~/.ssh/fleet_access

Host cic-workstation
    HostName 10.1.100.20
    User operator
    Port 2222
    ForwardAgent yes
```

Now you can simply type `ssh shore-server` or `ssh cic-workstation` instead of
remembering all the connection details.

<!-- exercise
id: ex03
title: Create an SSH config
xp: 15
difficulty: 2
sandbox_setup:
  - "mkdir -p .ssh"
validation_type: file_contains
expected: .ssh/config::HostName 172.16.50.10
hints:
  - "Write an SSH config block to a file using echo or printf."
  - "An SSH config block has Host, HostName, User, and other directives."
  - "Type: `printf 'Host shore-server\\n    HostName 172.16.50.10\\n    User admin\\n    Port 22\\n' > .ssh/config`"
-->
### Exercise 3: Create an SSH config
Create an SSH config file at `.ssh/config` with a host entry for `shore-server` pointing to `172.16.50.10`.

---

## Connecting with SSH Keys

With sshd running on this system, you can make a real SSH connection to
`localhost`. This is exactly how you would connect to any remote server --
the only difference is the destination address.

```bash
# Generate a key, then connect
ssh-keygen -t ed25519 -f .ssh/local_key -N '' -q
cat .ssh/local_key.pub >> .ssh/authorized_keys
chmod 600 .ssh/authorized_keys
ssh -i .ssh/local_key -o StrictHostKeyChecking=no student@localhost hostname
```

The `-o StrictHostKeyChecking=no` flag skips the fingerprint prompt (acceptable
for localhost; on real servers, always verify the fingerprint).

<!-- exercise
id: ex04
title: Connect to localhost via SSH
xp: 15
difficulty: 2
sandbox_setup:
  - "ssh-keygen -t ed25519 -f .ssh/local_key -N '' -q"
  - "cat .ssh/local_key.pub >> .ssh/authorized_keys"
  - "chmod 600 .ssh/authorized_keys"
validation_type: output_contains
expected: clitutor
hints:
  - "Use ssh with -i to specify the key file."
  - "Connect to student@localhost and run a command."
  - "Type: `ssh -i .ssh/local_key -o StrictHostKeyChecking=no student@localhost hostname`"
-->
### Exercise 4: Connect to localhost via SSH
Use your key to SSH into `student@localhost` and run `hostname` to prove the connection works.

---

## SCP and SFTP -- Transferring Files

### SCP (Secure Copy)

```bash
# Copy local file to remote
scp sitrep.txt admin@shore-server:/reports/

# Copy remote file to local
scp admin@shore-server:/reports/sitrep.txt ./local/

# Copy directory recursively
scp -r logs/ admin@shore-server:/archive/

# Use a specific port
scp -P 2222 file.txt admin@host:/path/
```

### SFTP (Secure FTP)

```bash
sftp admin@shore-server
# Interactive commands: ls, cd, get, put, mkdir, quit
```

---

## SSH Tunneling (Port Forwarding)

SSH can forward network traffic through an encrypted tunnel:

### Local Port Forwarding

Access a remote service through a local port:

```bash
# Access shore-server:3306 (MySQL) via localhost:3307
ssh -L 3307:localhost:3306 admin@shore-server
```

### Remote Port Forwarding

Expose a local service on the remote machine:

```bash
# Make local port 8080 available on remote as port 9090
ssh -R 9090:localhost:8080 admin@shore-server
```

### SOCKS Proxy

```bash
# Create a SOCKS proxy on local port 1080
ssh -D 1080 admin@shore-server
```

<!-- exercise
id: ex05
title: Check SSH key permissions
xp: 15
difficulty: 2
sandbox_setup:
  - "mkdir -p .ssh"
  - "ssh-keygen -t ed25519 -f .ssh/shore_key -N '' -q"
  - "chmod 644 .ssh/shore_key"
validation_type: output_contains
expected: rw-------
hints:
  - "SSH private keys must have restrictive permissions (600)."
  - "Use chmod to set the correct permissions, then ls -l to verify."
  - "Type: `chmod 600 .ssh/shore_key && ls -l .ssh/shore_key`"
-->
### Exercise 5: Fix SSH key permissions
The private key `.ssh/shore_key` has incorrect permissions. Fix them to the required `600` and verify.

---

## SSH Security Best Practices

1. **Use key-based authentication** -- disable password auth when possible
2. **Protect your private key** -- permissions must be `600` (`-rw-------`)
3. **Use a passphrase** -- adds a second factor if your key is stolen
4. **Disable root login** -- force users to log in as themselves, then `sudo`
5. **Change the default port** -- reduces automated scanning noise
6. **Use `ssh-agent`** -- caches your key passphrase so you don't re-enter it

```bash
# Start ssh-agent and add your key
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/fleet_access
```

<!-- exercise
id: ex06
title: View authorized_keys format
xp: 15
difficulty: 2
sandbox_setup:
  - "mkdir -p .ssh"
  - "ssh-keygen -t ed25519 -f .ssh/shore_key -N '' -q"
validation_type: output_contains
expected: ssh-ed25519
hints:
  - "The public key file is what goes into authorized_keys."
  - "View the contents of the public key file."
  - "Type: `cat .ssh/shore_key.pub`"
-->
### Exercise 6: View the public key format
Display the contents of the generated public key file `.ssh/shore_key.pub` to see the authorized_keys format.

---

## What You Learned

- **`ssh`** -- securely connect to remote machines
- **`ssh-keygen`** -- generate key pairs for passwordless authentication
- **`~/.ssh/config`** -- create connection shortcuts
- **`scp`** / **`sftp`** -- securely transfer files
- **SSH tunneling** -- local and remote port forwarding
- **Security best practices** -- key permissions, passphrases, agent forwarding
