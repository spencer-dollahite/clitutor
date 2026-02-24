"""Tests for output validator."""
import pytest

from clitutor.core.executor import CommandResult
from clitutor.core.sandbox import SandboxManager
from clitutor.core.validator import OutputValidator
from clitutor.models.lesson import Exercise


@pytest.fixture
def sandbox():
    with SandboxManager() as sm:
        yield sm


def make_result(stdout="", stderr="", returncode=0) -> CommandResult:
    return CommandResult(
        command="test", stdout=stdout, stderr=stderr, returncode=returncode
    )


def make_exercise(**kwargs) -> Exercise:
    defaults = {
        "id": "test",
        "title": "Test",
        "xp": 10,
        "difficulty": 1,
        "validation_type": "output_contains",
        "expected": "expected",
    }
    defaults.update(kwargs)
    return Exercise(**defaults)


class TestOutputValidator:
    def test_output_contains_pass(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="output_contains", expected="hello")
        result = make_result(stdout="hello world")
        assert v.validate(ex, result).passed

    def test_output_contains_fail(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="output_contains", expected="hello")
        result = make_result(stdout="goodbye")
        assert not v.validate(ex, result).passed

    def test_output_contains_in_stderr(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="output_contains", expected="warning")
        result = make_result(stderr="warning: something")
        assert v.validate(ex, result).passed

    def test_output_equals_pass(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="output_equals", expected="hello")
        result = make_result(stdout="hello\n")
        assert v.validate(ex, result).passed

    def test_output_equals_fail(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="output_equals", expected="hello")
        result = make_result(stdout="hello world\n")
        assert not v.validate(ex, result).passed

    def test_output_regex_pass(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="output_regex", expected=r"\d{3}")
        result = make_result(stdout="status 200")
        assert v.validate(ex, result).passed

    def test_output_regex_fail(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="output_regex", expected=r"^\d+$")
        result = make_result(stdout="not a number")
        assert not v.validate(ex, result).passed

    def test_file_exists_pass(self, sandbox):
        v = OutputValidator(sandbox)
        (sandbox.path / "target.txt").write_text("data")
        ex = make_exercise(validation_type="file_exists", expected="target.txt")
        result = make_result()
        assert v.validate(ex, result).passed

    def test_file_exists_fail(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="file_exists", expected="missing.txt")
        result = make_result()
        assert not v.validate(ex, result).passed

    def test_file_contains_pass(self, sandbox):
        v = OutputValidator(sandbox)
        (sandbox.path / "out.txt").write_text("hello world")
        ex = make_exercise(
            validation_type="file_contains", expected="out.txt::hello"
        )
        result = make_result()
        assert v.validate(ex, result).passed

    def test_file_contains_fail(self, sandbox):
        v = OutputValidator(sandbox)
        (sandbox.path / "out.txt").write_text("goodbye")
        ex = make_exercise(
            validation_type="file_contains", expected="out.txt::hello"
        )
        result = make_result()
        assert not v.validate(ex, result).passed

    def test_file_contains_missing_file(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(
            validation_type="file_contains", expected="missing.txt::data"
        )
        result = make_result()
        assert not v.validate(ex, result).passed

    def test_exit_code_pass(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="exit_code", expected="0")
        result = make_result(returncode=0)
        assert v.validate(ex, result).passed

    def test_exit_code_fail(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="exit_code", expected="0")
        result = make_result(returncode=1)
        assert not v.validate(ex, result).passed

    def test_unknown_validation_type(self, sandbox):
        v = OutputValidator(sandbox)
        ex = make_exercise(validation_type="unknown_type", expected="")
        result = make_result()
        assert not v.validate(ex, result).passed
