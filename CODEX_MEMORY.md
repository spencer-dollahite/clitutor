# Codex Memory

## Project Focus
- CLItutor has both a TUI (`src/clitutor`) and web VM app (`clitutor-web`).
- Web app is terminal-first and runs Alpine Linux in browser via v86.
- Deployed under `/clitutor/` subpath and depends on COOP/COEP headers.

## Core Runtime Flow (Web)
- `App.start()` loads metadata and shows lesson picker.
- VM boots only after lesson selection.
- Serial output is parsed by `SentinelCapture` to separate display text and command results.
- Validation happens per exercise via `OutputValidator`.

## Lessons and Validation
- Lesson markdown embeds YAML exercise blocks in HTML comments.
- Metadata lives in `public/lessons/metadata.json` (web) and `src/clitutor/lessons/metadata.json` (TUI).
- Validation types in use include output/cwd/file-based checks.

## Known Recent Changes
- Tightened several false-positive validations (cut/wc/pipeline/vi delete cases).
- Added stricter expected patterns in:
  - `src/clitutor/lessons/01_slicing_and_dicing.md`
  - `src/clitutor/lessons/10_vi.md`
  - `clitutor-web/public/lessons/01_slicing_and_dicing.md`
  - `clitutor-web/public/lessons/10_vi.md`
- Updated TUI PTY capture to strip prompt+echo first line before validation.

## Local Dev
- Web dev server command: `cd clitutor-web && npm run dev -- --host 127.0.0.1 --port 5173`
- TUI tests (fast subset): `.venv/bin/pytest -q tests/test_validator.py tests/test_loader.py tests/test_executor.py`
- Docker-backed `test_student_flow.py` requires Docker daemon access.

