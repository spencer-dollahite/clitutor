"""Lesson screen - split pane with markdown content and live terminal."""
from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Label, Static

from clitutor.core.docker_sandbox import DockerSandbox
from clitutor.core.executor import CommandExecutor, CommandResult, DockerExecutor
from clitutor.core.sandbox import SandboxManager
from clitutor.core.validator import OutputValidator, ValidationResult
from clitutor.models.lesson import Exercise, LessonData
from clitutor.models.progress import ProgressManager
from clitutor.models.xp import calculate_xp, get_level_info
from clitutor.widgets.hint_overlay import HintOverlay
from clitutor.widgets.markdown_pane import MarkdownPane
from clitutor.widgets.terminal_pane import SlashCommand, TerminalPane
from clitutor.widgets.xp_bar import XPBar


class LessonScreen(Screen):
    """Split-pane lesson screen with content + terminal."""

    BINDINGS = [
        ("escape", "go_back", "Back to Lessons"),
    ]

    def __init__(
        self,
        lesson: LessonData,
        progress_mgr: ProgressManager,
        sandbox: SandboxManager | DockerSandbox,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._lesson = lesson
        self._progress = progress_mgr
        self._sandbox = sandbox
        self._current_exercise_idx = 0
        self._executor = self._make_executor()
        self._validator = OutputValidator(sandbox, executor=self._executor)

        # Skip already-completed exercises
        self._advance_to_first_incomplete()

    def _make_executor(self):
        """Create the appropriate executor for the sandbox type."""
        if isinstance(self._sandbox, DockerSandbox):
            return DockerExecutor(self._sandbox)
        return CommandExecutor(self._sandbox.path)

    def _advance_to_first_incomplete(self) -> None:
        """Skip to the first incomplete exercise."""
        for i, ex in enumerate(self._lesson.exercises):
            if not self._progress.is_exercise_completed(self._lesson.id, ex.id):
                self._current_exercise_idx = i
                return
        # All completed
        self._current_exercise_idx = len(self._lesson.exercises)

    @property
    def current_exercise(self) -> Exercise | None:
        if self._current_exercise_idx < len(self._lesson.exercises):
            return self._lesson.exercises[self._current_exercise_idx]
        return None

    def compose(self) -> ComposeResult:
        yield XPBar(total_xp=self._progress.total_xp, id="header-bar")
        with Horizontal(id="lesson-container"):
            with Vertical(id="lesson-pane"):
                yield MarkdownPane(
                    self._lesson.content_markdown,
                    id="markdown-content",
                )
                yield Label("", id="exercise-indicator")
            yield TerminalPane(self._executor, id="terminal-pane")
        yield Footer()

    def on_mount(self) -> None:
        self._setup_current_exercise()
        # Always default cursor to terminal input
        self._focus_terminal()

    def on_screen_resume(self) -> None:
        """Re-focus terminal when returning from overlay."""
        self._focus_terminal()

    def on_click(self) -> None:
        """Re-focus terminal input on any click."""
        self._focus_terminal()

    def _focus_terminal(self) -> None:
        """Send focus to the terminal command input."""
        self.set_timer(0.05, self._do_focus_terminal)

    def _do_focus_terminal(self) -> None:
        try:
            self.query_one(TerminalPane).focus_input()
        except Exception:
            pass

    def _setup_current_exercise(self) -> None:
        """Set up the current exercise - sandbox files and indicator."""
        ex = self.current_exercise
        indicator = self.query_one("#exercise-indicator", Label)

        if ex is None:
            indicator.update(
                "[bold green]All exercises completed! Press ESC to return.[/]"
            )
            return

        # Reset exercise runtime state
        ex.attempts = 0
        ex.first_try = True
        ex.hints_used = 0
        ex.completed = False

        # Reset cwd to sandbox root for a clean exercise start
        self._executor.reset_cwd()

        # Set up sandbox for exercise
        if ex.sandbox_setup:
            for cmd in ex.sandbox_setup:
                self._executor.run(cmd)

        # Copy required assets
        self._seed_lesson_assets()

        completed = self._current_exercise_idx
        total = len(self._lesson.exercises)
        indicator.update(
            f"[bold] Exercise {completed + 1}/{total}: {ex.title} [/]"
        )

        # Show exercise prompt in terminal and update prompt after cwd reset
        terminal = self.query_one(TerminalPane)
        terminal.update_prompt()
        terminal.write_system_message(f"--- Exercise {completed + 1}: {ex.title} ---")

    def _seed_lesson_assets(self) -> None:
        """Seed sandbox with assets needed for the current lesson."""
        # Always provide log files for the start-here lesson
        if self._lesson.id == "00_start_here":
            self._sandbox.seed_asset("1.log")
            self._sandbox.seed_asset("2.log")
        if self._lesson.id == "06_scripting":
            self._sandbox.seed_asset("sample_script.sh")

    def on_terminal_pane_command_completed(
        self, event: TerminalPane.CommandCompleted
    ) -> None:
        """Validate command result against current exercise."""
        ex = self.current_exercise
        if ex is None:
            return

        result = event.result
        if result.blocked:
            return

        ex.attempts += 1
        validation = self._validator.validate(ex, result)

        terminal = self.query_one(TerminalPane)

        if validation.passed:
            # Calculate XP
            xp = calculate_xp(
                base_xp=ex.xp,
                difficulty=ex.difficulty,
                first_try=ex.first_try,
                hints_used=ex.hints_used,
            )

            # Record progress
            self._progress.record_exercise(
                lesson_id=self._lesson.id,
                exercise_id=ex.id,
                xp_earned=xp,
                attempts=ex.attempts,
                hints_used=ex.hints_used,
            )

            # Update XP bar
            xp_bar = self.query_one(XPBar)
            old_xp = xp_bar.total_xp
            xp_bar.total_xp = self._progress.total_xp

            # Check for level up
            old_info = get_level_info(old_xp)
            new_info = get_level_info(self._progress.total_xp)

            terminal.write_system_message(f"✓ {validation.message} (+{xp} XP)")

            if new_info.level > old_info.level:
                self.notify(
                    f"Level Up! You are now {new_info.title}!",
                    title="Level Up!",
                    severity="information",
                    timeout=5,
                )
                terminal.write_system_message(
                    f"★ LEVEL UP! You are now Lv.{new_info.level} {new_info.title}! ★"
                )

            # Advance to next exercise
            self._current_exercise_idx += 1
            if self.current_exercise is not None:
                self._setup_current_exercise()
            else:
                indicator = self.query_one("#exercise-indicator", Label)
                indicator.update(
                    "[bold green]All exercises completed! Press ESC to return.[/]"
                )
                terminal.write_system_message(
                    "★ Lesson complete! Press ESC to return to the lesson browser. ★"
                )
                self.notify(
                    f"Lesson '{self._lesson.title}' completed!",
                    title="Lesson Complete!",
                    severity="information",
                    timeout=5,
                )
        else:
            # Mark first_try as failed
            ex.first_try = False
            terminal.write_system_message(f"✗ {validation.message} Try again!")

    def on_slash_command(self, event: SlashCommand) -> None:
        """Handle slash commands."""
        cmd = event.command.strip().lower()
        terminal = self.query_one(TerminalPane)

        if cmd == "/hint":
            self._show_hint()
        elif cmd == "/reset":
            self._reset_sandbox()
        elif cmd == "/lessons":
            self.action_go_back()
        elif cmd == "/progress":
            self._show_progress()
        elif cmd in ("/quit", "/exit"):
            self.app.exit()
        elif cmd == "/skip":
            self._skip_exercise()
        else:
            terminal.write_system_message(
                "Available commands: /hint /reset /lessons /progress /skip /quit"
            )

    def _show_hint(self) -> None:
        """Show the hint overlay for the current exercise."""
        ex = self.current_exercise
        if ex is None:
            self.query_one(TerminalPane).write_system_message("No active exercise.")
            return

        if not ex.hints:
            self.query_one(TerminalPane).write_system_message(
                "No hints available for this exercise."
            )
            return

        def on_dismiss(_result) -> None:
            # Update hints_used from the overlay
            overlay = self._current_hint_overlay
            if overlay and overlay.hints_shown > ex.hints_used:
                ex.hints_used = overlay.hints_shown

        overlay = HintOverlay(
            hints=ex.hints,
            hints_shown=ex.hints_used,
        )
        self._current_hint_overlay = overlay
        self.app.push_screen(overlay, callback=on_dismiss)

    def _reset_sandbox(self) -> None:
        """Reset the sandbox and re-setup current exercise."""
        self._sandbox.reset()
        self._executor = self._make_executor()
        self._validator = OutputValidator(self._sandbox, executor=self._executor)
        self._setup_current_exercise()
        terminal = self.query_one(TerminalPane)
        terminal.executor = self._executor
        terminal.update_prompt()
        terminal.write_system_message("Sandbox reset.")

    def _show_progress(self) -> None:
        """Show current lesson progress."""
        terminal = self.query_one(TerminalPane)
        total = len(self._lesson.exercises)
        done = sum(
            1 for ex in self._lesson.exercises
            if self._progress.is_exercise_completed(self._lesson.id, ex.id)
        )
        terminal.write_system_message(
            f"Lesson progress: {done}/{total} exercises | "
            f"Total XP: {self._progress.total_xp}"
        )

    def _skip_exercise(self) -> None:
        """Skip the current exercise (no XP)."""
        ex = self.current_exercise
        if ex is None:
            return
        terminal = self.query_one(TerminalPane)
        terminal.write_system_message(f"Skipped: {ex.title} (0 XP)")
        self._current_exercise_idx += 1
        if self.current_exercise is not None:
            self._setup_current_exercise()
        else:
            indicator = self.query_one("#exercise-indicator", Label)
            indicator.update(
                "[bold green]All exercises completed! Press ESC to return.[/]"
            )

    def action_go_back(self) -> None:
        """Return to the home screen."""
        self.app.pop_screen()
