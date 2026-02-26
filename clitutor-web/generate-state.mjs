/**
 * generate-state.mjs — Headless Chrome boots the v86 VM and saves a state snapshot.
 *
 * Usage: node generate-state.mjs
 *
 * Requires: puppeteer, vite (runs vite preview internally)
 */

import { launch } from "puppeteer";
import { spawn } from "child_process";
import { writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const STATE_OUT = resolve(__dirname, "public/v86/alpine-state.bin");
const PORT = 4174;
const BASE_URL = `http://localhost:${PORT}/clitutor/`;

// 1. Start vite preview in the background
console.log("[gen-state] Starting vite preview...");
const vite = spawn("npx", ["vite", "preview", "--port", String(PORT)], {
  cwd: __dirname,
  stdio: ["ignore", "pipe", "pipe"],
});

// Wait for vite to be ready
await new Promise((resolve, reject) => {
  const timeout = setTimeout(() => reject(new Error("Vite preview did not start in 10s")), 10000);
  vite.stdout.on("data", (data) => {
    const text = data.toString();
    if (text.includes("Local:") || text.includes("localhost")) {
      clearTimeout(timeout);
      resolve();
    }
  });
  vite.on("error", reject);
});
console.log("[gen-state] Vite preview running on port", PORT);

try {
  // 2. Launch headless Chrome with SharedArrayBuffer support
  console.log("[gen-state] Launching headless Chrome...");
  const browser = await launch({
    headless: "new",
    args: [
      "--enable-features=SharedArrayBuffer",
      "--no-sandbox",
      "--disable-setuid-sandbox",
    ],
  });

  const page = await browser.newPage();

  // Enable SharedArrayBuffer by setting headers via page interception
  await page.setExtraHTTPHeaders({
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Embedder-Policy": "require-corp",
  });

  page.on("console", (msg) => {
    const text = msg.text();
    if (text.includes("[LinuxVM]") || text.includes("[App]") || text.includes("gen-state")) {
      console.log("[browser]", text);
    }
  });

  console.log("[gen-state] Navigating to", BASE_URL);
  await page.goto(BASE_URL, { waitUntil: "networkidle0", timeout: 30000 });

  // Check SharedArrayBuffer is available
  const isolated = await page.evaluate(() => crossOriginIsolated);
  console.log("[gen-state] crossOriginIsolated:", isolated);
  if (!isolated) {
    throw new Error("crossOriginIsolated is false — headers not working");
  }

  // 3. Click the first lesson to trigger VM boot
  console.log("[gen-state] Clicking first lesson...");
  await page.waitForSelector(".lesson-card", { timeout: 10000 });
  await page.click(".lesson-card");

  // 4. Wait for VM to be fully ready (poll __vmReady)
  console.log("[gen-state] Waiting for VM to boot (cold boot, ~30-60s)...");
  await page.waitForFunction("window.__vmReady === true", { timeout: 120000 });
  console.log("[gen-state] VM is ready!");

  // Give shell a moment to settle
  await new Promise((r) => setTimeout(r, 3000));

  // 5. Save state
  console.log("[gen-state] Saving state snapshot...");
  const stateBase64 = await page.evaluate(async () => {
    const state = await window.__vm.save_state();
    const bytes = new Uint8Array(state);
    let binary = "";
    for (let i = 0; i < bytes.length; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  });

  const stateBuffer = Buffer.from(stateBase64, "base64");
  writeFileSync(STATE_OUT, stateBuffer);
  console.log("[gen-state] State snapshot saved to", STATE_OUT, `(${(stateBuffer.length / 1024 / 1024).toFixed(1)} MB)`);

  await browser.close();
} finally {
  vite.kill();
}

console.log("[gen-state] Done!");
