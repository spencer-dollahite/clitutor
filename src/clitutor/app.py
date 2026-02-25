"""Main CLItutor Textual application."""
from __future__ import annotations

import subprocess
from typing import TYPE_CHECKING, Union

from textual.app import App

from clitutor.core.loader import LessonLoader
from clitutor.models.progress import ProgressManager
from clitutor.screens.home import HomeScreen

if TYPE_CHECKING:
    from clitutor.core.docker_sandbox import DockerSandbox
    from clitutor.core.sandbox import SandboxManager
    from clitutor.models.lesson import LessonMeta


class CLItutorApp(App):
    """The main CLItutor TUI application."""

    TITLE = "CLItutor"
    CSS_PATH = [
        "styles/app.tcss",
        "styles/home.tcss",
        "styles/lesson.tcss",
    ]

    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._loader = LessonLoader()
        self._progress = ProgressManager()
        self._lesson_metadata = self._loader.load_metadata()
        # Sandbox is created lazily on first lesson open
        self._sandbox: Union[DockerSandbox, SandboxManager, None] = None

    def _ensure_sandbox(self) -> Union[DockerSandbox, SandboxManager]:
        """Create sandbox on first use (defers docker check from startup)."""
        if self._sandbox is None:
            if self._docker_available():
                from clitutor.core.docker_sandbox import DockerSandbox
                self._sandbox = DockerSandbox()
            else:
                from clitutor.core.sandbox import SandboxManager
                self._sandbox = SandboxManager()
        return self._sandbox

    @staticmethod
    def _docker_available() -> bool:
        """Check if Docker is available and running."""
        try:
            result = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                timeout=3,
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
            exercise_progress=self._progress.exercise_progress,
            progress_mgr=self._progress,
        )
        self.push_screen(home)

    def open_lesson(self, meta: LessonMeta) -> None:
        """Open a lesson screen."""
        from clitutor.screens.lesson import LessonScreen

        lesson = self._loader.load_lesson(meta)

        # Create fresh sandbox (first call also runs docker check)
        sandbox = self._ensure_sandbox()
        sandbox.cleanup()
        sandbox.create()

        screen = LessonScreen(
            lesson=lesson,
            progress_mgr=self._progress,
            sandbox=sandbox,
        )
        self.push_screen(screen)

    def on_screen_resume(self) -> None:
        """Refresh home screen data when returning from a lesson."""
        screen = self.screen
        if isinstance(screen, HomeScreen):
            screen.refresh_data(
                total_xp=self._progress.total_xp,
                completed=self._progress.completed_lessons,
                exercise_progress=self._progress.exercise_progress,
            )

    def on_unmount(self) -> None:
        """Clean up sandbox on exit."""
        if self._sandbox is not None:
            self._sandbox.cleanup()


def main() -> None:
    """Entry point for the CLItutor application."""
    app = CLItutorApp()
    app.run()


if __name__ == "__main__":
    main()
