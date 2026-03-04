# Tips and Tricks

This lesson is a hands-on speed drill built around a realistic on-call moment.
An alert just fired. You need to build a triage workspace, move quickly, and
avoid wasting keystrokes.

Goal: build muscle memory for history recall, cursor movement, tab completion,
and fast command composition under time pressure.

## Fast Recall and Editing

These are the shortcuts you should actively practice during each exercise. The
first exercises are slow reps. The last exercises are speed reps.

| Shortcut | Action |
|----------|--------|
| `Up Arrow` / `Down Arrow` | Move through recent commands |
| `Ctrl+R` | Reverse-search command history |
| `Ctrl+A` / `Ctrl+E` | Jump to start/end of line |
| `Alt+B` / `Alt+F` | Move by word |
| `Ctrl+W` | Delete previous word |
| `Ctrl+U` / `Ctrl+K` | Delete before/after cursor |
| `Tab` | Complete commands/paths |

Rule for this lesson: if you make a typo, fix it in place with shortcuts.
Avoid clearing and retyping entire commands.

## Scenario Setup: Active Incident

You are on call and a service health check just failed. Work through this
sequence like a real triage pass: set up, inspect, log, summarize.

<!-- exercise
id: ex01
title: Enter your incident workspace
xp: 8
difficulty: 1
sandbox_setup: null
validation_type: cwd_regex
expected: "/incident$"
hints:
  - "Create a directory named incident and change into it."
  - "Use command chaining so setup is one fast action."
  - "Type: `mkdir -p incident && cd incident`"
-->
### Exercise 1: Enter your incident workspace
Create a directory called `incident` and move into it.

Warm-up rep: before pressing Enter, hit `Ctrl+A`, then `Ctrl+E`, then run it.

---

<!-- exercise
id: ex02
title: Create triage checklists quickly
xp: 8
difficulty: 1
sandbox_setup: null
validation_type: file_exists
expected: incident/checklists/auth.txt
hints:
  - "Create `incident/checklists` and three files in one command."
  - "Brace expansion is faster than three separate touch commands."
  - "Type: `mkdir -p incident/checklists && touch incident/checklists/{network,auth,dns}.txt`"
-->
### Exercise 2: Create triage checklists quickly
Create `network.txt`, `auth.txt`, and `dns.txt` in `incident/checklists/` as
your triage checklist files.

Type only part of the path and use `Tab` to complete the rest.

---

<!-- exercise
id: ex03
title: Count checklist files with a wildcard
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_regex
expected: '^\s*3\s*$'
hints:
  - "Count checklist files to confirm setup is complete."
  - "Use a wildcard with wc -l."
  - "Type: `ls incident/checklists/*.txt | wc -l`"
-->
### Exercise 3: Count checklist files with a wildcard
Count how many `.txt` files are in `incident/checklists/`.

Do not start from an empty line: use `Up Arrow`, edit, then run.

---

<!-- exercise
id: ex04
title: Cursor movement drill
xp: 10
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: incident triage in progress
hints:
  - "Print this exact phrase with echo."
  - "Deliberately fix a typo using Ctrl+A/Ctrl+E or Alt+B/Alt+F before you run it."
  - "Type: `echo 'incident triage in progress'`"
-->
### Exercise 4: Cursor movement drill
Print exactly:

`incident triage in progress`

This is your editing rep. Fix mistakes with cursor movement keys, not retyping.

---

## Job Control in the Middle of Work

A common on-call move: kick off a long-running check, then keep working.

<!-- exercise
id: ex05
title: Start a background check and list jobs
xp: 12
difficulty: 2
sandbox_setup: null
validation_type: output_regex
expected: '(sleep|Running|\[1\])'
hints:
  - "Start a background check, then verify it in the jobs list."
  - "Use `&` to background a command."
  - "Type: `sleep 60 & jobs`"
-->
### Exercise 5: Start a background check and list jobs
Start a background task and verify it appears in the jobs list.

After running it, tap `Up Arrow` and inspect the command you just used.

---

## Aliases and Command Chaining

<!-- exercise
id: ex06
title: Make a quick alias for checklist review
xp: 14
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: ls -lah incident/checklists
hints:
  - "Create alias lcheck for listing the checklists directory in long format."
  - "Immediately verify the alias so you trust it under pressure."
  - "Type: `alias lcheck='ls -lah incident/checklists' && alias lcheck`"
-->
### Exercise 6: Make a quick alias for checklist review
Create an alias called `lcheck` for:

`ls -lah incident/checklists`

Then show the alias definition to confirm it is correct.

---

<!-- exercise
id: ex07
title: Log an action with command chaining
xp: 18
difficulty: 3
sandbox_setup: null
validation_type: file_contains
expected: incident/logs/actions.log::checked network
hints:
  - "Create the logs directory, append a line, then print the file."
  - "Use && so each step must succeed before the next runs."
  - "Type: `mkdir -p incident/logs && echo 'checked network' >> incident/logs/actions.log && cat incident/logs/actions.log`"
-->
### Exercise 7: Log an action with command chaining
Append `checked network` to `incident/logs/actions.log`, then display the file.

Speed rep: recall a recent command from history and edit it into this one.

---

<!-- exercise
id: ex08
title: Build a one-line status summary
xp: 20
difficulty: 3
sandbox_setup: null
validation_type: output_contains
expected: "summary:"
hints:
  - "Use command substitution so values are generated dynamically."
  - "Include checklist count and current directory in one status line."
  - "Type: `echo \"summary: $(ls incident/checklists/*.txt | wc -l) checklists in $(pwd)\"`"
-->
### Exercise 8: Build a one-line status summary
Print one line that starts with `summary:` and includes:
- the checklist file count
- your current directory

Final speed rep: build the whole line in one go using command substitution
(`$()`) instead of hardcoding values.

---

## What You Practiced

- **History recall** with `Up Arrow` and `Ctrl+R`
- **Cursor movement/editing** with `Ctrl+A/E`, `Alt+B/F`, `Ctrl+W/U/K`
- **Tab completion** for faster path entry
- **Wildcards** for selecting multiple files
- **Job control** with background tasks and `jobs`
- **Aliases** for repeated commands
- **Command chaining** with `&&`
- **Command substitution** with `$()`
