"""Terminal pane - RichLog output + command input + executor integration."""
from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import RichLog, Static
from textual import work

from clitutor.core.completer import (
    apply_completion,
    build_compgen_command,
    compute_common_prefix,
    parse_completions,
)
from clitutor.core.executor import CommandResult
from clitutor.widgets.command_input import CommandInput


class TerminalPane(Vertical):
    """Terminal-like pane with scrollable output and command input."""

    class CommandCompleted(Message):
        """Posted when a command finishes execution."""
        def __init__(self, result: CommandResult) -> None:
            super().__init__()
            self.result = result

    def __init__(self, executor, **kwargs) -> None:
        super().__init__(**kwargs)
        self.executor = executor

    def compose(self) -> ComposeResult:
        yield RichLog(highlight=True, markup=True, wrap=True, id="terminal-output")
        yield CommandInput(id="cmd-input-widget")

    def on_mount(self) -> None:
        log = self.query_one("#terminal-output", RichLog)
        log.write("[bold green]CLItutor Sandbox Terminal[/]")
        log.write(f"[dim]cwd: {self.executor.sandbox_path}[/]")
        log.write("[dim]Type commands below. Use /hint, /reset, /skip, /lessons, /quit.[/]")
        log.write("")
        # Ensure the input gets focus
        self.set_timer(0.1, self._focus_input)

    def _focus_input(self) -> None:
        self.query_one(CommandInput).focus_input()

    # ------------------------------------------------------------------
    # Command execution
    # ------------------------------------------------------------------

    def on_command_input_command_submitted(self, event: CommandInput.CommandSubmitted) -> None:
        """Handle submitted commands."""
        cmd = event.command

        # Slash commands bubble up to LessonScreen
        if cmd.startswith("/"):
            self.post_message(SlashCommand(cmd))
            return

        # Echo command in output
        log = self.query_one("#terminal-output", RichLog)
        log.write(f"[green bold]$ {cmd}[/]")

        # Disable input while running
        self.query_one(CommandInput).set_disabled(True)

        # Execute in background thread
        self._run_command(cmd)

    @work(thread=True)
    def _run_command(self, command: str) -> None:
        """Run command in background thread."""
        result = self.executor.run(command)
        self.app.call_from_thread(self._display_result, result)

    def _display_result(self, result: CommandResult) -> None:
        """Display command result and re-enable input."""
        log = self.query_one("#terminal-output", RichLog)

        if result.stdout:
            for line in result.stdout.rstrip("\n").split("\n"):
                log.write(line)
        if result.stderr:
            style = "[red]" if result.returncode != 0 else "[yellow]"
            for line in result.stderr.rstrip("\n").split("\n"):
                log.write(f"{style}{line}[/]")
        log.write("")

        # Re-enable and refocus input
        self.query_one(CommandInput).set_disabled(False)
        self.query_one(CommandInput).focus_input()

        # Notify parent
        self.post_message(self.CommandCompleted(result))

    # ------------------------------------------------------------------
    # Tab completion
    # ------------------------------------------------------------------

    def on_command_input_tab_completion_requested(
        self, event: CommandInput.TabCompletionRequested
    ) -> None:
        """Kick off tab completion in a background thread."""
        self._resolve_tab_completion(event.text, event.cursor_pos)

    @work(thread=True)
    def _resolve_tab_completion(self, text: str, cursor_pos: int) -> None:
        """Build a compgen command, execute it, and relay results to the main thread."""
        cmd = build_compgen_command(text, cursor_pos)
        if cmd is None:
            self.app.call_from_thread(self._apply_tab_completion, text, cursor_pos, [])
            return

        result = self.executor.run(cmd, timeout=3)
        matches = parse_completions(result.stdout) if result.returncode == 0 else []
        self.app.call_from_thread(self._apply_tab_completion, text, cursor_pos, matches)

    def _apply_tab_completion(
        self, text: str, cursor_pos: int, matches: List[str]
    ) -> None:
        """Apply completion results on the main thread."""
        cmd_input = self.query_one(CommandInput)

        if not matches:
            self.app.bell()
            cmd_input.clear_completing()
            return

        if len(matches) == 1:
            new_text, new_pos = apply_completion(text, cursor_pos, matches[0])
            # Append a trailing space like bash does for unique completions
            new_text = new_text[:new_pos] + " " + new_text[new_pos:]
            new_pos += 1
            cmd_input.set_completion_result(new_text, new_pos)
            return

        # Multiple matches — try to extend with common prefix
        prefix = compute_common_prefix(matches)
        # Determine the current partial token to see if we can extend
        token_text = text[:cursor_pos]
        token_start = len(token_text)
        while token_start > 0 and token_text[token_start - 1] != " ":
            token_start -= 1
        current_token = token_text[token_start:]

        if len(prefix) > len(current_token):
            new_text, new_pos = apply_completion(text, cursor_pos, prefix)
            cmd_input.set_completion_result(new_text, new_pos)
        else:
            # Cannot extend further — show all matches
            cmd_input.clear_completing()
            self._display_completions(matches)

    def _display_completions(self, matches: List[str]) -> None:
        """Show completion candidates in the terminal output as columns."""
        log = self.query_one("#terminal-output", RichLog)

        # Compute column layout (aim for ~80-char terminal width)
        width = 80
        col_width = max(len(m) for m in matches) + 2
        cols = max(width // col_width, 1)

        lines: list[str] = []
        row: list[str] = []
        for i, match in enumerate(matches):
            row.append(match.ljust(col_width))
            if len(row) == cols:
                lines.append("".join(row))
                row = []
        if row:
            lines.append("".join(row))

        for line in lines:
            log.write(f"[cyan]{line}[/]")

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def write_system_message(self, text: str) -> None:
        """Write a system message to the terminal output."""
        log = self.query_one("#terminal-output", RichLog)
        log.write(f"[bold cyan]{text}[/]")

    def focus_input(self) -> None:
        self.query_one(CommandInput).focus_input()


class SlashCommand(Message):
    """A slash command entered by the user."""
    def __init__(self, command: str) -> None:
        super().__init__()
        self.command = command
