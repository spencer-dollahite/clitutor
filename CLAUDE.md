# CLItutor-Web

Browser-based interactive CLI tutorial running Alpine Linux via v86 (x86→WASM JIT).
Designed for graduate education at the Naval Postgraduate School, teaching Linux
command-line skills through hands-on exercises in a sandboxed in-browser VM.

## Quick Reference

- **Dev server:** `cd clitutor-web && npm run dev` (port 5173, auto-sets COOP/COEP headers)
- **Build:** `npm run build` (tsc + vite → `dist/`)
- **Build rootfs:** `npm run build-rootfs` (Docker-based Alpine i386 rootfs builder)
- **Build state:** `npm run build-state` (headless v86 state snapshot generator)
- **Deploy path:** `/clitutor/` subpath (configured in `vite.config.ts` `base`)

## Architecture

```
clitutor-web/src/
  main.ts                     # Entry: DOMContentLoaded → App(#app).start()
  v86.d.ts                    # Ambient types for global V86 class

  core/
    models.ts                  # Exercise, LessonData, LessonMeta, CommandResult interfaces
    lesson-loader.ts           # Fetch metadata.json + parse lesson .md + YAML exercise blocks
    progress.ts                # IndexedDB persistence (db: "clitutor", store: "progress")
    validator.ts               # 9 validation types against CommandResult + VM filesystem
    xp.ts                      # 17 levels ("Newbie"→"BDFL"), hint/difficulty/first-try modifiers

  vm/
    linux-vm.ts                # v86 wrapper: boot, serial I/O, 9p filesystem queries, respawn detection
    sentinel-capture.ts        # Serial stream state machine: sentinel extraction, ANSI strip
    bashrc.ts                  # Generates .clitutor_bashrc with sentinel PROMPT_COMMAND

  ui/
    app.ts                     # Central orchestrator: lifecycle, validation, muting, seeding
    toast.ts                   # Toast notifications (success/error/info)
    components/
      terminal-pane.ts         # xterm.js wrapper (FitAddon, WebLinksAddon, slash cmd intercept)
      markdown-pane.ts         # marked + highlight.js for lesson content
      hint-overlay.ts          # Modal with progressive hints + XP penalty warnings
    screens/
      lesson-picker.ts         # Landing: ASCII art, lesson cards, j/k nav, progress bars

  styles/theme.css             # Full CSS theme (~950 lines)

public/
  lessons/
    metadata.json              # Lesson index (15 lessons)
    *.md                       # Lesson content with embedded YAML exercise blocks
  v86/                         # VM assets: libv86.js, v86.wasm, BIOS, rootfs, state snapshot
```

## Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| VM | v86 ^0.5.319 | x86 emulator → Alpine Linux 3.21 i386 (GNU coreutils/grep/sed/gawk/findutils + bash) in browser |
| Terminal | @xterm/xterm ^5.5.0 | Terminal display with fit + web-links addons |
| Build | Vite ^6.0.0 + TypeScript ^5.7 | Dev server, bundling, COOP/COEP headers |
| Markdown | marked ^15.0.0 + highlight.js ^11.11 | Lesson content rendering |
| YAML | js-yaml ^4.1.0 | Parse exercise blocks embedded in lesson markdown |
| Persistence | IndexedDB (native) | Progress tracking across sessions |

## Boot Sequence

1. **LessonPicker** — user browses lessons (no VM yet)
2. **bootVM()** — creates LinuxVM, wires sentinel→terminal and sentinel→handleCommand
3. **waitForShell()** — watches serial for prompt pattern, then installs `.clitutor_bashrc`
4. **seedLessonSetup()** — writes sandbox files via 9p, executes setup script (muted)
5. **openLessonByMeta()** — loads sidebar, restores progress, announces first exercise

State snapshot path: instant restore ~1-3s. Cold boot: ~30s.

## Serial Data Flow

```
v86 serial0-output-byte → byte buffer → flush (on \n, \r, >128 bytes, 4ms timer)
  → sentinel.processOutput() → [1] onDisplay → xterm.js write
                               → [2] onCommand → handleCommand → validate
```

**CRITICAL**: onDisplay fires BEFORE onCommand. This ensures the prompt renders
before handleCommand can mute display for validation commands.

## Sentinel Machinery

PROMPT_COMMAND in bashrc runs after every command:
```bash
printf '\x1f__CLITUTOR_CMD_END__:%d:%s\x1f' "$rc" "$PWD"   # End previous capture
printf '\x1f__CLITUTOR_CMD_START__\x1f'                      # Start next capture
```

Sentinel char: `\x1f` (Unit Separator). SentinelCapture state machine tracks
`capturing`, `capturedChunks`, `skipCaptures` (starts at 1 for bash startup).

## Command Validation Flow

`handleCommand` guard chain:
1. `if (validating) return` — prevent recursive validation
2. `if (!currentLesson) return` — no lesson loaded
3. `if (exerciseIndex >= exercises.length) return` — past last exercise
4. `if (exercise.completed) return` — already done
5. For output-based types: `if (stdout==='') return` — empty Enter / Ctrl+C (130) / Ctrl+Z (148)
6. For `cwd_regex`: failing look-around commands (output produced, cwd unchanged) are not counted as attempts

