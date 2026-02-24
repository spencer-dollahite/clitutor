"""Hint overlay - 3-level progressive hint modal."""
from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Label, Markdown, Static


class HintOverlay(ModalScreen[None]):
    """Modal showing progressive hints for the current exercise."""

    BINDINGS = [
        ("escape", "dismiss_hint", "Close"),
        ("n", "next_hint", "Next Hint"),
    ]

    def __init__(
        self,
        hints: List[str],
        hints_shown: int = 0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._hints = hints
        self._hints_shown = min(hints_shown, len(hints))

    def compose(self) -> ComposeResult:
        with Vertical(id="hint-dialog"):
            yield Label(f" Hint ({self._hints_shown}/{len(self._hints)}) ", id="hint-title")
            if self._hints_shown == 0:
                yield Label("[dim]Press [bold]n[/bold] to reveal the first hint.[/]", id="hint-content")
            else:
                hint_text = ""
                labels = ["Nudge", "Guidance", "Almost the answer"]
                for i in range(self._hints_shown):
                    level = labels[i] if i < len(labels) else f"Hint {i + 1}"
                    hint_text += f"**{level}:** {self._hints[i]}\n\n"
                if self._hints_shown < len(self._hints):
                    hint_text += "*Press `n` for more hints (XP penalty increases)*"
                else:
                    hint_text += "*No more hints available*"
                yield Markdown(hint_text, id="hint-content")
            yield Label("[dim]ESC to close | n for next hint[/]", id="hint-footer")

    def action_dismiss_hint(self) -> None:
        self.dismiss(None)

    def action_next_hint(self) -> None:
        if self._hints_shown < len(self._hints):
            self._hints_shown += 1
            self._refresh_content()

    def _refresh_content(self) -> None:
        """Refresh the hint content display."""
        title = self.query_one("#hint-title", Label)
        title.update(f" Hint ({self._hints_shown}/{len(self._hints)}) ")

        content = self.query_one("#hint-content")
        labels = ["Nudge", "Guidance", "Almost the answer"]
        hint_text = ""
        for i in range(self._hints_shown):
            level = labels[i] if i < len(labels) else f"Hint {i + 1}"
            hint_text += f"**{level}:** {self._hints[i]}\n\n"
        if self._hints_shown < len(self._hints):
            hint_text += "*Press `n` for more hints (XP penalty increases)*"
        else:
            hint_text += "*No more hints available*"

        if isinstance(content, Markdown):
            content.update(hint_text)
        elif isinstance(content, Label):
            # Replace label with Markdown on first hint reveal
            content.remove()
            md = Markdown(hint_text, id="hint-content")
            dialog = self.query_one("#hint-dialog")
            footer = self.query_one("#hint-footer")
            dialog.mount(md, before=footer)

    @property
    def hints_shown(self) -> int:
        return self._hints_shown
