# The PATH Variable

When you type a command like `ls` or `python`, how does the shell know where
that program lives on disk? The answer is the **PATH** environment variable.
Understanding PATH is essential for troubleshooting "command not found" errors
and for managing your environment.

## What Is PATH?

PATH is an environment variable containing a colon-separated list of
directories. When you type a command, the shell searches these directories **in
order** for an executable with that name.

```bash
echo $PATH
```

You will see something like:

```
/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
```

The shell checks `/usr/local/bin` first, then `/usr/bin`, then `/bin`, and so
on. The first match wins.

<!-- exercise
id: ex01
title: Display your PATH
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: /usr
hints:
  - "PATH is an environment variable. How do you display a variable's value?"
  - "Use echo with a dollar sign before the variable name."
  - "Type: `echo $PATH`"
-->
### Exercise 1: Display your PATH
Print the current value of your PATH variable.

---

## `which` and `type` -- Finding Commands

When you want to know exactly which executable will run:

```bash
which ls              # shows the full path to the ls binary
which python          # which python will run?
type ls               # more detailed: shows if it is an alias, builtin, or file
type cd               # reveals cd is a shell builtin
command -v git        # another way to check if a command exists
```

<!-- exercise
id: ex02
title: Locate the ls command
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: /bin/ls
hints:
  - "Use a command that shows the full path to an executable."
  - "The command 'which' shows where a program is located."
  - "Type: `which ls`"
-->
### Exercise 2: Locate the ls command
Find the full filesystem path of the `ls` command.

---

## How PATH Gets Set

PATH is typically configured in your shell startup files:

- `/etc/environment` -- system-wide (Debian/Ubuntu)
- `/etc/profile` -- system-wide for login shells
- `~/.bashrc` -- user-specific for interactive shells
- `~/.profile` or `~/.bash_profile` -- user-specific for login shells

When you open a terminal, these files are sourced in a specific order, building
up your PATH.

<!-- exercise
id: ex03
title: Count directories in PATH
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_regex
expected: "^\\s*\\d+\\s*$"
hints:
  - "Replace colons with newlines, then count the lines."
  - "Use echo $PATH piped through tr to replace colons, then wc -l."
  - "Type: `echo $PATH | tr ':' '\\n' | wc -l`"
-->
### Exercise 3: Count directories in PATH
Count how many directories are in your current PATH (hint: replace `:` with newlines and count).

---

## Modifying PATH

You can temporarily add directories to PATH:

```bash
# Prepend (your directory is checked FIRST)
export PATH="/my/custom/bin:$PATH"

# Append (your directory is checked LAST)
export PATH="$PATH:/my/custom/bin"
```

This change lasts only for the current shell session. To make it permanent, add
the `export` line to your `~/.bashrc` or `~/.profile`.

> **Warning:** Never set PATH to just your directory without including the
> existing PATH. Writing `export PATH="/my/bin"` would make almost all commands
> unavailable.

<!-- exercise
id: ex04
title: Add a directory to PATH
xp: 15
difficulty: 2
sandbox_setup:
  - "mkdir -p navbin"
  - "printf '#!/bin/bash\\necho \"firewall status: nominal\"\\n' > navbin/chk_firewall"
  - "chmod +x navbin/chk_firewall"
validation_type: output_contains
expected: "firewall status: nominal"
hints:
  - "Export PATH with your new directory prepended, then run the command."
  - "Use export PATH=\"$PWD/navbin:$PATH\" to add the directory."
  - "Type: `export PATH=\"$PWD/navbin:$PATH\" && chk_firewall`"
-->
### Exercise 4: Add a directory to PATH
Add the `navbin` directory to your PATH and run the `chk_firewall` command that lives inside it.

---

## Troubleshooting "Command Not Found"

When you see `command not found`, it means the shell searched every directory in
PATH and found no matching executable. Common fixes:

1. **Check the spelling** -- typos are the most common cause
2. **Check if it is installed** -- `dpkg -l | grep <package>` or `apt list --installed | grep <package>`
3. **Find it manually** -- `find / -name "command" -type f 2>/dev/null`
4. **Check PATH** -- is the directory containing the program in your PATH?
5. **Use the full path** -- `/usr/local/bin/mycommand` works even if PATH is wrong

<!-- exercise
id: ex05
title: Use the full path
xp: 10
difficulty: 2
sandbox_setup: null
validation_type: output_regex
expected: "^/"
hints:
  - "Instead of just typing a command name, use its absolute path."
  - "Use which to find the path, then use that full path."
  - "Type: `/bin/pwd`"
-->
### Exercise 5: Use the full path
Run `pwd` by specifying its full absolute path (e.g., `/bin/pwd`).

---

## The Current Directory and PATH

By default, the current directory (`.`) is **not** in PATH on Linux. This is a
security measure. To run a script in the current directory, you must use:

```bash
./myscript.sh
```

The `./` prefix tells the shell "look in the current directory" rather than
searching PATH.

<!-- exercise
id: ex06
title: Run a local script
xp: 15
difficulty: 2
sandbox_setup:
  - "printf '#!/bin/bash\\necho \"port scan initiated\"\\n' > scan_ports.sh"
  - "chmod +x scan_ports.sh"
validation_type: output_contains
expected: port scan initiated
hints:
  - "Scripts in the current directory need a special prefix to run."
  - "Use ./ before the script name to run it from the current directory."
  - "Type: `./scan_ports.sh`"
-->
### Exercise 6: Run a local script
Execute the `scan_ports.sh` script in the current directory.

---

## What You Learned

- **PATH** -- a colon-separated list of directories the shell searches for commands
- **`echo $PATH`** -- display the current PATH
- **`which`** / **`type`** -- find where a command lives
- **`export PATH=...`** -- temporarily modify PATH
- **Shell startup files** -- where PATH is configured permanently
- **`./`** -- required prefix to run scripts in the current directory
- **Troubleshooting** -- steps to fix "command not found" errors
