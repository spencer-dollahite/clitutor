"""XP formulas, level thresholds, and titles."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

# (cumulative_xp_threshold, title)
LEVEL_TABLE: List[Tuple[int, str]] = [
    (0, "Newbie"),
    (50, "Curious Cat"),
    (150, "Script Kiddie"),
    (300, "Terminal Apprentice"),
    (500, "Shell Wrangler"),
    (750, "Pipe Plumber"),
    (1050, "Regex Ranger"),
    (1400, "Sysadmin Acolyte"),
    (1800, "Root Whisperer"),
    (2250, "Kernel Sage"),
    (2750, "Daemon Tamer"),
    (3300, "Syscall Sorcerer"),
    (3900, "Namespace Ninja"),
    (4550, "Container Captain"),
    (5250, "Cluster Commander"),
    (6000, "Infra Overlord"),
    (6500, "BDFL"),
]

# Hint penalty map: hints_used -> penalty
HINT_PENALTIES = {0: 0.0, 1: 0.10, 2: 0.30, 3: 0.50}


@dataclass
class LevelInfo:
    """Current level information for a given XP total."""
    level: int
    title: str
    current_xp: int
    level_floor: int
    level_ceiling: int

    @property
    def xp_in_level(self) -> int:
        return self.current_xp - self.level_floor

    @property
    def xp_for_level(self) -> int:
        return self.level_ceiling - self.level_floor

    @property
    def progress(self) -> float:
        if self.xp_for_level == 0:
            return 1.0
        return self.xp_in_level / self.xp_for_level


def get_level_info(total_xp: int) -> LevelInfo:
    """Determine level info from total XP."""
    level = 0
    for i, (threshold, _title) in enumerate(LEVEL_TABLE):
        if total_xp >= threshold:
            level = i
        else:
            break

    _floor_xp, title = LEVEL_TABLE[level]
    floor_xp = LEVEL_TABLE[level][0]

    if level + 1 < len(LEVEL_TABLE):
        ceiling_xp = LEVEL_TABLE[level + 1][0]
    else:
        # Max level
        ceiling_xp = floor_xp

    return LevelInfo(
        level=level,
        title=title,
        current_xp=total_xp,
        level_floor=floor_xp,
        level_ceiling=ceiling_xp,
    )


def calculate_xp(
    base_xp: int,
    difficulty: int = 1,
    first_try: bool = True,
    hints_used: int = 0,
) -> int:
    """Calculate XP earned for completing an exercise.

    XP = base_xp * multiplier
      multiplier starts at 1.0
      + (difficulty - 1) * 0.10   (difficulty bonus)
      + 0.50 if first_try          (first-try bonus)
      - hint_penalty[hints_used]   (hint penalty)
      floor at 0.25
    """
    multiplier = 1.0
    multiplier += (difficulty - 1) * 0.10
    if first_try:
        multiplier += 0.50
    hint_penalty = HINT_PENALTIES.get(min(hints_used, 3), 0.50)
    multiplier -= hint_penalty
    multiplier = max(multiplier, 0.25)
    return int(base_xp * multiplier)
