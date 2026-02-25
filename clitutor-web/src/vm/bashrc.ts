/** Custom bashrc for the v86 serial console — port of core/bashrc_template.py */

export const CMD_START_SENTINEL = "__CLITUTOR_CMD_START__";
export const CMD_END_SENTINEL = "__CLITUTOR_CMD_END__";
export const SENTINEL_CHAR = "\x1f";

const BLOCKED_COMMANDS = ["sudo", "su", "chroot", "mount", "umount", "fdisk", "parted"];

export function generateBashrc(
  sandboxPath: string = "/home/student",
  user: string = "student",
  hostname: string = "clitutor",
): string {
  const blockedFuncs = BLOCKED_COMMANDS.map(
    (cmd) => `${cmd}() { echo "${cmd}: not allowed in the sandbox"; return 1; }`,
  ).join("\n");

  return `# CLItutor sandbox bashrc — generated, do not edit
export HOME="${sandboxPath}"
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
export TERM="xterm-256color"

# ── Store real ESC byte for ash-compatible ANSI ─────────────
_esc=$(printf '\\033')

# ── Colored prompt (rebuilt each time via PROMPT_COMMAND) ───
PS1="\${_esc}[01;32m${user}@${hostname}\${_esc}[00m:\${_esc}[01;34m${sandboxPath}\${_esc}[00m\\$ "

# ── Colors and aliases ──────────────────────────────────────
alias ls='ls --color=auto'
alias grep='grep --color=auto'
alias fgrep='fgrep --color=auto'
alias egrep='egrep --color=auto'
alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'

export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'

# ── History settings ────────────────────────────────────────
HISTCONTROL=ignoreboth
HISTSIZE=1000

# ── CLItutor sentinel machinery ─────────────────────────────
__clitutor_prompt_cmd() {
    local rc=$?
    printf '\\x1f${CMD_END_SENTINEL}:%d:%s\\x1f' "$rc" "$PWD"
    PS1="\${_esc}[01;32m${user}@${hostname}\${_esc}[00m:\${_esc}[01;34m$PWD\${_esc}[00m\\$ "
    printf '\\x1f${CMD_START_SENTINEL}\\x1f'
}
PROMPT_COMMAND="__clitutor_prompt_cmd"

_msg() { printf '\\033[1;36m%b\\033[0m\\n' "$*"; }

# Block dangerous commands
${blockedFuncs}

# Prevent accidental Ctrl+D shell exit
set -o ignoreeof

# No history file in sandbox
unset HISTFILE

cd "${sandboxPath}"
`;
}
