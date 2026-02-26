# CLItutor

An interactive CLI tutorial designed for graduate education at the Naval
Postgraduate School. CLItutor teaches Linux command-line skills through hands-on
exercises in a sandboxed environment. Students work through lessons in an
integrated terminal, earn XP for completing exercises, and track their progress.

## Try It Now

**No install required** — run CLItutor directly in your browser:

### [ssdollahite.com/clitutor](https://ssdollahite.com/clitutor)

The web version runs a full Linux environment in-browser, so you can start
learning immediately from any device.

---

## Features

- **15 lessons** covering basics through advanced topics (scripting, networking,
  SSH, Git, Docker, and more)
- **Interactive terminal** with a real sandboxed Linux environment
- **Automatic validation** of exercise output, exit codes, and file state
- **XP and progress tracking** across sessions
- **Tab completion** and hint overlays for a guided experience

## Local Installation

If you prefer to run CLItutor locally, clone and run — one command does it all:

```bash
git clone https://github.com/spencer-dollahite/clitutor.git && cd clitutor && ./bootstrap.sh
```

The bootstrap script finds (or installs) Python, creates a virtualenv, installs
dependencies, and launches the app automatically.

<details>
<summary>Manual installation</summary>

Requires **Python 3.8+**.

```bash
git clone https://github.com/spencer-dollahite/clitutor.git
cd clitutor
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Then run:

```bash
clitutor          # installed entry point
# or
python -m clitutor
```

</details>

## Lessons

| # | Title | Category | Difficulty |
|---|-------|----------|------------|
| 0 | Start Here: CLI Basics | basics | 1 |
| 1 | Slicing and Dicing | text processing | 2 |
| 2 | File Permissions | system admin | 2 |
| 3 | Tips and Tricks | productivity | 2 |
| 4 | The PATH Variable | system | 2 |
| 5 | Customizing Your Prompt | customization | 2 |
| 6 | Shell Scripting Basics | scripting | 3 |
| 7 | Networking Tools | networking | 3 |
| 8 | SSH | networking | 3 |
| 9 | Version Control with Git | tools | 3 |
| 10 | The vi Editor | tools | 2 |
| 11 | Terminal Multiplexing with tmux | tools | 3 |
| 12 | Dotfiles | customization | 2 |
| 13 | Installing Software | system admin | 2 |
| 14 | Docker Basics | devops | 4 |

## Docker Sandbox

If Docker is available, CLItutor automatically uses a container sandbox
(Ubuntu 22.04 with common CLI tools pre-installed) for exercise isolation.
Otherwise it falls back to a local tmpdir sandbox.

To build the sandbox image manually:

```bash
docker build -t clitutor-sandbox docker/
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

Tests cover the core modules (XP, progress, sandbox, executor, validator,
loader) and use `pytest-asyncio` for async Textual tests.

## License

This software was created by United States Government employees at the Naval
Postgraduate School. See [LICENSE](LICENSE) for details.
