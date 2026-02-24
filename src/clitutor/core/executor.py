"""Command execution with safety measures."""
from __future__ import annotations

import os
import re
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

    def _make_env(self) -> dict:
        env = os.environ.copy()
        env["PATH"] = "/usr/local/bin:/usr/bin:/bin"
        env["HOME"] = str(self.sandbox_path)
        return env

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

    def run(self, command: str, timeout: int = DEFAULT_TIMEOUT) -> CommandResult:
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

        try:
            proc = subprocess.run(
                ["bash", "-c", command],
                cwd=str(self.sandbox_path),
                env=self._env,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return CommandResult(
                command=command,
                stdout=proc.stdout,
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

    @property
    def sandbox_path(self) -> str:
        return self._sandbox.path

    def run(self, command: str, timeout: int = DEFAULT_TIMEOUT) -> CommandResult:
        """Execute a command inside the Docker container."""
        if self._sandbox.container_name is None:
            return CommandResult(
                command=command,
                stdout="",
                stderr="Docker container not running.",
                returncode=1,
            )
        try:
            proc = subprocess.run(
                [
                    "docker", "exec",
                    "-w", self._sandbox.path,
                    self._sandbox.container_name,
                    "bash", "-c", command,
                ],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return CommandResult(
                command=command,
                stdout=proc.stdout,
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
