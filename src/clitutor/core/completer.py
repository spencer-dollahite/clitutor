"""Bash-style tab completion helpers.

Stateless functions that build compgen commands, parse their output,
and apply completions to an input line.  No Textual dependency.
"""
from __future__ import annotations

import shlex
from os.path import commonprefix
from typing import List, Optional, Tuple


def build_compgen_command(input_text: str, cursor_pos: int) -> Optional[str]:
    """Return a bash compgen command string, or *None* if nothing to complete.

    * First-word position → ``compgen -c`` (command names).
    * Argument position   → ``compgen -f`` (file paths).
    * Empty / whitespace-only input → ``None``.
    """
    text = input_text[:cursor_pos]
    if not text or text.isspace():
        return None

    # Split respecting shell quoting; on unterminated quotes fall back to
    # simple whitespace split so we still get a usable prefix.
    try:
        parts = shlex.split(text)
    except ValueError:
        parts = text.split()

    # If the text ends with whitespace the user wants to complete a *new*
    # (empty) argument — compgen -f with no prefix lists all files.
    trailing_space = text[-1] == " "

    if trailing_space:
        # New argument position: complete files with empty prefix
        return "compgen -f -- ''"
    elif len(parts) == 1:
        # Still typing the very first word → complete commands
        prefix = _shell_escape(parts[0])
        return f"compgen -c -- '{prefix}'"
    else:
        # Completing an argument
        prefix = _shell_escape(parts[-1])
        return f"compgen -f -- '{prefix}'"


def parse_completions(stdout: str) -> List[str]:
    """Parse compgen output into a sorted, deduplicated list."""
    seen: set[str] = set()
    result: List[str] = []
    for line in stdout.splitlines():
        entry = line.strip()
        if entry and entry not in seen:
            seen.add(entry)
            result.append(entry)
    result.sort()
    return result


def compute_common_prefix(matches: List[str]) -> str:
    """Return the longest common prefix shared by all *matches*."""
    if not matches:
        return ""
    return commonprefix(matches)


def apply_completion(
    input_text: str,
    cursor_pos: int,
    replacement: str,
) -> Tuple[str, int]:
    """Replace the token under the cursor with *replacement*.

    Returns ``(new_text, new_cursor_pos)``.
    """
    text = input_text[:cursor_pos]

    # Find the start of the current token (walk backwards past non-space).
    token_start = len(text)
    while token_start > 0 and text[token_start - 1] != " ":
        token_start -= 1

    after_cursor = input_text[cursor_pos:]
    new_text = text[:token_start] + replacement + after_cursor
    new_cursor = token_start + len(replacement)
    return new_text, new_cursor


# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------

def _shell_escape(s: str) -> str:
    """Escape single quotes for embedding inside a single-quoted bash string."""
    return s.replace("'", "'\\''")
