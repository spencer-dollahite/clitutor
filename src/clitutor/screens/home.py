"""Home screen - banner, stats, lesson browser."""
from __future__ import annotations

from typing import Dict, List, Set

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import ModalScreen, Screen
from textual.widgets import Button, Footer, Header, Label, Static

from clitutor.models.lesson import LessonMeta
from clitutor.models.progress import ProgressManager
from clitutor.models.xp import get_level_info
from clitutor.widgets.lesson_browser import LessonBrowser
from clitutor.widgets.xp_bar import XPBar


class ConfirmResetScreen(ModalScreen[bool]):
    """Modal confirmation dialog for resetting progress."""

    DEFAULT_CSS = """
    ConfirmResetScreen {
        align: center middle;
    }
    #confirm-dialog {
        width: 50;
        height: auto;
        padding: 1 2;
        background: #0a0a0a;
        border: solid #ff4444;
    }
    #confirm-dialog Label {
        width: 100%;
        text-align: center;
        margin-bottom: 1;
    }
    #confirm-buttons {
        width: 100%;
        height: auto;
        align-horizontal: center;
        layout: horizontal;
    }
    #confirm-buttons Button {
        margin: 0 1;
    }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label("[bold red]Reset All Progress?[/]")
            yield Label("This will erase all XP and exercise completions.")
            with Vertical(id="confirm-buttons"):
                yield Button("Yes, reset", variant="error", id="confirm-yes")
                yield Button("Cancel", variant="primary", id="confirm-no")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "confirm-yes")

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
        ("r", "reset_progress", "Reset Progress"),
    ]

    def __init__(
        self,
        lessons: List[LessonMeta],
        total_xp: int = 0,
        completed: Set[str] | None = None,
        exercise_progress: Dict[str, int] | None = None,
        progress_mgr: ProgressManager | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._lessons = lessons
        self._total_xp = total_xp
        self._completed = completed or set()
        self._exercise_progress = exercise_progress or {}
        self._progress = progress_mgr

    def compose(self) -> ComposeResult:
        yield XPBar(total_xp=self._total_xp, id="header-bar")
        with Vertical(id="home-container"):
            yield Label(BANNER, id="banner")
            yield self._make_stats_bar()
            yield LessonBrowser(
                self._lessons,
                exercise_progress=self._exercise_progress,
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

    def action_reset_progress(self) -> None:
        if self._progress is None:
            return

        def _on_confirm(confirmed: bool) -> None:
            if not confirmed:
                return
            self._progress.reset_all()
            self.refresh_data(
                total_xp=0,
                completed=set(),
                exercise_progress={},
            )
            self.notify("All progress has been reset.", severity="warning", timeout=3)

        self.app.push_screen(ConfirmResetScreen(), callback=_on_confirm)

    def refresh_data(
        self,
        total_xp: int,
        completed: Set[str],
        exercise_progress: Dict[str, int] | None = None,
    ) -> None:
        """Refresh displayed data after returning from a lesson."""
        self._total_xp = total_xp
        self._completed = completed
        self._exercise_progress = exercise_progress or {}

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
        browser.refresh_status(self._exercise_progress)
