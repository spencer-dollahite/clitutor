"""Tests for command executor."""
import pytest

from clitutor.core.executor import CommandExecutor, BLOCKED_COMMANDS
from clitutor.core.sandbox import SandboxManager


@pytest.fixture
def executor():
    with SandboxManager() as sm:
        yield CommandExecutor(sm.path)


class TestCommandExecutor:
    def test_simple_command(self, executor):
        result = executor.run("echo hello")
        assert result.stdout.strip() == "hello"
        assert result.returncode == 0
        assert not result.blocked
        assert not result.timed_out

    def test_ls_command(self, executor):
        # Create a file in sandbox first
        (executor.sandbox_path / "test.txt").write_text("data")
        result = executor.run("ls")
        assert "test.txt" in result.stdout

    def test_command_in_sandbox_dir(self, executor):
        result = executor.run("pwd")
        assert str(executor.sandbox_path) in result.stdout

    def test_blocked_sudo(self, executor):
        result = executor.run("sudo ls")
        assert result.blocked
        assert result.returncode == 1
        assert "not allowed" in result.stderr

    def test_blocked_su(self, executor):
        result = executor.run("su root")
        assert result.blocked

    def test_blocked_fork_bomb(self, executor):
        result = executor.run(":(){ :|:& };:")
        assert result.blocked

    def test_blocked_rm_rf_root(self, executor):
        result = executor.run("rm -rf /")
        assert result.blocked

    def test_timeout(self, executor):
        result = executor.run("sleep 5", timeout=1)
        assert result.timed_out
        assert result.returncode == 1

    def test_nonzero_exit_code(self, executor):
        result = executor.run("ls /nonexistent_directory_12345")
        assert result.returncode != 0
        assert result.stderr != ""

    def test_stderr_capture(self, executor):
        result = executor.run("echo error >&2")
        assert "error" in result.stderr

    def test_check_safety_returns_none_for_safe(self, executor):
        assert executor.check_safety("ls -la") is None
        assert executor.check_safety("echo hello") is None
        assert executor.check_safety("cat file.txt") is None

    def test_check_safety_returns_reason_for_blocked(self, executor):
        for cmd in BLOCKED_COMMANDS:
            reason = executor.check_safety(f"{cmd} something")
            assert reason is not None

    def test_pipe_commands(self, executor):
        (executor.sandbox_path / "data.txt").write_text("a\nb\nc\na\nb\na\n")
        result = executor.run("sort data.txt | uniq -c | sort -rn")
        assert "3" in result.stdout  # 'a' appears 3 times
