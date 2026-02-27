# Terminal Multiplexing with tmux

**tmux** (Terminal Multiplexer) lets you manage multiple terminal sessions
inside a single window. You can split your terminal into panes, switch between
windows, and most importantly, **detach and reattach** sessions. This means
your work continues running even if you disconnect.

## Why tmux?

- **Persistent sessions** -- disconnect from SSH and your processes keep running
- **Multiple windows** -- like tabs in a browser, but for terminals
- **Split panes** -- see multiple things at once
- **Session sharing** -- let someone else view your terminal

## Starting tmux

```bash
tmux                          # start a new session
tmux new -s watchfloor        # start a named session
tmux ls                       # list existing sessions
tmux attach -t watchfloor     # reattach to a session
tmux kill-session -t watchfloor # kill a session
```

<!-- exercise
id: ex01
title: Check if tmux is installed
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: tmux
hints:
  - "Use which or the --version flag to check for tmux."
  - "Try running tmux -V to print the version."
  - "Type: `which tmux || echo 'tmux not found'`"
-->
### Exercise 1: Check if tmux is installed
Verify that tmux is available on your system.

---

## The Prefix Key

tmux commands use a **prefix key** followed by another key. The default prefix
is `Ctrl+b`. You press `Ctrl+b`, release both keys, then press the command key.

For example: `Ctrl+b` then `c` creates a new window.

> Many users rebind the prefix to `Ctrl+a` (like GNU screen) because it is
> easier to reach. This is done in `~/.tmux.conf`.

---

## Windows (Tabs)

| Command | Action |
|---------|--------|
| `Ctrl+b c` | Create new window |
| `Ctrl+b n` | Next window |
| `Ctrl+b p` | Previous window |
| `Ctrl+b 0-9` | Switch to window by number |
| `Ctrl+b ,` | Rename current window |
| `Ctrl+b &` | Kill current window |
| `Ctrl+b w` | List windows (interactive picker) |

The status bar at the bottom shows your windows.

---

## Panes (Splits)

| Command | Action |
|---------|--------|
| `Ctrl+b %` | Split vertically (left/right) |
| `Ctrl+b "` | Split horizontally (top/bottom) |
| `Ctrl+b arrow` | Move between panes |
| `Ctrl+b x` | Kill current pane |
| `Ctrl+b z` | Zoom/unzoom current pane (toggle fullscreen) |
| `Ctrl+b {` | Swap pane left |
| `Ctrl+b }` | Swap pane right |
| `Ctrl+b q` | Show pane numbers (press number to switch) |

<!-- exercise
id: ex02
title: Create a tmux cheat sheet
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: file_contains
expected: tmux_cheat.txt::Ctrl+b c
hints:
  - "Write common tmux commands to a reference file."
  - "Use printf or echo with redirection."
  - "Type: `printf 'Ctrl+b c  - new window\\nCtrl+b n  - next window\\nCtrl+b %%  - split vertical\\nCtrl+b \"  - split horizontal\\n' > tmux_cheat.txt`"
-->
### Exercise 2: Create a tmux cheat sheet
Create a file called `tmux_cheat.txt` listing at least the command for creating a new window (`Ctrl+b c`).

---

## Detach and Reattach

This is tmux's killer feature. When you **detach**, the session keeps running
in the background. You can reattach later, even from a different SSH connection.

```bash
# Inside tmux:
Ctrl+b d              # detach from current session

# From the regular shell:
tmux ls               # list sessions
tmux attach -t 0      # reattach to session 0
tmux a                # reattach to last session (shorthand)
```

This is invaluable for long-running processes over SSH. If your network drops,
your session survives.

<!-- exercise
id: ex03
title: Simulate session persistence
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: file_contains
expected: long_running.sh::echo "Process complete"
hints:
  - "Create a script that simulates a long-running monitoring process."
  - "Write a script with a sleep and a completion message."
  - "Type: `printf '#!/bin/bash\\necho \"Starting network monitor...\"\\nsleep 1\\necho \"Process complete\"\\n' > long_running.sh && chmod +x long_running.sh`"
