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
- Web terminal serial input now normalizes Enter payloads (`\r\n`/`\r` -> `\n`)
  before forwarding to VM to prevent duplicate empty-command submits and
  repeated prompts.
- Web startup prompt behavior now coalesces deferred terminal size-sync (`stty`)
  into the lesson-open prompt refresh, and dedupes already-synced dimensions,
  to avoid multiple prompt repaints on initial lesson load.
- Sentinel mute release now occurs on the skipped internal capture `CMD_END`
  (not `CMD_START`) so delayed/stale sentinel ordering cannot reveal internal
  maintenance commands like `stty ...` in the visible terminal.
- Sentinel mute tracking now uses a counter (`pendingMutedSkips`) so overlapping
  internal skipped commands cannot unmute each other early.
- Sentinel counter arming now happens in `skipNextCapture()` (only when muted),
  preventing unmatched mute calls (like pre-validation mute) from hiding the
  next prompt indefinitely.
- Removed eager post-boot terminal-size sync; first size sync is deferred until
  lesson layout stabilizes to avoid transient-width `stty` churn at startup.
- Lesson-open flow now defers execution of terminal-size sync through sidebar
  settle (~380ms) so the pending resize sync is consumed by the same
  `refreshPrompt("open-lesson")` command, preventing a second startup prompt.
- Final web lesson (`14_next_steps`) now uses a dedicated non-VM interactive
  guide page (`NextStepsGuide`) and skips v86 boot entirely, with dynamic setup
  tracks for local native, local VM, and cloud environments.

## Local Dev
- Web dev server command: `cd clitutor-web && npm run dev -- --host localhost --port 5173`
- TUI tests (fast subset): `.venv/bin/pytest -q tests/test_validator.py tests/test_loader.py tests/test_executor.py`
- Docker-backed `test_student_flow.py` requires Docker daemon access.
