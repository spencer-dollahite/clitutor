/**
 * App shell — lesson picker landing screen.
 *
 * User sees a lesson picker dashboard on page load.
 * VM only boots when the user selects a lesson.
 * Lesson content lives in a collapsible sidebar panel.
 */

import type { LessonMeta, LessonData, CommandResult } from "../core/models";
import { LessonLoader } from "../core/lesson-loader";
import { ProgressManager } from "../core/progress";
import { LinuxVM } from "../vm/linux-vm";
import { SentinelCapture } from "../vm/sentinel-capture";
import { OutputValidator } from "../core/validator";
import { calculateXp } from "../core/xp";
import { getLevelInfo, levelProgress, xpInLevel, xpForLevel } from "../core/xp";
import { TerminalPane } from "./components/terminal-pane";
import { MarkdownPane } from "./components/markdown-pane";
import { HintOverlay } from "./components/hint-overlay";
import { LessonPicker } from "./screens/lesson-picker";
import { showToast } from "./toast";

export class App {
  private root: HTMLElement;
  private vm: LinuxVM | null = null;
  private loader: LessonLoader;
  private progress: ProgressManager;
  private sentinel: SentinelCapture;
  private validator: OutputValidator | null = null;
  private terminalPane: TerminalPane | null = null;
  private markdownPane: MarkdownPane | null = null;
  private hintOverlay: HintOverlay;
  private picker: LessonPicker | null = null;

  // Lesson state
  private lessonsMeta: LessonMeta[] = [];
  private currentLesson: LessonData | null = null;
  private currentExercise = 0;
  private sidebarOpen = false;
  private sidebarMode: "lessons" | "content" = "lessons";

  // DOM refs
  private termContainer: HTMLElement | null = null;
  private sidebar: HTMLElement | null = null;
  private sidebarContent: HTMLElement | null = null;
  private exerciseBar: HTMLElement | null = null;
  private statusBar: HTMLElement | null = null;
  private bootOverlay: HTMLElement | null = null;
  private appMain: HTMLElement | null = null;

  constructor(root: HTMLElement) {
    this.root = root;
    this.loader = new LessonLoader("/lessons");
    this.progress = new ProgressManager();
    this.sentinel = new SentinelCapture();
    this.hintOverlay = new HintOverlay();
  }

  async start(): Promise<void> {
    console.log("[App] start() called");

    // Init progress DB and load lesson metadata — no VM boot yet
    console.log("[App] Initializing progress DB...");
    await this.progress.init();
    console.log("[App] Progress DB initialized");

    console.log("[App] Loading lesson metadata...");
    this.lessonsMeta = await this.loader.loadMetadata();
    console.log("[App] Loaded %d lessons", this.lessonsMeta.length, this.lessonsMeta);

    // Show the lesson picker as the landing screen
    console.log("[App] Showing lesson picker");
    this.showPicker();

    // Listen for XP updates
    document.addEventListener("xp-updated", () => {
      console.log("[App] xp-updated event received");
      this.updateStatusBar();
      this.picker?.refresh();
    });
  }

  // ── Picker (landing screen) ──────────────────────────────────────

  private showPicker(): void {
    console.log("[App] showPicker(): clearing root, creating LessonPicker");
    this.root.innerHTML = "";
    this.picker = new LessonPicker(
      this.lessonsMeta,
      this.progress,
      (meta) => this.enterLesson(meta),
    );
    this.picker.render(this.root);
    console.log("[App] showPicker(): picker rendered");
  }

