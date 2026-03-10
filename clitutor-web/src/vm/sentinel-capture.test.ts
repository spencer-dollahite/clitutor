/**
 * Tests for the SentinelCapture serial stream state machine.
 *
 * Uses synthetic sentinel data to verify display output, command callbacks,
 * skip/mute mechanics, and the freeze mechanism that prevents stale seed
 * CMD_ENDs from leaking through during lesson load.
 */

import { describe, it, expect, beforeEach, vi } from "vitest";
import { SentinelCapture } from "./sentinel-capture";
import { CMD_START_SENTINEL, CMD_END_SENTINEL, SENTINEL_CHAR } from "./bashrc";
import type { CommandResult } from "../core/models";

// ── Helpers ──────────────────────────────────────────────────

/** Build a CMD_END sentinel string: \x1f__CLITUTOR_CMD_END__:rc:cwd\x1f */
function cmdEnd(rc = 0, cwd = "/home/student"): string {
  return `${SENTINEL_CHAR}${CMD_END_SENTINEL}:${rc}:${cwd}${SENTINEL_CHAR}`;
}

/** Build a CMD_START sentinel string: \x1f__CLITUTOR_CMD_START__\x1f */
function cmdStart(): string {
  return `${SENTINEL_CHAR}${CMD_START_SENTINEL}${SENTINEL_CHAR}`;
}

/** Simulate the bash startup sentinel (CMD_END + CMD_START) that SentinelCapture expects. */
function bootSentinel(s: SentinelCapture): void {
  s.processOutput(cmdEnd(0) + cmdStart());
}

/** Collect all display output into an array. */
function trackDisplay(s: SentinelCapture): string[] {
  const out: string[] = [];
  s.onDisplay = (text) => out.push(text);
  return out;
}

/** Collect all command results into an array. */
function trackCommands(s: SentinelCapture): CommandResult[] {
  const out: CommandResult[] = [];
  s.onCommand = (result) => out.push(result);
  return out;
}

// ── Tests ────────────────────────────────────────────────────

