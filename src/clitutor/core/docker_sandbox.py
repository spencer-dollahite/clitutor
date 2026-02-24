"""Docker-based sandbox for fully isolated command execution."""
from __future__ import annotations

import shutil
import subprocess
import uuid
from pathlib import Path
from typing import List, Optional


IMAGE_NAME = "clitutor-sandbox"
SANDBOX_DIR = "/home/student/sandbox"


class DockerSandbox:
    """Manages a Docker container as a disposable sandbox environment."""

    def __init__(self) -> None:
        self._container_name: Optional[str] = None

    @property
    def path(self) -> str:
        """Return the sandbox path inside the container."""
        return SANDBOX_DIR

    @property
    def container_name(self) -> Optional[str]:
        return self._container_name

    def create(self) -> str:
        """Create and start a new sandbox container.

        Auto-builds the image if it doesn't exist.
        """
        self._ensure_image()
        name = f"clitutor-{uuid.uuid4().hex[:12]}"
        subprocess.run(
            [
                "docker", "run", "-d",
                "--name", name,
                "--hostname", "clitutor",
                "--network", "none",
                IMAGE_NAME,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        self._container_name = name
        return SANDBOX_DIR

    def seed_files(self, file_specs: List[str]) -> None:
        """Seed the sandbox with files.

        Each spec is 'filename:content' or just 'filename' for empty file.
        """
        if self._container_name is None:
            raise RuntimeError("Container not created. Call create() first.")
        for spec in file_specs:
            if ":" in spec:
                name, content = spec.split(":", 1)
            else:
                name, content = spec, ""
            # Ensure parent directory exists, then write file
            parent = str(Path(SANDBOX_DIR) / Path(name).parent)
            self._exec(f"mkdir -p {parent}")
            filepath = f"{SANDBOX_DIR}/{name}"
            # Use printf to handle special characters
            self._exec(f"printf '%s' {_shell_quote(content)} > {filepath}")

    def seed_asset(self, asset_name: str, dest_name: Optional[str] = None) -> None:
        """Copy a bundled asset file into the sandbox container."""
        if self._container_name is None:
            raise RuntimeError("Container not created. Call create() first.")
        assets_dir = Path(__file__).parent.parent / "assets"
        src = assets_dir / asset_name
        if src.exists():
            dest = f"{SANDBOX_DIR}/{dest_name or asset_name}"
            subprocess.run(
                ["docker", "cp", str(src), f"{self._container_name}:{dest}"],
                capture_output=True,
                text=True,
                check=True,
            )
            # Fix ownership
            self._exec(f"sudo chown student:student {dest}")

    def reset(self) -> str:
        """Clear sandbox contents without restarting the container."""
        if self._container_name is None:
            raise RuntimeError("Container not created. Call create() first.")
        self._exec(f"rm -rf {SANDBOX_DIR}/* {SANDBOX_DIR}/.[!.]* {SANDBOX_DIR}/..?*")
        return SANDBOX_DIR

    def cleanup(self) -> None:
        """Stop and remove the container."""
        if self._container_name is not None:
            subprocess.run(
                ["docker", "rm", "-f", self._container_name],
                capture_output=True,
                text=True,
            )
            self._container_name = None

    def file_exists(self, filepath: str) -> bool:
        """Check if a file exists inside the container."""
        if self._container_name is None:
            return False
        result = subprocess.run(
            [
                "docker", "exec", self._container_name,
                "test", "-e", f"{SANDBOX_DIR}/{filepath}",
            ],
            capture_output=True,
        )
        return result.returncode == 0

    def file_read(self, filepath: str) -> str:
        """Read a file's contents from inside the container."""
        if self._container_name is None:
            raise RuntimeError("Container not created.")
        result = subprocess.run(
            [
                "docker", "exec", self._container_name,
                "cat", f"{SANDBOX_DIR}/{filepath}",
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise FileNotFoundError(f"File not found in container: {filepath}")
        return result.stdout

    def _exec(self, command: str, user: str = "student") -> subprocess.CompletedProcess:
        """Run a command inside the container."""
        return subprocess.run(
            [
                "docker", "exec",
                "-u", user,
                "-w", SANDBOX_DIR,
                self._container_name,
                "bash", "-c", command,
            ],
            capture_output=True,
            text=True,
        )

    def _ensure_image(self) -> None:
        """Build the Docker image if it doesn't already exist."""
        result = subprocess.run(
            ["docker", "images", "-q", IMAGE_NAME],
            capture_output=True,
            text=True,
        )
        if not result.stdout.strip():
            dockerfile_dir = Path(__file__).parent.parent.parent.parent / "docker"
            if not dockerfile_dir.exists():
                # Try installed package location fallback
                dockerfile_dir = Path(shutil.which("docker") or "").parent.parent / "docker"
            subprocess.run(
                ["docker", "build", "-t", IMAGE_NAME, str(dockerfile_dir)],
                check=True,
            )

    def __enter__(self) -> "DockerSandbox":
        self.create()
        return self

    def __exit__(self, *args) -> None:
        self.cleanup()


def _shell_quote(s: str) -> str:
    """Single-quote a string for safe shell usage."""
    return "'" + s.replace("'", "'\\''") + "'"