-->
### Exercise 3: Simulate session persistence
Create an executable script called `long_running.sh` that prints `Starting network monitor...`, sleeps, then prints `Process complete`.

---

## Copy Mode

tmux has a copy mode that lets you scroll through output and select text:

```
Ctrl+b [              # enter copy mode
q                     # exit copy mode
```

In copy mode:
- Use arrow keys or vi keys (`hjkl`) to navigate
- `Space` to start selection, `Enter` to copy
- `Ctrl+b ]` to paste

> With `set -g mode-keys vi` in your config, copy mode uses vi keybindings.

---

## Configuration -- `~/.tmux.conf`

tmux is highly configurable. Common customizations:

```bash
# ~/.tmux.conf

# Change prefix to Ctrl+a
unbind C-b
set -g prefix C-a
bind C-a send-prefix

# Enable mouse support
set -g mouse on

# Use vi keys in copy mode
set -g mode-keys vi

# Start window numbering at 1 (not 0)
set -g base-index 1

# Split panes with | and -
bind | split-window -h
bind - split-window -v

# Reload config
bind r source-file ~/.tmux.conf \; display "Reloaded!"
```

<!-- exercise
id: ex04
title: Create a tmux config
xp: 20
difficulty: 3
sandbox_setup: null
validation_type: file_contains
expected: my_tmux.conf::set -g mouse on
hints:
  - "Write tmux configuration directives to a file."
  - "Include mouse support and vi keys."
  - "Type: `printf 'set -g mouse on\\nset -g mode-keys vi\\nset -g base-index 1\\n' > my_tmux.conf`"
-->
### Exercise 4: Create a tmux config
Create a file called `my_tmux.conf` with tmux settings including `set -g mouse on`.

---

## Named Sessions and Workflow

Power users create named sessions for different monitoring tasks:

```bash
# Start operations-specific sessions
tmux new -s watchfloor
tmux new -s logs
tmux new -s network

# Quick switch between sessions
Ctrl+b s              # interactive session picker
Ctrl+b (              # previous session
Ctrl+b )              # next session
```

<!-- exercise
id: ex05
title: Write a tmux startup script
xp: 20
difficulty: 3
sandbox_setup: null
validation_type: file_contains
expected: tmux_start.sh::tmux new-session
hints:
  - "Write a script that creates a tmux session with specific setup."
  - "Use tmux new-session with the -d flag to start detached."
  - "Type: `printf '#!/bin/bash\\ntmux new-session -d -s watchfloor\\ntmux send-keys -t watchfloor \"echo ready\" Enter\\necho \"Session created\"\\n' > tmux_start.sh && chmod +x tmux_start.sh`"
-->
### Exercise 5: Write a tmux startup script
Create a script called `tmux_start.sh` that programmatically creates a tmux session named `watchfloor`.

---

## tmux vs screen

`screen` is an older terminal multiplexer. tmux has largely replaced it due to:
- Better scripting support
- Cleaner configuration
- Vertical splits (screen added this late)
- Active development

If tmux is not available, `screen` is a reasonable fallback with similar
(but not identical) functionality.

<!-- exercise
id: ex06
title: List tmux key bindings reference
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: bind-key
hints:
  - "tmux can list all its key bindings."
  - "Use tmux with the list-keys command."
  - "Type: `tmux list-keys 2>/dev/null | head -5 || echo 'bind-key reference: Ctrl+b ? inside tmux'`"
-->
### Exercise 6: List tmux key bindings
Display tmux key bindings (or a reference note if tmux is not running).

---

## What You Learned

- **`tmux`** -- start, attach, detach, and manage terminal sessions
- **Prefix key** (`Ctrl+b`) -- the gateway to all tmux commands
- **Windows** -- multiple terminal tabs within a session
- **Panes** -- split views within a window
- **Detach/reattach** -- persistent sessions that survive disconnects
- **Copy mode** -- scroll and copy text from output
- **`~/.tmux.conf`** -- customize tmux behavior
