"""PTY process lifecycle management."""
from __future__ import annotations

import asyncio
import fcntl
import os
import pty
import signal
import struct
import termios
from typing import Callable, Optional


class PtyManager:
    """Manages a PTY-backed bash process."""

    def __init__(self) -> None:
        self._pid: int = -1
        self._fd: int = -1
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._on_output: Optional[Callable[[bytes], None]] = None
        self._on_disconnect: Optional[Callable[[], None]] = None

    @property
    def fd(self) -> int:
        return self._fd

    @property
    def pid(self) -> int:
        return self._pid

    @property
    def alive(self) -> bool:
        if self._pid <= 0:
            return False
        try:
            os.waitpid(self._pid, os.WNOHANG)
            os.kill(self._pid, 0)
            return True
        except (ProcessLookupError, ChildProcessError, PermissionError):
            return False

    def spawn(self, bashrc_path: str, rows: int = 24, cols: int = 80) -> None:
        """Fork a PTY, exec bash with the given rcfile."""
        master_fd, slave_fd = pty.openpty()

        child_pid = os.fork()
        if child_pid == 0:
            # ---- child process ----
            os.close(master_fd)
            os.setsid()

            # Open the slave side and make it the controlling terminal
            slave_path = os.ttyname(slave_fd)
            os.close(slave_fd)
            new_slave = os.open(slave_path, os.O_RDWR)
            # Set up as controlling terminal
            fcntl.ioctl(new_slave, termios.TIOCSCTTY, 0)

            # Dup to stdio
            os.dup2(new_slave, 0)
            os.dup2(new_slave, 1)
            os.dup2(new_slave, 2)
            if new_slave > 2:
                os.close(new_slave)

            os.execvp("bash", ["bash", "--rcfile", bashrc_path])
        else:
            # ---- parent process ----
            os.close(slave_fd)
            self._pid = child_pid
            self._fd = master_fd

            # Set initial size
            self.resize(rows, cols)

            # Make fd non-blocking
            flags = fcntl.fcntl(master_fd, fcntl.F_GETFL)
            fcntl.fcntl(master_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

    def start(
        self,
        on_output: Callable[[bytes], None],
        on_disconnect: Callable[[], None],
    ) -> None:
        """Begin async reading from the PTY fd."""
        self._on_output = on_output
        self._on_disconnect = on_disconnect
        self._loop = asyncio.get_running_loop()
        self._loop.add_reader(self._fd, self._reader_callback)

    def _reader_callback(self) -> None:
        """Called by the event loop when data is available on the PTY fd."""
        try:
            data = os.read(self._fd, 65536)
            if not data:
                self._handle_disconnect()
                return
            if self._on_output:
                self._on_output(data)
        except OSError:
            self._handle_disconnect()

    def _handle_disconnect(self) -> None:
        """Handle PTY disconnect."""
        try:
            if self._loop and self._fd >= 0:
                self._loop.remove_reader(self._fd)
        except Exception:
            pass
        if self._on_disconnect:
            self._on_disconnect()

    def write(self, data: bytes) -> None:
        """Send data to the PTY stdin."""
        if self._fd >= 0:
            try:
                os.write(self._fd, data)
            except OSError:
                pass

    def resize(self, rows: int, cols: int) -> None:
        """Update the PTY window size via ioctl."""
        if self._fd >= 0:
            try:
                winsize = struct.pack("HHHH", rows, cols, 0, 0)
                fcntl.ioctl(self._fd, termios.TIOCSWINSZ, winsize)
            except OSError:
                pass

    def stop(self) -> None:
        """Kill the child process and clean up."""
        # Remove reader first
        if self._loop and self._fd >= 0:
            try:
                self._loop.remove_reader(self._fd)
            except Exception:
                pass

        # Kill child
        if self._pid > 0:
            try:
                os.kill(self._pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                os.waitpid(self._pid, os.WNOHANG)
            except ChildProcessError:
                pass
            self._pid = -1

        # Close fd
        if self._fd >= 0:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = -1

        self._loop = None