  private async enterLesson(meta: LessonMeta): Promise<void> {
    console.log("[App] enterLesson() called for:", meta.id, meta.title);

    // Destroy picker
    console.log("[App] Destroying picker");
    this.picker?.destroy();
    this.picker = null;

    // Render terminal layout
    console.log("[App] Rendering terminal layout");
    this.renderLayout();
    console.log("[App] Terminal layout rendered, terminalPane:", !!this.terminalPane);

    // Show boot overlay and boot VM
    console.log("[App] Showing boot overlay");
    this.showBootOverlay();

    console.log("[App] Starting VM boot...");
    const bootStart = performance.now();
    try {
      await this.bootVM();
      console.log("[App] VM boot complete in %dms", Math.round(performance.now() - bootStart));
    } catch (err) {
      console.error("[App] VM boot FAILED:", err);
      throw err;
    }

    // Pre-load lesson and seed files while overlay is still showing
    console.log("[App] Pre-loading and seeding lesson:", meta.id);
    const lesson = await this.loader.loadLesson(meta);
    await this.seedLessonSetup(lesson);

    // Clear xterm.js display directly (synchronous, no serial race)
    this.terminalPane?.term.write('\x1b[2J\x1b[H');

    // VM is ready — hide boot overlay, focus terminal
    console.log("[App] Hiding boot overlay, focusing terminal");
    this.hideBootOverlay();
    this.terminalPane?.focus();

    // Set up lesson UI (pass pre-loaded lesson to skip re-seeding)
    console.log("[App] Opening lesson by meta:", meta.id);
    await this.openLessonByMeta(meta, lesson);

    // Trigger a fresh bash prompt below the messages
    this.sentinel.skipNextCapture();
    this.vm?.sendSerial('\n');
    console.log("[App] enterLesson() complete");
  }

  private backToPicker(): void {
    console.log("[App] backToPicker(): destroying VM and layout");
    // Destroy VM
    if (this.vm) {
      this.vm.destroy();
      this.vm = null;
      this.validator = null;
    }

    // Destroy terminal layout
    this.terminalPane = null;
    this.markdownPane = null;
    this.termContainer = null;
    this.sidebar = null;
    this.sidebarContent = null;
    this.exerciseBar = null;
    this.statusBar = null;
    this.appMain = null;
    this.currentLesson = null;
    this.currentExercise = 0;
    this.sidebarOpen = false;

    // Show picker with updated progress
    console.log("[App] backToPicker(): showing picker");
    this.showPicker();
  }

  // ── Layout ────────────────────────────────────────────────────────

  private renderLayout(): void {
    this.root.innerHTML = "";

    // Main container: sidebar + terminal
    this.appMain = document.createElement("div");
    this.appMain.className = "app-main";
    this.root.appendChild(this.appMain);

    // Sidebar (hidden by default)
    this.sidebar = document.createElement("div");
    this.sidebar.className = "sidebar";
    this.sidebar.innerHTML = `
      <div class="sidebar-header">
        <span class="sidebar-title">CLItutor</span>
        <button class="sidebar-close" id="sidebar-close">&times;</button>
      </div>
      <div class="sidebar-body" id="sidebar-body"></div>
    `;
    this.appMain.appendChild(this.sidebar);

    this.sidebarContent = this.sidebar.querySelector("#sidebar-body")!;
    this.sidebar.querySelector("#sidebar-close")!.addEventListener("click", () =>
      this.toggleSidebar(false),
    );

    // Terminal area (takes full width when sidebar closed)
    const termArea = document.createElement("div");
    termArea.className = "term-area";
    this.appMain.appendChild(termArea);

    // Terminal container
    this.termContainer = document.createElement("div");
    this.termContainer.className = "term-container";
    termArea.appendChild(this.termContainer);

    // Exercise bar (bottom, hidden when no lesson active)
    this.exerciseBar = document.createElement("div");
    this.exerciseBar.className = "exercise-bar hidden";
    termArea.appendChild(this.exerciseBar);

    // Status bar (very bottom)
    this.statusBar = document.createElement("div");
    this.statusBar.className = "status-bar";
    termArea.appendChild(this.statusBar);

    // Create terminal pane
    this.terminalPane = new TerminalPane(this.termContainer);
    this.terminalPane.onSlashCommand = (cmd) => this.handleSlashCommand(cmd);
  }

  private bootTimer: ReturnType<typeof setInterval> | null = null;

