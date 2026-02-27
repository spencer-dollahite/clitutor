# Version Control with Git

**Git** is the most widely used version control system in the world. It tracks
changes to files, enables collaboration, and provides a safety net for your
code. Every developer and sysadmin should know git basics.

## Initializing a Repository

```bash
git init                  # create a new git repo in the current directory
git init network-configs  # create a new repo in a new directory
```

This creates a hidden `.git` directory that stores all version history.

<!-- exercise
id: ex01
title: Initialize a git repository
xp: 15
difficulty: 2
sandbox_setup: null
validation_type: output_contains
expected: Initialized
hints:
  - "Use the git command that creates a new repository."
  - "The subcommand is 'init'."
  - "Type: `git init network-configs`"
-->
### Exercise 1: Initialize a git repository
Create a new git repository called `network-configs`.

---

## The Git Workflow

The basic git workflow is:

1. **Modify** files in your working directory
2. **Stage** changes you want to commit (`git add`)
3. **Commit** staged changes with a message (`git commit`)

```
Working Directory  -->  Staging Area  -->  Repository
     (edit)          (git add)         (git commit)
```

### Checking Status

```bash
git status               # see what has changed
git diff                 # see unstaged changes
git diff --staged        # see staged changes
```

<!-- exercise
id: ex02
title: Add and check status
xp: 15
difficulty: 2
sandbox_setup:
  - "git init network-configs"
validation_type: output_contains
expected: new file
hints:
  - "Create a file inside the repo, add it to staging, and check status."
  - "Use touch to create, git add to stage, and git status to check."
  - "Type: `cd network-configs && touch README.md && git add README.md && git status`"
-->
### Exercise 2: Add and check status
Inside the `network-configs` repository, create a `README.md` file, stage it, and check the status.

---

## Committing Changes

```bash
git add file.txt          # stage a specific file
git add .                 # stage all changes
git commit -m "message"   # commit with a message
git commit -am "message"  # add + commit tracked files (shortcut)
```

Write meaningful commit messages. The convention is:
- Short summary on the first line (under 50 characters)
- Blank line, then longer description if needed

<!-- exercise
id: ex03
title: Make your first commit
xp: 20
difficulty: 2
sandbox_setup:
  - "git init network-configs"
  - "cd network-configs && git config user.name student && git config user.email student@clitutor && touch README.md && git add README.md"
validation_type: output_contains
expected: "initial baseline config"
hints:
  - "Use git commit with the -m flag to provide a message."
  - "The message should be in quotes after -m."
  - "Type: `cd network-configs && git commit -m 'initial baseline config'`"
-->
### Exercise 3: Make your first commit
Commit the staged `README.md` with the message `initial baseline config`.

---

## Viewing History

```bash
git log                   # full commit history
git log --oneline         # compact one-line format
git log --graph           # visual branch graph
git log -n 5              # last 5 commits
git show <commit-hash>    # details of a specific commit
```

<!-- exercise
id: ex04
title: View the log
xp: 10
difficulty: 2
sandbox_setup:
  - "git init network-configs"
  - "cd network-configs && git config user.name student && git config user.email student@clitutor && touch README.md && git add README.md && git commit -m 'initial baseline config'"
validation_type: output_contains
expected: initial baseline config
hints:
  - "Use the git command that shows commit history."
  - "The subcommand is 'log'."
  - "Type: `cd network-configs && git log --oneline`"
-->
### Exercise 4: View the log
View the commit history of `network-configs` in one-line format.

---

## Branching

Branches let you work on features or fixes in isolation:

```bash
git branch                        # list branches
git branch patch-firewall-rules   # create a branch
git checkout patch-firewall-rules # switch to the branch
git checkout -b patch-firewall-rules  # create AND switch (shortcut)
git switch patch-firewall-rules   # modern alternative to checkout
git switch -c patch-firewall-rules    # create AND switch (modern)
```

<!-- exercise
id: ex05
title: Create and switch to a branch
xp: 15
difficulty: 3
sandbox_setup:
  - "git init network-configs"
  - "cd network-configs && git config user.name student && git config user.email student@clitutor && touch README.md && git add README.md && git commit -m 'initial baseline config'"
