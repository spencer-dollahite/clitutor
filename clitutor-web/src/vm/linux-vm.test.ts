/**
 * Tests for LinuxVM filesystem queries against the host-side 9p inode tree.
 *
 * Regression coverage for the empty-file bug: v86's read_file() rejects for
 * zero-byte files (inode exists but has no inodedata and is not on storage),
 * so existence checks must walk the 9p tree via SearchPath instead.
 */

import { describe, it, expect, vi } from "vitest";
import { LinuxVM } from "./linux-vm";

const S_IFREG = 0x8000;
const S_IFDIR = 0x4000;

/** Minimal fake of v86's 9p filesystem object. */
function fake9pFs(entries: Record<string, { mode: number }>) {
  const paths = Object.keys(entries);
  const inodes = paths.map((p) => ({ mode: entries[p].mode }));
  return {
    SearchPath: (path: string) => ({ id: paths.indexOf(path) }),
    GetInode: (id: number) => inodes[id],
    inodes,
  };
}

/** Wire a LinuxVM with a fake emulator exposing the given 9p fs. */
function vmWith(fs: any, readFile?: (path: string) => Promise<Uint8Array>) {
  const vm = new LinuxVM();
  (vm as any).emulator = {
    read_file: readFile ?? vi.fn().mockRejectedValue(new Error("FileNotFound")),
    v86: { cpu: { devices: { virtio_9p: { fs } } } },
  };
  return vm;
}

describe("LinuxVM.fileExists", () => {
  it("finds a zero-byte file even though read_file rejects (touch case)", async () => {
    const vm = vmWith(fake9pFs({ "/home/student/notes.txt": { mode: S_IFREG } }));
    expect(await vm.fileExists("/home/student/notes.txt")).toBe(true);
  });

  it("returns false for a missing path", async () => {
    const vm = vmWith(fake9pFs({}));
    expect(await vm.fileExists("/home/student/nope.txt")).toBe(false);
  });

  it("returns false for a directory with the expected name", async () => {
    const vm = vmWith(fake9pFs({ "/home/student/notes.txt": { mode: S_IFDIR } }));
    expect(await vm.fileExists("/home/student/notes.txt")).toBe(false);
  });

  it("falls back to read_file when the 9p tree is unavailable", async () => {
    const vm = vmWith(null, () => Promise.resolve(new Uint8Array([104, 105])));
    expect(await vm.fileExists("/home/student/hello.txt")).toBe(true);

    const vmMissing = vmWith(null);
    expect(await vmMissing.fileExists("/home/student/nope.txt")).toBe(false);
  });

  it("returns false when no emulator is running", async () => {
    const vm = new LinuxVM();
    expect(await vm.fileExists("/anything")).toBe(false);
  });
});