  private showBootOverlay(): void {
    this.bootOverlay = document.createElement("div");
    this.bootOverlay.className = "boot-overlay";
    this.bootOverlay.innerHTML = `
      <div class="boot-content">
        <pre class="boot-ascii">
   ____ _     ___ _         _
  / ___| |   |_ _| |_ _   _| |_ ___  _ __
 | |   | |    | || __| | | | __/ _ \\| '__|
 | |___| |___ | || |_| |_| | || (_) | |
  \\____|_____|___|\\__|\\__,_|\\__\\___/|_|
        </pre>
        <div class="boot-progress-wrap">
          <div class="boot-progress-bar">
            <div class="boot-progress-fill" id="boot-progress-fill"></div>
          </div>
        </div>
        <div class="boot-status">
          <div class="loading-spinner"></div>
          <span id="boot-message">Booting Linux...</span>
        </div>
        <div class="boot-hint" id="boot-hint">First boot may take up to 30 seconds</div>
      </div>
    `;
    this.root.appendChild(this.bootOverlay);

    // Animate the progress bar over ~30s
    const startTime = performance.now();
    const duration = 30000;
    const fill = this.bootOverlay.querySelector("#boot-progress-fill") as HTMLElement;
    const hint = this.bootOverlay.querySelector("#boot-hint") as HTMLElement;
    const msg = this.bootOverlay.querySelector("#boot-message") as HTMLElement;

    const phases = [
      { at: 0, text: "Booting Linux..." },
      { at: 3000, text: "Loading kernel..." },
      { at: 8000, text: "Starting system..." },
      { at: 15000, text: "Waiting for shell..." },
      { at: 25000, text: "Almost there..." },
    ];
    let phaseIdx = 0;

    this.bootTimer = setInterval(() => {
      const elapsed = performance.now() - startTime;
      // Ease-out: fast start, slows toward 95%
      const raw = Math.min(elapsed / duration, 1);
      const pct = Math.min(95, raw * 100 * (2 - raw));
      if (fill) fill.style.width = `${Math.round(pct)}%`;

      // Update phase message
      while (phaseIdx < phases.length && elapsed >= phases[phaseIdx].at) {
        if (msg) msg.textContent = phases[phaseIdx].text;
        phaseIdx++;
      }

      // After 10s, update hint
      if (elapsed > 10000 && hint) {
        hint.textContent = "Hang tight — the VM is booting";
      }
    }, 200);
  }

  private hideBootOverlay(): void {
    // Stop progress timer
    if (this.bootTimer) {
      clearInterval(this.bootTimer);
      this.bootTimer = null;
    }

    if (this.bootOverlay) {
      // Fill the bar to 100% before fading
      const fill = this.bootOverlay.querySelector("#boot-progress-fill") as HTMLElement;
      if (fill) fill.style.width = "100%";

      setTimeout(() => {
        this.bootOverlay?.classList.add("fade-out");
        setTimeout(() => {
          this.bootOverlay?.remove();
          this.bootOverlay = null;
        }, 500);
      }, 300);
    }
  }

  private updateBootMessage(msg: string): void {
    const el = document.getElementById("boot-message");
    if (el) el.textContent = msg;
  }

  // ── VM Boot ───────────────────────────────────────────────────────

