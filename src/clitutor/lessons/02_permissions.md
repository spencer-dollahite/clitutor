# File Permissions

Linux is a multi-user operating system. Permissions control who can read, write,
and execute files. Understanding permissions is essential for system
administration and security.

## The Permission Bits

Run `ls -l` to see permissions in action:

```
-rw-r--r-- 1 alice dev  1234 Aug 30 12:00 notes.txt
drwxr-xr-x 2 root  root 4096 Aug 30 12:00 bin
```

The leftmost column is the **mode string**, broken down as:

```
[type] [owner perms] [group perms] [other perms]
 1 char   3 chars       3 chars       3 chars
```

**File type** (first character):
- `-` regular file
- `d` directory
- `l` symbolic link

**Permission triplets** (rwx):

| Letter | Meaning | Octal Value |
|--------|---------|-------------|
| `r`    | read    | 4           |
| `w`    | write   | 2           |
| `x`    | execute | 1           |
| `-`    | not set | 0           |

The three sets apply to: **owner** (the file's owner), **group** (the file's
owning group), and **other** (everyone else).

---

## What the Bits Mean

**For regular files:**
- `r` -- can read file contents
- `w` -- can modify file contents
- `x` -- can execute the file as a program/script

**For directories:**
- `r` -- can list names in the directory
- `w` -- can create, delete, or rename entries
- `x` -- can enter/traverse the directory (access items within by path)

> **Important:** Deleting a file requires write+execute on the **directory**,
> not on the file itself.

---

## Octal (Numeric) Permissions

Each triplet maps to a single digit by summing r=4, w=2, x=1:

| Symbolic | Octal | Common Use |
|----------|-------|------------|
| `rw-r--r--` | 644 | Regular text files |
| `rw-------` | 600 | Private files (e.g., SSH keys) |
| `rwxr-xr-x` | 755 | Directories, executables |
| `rwx------` | 700 | Private directory or script |
| `rwxrwx---` | 770 | Shared within a group |

<!-- exercise
id: ex01
title: Read permission bits
xp: 10
difficulty: 1
sandbox_setup:
  - "touch secret.txt"
  - "chmod 640 secret.txt"
validation_type: output_contains
expected: rw-r-----
hints:
  - "You need to see the detailed listing of a file to read its permissions."
  - "Use ls with the -l flag to see file metadata."
  - "Type: `ls -l secret.txt`"
-->
### Exercise 1: Read permission bits
Display the permissions of `secret.txt` using a long listing.

---

## `chmod` -- Changing Permissions

You can set permissions with **octal notation** or **symbolic notation**:

```bash
# Octal
chmod 644 notes.txt       # rw-r--r--
chmod 755 script.sh       # rwxr-xr-x
chmod 600 private.key     # rw-------

# Symbolic
chmod u+x script.sh       # add execute for owner
chmod g-w file.txt         # remove write from group
chmod o=r file.txt         # set other to read-only
chmod a-x file.txt         # remove execute from all
```

**Symbolic format:** `[who][op][perm]`
- who: `u` (user/owner), `g` (group), `o` (other), `a` (all)
- op: `+` (add), `-` (remove), `=` (set exactly)
- perm: `r`, `w`, `x`

<!-- exercise
id: ex02
title: Make a file executable
xp: 15
difficulty: 2
sandbox_setup:
  - "echo '#!/bin/bash' > myscript.sh"
  - "echo 'echo hello' >> myscript.sh"
  - "chmod 644 myscript.sh"
validation_type: output_contains
expected: rwxr-xr-x
hints:
  - "You need to set the file to be executable by everyone."
  - "Use chmod with octal 755 or symbolic u+x,g+x,o+x."
  - "Type: `chmod 755 myscript.sh && ls -l myscript.sh`"
-->
### Exercise 2: Make a file executable
Make `myscript.sh` executable (permissions `755`) and verify with `ls -l`.

---

## `chown` and `chgrp` -- Ownership

```bash
chown alice file.txt          # change owner to alice
chown alice:dev file.txt      # change owner and group
chgrp dev file.txt            # change group only
chown -R alice:dev dir/       # recursive ownership change
```

> Note: Changing ownership typically requires root/sudo privileges.

<!-- exercise
id: ex03
title: Set restrictive permissions
xp: 15
difficulty: 2
sandbox_setup:
  - "echo 'TOP SECRET DATA' > classified.txt"
  - "chmod 644 classified.txt"
validation_type: output_contains
expected: rw-------
hints:
  - "You need to set permissions so only the owner can read and write."
  - "The octal for owner read+write only is 600."
  - "Type: `chmod 600 classified.txt && ls -l classified.txt`"
