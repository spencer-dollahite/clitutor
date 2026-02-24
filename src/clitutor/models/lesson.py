"""Dataclasses for lesson and exercise data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Exercise:
    """A single exercise within a lesson."""
    id: str
    title: str
    xp: int = 10
    difficulty: int = 1
    sandbox_setup: Optional[List[str]] = None
    validation_type: str = "output_contains"
    expected: str = ""
    hints: List[str] = field(default_factory=list)

    # Runtime state (not persisted in lesson file)
    attempts: int = 0
    first_try: bool = True
    hints_used: int = 0
    completed: bool = False


@dataclass
class LessonData:
    """A full lesson with content and exercises."""
    id: str
    title: str
    slug: str
    order: int
    category: str = "basics"
    difficulty: int = 1
    description: str = ""
    content_markdown: str = ""
    exercises: List[Exercise] = field(default_factory=list)

    @property
    def total_xp(self) -> int:
        return sum(ex.xp for ex in self.exercises)

    @property
    def exercise_count(self) -> int:
        return len(self.exercises)


@dataclass
class LessonMeta:
    """Metadata entry for a lesson in metadata.json."""
    id: str
    title: str
    slug: str
    order: int
    category: str
    difficulty: int
    description: str
    xp: int
    exercise_count: int
    file: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LessonMeta":
        return cls(**data)
