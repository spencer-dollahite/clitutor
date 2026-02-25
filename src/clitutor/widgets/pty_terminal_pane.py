"""PTY-backed terminal widget using pyte for VT100 emulation."""
from __future__ import annotations

import os
import re
import tempfile
from functools import lru_cache
from typing import Optional

import pyte
from rich.segment import Segment
from rich.style import Style
from rich.text import Text
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget

from clitutor.core.bashrc_template import (
    CMD_END_SENTINEL,
    CMD_START_SENTINEL,
    SENTINEL_CHAR,
    generate_bashrc,
)
from clitutor.core.executor import CommandResult
from clitutor.core.pty_manager import PtyManager

# Regex to match sentinel markers in the data stream
_SENTINEL_RE = re.compile(
    SENTINEL_CHAR.encode()
    + rb"("
    + re.escape(CMD_START_SENTINEL.encode())
    + rb"|"
    + re.escape(CMD_END_SENTINEL.encode())
    + rb":\d+:[^\x1f]*"
    + rb")"
    + SENTINEL_CHAR.encode()
)

# Pre-compiled ANSI stripping patterns (used in _finish_capture)
_ANSI_CSI_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")
_ANSI_OSC_RE = re.compile(r"\x1b\][^\x07]*\x07")
_CTRL_CHAR_RE = re.compile(r"[\x00-\x08\x0e-\x1f]")

# Map pyte color names to Rich color names
_PYTE_COLOR_MAP = {
    "black": "black",
    "red": "red",
    "green": "green",
    "brown": "yellow",
    "blue": "blue",
    "magenta": "magenta",
    "cyan": "cyan",
    "white": "white",
    "default": "default",
    # Bright variants
    "brightblack": "bright_black",
    "brightred": "bright_red",
    "brightgreen": "bright_green",
    "brightbrown": "bright_yellow",
    "brightblue": "bright_blue",
    "brightmagenta": "bright_magenta",
    "brightcyan": "bright_cyan",
    "brightwhite": "bright_white",
}

# Special key -> escape sequence mapping
_KEY_MAP = {
    "up": b"\x1b[A",
    "down": b"\x1b[B",
    "right": b"\x1b[C",
    "left": b"\x1b[D",
    "home": b"\x1b[H",
    "end": b"\x1b[F",
    "insert": b"\x1b[2~",
    "delete": b"\x1b[3~",
    "pageup": b"\x1b[5~",
    "pagedown": b"\x1b[6~",
    "f1": b"\x1bOP",
    "f2": b"\x1bOQ",
    "f3": b"\x1bOR",
    "f4": b"\x1bOS",
    "f5": b"\x1b[15~",
    "f6": b"\x1b[17~",
    "f7": b"\x1b[18~",
    "f8": b"\x1b[19~",
    "f9": b"\x1b[20~",
    "f10": b"\x1b[21~",
    "f11": b"\x1b[23~",
    "f12": b"\x1b[24~",
    "tab": b"\t",
    "enter": b"\r",
    "backspace": b"\x7f",
}


@lru_cache(maxsize=256)
def _pyte_color_to_rich(color: str) -> Optional[str]:
    """Convert a pyte color value to a Rich color string."""
    if not color or color == "default":
        return None
    # Direct name mapping
    normalized = color.lower().replace(" ", "").replace("-", "").replace("_", "")
    if normalized in _PYTE_COLOR_MAP:
        mapped = _PYTE_COLOR_MAP[normalized]
        return None if mapped == "default" else mapped
    # 256-color or hex (pyte sometimes gives numeric strings)
    try:
        idx = int(color)
        return f"color({idx})"
    except (ValueError, TypeError):
        pass
    # 6-digit hex
    if len(color) == 6:
        try:
            int(color, 16)
            return f"#{color}"
        except ValueError:
            pass
    return None


# Style cache: (fg, bg, bold, italic, underline, strike, reverse) -> Style
_style_cache: dict[tuple, Style] = {}


