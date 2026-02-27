# Next Steps: Beyond the Browser

Congratulations -- you have completed 14 lessons of hands-on Linux command-line
training. You can navigate filesystems, process text, manage permissions, write
scripts, use networking tools, configure SSH, manage Git repositories, and
more. These skills work on any Linux system you will ever touch.

This final lesson helps you set up a real Linux environment and plan your
continued learning.

## What You Have Learned

Across these lessons you have built a solid foundation:

- **Navigation and files** -- `pwd`, `ls`, `cd`, `cp`, `mv`, `rm`, `mkdir`
- **Text processing** -- `grep`, `sed`, `awk`, `cut`, `sort`, `uniq`, pipes
- **Permissions** -- `chmod`, `chown`, `umask`, user/group/other model
- **Shell productivity** -- history, aliases, job control, tab completion
- **PATH and environment** -- how the shell finds commands
- **Prompt customization** -- PS1 and escape sequences
- **Shell scripting** -- variables, conditionals, loops, functions
- **Networking** -- `ip`, `ping`, `curl`, `ss`, DNS configuration
- **SSH** -- key generation, config files, real connections
- **Git** -- init, add, commit, branch, merge, log
- **vi/vim** -- modal editing, navigation, search, replace
- **tmux** -- sessions, windows, panes, detach/reattach
- **Dotfiles** -- `.bashrc`, `.profile`, hidden configuration files
- **Network security** -- `nmap`, `iptables`, `tcpdump`

<!-- exercise
id: ex01
title: Identify your system
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: Linux
hints:
  - "Use a command that prints system information."
  - "The uname command shows operating system details."
  - "Type: `uname -a`"
-->
### Exercise 1: Identify your system
Print detailed information about the operating system running in this VM.

---

## Setting Up Your Own Linux Environment

The browser VM is great for learning, but you will want a full environment for
real work. Here are your options, roughly ordered from easiest to most flexible:

### WSL2 (Windows)

If you run Windows 10/11, the Windows Subsystem for Linux gives you a real
Linux kernel with full tool compatibility:

```
wsl --install
```

This installs Ubuntu by default. You get a full bash shell, apt package
management, and access to your Windows files at `/mnt/c/`.

### UTM (macOS) / Multipass

On macOS, **UTM** provides a graphical VM manager, or use Canonical's
**Multipass** for quick command-line VMs:

```
brew install multipass
multipass launch --name dev
multipass shell dev
```

### VirtualBox (Cross-Platform)

Oracle VirtualBox runs on Windows, macOS, and Linux. Download an Ubuntu Server
ISO and create a VM with 2GB RAM and 20GB disk.

### Cloud VMs

All major cloud providers offer free-tier or low-cost VMs:

- **AWS** -- EC2 t2.micro (free tier, 12 months)
- **Google Cloud** -- e2-micro (always free)
- **Azure** -- B1s (free tier, 12 months)
- **DigitalOcean** -- $4/month droplet

For all of these, choose **Ubuntu Server 22.04 LTS** as your first real
distribution. It has the largest community, the most tutorials, and long-term
support.

<!-- exercise
id: ex02
title: Write a setup plan
xp: 20
difficulty: 1
sandbox_setup: null
validation_type: file_contains
expected: "setup_plan.txt::Linux"
hints:
  - "Create a text file describing which Linux environment you plan to set up."
  - "Your plan should mention Linux and your chosen method (WSL2, VM, cloud, etc.)."
  - "Example: `echo 'I will install Linux using WSL2 on my Windows laptop' > setup_plan.txt`"
-->
### Exercise 2: Write a setup plan
Create a file called `setup_plan.txt` describing which Linux environment you
plan to set up and why.

---

## What to Learn Next

These topics require a full Linux environment with package management, systemd,
and network access -- things that do not exist in the browser VM:

### Package Management
Every Linux distribution has a package manager. Ubuntu uses `apt`:
```bash
sudo apt update && sudo apt install nginx
```
Fedora uses `dnf`, Arch uses `pacman`. Learn the one your distro uses.

### Systemd Service Management
Most modern distributions use `systemd` to manage services:
```bash
sudo systemctl start nginx
sudo systemctl enable nginx
sudo systemctl status nginx
```

### Docker and Containers
Containers package applications with their dependencies:
```bash
docker run -p 8080:80 nginx
docker build -t myapp .
docker compose up -d
```

### Advanced Networking
- VLANs and bridges
- VPN configuration (WireGuard, OpenVPN)
- DNS server setup (bind, dnsmasq)

### Configuration Management
Automate server setup across many machines:
- **Ansible** -- agentless, SSH-based, YAML playbooks
- **Terraform** -- infrastructure as code for cloud resources

### Cloud CLIs
Manage cloud infrastructure from the command line:
```bash
aws ec2 describe-instances
gcloud compute instances list
az vm list
```

## Resources

Here are high-quality, free resources to continue your learning:

- **OverTheWire Bandit** (overthewire.org/wargames/bandit) -- security-focused
  CLI challenges, perfect next step after this course
- **The Linux Command Line** by William Shotts -- comprehensive free book
  (linuxcommand.org)
- **Linux Journey** (linuxjourney.com) -- interactive tutorials covering
  everything from basics to system administration
- **Docker Getting Started** (docs.docker.com/get-started) -- official
  container tutorial
- **Ansible Getting Started** (docs.ansible.com/ansible/latest/getting_started)
  -- automation fundamentals
- **SANS SEC275 / CyberDefense courses** -- professional security training

<!-- exercise
id: ex03
title: Set learning goals
xp: 20
difficulty: 1
sandbox_setup: null
validation_type: file_contains
expected: "learning_goals.txt::learn"
hints:
  - "Create a text file listing what you want to learn next."
  - "Your goals should include the word 'learn' and mention specific topics."
  - "Example: `echo 'I want to learn Docker and Ansible for DevOps' > learning_goals.txt`"
-->
### Exercise 3: Set learning goals
Create a file called `learning_goals.txt` listing three things you want to
learn next.

---

## What You Learned

- **Where to go next** -- WSL2, VMs, or cloud for a real Linux environment
- **What to learn next** -- package management, systemd, Docker, and beyond
- **Resources** -- books, websites, and courses for continued growth

You are ready. Go build something.