  private async bootVM(): Promise<void> {
    console.log("[App.bootVM] Creating LinuxVM instance");
    this.vm = new LinuxVM();
    this.validator = new OutputValidator(this.vm);

    // Wire sentinel capture
    console.log("[App.bootVM] Wiring sentinel capture callbacks");
    this.sentinel.onDisplay = (text) => this.terminalPane?.write(text);
    this.sentinel.onCommand = (result) => this.handleCommand(result);
    this.sentinel.onReady = () => {
      console.log("[App.bootVM] sentinel.onReady fired");
    };

    // Boot VM with serial output flowing to sentinel parser
    let buffer = "";
    let flushTimer: ReturnType<typeof setTimeout> | null = null;
    let byteCount = 0;

    const flushBuffer = () => {
      if (flushTimer) { clearTimeout(flushTimer); flushTimer = null; }
      if (buffer) {
        this.sentinel.processOutput(buffer);
        buffer = "";
      }
    };

    console.log("[App.bootVM] Calling vm.boot()...");
    await this.vm.boot((byte: number) => {
      byteCount++;
      if (byteCount <= 5 || byteCount % 1000 === 0) {
        console.log("[App.bootVM] serial byte #%d: %s", byteCount, JSON.stringify(String.fromCharCode(byte)));
      }
      buffer += String.fromCharCode(byte);
      // Flush immediately on newlines or large buffers; otherwise
      // schedule a short-delay flush so echo chars appear promptly.
      if (byte === 10 || byte === 13 || buffer.length > 128) {
        flushBuffer();
      } else if (!flushTimer) {
        flushTimer = setTimeout(flushBuffer, 4);
      }
    });
    console.log("[App.bootVM] vm.boot() resolved, total serial bytes so far: %d", byteCount);

    // Attach terminal to VM for keyboard input
    console.log("[App.bootVM] Attaching terminal pane to VM");
    this.terminalPane?.attach(this.vm);

    this.updateBootMessage("Waiting for shell...");
    console.log("[App.bootVM] Calling vm.waitForShell()...");

    await this.vm.waitForShell();
    console.log("[App.bootVM] waitForShell() resolved — shell is ready");
  }

  // ── Command handling ──────────────────────────────────────────────

  private async handleCommand(result: CommandResult): Promise<void> {
    if (!this.currentLesson) return;
    if (this.currentExercise >= this.currentLesson.exercises.length) return;

    const exercise = this.currentLesson.exercises[this.currentExercise];
    exercise.attempts++;

    const validation = await this.validator!.validate(exercise, result);

    if (validation.passed) {
      exercise.completed = true;
      const xp = calculateXp(
        exercise.xp,
        exercise.difficulty,
        exercise.first_try,
        exercise.hints_used,
      );

      await this.progress.recordExercise(
        this.currentLesson.id,
        exercise.id,
        xp,
        exercise.attempts,
        exercise.hints_used,
      );

      showToast(`+${xp} XP — ${exercise.title}`, "success");
      this.sentinel.queueSystemMessage(`\u2713 ${exercise.title} — +${xp} XP`);

      this.currentExercise++;
      this.updateExerciseBar();
      this.updateStatusBar();
      document.dispatchEvent(new CustomEvent("xp-updated"));

      if (this.currentExercise < this.currentLesson.exercises.length) {
        const next = this.currentLesson.exercises[this.currentExercise];
        this.sentinel.queueSystemMessage(`Next: ${next.title}`);
        this.markdownPane?.scrollToExercise(this.currentExercise + 1);
      } else {
        this.sentinel.queueSystemMessage(
          `\u2605 Lesson complete: ${this.currentLesson.title}! Type /lessons for more.`,
        );
        showToast(`Lesson complete: ${this.currentLesson.title}!`, "success");
      }
    } else {
      exercise.first_try = false;
      this.sentinel.queueSystemMessage(validation.message);
    }
  }

  // ── Slash commands ────────────────────────────────────────────────

  private handleSlashCommand(cmd: string): void {
    this.sentinel.skipNextCapture();
    const parts = cmd.toLowerCase().split(/\s+/);
    const command = parts[0];

    switch (command) {
      case "/help":
        this.showHelp();
        break;
      case "/lessons":
        this.toggleSidebar(true);
        this.showLessonList();
        break;
      case "/lesson": {
        const num = parseInt(parts[1], 10);
        if (!isNaN(num)) this.openLessonByNumber(num);
        else this.sentinel.queueSystemMessage("Usage: /lesson <number>");
        break;
      }
      case "/hint":
        this.showHint();
        break;
      case "/skip":
        this.skipExercise();
        break;
      case "/reset":
        this.resetSandbox();
        break;
      case "/status":
        this.showStatus();
        break;
      case "/sidebar":
        this.toggleSidebar(!this.sidebarOpen);
        break;
      case "/close":
        this.toggleSidebar(false);
        break;
      case "/back":
        this.backToPicker();
        break;
      default:
        this.sentinel.queueSystemMessage(
          `Unknown: ${cmd}. Type /help for commands.`,
        );
    }
  }

