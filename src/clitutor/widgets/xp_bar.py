"""XP progress bar widget with level badge."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Label, ProgressBar, Static

from clitutor.models.xp import LevelInfo, get_level_info


class XPBar(Static):
    """Header widget showing level badge + XP progress bar."""

    total_xp: reactive[int] = reactive(0, init=False)

    def __init__(self, total_xp: int = 0, **kwargs) -> None:
        super().__init__(**kwargs)
        self._initial_xp = total_xp

    def compose(self) -> ComposeResult:
        with Horizontal(id="xp-bar-container"):
            yield Label("CLItutor", id="app-title")
            yield Label("", id="level-badge")
            yield ProgressBar(total=100, show_eta=False, show_percentage=False, id="xp-progress")
            yield Label("", id="xp-label")

    def on_mount(self) -> None:
        self.total_xp = self._initial_xp

    def watch_total_xp(self, value: int) -> None:
        self._update_display()

    def _update_display(self) -> None:
        try:
            info = get_level_info(self.total_xp)

            badge = self.query_one("#level-badge", Label)
            badge.update(f" Lv.{info.level} {info.title} ")

            bar = self.query_one("#xp-progress", ProgressBar)
            bar.total = max(info.xp_for_level, 1)
            bar.progress = info.xp_in_level

            label = self.query_one("#xp-label", Label)
            label.update(f" {info.current_xp}/{info.level_ceiling} XP ")
        except Exception:
            pass  # Widget not yet mounted
