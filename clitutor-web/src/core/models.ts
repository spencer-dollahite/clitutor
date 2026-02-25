/** Dataclasses for lesson and exercise data — port of models/lesson.py + executor.py */

export interface Exercise {
  id: string;
  title: string;
  xp: number;
  difficulty: number;
  sandbox_setup: string[] | null;
  validation_type: string;
  expected: string;
  hints: string[];

  // Runtime state (not persisted in lesson file)
  attempts: number;
  first_try: boolean;
  hints_used: number;
  completed: boolean;
}

export function createExercise(partial: Partial<Exercise> & { id: string; title: string }): Exercise {
  return {
    xp: 10,
    difficulty: 1,
    sandbox_setup: null,
    validation_type: "output_contains",
    expected: "",
    hints: [],
    attempts: 0,
    first_try: true,
    hints_used: 0,
    completed: false,
    ...partial,
  };
}

export interface LessonData {
  id: string;
  title: string;
  slug: string;
  order: number;
  category: string;
  difficulty: number;
  description: string;
  content_markdown: string;
  exercises: Exercise[];
}

export function lessonTotalXp(lesson: LessonData): number {
  return lesson.exercises.reduce((sum, ex) => sum + ex.xp, 0);
}

export interface LessonMeta {
  id: string;
  title: string;
  slug: string;
  order: number;
  category: string;
  difficulty: number;
  description: string;
  xp: number;
  exercise_count: number;
  file: string;
}

export interface CommandResult {
  command: string;
  stdout: string;
  stderr: string;
  returncode: number;
  timed_out: boolean;
  blocked: boolean;
  block_reason: string;
  cwd: string;
}

export function createCommandResult(partial: Partial<CommandResult>): CommandResult {
  return {
    command: "",
    stdout: "",
    stderr: "",
    returncode: 0,
    timed_out: false,
    blocked: false,
    block_reason: "",
    cwd: "",
    ...partial,
  };
}