validation_type: output_contains
expected: patch-firewall-rules
hints:
  - "Use git checkout -b or git switch -c to create and switch to a new branch."
  - "Then verify with git branch to see the current branch."
  - "Type: `cd network-configs && git checkout -b patch-firewall-rules && git branch`"
-->
### Exercise 5: Create and switch to a branch
In `network-configs`, create a new branch called `patch-firewall-rules` and switch to it. List branches to verify.

---

## Merging

Bring changes from one branch into another:

```bash
git checkout main                 # switch to the target branch
git merge patch-firewall-rules    # merge feature branch into main
```

If git cannot automatically merge (both branches changed the same lines), you
get a **merge conflict**. You must manually edit the conflicting files, then:

```bash
git add resolved_file.txt
git commit                # complete the merge
```

<!-- exercise
id: ex06
title: Merge a branch
xp: 20
difficulty: 3
sandbox_setup:
  - "git init -b main network-configs"
  - "cd network-configs && git config user.name student && git config user.email student@clitutor && touch README.md && git add README.md && git commit -m 'initial baseline config'"
  - "cd network-configs && git checkout -b patch-firewall-rules"
  - "cd network-configs && echo 'ACCEPT TCP/8443 0.0.0.0/0' > firewall_patch.txt && git add firewall_patch.txt && git commit -m 'add HTTPS alt port rule'"
validation_type: output_contains
expected: firewall_patch.txt
hints:
  - "Switch back to the main branch and merge the feature branch."
  - "Use git checkout then git merge."
  - "Type: `cd network-configs && git checkout main && git merge patch-firewall-rules && ls`"
-->
### Exercise 6: Merge a branch
Switch back to the main branch in `network-configs` and merge the `patch-firewall-rules` branch. List files to confirm.

---

## Useful Git Commands

```bash
git stash                 # temporarily shelve changes
git stash pop             # restore stashed changes
git reset HEAD file.txt   # unstage a file
git checkout -- file.txt  # discard unstaged changes
git remote -v             # show remote repositories
git clone <url>           # clone a remote repository
git pull                  # fetch and merge remote changes
git push                  # push local commits to remote
```

<!-- exercise
id: ex07
title: Configure git user
xp: 10
difficulty: 2
sandbox_setup:
  - "git init network-configs"
validation_type: output_contains
expected: operator
hints:
  - "Set your git user name using git config."
  - "The command is git config user.name followed by the name in quotes."
  - "Type: `cd network-configs && git config user.name 'operator' && git config user.name`"
-->
### Exercise 7: Configure git user
Set the git user name to `operator` in the `network-configs` repository and verify it.

---

## `.gitignore`

The `.gitignore` file tells git which files to ignore:

```
# .gitignore
*.log
*.pcap
.env
credentials/
```

Files listed here will not appear in `git status` and will not be staged.

<!-- exercise
id: ex08
title: Create a .gitignore
xp: 15
difficulty: 2
sandbox_setup:
  - "git init network-configs"
validation_type: file_contains
expected: network-configs/.gitignore::*.log
hints:
  - "Create a .gitignore file with patterns for files to ignore."
  - "Use echo or printf with redirection."
  - "Type: `printf '*.log\\n*.pcap\\n.env\\ncredentials/\\n' > network-configs/.gitignore`"
-->
### Exercise 8: Create a .gitignore
Create a `.gitignore` file in `network-configs` that ignores `*.log` and `*.pcap` files, `.env`, and the `credentials/` directory.

---

## What You Learned

- **`git init`** -- create a new repository
- **`git add`** / **`git commit`** -- stage and commit changes
- **`git status`** / **`git diff`** -- inspect the working tree
- **`git log`** -- view commit history
- **`git branch`** / **`git checkout`** -- create and switch branches
- **`git merge`** -- combine branches
- **`.gitignore`** -- exclude files from version control
- **`git config`** -- configure user info and preferences
