"""Pet data model, persistence, and leveling logic."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_DATA_DIR = Path.home() / ".claude-pet"

SPECIES_LIST = ["cat", "dog", "fox", "rabbit", "frog", "penguin", "owl", "snake", "axolotl"]

XP_EVENTS = {
    "test_pass": 10,
    "test_fail": 2,
    "commit": 15,
    "long_session": 20,
    "error_fixed": 25,
    "idle_return": 5,
    "session_start": 0,
    "error": 0,
}

MAX_LEVEL = 20

# Each level N requires N * 50 XP to go from N to N+1
def xp_for_level(level: int) -> int:
    """XP required to go from level-1 to level."""
    return level * 50


def total_xp_for_level(level: int) -> int:
    """Total cumulative XP needed to reach a given level."""
    # Level 1 = 0 XP, Level 2 = 100 XP, Level 3 = 250 XP, etc.
    return sum(xp_for_level(lv) for lv in range(2, level + 1))


# Unlock definitions per level
UNLOCK_TABLE: dict[int, dict[str, list[str]]] = {
    1: {"colors": ["white", "gray", "black"], "eyes": ["default", "cute"], "patterns": ["solid", "tabby"], "accessories": {}},
    2: {"colors": ["orange", "brown"]},
    3: {"eyes": ["sleepy"]},
    4: {"accessories": {"collar": ["simple"]}},
    5: {"patterns": ["spotted"], "eyes": ["surprised"]},
    6: {"accessories": {"scarf": ["basic"]}},
    7: {"colors": ["golden", "blue"]},
    8: {"eyes": ["wink"], "patterns": ["striped"]},
    9: {"accessories": {"hat": ["beanie"]}},
    10: {"accessories": {"hat": ["tophat", "cap"]}, "patterns": ["tuxedo"]},
    11: {"accessories": {"glasses": ["round"]}},
    12: {"colors": ["purple"], "eyes": ["focused"]},
    13: {"accessories": {"cape": ["short"]}},
    14: {"accessories": {"hat": ["wizard"]}},
    15: {"eyes": ["cool"], "accessories": {"scarf": ["striped"]}},
    16: {"accessories": {"collar": ["spiked", "bowtie"]}},
    17: {"accessories": {"cape": ["long", "royal"]}},
    18: {"accessories": {"glasses": ["monocle"], "hat": ["crown"]}},
    19: {"accessories": {"glasses": ["star"], "cape": ["sparkle"]}},
    20: {"titles": ["Master Coder", "Terminal Tamer", "Bug Slayer", "Code Wizard"]},
}


def get_unlocks_at_level(level: int) -> dict:
    """Get the specific unlocks granted at a given level."""
    return UNLOCK_TABLE.get(level, {})


def get_all_unlocked(level: int) -> dict[str, list[str]]:
    """Get all unlocked options up to and including the given level."""
    result: dict[str, list[str]] = {
        "colors": [],
        "eyes": [],
        "patterns": [],
        "titles": [],
    }
    accessories: dict[str, list[str]] = {}

    for lv in range(1, level + 1):
        unlocks = UNLOCK_TABLE.get(lv, {})
        for key in ("colors", "eyes", "patterns", "titles"):
            if key in unlocks:
                result[key].extend(unlocks[key])
        if "accessories" in unlocks:
            for slot, items in unlocks["accessories"].items():
                if slot not in accessories:
                    accessories[slot] = []
                accessories[slot].extend(items)

    result["accessories"] = accessories
    return result


@dataclass
class PetStats:
    tests_passed: int = 0
    tests_failed: int = 0
    commits: int = 0
    errors_fixed: int = 0
    sessions: int = 0
    total_session_minutes: int = 0


@dataclass
class PetData:
    species: str
    name: str
    color: str = "white"
    pattern: str = "solid"
    eyes: str = "default"
    accessories: dict[str, str] = field(default_factory=dict)
    level: int = 1
    xp: int = 0
    mood: str = "idle"
    mood_updated: str = ""
    stats: PetStats = field(default_factory=PetStats)
    created: str = ""
    title: str = ""

    def __post_init__(self):
        if not self.created:
            self.created = datetime.now(timezone.utc).isoformat()
        if not self.mood_updated:
            self.mood_updated = datetime.now(timezone.utc).isoformat()
        if isinstance(self.stats, dict):
            self.stats = PetStats(**self.stats)

    def add_xp(self, amount: int) -> bool:
        """Add XP and handle level-ups. Returns True if leveled up."""
        if self.level >= MAX_LEVEL:
            return False

        self.xp += amount
        leveled_up = False

        while self.level < MAX_LEVEL:
            xp_needed = total_xp_for_level(self.level + 1)
            if self.xp >= xp_needed:
                self.level += 1
                leveled_up = True
            else:
                break

        return leveled_up

    def xp_progress(self) -> tuple[int, int]:
        """Returns (current_xp_in_level, xp_needed_for_next_level)."""
        if self.level >= MAX_LEVEL:
            return (0, 0)
        current_level_xp = total_xp_for_level(self.level)
        next_level_xp = total_xp_for_level(self.level + 1)
        return (self.xp - current_level_xp, next_level_xp - current_level_xp)

    def set_mood(self, mood: str) -> None:
        self.mood = mood
        self.mood_updated = datetime.now(timezone.utc).isoformat()


def save_pet(pet: PetData, data_dir: Path = DEFAULT_DATA_DIR) -> None:
    """Save pet data to JSON file."""
    data_dir.mkdir(parents=True, exist_ok=True)
    data = asdict(pet)
    (data_dir / "pet.json").write_text(json.dumps(data, indent=2))


def load_pet(data_dir: Path = DEFAULT_DATA_DIR) -> PetData | None:
    """Load pet data from JSON file. Returns None if no pet exists."""
    pet_file = data_dir / "pet.json"
    if not pet_file.exists():
        return None
    data = json.loads(pet_file.read_text())
    return PetData(**data)


def reset_pet(data_dir: Path = DEFAULT_DATA_DIR, confirm: bool = True) -> None:
    """Delete pet data. If confirm=True, ask user first."""
    pet_file = data_dir / "pet.json"
    if not pet_file.exists():
        print("No pet data found.")
        return

    if confirm:
        response = input("Are you sure you want to reset your pet? This cannot be undone. [y/N] ")
        if response.lower() != "y":
            print("Reset cancelled.")
            return

    pet_file.unlink()
    print("Pet data reset. Run 'claude-pet design' to create a new pet.")