  private showHelp(): void {
    const lines = [
      "Available commands:",
      "  /lessons        — Browse lesson list",
      "  /lesson <num>   — Start lesson (e.g., /lesson 0)",
      "  /hint           — Get a hint for current exercise",
      "  /skip           — Skip current exercise",
      "  /reset          — Reset lesson files to starting state",
      "  /status         — Show XP and progress",
      "  /sidebar        — Toggle lesson sidebar",
      "  /close          — Close sidebar",
      "  /back           — Back to lesson picker",
    ];
    for (const line of lines) {
      this.sentinel.queueSystemMessage(line);
    }
  }

  private showStatus(): void {
    const totalXp = this.progress.totalXp;
    const info = getLevelInfo(totalXp);
    const completed = this.progress.completedLessons.size;
    this.sentinel.queueSystemMessage(
      `Level ${info.level} "${info.title}" | ${totalXp} XP | ${completed}/${this.lessonsMeta.length} lessons`,
    );
    if (this.currentLesson) {
      this.sentinel.queueSystemMessage(
        `Current: ${this.currentLesson.title} — Exercise ${this.currentExercise + 1}/${this.currentLesson.exercises.length}`,
      );
    }
  }

  // ── Lesson management ─────────────────────────────────────────────

  private showLessonList(): void {
    this.sidebarMode = "lessons";
    if (!this.sidebarContent) return;

    const completed = this.progress.completedLessons;
    const exerciseProg = this.progress.exerciseProgress();

    let html = `<div class="lesson-list-sidebar">`;
    for (const meta of this.lessonsMeta) {
      const isDone = completed.has(meta.id);
      const doneCount = exerciseProg[meta.id] ?? 0;
      const cls = isDone ? "sidebar-lesson-item completed" : "sidebar-lesson-item";
      const check = isDone ? '<span class="check">\u2713</span>' : "";
      const prog =
        doneCount > 0 && !isDone ? ` (${doneCount}/${meta.exercise_count})` : "";

      html += `
        <div class="${cls}" data-order="${meta.order}">
          <span class="lesson-num">${String(meta.order).padStart(2, "0")}</span>
          <span class="lesson-name">${this.escapeHtml(meta.title)}${prog}</span>
          <span class="lesson-xp">${meta.xp} XP ${check}</span>
        </div>
      `;
    }
    html += `</div>`;
    this.sidebarContent.innerHTML = html;

    // Click handlers
    this.sidebarContent.querySelectorAll(".sidebar-lesson-item").forEach((el) => {
      el.addEventListener("click", () => {
        const order = parseInt((el as HTMLElement).dataset.order!, 10);
        this.openLessonByNumber(order);
      });
    });
  }

  private async openLessonByNumber(num: number): Promise<void> {
    const meta = this.lessonsMeta.find((m) => m.order === num);
    if (!meta) {
      this.sentinel.queueSystemMessage(`Lesson ${num} not found.`);
      return;
    }
    await this.openLessonByMeta(meta);
  }

