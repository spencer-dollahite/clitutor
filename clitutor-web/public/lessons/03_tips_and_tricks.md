# Tips and Tricks

This lesson covers productivity boosters -- keyboard shortcuts, command history,
job control, and other tricks that will make you dramatically faster on the
command line. These are the habits that separate beginners from power users.

## Command History

Every command you type is saved in your shell history (usually in
`~/.bash_history`). You can browse and re-use previous commands:

```bash
history              # show your command history (numbered)
history | grep ssh   # search history for a term
!!                   # repeat the last command
sudo !!              # re-run the last command with sudo (very handy!)
!<string>            # run the most recent command starting with <string>
!42                  # run command number 42 from history
!$                   # the last argument of the previous command
```

**`Ctrl+R`** starts a **reverse incremental search** through your history. Just
start typing and it will find the most recent match. Press `Ctrl+R` again to
cycle through older matches. Press `Enter` to execute, or `Ctrl+C` to cancel.
This is, in many experienced users' opinions, the best way to recall commands.

<!-- exercise
id: ex01
title: Use the type command
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: builtin
hints:
  - "The 'type' command tells you what kind of command something is."
  - "Try using type on a well-known shell builtin."
  - "Type: `type cd`"
-->
### Exercise 1: Identify a builtin command
Use the `type` command to check what kind of command `cd` is.

---

## Keyboard Shortcuts

These shortcuts work in bash (and most shells using readline/emacs mode):

### Navigation
| Shortcut | Action |
|----------|--------|
| `Ctrl+A` | Jump to beginning of line |
| `Ctrl+E` | Jump to end of line |
| `Ctrl+B` | Move back one character |
| `Ctrl+F` | Move forward one character |
| `Alt+B`  | Move back one word |
| `Alt+F`  | Move forward one word |

### Editing
| Shortcut | Action |
|----------|--------|
| `Ctrl+W` | Delete the word before the cursor |
| `Ctrl+U` | Delete everything before the cursor |
| `Ctrl+K` | Delete everything after the cursor |
| `Ctrl+Y` | Paste (yank) the last killed text |

### Other
| Shortcut | Action |
|----------|--------|
| `Ctrl+C` | Cancel the current command / kill running process |
| `Ctrl+L` | Clear the screen (same as `clear`) |
| `Ctrl+D` | End of input / logout |

<!-- exercise
id: ex02
title: Use echo with special characters
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: efficient keystrokes save time on watch
hints:
  - "Use echo to print a message to the screen."
  - "Put the text in quotes after echo."
  - "Type: `echo 'efficient keystrokes save time on watch'`"
-->
### Exercise 2: Practice on the command line
Use `echo` to print the message: `efficient keystrokes save time on watch`

---

## Tab Completion

After typing a few letters, press **Tab**:
- If the match is unique, the shell auto-completes the word
- If multiple matches exist, press **Tab twice** to list all possibilities

Tab completion works for:
- Filenames and directories
- Commands
- Variables (after `$`)
- Hostnames (after `@` in some setups)

This is a **massive** quality-of-life feature. If it does not work on your
system, research how to install `bash-completion` for your distribution.

<!-- exercise
id: ex03
title: Create nested structure
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: file_exists
expected: operations/reports/daily_sitrep.txt
hints:
  - "Use mkdir -p to create the full directory path in one command."
  - "Then touch to create the file inside the nested directory."
  - "Type: `mkdir -p operations/reports && touch operations/reports/daily_sitrep.txt`"
-->
### Exercise 3: Create a nested structure
Create the directory path `operations/reports/` and a file `daily_sitrep.txt` inside it. (Hint: `mkdir -p` creates parent directories as needed.)

---

## Job Control

You can manage running processes directly from the shell:

```bash
sleep 300 &         # start a command in the background
jobs                 # list background jobs
fg %1               # bring job 1 to the foreground
Ctrl+Z              # suspend the foreground process
bg                   # resume a suspended job in the background
```

This is useful when you have a long-running process and need your shell back.

<!-- exercise
id: ex04
title: Echo a process list
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_regex
expected: "PID|pid|sleep"
hints:
  - "Use a command that shows running processes."
  - "The ps command shows running processes. Or try echo with $BASHPID."
  - "Type: `echo \"My PID is $$\"`"
-->
### Exercise 4: Show process information
Use `echo` with a shell variable to display your current process ID (PID). The variable `$$` holds the current shell's PID.

---

## Aliases

Aliases let you create shortcuts for commands you use frequently:

```bash
alias ll='ls -la'
alias gs='git status'
alias ..='cd ..'
alias ...='cd ../..'
```

Aliases defined on the command line last only for the current session. To make
them permanent, add them to your `~/.bashrc` or `~/.bash_aliases` file.

<!-- exercise
id: ex05
title: Create an alias
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: ls -la
hints:
  - "Define an alias using the alias command, then verify it exists."
  - "The format is: alias name='command'. Then run alias to list all."
  - "Type: `alias ll='ls -la' && alias`"
-->
### Exercise 5: Create an alias
Create an alias called `ll` that runs `ls -la`, then display all defined aliases.

---

## Brace Expansion and Wildcards

**Brace expansion** generates strings:

```bash
echo {a,b,c}           # a b c
mkdir patrol_{01..05}   # patrol_01 patrol_02 patrol_03 patrol_04 patrol_05
touch log_{a,b,c}.txt   # log_a.txt log_b.txt log_c.txt
```

**Wildcards** (globbing) match filenames:

| Pattern | Matches |
|---------|---------|
| `*`     | Any string (including empty) |
| `?`     | Exactly one character |
| `[abc]` | One of a, b, or c |
| `[0-9]` | One digit |

```bash
ls *.txt              # all .txt files
ls file?.log          # file1.log, fileA.log, etc.
rm temp_[0-9]*        # remove files starting with temp_ followed by a digit
```

<!-- exercise
id: ex06
title: Brace expansion
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: file_exists
expected: patrol_03
hints:
  - "Use brace expansion with mkdir to create multiple directories at once."
  - "The syntax {01..05} generates a sequence."
  - "Type: `mkdir patrol_{01..05}`"
-->
### Exercise 6: Brace expansion
Create five directories named `patrol_01` through `patrol_05` using a single command with brace expansion.

---

## Useful Command Combinations

```bash
# Run two commands in sequence (second runs only if first succeeds)
mkdir newdir && cd newdir

# Run two commands in sequence (second runs regardless)
command1 ; command2

# Repeat the last argument
cat /var/log/auth.log
vim !$    # opens the same file in vim

# Quick command substitution
echo "Today is $(date)"
echo "I am in $(pwd)"
```

<!-- exercise
id: ex07
title: Command substitution
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: "files:"
hints:
  - "Use command substitution $() to embed one command's output in another."
  - "The syntax is $(command) inside a string."
  - "Type: `echo \"files: $(ls)\"` (there may be no files listed and that is OK)"
-->
### Exercise 7: Command substitution
Use `echo` and command substitution to print `files:` followed by the output of `ls`.

---

## What You Learned

- **`history`** and **`Ctrl+R`** -- recall and search previous commands
- **Keyboard shortcuts** -- `Ctrl+A/E/W/U/K/Y/L/C` for fast editing
- **Tab completion** -- auto-complete filenames and commands
- **Job control** -- background jobs, `fg`, `bg`, `Ctrl+Z`
- **Aliases** -- create shortcuts for frequent commands
- **Brace expansion** and **wildcards** -- generate and match filenames efficiently
- **`&&`** vs **`;`** -- chaining commands conditionally or unconditionally
- **`$()`** -- command substitution
