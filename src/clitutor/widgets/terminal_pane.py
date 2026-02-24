"""Terminal pane - RichLog output + command input + executor integration."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import RichLog, Static
from textual import work

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
