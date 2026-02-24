"""Tests for progress persistence."""
import json
import tempfile
from pathlib import Path

import pytest

from clitutor.models.progress import ExerciseProgress, LessonProgress, ProgressManager


@pytest.fixture
def tmp_progress_file(tmp_path):
    return str(tmp_path / "progress.json")


class TestExerciseProgress:
    def test_defaults(self):
        ep = ExerciseProgress()
        assert not ep.completed
        assert ep.xp_earned == 0
        assert ep.attempts == 0
        assert ep.hints_used == 0

    def test_round_trip(self):
        ep = ExerciseProgress(completed=True, xp_earned=15, attempts=3, hints_used=2)
        data = ep.to_dict()
        ep2 = ExerciseProgress.from_dict(data)
        assert ep2.completed is True
        assert ep2.xp_earned == 15
        assert ep2.attempts == 3
        assert ep2.hints_used == 2


class TestLessonProgress:
    def test_empty_not_completed(self):
        lp = LessonProgress()
        assert not lp.completed
        assert lp.total_xp == 0
        assert lp.completed_count == 0

    def test_all_completed(self):
        lp = LessonProgress(exercises={
            "ex01": ExerciseProgress(completed=True, xp_earned=10),
            "ex02": ExerciseProgress(completed=True, xp_earned=15),
        })
        assert lp.completed is True
        assert lp.total_xp == 25
        assert lp.completed_count == 2

    def test_partially_completed(self):
        lp = LessonProgress(exercises={
            "ex01": ExerciseProgress(completed=True, xp_earned=10),
            "ex02": ExerciseProgress(completed=False),
        })
        assert lp.completed is False
        assert lp.completed_count == 1


class TestProgressManager:
    def test_empty_state(self, tmp_progress_file):
        pm = ProgressManager(tmp_progress_file)
        assert pm.total_xp == 0
        assert pm.completed_lessons == set()

    def test_record_exercise(self, tmp_progress_file):
        pm = ProgressManager(tmp_progress_file)
        pm.record_exercise("lesson01", "ex01", xp_earned=15, attempts=2, hints_used=1)
        assert pm.total_xp == 15
        assert pm.is_exercise_completed("lesson01", "ex01")

    def test_persistence(self, tmp_progress_file):
        pm1 = ProgressManager(tmp_progress_file)
        pm1.record_exercise("lesson01", "ex01", xp_earned=15, attempts=1, hints_used=0)

        pm2 = ProgressManager(tmp_progress_file)
        assert pm2.total_xp == 15
        assert pm2.is_exercise_completed("lesson01", "ex01")

    def test_completed_lessons(self, tmp_progress_file):
        pm = ProgressManager(tmp_progress_file)
        pm.record_exercise("lesson01", "ex01", xp_earned=10, attempts=1, hints_used=0)
        pm.record_exercise("lesson01", "ex02", xp_earned=10, attempts=1, hints_used=0)
        # Only if we define "completion" as "all exercises recorded"
        assert "lesson01" in pm.completed_lessons

    def test_reset_lesson(self, tmp_progress_file):
        pm = ProgressManager(tmp_progress_file)
        pm.record_exercise("lesson01", "ex01", xp_earned=10, attempts=1, hints_used=0)
        pm.reset_lesson("lesson01")
        assert pm.total_xp == 0
        assert not pm.is_exercise_completed("lesson01", "ex01")

    def test_reset_all(self, tmp_progress_file):
        pm = ProgressManager(tmp_progress_file)
        pm.record_exercise("lesson01", "ex01", xp_earned=10, attempts=1, hints_used=0)
        pm.record_exercise("lesson02", "ex01", xp_earned=20, attempts=1, hints_used=0)
        pm.reset_all()
        assert pm.total_xp == 0
        assert pm.completed_lessons == set()

    def test_corrupt_file(self, tmp_path):
        path = tmp_path / "progress.json"
        path.write_text("not json at all{{{")
        pm = ProgressManager(str(path))
        assert pm.total_xp == 0

    def test_not_completed_exercise(self, tmp_progress_file):
        pm = ProgressManager(tmp_progress_file)
        assert not pm.is_exercise_completed("nonexistent", "ex01")
