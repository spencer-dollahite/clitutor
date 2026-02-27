# Start Here: CLI Basics

Welcome to **CLItutor**! You are on the cusp of an exciting journey.

## Why Learn the CLI?

Both Windows and Linux/UNIX systems can be managed at scale via automation by
using text-only commands rather than clicking around icons in a GUI (Graphical
User Interface). Knowing your way around the CLI will let you operate expertly
and efficiently on systems for both defensive and offensive operations.

We will focus on non-Windows CLI. Over 90% of workloads on the internet and
in "the cloud" run on Linux/Unix systems, so this skillset is widely applicable
when administering infrastructure.

## Where Am I? -- `pwd`

The very first thing you need to know is **where you are** in the filesystem.
The command `pwd` stands for **P**rint **W**orking **D**irectory. Think of a
directory as the same thing as a folder.

<!-- exercise
id: ex01
title: Print your current directory
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_regex
expected: "^/"
hints:
  - "Think about what command shows WHERE you are."
  - "The command is three letters: Print Working Directory."
  - "Type exactly: `pwd`"
-->
### Exercise 1: Print your current directory
Run the command that shows your current working directory.

---

## What Is Here? -- `ls`

Now that you know where you are, you want to see what is inside the current
directory. The `ls` command **l**ists **s**torage -- the files and folders in
your current location.

<!-- exercise
id: ex02
title: List directory contents
xp: 10
difficulty: 1
sandbox_setup:
  - "touch sitrep.txt roster.txt comms.log"
  - "mkdir operations"
validation_type: output_contains
expected: sitrep.txt
hints:
  - "You need to list the files in the current directory."
  - "The command is two letters: list storage."
  - "Type exactly: `ls`"
-->
### Exercise 2: List directory contents
List the files and folders in the current directory.

---

## Moving Around -- `cd`

You can **c**hange **d**irectory with the `cd` command. Here are some important
path concepts:

| Symbol | Meaning |
|--------|---------|
| `/`    | The root (top) of the filesystem |
| `.`    | The current directory |
| `..`   | The parent directory (one level up) |
| `~`    | Your home directory |

**Absolute paths** start from the root: `/home/student/missions`

**Relative paths** start from where you are: `./missions` or just `missions`

<!-- exercise
id: ex03
title: Change to a subdirectory
xp: 15
difficulty: 1
sandbox_setup:
  - "mkdir -p missions/operation-typhoon"
validation_type: cwd_regex
expected: "^/home/student/.+"
hints:
  - "You need to change into a subdirectory. Use ls to see what's available."
  - "Use cd followed by the directory name."
  - "Type: `cd missions`"
-->
### Exercise 3: Change to a subdirectory
You're currently in your home directory (`/home/student`). Use `ls` to see the
available subdirectories, then `cd` into one of them.

---

## Going Back -- `cd`, `cd -`, `cd ..`

You can return to the previous directory with `cd -` (toggles between your last
two locations). You can go up one level with `cd ..`, or up two levels with
`cd ../..`, and so on.

**`cd` by itself (or `cd ~`) takes you straight to your home directory.** This
is one of the most useful things to remember -- no matter how deep into the
filesystem you've wandered, `cd` with no arguments brings you back home.

<!-- exercise
id: ex04
title: Return to your home directory
xp: 10
difficulty: 1
sandbox_setup:
  - "mkdir -p a/b/c"
validation_type: cwd_regex
expected: "^/home/student$"
hints:
  - "You need to get back to your home directory. What command takes you there with no arguments?"
  - "Type cd by itself (no arguments) to return to your home directory."
  - "Type exactly: `cd`"
-->
### Exercise 4: Return to your home directory
You should still be inside a subdirectory from the previous exercise. Use `cd`
with no arguments to return to your home directory (`/home/student`). You can
verify with `pwd` afterward.

---

## Seeing Hidden Files -- `ls -a`

Anything that starts with a `.` (dot) is hidden by default. The `-a` flag shows
**a**ll files, including hidden ones. You will encounter hidden files frequently
-- they are used for configuration (like `.bashrc`, `.profile`, `.ssh/`).

<!-- exercise
id: ex05
title: Show hidden files
xp: 10
difficulty: 1
sandbox_setup:
  - "touch .classified_config visible_file"
