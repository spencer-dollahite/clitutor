# Dotfiles

**Dotfiles** are hidden configuration files that customize your shell, editor,
tools, and environment. They are called "dotfiles" because their names begin
with a `.` (dot), which makes them hidden from normal directory listings.

## Common Dotfiles

| File | Purpose |
|------|---------|
| `~/.bashrc` | Bash config for interactive non-login shells |
| `~/.bash_profile` | Bash config for login shells |
| `~/.profile` | Generic login shell config |
| `~/.bash_aliases` | Custom alias definitions (sourced by .bashrc) |
| `~/.bash_history` | Command history |
| `~/.vimrc` | Vim editor configuration |
| `~/.tmux.conf` | tmux configuration |
| `~/.gitconfig` | Git global configuration |
| `~/.ssh/config` | SSH connection shortcuts |
| `~/.inputrc` | Readline (input) configuration |

<!-- exercise
id: ex01
title: Find dotfiles in home
xp: 10
difficulty: 1
sandbox_setup:
  - "touch .bashrc .profile .vimrc .hidden_config"
validation_type: output_contains
expected: .bashrc
hints:
  - "Use ls with the -a flag to show hidden files."
  - "Hidden files start with a dot and are shown by ls -a."
  - "Type: `ls -a`"
-->
### Exercise 1: Find dotfiles
List all files including hidden dotfiles in the current directory.

---

## `.bashrc` vs `.bash_profile`

Understanding when each file runs is important:

- **Login shell** (SSH, console login, `su -`): reads `~/.bash_profile` (or
  `~/.profile`)
- **Interactive non-login shell** (opening a new terminal tab): reads
  `~/.bashrc`

A common pattern is to have `.bash_profile` source `.bashrc`, so your settings
are consistent:

```bash
# ~/.bash_profile
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi
```

### What Goes Where

In `.bashrc` (interactive settings):
- Aliases
- Prompt (PS1)
- Shell options (`shopt`)
- Functions

In `.bash_profile` (login settings):
- PATH modifications
- Environment variables (`export`)
- Login-specific setup

<!-- exercise
id: ex02
title: Create a bashrc file
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: file_contains
expected: my_bashrc::alias ll=
hints:
  - "Write typical bashrc content including an alias."
  - "Use printf or echo with redirection."
  - "Type: `printf '# My custom bashrc\\nalias ll=\"ls -la\"\\nalias gs=\"git status\"\\nexport EDITOR=vim\\n' > my_bashrc`"
-->
### Exercise 2: Create a bashrc file
Create a file called `my_bashrc` with at least one alias definition (e.g., `alias ll="ls -la"`).

---

## Sourcing Files

The `source` command (or its shorthand `.`) executes a file in the current
shell, applying any changes immediately:

```bash
source ~/.bashrc       # reload bashrc
. ~/.bashrc            # same thing, shorter syntax
```

This is how changes to dotfiles take effect without opening a new terminal.

<!-- exercise
id: ex03
title: Create and source a config
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: myconfig loaded
hints:
  - "Create a file that echoes a message, then source it."
  - "Use echo to create the file, then source to execute it."
  - "Type: `echo 'echo \"myconfig loaded\"' > myconfig.sh && . ./myconfig.sh`"
-->
### Exercise 3: Create and source a config
Create a file `myconfig.sh` that prints `myconfig loaded`, then source it to run it in the current shell.

---

## Environment Variables

Dotfiles commonly set environment variables that control tool behavior:

```bash
export EDITOR=vim            # default text editor
export VISUAL=vim            # visual editor
export PAGER=less            # default pager
export LANG=en_US.UTF-8      # locale
export HISTSIZE=10000         # history size
export HISTCONTROL=ignoredups # skip duplicate commands in history
```

Use `env` or `printenv` to see all current environment variables.

<!-- exercise
id: ex04
title: Set and display a variable
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: MY_VAR=hello
hints:
  - "Export a variable and then display it."
  - "Use export to set the variable, then env or echo to show it."
  - "Type: `export MY_VAR=hello && echo MY_VAR=$MY_VAR`"
-->
### Exercise 4: Set and display a variable
Set an environment variable `MY_VAR` to `hello` and print it in the format `MY_VAR=hello`.

---

## Managing Dotfiles with Git

Many developers track their dotfiles in a git repository for backup and
portability. Common approaches:

### Simple Symlink Method

```bash
mkdir ~/dotfiles
mv ~/.bashrc ~/dotfiles/bashrc
ln -s ~/dotfiles/bashrc ~/.bashrc
cd ~/dotfiles && git init && git add -A && git commit -m "initial dotfiles"
```

### Bare Repository Method

```bash
git init --bare ~/.dotfiles
alias dotgit='git --git-dir=$HOME/.dotfiles --work-tree=$HOME'
dotgit add ~/.bashrc
dotgit commit -m "add bashrc"
```

<!-- exercise
id: ex05
title: Create a symlink
xp: 15
difficulty: 2
sandbox_setup:
  - "mkdir -p dotfiles_repo"
  - "echo 'alias ll=\"ls -la\"' > dotfiles_repo/bashrc"
validation_type: output_contains
expected: dotfiles_repo/bashrc
hints:
  - "Use ln -s to create a symbolic link from one file to another."
  - "The syntax is ln -s target linkname."
  - "Type: `ln -s dotfiles_repo/bashrc link_bashrc && ls -l link_bashrc`"
-->
### Exercise 5: Create a symlink
Create a symbolic link called `link_bashrc` pointing to `dotfiles_repo/bashrc`. Verify with `ls -l`.

---

## `.inputrc` -- Readline Configuration

The `~/.inputrc` file configures readline, which controls command-line editing
behavior:

```bash
# ~/.inputrc
# Case-insensitive tab completion
set completion-ignore-case on

# Show all completions on first tab
set show-all-if-ambiguous on

# Vi mode (instead of default emacs mode)
# set editing-mode vi

# Color the common prefix in completions
set colored-completion-prefix on
```

<!-- exercise
id: ex06
title: Create an inputrc
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: file_contains
expected: my_inputrc::completion-ignore-case on
hints:
  - "Write readline configuration directives to a file."
  - "Use printf or echo with redirection."
  - "Type: `printf 'set completion-ignore-case on\\nset show-all-if-ambiguous on\\n' > my_inputrc`"
-->
### Exercise 6: Create an inputrc
Create a file called `my_inputrc` with readline settings including case-insensitive completion.

---

## What You Learned

- **Dotfiles** -- hidden config files that customize your environment
- **`.bashrc`** vs **`.bash_profile`** -- when each is loaded
- **`source`** -- apply config changes without restarting
- **Environment variables** -- `export` to set, `env` to list
- **Symlinks** -- manage dotfiles with git using symbolic links
- **`.inputrc`** -- customize command-line input behavior
