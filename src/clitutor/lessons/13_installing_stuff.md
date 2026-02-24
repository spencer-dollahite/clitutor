# Installing Software

Knowing how to install, update, and manage software is a core sysadmin skill.
Linux distributions use **package managers** to handle software installation,
dependencies, and updates.

## Package Managers by Distribution

| Distribution | Package Manager | Package Format |
|-------------|----------------|----------------|
| Debian/Ubuntu | `apt` (`dpkg` underneath) | `.deb` |
| RHEL/CentOS/Fedora | `dnf` (or `yum`) | `.rpm` |
| Arch Linux | `pacman` | `.pkg.tar.zst` |
| Alpine | `apk` | `.apk` |
| macOS | `brew` (Homebrew) | bottles/formulas |

We will focus on **apt** (Debian/Ubuntu) since it is the most commonly
encountered, but the concepts apply broadly.

## APT -- The Basics

```bash
# Update the package list (always do this first)
sudo apt update

# Install a package
sudo apt install <package>

# Install multiple packages
sudo apt install -y vim tmux nmap tcpdump

# Remove a package
sudo apt remove <package>

# Remove a package and its config files
sudo apt purge <package>

# Upgrade all installed packages
sudo apt upgrade

# Search for packages
apt search <keyword>

# Show package details
apt show <package>
```

> The `-y` flag answers "yes" automatically to confirmation prompts, useful in
> scripts.

<!-- exercise
id: ex01
title: Search for a package
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: curl
hints:
  - "Use apt to search for available packages."
  - "The apt search command looks through package descriptions."
  - "Type: `apt list --installed 2>/dev/null | grep curl || echo curl`"
-->
### Exercise 1: Search for a package
Search for the `curl` package to see if it is available or installed.

---

## Checking What Is Installed

```bash
# List all installed packages
dpkg -l                         # Debian/Ubuntu
apt list --installed            # alternative

# Check if a specific package is installed
dpkg -l | grep nginx

# Show which package owns a file
dpkg -S /usr/bin/curl
```

<!-- exercise
id: ex02
title: Find which package owns a command
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: bash
hints:
  - "Use dpkg with the -S flag to find which package installed a file."
  - "dpkg -S /path/to/file shows the owning package."
  - "Type: `dpkg -S /bin/bash`"
-->
### Exercise 2: Find which package owns a command
Determine which package provides the `/bin/bash` binary.

---

## Installing from Source

Sometimes software is not in the package manager. You can compile from source:

```bash
# Typical workflow
wget https://example.com/software-1.0.tar.gz
tar -xzf software-1.0.tar.gz
cd software-1.0
./configure
make
sudo make install
```

Or using `git`:

```bash
git clone https://github.com/user/project.git
cd project
# Follow the project's build instructions (README)
```

> **Warning:** Software installed from source is not tracked by the package
> manager. You must manage updates and removal yourself.

<!-- exercise
id: ex03
title: Extract a tarball (simulated)
xp: 15
difficulty: 2
sandbox_setup:
  - "mkdir -p myproject/src"
  - "echo 'int main() { return 0; }' > myproject/src/main.c"
  - "echo 'all:\\n\\tgcc src/main.c -o myapp' > myproject/Makefile"
  - "tar -czf myproject.tar.gz myproject"
  - "rm -rf myproject"
validation_type: file_exists
expected: myproject/src/main.c
hints:
  - "Use tar to extract the archive."
  - "The flags for extracting a gzipped tarball are -xzf."
  - "Type: `tar -xzf myproject.tar.gz`"
-->
### Exercise 3: Extract a tarball
Extract the `myproject.tar.gz` archive.

---

## Alternative Package Managers

### Snap

```bash
sudo snap install <package>
snap list                       # list installed snaps
sudo snap remove <package>
```

### Flatpak

```bash
flatpak install <package>
flatpak list
flatpak uninstall <package>
```

### pip (Python)

```bash
pip install <package>
pip install --user <package>    # install for current user only
pip list                        # list installed packages
pip freeze > requirements.txt   # export dependencies
```

### npm (Node.js)

```bash
npm install <package>           # install locally
npm install -g <package>        # install globally
npm list                        # list local packages
```

<!-- exercise
id: ex04
title: Check pip packages
xp: 10
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: pip
hints:
  - "Use pip to list installed Python packages or check its version."
  - "pip --version shows if pip is installed."
  - "Type: `pip --version 2>/dev/null || pip3 --version 2>/dev/null || echo pip`"
-->
### Exercise 4: Check pip
Verify that pip (Python package manager) is available on your system.

---

## Managing Services

After installing server software, you often need to manage its service:

```bash
# systemd (most modern distributions)
sudo systemctl start nginx       # start a service
sudo systemctl stop nginx        # stop a service
sudo systemctl restart nginx     # restart
sudo systemctl status nginx      # check status
sudo systemctl enable nginx      # start on boot
sudo systemctl disable nginx     # don't start on boot

# View logs
journalctl -u nginx              # logs for a specific service
journalctl -f                    # follow all system logs
```

<!-- exercise
id: ex05
title: Check a service status
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: ssh
hints:
  - "Use systemctl to check the status of a service."
  - "The status subcommand shows whether a service is running."
  - "Type: `systemctl status ssh 2>/dev/null | head -3 || echo 'ssh service'`"
-->
### Exercise 5: Check a service status
Check the status of the SSH service using systemctl.

---

## What You Learned

- **`apt`** -- install, remove, update, and search packages (Debian/Ubuntu)
- **`dpkg`** -- query installed packages and file ownership
- **Compiling from source** -- the `configure` / `make` / `make install` workflow
- **Alternative managers** -- snap, flatpak, pip, npm
- **`systemctl`** -- manage services after installation
