/** Entry point for CLItutor Web. */

import { App } from "./ui/app";

// Import xterm.js CSS
import "@xterm/xterm/css/xterm.css";

document.addEventListener("DOMContentLoaded", () => {
  const root = document.getElementById("app");
  if (!root) {
    console.error("Missing #app element");
    return;
  }

  const app = new App(root);
  app.start().catch((err) => {
    console.error("Failed to start CLItutor:", err);
    root.innerHTML = `
      <div class="loading-screen">
        <div style="color: var(--error); font-size: 16px;">Failed to start CLItutor</div>
        <div style="color: var(--text-muted);">${err.message}</div>
      </div>
    `;
  });
});
