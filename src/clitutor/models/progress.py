"""Progress persistence to ~/.clitutor/progress.json."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Set

from clitutor import PROGRESS_DIR, PROGRESS_FILE


@dataclass
class ExerciseProgress:
    """Progress for a single exercise."""
    completed: bool = False
    xp_earned: int = 0
    attempts: int = 0
    hints_used: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "completed": self.completed,
            "xp_earned": self.xp_earned,
            "attempts": self.attempts,
            "hints_used": self.hints_used,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExerciseProgress":
        return cls(
            completed=data.get("completed", False),
            xp_earned=data.get("xp_earned", 0),
            attempts=data.get("attempts", 0),
            hints_used=data.get("hints_used", 0),
        )


@dataclass
class LessonProgress:
    """Progress for a lesson."""
    exercises: Dict[str, ExerciseProgress] = field(default_factory=dict)

    @property
    def completed(self) -> bool:
        return len(self.exercises) > 0 and all(
            ep.completed for ep in self.exercises.values()
        )

    @property
    def total_xp(self) -> int:
        return sum(ep.xp_earned for ep in self.exercises.values())

    @property
    def completed_count(self) -> int:
        return sum(1 for ep in self.exercises.values() if ep.completed)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "exercises": {k: v.to_dict() for k, v in self.exercises.items()}
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LessonProgress":
        exercises = {}
        for k, v in data.get("exercises", {}).items():
            exercises[k] = ExerciseProgress.from_dict(v)
        return cls(exercises=exercises)


class ProgressManager:
    """Manages reading/writing progress to JSON file."""

    def __init__(self, path: str | None = None):
        self._path = Path(os.path.expanduser(path or PROGRESS_FILE))
        self._lessons: Dict[str, LessonProgress] = {}
        self._load()

    def _load(self) -> None:
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text())
                for lesson_id, lesson_data in data.get("lessons", {}).items():
                    self._lessons[lesson_id] = LessonProgress.from_dict(lesson_data)
            except (json.JSONDecodeError, KeyError):
                self._lessons = {}

    def save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "lessons": {k: v.to_dict() for k, v in self._lessons.items()}
        }
        self._path.write_text(json.dumps(data, indent=2) + "\n")

    def get_lesson(self, lesson_id: str) -> LessonProgress:
        if lesson_id not in self._lessons:
            self._lessons[lesson_id] = LessonProgress()
        return self._lessons[lesson_id]

    def record_exercise(
        self,
        lesson_id: str,
        exercise_id: str,
        xp_earned: int,
        attempts: int,
        hints_used: int,
    ) -> None:
        lp = self.get_lesson(lesson_id)
        lp.exercises[exercise_id] = ExerciseProgress(
            completed=True,
            xp_earned=xp_earned,
            attempts=attempts,
            hints_used=hints_used,
        )
        self.save()

    @property
    def total_xp(self) -> int:
        return sum(lp.total_xp for lp in self._lessons.values())

    @property
    def completed_lessons(self) -> Set[str]:
        return {lid for lid, lp in self._lessons.items() if lp.completed}

    def is_exercise_completed(self, lesson_id: str, exercise_id: str) -> bool:
        lp = self._lessons.get(lesson_id)
        if lp is None:
            return False
        ep = lp.exercises.get(exercise_id)
        return ep is not None and ep.completed

    def reset_lesson(self, lesson_id: str) -> None:
        if lesson_id in self._lessons:
            del self._lessons[lesson_id]
            self.save()

    @property
    def exercise_progress(self) -> Dict[str, int]:
        """Return {lesson_id: completed_exercise_count} for all lessons."""
        return {lid: lp.completed_count for lid, lp in self._lessons.items()}

    def reset_all(self) -> None:
        self._lessons.clear()
        self.save()
