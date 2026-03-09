/**
 * Text-to-Speech service using the Web Speech API.
 *
 * Handles voice pre-loading, CLI term pronunciation, markdown stripping,
 * and sentence chunking to avoid Chrome's 15-second silence bug.
 */

const CLI_PRONUNCIATIONS: Record<string, string> = {
  pwd: "P W D",
  ls: "L S",
  cd: "C D",
  chmod: "C H mod",
  sudo: "sue-doh",
  mkdir: "M K dir",
  rmdir: "R M dir",
  mv: "M V",
  cp: "C P",
  rm: "R M",
  ssh: "S S H",
  scp: "S C P",
  vim: "vim",
  nano: "nano",
  cat: "cat",
  grep: "grep",
  apt: "apt",
  sed: "sed",
  awk: "awk",
  tar: "tar",
  gzip: "G zip",
  gunzip: "G unzip",
  wget: "W get",
  curl: "curl",
  chown: "C H own",
  chgrp: "C H group",
  stdin: "standard in",
  stdout: "standard out",
  stderr: "standard error",
  clitutor: "CLI Tutor",
  CLItutor: "CLI Tutor",
};

/** Regex that matches CLI terms as whole words (case-sensitive). */
const CLI_TERM_RE = new RegExp(
  `\\b(${Object.keys(CLI_PRONUNCIATIONS).join("|")})\\b`,
  "g",
);

const AUTO_READ_KEY = "clitutor-auto-read";
const RATE_KEY = "clitutor-tts-rate";
const RATE_MIN = 0.5;
const RATE_MAX = 2.0;
const RATE_STEP = 0.25;

export class TTSService {
  private synth = window.speechSynthesis;
  private speaking = false;
  private autoRead = false;
  private rate = 1.0;
  private cachedVoice: SpeechSynthesisVoice | null = null;
  private voicesReady = false;
  /** Queue of sentence chunks for the current speech. */
  private chunks: string[] = [];
  private chunkIndex = 0;

  /** Called when speaking state changes — wire to UI button updates. */
  onStateChange?: (speaking: boolean) => void;

  constructor() {
    this.autoRead = localStorage.getItem(AUTO_READ_KEY) === "true";
    const saved = parseFloat(localStorage.getItem(RATE_KEY) ?? "");
    if (!isNaN(saved) && saved >= RATE_MIN && saved <= RATE_MAX) this.rate = saved;

    // Pre-load voices. Chrome fires voiceschanged asynchronously;
    // other browsers populate getVoices() synchronously.
    this.loadVoices();
    if (typeof this.synth.onvoiceschanged !== "undefined") {
      this.synth.onvoiceschanged = () => this.loadVoices();
    }
  }

  /** Speak text (cancels any current speech). */
  speak(text: string): void {
    this.stop();

    const cleaned = this.prepareText(text);
    if (!cleaned) return;

    // Split into sentence-sized chunks to avoid Chrome's 15s cutoff.
    // Each chunk is spoken as its own utterance, chained via onend.
    this.chunks = this.splitIntoChunks(cleaned);
    this.chunkIndex = 0;

    if (this.chunks.length > 0) {
      this.setSpeaking(true);
      this.speakNextChunk();
    }
  }

  /** Stop any in-progress speech. */
  stop(): void {
    this.chunks = [];
    this.chunkIndex = 0;
    this.synth.cancel();
    if (this.speaking) this.setSpeaking(false);
  }

  /** Toggle: speak if idle, stop if speaking. */
  toggle(text: string): void {
    if (this.speaking) {
      this.stop();
    } else {
      this.speak(text);
    }
  }

  isSpeaking(): boolean {
    return this.speaking;
  }

  setAutoRead(on: boolean): void {
    this.autoRead = on;
    localStorage.setItem(AUTO_READ_KEY, String(on));
  }

  getAutoRead(): boolean {
    return this.autoRead;
  }

  getRate(): number {
    return this.rate;
  }

  /** Increase speech rate by one step. */
  faster(): void {
    this.setRate(Math.min(RATE_MAX, this.rate + RATE_STEP));
  }

  /** Decrease speech rate by one step. */
  slower(): void {
    this.setRate(Math.max(RATE_MIN, this.rate - RATE_STEP));
  }

