"""Lesson browser widget - ListView with status icons."""
from __future__ import annotations

from typing import List, Set

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Label, ListItem, ListView, Static

from clitutor.models.lesson import LessonMeta


class LessonItem(ListItem):
    """A single lesson entry in the browser."""

    def __init__(self, meta: LessonMeta, completed: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.meta = meta
        self.completed = completed

    def compose(self) -> ComposeResult:
        icon = "[green]✓[/]" if self.completed else "[dim]○[/]"
        diff_stars = "[yellow]" + ("★" * self.meta.difficulty) + ("☆" * (5 - self.meta.difficulty)) + "[/]"
        yield Label(
            f" {icon}  {self.meta.order:02d}. {self.meta.title}  {diff_stars}  [dim]{self.meta.xp} XP[/]",
            markup=True,
        )


class LessonBrowser(Static):
    """Browsable list of all lessons with completion status."""

    class LessonSelected(Message):
        """Posted when a lesson is selected."""
        def __init__(self, meta: LessonMeta) -> None:
            super().__init__()
            self.meta = meta

    def __init__(
        self,
        lessons: List[LessonMeta],
        completed: Set[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._lessons = lessons
        self._completed = completed or set()

    def compose(self) -> ComposeResult:
        yield Label(" Lessons ", id="lesson-browser-title")
        items = [
            LessonItem(meta, completed=meta.id in self._completed)
            for meta in self._lessons
        ]
        yield ListView(*items, id="lesson-list")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, LessonItem):
            self.post_message(self.LessonSelected(item.meta))

    def refresh_status(self, completed: Set[str]) -> None:
        """Update completion status icons."""
        self._completed = completed
        list_view = self.query_one("#lesson-list", ListView)
        for child in list_view.children:
            if isinstance(child, LessonItem):
                was = child.completed
                child.completed = child.meta.id in completed
                if was != child.completed:
                    child.refresh()
