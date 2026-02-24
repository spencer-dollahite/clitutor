"""Markdown content pane for lesson display."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Markdown, Static


class MarkdownPane(Static):
    """Scrollable markdown viewer for lesson content."""

    def __init__(self, content: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._content = content

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="lesson-scroll"):
            yield Markdown(self._content, id="lesson-markdown")

    def update_content(self, content: str) -> None:
        """Update the displayed markdown content."""
        self._content = content
        try:
            md = self.query_one("#lesson-markdown", Markdown)
            md.update(content)
        except Exception:
            pass