  private setRate(r: number): void {
    this.rate = Math.round(r * 100) / 100;
    localStorage.setItem(RATE_KEY, String(this.rate));
    this.onStateChange?.(this.speaking);
  }

  // ── Internal ────────────────────────────────────────────────

  private setSpeaking(value: boolean): void {
    this.speaking = value;
    this.onStateChange?.(value);
  }

  /** Pre-load and cache the best voice so it's ready when speak() is called. */
  private loadVoices(): void {
    const voices = this.synth.getVoices();
    if (!voices.length) return;

    this.voicesReady = true;

    const english = voices.filter((v) => v.lang.startsWith("en"));
    if (!english.length) { this.cachedVoice = voices[0]; return; }

    // Prefer voices with "neural", "enhanced", "natural", or "premium" in name
    const premium = english.find((v) =>
      /neural|enhanced|natural|premium/i.test(v.name),
    );
    if (premium) { this.cachedVoice = premium; return; }

    const defaultEn = english.find((v) => v.default);
    this.cachedVoice = defaultEn ?? english[0];
  }

  /**
   * Split text into sentence-sized chunks. Each chunk stays under ~200 chars
   * to keep well within Chrome's comfort zone. Splits on sentence-ending
   * punctuation, falling back to commas/semicolons, then hard-wraps.
   */
  private splitIntoChunks(text: string): string[] {
    // Split on sentence boundaries (., !, ?) followed by a space
    const sentences = text.split(/(?<=[.!?])\s+/);
    const chunks: string[] = [];
    let current = "";

    for (const sentence of sentences) {
      if (current && (current.length + sentence.length + 1) > 200) {
        chunks.push(current.trim());
        current = sentence;
      } else {
        current += (current ? " " : "") + sentence;
      }
    }
    if (current.trim()) chunks.push(current.trim());

    return chunks.filter((c) => c.length > 0);
  }

  /** Speak the next chunk in the queue, chaining via onend. */
  private speakNextChunk(): void {
    if (this.chunkIndex >= this.chunks.length) {
      this.chunks = [];
      this.chunkIndex = 0;
      this.setSpeaking(false);
      return;
    }

    const text = this.chunks[this.chunkIndex];
    const utterance = new SpeechSynthesisUtterance(text);
    if (this.cachedVoice) utterance.voice = this.cachedVoice;
    utterance.rate = this.rate;
    utterance.pitch = 1.0;

    utterance.onend = () => {
      this.chunkIndex++;
      this.speakNextChunk();
    };
    utterance.onerror = (e) => {
      // 'interrupted' and 'canceled' fire on normal stop() calls — not real errors
      if (e.error === "interrupted" || e.error === "canceled") return;
      this.stop();
    };

    this.synth.speak(utterance);
  }

  /** Strip markdown/code and apply CLI pronunciation dictionary. */
  private prepareText(raw: string): string {
    let text = raw;

    // Strip fenced code blocks
    text = text.replace(/```[\s\S]*?```/g, "");

    // Strip inline code backticks but keep the content
    text = text.replace(/`([^`]+)`/g, "$1");

    // Strip HTML tags (including exercise comment blocks)
    text = text.replace(/<!--[\s\S]*?-->/g, "");
    text = text.replace(/<[^>]+>/g, "");

    // Strip markdown heading markers
    text = text.replace(/^#{1,6}\s+/gm, "");

    // Strip bold/italic markers
    text = text.replace(/\*{1,3}([^*]+)\*{1,3}/g, "$1");
    text = text.replace(/_{1,3}([^_]+)_{1,3}/g, "$1");

    // Strip link syntax [text](url) → text
    text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");

    // Strip image syntax ![alt](url)
    text = text.replace(/!\[([^\]]*)\]\([^)]+\)/g, "$1");

    // Apply CLI pronunciation dictionary
    text = text.replace(CLI_TERM_RE, (match) => CLI_PRONUNCIATIONS[match] ?? match);

    // Collapse whitespace
    text = text.replace(/\n{2,}/g, ". ").replace(/\n/g, " ").replace(/\s+/g, " ").trim();

    return text;
  }
}
