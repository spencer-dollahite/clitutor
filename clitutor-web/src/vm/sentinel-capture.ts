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
  private displayQueue: string[] = [];
  private flushTimer: ReturnType<typeof setTimeout> | null = null;
  private partialBuffer = "";
  private partialTimer: ReturnType<typeof setTimeout> | null = null;

  /**
   * When true, serial display output is suppressed (old prompt bytes still in
   * the serial pipeline are hidden).  Cleared when the next CMD_START sentinel
   * arrives, signalling the start of a fresh prompt cycle.
   *
   * System messages (via displayQueue / flushDisplayQueue) bypass this flag
   * because they write through a separate path.
   */
  private muteSerial = false;

  /**
   * Resolve function for waitForCommand().  Set when a caller is waiting for
   * the next CMD_END sentinel to signal shell command completion.
   */
  private commandWaiter: (() => void) | null = null;

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
   *
   * IMPORTANT: Display text is written BEFORE command callbacks fire.
   * This ensures the prompt (which follows CMD_START) is rendered before
   * handleCommand can mute onDisplay for validation.
   */
  processOutput(data: string): void {
    // Flush any buffered system messages BEFORE processing new serial data.
    // This prevents system message ANSI codes from interleaving with
    // prompt ANSI sequences mid-parse in xterm.js.
    this.flushDisplayQueue();

    // Prepend any buffered partial sentinel from a previous call
    if (this.partialBuffer) {
      data = this.partialBuffer + data;
      this.partialBuffer = "";
    }
    if (this.partialTimer) {
      clearTimeout(this.partialTimer);
      this.partialTimer = null;
    }

    const displayParts: string[] = [];
    const pendingResults: CommandResult[] = [];
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
        // When muteSerial is active, suppress stale serial display bytes
        // (old prompt remnants still in the pipeline). Capture data is
        // unaffected so the sentinel state machine stays consistent.
        if (!this.muteSerial) {
          displayParts.push(segment);
        }
      }

      // Handle the sentinel
      const sentinelBody = match[1];
      console.log("[SentinelCapture] processOutput: sentinel=%s capturing=%s skipCaptures=%d ready=%s muteSerial=%s",
        sentinelBody.slice(0, 60), this.capturing, this.skipCaptures, this.ready, this.muteSerial);
      if (sentinelBody === CMD_START_SENTINEL) {
        // CMD_START marks the beginning of a fresh prompt cycle.
        // Clear muteSerial so the new PS1 prompt renders normally.
        if (this.muteSerial) {
          this.muteSerial = false;
          console.log("[SentinelCapture] CMD_START: cleared muteSerial");
        }
        this.capturing = true;
        this.capturedChunks = [];
      } else if (sentinelBody.startsWith(CMD_END_SENTINEL + ":")) {
        const parts = sentinelBody.split(":", 3);
        // parts = ["__CLITUTOR_CMD_END__", "exitcode", "cwd"]
        const exitCode = parts.length > 1 ? parseInt(parts[1], 10) : 0;
        const newCwd = parts.length > 2 ? parts[2] : this.cwd;
        this.cwd = newCwd;
        const result = this.finishCapture(exitCode);
        if (result) pendingResults.push(result);
      }

      lastEnd = match.index + match[0].length;
    }

    // Data after the last sentinel — check for a partial sentinel split
    // across serial chunks. \x1f only appears as a sentinel delimiter, so
    // any trailing \x1f means a sentinel started but didn't finish yet.
    const tail = data.slice(lastEnd);
    if (tail) {
      const sentIdx = tail.indexOf(SENTINEL_CHAR);
      if (sentIdx !== -1) {
        // Text before the \x1f is safe to display/capture
        const safe = tail.slice(0, sentIdx);
        if (safe) {
          if (this.capturing) this.capturedChunks.push(safe);
          if (!this.muteSerial) displayParts.push(safe);
        }
        // Buffer from \x1f onward for next processOutput call
        this.partialBuffer = tail.slice(sentIdx);
        // Safety: flush after 50ms if no more data arrives (not a real sentinel)
        this.partialTimer = setTimeout(() => {
          this.partialTimer = null;
          if (this.partialBuffer) {
            const buf = this.partialBuffer;
            this.partialBuffer = "";
            if (this.capturing) this.capturedChunks.push(buf);
            if (!this.muteSerial) this.onDisplay?.(buf);
          }
        }, 50);
      } else {
        if (this.capturing) this.capturedChunks.push(tail);
        if (!this.muteSerial) displayParts.push(tail);
      }
    }

    // Display text FIRST — ensures the prompt is written to the terminal
    // before any command callback can mute onDisplay for validation.
    const clean = displayParts.join("");
    if (clean && this.onDisplay) {
      this.onDisplay(clean);
    }

    // THEN fire command callbacks
    if (pendingResults.length > 0) {
      console.log("[SentinelCapture] processOutput: firing %d command callback(s)", pendingResults.length);
    }
    for (const result of pendingResults) {
      console.log("[SentinelCapture] firing onCommand: stdout=%s rc=%d cwd=%s",
        JSON.stringify(result.stdout.slice(0, 80)), result.returncode, result.cwd);
      this.onCommand?.(result);
    }
  }

  /**
   * Finish a capture and return the cleaned result (or null if skipped).
   */
  private finishCapture(exitCode: number): CommandResult | null {
    this.capturing = false;
    const rawChunks = [...this.capturedChunks];
    this.capturedChunks = [];

    console.log("[SentinelCapture] finishCapture: exitCode=%d skipCaptures=%d rawChunks=%d ready=%s",
      exitCode, this.skipCaptures, rawChunks.length, this.ready);

    // Resolve any pending waitForCommand() caller.  This fires for every
    // CMD_END — both skipped (internal) and real commands — which is correct
    // because the waiter just needs to know the shell finished *something*.
    if (this.commandWaiter) {
      const resolve = this.commandWaiter;
      this.commandWaiter = null;
      resolve();
    }

    // Skip internal captures (bash startup)
    if (this.skipCaptures > 0) {
      this.skipCaptures--;
      console.log("[SentinelCapture] SKIPPED capture (skipCaptures now %d)", this.skipCaptures);
      if (!this.ready) {
        this.ready = true;
        this.flushPendingMessages();
        this.onReady?.();
      }
      return null;
    }

    // Clean output for validation
    let text = rawChunks.join("");
    text = text.replace(ANSI_CSI_RE, "");
    text = text.replace(ANSI_OSC_RE, "");
    text = text.replace(CTRL_CHAR_RE, "");

    // CMD_START fires from PROMPT_COMMAND (before the prompt), so the
    // capture includes the prompt line + echoed user command.  Strip
    // everything up to and including the first newline.
    const nlIdx = text.indexOf("\n");
    if (nlIdx !== -1) {
      text = text.slice(nlIdx + 1);
    }

    return createCommandResult({
      stdout: text,
      returncode: exitCode,
      cwd: this.cwd,
    });
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
    // Buffer the message instead of writing directly to avoid interleaving
    // with serial data (which can corrupt ANSI sequences in xterm.js).
    this.displayQueue.push(`\r\x1b[K\x1b[1;36m  \u25b8 ${text}\x1b[0m\r\n`);
    this.scheduleFlush();
  }

  /** Schedule a flush for when no serial data arrives soon. */
  private scheduleFlush(): void {
    if (this.flushTimer) return;
    this.flushTimer = setTimeout(() => {
      this.flushTimer = null;
      this.flushDisplayQueue();
    }, 8);
  }

  /** Write all buffered system messages to the terminal at once. */
  private flushDisplayQueue(): void {
    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }
    if (this.displayQueue.length === 0) return;
    const batch = this.displayQueue.join("");
    this.displayQueue = [];
    this.onDisplay?.(batch);
  }

  /**
   * Suppress serial display output until the next CMD_START sentinel.
   *
   * After validation fires system messages (which use \r\x1b[K to overwrite
   * the current terminal line), old prompt bytes may still be in the serial
   * pipeline.  This flag prevents those stale bytes from rendering.
   *
   * The flag is cleared deterministically when CMD_START is processed — no
   * timers, no guessing.  System messages (displayQueue) are unaffected
   * because they write through flushDisplayQueue, not through displayParts.
   */
  muteUntilNextPrompt(): void {
    this.muteSerial = true;
    console.log("[SentinelCapture] muteUntilNextPrompt: muteSerial=true");
  }

  /**
   * Returns a Promise that resolves when the next CMD_END sentinel is
   * processed by finishCapture.  Used to wait for shell command completion
   * (e.g. seed scripts) without hardcoded timers.
   *
   * The sentinel state machine itself signals completion — deterministic,
   * not timing-based.  If the command never completes (VM hung), the
   * Promise never resolves; callers can race with a timeout if needed.
   */
  waitForCommand(): Promise<void> {
    return new Promise((resolve) => {
      this.commandWaiter = resolve;
    });
  }

  /** Increment skip counter (e.g., for empty commands from slash command handling). */
  skipNextCapture(): void {
    this.skipCaptures++;
    console.log("[SentinelCapture] skipNextCapture: skipCaptures now=%d", this.skipCaptures);
  }

  /** Reset state for sandbox respawn. */
  reset(): void {
    console.log("[SentinelCapture] reset: clearing all state, skipCaptures=1");
    this.capturing = false;
    this.capturedChunks = [];
    this.skipCaptures = 1;
    this.ready = false;
    this.muteSerial = false;
    this.commandWaiter = null;
    this.pendingMessages = [];
    this.displayQueue = [];
    this.partialBuffer = "";
    if (this.flushTimer) {
      clearTimeout(this.flushTimer);
      this.flushTimer = null;
    }
    if (this.partialTimer) {
      clearTimeout(this.partialTimer);
      this.partialTimer = null;
    }
  }
}
