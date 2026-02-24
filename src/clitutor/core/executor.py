"""Command execution with safety measures."""
from __future__ import annotations

import os
import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from clitutor.core.docker_sandbox import DockerSandbox

BLACKLIST_PATTERNS = [
    r"rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?/\s*$",
    r"rm\s+-[a-zA-Z]*f[a-zA-Z]*\s+/",
    r":\(\)\{.*\}",
    r"mkfs\.",
    r"dd\s+.*of=/dev/",
    r">\s*/dev/sd",
    r"chmod\s+(-R\s+)?777\s+/",
    r"curl.*\|\s*(ba)?sh",
    r"wget.*\|\s*(ba)?sh",
    r"shutdown",
    r"reboot",
    r"init\s+[06]",
    r"systemctl\s+(halt|poweroff|reboot)",
]

BLOCKED_COMMANDS = {"sudo", "su", "chroot", "mount", "umount", "fdisk", "parted"}

DEFAULT_TIMEOUT = 10

_CWD_SENTINEL = "\x1f__CLITUTOR_CWD__:"


def _format_prompt_markup(
    cwd: str, home: str, user: str = "student", hostname: str = "clitutor"
) -> str:
    """Return Rich markup for a bash-style prompt."""
    display_cwd = cwd
    if cwd == home:
        display_cwd = "~"
    elif cwd.startswith(home + "/"):
        display_cwd = "~/" + cwd[len(home) + 1 :]
    return (
        f"[bold green]{user}@{hostname}[/]"
        f":[bold blue]{display_cwd}[/]$ "
    )


def _parse_cwd(raw_stdout: str, fallback: str) -> tuple[str, str]:
    """Extract the CWD from command output and return (clean_stdout, new_cwd)."""
    idx = raw_stdout.rfind(_CWD_SENTINEL)
    if idx == -1:
        return raw_stdout, fallback
    clean = raw_stdout[:idx]
    new_cwd = raw_stdout[idx + len(_CWD_SENTINEL) :].strip()
    return clean, new_cwd if new_cwd else fallback


def _wrap_command(command: str, cwd: str, sandbox_root: str, track_cwd: bool) -> str:
    """Wrap a user command so it runs in the tracked cwd and optionally reports the new cwd."""
    quoted_cwd = shlex.quote(cwd)
    quoted_root = shlex.quote(sandbox_root)
    parts = [f"cd {quoted_cwd} 2>/dev/null || cd {quoted_root}"]
    parts.append(command)
    if track_cwd:
        parts.append(
            f"__rc=$?; printf '\\x1f__CLITUTOR_CWD__:%s' \"$(pwd)\"; exit $__rc"
        )
    return "; ".join(parts)


@dataclass
class CommandResult:
    """Result of a command execution."""
    command: str
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool = False
    blocked: bool = False
    block_reason: str = ""


class CommandExecutor:
    """Executes commands safely in a sandbox directory."""

    def __init__(self, sandbox_path: Path) -> None:
        self.sandbox_path = sandbox_path
        self._env = self._make_env()
        self._home = str(sandbox_path)
        self._cwd = str(sandbox_path)
        self._user = "student"
        self._hostname = "clitutor"

    def _make_env(self) -> dict:
        env = os.environ.copy()
        env["PATH"] = "/usr/local/bin:/usr/bin:/bin"
        env["HOME"] = str(self.sandbox_path)
        return env

    @property
    def cwd(self) -> str:
        return self._cwd

    @property
    def prompt_markup(self) -> str:
        return _format_prompt_markup(
            self._cwd, self._home, self._user, self._hostname
        )

    def reset_cwd(self) -> None:
        """Reset cwd to the sandbox root."""
        self._cwd = str(self.sandbox_path)

    def check_safety(self, command: str) -> Optional[str]:
        """Check if a command is safe. Returns reason if blocked, None if safe."""
        cmd_stripped = command.strip()

        first_word = cmd_stripped.split()[0] if cmd_stripped.split() else ""
        if first_word in BLOCKED_COMMANDS:
            return f"'{first_word}' is not allowed in the sandbox."

        for pattern in BLACKLIST_PATTERNS:
            if re.search(pattern, cmd_stripped):
                return "This command pattern is blocked for safety."

        return None

    def run(
        self, command: str, timeout: int = DEFAULT_TIMEOUT, track_cwd: bool = True
    ) -> CommandResult:
        """Execute a command in the sandbox."""
        reason = self.check_safety(command)
        if reason:
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Blocked: {reason}",
                returncode=1,
                blocked=True,
                block_reason=reason,
            )

        wrapped = _wrap_command(
            command, self._cwd, str(self.sandbox_path), track_cwd
        )

        try:
            proc = subprocess.run(
                ["bash", "-c", wrapped],
                cwd=str(self.sandbox_path),
                env=self._env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = proc.stdout
            if track_cwd:
                stdout, new_cwd = _parse_cwd(stdout, self._cwd)
                self._cwd = new_cwd
            return CommandResult(
                command=command,
                stdout=stdout,
                stderr=proc.stderr,
                returncode=proc.returncode,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds.",
                returncode=1,
                timed_out=True,
            )
        except Exception as e:
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Error: {e}",
                returncode=1,
            )


class DockerExecutor:
    """Executes commands inside a Docker sandbox container."""

    def __init__(self, sandbox: DockerSandbox) -> None:
        self._sandbox = sandbox
        self._home = sandbox.path
        self._cwd = sandbox.path
        self._user = "student"
        self._hostname = "clitutor"

    @property
    def sandbox_path(self) -> str:
        return self._sandbox.path

    @property
    def cwd(self) -> str:
        return self._cwd

    @property
    def prompt_markup(self) -> str:
        return _format_prompt_markup(
            self._cwd, self._home, self._user, self._hostname
        )

    def reset_cwd(self) -> None:
        """Reset cwd to the sandbox root."""
        self._cwd = self._sandbox.path

    def run(
        self, command: str, timeout: int = DEFAULT_TIMEOUT, track_cwd: bool = True
    ) -> CommandResult:
        """Execute a command inside the Docker container."""
        if self._sandbox.container_name is None:
            return CommandResult(
                command=command,
                stdout="",
                stderr="Docker container not running.",
                returncode=1,
            )

        wrapped = _wrap_command(
            command, self._cwd, self._sandbox.path, track_cwd
        )

        try:
            proc = subprocess.run(
                [
                    "docker", "exec",
                    "-w", self._sandbox.path,
                    self._sandbox.container_name,
                    "bash", "-c", wrapped,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            stdout = proc.stdout
            if track_cwd:
                stdout, new_cwd = _parse_cwd(stdout, self._cwd)
                self._cwd = new_cwd
            return CommandResult(
                command=command,
                stdout=stdout,
                stderr=proc.stderr,
                returncode=proc.returncode,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Command timed out after {timeout} seconds.",
                returncode=1,
                timed_out=True,
            )
        except Exception as e:
            return CommandResult(
                command=command,
                stdout="",
                stderr=f"Error: {e}",
                returncode=1,
            )