  private async openLessonByMeta(
    meta: LessonMeta,
    preloaded?: LessonData,
  ): Promise<void> {
    const lesson = preloaded ?? await this.loader.loadLesson(meta);
    this.currentLesson = lesson;

    // Restore progress
    this.currentExercise = 0;
    for (let i = 0; i < lesson.exercises.length; i++) {
      const ex = lesson.exercises[i];
      if (this.progress.isExerciseCompleted(lesson.id, ex.id)) {
        ex.completed = true;
        this.currentExercise = i + 1;
      }
    }
    if (this.currentExercise >= lesson.exercises.length) {
      this.currentExercise = Math.max(0, lesson.exercises.length - 1);
    }

    // Seed lesson files silently when switching lessons (not pre-seeded)
    if (!preloaded) {
      await this.seedLessonSetup(lesson, true);
      this.terminalPane?.term.write('\x1b[2J\x1b[H');
    }

    // Show lesson content in sidebar
    this.sidebarMode = "content";
    this.showLessonContent();
    this.toggleSidebar(true);

    // Show exercise bar
    this.updateExerciseBar();
    this.updateStatusBar();

    // Announce
    this.sentinel.queueSystemMessage(
      `\u2500\u2500 ${lesson.title} \u2500\u2500`,
    );
    if (this.currentExercise < lesson.exercises.length) {
      const ex = lesson.exercises[this.currentExercise];
      this.sentinel.queueSystemMessage(`Exercise ${this.currentExercise + 1}: ${ex.title}`);
    } else {
      this.sentinel.queueSystemMessage("All exercises complete!");
    }

    // Trigger fresh prompt after messages
    this.sentinel.skipNextCapture();
    this.vm?.sendSerial('\n');

    this.terminalPane?.focus();
  }

  private showLessonContent(): void {
    if (!this.sidebarContent || !this.currentLesson) return;

    // Clear and render markdown
    this.sidebarContent.innerHTML = `
      <div class="sidebar-lesson-header">
        <button class="btn sidebar-back" id="sidebar-back">\u2190 All Lessons</button>
      </div>
      <div class="sidebar-markdown"></div>
    `;

    this.sidebarContent.querySelector("#sidebar-back")!.addEventListener("click", () =>
      this.showLessonList(),
    );

    const mdContainer = this.sidebarContent.querySelector(".sidebar-markdown")!;
    this.markdownPane = new MarkdownPane(mdContainer as HTMLElement);
    this.markdownPane.render(this.currentLesson.content_markdown);
  }

  /**
   * Seed all exercise files for an entire lesson at once, silently.
   * Uses create_file() to write a script (invisible), then executes
   * it with display muted so nothing appears in the terminal.
   *
   * @param clean  If true, remove existing /root files first (for lesson switch / reset).
   */
  private async seedLessonSetup(lesson: LessonData, clean = false): Promise<void> {
    if (!this.vm) return;

    const commands: string[] = [];
    if (clean) {
      commands.push("cd /root && rm -rf /root/* /root/.* 2>/dev/null");
    }
    for (const ex of lesson.exercises) {
      if (ex.sandbox_setup && ex.sandbox_setup.length > 0) {
        commands.push("cd /root");
        commands.push(...ex.sandbox_setup);
      }
    }
    if (commands.length === 0) return;

    console.log("[App] seedLessonSetup: %d commands, clean=%s", commands.length, clean);

    // Mute terminal display during seeding
    const origDisplay = this.sentinel.onDisplay;
    this.sentinel.onDisplay = () => {};

    // Skip sentinel capture for the seed script command
    this.sentinel.skipNextCapture();

    // Write seed commands as a script via filesystem API (invisible)
    const script = commands.join("\n") + "\n";
    await this.vm.writeFile("/tmp/_clitutor_seed.sh", script);
    this.vm.sendSerial(
      "bash /tmp/_clitutor_seed.sh >/dev/null 2>&1; rm -f /tmp/_clitutor_seed.sh\n",
    );

    // Wait for execution (longer for git operations)
    const hasGit = commands.some((c) => c.includes("git"));
    await new Promise((r) => setTimeout(r, hasGit ? 3000 : 800));

    // Unmute display (no serial clear — it races with message display)
    this.sentinel.onDisplay = origDisplay;
  }

  private showHint(): void {
    if (!this.currentLesson || this.currentExercise >= this.currentLesson.exercises.length) {
      this.sentinel.queueSystemMessage("No active exercise. Type /lessons to start.");
      return;
    }
    const exercise = this.currentLesson.exercises[this.currentExercise];
    exercise.hints_used = Math.min(exercise.hints_used + 1, exercise.hints.length);
    this.hintOverlay.show(exercise);
  }

