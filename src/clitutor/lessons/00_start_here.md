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
  - "touch file1.txt file2.txt file3.txt"
  - "mkdir subdir"
validation_type: output_contains
expected: file1.txt
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

**Absolute paths** start from the root: `/home/user/documents`

**Relative paths** start from where you are: `./documents` or just `documents`

<!-- exercise
id: ex03
title: Change to a subdirectory
xp: 15
difficulty: 1
sandbox_setup:
  - "mkdir -p projects/webapp"
validation_type: cwd_regex
expected: "/(subdir|projects|webapp|docs|a)(/|$)"
hints:
  - "You need to change into a subdirectory. Use ls to see what's available."
  - "Use cd followed by the directory name."
  - "Type: `cd projects`"
-->
### Exercise 3: Change to a subdirectory
Change into any subdirectory (use `ls` to see what's available).

---

## Going Back -- `cd -` and `cd ..`

You can return to the previous directory with `cd -` (toggles between your last
two locations). You can go up one level with `cd ..`, or up two levels with
`cd ../..`, and so on.

`cd` by itself (or `cd ~`) takes you straight to your home directory.

<!-- exercise
id: ex04
title: Confirm your location
xp: 10
difficulty: 1
sandbox_setup:
  - "mkdir -p a/b/c"
validation_type: output_regex
expected: "^/"
hints:
  - "You need to confirm your current directory."
  - "The command to print your working directory is three letters."
  - "Type exactly: `pwd`"
-->
### Exercise 4: Confirm your location
Print your current working directory to confirm where you are.

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
  - "touch .hidden_file visible_file"
validation_type: output_regex
expected: (^|\s)\.\.(\s|$)
hints:
  - "You need a flag that shows ALL files including hidden ones."
  - "Hidden files start with a dot. The flag to show them also starts with 'a'."
  - "Type exactly: `ls -a`"
-->
### Exercise 5: Show hidden files
List all files in the current directory, including hidden ones.

---

## Detailed Listings -- `ls -l`

The `-l` flag gives you a **l**ong listing with metadata: permissions, owner,
group, size, modification time, and filename.

```
-rw-r--r-- 1 alice dev 1234 Aug 30 12:00 notes.txt
```

You can combine flags: `ls -la` shows a long listing of all files including
hidden ones.

<!-- exercise
id: ex06
title: Long listing
xp: 10
difficulty: 1
sandbox_setup:
  - "echo 'hello world' > greeting.txt"
  - "mkdir docs"
validation_type: output_regex
expected: total \d+
hints:
  - "Use the long-format flag with ls."
  - "The flag for a long listing is -l."
  - "Type exactly: `ls -l`"
-->
### Exercise 6: Long listing
Display a detailed (long) listing of the current directory.

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
title: Create a directory with a file inside it
xp: 15
difficulty: 1
sandbox_setup: null
validation_type: dir_with_file
expected: ""
hints:
  - "You need to create a directory first, then create a file inside it."
  - "Use mkdir for the directory and touch for the file."
  - "Example: `mkdir mydir && touch mydir/myfile.txt`"
-->
### Exercise 7: Create a directory with a file inside it
First, create a new directory using `mkdir`. Then, create an empty file **inside
that new directory** using `touch`. You can pick any names you like
(for example, `mkdir mydir && touch mydir/myfile.txt`).

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
echo 'hello' > greet.txt     # creates/overwrites greet.txt
echo 'world' >> greet.txt    # appends to greet.txt
cat greet.txt                 # shows both lines
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
