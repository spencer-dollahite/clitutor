/** Type declarations for v86 emulator. */
declare class V86 {
  constructor(options: V86Options);

  add_listener(event: string, callback: (...args: any[]) => void): void;
  remove_listener(event: string, callback: (...args: any[]) => void): void;

  /** Send a byte to serial port 0. */
  serial0_send(data: string): void;

  /** Create a file in the 9p filesystem. */
  create_file(path: string, data: Uint8Array): Promise<void>;

  /** Read a file from the 9p filesystem. */
  read_file(path: string): Promise<Uint8Array>;

  /** Save VM state as a binary blob. */
  save_state(): Promise<ArrayBuffer>;

  /** Restore VM state from a binary blob. */
  restore_state(state: ArrayBuffer): void;

  /** Destroy the emulator instance. */
  destroy(): void;

  /** Check if emulator is running. */
  is_running(): boolean;

  /** V86 keyboard adapter (for focus management). */
  keyboard_adapter: { emu: { clear_key_queue(): void } };

  /** The emulation bus. */
  bus: {
    register(event: string, callback: (...args: any[]) => void): void;
    send(event: string, ...args: any[]): void;
  };

  v86: {
    cpu: {
      devices: {
        virtio_9p?: { get_file_list(): string[] };
      };
    };
  };
}

interface V86Options {
  wasm_path?: string;
  memory_size?: number;
  vga_memory_size?: number;
  bios?: { url: string };
  vga_bios?: { url: string };
  bzimage?: { url: string };
  initrd?: { url: string };
  cmdline?: string;
  filesystem?: { baseurl: string; basefs: string };
  initial_state?: { url: string };
  autostart?: boolean;
  screen_container?: HTMLElement | null;
  serial_container_xtermjs?: any;
  disable_keyboard?: boolean;
  disable_mouse?: boolean;
  disable_speaker?: boolean;
  network_relay_url?: string;
  acpi?: boolean;
  /** Load bzImage + initramfs from the 9p filesystem (/boot/*). */
  bzimage_initrd_from_filesystem?: boolean;
}
