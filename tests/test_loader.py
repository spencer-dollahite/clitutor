"""Tests for lesson loader."""
import json
from pathlib import Path

import pytest

from clitutor.core.loader import LessonLoader


@pytest.fixture
def lesson_dir(tmp_path):
    """Create a temporary lesson directory with a sample lesson."""
    # metadata.json
    metadata = {
        "lessons": [
            {
                "id": "test_lesson",
                "title": "Test Lesson",
                "slug": "test-lesson",
                "order": 0,
                "category": "test",
                "difficulty": 1,
                "description": "A test lesson",
                "xp": 20,
                "exercise_count": 2,
                "file": "test_lesson.md",
            }
        ]
    }
    (tmp_path / "metadata.json").write_text(json.dumps(metadata))

    # lesson markdown
    content = """# Test Lesson

Some introductory content.

<!-- exercise
id: ex01
title: Say hello
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: output_contains
expected: hello
hints:
  - "Think about echoing something."
  - "Use the echo command."
  - "Type: echo hello"
-->
### Exercise 1: Say hello
Run a command that outputs "hello".

<!-- exercise
id: ex02
title: Create a file
xp: 10
difficulty: 1
sandbox_setup: null
validation_type: file_exists
expected: test.txt
hints:
  - "You need to create a file."
  - "Use the touch command."
  - "Type: touch test.txt"
-->
### Exercise 2: Create a file
Create a file called test.txt.
"""
    (tmp_path / "test_lesson.md").write_text(content)
    return tmp_path


class TestLessonLoader:
    def test_load_metadata(self, lesson_dir):
        loader = LessonLoader(lesson_dir)
        meta = loader.load_metadata()
        assert len(meta) == 1
        assert meta[0].id == "test_lesson"
        assert meta[0].title == "Test Lesson"
        assert meta[0].xp == 20

    def test_load_lesson(self, lesson_dir):
        loader = LessonLoader(lesson_dir)
        meta = loader.load_metadata()[0]
        lesson = loader.load_lesson(meta)
        assert lesson.id == "test_lesson"
        assert lesson.title == "Test Lesson"
        assert len(lesson.exercises) == 2

    def test_exercise_fields(self, lesson_dir):
        loader = LessonLoader(lesson_dir)
        meta = loader.load_metadata()[0]
        lesson = loader.load_lesson(meta)
        ex = lesson.exercises[0]
        assert ex.id == "ex01"
        assert ex.title == "Say hello"
        assert ex.xp == 10
        assert ex.validation_type == "output_contains"
        assert ex.expected == "hello"
        assert len(ex.hints) == 3

    def test_exercise_comments_stripped(self, lesson_dir):
        loader = LessonLoader(lesson_dir)
        meta = loader.load_metadata()[0]
        lesson = loader.load_lesson(meta)
        assert "<!-- exercise" not in lesson.content_markdown
        assert "Exercise 1" in lesson.content_markdown

    def test_load_all(self, lesson_dir):
        loader = LessonLoader(lesson_dir)
        lessons = loader.load_all()
        assert len(lessons) == 1
        assert lessons[0].id == "test_lesson"

    def test_missing_lesson_file(self, lesson_dir):
        loader = LessonLoader(lesson_dir)
        meta = loader.load_metadata()[0]
        # Delete the lesson file
        (lesson_dir / "test_lesson.md").unlink()
        with pytest.raises(FileNotFoundError):
            loader.load_lesson(meta)

    def test_load_all_skips_missing(self, lesson_dir):
        loader = LessonLoader(lesson_dir)
        (lesson_dir / "test_lesson.md").unlink()
        lessons = loader.load_all()
        assert len(lessons) == 0

    def test_empty_metadata(self, tmp_path):
        (tmp_path / "metadata.json").write_text('{"lessons": []}')
        loader = LessonLoader(tmp_path)
        assert loader.load_metadata() == []

    def test_no_metadata_file(self, tmp_path):
        loader = LessonLoader(tmp_path)
        assert loader.load_metadata() == []
