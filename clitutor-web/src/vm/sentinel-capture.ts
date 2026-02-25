/** Sentinel parser for serial console output — port of PTY sentinel logic */

import { CMD_START_SENTINEL, CMD_END_SENTINEL, SENTINEL_CHAR } from "./bashrc";
import { createCommandResult, type CommandResult } from "../core/models";

// ANSI stripping patterns (used to clean captured output for validation)
const ANSI_CSI_RE = /\x1b\[[\x20-\x3f]*[\x40-\x7e]/g; // handles standard + private CSI (e.g. \x1b[?2004l)
const ANSI_OSC_RE = /\x1b\][^\x07]*\x07/g;
const CTRL_CHAR_RE = /[\x00-\x08\x0b-\x1f]/g; // includes \r (0x0d), excludes \t and \n

// Build sentinel regex to match: \x1f(CMD_START|CMD_END:exitcode:cwd)\x1f
const SENTINEL_RE = new RegExp(
  escapeRegex(SENTINEL_CHAR) +
  "(" +
  escapeRegex(CMD_START_SENTINEL) +
  "|" +
  escapeRegex(CMD_END_SENTINEL) +
  ":\\d+:[^\\x1f]*" +
  ")" +
  escapeRegex(SENTINEL_CHAR),
  "g",
);

function escapeRegex(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export type CommandCallback = (result: CommandResult) => void;
export type DisplayCallback = (text: string) => void;

export class SentinelCapture {
  private capturing = false;
  private capturedChunks: string[] = [];
  private cwd = "/home/student";
  private skipCaptures = 1; // Skip bash startup sentinel
  private ready = false;
  private pendingMessages: string[] = [];

  onCommand: CommandCallback | null = null;
  onDisplay: DisplayCallback | null = null;
  onReady: (() => void) | null = null;

  /** Whether the bash prompt is ready (startup sentinel received). */
  get isReady(): boolean {
    return this.ready;
  }

  get currentCwd(): string {
    return this.cwd;
  }

  /**
   * Process incoming serial console text.
   * Strips sentinels, sends display text to onDisplay, and captures
   * command output between CMD_START and CMD_END.
   */
  processOutput(data: string): void {
    const displayParts: string[] = [];
    let lastEnd = 0;

    SENTINEL_RE.lastIndex = 0;
    let match: RegExpExecArray | null;
    while ((match = SENTINEL_RE.exec(data)) !== null) {
      // Data before this sentinel
      const segment = data.slice(lastEnd, match.index);
      if (segment) {
        if (this.capturing) {
          this.capturedChunks.push(segment);
        }
        displayParts.push(segment);
      }

      // Handle the sentinel
      const sentinelBody = match[1];
      if (sentinelBody === CMD_START_SENTINEL) {
        this.capturing = true;
        this.capturedChunks = [];
      } else if (sentinelBody.startsWith(CMD_END_SENTINEL + ":")) {
        const parts = sentinelBody.split(":", 3);
        // parts = ["__CLITUTOR_CMD_END__", "exitcode", "cwd"]
        const exitCode = parts.length > 1 ? parseInt(parts[1], 10) : 0;
        const newCwd = parts.length > 2 ? parts[2] : this.cwd;
        this.cwd = newCwd;
        this.finishCapture(exitCode);
      }

      lastEnd = match.index + match[0].length;
    }

    // Data after the last sentinel
    const tail = data.slice(lastEnd);
    if (tail) {
      if (this.capturing) {
        this.capturedChunks.push(tail);
      }
      displayParts.push(tail);
    }

    // Send clean display text to terminal
    const clean = displayParts.join("");
    if (clean && this.onDisplay) {
      this.onDisplay(clean);
    }
  }

  private finishCapture(exitCode: number): void {
    this.capturing = false;
    const rawChunks = [...this.capturedChunks];
    this.capturedChunks = [];

    // Skip internal captures (bash startup)
    if (this.skipCaptures > 0) {
      this.skipCaptures--;
      if (!this.ready) {
        this.ready = true;
        this.flushPendingMessages();
        this.onReady?.();
      }
      return;
    }

    // Clean output for validation
    let text = rawChunks.join("");
    console.log("[SentinelCapture] raw chunks:", JSON.stringify(rawChunks));
    console.log("[SentinelCapture] joined text:", JSON.stringify(text));

    text = text.replace(ANSI_CSI_RE, "");
    text = text.replace(ANSI_OSC_RE, "");
    text = text.replace(CTRL_CHAR_RE, "");
    console.log("[SentinelCapture] after ANSI/ctrl strip:", JSON.stringify(text));

    // CMD_START fires from PROMPT_COMMAND (before the prompt), so the
    // capture includes the prompt line + echoed user command.  Strip
    // everything up to and including the first newline.
    const nlIdx = text.indexOf("\n");
    if (nlIdx !== -1) {
      text = text.slice(nlIdx + 1);
    }
    console.log("[SentinelCapture] after first-line strip (nlIdx=%d):", nlIdx, JSON.stringify(text));

    const result = createCommandResult({
      stdout: text,
      returncode: exitCode,
      cwd: this.cwd,
    });
    console.log("[SentinelCapture] result:", { stdout: JSON.stringify(result.stdout), returncode: result.returncode, cwd: result.cwd });

    this.onCommand?.(result);
  }

  private flushPendingMessages(): void {
    if (this.pendingMessages.length === 0) return;
    for (const msg of this.pendingMessages) {
      this.onDisplay?.(`\x1b[1;36m  \u25b8 ${msg}\x1b[0m\r\n`);
    }
    this.pendingMessages = [];
  }

  /** Queue a system message for display (before or after ready). */
  queueSystemMessage(text: string): void {
    if (!this.ready) {
      this.pendingMessages.push(text);
      return;
    }
    this.onDisplay?.(`\r\x1b[K\x1b[1;36m  \u25b8 ${text}\x1b[0m\r\n`);
  }

  /** Increment skip counter (e.g., for empty commands from slash command handling). */
  skipNextCapture(): void {
    this.skipCaptures++;
  }

  /** Reset state for sandbox respawn. */
  reset(): void {
    this.capturing = false;
    this.capturedChunks = [];
    this.skipCaptures = 1;
    this.ready = false;
    this.pendingMessages = [];
  }
}
