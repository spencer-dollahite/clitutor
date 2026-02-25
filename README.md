# CLItutor

An interactive CLI tutorial with a gamified TUI built on
[Textual](https://github.com/Textualize/textual). Designed for graduate
education at the Naval Postgraduate School, CLItutor teaches Linux command-line
skills through hands-on exercises in a sandboxed environment.

Students work through lessons in an integrated terminal, earn XP for completing
exercises, and track their progress — all without leaving the TUI.

## Features

- **15 lessons** covering basics through advanced topics (scripting, networking,
  SSH, Git, Docker, and more)
- **Interactive terminal** with a real PTY embedded in the TUI
- **Automatic validation** of exercise output, exit codes, and file state
- **XP and progress tracking** across sessions
- **Sandboxed execution** — exercises run in a local tmpdir or Docker container
- **Tab completion** and hint overlays for a guided experience

## Quick Start

The bootstrap script handles everything — finding (or installing) Python,
creating a virtualenv, installing dependencies, and launching the app:

```bash
./bootstrap.sh
```

### Manual Installation

Requires **Python 3.8+**.

```bash
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
