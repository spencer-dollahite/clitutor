/** XP formulas, level thresholds, and titles — port of models/xp.py */

// (cumulative_xp_threshold, title)
export const LEVEL_TABLE: [number, string][] = [
  [0, "Newbie"],
  [50, "Curious Cat"],
  [150, "Script Kiddie"],
  [300, "Terminal Apprentice"],
  [500, "Shell Wrangler"],
  [750, "Pipe Plumber"],
  [1050, "Regex Ranger"],
  [1400, "Sysadmin Acolyte"],
  [1800, "Root Whisperer"],
  [2250, "Kernel Sage"],
  [2750, "Daemon Tamer"],
  [3300, "Syscall Sorcerer"],
  [3900, "Namespace Ninja"],
  [4550, "Container Captain"],
  [5250, "Cluster Commander"],
  [6000, "Infra Overlord"],
  [6500, "BDFL"],
];

// Hint penalty map: hints_used -> penalty
const HINT_PENALTIES: Record<number, number> = { 0: 0.0, 1: 0.10, 2: 0.30, 3: 0.50 };

export interface LevelInfo {
  level: number;
  title: string;
  current_xp: number;
  level_floor: number;
  level_ceiling: number;
}

export function xpInLevel(info: LevelInfo): number {
  return info.current_xp - info.level_floor;
}

export function xpForLevel(info: LevelInfo): number {
  return info.level_ceiling - info.level_floor;
}

export function levelProgress(info: LevelInfo): number {
  const needed = xpForLevel(info);
  if (needed === 0) return 1.0;
  return xpInLevel(info) / needed;
}

export function getLevelInfo(totalXp: number): LevelInfo {
  let level = 0;
  for (let i = 0; i < LEVEL_TABLE.length; i++) {
    if (totalXp >= LEVEL_TABLE[i][0]) {
      level = i;
    } else {
      break;
    }
  }

  const [floorXp, title] = LEVEL_TABLE[level];
  const ceilingXp = level + 1 < LEVEL_TABLE.length ? LEVEL_TABLE[level + 1][0] : floorXp;

  return {
    level,
    title,
    current_xp: totalXp,
    level_floor: floorXp,
    level_ceiling: ceilingXp,
  };
}

export function calculateXp(
  baseXp: number,
  difficulty: number = 1,
  firstTry: boolean = true,
  hintsUsed: number = 0,
): number {
  let multiplier = 1.0;
  multiplier += (difficulty - 1) * 0.10;
  if (firstTry) multiplier += 0.50;
  const hintPenalty = HINT_PENALTIES[Math.min(hintsUsed, 3)] ?? 0.50;
  multiplier -= hintPenalty;
  multiplier = Math.max(multiplier, 0.25);
  return Math.floor(baseXp * multiplier);
}
