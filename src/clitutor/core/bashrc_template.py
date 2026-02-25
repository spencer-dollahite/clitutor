"""Generate a custom bashrc for the PTY sandbox session."""
from __future__ import annotations

import textwrap

# Sentinels use \x1f (Unit Separator) framing — non-printable, won't appear in
# normal output.  The PTY terminal widget strips them before pyte sees them.
CMD_START_SENTINEL = "__CLITUTOR_CMD_START__"
CMD_END_SENTINEL = "__CLITUTOR_CMD_END__"
SENTINEL_CHAR = "\x1f"

BLOCKED_COMMANDS = ("sudo", "su", "chroot", "mount", "umount", "fdisk", "parted")


def generate_bashrc(
    sandbox_path: str,
    user: str = "student",
    hostname: str = "clitutor",
) -> str:
    """Return bashrc content that instruments bash for sentinel-based capture."""
    blocked_funcs = "\n".join(
        f'{cmd}() {{ echo "{cmd}: not allowed in the sandbox"; return 1; }}'
        for cmd in BLOCKED_COMMANDS
    )

    return textwrap.dedent(f"""\
        # CLItutor sandbox bashrc — generated, do not edit
        export HOME="{sandbox_path}"
        export PATH="/usr/local/bin:/usr/bin:/bin"
        export TERM="xterm-256color"

        # ── Colored prompt ──────────────────────────────────────────
        export PS1='\\[\\033[01;32m\\]{user}@{hostname}\\[\\033[00m\\]:\\[\\033[01;34m\\]\\w\\[\\033[00m\\]\\$ '

        # ── Colors and aliases ──────────────────────────────────────
        alias ls='ls --color=auto'
        alias grep='grep --color=auto'
        alias fgrep='fgrep --color=auto'
        alias egrep='egrep --color=auto'
        alias ll='ls -alF'
        alias la='ls -A'
        alias l='ls -CF'

        # colored GCC warnings and errors
        export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

        # ── History settings ────────────────────────────────────────
        HISTCONTROL=ignoreboth
        HISTSIZE=1000
        shopt -s histappend

        # check the window size after each command
        shopt -s checkwinsize

        # make less friendlier for non-text input files
        [ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

        # enable programmable completion if available
        if [ -f /etc/bash_completion ] && ! shopt -oq posix; then
            . /etc/bash_completion
        fi

        # ── CLItutor sentinel machinery ─────────────────────────────
        # Emit sentinel before each command executes
        PS0=$'\\x1f{CMD_START_SENTINEL}\\x1f'

        # Emit sentinel after each command completes (with exit code and cwd)
        __clitutor_prompt_cmd() {{
            local rc=$?
            printf '\\x1f{CMD_END_SENTINEL}:%d:%s\\x1f' "$rc" "$PWD"
        }}
        PROMPT_COMMAND="__clitutor_prompt_cmd"

        # Internal helper for system messages (called by the TUI, not the user)
        _msg() {{ printf '\\033[1;36m%b\\033[0m\\n' "$*"; }}

        # Block dangerous commands
        {blocked_funcs}

        # Prevent accidental Ctrl+D shell exit
        set -o ignoreeof

        # No history file in sandbox
        unset HISTFILE

        cd "{sandbox_path}"
    """)
