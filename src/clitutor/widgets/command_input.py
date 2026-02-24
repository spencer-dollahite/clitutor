"""Command input widget with $ prompt and history."""
from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Input, Label, Static


class CommandInput(Static):
    """Input widget with $ prompt and command history (up/down arrows)."""

    class CommandSubmitted(Message):
        """Posted when user submits a command."""
        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._history: List[str] = []
        self._history_index: int = -1

    def compose(self) -> ComposeResult:
        with Horizontal(id="command-input-container"):
            yield Label("$ ", id="prompt-label")
            yield Input(
                placeholder="Type a command...",
                id="command-input",
            )

    def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip()
        if cmd:
            self._history.append(cmd)
            self._history_index = -1
            self.post_message(self.CommandSubmitted(cmd))
        event.input.value = ""

    def on_key(self, event) -> None:
        inp = self.query_one("#command-input", Input)
        if not inp.has_focus:
            return
        if event.key == "up":
            if self._history:
                if self._history_index == -1:
                    self._history_index = len(self._history) - 1
                elif self._history_index > 0:
                    self._history_index -= 1
                inp.value = self._history[self._history_index]
                inp.cursor_position = len(inp.value)
            event.prevent_default()
        elif event.key == "down":
            if self._history_index != -1:
                self._history_index += 1
                if self._history_index >= len(self._history):
                    self._history_index = -1
                    inp.value = ""
                else:
                    inp.value = self._history[self._history_index]
                    inp.cursor_position = len(inp.value)
            event.prevent_default()

    def focus_input(self) -> None:
        """Focus the command input field."""
        try:
            self.query_one("#command-input", Input).focus()
        except Exception:
            pass

    def set_disabled(self, disabled: bool) -> None:
        """Enable/disable input."""
        self.query_one("#command-input", Input).disabled = disabled
