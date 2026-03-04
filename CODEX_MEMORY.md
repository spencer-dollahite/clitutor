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
- Reworked Lesson 03 (`03_tips_and_tricks`) into a progressive, scenario-based
  incident-triage drill focused on muscle-memory practice, replacing the old
  generic checks.
- Removed the prior `type cd` builtin exercise from Lesson 03 and replaced the
  sequence with smaller exercises covering:
  - workspace navigation (`cd` + chaining),
  - tab-friendly path/file creation with brace expansion,
  - wildcard counting,
  - cursor/editing drill prompts,
  - job control (`sleep ... &` + `jobs`),
  - aliases,
  - command chaining,
  - command substitution.
- Mirrored Lesson 03 updates in both:
  - `src/clitutor/lessons/03_tips_and_tricks.md`
  - `clitutor-web/public/lessons/03_tips_and_tricks.md`
- Updated `tests/test_student_flow.py` Lesson 03 coverage to match the new
  8-exercise flow.
- Tuned Lesson 03 pacing (XP/difficulty ramp) to start lighter and end with a
  stronger capstone:
  - XP progression: `8, 8, 10, 10, 12, 14, 18, 20` (total still 100)
  - Difficulty progression: `1, 1, 1, 2, 2, 2, 3, 3`
- Refined Lesson 03 instructional wording/hints to feel like an escalating
  on-call incident drill ("warm-up reps" -> "speed reps") while preserving the
  same validation logic and command targets.
- Added sandbox startup guard in generated bashrc (web VM + TUI template) to
  ensure `/etc/hosts` contains `127.0.0.1 localhost`, so `ping localhost`
  resolves reliably in networking exercises.
- Extended sandbox startup host aliasing for networking labs so
  `gateway.fleet.mil` and `cic-display.local` also resolve to `127.0.0.1`
  (in addition to `localhost`) for deterministic offline behavior.
- Updated Lesson 07 networking copy (both TUI + web lesson files) with an
  explicit "lab realism" note that these fleet hostnames are simulated aliases
  mapped locally, while networking principles remain real.
- Added nginx overlay config at
  `clitutor-web/build/rootfs-overlay/etc/nginx/http.d/default.conf` so unknown
  paths fall back to `/index.html` instead of 404, making exploratory `curl`
  to arbitrary lab endpoints return the dashboard page.
- Relaxed Lesson 07 exercise 3 validation from strict `output_contains: HTTP`
  to regex accepting either header output (`HTTP`) or dashboard body output
  (`Fleet Shore Station Monitor`) to support multiple valid `curl` workflows.
- Updated Lesson 10 (`10_vi`) exercise 1 to focus on launching `vimtutor` with
  explicit "spend ~1 hour practicing" guidance; validation now accepts either
  real tutor screen text (`vim tutor`) or binary-path verification
  (`command -v vimtutor`) for environments where fullscreen capture is brittle.
- Lesson 05 prompt exercise 2 validation was relaxed from literal
  `output_contains: "PS1"` to a regex that accepts either:
  - `echo "PS1=$PS1"` style output, or
  - direct `echo $PS1` output (expanded or escaped prompt forms).
- Mirrored this lesson metadata change in both:
  - `src/clitutor/lessons/05_prompt.md`
  - `clitutor-web/public/lessons/05_prompt.md`
- Added a student-flow regression test to accept
  `PS1='\\u@\\h:\\w\\$ ' && echo $PS1` for lesson 05 ex02.
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
- Reordered lesson sequencing so `10_vi` is positioned as the second-to-last
  lesson in both metadata tracks; in the web track it now appears immediately
  before `14_next_steps`, and source metadata order values were adjusted to keep
  ordering contiguous.
- Fixed `10_vi` exercise-1 regex compatibility across runtimes:
  - updated expected pattern to `vimtutor|vim tutor` in both source + web lesson
    files,
  - hardened web regex validation to accept legacy Python-style `(?i)` and
    slash-delimited `/.../flags` patterns instead of erroring with
    "Invalid regex pattern."
- Tightened `10_vi` exercise-1 matching to avoid false passes on
  `vimtutor: command not found` by requiring one of:
  `/vimtutor`, `vim tutor`, or `usage: vimtutor`.
- Added VM overlay wrapper at
  `clitutor-web/build/rootfs-overlay/usr/local/bin/vimtutor` so `vimtutor`
  exists in lab PATH even when distro packaging differs; wrapper delegates to
  packaged `vimtutor` when available, otherwise opens tutor files with `vi`.
- Updated lab `vimtutor` wrapper UX:
  - added explicit `-h/--help` support with `usage: vimtutor` output (non-
    interactive validation path),
  - prints a one-line "vim tutor: opening ..." message before launching `vi`
    fallback so students get clear feedback instead of a perceived hang.
- Updated Lesson 10 exercise-1 hints (source + web) to recommend `vimtutor -h`
  or `command -v vimtutor` when fullscreen interaction is awkward.
- Further simplified Lesson 10 exercise 1 validation: it no longer watches the
  interactive session. The exercise now asks students to run `vimtutor` for
  practice and, upon exit, run `command -v vimtutor`; the validator only checks
  that the binary exists (`output_contains: vimtutor`), acknowledging that the
  actual tutoring happens outside the grader.
- Replaced the repeated wrapper logic with a self-contained, interactive
  `vimtutor` experience stored under `/usr/local/share/vimtutor/vimtutor.txt`.
  The wrapper now creates that file (with navigation/edit drills) and launches
  `vim` directly against it, printing a short banner so students see progress.
- Reverted to the upstream Vim `vimtutor` launcher:
  - copied `/usr/bin/vimtutor` and the entire `/usr/share/vim/vim91/tutor`
    tree from the host into `rootfs-overlay`,
  - the script now behaves just like the official tutorial (copies a tutor
    file and launches Vim), so students see the real interactive experience.
- Updated `deploy.sh` so VPS deployments rebuild the VM assets and include
  the `public/v86` directory:
  1. `npm run build-rootfs` + `npm run build-state` now run before `npm run build`.
  2. After `dist/` is synced, `public/v86/` (whole VM state/rootfs) is rsynced
     to `$DEPLOY_DIR/v86` so production also serves the same VM snapshot.

## Local Dev
- Web dev server command: `cd clitutor-web && npm run dev -- --host localhost --port 5173`
- TUI tests (fast subset): `.venv/bin/pytest -q tests/test_validator.py tests/test_loader.py tests/test_executor.py`
- Docker-backed `test_student_flow.py` requires Docker daemon access.
