/** Markdown renderer using marked + highlight.js. */

import { marked, type MarkedExtension, type Tokens } from "marked";
import hljs from "highlight.js/lib/core";
import bash from "highlight.js/lib/languages/bash";
import python from "highlight.js/lib/languages/python";
import json from "highlight.js/lib/languages/json";
import yaml from "highlight.js/lib/languages/yaml";
import dockerfile from "highlight.js/lib/languages/dockerfile";

// Register languages
hljs.registerLanguage("bash", bash);
hljs.registerLanguage("sh", bash);
hljs.registerLanguage("python", python);
hljs.registerLanguage("json", json);
hljs.registerLanguage("yaml", yaml);
hljs.registerLanguage("dockerfile", dockerfile);

// Configure marked with syntax highlighting via renderer extension
const highlightExtension: MarkedExtension = {
  renderer: {
    code({ text, lang }: Tokens.Code): string {
      let highlighted: string;
      if (lang && hljs.getLanguage(lang)) {
        highlighted = hljs.highlight(text, { language: lang }).value;
      } else {
        highlighted = hljs.highlightAuto(text).value;
      }
      return `<pre><code class="hljs language-${lang || ""}">${highlighted}</code></pre>`;
    },
  },
};

marked.use(highlightExtension);

export class MarkdownPane {
  private container: HTMLElement;
  private exerciseHeadings = new Map<number, HTMLHeadingElement>();

  constructor(parent: HTMLElement) {
    this.container = document.createElement("div");
    this.container.className = "markdown-pane";
    parent.appendChild(this.container);
  }

  render(markdown: string): void {
    this.container.innerHTML = marked.parse(markdown) as string;
    this.indexExerciseHeadings();
  }

  /** Scroll to a specific exercise heading by exercise number. */
  scrollToExercise(exerciseNum: number): void {
    const heading =
      this.exerciseHeadings.get(exerciseNum) ??
      // Fallback: if labels are malformed, use exercise order.
      Array.from(this.exerciseHeadings.values())[exerciseNum - 1];
    if (!heading) return;

    heading.scrollIntoView({ behavior: "smooth", block: "start" });
    // Brief highlight effect
    heading.style.color = "var(--accent)";
    setTimeout(() => { heading.style.color = ""; }, 2000);
  }

  /** Scroll to top. */
  scrollToTop(): void {
    this.container.scrollTop = 0;
  }

  /** Build an exact mapping from "Exercise N" headings to DOM nodes. */
  private indexExerciseHeadings(): void {
    this.exerciseHeadings.clear();
    const headings = this.container.querySelectorAll("h3");
    for (const h of headings) {
      const text = h.textContent ?? "";
      const m = text.match(/\bexercise\s+(\d+)\b/i);
      if (!m) continue;
      const num = parseInt(m[1], 10);
      if (!Number.isFinite(num)) continue;
      if (!this.exerciseHeadings.has(num)) {
        this.exerciseHeadings.set(num, h as HTMLHeadingElement);
      }
    }
  }
}