def _get_style(fg_raw: str, bg_raw: str, bold: bool, italic: bool,
               underline: bool, strike: bool, reverse: bool) -> tuple[Style, tuple]:
    """Return a cached Style and its key for the given pyte character attributes."""
    key = (fg_raw, bg_raw, bold, italic, underline, strike, reverse)
    cached = _style_cache.get(key)
    if cached is not None:
        return cached, key
    fg = _pyte_color_to_rich(fg_raw) if fg_raw != "default" else None
    bg = _pyte_color_to_rich(bg_raw) if bg_raw != "default" else None
    style = Style(
        color=fg or ("white" if not reverse else "black"),
        bgcolor=bg or ("#000000" if not reverse else "white"),
        bold=bold,
        italic=italic,
        underline=underline,
        strike=strike,
        reverse=reverse,
    )
    _style_cache[key] = style
    return style, key


class PtyTerminalPane(Widget, can_focus=True):
    """Real PTY terminal widget with VT100 emulation via pyte."""

    DEFAULT_CSS = """
    PtyTerminalPane {
        width: 1fr;
        height: 1fr;
        background: #000000;
    }
    """

    class CommandCompleted(Message):
        """Posted when a command finishes execution."""

        def __init__(self, result: CommandResult) -> None:
            super().__init__()
            self.result = result

    class SlashCommand(Message):
        """A slash command entered by the user."""

        def __init__(self, command: str) -> None:
            super().__init__()
            self.command = command

    def __init__(
        self,
        sandbox_path: str,
        sandbox_type: str = "local",
        docker_container: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._sandbox_path = str(sandbox_path)
        self._sandbox_type = sandbox_type
        self._docker_container = docker_container

        # pyte screen and stream
        self._screen = pyte.Screen(80, 24)
        self._stream = pyte.Stream(self._screen)

        # PTY manager
        self._pty = PtyManager()

        # State for sentinel capture
        self._capturing = False
        self._captured_chunks: list[bytes] = []
        self._cwd = self._sandbox_path
        self._bashrc_tmpfile: Optional[str] = None
        self._pty_spawned = False

        # Skip counter: how many CMD_END sentinels to ignore (1 = bash startup)
        self._skip_captures = 1
        # Set once the first CMD_END fires (bash prompt is ready)
        self._pty_ready = False
        # Messages queued before the PTY prompt is ready
        self._pending_messages: list[str] = []

        # Buffered system messages for batched display
        self._msg_buffer: list[str] = []
        self._msg_flush_scheduled = False

        # Input line buffer for slash command detection
        self._input_buffer = ""

        # Performance: debounced refresh and dirty-line cache
        self._refresh_pending = False
        self._line_cache: dict[int, Strip] = {}

    @property
    def cwd(self) -> str:
        """Current working directory reported by the bash session."""
        return self._cwd

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        """PTY spawn is deferred to the first on_resize, where the real
        widget dimensions are available."""
        pass

    def _spawn_pty(self) -> None:
        """Write bashrc, spawn PTY, start reader."""
        rows, cols = self._effective_size()

        bashrc_content = generate_bashrc(self._sandbox_path)
        fd, self._bashrc_tmpfile = tempfile.mkstemp(
            prefix="clitutor-bashrc-", suffix=".sh"
        )
        os.write(fd, bashrc_content.encode())
        os.close(fd)

        if self._sandbox_type == "docker" and self._docker_container:
            self._spawn_docker_pty(rows, cols)
        else:
            self._pty.spawn(self._bashrc_tmpfile, rows=rows, cols=cols)

        self._pty.start(
            on_output=self._on_pty_output,
            on_disconnect=self._on_pty_disconnect,
        )

    def _spawn_docker_pty(self, rows: int, cols: int) -> None:
        """Spawn PTY running docker exec with custom bashrc."""
        import subprocess

        # Copy bashrc into container
        subprocess.run(
            [
                "docker",
                "cp",
                self._bashrc_tmpfile,
                f"{self._docker_container}:/tmp/clitutor.bashrc",
            ],
            capture_output=True,
        )
        # Override spawn to exec docker
        import pty as pty_mod
        import fcntl
        import termios

        master_fd, slave_fd = pty_mod.openpty()
        child_pid = os.fork()
        if child_pid == 0:
            os.close(master_fd)
            os.setsid()
            slave_path = os.ttyname(slave_fd)
            os.close(slave_fd)
            new_slave = os.open(slave_path, os.O_RDWR)
            fcntl.ioctl(new_slave, termios.TIOCSCTTY, 0)
            os.dup2(new_slave, 0)
            os.dup2(new_slave, 1)
            os.dup2(new_slave, 2)
            if new_slave > 2:
                os.close(new_slave)
            os.execvp(
                "docker",
                [
                    "docker",
                    "exec",
                    "-it",
                    self._docker_container,
                    "bash",
                    "--rcfile",
                    "/tmp/clitutor.bashrc",
                ],
            )
        else:
            os.close(slave_fd)
            self._pty._pid = child_pid
            self._pty._fd = master_fd
            self._pty.resize(rows, cols)
            flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
            fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def _effective_size(self) -> tuple[int, int]:
        """Return (rows, cols) based on current widget size."""
        size = self.size
        rows = max(size.height, 2)
        cols = max(size.width, 10)
        return rows, cols

    def on_unmount(self) -> None:
        """Clean up PTY and temp files."""
        self._cleanup()

    def _cleanup(self) -> None:
        self._pty.stop()
        if self._bashrc_tmpfile:
            try:
                os.unlink(self._bashrc_tmpfile)
            except OSError:
                pass
            self._bashrc_tmpfile = None

    # ------------------------------------------------------------------
    # PTY output processing
    # ------------------------------------------------------------------

    def _on_pty_output(self, data: bytes) -> None:
        """Called (from event loop reader) when PTY produces output."""
        # Process data and sentinels in the order they appear so that
        # only bytes between CMD_START and CMD_END are captured.
        display_parts: list[bytes] = []
        last_end = 0

        for match in _SENTINEL_RE.finditer(data):
            # Handle the data segment before this sentinel
            segment = data[last_end:match.start()]
            if segment:
                if self._capturing:
                    self._captured_chunks.append(segment)
                display_parts.append(segment)

            # Handle the sentinel itself
            sentinel_body = match.group(1).decode("utf-8", errors="replace")
            if sentinel_body == CMD_START_SENTINEL:
                self._capturing = True
                self._captured_chunks = []
            elif sentinel_body.startswith(CMD_END_SENTINEL + ":"):
                parts = sentinel_body.split(":", 2)
                exit_code = int(parts[1]) if len(parts) > 1 else 0
                new_cwd = parts[2] if len(parts) > 2 else self._cwd
                self._cwd = new_cwd
                self._finish_capture(exit_code)

            last_end = match.end()

        # Handle any data after the last sentinel
        tail = data[last_end:]
        if tail:
            if self._capturing:
                self._captured_chunks.append(tail)
            display_parts.append(tail)

        # Feed non-sentinel data to pyte for display
        clean = b"".join(display_parts)
        if clean:
            try:
                self._stream.feed(clean.decode("utf-8", errors="replace"))
            except Exception:
                pass
            # Evict dirty lines from cache, then clear dirty set
            for row in self._screen.dirty:
                self._line_cache.pop(row, None)
            self._screen.dirty.clear()
            self._schedule_refresh()

    def _finish_capture(self, exit_code: int) -> None:
        """Build a CommandResult from captured output and post it."""
        self._capturing = False
        self._captured_chunks_raw = self._captured_chunks
        self._captured_chunks = []

        # Skip internal captures (bash startup sentinel, prompt repaints)
        if self._skip_captures > 0:
            self._skip_captures -= 1
            if not self._pty_ready:
                self._pty_ready = True
                self._flush_pending_messages()
            return

        raw = b"".join(self._captured_chunks_raw)
        # Strip ANSI escape sequences to get plain text for validation
        text = raw.decode("utf-8", errors="replace")
        text = _ANSI_CSI_RE.sub("", text)
        text = _ANSI_OSC_RE.sub("", text)
        text = _CTRL_CHAR_RE.sub("", text)

        result = CommandResult(
            command="",
            stdout=text,
            stderr="",
            returncode=exit_code,
        )
        self.post_message(self.CommandCompleted(result))

    def _on_pty_disconnect(self) -> None:
        """Handle PTY process exit."""
        pass

    def _schedule_refresh(self) -> None:
        """Coalesce multiple PTY reads into a single refresh (~8ms)."""
        if not self._refresh_pending:
            self._refresh_pending = True
            self.set_timer(0.008, self._do_deferred_refresh)

    def _do_deferred_refresh(self) -> None:
        """Execute the deferred refresh."""
        self._refresh_pending = False
        self.refresh()

    # ------------------------------------------------------------------
    # Rendering -- convert pyte screen to Textual Strips
    # ------------------------------------------------------------------

    def get_content_width(self, container, viewport):
        return self._screen.columns

    def get_content_height(self, container, viewport, width):
        return self._screen.lines

    def render_line(self, y: int) -> Strip:
        """Render a single line from the pyte screen buffer.

        Batches consecutive characters sharing the same style into a
        single Segment for much fewer allocations per refresh.
        Uses a dirty-line cache to skip unchanged rows.
        """
        if y >= self._screen.lines:
            return Strip.blank(self.size.width)

        cursor_y = self._screen.cursor.y

        # Return cached strip if line is clean and not the cursor row
        if y != cursor_y and y in self._line_cache:
            return self._line_cache[y]

        line = self._screen.buffer[y]
        cursor_x = self._screen.cursor.x
        has_focus = self.has_focus
        cols = self._screen.columns
        segments: list[Segment] = []

        x = 0
        while x < cols:
            char = line[x]
            is_cursor = has_focus and y == cursor_y and x == cursor_x
            reverse = char.reverse ^ is_cursor

            style, style_key = _get_style(
                char.fg, char.bg, char.bold, char.italics,
                char.underscore, char.strikethrough, reverse,
            )

            # Start batching characters with the same style
            chars: list[str] = [char.data or " "]
            if not is_cursor:
                nx = x + 1
                while nx < cols:
                    nc = line[nx]
                    # Break at cursor position
                    if has_focus and y == cursor_y and nx == cursor_x:
                        break
                    nc_key = (nc.fg, nc.bg, nc.bold, nc.italics,
                              nc.underscore, nc.strikethrough, nc.reverse)
                    if nc_key != style_key:
                        break
                    chars.append(nc.data or " ")
                    nx += 1
                x = nx
            else:
                x += 1

            segments.append(Segment("".join(chars), style))

        # Pad remaining width
        width = self.size.width
        if cols < width:
            segments.append(Segment(" " * (width - cols)))

        strip = Strip(segments)

        # Cache non-cursor lines
        if y != cursor_y:
            self._line_cache[y] = strip

        return strip

    def on_focus(self) -> None:
        """Invalidate cursor line cache on focus change."""
        self._line_cache.pop(self._screen.cursor.y, None)
        self.refresh()

    def on_blur(self) -> None:
        """Invalidate cursor line cache on focus change."""
        self._line_cache.pop(self._screen.cursor.y, None)
        self.refresh()

    # ------------------------------------------------------------------
    # Keyboard input
    # ------------------------------------------------------------------

    def on_key(self, event) -> None:
        """Forward keyboard input to the PTY."""
        key = event.key

        # Let escape bubble up to the Screen for navigation bindings
        if key == "escape":
            return

        event.stop()
        event.prevent_default()

        # Handle Ctrl combos
        if key == "ctrl+c":
            self._pty.write(b"\x03")
            self._input_buffer = ""
            return
        if key == "ctrl+d":
            # Don't send EOF -- bash has ignoreeof, but also don't forward
            return
        if key == "ctrl+z":
            self._pty.write(b"\x1a")
            return
        if key == "ctrl+l":
            self._pty.write(b"\x0c")
            return
        if key == "ctrl+a":
            self._pty.write(b"\x01")
            return
        if key == "ctrl+e":
            self._pty.write(b"\x05")
            return
        if key == "ctrl+u":
            self._pty.write(b"\x15")
            self._input_buffer = ""
            return
        if key == "ctrl+k":
            self._pty.write(b"\x0b")
            return
        if key == "ctrl+w":
            self._pty.write(b"\x17")
            # Rough buffer update
            self._input_buffer = ""
            return
        if key == "ctrl+r":
            self._pty.write(b"\x12")
            return

        # Special keys
        if key in _KEY_MAP:
            if key == "enter":
                # Check for slash command before sending
                stripped = self._input_buffer.strip()
                if stripped.startswith("/"):
                    # Clear the bash input line with Ctrl+U, then Enter for fresh prompt
                    self._pty.write(b"\x15")  # Ctrl+U clears line
                    self._pty.write(b"\r")    # Enter to get fresh prompt
                    self._skip_captures += 1  # skip the empty-command capture
                    self._input_buffer = ""
                    self.post_message(self.SlashCommand(stripped))
                    return
                self._pty.write(_KEY_MAP[key])
                self._input_buffer = ""
                return
            if key == "backspace":
                self._input_buffer = self._input_buffer[:-1]
            self._pty.write(_KEY_MAP[key])
            return

        # Regular character
        if event.character and len(event.character) == 1:
            ch = event.character
            self._input_buffer += ch
            self._pty.write(ch.encode("utf-8"))
            return

        # Fallback: try to send as ctrl sequence (ctrl+<letter>)
        if key.startswith("ctrl+") and len(key) == 6:
            letter = key[-1]
            code = ord(letter.lower()) - ord("a") + 1
            if 1 <= code <= 26:
                self._pty.write(bytes([code]))

    # ------------------------------------------------------------------
    # Resize
    # ------------------------------------------------------------------

    def on_resize(self, event) -> None:
        """Spawn PTY on first resize (when real dimensions are known),
        then handle subsequent resizes."""
        rows, cols = self._effective_size()
        if not self._pty_spawned:
            # First resize -- create pyte screen and PTY with correct size
            self._screen = pyte.Screen(cols, rows)
            self._stream = pyte.Stream(self._screen)
            self._spawn_pty()
            self._pty_spawned = True
            # pyte marks all rows dirty on init; clear to avoid stale evictions
            self._screen.dirty.clear()
        elif rows != self._screen.lines or cols != self._screen.columns:
            self._screen.resize(rows, cols)
            self._pty.resize(rows, cols)
            self._line_cache.clear()

    # ------------------------------------------------------------------
    # Public API -- system messages
    # ------------------------------------------------------------------

    def write_system_message(self, text: str) -> None:
        """Display a system message in the terminal output area.

        Messages are injected directly into the pyte screen buffer
        (not sent through bash), so they never appear on the prompt
        line.  Multiple messages in the same event-loop tick are
        batched into a single display update + prompt repaint.
        """
        if not self._pty_ready:
            self._pending_messages.append(text)
            return
        self._msg_buffer.append(text)
        if not self._msg_flush_scheduled:
            self._msg_flush_scheduled = True
            self.call_after_refresh(self._flush_msg_buffer)

    def _flush_msg_buffer(self) -> None:
        """Flush buffered system messages to the pyte display."""
        self._msg_flush_scheduled = False
        if not self._msg_buffer:
            return

        parts: list[str] = []
        for i, msg in enumerate(self._msg_buffer):
            if i == 0:
                # First message: overwrite the current prompt line
                parts.append(f"\r\033[K\033[1;36m  \u25b8 {msg}\033[0m")
            else:
                # Subsequent: new line
                parts.append(f"\r\n\033[1;36m  \u25b8 {msg}\033[0m")

        self._stream.feed("".join(parts))
        self._msg_buffer = []
        self._line_cache.clear()

        # Force bash to print a fresh prompt below the messages
        self._skip_captures += 1
        self._pty.write(b"\r")
        self.refresh()

    def _flush_pending_messages(self) -> None:
        """Display queued messages now that the PTY prompt is ready.

        Called from _finish_capture when the bash startup sentinel
        arrives.  The first PS1 prompt is about to be fed to pyte
        right after this, so we do NOT need to force a prompt repaint.
        """
        if not self._pending_messages:
            return
        parts: list[str] = []
        for msg in self._pending_messages:
            parts.append(f"\033[1;36m  \u25b8 {msg}\033[0m\r\n")
        self._stream.feed("".join(parts))
        self._pending_messages = []
        self._line_cache.clear()

    def focus_input(self) -> None:
        """Focus this widget (compatibility API)."""
        self.focus()

    def respawn(self, new_sandbox_path: Optional[str] = None) -> None:
        """Kill PTY, reset screen, spawn fresh."""
        self._cleanup()
        if new_sandbox_path:
            self._sandbox_path = str(new_sandbox_path)
        self._cwd = self._sandbox_path
        self._capturing = False
        self._captured_chunks = []
        self._input_buffer = ""
        self._skip_captures = 1  # skip new bash startup sentinel
        self._pty_ready = False
        self._pending_messages = []
        self._msg_buffer = []
        self._msg_flush_scheduled = False
        self._refresh_pending = False
        self._line_cache.clear()

        # Reset pyte screen
        rows, cols = self._effective_size()
        self._screen = pyte.Screen(cols, rows)
        self._stream = pyte.Stream(self._screen)

        # Respawn PTY
        self._pty = PtyManager()
        self._spawn_pty()
        self.refresh()
