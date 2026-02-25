/** Lesson loader — port of core/loader.py */

import yaml from "js-yaml";
import type { Exercise, LessonData, LessonMeta } from "./models";
import { createExercise } from "./models";

const EXERCISE_PATTERN = /<!--\s*exercise\s*\n(.*?)-->/gs;

export class LessonLoader {
  private lessonsBase: string;

  constructor(lessonsBase = "/lessons") {
    this.lessonsBase = lessonsBase;
  }

  async loadMetadata(): Promise<LessonMeta[]> {
    const resp = await fetch(`${this.lessonsBase}/metadata.json`);
    if (!resp.ok) return [];
    const data = await resp.json();
    const lessons: LessonMeta[] = data.lessons;
    lessons.sort((a, b) => a.order - b.order);
    return lessons;
  }

  async loadLesson(meta: LessonMeta): Promise<LessonData> {
    const resp = await fetch(`${this.lessonsBase}/${meta.file}`);
    if (!resp.ok) throw new Error(`Lesson file not found: ${meta.file}`);
    const content = await resp.text();

    const exercises = this.extractExercises(content);

    // Strip exercise comments from content for display
    const displayContent = content.replace(EXERCISE_PATTERN, "").trim();

    return {
      id: meta.id,
      title: meta.title,
      slug: meta.slug,
      order: meta.order,
      category: meta.category,
      difficulty: meta.difficulty,
      description: meta.description,
      content_markdown: displayContent,
      exercises,
    };
  }

  private extractExercises(content: string): Exercise[] {
    const exercises: Exercise[] = [];
    // Reset regex lastIndex since it has the global flag
    EXERCISE_PATTERN.lastIndex = 0;

    let match: RegExpExecArray | null;
    while ((match = EXERCISE_PATTERN.exec(content)) !== null) {
      const yamlStr = match[1];
      try {
        const data = yaml.load(yamlStr) as Record<string, unknown> | null;
        if (data && typeof data === "object") {
          exercises.push(
            createExercise({
              id: String(data.id ?? `ex${exercises.length}`),
              title: String(data.title ?? "Untitled"),
              xp: Number(data.xp ?? 10),
              difficulty: Number(data.difficulty ?? 1),
              sandbox_setup: (data.sandbox_setup as string[] | null) ?? null,
              validation_type: String(data.validation_type ?? "output_contains"),
              expected: String(data.expected ?? ""),
              hints: Array.isArray(data.hints) ? data.hints.map(String) : [],
            }),
          );
        }
      } catch {
        // Skip malformed YAML
        continue;
      }
    }
    return exercises;
  }

  async loadAll(): Promise<LessonData[]> {
    const metadata = await this.loadMetadata();
    const lessons: LessonData[] = [];
    for (const meta of metadata) {
      try {
        lessons.push(await this.loadLesson(meta));
      } catch {
        continue;
      }
    }
    return lessons;
  }
}
