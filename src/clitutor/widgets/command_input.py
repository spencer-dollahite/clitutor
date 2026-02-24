"""Command input widget with $ prompt, history, and tab-completion support."""
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

    class TabCompletionRequested(Message):
        """Posted when user presses Tab to request completion."""
        def __init__(self, text: str, cursor_pos: int) -> None:
            super().__init__()
            self.text = text
            self.cursor_pos = cursor_pos

    def __init__(self, prompt_markup: str = "$ ", **kwargs) -> None:
        super().__init__(**kwargs)
        self._history: List[str] = []
        self._history_index: int = -1
        self._completing: bool = False
        self._prompt_markup = prompt_markup

    def compose(self) -> ComposeResult:
        with Horizontal(id="command-input-container"):
            yield Label(self._prompt_markup, id="prompt-label", markup=True)
            yield Input(id="command-input")

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
        if event.key == "tab":
            event.prevent_default()
            event.stop()
            if self._completing:
                return
            self._completing = True
            self.post_message(
                self.TabCompletionRequested(inp.value, inp.cursor_position)
            )
        elif event.key == "up":
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

    def set_completion_result(self, new_value: str, cursor_pos: int) -> None:
        """Apply a tab-completion result to the input field."""
        inp = self.query_one("#command-input", Input)
        inp.value = new_value
        inp.cursor_position = cursor_pos
        self._completing = False

    def clear_completing(self) -> None:
        """Reset the completing flag (no result to apply)."""
        self._completing = False

    def focus_input(self) -> None:
        """Focus the command input field."""
        try:
            self.query_one("#command-input", Input).focus()
        except Exception:
            pass

    def update_prompt(self, markup: str) -> None:
        """Update the prompt label text at runtime."""
        self._prompt_markup = markup
        self.query_one("#prompt-label", Label).update(markup)

    def set_disabled(self, disabled: bool) -> None:
        """Enable/disable input."""
        self.query_one("#command-input", Input).disabled = disabled
