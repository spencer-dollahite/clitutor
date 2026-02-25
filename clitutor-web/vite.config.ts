import { defineConfig } from "vite";
import { resolve } from "path";
import { copyFileSync, mkdirSync, existsSync } from "fs";

// Copy v86 build artifacts from node_modules to public/v86 at build time
function copyV86Assets() {
  return {
    name: "copy-v86-assets",
    buildStart() {
      const outDir = resolve(__dirname, "public/v86");
      mkdirSync(outDir, { recursive: true });

      const v86Build = resolve(__dirname, "node_modules/v86/build");
      const assets = ["libv86.js", "v86.wasm"];

      for (const file of assets) {
        const src = resolve(v86Build, file);
        const dest = resolve(outDir, file);
        if (existsSync(src) && !existsSync(dest)) {
          copyFileSync(src, dest);
          console.log(`  Copied ${file} to public/v86/`);
        }
      }
    },
  };
}

export default defineConfig({
  base: "/clitutor/",
  plugins: [copyV86Assets()],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
    },
  },
  build: {
    target: "es2020",
    outDir: "dist",
    assetsInlineLimit: 0,
  },
  server: {
    headers: {
      // Required for SharedArrayBuffer (v86 needs it for WASM threads)
      "Cross-Origin-Opener-Policy": "same-origin",
      "Cross-Origin-Embedder-Policy": "require-corp",
    },
  },
  preview: {
    headers: {
      "Cross-Origin-Opener-Policy": "same-origin",
      "Cross-Origin-Embedder-Policy": "require-corp",
    },
  },
});
