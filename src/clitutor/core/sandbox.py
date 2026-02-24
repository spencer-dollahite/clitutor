"""Sandbox environment for safe command execution."""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import List, Optional


class SandboxManager:
    """Manages a temporary sandbox directory for command execution."""

    def __init__(self) -> None:
        self._sandbox_dir: Optional[Path] = None

    @property
    def path(self) -> Path:
        if self._sandbox_dir is None:
            raise RuntimeError("Sandbox not created. Call create() first.")
        return self._sandbox_dir

    def create(self) -> Path:
        """Create a new sandbox directory."""
        self._sandbox_dir = Path(tempfile.mkdtemp(prefix="clitutor-sandbox-"))
        return self._sandbox_dir

    def seed_files(self, file_specs: List[str]) -> None:
        """Seed the sandbox with files.

        Each spec is 'filename:content' or just 'filename' for empty file.
        """
        if self._sandbox_dir is None:
            raise RuntimeError("Sandbox not created.")
        for spec in file_specs:
            if ":" in spec:
                name, content = spec.split(":", 1)
            else:
                name, content = spec, ""
            filepath = self._sandbox_dir / name
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(content)

    def seed_asset(self, asset_name: str, dest_name: Optional[str] = None) -> None:
        """Copy a bundled asset file into the sandbox."""
        if self._sandbox_dir is None:
            raise RuntimeError("Sandbox not created.")
        assets_dir = Path(__file__).parent.parent / "assets"
        src = assets_dir / asset_name
        if src.exists():
            dest = self._sandbox_dir / (dest_name or asset_name)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    def reset(self) -> Path:
        """Destroy and recreate the sandbox."""
        self.cleanup()
        return self.create()

    def cleanup(self) -> None:
        """Remove the sandbox directory."""
        if self._sandbox_dir is not None and self._sandbox_dir.exists():
            shutil.rmtree(self._sandbox_dir, ignore_errors=True)
            self._sandbox_dir = None

    def file_exists(self, filepath: str) -> bool:
        """Check if a file exists in the sandbox."""
        if self._sandbox_dir is None:
            return False
        return (self._sandbox_dir / filepath).exists()

    def file_read(self, filepath: str) -> str:
        """Read a file's contents from the sandbox."""
        if self._sandbox_dir is None:
            raise RuntimeError("Sandbox not created.")
        target = self._sandbox_dir / filepath
        if not target.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        return target.read_text()

    def __enter__(self) -> "SandboxManager":
        self.create()
        return self

    def __exit__(self, *args) -> None:
        self.cleanup()
