# AGENTS.md

This repository currently uses Codex as the active coding agent.

## Primary Agent Docs
- `CODEX.md`: full project reference and architecture notes
- `CODEX_MEMORY.md`: concise continuity notes and recent decisions
- `.codex/settings.json`: baseline Codex local permissions mode
- `.codex/settings.local.json`: local allow/deny command safety rules

## Continuity Rule
When updating major flow, validation logic, lesson metadata, or VM/serial behavior:
1. Update `CODEX_MEMORY.md` with what changed and why.
2. Keep lesson changes mirrored in both:
   - `src/clitutor/lessons/`
   - `clitutor-web/public/lessons/`
3. Prefer objective-based validation that allows valid command variations.

