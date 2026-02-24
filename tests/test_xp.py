"""Tests for XP formulas and level system."""
import pytest

from clitutor.models.xp import calculate_xp, get_level_info, LEVEL_TABLE


class TestCalculateXP:
    def test_base_xp_first_try_no_hints(self):
        # multiplier = 1.0 + 0.0 (diff=1) + 0.50 (first_try) - 0.0 = 1.50
        assert calculate_xp(10, difficulty=1, first_try=True, hints_used=0) == 15

    def test_base_xp_not_first_try(self):
        # multiplier = 1.0 + 0.0 + 0.0 - 0.0 = 1.0
        assert calculate_xp(10, difficulty=1, first_try=False, hints_used=0) == 10

    def test_difficulty_bonus(self):
        # multiplier = 1.0 + 0.20 (diff=3) + 0.50 - 0.0 = 1.70
        assert calculate_xp(10, difficulty=3, first_try=True, hints_used=0) == 17

    def test_hint_penalty_one(self):
        # multiplier = 1.0 + 0.0 + 0.50 - 0.10 = 1.40
        assert calculate_xp(10, difficulty=1, first_try=True, hints_used=1) == 14

    def test_hint_penalty_two(self):
        # multiplier = 1.0 + 0.0 + 0.50 - 0.30 = 1.20
        assert calculate_xp(10, difficulty=1, first_try=True, hints_used=2) == 12

    def test_hint_penalty_three(self):
        # multiplier = 1.0 + 0.0 + 0.50 - 0.50 = 1.00
        assert calculate_xp(10, difficulty=1, first_try=True, hints_used=3) == 10

    def test_floor_at_025(self):
        # multiplier = 1.0 + 0.0 + 0.0 - 0.50 = 0.50, but scenario with more penalty
        # Not first try + max hints: 1.0 + 0.0 + 0.0 - 0.50 = 0.50
        assert calculate_xp(10, difficulty=1, first_try=False, hints_used=3) == 5

    def test_floor_enforced(self):
        # Test that the floor of 0.25 is enforced
        # Even with worst case, should be at least base * 0.25
        result = calculate_xp(100, difficulty=1, first_try=False, hints_used=3)
        assert result >= 25

    def test_zero_base_xp(self):
        assert calculate_xp(0) == 0

    def test_large_difficulty(self):
        # multiplier = 1.0 + 0.40 (diff=5) + 0.50 - 0.0 = 1.90
        assert calculate_xp(100, difficulty=5, first_try=True, hints_used=0) == 190

    def test_hints_capped_at_three(self):
        # hints_used=10 should be treated as 3
        result = calculate_xp(10, difficulty=1, first_try=True, hints_used=10)
        expected = calculate_xp(10, difficulty=1, first_try=True, hints_used=3)
        assert result == expected


class TestGetLevelInfo:
    def test_level_zero(self):
        info = get_level_info(0)
        assert info.level == 0
        assert info.title == "Newbie"
        assert info.level_floor == 0
        assert info.level_ceiling == 50

    def test_level_one(self):
        info = get_level_info(50)
        assert info.level == 1
        assert info.title == "Curious Cat"
        assert info.level_floor == 50
        assert info.level_ceiling == 150

    def test_just_under_threshold(self):
        info = get_level_info(49)
        assert info.level == 0
        assert info.title == "Newbie"

    def test_max_level(self):
        info = get_level_info(9999)
        assert info.level == len(LEVEL_TABLE) - 1
        assert info.title == "BDFL"

    def test_progress_half(self):
        info = get_level_info(25)
        assert info.progress == pytest.approx(0.5)

    def test_progress_zero(self):
        info = get_level_info(0)
        assert info.progress == pytest.approx(0.0)

    def test_xp_in_level(self):
        info = get_level_info(75)
        assert info.xp_in_level == 25  # 75 - 50 floor
        assert info.xp_for_level == 100  # 150 - 50

    def test_mid_range_level(self):
        info = get_level_info(500)
        assert info.level == 4
        assert info.title == "Shell Wrangler"