describe("SentinelCapture", () => {
  let sentinel: SentinelCapture;

  beforeEach(() => {
    sentinel = new SentinelCapture();
  });

  // ── Boot / ready ────────────────────────────────────────────

  describe("boot sequence", () => {
    it("becomes ready after first CMD_END (startup skip)", () => {
      expect(sentinel.isReady).toBe(false);
      bootSentinel(sentinel);
      expect(sentinel.isReady).toBe(true);
    });

    it("fires onReady callback", () => {
      const onReady = vi.fn();
      sentinel.onReady = onReady;
      bootSentinel(sentinel);
      expect(onReady).toHaveBeenCalledOnce();
    });

    it("does not fire onCommand for the startup sentinel", () => {
      const commands = trackCommands(sentinel);
      bootSentinel(sentinel);
      expect(commands).toHaveLength(0);
    });
  });

  // ── Basic capture ───────────────────────────────────────────

  describe("command capture", () => {
    beforeEach(() => {
      bootSentinel(sentinel);
    });

    it("captures command output between CMD_START and CMD_END", () => {
      const commands = trackCommands(sentinel);
      // Simulate: user runs "echo hello" → prompt echo + output + sentinels
      sentinel.processOutput("$ echo hello\nhello\n" + cmdEnd(0) + cmdStart());
      expect(commands).toHaveLength(1);
      expect(commands[0].stdout).toBe("hello\n");
      expect(commands[0].returncode).toBe(0);
    });

    it("captures exit code from CMD_END", () => {
      const commands = trackCommands(sentinel);
      sentinel.processOutput("$ false\n" + cmdEnd(1) + cmdStart());
      expect(commands[0].returncode).toBe(1);
    });

    it("updates cwd from CMD_END", () => {
      sentinel.processOutput("$ cd /tmp\n" + cmdEnd(0, "/tmp") + cmdStart());
      expect(sentinel.currentCwd).toBe("/tmp");
    });

    it("strips ANSI escape sequences from captured output", () => {
      const commands = trackCommands(sentinel);
      sentinel.processOutput("$ ls\n\x1b[1;32mfile.txt\x1b[0m\n" + cmdEnd(0) + cmdStart());
      expect(commands[0].stdout).toBe("file.txt\n");
    });
  });

  // ── Display output ──────────────────────────────────────────

  describe("display output", () => {
    beforeEach(() => {
      bootSentinel(sentinel);
    });

    it("sends non-sentinel text to onDisplay", () => {
      const display = trackDisplay(sentinel);
      sentinel.processOutput("hello world");
      expect(display).toEqual(["hello world"]);
    });

    it("does not send sentinel markers to onDisplay", () => {
      const display = trackDisplay(sentinel);
      sentinel.processOutput("before" + cmdEnd(0) + "after" + cmdStart());
      // Text between sentinels is both captured AND displayed (user sees output).
      // Only the sentinel markers themselves are stripped from display.
      const joined = display.join("");
      expect(joined).toContain("before");
      expect(joined).toContain("after");
      expect(joined).not.toContain(CMD_END_SENTINEL);
      expect(joined).not.toContain(CMD_START_SENTINEL);
      expect(joined).not.toContain(SENTINEL_CHAR);
    });

    it("fires onDisplay BEFORE onCommand", () => {
      const order: string[] = [];
      sentinel.onDisplay = () => order.push("display");
      sentinel.onCommand = () => order.push("command");
      sentinel.processOutput("$ cmd\nout\n" + cmdEnd(0) + "prompt$ " + cmdStart());
      expect(order).toEqual(["display", "command"]);
    });
  });

  // ── skipNextCapture ─────────────────────────────────────────

  describe("skipNextCapture", () => {
    beforeEach(() => {
      bootSentinel(sentinel);
    });

    it("skips the next command callback", () => {
      const commands = trackCommands(sentinel);
      sentinel.skipNextCapture();
      sentinel.processOutput("$ internal\n" + cmdEnd(0) + cmdStart());
      expect(commands).toHaveLength(0);
    });

    it("only skips one capture, next fires normally", () => {
      const commands = trackCommands(sentinel);
      sentinel.skipNextCapture();
      sentinel.processOutput("$ internal\n" + cmdEnd(0) + cmdStart());
      sentinel.processOutput("$ real\noutput\n" + cmdEnd(0) + cmdStart());
      expect(commands).toHaveLength(1);
      expect(commands[0].stdout).toBe("output\n");
    });
  });

  // ── muteUntilNextPrompt ─────────────────────────────────────

  describe("muteUntilNextPrompt + skipNextCapture", () => {
    beforeEach(() => {
      bootSentinel(sentinel);
    });

    it("suppresses display during muted window", () => {
      const display = trackDisplay(sentinel);
      sentinel.muteUntilNextPrompt();
      sentinel.skipNextCapture();
      sentinel.processOutput("stale prompt$ " + cmdEnd(0) + cmdStart());
      // All text before CMD_END should be muted; text after CMD_START is fresh
      expect(display.join("")).toBe("");
    });

    it("restores display after CMD_START following skipped CMD_END", () => {
      const display = trackDisplay(sentinel);
      sentinel.muteUntilNextPrompt();
      sentinel.skipNextCapture();
      sentinel.processOutput("muted" + cmdEnd(0) + cmdStart());
      // Now send normal text — should display
      sentinel.processOutput("visible");
      expect(display.join("")).toBe("visible");
    });

    it("recovers mute after >32 bytes without pending skip", () => {
      const display = trackDisplay(sentinel);
      sentinel.muteUntilNextPrompt();
      // No skipNextCapture — simulates stale mute
      const bigOutput = "x".repeat(50);
      // Feed text in a capturing context (CMD_START already fired from boot)
      sentinel.processOutput(bigOutput);
      // Recovery should have triggered — text after recovery is displayed
      // The recovery happens mid-parse, so the same chunk triggers it
      expect(display.join("").length).toBeGreaterThan(0);
    });
  });

  // ── Freeze / Unfreeze ───────────────────────────────────────

  describe("freeze", () => {
    beforeEach(() => {
      bootSentinel(sentinel);
    });

    it("suppresses display while frozen", () => {
      const display = trackDisplay(sentinel);
      sentinel.freeze();
      sentinel.processOutput("should not appear");
      expect(display).toHaveLength(0);
    });

    it("does not fire onCommand while frozen", () => {
      const commands = trackCommands(sentinel);
      sentinel.freeze();
      sentinel.processOutput("$ cmd\nout\n" + cmdEnd(0) + cmdStart());
      expect(commands).toHaveLength(0);
    });

    it("does NOT consume skipCaptures when frozen", () => {
      const commands = trackCommands(sentinel);
      sentinel.skipNextCapture(); // skipCaptures=1
      sentinel.freeze();
      // Stale CMD_END arrives while frozen — should NOT consume the skip
      sentinel.processOutput("stale\n" + cmdEnd(0) + cmdStart());
      sentinel.unfreeze();
      // The skip should still be available for the real command
      sentinel.processOutput("$ real\noutput\n" + cmdEnd(0) + cmdStart());
      // The skip consumes the real CMD_END, so no onCommand fires
      expect(commands).toHaveLength(0);
      // Next command should fire normally (skip exhausted)
      sentinel.processOutput("$ next\nresult\n" + cmdEnd(0) + cmdStart());
      expect(commands).toHaveLength(1);
      expect(commands[0].stdout).toBe("result\n");
    });

    it("unfreeze clears stale captured data", () => {
      const commands = trackCommands(sentinel);
      sentinel.freeze();
      sentinel.processOutput("stale captured data" + cmdEnd(0) + cmdStart());
      sentinel.unfreeze();
      // Next real command should have clean output, not stale data
      sentinel.processOutput("$ echo clean\nclean\n" + cmdEnd(0) + cmdStart());
      expect(commands).toHaveLength(1);
      expect(commands[0].stdout).toBe("clean\n");
    });

    it("resolves waitForCommand even while frozen", async () => {
      sentinel.freeze();
      const promise = sentinel.waitForCommand();
      sentinel.processOutput(cmdEnd(0) + cmdStart());
      // Should resolve without hanging
      await expect(promise).resolves.toBeUndefined();
    });

    it("system messages bypass freeze", () => {
      // System messages go through displayQueue → onDisplay, not the serial path
      const display = trackDisplay(sentinel);
      sentinel.freeze();
      sentinel.queueSystemMessage("Hello from system");
      // Manually flush (normally done by timer or processOutput)
      sentinel.processOutput("");
      expect(display.join("")).toContain("Hello from system");
    });

    it("unfreeze is idempotent when not frozen", () => {
      const commands = trackCommands(sentinel);
      sentinel.unfreeze(); // should be a no-op
      sentinel.processOutput("$ echo hi\nhi\n" + cmdEnd(0) + cmdStart());
      expect(commands).toHaveLength(1);
    });
  });

  // ── Seed→Lesson transition (integration) ────────────────────

  describe("seed→lesson transition (freeze protects refreshPrompt skip)", () => {
    beforeEach(() => {
      bootSentinel(sentinel);
    });

    it("stale seed CMD_END does not steal refreshPrompt skip slot", () => {
      const commands = trackCommands(sentinel);
      const display = trackDisplay(sentinel);

      // 1. Freeze before lifting serial suppression (as enterLesson does)
      sentinel.freeze();

      // 2. Stale seed CMD_END + CMD_START arrive via serial
      sentinel.processOutput("PS1$ " + cmdEnd(0) + cmdStart());

      // 3. Unfreeze before refreshPrompt
      sentinel.unfreeze();

      // 4. refreshPrompt: mute + skip + send stty
      sentinel.muteUntilNextPrompt();
      sentinel.skipNextCapture();
      const sttyCmd = " stty rows 24 cols 80\n";
      sentinel.processOutput(sttyCmd + cmdEnd(0) + cmdStart());

      // stty CMD_END should be SKIPPED (skip not stolen by frozen CMD_END)
      expect(commands).toHaveLength(0);

      // stty echo should be MUTED (mute not cleared by frozen CMD_END)
      expect(display.join("")).not.toContain("stty");

      // 5. User's first real command should work normally
      sentinel.processOutput("$ echo test\ntest\n" + cmdEnd(0) + cmdStart());
      expect(commands).toHaveLength(1);
      expect(commands[0].stdout).toBe("test\n");
    });

    it("works correctly when no stale CMD_END exists", () => {
      const commands = trackCommands(sentinel);
      const display = trackDisplay(sentinel);

      // 1. Freeze (no stale bytes arrive)
      sentinel.freeze();

      // 2. Unfreeze
      sentinel.unfreeze();

      // 3. refreshPrompt: mute + skip + send stty
      sentinel.muteUntilNextPrompt();
      sentinel.skipNextCapture();
      sentinel.processOutput(" stty rows 24 cols 80\n" + cmdEnd(0) + cmdStart());

      // stty should be skipped and muted
      expect(commands).toHaveLength(0);
      expect(display.join("")).not.toContain("stty");

      // 4. User's first command works
      sentinel.processOutput("$ pwd\n/home/student\n" + cmdEnd(0) + cmdStart());
      expect(commands).toHaveLength(1);
      expect(commands[0].stdout).toBe("/home/student\n");
    });
  });

  // ── Reset ───────────────────────────────────────────────────

  describe("reset", () => {
    it("clears all state including frozen", () => {
      bootSentinel(sentinel);
      sentinel.freeze();
      sentinel.muteUntilNextPrompt();
      sentinel.skipNextCapture();
      sentinel.reset();

      expect(sentinel.isReady).toBe(false);
      // After reset, should need boot sentinel again
      const commands = trackCommands(sentinel);
      bootSentinel(sentinel);
      expect(sentinel.isReady).toBe(true);
      expect(commands).toHaveLength(0); // startup skip consumed
    });
  });

  // ── Partial sentinel split ──────────────────────────────────

  describe("partial sentinel across chunks", () => {
    beforeEach(() => {
      bootSentinel(sentinel);
    });

    it("handles sentinel split across two processOutput calls", () => {
      const commands = trackCommands(sentinel);
      const full = "$ echo hi\nhi\n" + cmdEnd(0) + cmdStart();
      // Split in the middle of the sentinel
      const splitPoint = full.indexOf(SENTINEL_CHAR) + 5;
      sentinel.processOutput(full.slice(0, splitPoint));
      sentinel.processOutput(full.slice(splitPoint));
      expect(commands).toHaveLength(1);
      expect(commands[0].stdout).toBe("hi\n");
    });
  });
});
