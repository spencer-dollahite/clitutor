#!/usr/bin/env node
/**
 * Generate a v86 state snapshot for fast boot.
 *
 * Boots the VM headless in Node.js, waits for the shell prompt,
 * drops filesystem caches, and saves the state for instant restore.
 *
 * Run: node build/build-state.js
 *
 * Prerequisites: npm run build-rootfs (produces alpine-fs.json + flat files)
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT = resolve(__dirname, "..");
const V86_DIR = resolve(PROJECT, "public/v86");

// v86 can run in Node.js — load it
const V86_LIB = resolve(PROJECT, "node_modules/v86/build/libv86.js");

async function main() {
  // Check prerequisites
  const required = [
    "alpine-fs.json",
    "seabios.bin",
    "vgabios.bin",
  ];

  const missing = required.filter((f) => !existsSync(resolve(V86_DIR, f)));
  if (missing.length > 0) {
    console.error("Missing files in public/v86/:");
    for (const f of missing) console.error(`  - ${f}`);
    console.error("\nRun 'npm run build-rootfs' first.");
    process.exit(1);
  }

  if (!existsSync(V86_LIB)) {
    console.error("Missing node_modules/v86/build/libv86.js");
    console.error("Run 'npm install' first.");
    process.exit(1);
  }

  console.log("==> Booting v86 to generate state snapshot...");
  console.log("    This takes 30-60 seconds.\n");

  // v86's .mjs build has proper ESM exports
  const V86_ESM = resolve(PROJECT, "node_modules/v86/build/libv86.mjs");
  const { V86 } = await import(V86_ESM);

  const emulator = new V86({
    bios: { url: resolve(V86_DIR, "seabios.bin") },
    vga_bios: { url: resolve(V86_DIR, "vgabios.bin") },
    wasm_path: resolve(V86_DIR, "v86.wasm"),
    memory_size: 512 * 1024 * 1024,
    vga_memory_size: 8 * 1024 * 1024,
    filesystem: {
      basefs: resolve(V86_DIR, "alpine-fs.json"),
      baseurl: resolve(V86_DIR, "alpine-rootfs-flat") + "/",
    },
    autostart: true,
    bzimage_initrd_from_filesystem: true,
    cmdline:
      "rw root=host9p rootfstype=9p rootflags=trans=virtio,cache=loose " +
      "modules=virtio_pci tsc=reliable console=ttyS0",
  });

  let serialText = "";
  let saving = false;
  let loggedIn = false;

  emulator.add_listener("serial0-output-byte", function (byte) {
    const ch = String.fromCharCode(byte);
    process.stdout.write(ch);
    serialText += ch;
    if (serialText.length > 2000) serialText = serialText.slice(-500);

    if (saving) return;

    // Handle login prompt
    if (!loggedIn && serialText.endsWith("login: ")) {
      loggedIn = true;
      emulator.serial0_send("root\n");
      return;
    }

    // Detect shell prompt (hostname may be "clitutor", shell may be bash or sh)
    if (serialText.endsWith(":~# ") || serialText.endsWith(":~# \n") ||
        /[#$] $/.test(serialText.slice(-5))) {
      saving = true;
      console.log("\n\n==> Shell prompt detected. Preparing snapshot...");

      // Drop caches for a clean snapshot
      emulator.serial0_send("sync; echo 3 > /proc/sys/vm/drop_caches\n");

      setTimeout(async () => {
        console.log("==> Saving state...");
        try {
          const state = await emulator.save_state();
          const buf = Buffer.from(new Uint8Array(state));
          const outPath = resolve(V86_DIR, "alpine-state.bin");
          writeFileSync(outPath, buf);
          console.log(
            `==> State saved: ${outPath} (${(buf.length / 1024 / 1024).toFixed(1)} MB)`,
          );
          emulator.destroy();
          process.exit(0);
        } catch (err) {
          console.error("Failed to save state:", err);
          process.exit(1);
        }
      }, 5000);
    }
  });

  // Timeout after 2 minutes
  setTimeout(() => {
    console.error("\n==> Timeout: VM did not reach shell prompt in 120 seconds.");
    emulator.destroy();
    process.exit(1);
  }, 120000);
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
