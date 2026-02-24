"""Main CLItutor Textual application."""
from __future__ import annotations

import subprocess
from typing import Union

from textual.app import App

from clitutor.core.docker_sandbox import DockerSandbox
from clitutor.core.loader import LessonLoader
from clitutor.core.sandbox import SandboxManager
from clitutor.models.lesson import LessonMeta
from clitutor.models.progress import ProgressManager
from clitutor.screens.home import HomeScreen
from clitutor.screens.lesson import LessonScreen


class CLItutorApp(App):
    """The main CLItutor TUI application."""

    TITLE = "CLItutor"
    CSS_PATH = [
        "styles/app.tcss",
        "styles/home.tcss",
        "styles/lesson.tcss",
    ]

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+d", "quit", "Quit"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._loader = LessonLoader()
        self._progress = ProgressManager()
        self._docker_mode = self._docker_available()
        self._sandbox: Union[DockerSandbox, SandboxManager] = (
            DockerSandbox() if self._docker_mode else SandboxManager()
        )
        self._lesson_metadata = self._loader.load_metadata()

    @staticmethod
    def _docker_available() -> bool:
        """Check if Docker is available and running."""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=5,
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def on_mount(self) -> None:
        """Show the home screen on startup."""
        self._show_home()

    def _show_home(self) -> None:
        """Push or switch to the home screen."""
        home = HomeScreen(
            lessons=self._lesson_metadata,
            total_xp=self._progress.total_xp,
            completed=self._progress.completed_lessons,
        )
        self.push_screen(home)

    def open_lesson(self, meta: LessonMeta) -> None:
        """Open a lesson screen."""
        lesson = self._loader.load_lesson(meta)

        # Create fresh sandbox
        self._sandbox.cleanup()
        self._sandbox.create()

        screen = LessonScreen(
            lesson=lesson,
            progress_mgr=self._progress,
            sandbox=self._sandbox,
        )
        self.push_screen(screen)

    def on_screen_resume(self) -> None:
        """Refresh home screen data when returning from a lesson."""
        screen = self.screen
        if isinstance(screen, HomeScreen):
            screen.refresh_data(
                total_xp=self._progress.total_xp,
                completed=self._progress.completed_lessons,
            )

    def on_unmount(self) -> None:
        """Clean up sandbox on exit."""
        self._sandbox.cleanup()


def main() -> None:
    """Entry point for the CLItutor application."""
    app = CLItutorApp()
    app.run()


if __name__ == "__main__":
    main()
