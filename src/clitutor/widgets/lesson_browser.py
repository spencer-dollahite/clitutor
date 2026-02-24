"""Lesson browser widget - ListView with status icons."""
from __future__ import annotations

from typing import Dict, List

from textual.app import ComposeResult
from textual.message import Message
from textual.widgets import Label, ListItem, ListView, Static

from clitutor.models.lesson import LessonMeta


class LessonItem(ListItem):
    """A single lesson entry in the browser."""

    def __init__(
        self, meta: LessonMeta, completed_count: int = 0, **kwargs
    ) -> None:
        super().__init__(**kwargs)
        self.meta = meta
        self.completed_count = completed_count

    def compose(self) -> ComposeResult:
        yield Label(self._render_label(), markup=True)

    def _render_label(self) -> str:
        total = self.meta.exercise_count
        done = self.completed_count
        all_done = done >= total and total > 0
        icon = "[green]✓[/]" if all_done else "[dim]○[/]"
        if total > 0:
            progress = f"[green]{done}/{total}[/]" if all_done else f"[yellow]{done}/{total}[/]"
        else:
            progress = ""
        diff_stars = "[yellow]" + ("★" * self.meta.difficulty) + ("☆" * (5 - self.meta.difficulty)) + "[/]"
        return (
            f" {icon}  {self.meta.order:02d}. {self.meta.title}  "
            f"{progress}  {diff_stars}  [dim]{self.meta.xp} XP[/]"
        )

    def update_progress(self, completed_count: int) -> None:
        """Update the completed count and re-render the label."""
        if self.completed_count != completed_count:
            self.completed_count = completed_count
            try:
                label = self.query_one(Label)
                label.update(self._render_label())
            except Exception:
                self.refresh()


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
        exercise_progress: Dict[str, int] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._lessons = lessons
        self._exercise_progress = exercise_progress or {}

    def compose(self) -> ComposeResult:
        yield Label(" Lessons ", id="lesson-browser-title")
        items = [
            LessonItem(
                meta,
                completed_count=self._exercise_progress.get(meta.id, 0),
            )
            for meta in self._lessons
        ]
        yield ListView(*items, id="lesson-list")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item = event.item
        if isinstance(item, LessonItem):
            self.post_message(self.LessonSelected(item.meta))

    def refresh_status(self, exercise_progress: Dict[str, int]) -> None:
        """Update exercise progress for all lessons."""
        self._exercise_progress = exercise_progress
        list_view = self.query_one("#lesson-list", ListView)
        for child in list_view.children:
            if isinstance(child, LessonItem):
                child.update_progress(
                    exercise_progress.get(child.meta.id, 0)
                )
