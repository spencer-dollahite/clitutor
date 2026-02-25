/**
 * Lesson Picker — landing screen showing all lessons with progress, XP, and level.
 * Single-column list with arrow-key navigation. VM does not boot until selection.
 */

import type { LessonMeta } from "../../core/models";
import { ProgressManager } from "../../core/progress";
import { getLevelInfo, levelProgress, xpInLevel, xpForLevel } from "../../core/xp";

export class LessonPicker {
  private meta: LessonMeta[];
  private progress: ProgressManager;
  private onSelect: (meta: LessonMeta) => void;
  private container: HTMLElement | null = null;
  private focusIndex = 0;
  private cards: HTMLElement[] = [];
  private keyHandler: ((e: KeyboardEvent) => void) | null = null;

  constructor(
    meta: LessonMeta[],
    progress: ProgressManager,
    onSelect: (meta: LessonMeta) => void,
  ) {
    this.meta = meta;
    this.progress = progress;
    this.onSelect = onSelect;
  }

  render(root: HTMLElement): void {
    this.container = document.createElement("div");
    this.container.className = "lesson-picker";
    root.appendChild(this.container);
    this.buildContent();
    this.bindKeys();
    this.setFocus(0);
  }

  destroy(): void {
    this.unbindKeys();
    this.container?.remove();
    this.container = null;
    this.cards = [];
  }

  refresh(): void {
    if (!this.container) return;
    const prevIndex = this.focusIndex;
    this.container.innerHTML = "";
    this.cards = [];
    this.buildContent();
    this.setFocus(Math.min(prevIndex, this.cards.length - 1));
  }

  private buildContent(): void {
    if (!this.container) return;

    const totalXp = this.progress.totalXp;
    const info = getLevelInfo(totalXp);
    const prog = levelProgress(info);
    const inLvl = xpInLevel(info);
    const forLvl = xpForLevel(info);
    const completedSet = this.progress.completedLessons;
    const exerciseProg = this.progress.exerciseProgress();

    // ── Header ──
    const header = document.createElement("div");
    header.className = "picker-header";
    header.innerHTML = `
      <pre class="picker-ascii">   ____ _     ___ _         _
  / ___| |   |_ _| |_ _   _| |_ ___  _ __
 | |   | |    | || __| | | | __/ _ \\| '__|
 | |___| |___ | || |_| |_| | || (_) | |
  \\____|_____|___|\\__|\\__,_|\\__\\___/|_|</pre>
      <div class="picker-stats">
        <span class="picker-level">Lv.${info.level} ${this.esc(info.title)}</span>
        <div class="picker-xp-row">
          <div class="picker-xp-bar">
            <div class="picker-xp-fill" style="width:${Math.round(prog * 100)}%"></div>
          </div>
          <span class="picker-xp-text">${inLvl}/${forLvl} XP</span>
        </div>
        <span class="picker-total">${totalXp} XP total &middot; ${completedSet.size}/${this.meta.length} lessons</span>
      </div>
    `;
    this.container.appendChild(header);

    // ── Lesson list (single column) ──
    const list = document.createElement("div");
    list.className = "picker-list";

    for (let idx = 0; idx < this.meta.length; idx++) {
      const m = this.meta[idx];
      const isDone = completedSet.has(m.id);
      const doneCount = exerciseProg[m.id] ?? 0;
      const pct = m.exercise_count > 0 ? Math.round((doneCount / m.exercise_count) * 100) : 0;

      const card = document.createElement("div");
      card.className = "lesson-card" + (isDone ? " completed" : "");
      card.dataset.idx = String(idx);
      card.innerHTML = `
        <span class="card-num">${String(m.order).padStart(2, "0")}</span>
        <div class="card-body">
          <div class="card-title-row">
            <span class="card-title">${this.esc(m.title)}</span>
            <span class="card-category">${this.esc(m.category)}</span>
            ${this.difficultyDots(m.difficulty)}
          </div>
          <div class="card-progress-row">
            <div class="card-progress-bar">
              <div class="card-progress-fill" style="width:${pct}%"></div>
            </div>
            <span class="card-progress-text">${doneCount}/${m.exercise_count}</span>
            <span class="card-xp">${m.xp} XP</span>
            ${isDone ? '<span class="card-check">&#10003;</span>' : ""}
            ${isDone ? '<button class="card-reset-btn" title="Reset lesson progress">&#x21bb;</button>' : ""}
          </div>
        </div>
        <span class="card-arrow">&#9654;</span>
      `;

      card.addEventListener("click", (e) => {
        if ((e.target as HTMLElement).closest(".card-reset-btn")) return;
        this.onSelect(m);
      });

      card.addEventListener("mouseenter", () => {
        this.setFocus(idx);
      });

      const resetBtn = card.querySelector(".card-reset-btn");
      if (resetBtn) {
        resetBtn.addEventListener("click", async (e) => {
          e.stopPropagation();
          if (confirm(`Reset progress for "${m.title}"?`)) {
            await this.progress.resetLesson(m.id);
            this.refresh();
          }
        });
      }

      list.appendChild(card);
      this.cards.push(card);
    }

    this.container.appendChild(list);

    // ── Footer ──
    const footer = document.createElement("div");
    footer.className = "picker-footer";
    footer.innerHTML = `
      <span class="picker-hint">&#8593;&#8595; navigate &middot; Enter select &middot; r reset</span>
      <button class="picker-reset-btn">Reset All Progress</button>
    `;
    footer.querySelector(".picker-reset-btn")!.addEventListener("click", async () => {
      if (confirm("Reset ALL lesson progress? This cannot be undone.")) {
        await this.progress.resetAll();
        this.refresh();
      }
    });
    this.container.appendChild(footer);
  }

