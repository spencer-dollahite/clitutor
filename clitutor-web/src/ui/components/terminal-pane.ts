/** xterm.js terminal wrapper — connects to v86 serial console. */

import { Terminal } from "@xterm/xterm";
import { FitAddon } from "@xterm/addon-fit";
import { WebLinksAddon } from "@xterm/addon-web-links";
import type { LinuxVM } from "../../vm/linux-vm";

export class TerminalPane {
  private terminal: Terminal;
  private fitAddon: FitAddon;
  private container: HTMLElement;
  private vm: LinuxVM | null = null;

  /** Callback for slash commands (e.g., /hint, /reset). */
  onSlashCommand: ((cmd: string) => void) | null = null;

  /** Buffer for detecting slash commands. */
  private inputBuffer = "";

  constructor(parent: HTMLElement) {
    this.container = document.createElement("div");
    this.container.className = "terminal-container";
    parent.appendChild(this.container);

    this.terminal = new Terminal({
      theme: {
        background: "#000000",
        foreground: "#e0e0e0",
        cursor: "#00d4aa",
        cursorAccent: "#000000",
        selectionBackground: "rgba(0, 212, 170, 0.3)",
        black: "#000000",
        red: "#ef4444",
        green: "#22c55e",
        yellow: "#f59e0b",
        blue: "#3b82f6",
        magenta: "#a855f7",
        cyan: "#06b6d4",
        white: "#e0e0e0",
        brightBlack: "#555555",
        brightRed: "#ff6b6b",
        brightGreen: "#4ade80",
        brightYellow: "#fbbf24",
        brightBlue: "#60a5fa",
        brightMagenta: "#c084fc",
        brightCyan: "#22d3ee",
        brightWhite: "#ffffff",
      },
      fontFamily: "'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace",
      fontSize: 14,
      cursorBlink: true,
      cursorStyle: "block",
      allowTransparency: true,
      scrollback: 5000,
    });

    this.fitAddon = new FitAddon();
    this.terminal.loadAddon(this.fitAddon);
    this.terminal.loadAddon(new WebLinksAddon());
  }

  /** Open the terminal and connect to VM serial I/O. */
  attach(vm: LinuxVM): void {
    this.vm = vm;
    this.terminal.open(this.container);
    this.fitAddon.fit();

    // Terminal input → VM serial
    this.terminal.onData((data) => {
      // Track input for slash command detection
      for (const ch of data) {
        if (ch === "\r" || ch === "\n") {
          const stripped = this.inputBuffer.trim();
          if (stripped.startsWith("/") && this.onSlashCommand) {
            // Don't send to VM; handle as slash command
            // Send Ctrl+U to clear the line, then Enter for fresh prompt
            this.vm?.sendSerial("\x15");
            this.vm?.sendSerial("\r");
            this.inputBuffer = "";
            this.onSlashCommand(stripped);
            return;
          }
          this.inputBuffer = "";
          this.vm?.sendSerial(data);
          return;
        } else if (ch === "\x7f") {
          // Backspace
          this.inputBuffer = this.inputBuffer.slice(0, -1);
        } else if (ch === "\x15") {
          // Ctrl+U
          this.inputBuffer = "";
        } else if (ch >= " ") {
          this.inputBuffer += ch;
        }
      }

      this.vm?.sendSerial(data);
    });

    // Handle resize
    const resizeObserver = new ResizeObserver(() => {
      this.fitAddon.fit();
    });
    resizeObserver.observe(this.container);
  }

  /** Write data to the terminal display (from VM serial output). */
  write(data: string): void {
    this.terminal.write(data);
  }

  /** Focus the terminal. */
  focus(): void {
    this.terminal.focus();
  }

  /** Fit terminal to container dimensions. */
  fit(): void {
    this.fitAddon.fit();
  }

  /** Get the underlying terminal for direct access. */
  get term(): Terminal {
    return this.terminal;
  }
}
