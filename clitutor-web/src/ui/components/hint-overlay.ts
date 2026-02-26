/** Progressive hint overlay modal. */

import type { Exercise } from "../../core/models";

const HINT_PENALTY_TEXT: Record<number, string> = {
  0: "",
  1: "Using a hint reduces XP by 10%",
  2: "Using 2 hints reduces XP by 30%",
  3: "Using 3+ hints reduces XP by 50%",
};

export class HintOverlay {
  private overlay: HTMLElement;
  private visible = false;
  private escHandler: ((e: KeyboardEvent) => void) | null = null;

  constructor() {
    this.overlay = document.createElement("div");
    this.overlay.className = "hint-overlay";
    this.overlay.style.display = "none";
    document.body.appendChild(this.overlay);

    // Close on backdrop click
    this.overlay.addEventListener("click", (e) => {
      if (e.target === this.overlay) this.hide();
    });
  }

  show(exercise: Exercise): void {
    const hintsAvailable = exercise.hints.length;
    const hintsToShow = Math.min(exercise.hints_used + 1, hintsAvailable);

    if (hintsToShow === 0) {
      // No hints available
      this.overlay.innerHTML = `
        <div class="hint-dialog">
          <h3>No Hints Available</h3>
          <p class="hint-text">This exercise doesn't have any hints.</p>
          <button class="hint-close-btn" id="hint-close">Close</button>
        </div>
      `;
    } else {
      let hintsHtml = "";
      for (let i = 0; i < hintsToShow; i++) {
        hintsHtml += `<p class="hint-text"><strong>Hint ${i + 1}:</strong> ${this.escapeHtml(exercise.hints[i])}</p>`;
      }

      const penaltyKey = Math.min(hintsToShow, 3);
      const penaltyText = HINT_PENALTY_TEXT[penaltyKey] ?? HINT_PENALTY_TEXT[3];
      const moreHints = hintsToShow < hintsAvailable
        ? `<p class="hint-text" style="color: var(--text-dim);">${hintsAvailable - hintsToShow} more hint(s) available — type /hint again</p>`
        : "";

      this.overlay.innerHTML = `
        <div class="hint-dialog">
          <h3>Hint for: ${this.escapeHtml(exercise.title)}</h3>
          ${hintsHtml}
          ${moreHints}
          ${penaltyText ? `<p class="hint-penalty">${penaltyText}</p>` : ""}
          <button class="hint-close-btn" id="hint-close">Close</button>
        </div>
      `;
    }

    this.overlay.style.display = "flex";
    this.visible = true;

    this.overlay.querySelector("#hint-close")?.addEventListener("click", () => this.hide());

    // Close on Escape — remove any stale handler first
    if (this.escHandler) {
      document.removeEventListener("keydown", this.escHandler);
    }
    this.escHandler = (e: KeyboardEvent) => {
      if (e.key === "Escape") this.hide();
    };
    document.addEventListener("keydown", this.escHandler);
  }

  hide(): void {
    this.overlay.style.display = "none";
    this.visible = false;

    if (this.escHandler) {
      document.removeEventListener("keydown", this.escHandler);
      this.escHandler = null;
    }
  }

  get isVisible(): boolean {
    return this.visible;
  }

  private escapeHtml(text: string): string {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
  }
}
