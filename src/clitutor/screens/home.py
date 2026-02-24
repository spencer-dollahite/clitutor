"""Home screen - banner, stats, lesson browser."""
from __future__ import annotations

from typing import List, Set

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Label, Static

from clitutor.models.lesson import LessonMeta
from clitutor.models.xp import get_level_info
from clitutor.widgets.lesson_browser import LessonBrowser
from clitutor.widgets.xp_bar import XPBar

BANNER = r"""
   ____ _     ___ _         _
  / ___| |   |_ _| |_ _   _| |_ ___  _ __
 | |   | |    | || __| | | | __/ _ \| '__|
 | |___| |___ | || |_| |_| | || (_) | |
  \____|_____|___|\__|\__,_|\__\___/|_|
"""


class HomeScreen(Screen):
    """Main dashboard with lesson browser and XP stats."""

    CSS_PATH = None  # We'll use the global CSS

    BINDINGS = [
        ("q", "quit_app", "Quit"),
        ("escape", "quit_app", "Quit"),
    ]

    def __init__(
        self,
        lessons: List[LessonMeta],
        total_xp: int = 0,
        completed: Set[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._lessons = lessons
        self._total_xp = total_xp
        self._completed = completed or set()

    def compose(self) -> ComposeResult:
        yield XPBar(total_xp=self._total_xp, id="header-bar")
        with Vertical(id="home-container"):
            yield Label(BANNER, id="banner")
            yield self._make_stats_bar()
            yield LessonBrowser(
                self._lessons,
                completed=self._completed,
                id="lesson-browser-container",
            )
        yield Footer()

    def _make_stats_bar(self) -> Static:
        info = get_level_info(self._total_xp)
        total_lessons = len(self._lessons)
        done = len(self._completed)

        bar = Static(id="stats-bar")
        bar._stats_text = (
            f"[yellow]XP: {self._total_xp}[/]  |  "
            f"[cyan]Level: {info.level} - {info.title}[/]  |  "
            f"[green]Completed: {done}/{total_lessons} lessons[/]"
        )
        return bar

    def on_mount(self) -> None:
        stats = self.query_one("#stats-bar", Static)
        if hasattr(stats, "_stats_text"):
            stats.update(stats._stats_text)

    def on_lesson_browser_lesson_selected(self, event: LessonBrowser.LessonSelected) -> None:
        """Handle lesson selection - notify the app."""
        self.app.open_lesson(event.meta)

    def action_quit_app(self) -> None:
        self.app.exit()

    def refresh_data(self, total_xp: int, completed: Set[str]) -> None:
        """Refresh displayed data after returning from a lesson."""
        self._total_xp = total_xp
        self._completed = completed

        # Update XP bar
        xp_bar = self.query_one(XPBar)
        xp_bar.total_xp = total_xp

        # Update stats
        info = get_level_info(total_xp)
        total_lessons = len(self._lessons)
        done = len(completed)
        stats = self.query_one("#stats-bar", Static)
        stats.update(
            f"[yellow]XP: {total_xp}[/]  |  "
            f"[cyan]Level: {info.level} - {info.title}[/]  |  "
            f"[green]Completed: {done}/{total_lessons} lessons[/]"
        )

        # Update lesson browser
        browser = self.query_one(LessonBrowser)
        browser.refresh_status(completed)
