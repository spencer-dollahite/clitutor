"""Output validation strategies for exercises."""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Union

from clitutor.core.executor import CommandResult
from clitutor.models.lesson import Exercise


@dataclass
class ValidationResult:
    """Result of validating a command against an exercise."""
    passed: bool
    message: str = ""


class OutputValidator:
    """Validates command results against exercise expectations."""

    def __init__(
        self,
        sandbox: Union["SandboxManager", "DockerSandbox", object],
        executor: object = None,
    ) -> None:
        self._sandbox = sandbox
        self._executor = executor

    def validate(self, exercise: Exercise, result: CommandResult) -> ValidationResult:
        """Validate a command result against an exercise's expectations."""
        vtype = exercise.validation_type
        expected = exercise.expected

        dispatch = {
            "output_equals": self._check_output_equals,
            "output_contains": self._check_output_contains,
            "output_regex": self._check_output_regex,
            "exit_code": self._check_exit_code,
        }

        if vtype == "file_exists":
            return self._check_file_exists(expected)
        elif vtype == "file_contains":
            return self._check_file_contains(expected)
        elif vtype == "dir_with_file":
            return self._check_dir_with_file(expected)
        elif vtype == "any_file_contains":
            return self._check_any_file_contains(expected)
        elif vtype in dispatch:
            return dispatch[vtype](result, expected)
        else:
            return ValidationResult(False, f"Unknown validation type: {vtype}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _cwd_relative_path(self, filepath: str) -> str | None:
        """Return the sandbox-relative version of filepath based on executor cwd."""
        if not self._executor:
            return None
        cwd = self._executor.cwd
        sandbox_root = str(self._sandbox.path)
        if cwd == sandbox_root:
            return None
        try:
            rel_cwd = os.path.relpath(cwd, sandbox_root)
            return os.path.join(rel_cwd, filepath)
        except ValueError:
            return None

    # ------------------------------------------------------------------
    # Validation methods
    # ------------------------------------------------------------------

    def _check_output_equals(self, result: CommandResult, expected: str) -> ValidationResult:
        actual = result.stdout.strip()
        if actual == expected.strip():
            return ValidationResult(True, "Correct!")
        return ValidationResult(False, "Output doesn't match expected result.")

    def _check_output_contains(self, result: CommandResult, expected: str) -> ValidationResult:
        combined = result.stdout + result.stderr
        if expected.strip() in combined:
            return ValidationResult(True, "Correct!")
        return ValidationResult(False, "Output doesn't contain expected text.")

    def _check_output_regex(self, result: CommandResult, expected: str) -> ValidationResult:
        combined = result.stdout + result.stderr
        if re.search(expected, combined):
            return ValidationResult(True, "Correct!")
        return ValidationResult(False, "Output doesn't match expected pattern.")

    def _check_file_exists(self, expected: str) -> ValidationResult:
        if self._sandbox.file_exists(expected):
            return ValidationResult(True, "Correct! File created.")
        # Fallback: check relative to executor's cwd
        alt = self._cwd_relative_path(expected)
        if alt and self._sandbox.file_exists(alt):
            return ValidationResult(True, "Correct! File created.")
        return ValidationResult(False, f"File '{expected}' not found.")

    def _check_file_contains(self, expected: str) -> ValidationResult:
        """Expected format: 'filename::content'"""
        if "::" not in expected:
            return ValidationResult(False, "Invalid file_contains spec.")
        filename, content = expected.split("::", 1)
        filename = filename.strip()

        # Try sandbox root first
        if self._sandbox.file_exists(filename):
            file_content = self._sandbox.file_read(filename)
            if content.strip() in file_content:
                return ValidationResult(True, "Correct! File contains expected content.")
            return ValidationResult(False, "File doesn't contain expected content.")

        # Fallback: check relative to executor's cwd
        alt = self._cwd_relative_path(filename)
        if alt and self._sandbox.file_exists(alt):
            file_content = self._sandbox.file_read(alt)
            if content.strip() in file_content:
                return ValidationResult(True, "Correct! File contains expected content.")
            return ValidationResult(False, "File doesn't contain expected content.")

        return ValidationResult(False, f"File '{filename}' not found.")

    def _check_dir_with_file(self, expected: str) -> ValidationResult:
        """Check that at least one subdirectory contains a file."""
        if self._sandbox.has_dir_with_file():
            return ValidationResult(True, "Correct! Directory with file created.")
        return ValidationResult(
            False,
            "No directory containing a file was found. "
            "Create a directory and then create a file inside it.",
        )

    def _check_any_file_contains(self, expected: str) -> ValidationResult:
        """Check that any file in the sandbox contains the expected content."""
        if self._sandbox.find_file_containing(expected.strip()):
            return ValidationResult(True, "Correct! File contains expected content.")
        return ValidationResult(
            False,
            f"No file found containing '{expected.strip()}'.",
        )

    def _check_exit_code(self, result: CommandResult, expected: str) -> ValidationResult:
        try:
            expected_code = int(expected.strip())
        except ValueError:
            return ValidationResult(False, "Invalid expected exit code.")
        if result.returncode == expected_code:
            return ValidationResult(True, "Correct!")
        return ValidationResult(False, f"Expected exit code {expected_code}, got {result.returncode}.")
