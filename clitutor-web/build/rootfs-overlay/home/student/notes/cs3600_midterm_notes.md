# CS3600 Midterm Study Notes

## File System Hierarchy
- `/` - root of everything
- `/home` - user home directories
- `/etc` - system configuration
- `/var` - variable data (logs, mail, spool)
- `/usr` - user programs and data
- `/tmp` - temporary files (cleared on reboot)
- `/proc` - virtual filesystem for process info
- `/dev` - device files

## Key Commands to Remember
- `ls -la` - list all files including hidden, long format
- `chmod 755 file` - rwxr-xr-x
- `chmod 600 file` - rw------- (private files like .ssh/id_rsa)
- `find / -name "*.conf"` - search for files by name
- `grep -r "pattern" /path` - recursive search for text
- `ps aux` - list all processes
- `netstat -tlnp` - list listening TCP ports

## Permission Bits
```
rwx = 4+2+1 = 7
rw- = 4+2+0 = 6
r-x = 4+0+1 = 5
r-- = 4+0+0 = 4
```

## Important Files
- `/etc/passwd` - user accounts (not actually passwords anymore)
- `/etc/shadow` - hashed passwords (root only)
- `/etc/hosts` - static hostname resolution
- `/etc/resolv.conf` - DNS resolver config
- `/etc/ssh/sshd_config` - SSH server settings

## Pipe Examples
```bash
cat /var/log/auth.log | grep "Failed" | awk '{print $11}' | sort | uniq -c | sort -rn
ps aux | grep nginx | grep -v grep
find . -name "*.py" -exec wc -l {} + | sort -n
```

## Exam Topics
- [ ] File permissions and ownership
- [ ] Process management (ps, kill, jobs, bg, fg)
- [ ] Network basics (ip addr, ss, nmap, curl)
- [ ] Shell scripting (variables, loops, conditionals)
- [ ] SSH key-based authentication
- [ ] Log analysis with grep/awk/sed
