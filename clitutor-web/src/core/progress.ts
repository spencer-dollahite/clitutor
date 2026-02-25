/** Progress persistence via IndexedDB — port of models/progress.py */

const DB_NAME = "clitutor";
const DB_VERSION = 1;
const STORE_NAME = "progress";
const PROGRESS_KEY = "user_progress";

export interface ExerciseProgress {
  completed: boolean;
  xp_earned: number;
  attempts: number;
  hints_used: number;
}

export interface LessonProgress {
  exercises: Record<string, ExerciseProgress>;
}

function createExerciseProgress(): ExerciseProgress {
  return { completed: false, xp_earned: 0, attempts: 0, hints_used: 0 };
}

function isLessonCompleted(lp: LessonProgress): boolean {
  const exs = Object.values(lp.exercises);
  return exs.length > 0 && exs.every((ep) => ep.completed);
}

function lessonTotalXp(lp: LessonProgress): number {
  return Object.values(lp.exercises).reduce((s, ep) => s + ep.xp_earned, 0);
}

function lessonCompletedCount(lp: LessonProgress): number {
  return Object.values(lp.exercises).filter((ep) => ep.completed).length;
}

interface ProgressData {
  lessons: Record<string, LessonProgress>;
}

export class ProgressManager {
  private lessons: Record<string, LessonProgress> = {};
  private db: IDBDatabase | null = null;

  async init(): Promise<void> {
    this.db = await this.openDB();
    await this.load();
  }

  private openDB(): Promise<IDBDatabase> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME);
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  private async load(): Promise<void> {
    if (!this.db) return;
    const data = await this.dbGet<ProgressData>(PROGRESS_KEY);
    if (data?.lessons) {
      this.lessons = data.lessons;
    }
  }

  private async save(): Promise<void> {
    if (!this.db) return;
    const data: ProgressData = { lessons: this.lessons };
    await this.dbPut(PROGRESS_KEY, data);
  }

  private dbGet<T>(key: string): Promise<T | undefined> {
    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, "readonly");
      const store = tx.objectStore(STORE_NAME);
      const req = store.get(key);
      req.onsuccess = () => resolve(req.result as T | undefined);
      req.onerror = () => reject(req.error);
    });
  }

  private dbPut(key: string, value: unknown): Promise<void> {
    return new Promise((resolve, reject) => {
      const tx = this.db!.transaction(STORE_NAME, "readwrite");
      const store = tx.objectStore(STORE_NAME);
      const req = store.put(value, key);
      req.onsuccess = () => resolve();
      req.onerror = () => reject(req.error);
    });
  }

  getLesson(lessonId: string): LessonProgress {
    if (!this.lessons[lessonId]) {
      this.lessons[lessonId] = { exercises: {} };
    }
    return this.lessons[lessonId];
  }

  async recordExercise(
    lessonId: string,
    exerciseId: string,
    xpEarned: number,
    attempts: number,
    hintsUsed: number,
  ): Promise<void> {
    const lp = this.getLesson(lessonId);
    lp.exercises[exerciseId] = {
      completed: true,
      xp_earned: xpEarned,
      attempts,
      hints_used: hintsUsed,
    };
    await this.save();
  }

  get totalXp(): number {
    return Object.values(this.lessons).reduce((s, lp) => s + lessonTotalXp(lp), 0);
  }

  get completedLessons(): Set<string> {
    const set = new Set<string>();
    for (const [id, lp] of Object.entries(this.lessons)) {
      if (isLessonCompleted(lp)) set.add(id);
    }
    return set;
  }

  isExerciseCompleted(lessonId: string, exerciseId: string): boolean {
    const lp = this.lessons[lessonId];
    if (!lp) return false;
    const ep = lp.exercises[exerciseId];
    return ep != null && ep.completed;
  }

  exerciseProgress(): Record<string, number> {
    const result: Record<string, number> = {};
    for (const [id, lp] of Object.entries(this.lessons)) {
      result[id] = lessonCompletedCount(lp);
    }
    return result;
  }

  async resetLesson(lessonId: string): Promise<void> {
    delete this.lessons[lessonId];
    await this.save();
  }

  async resetAll(): Promise<void> {
    this.lessons = {};
    await this.save();
  }
}