  private skipExercise(): void {
    if (!this.currentLesson || this.currentExercise >= this.currentLesson.exercises.length) return;
    this.sentinel.queueSystemMessage(
      `Skipped: ${this.currentLesson.exercises[this.currentExercise].title}`,
    );
    this.currentExercise++;
    this.updateExerciseBar();

    if (this.currentExercise < this.currentLesson.exercises.length) {
      const next = this.currentLesson.exercises[this.currentExercise];
      this.sentinel.queueSystemMessage(`Next: ${next.title}`);
    }
  }

  private async resetSandbox(): Promise<void> {
    if (!this.vm || !this.currentLesson) return;
    this.sentinel.queueSystemMessage("Resetting sandbox...");
    await this.seedLessonSetup(this.currentLesson, true);
    this.terminalPane?.term.write('\x1b[2J\x1b[H');
    this.sentinel.queueSystemMessage("Sandbox reset.");
    this.sentinel.skipNextCapture();
    this.vm.sendSerial('\n');
  }

  // ── UI updates ────────────────────────────────────────────────────

  private toggleSidebar(open: boolean): void {
    this.sidebarOpen = open;
    if (this.sidebar) {
      this.sidebar.classList.toggle("open", open);
    }
    // Refit terminal after sidebar animation
    setTimeout(() => this.terminalPane?.fit(), 350);
  }

  private updateExerciseBar(): void {
    if (!this.exerciseBar) return;

    if (!this.currentLesson) {
      this.exerciseBar.classList.add("hidden");
      return;
    }

    this.exerciseBar.classList.remove("hidden");
    const lesson = this.currentLesson;

    let dotsHtml = "";
    for (let i = 0; i < lesson.exercises.length; i++) {
      const ex = lesson.exercises[i];
      let cls = "exercise-dot";
      if (ex.completed || this.progress.isExerciseCompleted(lesson.id, ex.id)) {
        cls += " completed";
      } else if (i === this.currentExercise) {
        cls += " active";
      }
      dotsHtml += `<div class="${cls}"></div>`;
    }

    const ex =
      this.currentExercise < lesson.exercises.length
        ? lesson.exercises[this.currentExercise]
        : null;

    this.exerciseBar.innerHTML = `
      <div class="exercise-dots">${dotsHtml}</div>
      <span class="exercise-title">${
        ex
          ? `${this.currentExercise + 1}/${lesson.exercises.length}: ${this.escapeHtml(ex.title)}`
          : "All exercises complete!"
      }</span>
      ${ex ? `<span class="exercise-xp-label">${ex.xp} XP</span>` : ""}
      ${ex ? '<button class="hint-btn" id="hint-btn">/hint</button>' : ""}
    `;

    this.exerciseBar.querySelector("#hint-btn")?.addEventListener("click", () =>
      this.showHint(),
    );
  }

  private updateStatusBar(): void {
    if (!this.statusBar) return;
    const totalXp = this.progress.totalXp;
    const info = getLevelInfo(totalXp);
    const prog = levelProgress(info);
    const completed = this.progress.completedLessons.size;

    this.statusBar.innerHTML = `
      <span class="status-level">Lv.${info.level} ${info.title}</span>
      <div class="status-xp-bar">
        <div class="status-xp-fill" style="width:${Math.round(prog * 100)}%"></div>
      </div>
      <span class="status-xp">${totalXp} XP</span>
      <span class="status-lessons">${completed}/${this.lessonsMeta.length} lessons</span>
      <span class="status-spacer"></span>
      <button class="status-btn" id="status-back">&#8592; Lessons</button>
    `;

    this.statusBar.querySelector("#status-back")?.addEventListener("click", () => {
      this.backToPicker();
    });
  }

  private escapeHtml(text: string): string {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}
