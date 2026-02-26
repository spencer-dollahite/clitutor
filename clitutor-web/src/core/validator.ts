/** Output validation strategies — port of core/validator.py */

import type { Exercise, CommandResult } from "./models";
import type { LinuxVM } from "../vm/linux-vm";

export interface ValidationResult {
  passed: boolean;
  message: string;
}

function ok(message = "Correct!"): ValidationResult {
  return { passed: true, message };
}

function fail(message: string): ValidationResult {
  return { passed: false, message };
}

export class OutputValidator {
  private vm: LinuxVM;

  constructor(vm: LinuxVM) {
    this.vm = vm;
  }

  async validate(exercise: Exercise, result: CommandResult): Promise<ValidationResult> {
    const vtype = exercise.validation_type;
    const expected = exercise.expected;
    console.log("[Validator] validate: exercise=%s type=%s expected=%s stdout=%s cwd=%s rc=%d",
      exercise.id, vtype, JSON.stringify(expected), JSON.stringify(result.stdout.slice(0, 80)),
      result.cwd, result.returncode);

    switch (vtype) {
      case "output_equals":
        return this.checkOutputEquals(result, expected);
      case "output_contains":
        return this.checkOutputContains(result, expected);
      case "output_regex":
        return this.checkOutputRegex(result, expected);
      case "exit_code":
        return this.checkExitCode(result, expected);
      case "file_exists":
        return this.checkFileExists(expected, result.cwd);
      case "file_contains":
        return this.checkFileContains(expected, result.cwd);
      case "dir_with_file":
        return this.checkDirWithFile(result.cwd);
      case "any_file_contains":
        return this.checkAnyFileContains(expected, result.cwd);
      case "cwd_regex":
        return this.checkCwdRegex(expected, result.cwd);
      default:
        return fail(`Unknown validation type: ${vtype}`);
    }
  }

  // ── Output-based validations ──────────────────────────────────────

  private checkOutputEquals(result: CommandResult, expected: string): ValidationResult {
    const actual = result.stdout.trim();
    if (actual === expected.trim()) return ok();
    return fail("Output doesn't match expected result.");
  }

  private checkOutputContains(result: CommandResult, expected: string): ValidationResult {
    const combined = result.stdout + result.stderr;
    if (combined.includes(expected.trim())) return ok();
    return fail("Output doesn't contain expected text.");
  }

  private checkOutputRegex(result: CommandResult, expected: string): ValidationResult {
    const combined = result.stdout + result.stderr;
    try {
      if (new RegExp(expected).test(combined)) return ok();
    } catch {
      return fail("Invalid regex pattern.");
    }
    return fail("Output doesn't match expected pattern.");
  }

  private checkExitCode(result: CommandResult, expected: string): ValidationResult {
    const expectedCode = parseInt(expected.trim(), 10);
    if (isNaN(expectedCode)) return fail("Invalid expected exit code.");
    if (result.returncode === expectedCode) return ok();
    return fail(`Expected exit code ${expectedCode}, got ${result.returncode}.`);
  }

  // ── Filesystem-based validations ──────────────────────────────────

  private async checkFileExists(expected: string, cwd: string): Promise<ValidationResult> {
    const paths = this.resolvePaths(expected.trim(), cwd);
    for (const p of paths) {
      if (await this.vm.fileExists(p)) return ok("Correct! File created.");
    }
    return fail(`File '${expected}' not found.`);
  }

  private async checkFileContains(expected: string, cwd: string): Promise<ValidationResult> {
    if (!expected.includes("::")) return fail("Invalid file_contains spec.");
    const [filename, content] = expected.split("::", 2);
    const paths = this.resolvePaths(filename.trim(), cwd);

    for (const p of paths) {
      if (await this.vm.fileExists(p)) {
        const fileContent = await this.vm.readFile(p);
        if (fileContent.includes(content.trim())) {
          return ok("Correct! File contains expected content.");
        }
        return fail("File doesn't contain expected content.");
      }
    }
    return fail(`File '${filename.trim()}' not found.`);
  }

  private async checkDirWithFile(cwd: string): Promise<ValidationResult> {
    // List files in sandbox root, look for any directory containing a file
    const sandboxRoot = "/home/student";
    if (await this.vm.hasDirWithFile(sandboxRoot)) {
      return ok("Correct! Directory with file created.");
    }
    return fail(
      "No directory containing a file was found. " +
      "Create a directory and then create a file inside it.",
    );
  }

  private async checkAnyFileContains(expected: string, cwd: string): Promise<ValidationResult> {
    const sandboxRoot = "/home/student";
    if (await this.vm.findFileContaining(sandboxRoot, expected.trim())) {
      return ok("Correct! File contains expected content.");
    }
    return fail(`No file found containing '${expected.trim()}'.`);
  }

  private checkCwdRegex(expected: string, cwd: string): ValidationResult {
    if (!cwd) return fail("Cannot determine current directory.");
    try {
      if (new RegExp(expected).test(cwd)) return ok();
    } catch {
      return fail("Invalid regex pattern.");
    }
    return fail("You haven't changed into the right directory yet.");
  }

  // ── Helpers ───────────────────────────────────────────────────────

  /**
   * Return possible paths for a filename: both absolute (sandbox root) and
   * relative to the current working directory.
   */
  private resolvePaths(filename: string, cwd: string): string[] {
    const sandboxRoot = "/home/student";
    const paths = [`${sandboxRoot}/${filename}`];
    if (cwd && cwd !== sandboxRoot) {
      paths.push(`${cwd}/${filename}`);
    }
    return paths;
  }
}
