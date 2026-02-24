"""Lesson loader - parses markdown files with embedded exercise metadata."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List, Optional

import yaml

from clitutor.models.lesson import Exercise, LessonData, LessonMeta

EXERCISE_PATTERN = re.compile(
    r"<!--\s*exercise\s*\n(.*?)-->",
    re.DOTALL,
)


class LessonLoader:
    """Loads and parses lesson markdown files."""

    def __init__(self, lessons_dir: Optional[Path] = None) -> None:
        if lessons_dir is None:
            lessons_dir = Path(__file__).parent.parent / "lessons"
        self.lessons_dir = lessons_dir

    def load_metadata(self) -> List[LessonMeta]:
        """Load the lesson metadata index."""
        meta_path = self.lessons_dir / "metadata.json"
        if not meta_path.exists():
            return []
        data = json.loads(meta_path.read_text())
        lessons = [LessonMeta.from_dict(entry) for entry in data["lessons"]]
        lessons.sort(key=lambda m: m.order)
        return lessons

    def load_lesson(self, meta: LessonMeta) -> LessonData:
        """Load a full lesson from its markdown file."""
        md_path = self.lessons_dir / meta.file
        if not md_path.exists():
            raise FileNotFoundError(f"Lesson file not found: {md_path}")

        content = md_path.read_text()
        exercises = self._extract_exercises(content)

        # Strip exercise comments from content for display
        display_content = EXERCISE_PATTERN.sub("", content).strip()

        return LessonData(
            id=meta.id,
            title=meta.title,
            slug=meta.slug,
            order=meta.order,
            category=meta.category,
            difficulty=meta.difficulty,
            description=meta.description,
            content_markdown=display_content,
            exercises=exercises,
        )

    def _extract_exercises(self, content: str) -> List[Exercise]:
        """Extract exercise metadata from HTML comments in markdown."""
        exercises = []
        for match in EXERCISE_PATTERN.finditer(content):
            yaml_str = match.group(1)
            try:
                data = yaml.safe_load(yaml_str)
                if data and isinstance(data, dict):
                    exercises.append(Exercise(
                        id=str(data.get("id", f"ex{len(exercises)}")),
                        title=str(data.get("title", "Untitled")),
                        xp=int(data.get("xp", 10)),
                        difficulty=int(data.get("difficulty", 1)),
                        sandbox_setup=data.get("sandbox_setup"),
                        validation_type=str(data.get("validation_type", "output_contains")),
                        expected=str(data.get("expected", "")),
                        hints=list(data.get("hints", [])),
                    ))
            except yaml.YAMLError:
                continue
        return exercises

    def load_all(self) -> List[LessonData]:
        """Load all lessons."""
        metadata = self.load_metadata()
        lessons = []
        for meta in metadata:
            try:
                lessons.append(self.load_lesson(meta))
            except FileNotFoundError:
                continue
        return lessons
