# Customizing Your Prompt

The text you see to the left of your cursor in the terminal is the **prompt**.
It typically looks something like:

```
operator@shipnet:~/missions$
```

The `$` denotes a regular user. A `#` usually indicates you are **root** (the
most privileged user on the system). The prompt is fully customizable through
the `PS1` variable.

## The PS1 Variable

`PS1` (Prompt String 1) controls what your primary prompt displays. You can see
its current value:

```bash
echo $PS1
```

The default often contains escape sequences that the shell replaces with dynamic
values like your username, hostname, and current directory.

<!-- exercise
id: ex01
title: Display a shell variable
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: /bin/bash
hints:
  - "SHELL is a variable that holds the path to your shell."
  - "Use echo with the variable name preceded by a dollar sign."
  - "Type: `echo $SHELL`"
-->
### Exercise 1: Display a shell variable
Print the value of the `SHELL` variable to see which shell you are using.

---

## PS1 Escape Sequences

Here are the most commonly used escape sequences:

| Sequence | Meaning |
|----------|---------|
| `\u` | Current username |
| `\h` | Hostname (short) |
| `\H` | Hostname (full FQDN) |
| `\w` | Current working directory (full path, `~` for home) |
| `\W` | Current working directory (basename only) |
| `\d` | Date (e.g., "Mon Aug 30") |
| `\t` | Time in 24-hour HH:MM:SS |
| `\T` | Time in 12-hour HH:MM:SS |
| `\n` | Newline |
| `\$` | `$` for regular user, `#` for root |
| `\!` | History number of this command |
| `\#` | Command number in this session |

### Examples

```bash
# Simple: user@host:path$
PS1='\u@\h:\w\$ '

# With date and time (useful for logging watch activity)
PS1='[\d \t] \u@\h:\w\$ '

# Minimal
PS1='\W\$ '

# Multi-line
PS1='\u@\h:\w\n\$ '
```

<!-- exercise
id: ex02
title: Set a custom prompt
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: "PS1"
hints:
  - "Assign a new value to the PS1 variable using escape sequences."
  - "Use the export command or direct assignment."
  - "Type: `PS1='\\u@\\h:\\w\\$ ' && echo \"PS1=$PS1\"`"
-->
### Exercise 2: Set a custom prompt
Set your prompt to show `username@hostname:path$ ` format and echo the PS1 value to verify.

---

## Adding Color

You can add ANSI color codes to make parts of your prompt stand out:

```bash
# Color codes
# \[\e[COLORm\] ... \[\e[0m\]
# The \[ and \] tell bash not to count these characters for line wrapping

# Common colors:
# 30=black 31=red 32=green 33=yellow 34=blue 35=magenta 36=cyan 37=white
# Bold: add 1; prefix (e.g., 1;32 = bold green)

# Green user, blue path
PS1='\[\e[1;32m\]\u@\h\[\e[0m\]:\[\e[1;34m\]\w\[\e[0m\]\$ '
```

> **Important:** Always wrap color codes in `\[` and `\]`. Without these
> markers, bash miscounts the prompt length and line wrapping breaks.

<!-- exercise
id: ex03
title: Colorful prompt
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: "32m"
hints:
  - "Set PS1 with ANSI color escape codes."
  - "Use \\[\\e[1;32m\\] for green text and \\[\\e[0m\\] to reset."
  - "Type: `PS1='\\[\\e[1;32m\\]\\u\\[\\e[0m\\]:\\w\\$ ' && echo $PS1`"
-->
### Exercise 3: Colorful prompt
Set your prompt so your username displays in green. Print the PS1 value to verify it contains the color code.

---

## PS2, PS3, PS4 -- The Other Prompts

Bash has four prompt variables:

| Variable | When It Appears |
|----------|----------------|
| `PS1` | Primary prompt (the main one) |
| `PS2` | Continuation prompt (when a command spans multiple lines, default `> `) |
| `PS3` | Prompt for `select` statements in scripts |
| `PS4` | Debug prompt (shown when running with `set -x`, default `+ `) |

```bash
# Change the continuation prompt
PS2='... '

# Now when you type an incomplete command:
# $ echo "hello
# ... world"
```

<!-- exercise
id: ex04
title: Check the continuation prompt
xp: 10
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: ">"
hints:
  - "PS2 is the continuation prompt variable. In a non-interactive shell it may be empty."
  - "Set it first, then display it."
  - "Type: `PS2='> ' && echo $PS2`"
-->
### Exercise 4: Set and check the continuation prompt
Set PS2 to `> ` and then display it.

---

## Making It Permanent

Changes to PS1 on the command line are temporary. To make your prompt
permanent, add the `PS1=` line to your shell startup file:

```bash
# Add to ~/.bashrc
echo 'PS1="\u@\h:\w\$ "' >> ~/.bashrc

# Reload without restarting the terminal
source ~/.bashrc
```

Many users keep elaborate prompt configurations in their dotfiles. Some
popular prompt frameworks include **Starship**, **Oh My Bash**, and
**Powerlevel10k** (for zsh).

<!-- exercise
id: ex05
title: Write a prompt to a file
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: file_contains
expected: my_bashrc::PS1=
hints:
  - "Use echo with redirection to write a PS1 line into a file."
  - "The > operator writes output to a file."
  - "Type: `echo 'PS1=\"\\u@\\h:\\w\\$ \"' > my_bashrc`"
-->
### Exercise 5: Write a prompt to a file
Write a PS1 configuration line to a file called `my_bashrc` (simulating adding it to your bashrc).

---

## What You Learned

- **PS1** -- the primary prompt variable and its escape sequences
- **`\u`**, **`\h`**, **`\w`**, **`\$`** -- dynamic prompt tokens
- **ANSI color codes** -- adding color with `\[\e[COLORm\]`
- **PS2/PS3/PS4** -- the other prompt variables
- **Persistence** -- saving prompt changes in `~/.bashrc`