  // ── Keyboard navigation ──

  private bindKeys(): void {
    this.keyHandler = (e: KeyboardEvent) => this.handleKey(e);
    document.addEventListener("keydown", this.keyHandler);
  }

  private unbindKeys(): void {
    if (this.keyHandler) {
      document.removeEventListener("keydown", this.keyHandler);
      this.keyHandler = null;
    }
  }

  private handleKey(e: KeyboardEvent): void {
    // Ignore if a confirm dialog or input is focused
    if (document.activeElement && ["INPUT", "TEXTAREA", "SELECT"].includes(document.activeElement.tagName)) return;

    switch (e.key) {
      case "ArrowDown":
      case "j":
        e.preventDefault();
        this.setFocus(Math.min(this.focusIndex + 1, this.cards.length - 1));
        break;
      case "ArrowUp":
      case "k":
        e.preventDefault();
        this.setFocus(Math.max(this.focusIndex - 1, 0));
        break;
      case "Home":
        e.preventDefault();
        this.setFocus(0);
        break;
      case "End":
        e.preventDefault();
        this.setFocus(this.cards.length - 1);
        break;
      case "Enter":
        e.preventDefault();
        if (this.meta[this.focusIndex]) {
          this.onSelect(this.meta[this.focusIndex]);
        }
        break;
      case "r": {
        const m = this.meta[this.focusIndex];
        if (m && this.progress.completedLessons.has(m.id)) {
          if (confirm(`Reset progress for "${m.title}"?`)) {
            this.progress.resetLesson(m.id).then(() => this.refresh());
          }
        }
        break;
      }
    }
  }

  private setFocus(idx: number): void {
    if (idx < 0 || idx >= this.cards.length) return;

    // Remove previous focus
    this.cards[this.focusIndex]?.classList.remove("focused");

    this.focusIndex = idx;
    const card = this.cards[idx];
    card.classList.add("focused");

    // Scroll into view if needed
    card.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  private difficultyDots(level: number): string {
    let html = '<span class="difficulty-dots">';
    for (let i = 0; i < 4; i++) {
      html += `<span class="diff-dot${i < level ? " active" : ""}"></span>`;
    }
    html += "</span>";
    return html;
  }

  private esc(text: string): string {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}