## Validation Types

| Type | Checks | Notes |
|------|--------|-------|
| `output_equals` | `stdout.trim() === expected.trim()` | Exact match |
| `output_contains` | `(stdout+stderr).includes(expected)` | Substring |
| `output_regex` | `RegExp(expected).test(stdout+stderr)` | Regex |
| `exit_code` | `returncode === parseInt(expected)` | Numeric code |
| `cwd_regex` | `RegExp(expected).test(cwd)` | Working directory |
| `file_exists` | `vm.fileExists(path)` | Checks /home/student + cwd |
| `file_contains` | `vm.readFile().includes(content)` | Format: `filename::content` |
| `dir_with_file` | subdir containing a regular file | Host-side 9p inode walk (no shell cmds) |
| `any_file_contains` | recursive content search | Host-side 9p inode walk (no shell cmds) |

Filesystem types always validate (even empty stdout). Output types skip on empty Enter.

## Display Muting

During validation and sandbox seeding, `onDisplay` is swapped to a no-op:
```typescript
const origDisplay = this.sentinel.onDisplay;
this.sentinel.onDisplay = () => {};     // Mute
try { /* validation/seeding */ } finally { this.sentinel.onDisplay = origDisplay; }
```
Combined with `skipNextCapture()` for internal commands. Internal prompt kicks
(`refreshPrompt`, terminal-size sync) wait on `sentinel.waitForCommand()` with a
1200ms timeout; on timeout they call `cancelPendingSkip()` + `recoverMuteAfterTimeout()`
so a full-screen program (vi/less) can't leave the display muted or leak skip slots.
Both are gated on `terminalPane.isInputIdle` so a fast typist's input is never swallowed.

## Lesson Format

Exercise blocks in markdown are HTML comments with YAML:
```markdown
<!-- exercise
id: ex01
title: Print your current directory
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_regex
expected: "^/"
hints:
  - "Try the pwd command"
-->
```

Metadata in `public/lessons/metadata.json`:
```json
{ "id": "00_start_here", "title": "...", "slug": "...", "order": 0,
  "category": "basics", "difficulty": 1, "xp": 100, "exercise_count": 8,
  "file": "00_start_here.md" }
```

## When Adding Lessons

1. Add the `.md` file in `public/lessons/`
2. Add an entry to `metadata.json` with matching id, file, xp, exercise_count
   (`xp` must equal the sum of the exercise blocks' xp; `exercise_count` the block count)
3. Embed exercise blocks as `<!-- exercise ... -->` HTML comments in the markdown
4. Use `sandbox_setup` array for file/directory creation needed by the exercise
   (runs at every lesson load, POSIX `sh`, so keep it idempotent — no brace expansion)
5. If a later exercise depends on state an earlier exercise's SOLUTION creates
   (files, git commits), give the earlier exercise a `solution_setup` array that
   recreates that state — it is replayed at lesson load only for already-completed
   exercises, so progress survives a page reload (the VM always boots pristine)
6. Exercise `expected` regexes are JS `RegExp` — no Python syntax like `(?P<name>)`
7. Don't write exercises that need real network (the VM is loopback-only);
   sshd (:22) and nginx (:80) run locally, and lab hostnames resolve via /etc/hosts

## Deployment

- **Headers required:** `Cross-Origin-Opener-Policy: same-origin` + `Cross-Origin-Embedder-Policy: require-corp` (for SharedArrayBuffer used by v86 WASM threads)
- **Subpath:** `/clitutor/` — configured via Vite `base`, Apache `.htaccess`
- **Assets:** `public/v86/` contains libv86.js, v86.wasm, seabios.bin, vgabios.bin, rootfs flat files, alpine-fs.json, alpine-state.bin
- **State snapshot:** Pre-booted VM state for instant restore; regenerate with `npm run build-state` or `generate-state.mjs` (Puppeteer)

## Key Constraints

- **32-bit only:** v86 emulates i386 — no 64-bit binaries, use Alpine i386
- **Alpine 3.21 + GNU userland:** rootfs is `i386/alpine:3.21` with GNU
  coreutils/grep/sed/gawk/findutils/diffutils installed (see `build/build-rootfs.sh`) —
  reason about GNU output formats, not busybox
- **Root autologin:** the serial session is root (inittab agetty autologin) with a
  cosmetic `student@clitutor` prompt and `HOME=/home/student` set by the bashrc;
  if the tutor shell dies, inittab respawns a bare shell and `LinuxVM.checkRespawn`
  re-sources the bashrc automatically
- **No network:** `networkRelay` is null — loopback only; sshd and nginx run locally
- **Serial timing:** Byte-by-byte output with 4ms flush timer
- **9p limitations:** Flat file format, no hardlinks, no live mount syncing
  (symlinks DO work at runtime); v86's `read_file()` rejects for zero-byte files —
  use `SearchPath` for existence checks
- **No SIGWINCH:** Terminal resize over serial requires `stty rows N cols M` workaround
- **SharedArrayBuffer:** Requires COOP/COEP headers; won't work without them
- **v86 `read_file` empty-file quirk and `exit`-guard:** see `src/vm/linux-vm.ts` and
  `src/vm/bashrc.ts` before touching filesystem checks or the sentinel machinery
