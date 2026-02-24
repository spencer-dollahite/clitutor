"""Tests for sandbox management."""
import os
from pathlib import Path

import pytest

from clitutor.core.sandbox import SandboxManager


class TestSandboxManager:
    def test_create_and_cleanup(self):
        sm = SandboxManager()
        path = sm.create()
        assert path.exists()
        assert "clitutor-sandbox" in str(path)
        sm.cleanup()
        assert not path.exists()

    def test_context_manager(self):
        with SandboxManager() as sm:
            path = sm.path
            assert path.exists()
        assert not path.exists()

    def test_path_raises_before_create(self):
        sm = SandboxManager()
        with pytest.raises(RuntimeError, match="Sandbox not created"):
            _ = sm.path

    def test_seed_files(self):
        with SandboxManager() as sm:
            sm.seed_files(["test.txt:hello world", "empty.txt"])
            assert (sm.path / "test.txt").read_text() == "hello world"
            assert (sm.path / "empty.txt").read_text() == ""

    def test_seed_nested_files(self):
        with SandboxManager() as sm:
            sm.seed_files(["sub/dir/file.txt:nested content"])
            assert (sm.path / "sub" / "dir" / "file.txt").read_text() == "nested content"

    def test_reset(self):
        sm = SandboxManager()
        path1 = sm.create()
        (path1 / "file.txt").write_text("data")
        path2 = sm.reset()
        assert not path1.exists()
        assert path2.exists()
        assert not (path2 / "file.txt").exists()
        sm.cleanup()

    def test_seed_files_raises_before_create(self):
        sm = SandboxManager()
        with pytest.raises(RuntimeError, match="Sandbox not created"):
            sm.seed_files(["test.txt"])

    def test_cleanup_idempotent(self):
        sm = SandboxManager()
        sm.create()
        sm.cleanup()
        sm.cleanup()  # Should not raise
