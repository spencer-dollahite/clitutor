# CLItutor

Interactive CLI tutorial with a gamified TUI built on Textual. Designed for
graduate education at the Naval Postgraduate School, teaching students Linux
command-line skills through hands-on exercises in a sandboxed environment.

## Quick Reference

- **Run the app:** `python -m clitutor` or `clitutor` (after pip install)
- **Run tests:** `pytest` (from repo root; uses pytest-asyncio for async tests)
- **Install dev:** `pip install -e ".[dev]"` (venv at `.venv/`)
- **Python:** 3.8+ (uses `from __future__ import annotations` throughout)

## Architecture

```
src/clitutor/
  app.py              # Textual App entry point (CLItutorApp)
  core/
    loader.py          # Parses lesson markdown + metadata.json
    sandbox.py         # Local tmpdir sandbox (SandboxManager)
    docker_sandbox.py  # Docker-based sandbox (DockerSandbox)
    executor.py        # Runs commands in sandbox, returns CommandResult
    validator.py       # Validates exercise output (OutputValidator)
    completer.py       # Tab completion for terminal pane
  models/
    lesson.py          # Exercise, LessonData, LessonMeta dataclasses
    xp.py              # XP calculation
    progress.py        # ProgressManager (tracks completed lessons/XP)
  screens/
    home.py            # Home screen (lesson browser, XP display)
    lesson.py          # Lesson screen (markdown + terminal + exercises)
  widgets/
    terminal_pane.py   # Interactive terminal widget
    command_input.py   # Command input with tab completion
    markdown_pane.py   # Renders lesson markdown
    lesson_browser.py  # Lesson list/selection widget
    xp_bar.py          # XP progress bar
    hint_overlay.py    # Hint popup overlay
  styles/*.tcss        # Textual CSS stylesheets (app, home, lesson)
  lessons/
    metadata.json      # Lesson index (id, title, xp, exercise_count, file)
    *.md               # Lesson content with embedded exercises
```

## Key Patterns

- **Sandbox duality:** App auto-detects Docker; falls back to local tmpdir.
  Both implement: `create()`, `cleanup()`, `seed_files()`, `file_exists()`, `file_read()`.
- **Validation types:** `output_equals`, `output_contains`, `output_regex`,
  `exit_code`, `file_exists`, `file_contains` (format: `filename::content`).
- **Lesson format:** Markdown files with exercise blocks parsed by loader.
  Metadata lives in `metadata.json`; lesson content in `.md` files.
- **Textual conventions:** Screens pushed via `push_screen()`. Styles in
  separate `.tcss` files. Widgets in `widgets/` package.

## When Adding Lessons

- Add the `.md` file in `src/clitutor/lessons/`
- Add an entry to `metadata.json` with matching id, file, xp, exercise_count
- Exercise blocks inside markdown are parsed by `core/loader.py`

## Testing

- Tests live in `tests/` and cover core modules (xp, progress, sandbox,
  executor, validator, loader)
- Use `pytest-asyncio` for any async Textual tests