validation_type: output_regex
expected: (^|\s)\.\.(\s|$)
hints:
  - "You need a flag that shows ALL files including hidden ones."
  - "Hidden files start with a dot. The flag to show them also starts with 'a'."
  - "Type exactly: `ls -a`"
-->
### Exercise 5: Show hidden files
You should be in your home directory (`/home/student`). If you're not, run `cd`
to return there first.

List all files in the current directory, including hidden ones.

---

## Detailed Listings -- `ls -l`

The `-l` flag gives you a **l**ong listing with metadata: permissions, owner,
group, size, modification time, and filename.

```
-rw-r--r-- 1 student ops 1234 Aug 30 12:00 watchbill.txt
```

You can combine flags: `ls -la` shows a long listing of all files including
hidden ones.

<!-- exercise
id: ex06
title: Long listing
xp: 10
difficulty: 1
sandbox_setup:
  - "echo 'SITREP: All quiet on station' > watchbill.txt"
  - "mkdir intel"
validation_type: output_regex
expected: total \d+
hints:
  - "Use the long-format flag with ls."
  - "The flag for a long listing is -l."
  - "Type exactly: `ls -l`"
-->
### Exercise 6: Long listing
You should still be in your home directory. Display a detailed (long) listing of
the current directory.

---

## Creating Files and Directories

| Command | Purpose |
|---------|---------|
| `touch <file>` | Create an empty file (or update its timestamp) |
| `mkdir <dir>` | Create a new directory |
| `mkdir -p a/b/c` | Create nested directories (parents included) |
| `cp <src> <dst>` | Copy a file |
| `mv <src> <dst>` | Move or rename a file |
| `rm <file>` | Remove a file |
| `rm -r <dir>` | Remove a directory and its contents recursively |

> **Note:** Some commands succeed silently -- no output means it worked.
> Errors and warnings will be printed if something goes wrong.

<!-- exercise
id: ex07
title: Create a mission briefs directory with a file inside
xp: 15
difficulty: 1
sandbox_setup: null
validation_type: file_exists
expected: "briefs/oporder.txt"
hints:
  - "You need to create a directory first, then create a file inside it."
  - "Use mkdir for the directory and touch for the file."
  - "Type: `mkdir briefs && touch briefs/oporder.txt`"
-->
### Exercise 7: Create a mission briefs directory with a file inside
Make sure you are in your home directory (`cd` to return if needed).

Create a directory called `briefs`, then create an empty file called `oporder.txt`
**inside** it using `touch`:

```
mkdir briefs && touch briefs/oporder.txt
```

---

## Reading Files -- `cat`, `less`

| Command | Purpose |
|---------|---------|
| `cat <file>` | Print the entire file to the screen |
| `less <file>` | Page through a file interactively (press `q` to quit) |
| `head <file>` | Show the first 10 lines |
| `tail <file>` | Show the last 10 lines |

**Redirection** lets you send output to a file:
- `>` overwrites the file
- `>>` appends to the file

```bash
echo 'SITREP: All quiet' > sitrep.txt     # creates/overwrites sitrep.txt
echo 'No contacts reported' >> sitrep.txt  # appends to sitrep.txt
cat sitrep.txt                              # shows both lines
```

<!-- exercise
id: ex08
title: Write and read a file
xp: 20
difficulty: 1
sandbox_setup: null
validation_type: any_file_contains
expected: Today I learned the CLI
hints:
  - "Use echo with redirection to write text into a file."
  - "The > operator sends output to a file. Put your text in quotes."
  - "Example: `echo 'Today I learned the CLI' > journal.txt`"
-->
### Exercise 8: Write and read a file
You should still be in your home directory.

Use `echo` and redirection to create a file containing the text `Today I learned the CLI`.
You can name the file anything you like (for example, `journal.txt`).

---

## What You Learned

In this lesson you covered the absolute fundamentals:

- **`pwd`** -- print your current location
- **`ls`** / `ls -a` / `ls -l` -- list files with various detail levels
- **`cd`** -- navigate between directories
- **`touch`**, **`mkdir`**, **`cp`**, **`mv`**, **`rm`** -- create and manage files
- **`cat`**, **`less`** -- read file contents
- **`>`** and **`>>`** -- redirect output to files

These commands are the foundation of everything else you will learn. Practice
moving around your filesystem until these feel second nature.