-->
### Exercise 3: Set restrictive permissions
Set `classified.txt` so only the owner can read and write it (no access for group or others). Verify with `ls -l`.

---

## Special Permission Bits

Three special bits exist beyond the standard rwx:

| Bit | Octal | On Files | On Directories |
|-----|-------|----------|----------------|
| **setuid** | 4000 | Runs as file owner | (rare) |
| **setgid** | 2000 | Runs as file group | New files inherit directory group |
| **sticky** | 1000 | (rare) | Users can only delete own files |

These appear in `ls -l` as `s` or `t`:
- setuid: owner execute shows as `s` (e.g., `-rwsr-xr-x`)
- setgid: group execute shows as `s` (e.g., `drwxrwsr-x`)
- sticky: other execute shows as `t` (e.g., `drwxrwxrwt`)

The classic example is `/tmp` which is `1777` (drwxrwxrwt) -- everyone can
write, but you can only delete your own files.

<!-- exercise
id: ex04
title: Create a sticky directory
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_regex
expected: "d.{8}[tT]"
hints:
  - "Create a directory and set the sticky bit on it."
  - "Use mkdir then chmod 1777, then ls -ld to verify."
  - "Type: `mkdir shared_tmp && chmod 1777 shared_tmp && ls -ld shared_tmp`"
-->
### Exercise 4: Create a sticky directory
Create a directory called `shared_tmp` with sticky bit set (`1777`) and verify with `ls -ld`.

---

## `ls` Field Refresher

```
-rw-r--r-- 1 alice dev 1234 Aug 30 12:00 notes.txt
```

| Field | Meaning |
|-------|---------|
| `-rw-r--r--` | mode (type + permissions) |
| `1` | hard link count |
| `alice` | owner (user) |
| `dev` | group |
| `1234` | size in bytes |
| `Aug 30 12:00` | modification time |
| `notes.txt` | filename |

<!-- exercise
id: ex05
title: Create a private directory
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: rwx------
hints:
  - "Use mkdir with specific permissions so only the owner has access."
  - "The -m flag lets you set permissions at creation time, or use chmod after."
  - "Type: `mkdir -m 700 secrets && ls -ld secrets`"
-->
### Exercise 5: Create a private directory
Create a directory called `secrets` with permissions `700` (only owner has access). Verify with `ls -ld`.

---

## Symbolic chmod in Practice

Symbolic notation is handy for making small changes without remembering the
full octal number:

```bash
chmod u+x file     # owner can now execute
chmod g+rw file    # group can now read and write
chmod o-rwx file   # others lose all access
chmod a+r file     # everyone can read
```

<!-- exercise
id: ex06
title: Remove all group and other permissions
xp: 15
difficulty: 2
sandbox_setup:
  - "echo 'private data' > private.txt"
  - "chmod 664 private.txt"
validation_type: output_contains
expected: rw-------
hints:
  - "Use symbolic chmod to remove permissions from group and other."
  - "Remove read and write from group (g-rw) and other (o-r)."
  - "Type: `chmod go-rw private.txt && ls -l private.txt`"
-->
### Exercise 6: Remove all group and other permissions
Using symbolic notation, remove all group and other permissions from `private.txt`. Verify with `ls -l`.

---

## Common Permission Patterns

| Use Case | Octal | Symbolic |
|----------|-------|----------|
| Private SSH key | 600 | `-rw-------` |
| Config file | 640 | `-rw-r-----` |
| Executable script | 755 | `-rwxr-xr-x` |
| Home directory | 700 | `drwx------` |
| Web root | 755 | `drwxr-xr-x` |
| Team shared dir | 2775 | `drwxrwsr-x` |
| Temp scratch dir | 1777 | `drwxrwxrwt` |

<!-- exercise
id: ex07
title: Permission practice pipeline
xp: 20
difficulty: 2
sandbox_setup: null
validation_type: file_exists
expected: project/readme.txt
hints:
  - "Create the directory with 755, then create a file inside it."
  - "Use mkdir for the directory, chmod for permissions, and touch for the file."
  - "Type: `mkdir -m 755 project && touch project/readme.txt && chmod 644 project/readme.txt`"
-->
### Exercise 7: Permission practice pipeline
Create a directory called `project` with permissions `755`, then create a file `readme.txt` inside it with permissions `644`.

---

## What You Learned

- **Permission triplets** -- rwx for owner, group, and other
- **Octal notation** -- 644, 755, 600, 700 and what they mean
- **`chmod`** -- change permissions (octal and symbolic)
- **`chown`** / **`chgrp`** -- change file ownership
- **Special bits** -- setuid, setgid, and sticky
- **Reading `ls -l`** -- parsing the mode string and metadata fields
