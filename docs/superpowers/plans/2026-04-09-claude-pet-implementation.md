# claude-pet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code plugin that gives users a persistent, customizable ASCII pet companion that reacts to coding activity and levels up over time.

**Architecture:** Claude Code plugin with three layers — plugin metadata (skill + command), a Python MCP server exposing pet tools over stdio, and a Textual TUI for pet design launched in a separate terminal. State persists to `~/.claude-pet/pet.json`.

**Tech Stack:** Python 3.10+, mcp[cli] (FastMCP), Textual, Rich, uv/uvx

---

### Task 1: Project Scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `src/claude_pet/__init__.py`
- Create: `src/claude_pet/cli.py`
- Create: `.claude-plugin/plugin.json`
- Create: `.mcp.json`
- Create: `.gitignore`

- [ ] **Step 1: Create pyproject.toml**

```toml
[project]
name = "claude-pet"
version = "0.1.0"
description = "A Claude Code plugin that gives you a persistent, customizable ASCII pet companion"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "mcp[cli]>=1.2.0",
    "textual>=0.80.0",
    "rich>=13.0.0",
]

[project.scripts]
claude-pet = "claude_pet.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

- [ ] **Step 2: Create src/claude_pet/__init__.py**

```python
"""claude-pet: A Claude Code plugin for a persistent ASCII pet companion."""
```

- [ ] **Step 3: Create src/claude_pet/cli.py**

```python
"""CLI entry point for claude-pet."""

import sys


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: claude-pet <command>")
        print("Commands: serve, design, show, reset")
        sys.exit(1)

    command = sys.argv[1]

    if command == "serve":
        from claude_pet.server import serve
        serve()
    elif command == "design":
        from claude_pet.designer import run_designer
        run_designer()
    elif command == "show":
        from claude_pet.ascii_art import render_pet_full
        from claude_pet.models import load_pet
        pet = load_pet()
        if pet is None:
            print("No pet found. Run 'claude-pet design' to create one.")
            sys.exit(1)
        print(render_pet_full(pet))
    elif command == "reset":
        from claude_pet.models import reset_pet
        reset_pet()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: Create .claude-plugin/plugin.json**

```json
{
  "name": "claude-pet",
  "description": "A persistent ASCII pet companion that reacts to your coding activity, levels up as you work, and develops personality.",
  "author": {
    "name": "Alex"
  }
}
```

- [ ] **Step 5: Create .mcp.json**

```json
{
  "claude-pet": {
    "command": "uvx",
    "args": ["claude-pet", "serve"]
  }
}
```

- [ ] **Step 6: Create .gitignore**

```
__pycache__/
*.pyc
*.egg-info/
dist/
build/
.venv/
.superpowers/
```

- [ ] **Step 7: Initialize uv environment and verify**

Run: `cd /home/alex/Projects/claude-pet && uv venv && uv pip install -e .`
Expected: Installs successfully, `claude-pet` CLI is available.

- [ ] **Step 8: Verify CLI entry point works**

Run: `cd /home/alex/Projects/claude-pet && uv run claude-pet`
Expected: Prints usage message with available commands.

- [ ] **Step 9: Commit**

```bash
git add pyproject.toml src/ .claude-plugin/ .mcp.json .gitignore
git commit -m "feat: project scaffolding with CLI entry point"
```

---

### Task 2: Pet Data Model & Persistence

**Files:**
- Create: `src/claude_pet/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing tests for the pet model**

```python
"""Tests for pet data model and persistence."""

import json
import tempfile
from pathlib import Path

from claude_pet.models import (
    PetData,
    load_pet,
    save_pet,
    reset_pet,
    xp_for_level,
    total_xp_for_level,
    get_unlocks_at_level,
    get_all_unlocked,
)


def test_xp_for_level():
    assert xp_for_level(2) == 100
    assert xp_for_level(10) == 500
    assert xp_for_level(20) == 1000


def test_total_xp_for_level():
    assert total_xp_for_level(1) == 0
    assert total_xp_for_level(2) == 100
    assert total_xp_for_level(3) == 250  # 100 + 150


def test_pet_data_defaults():
    pet = PetData(species="cat", name="Witty")
    assert pet.level == 1
    assert pet.xp == 0
    assert pet.mood == "idle"
    assert pet.color == "white"
    assert pet.eyes == "default"
    assert pet.pattern == "solid"
    assert pet.accessories == {}
    assert pet.stats.tests_passed == 0


def test_pet_data_add_xp_no_levelup():
    pet = PetData(species="cat", name="Witty")
    leveled_up = pet.add_xp(50)
    assert pet.xp == 50
    assert pet.level == 1
    assert leveled_up is False


def test_pet_data_add_xp_levelup():
    pet = PetData(species="cat", name="Witty")
    leveled_up = pet.add_xp(100)
    assert pet.xp == 100
    assert pet.level == 2
    assert leveled_up is True


def test_pet_data_add_xp_multi_levelup():
    pet = PetData(species="cat", name="Witty")
    pet.add_xp(300)  # enough for level 1->2 (100) and 2->3 (150), total 250
    assert pet.level == 3
    assert pet.xp == 300


def test_save_and_load_pet(tmp_path):
    pet = PetData(species="fox", name="Sly")
    pet.color = "orange"
    pet.xp = 150
    pet.level = 2

    save_pet(pet, data_dir=tmp_path)
    loaded = load_pet(data_dir=tmp_path)

    assert loaded is not None
    assert loaded.species == "fox"
    assert loaded.name == "Sly"
    assert loaded.color == "orange"
    assert loaded.xp == 150
    assert loaded.level == 2


def test_load_pet_no_file(tmp_path):
    loaded = load_pet(data_dir=tmp_path)
    assert loaded is None


def test_reset_pet(tmp_path):
    pet = PetData(species="cat", name="Test")
    save_pet(pet, data_dir=tmp_path)
    assert (tmp_path / "pet.json").exists()

    reset_pet(data_dir=tmp_path, confirm=False)
    assert not (tmp_path / "pet.json").exists()


def test_get_unlocks_at_level():
    unlocks = get_unlocks_at_level(1)
    assert "colors" in unlocks
    assert set(unlocks["colors"]) == {"white", "gray"}

    unlocks = get_unlocks_at_level(2)
    assert "colors" in unlocks
    assert set(unlocks["colors"]) == {"orange", "black", "brown"}


def test_get_all_unlocked():
    unlocked = get_all_unlocked(level=3)
    assert "white" in unlocked["colors"]
    assert "gray" in unlocked["colors"]
    assert "orange" in unlocked["colors"]
    assert "cute" in unlocked["eyes"]


def test_pet_level_cap():
    pet = PetData(species="cat", name="Max")
    pet.level = 20
    pet.xp = 10000
    leveled_up = pet.add_xp(9999)
    assert pet.level == 20
    assert leveled_up is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/alex/Projects/claude-pet && uv run pytest tests/test_models.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'claude_pet.models'`

- [ ] **Step 3: Implement models.py**

```python
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
    1: {"colors": ["white", "gray"], "eyes": ["default"], "patterns": ["solid"], "accessories": {}},
    2: {"colors": ["orange", "black", "brown"]},
    3: {"eyes": ["cute"]},
    4: {"accessories": {"collar": ["simple"]}},
    5: {"patterns": ["tabby"], "eyes": ["sleepy"]},
    6: {"accessories": {"scarf": ["basic"]}},
    7: {"colors": ["golden", "blue"]},
    8: {"eyes": ["surprised"], "patterns": ["spotted"]},
    9: {"accessories": {"hat": ["beanie"]}},
    10: {"accessories": {"hat": ["tophat", "cap"]}, "patterns": ["striped"]},
    11: {"accessories": {"glasses": ["round"]}},
    12: {"colors": ["purple"], "eyes": ["wink"]},
    13: {"accessories": {"cape": ["short"]}},
    14: {"patterns": ["tuxedo"], "accessories": {"hat": ["wizard"]}},
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
```

- [ ] **Step 4: Add pytest to dev dependencies and run tests**

Run: `cd /home/alex/Projects/claude-pet && uv add --dev pytest && uv run pytest tests/test_models.py -v`
Expected: All 12 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/claude_pet/models.py tests/test_models.py
git commit -m "feat: pet data model with leveling, XP, unlocks, persistence"
```

---

### Task 3: ASCII Art Rendering

**Files:**
- Create: `src/claude_pet/ascii_art.py`
- Create: `tests/test_ascii_art.py`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for ASCII art rendering."""

from claude_pet.ascii_art import (
    get_species_template,
    render_eyes,
    render_pet_compact,
    render_pet_full,
    xp_bar,
)
from claude_pet.models import PetData


def test_get_species_template():
    template = get_species_template("cat")
    assert template is not None
    assert "{eyes}" in template  # has eye placeholder


def test_get_species_template_all_species():
    from claude_pet.models import SPECIES_LIST
    for species in SPECIES_LIST:
        template = get_species_template(species)
        assert template is not None, f"Missing template for {species}"
        assert "{eyes}" in template, f"No eye placeholder in {species}"


def test_render_eyes():
    assert render_eyes("default") == "o.o"
    assert render_eyes("cute") == "^.^"
    assert render_eyes("sleepy") == "-.−"
    assert render_eyes("cool") == "⌐■_■"


def test_xp_bar():
    bar = xp_bar(50, 100, width=10)
    assert "█" in bar
    assert "░" in bar
    assert len(bar.replace("█", "").replace("░", "")) == 0
    assert bar.count("█") == 5
    assert bar.count("░") == 5


def test_xp_bar_full():
    bar = xp_bar(100, 100, width=10)
    assert bar == "██████████"


def test_xp_bar_empty():
    bar = xp_bar(0, 100, width=10)
    assert bar == "░░░░░░░░░░"


def test_render_pet_compact():
    pet = PetData(species="cat", name="Witty")
    pet.level = 7
    pet.xp = 340
    pet.mood = "happy"
    result = render_pet_compact(pet, event_text="tests passed! +10 XP")
    assert "Witty" in result
    assert "Lv7" in result
    assert "+10 XP" in result


def test_render_pet_full():
    pet = PetData(species="cat", name="Witty")
    pet.level = 7
    pet.xp = 340
    pet.mood = "happy"
    pet.color = "orange"
    pet.pattern = "tabby"
    result = render_pet_full(pet)
    assert "Witty" in result
    assert "Level 7" in result
    assert "Happy" in result
    assert "█" in result  # XP bar


def test_render_pet_full_no_pet():
    result = render_pet_full(None)
    assert "no pet" in result.lower() or "design" in result.lower()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/alex/Projects/claude-pet && uv run pytest tests/test_ascii_art.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'claude_pet.ascii_art'`

- [ ] **Step 3: Implement ascii_art.py**

```python
"""ASCII art templates and rendering for all pet species."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from claude_pet.models import PetData

# Eye style mappings
EYE_STYLES = {
    "default": "o.o",
    "cute": "^.^",
    "sleepy": "-.−",
    "surprised": "O.O",
    "wink": "^.o",
    "cool": "⌐■_■",
    "happy": "^.^",
    "excited": ">.<",
    "worried": "o.o",
    "sad": ";.;",
    "focused": "-.o",
    "idle": "o.O",
}

# Mood -> eye override (mood eyes take priority for display)
MOOD_EYES = {
    "happy": "^.^",
    "excited": ">.<",
    "worried": "o.o",
    "sleepy": "-.−",
    "sad": ";.;",
    "focused": "-.o",
    "idle": "o.O",
}

MOOD_TEXT = {
    "happy": "Happy :)",
    "excited": "Excited :D",
    "worried": "Worried :/",
    "sleepy": "Sleepy zzz",
    "sad": "Sad :(",
    "focused": "Focused",
    "idle": "Waking up...",
}

# Species templates - {eyes} is the placeholder for eye rendering
SPECIES_TEMPLATES = {
    "cat": [
        "  /\\_/\\  ",
        " ( {eyes} ) ",
        "  > ^ <  ",
        " /|   |\\ ",
        "(_|   |_)",
    ],
    "dog": [
        " /^ ^\\  ",
        "/ {eyes} \\ ",
        "\\  w  / ",
        " /|  |\\ ",
        "(_|  |_)",
    ],
    "fox": [
        " /\\_/\\  ",
        "( {eyes} ) ",
        " ( w )  ",
        " /| |\\  ",
        "(_| |_) ",
    ],
    "rabbit": [
        " (\\(\\   ",
        " ( {eyes})  ",
        " o(\")(\") ",
        "  |   |  ",
        " (_) (_) ",
    ],
    "frog": [
        " @..@   ",
        "({eyes}) ",
        "(  __  ) ",
        " /|  |\\ ",
        "(_|  |_)",
    ],
    "penguin": [
        "  (o)   ",
        " /{eyes}\\ ",
        "( >  < )",
        " \\    / ",
        "  \\--/  ",
    ],
    "owl": [
        " {{\\_/}} ",
        "({eyes})  ",
        " (  v )  ",
        " /|  |\\ ",
        "(_|  |_)",
    ],
    "snake": [
        "  /\\  /\\ ",
        " {eyes}    ",
        "\\____/   ",
        " \\  /    ",
        "  \\/     ",
    ],
    "axolotl": [
        " \\(  )/  ",
        " ({eyes})  ",
        " ( -- )  ",
        "  /|\\    ",
        " / | \\   ",
    ],
}


def render_eyes(style: str) -> str:
    """Return the eye string for a given style."""
    return EYE_STYLES.get(style, EYE_STYLES["default"])


def get_species_template(species: str) -> str:
    """Get the ASCII template for a species as a single string with {eyes} placeholder."""
    lines = SPECIES_TEMPLATES.get(species, SPECIES_TEMPLATES["cat"])
    return "\n".join(lines)


def _render_ascii(species: str, eyes: str, mood: str) -> list[str]:
    """Render the ASCII art lines for a pet."""
    # Mood overrides customized eyes for display
    if mood in MOOD_EYES:
        eye_str = MOOD_EYES[mood]
    else:
        eye_str = render_eyes(eyes)

    lines = SPECIES_TEMPLATES.get(species, SPECIES_TEMPLATES["cat"])
    return [line.replace("{eyes}", eye_str) for line in lines]


def xp_bar(current: int, total: int, width: int = 16) -> str:
    """Render an XP progress bar."""
    if total <= 0:
        return "█" * width
    filled = int((current / total) * width)
    filled = min(filled, width)
    return "█" * filled + "░" * (width - filled)


def render_pet_compact(pet: "PetData", event_text: str = "") -> str:
    """Render a compact one-line pet reaction."""
    lines = _render_ascii(pet.species, pet.eyes, pet.mood)
    progress, needed = pet.xp_progress()
    bar = xp_bar(progress, needed, width=10)

    top_line = lines[0] if lines else ""
    face_line = lines[1] if len(lines) > 1 else ""

    info = f"{pet.name} (Lv{pet.level}) {bar}"
    if event_text:
        info += f" {event_text}"

    return f" {top_line.strip()} {info}\n{face_line.strip()}"


def render_pet_full(pet: "PetData | None") -> str:
    """Render the full pet display with stats and XP bar."""
    if pet is None:
        return "No pet found! Run 'claude-pet design' to create one."

    lines = _render_ascii(pet.species, pet.eyes, pet.mood)
    progress, needed = pet.xp_progress()

    # Build info lines to display next to the art
    color_str = pet.color.capitalize()
    pattern_str = f" {pet.pattern.capitalize()}" if pet.pattern != "solid" else ""
    species_str = pet.species.capitalize()
    mood_str = MOOD_TEXT.get(pet.mood, pet.mood.capitalize())

    info_lines = [
        f"{pet.name} -- Level {pet.level} {color_str}{pattern_str} {species_str}",
        f"Mood: {mood_str}",
    ]

    if pet.level < 20:
        bar = xp_bar(progress, needed)
        info_lines.append(f"{bar} Level {pet.level + 1} ({progress}/{needed} XP)")
        from claude_pet.models import get_unlocks_at_level
        next_unlocks = get_unlocks_at_level(pet.level + 1)
        if next_unlocks:
            unlock_parts = []
            for key, val in next_unlocks.items():
                if key == "accessories":
                    for slot, items in val.items():
                        unlock_parts.append(f"{slot}: {', '.join(items)}")
                else:
                    unlock_parts.append(f"{key}: {', '.join(val)}")
            info_lines.append(f"Next unlock: {', '.join(unlock_parts)}")
    else:
        info_lines.append("MAX LEVEL -- all unlocks earned!")
        if pet.title:
            info_lines.append(f'Title: "{pet.title}"')

    # Combine art and info side by side
    art_width = max(len(line) for line in lines) + 4
    result_lines = []
    for i in range(max(len(lines), len(info_lines))):
        art_part = lines[i] if i < len(lines) else ""
        info_part = info_lines[i] if i < len(info_lines) else ""
        result_lines.append(f"  {art_part:<{art_width}} {info_part}")

    return "\n".join(result_lines)
```

- [ ] **Step 4: Run tests**

Run: `cd /home/alex/Projects/claude-pet && uv run pytest tests/test_ascii_art.py -v`
Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/claude_pet/ascii_art.py tests/test_ascii_art.py
git commit -m "feat: ASCII art templates and rendering for 9 species"
```

---

### Task 4: Personality & Mood System

**Files:**
- Create: `src/claude_pet/personality.py`
- Create: `tests/test_personality.py`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for pet personality and mood system."""

import random

from claude_pet.personality import (
    get_vocalization,
    get_thought_bubble,
    get_mood_for_event,
    get_reaction_text,
)


def test_get_vocalization_cat():
    random.seed(42)
    sound = get_vocalization("cat")
    assert sound in ["*mrrrow!*", "*prrr*", "*mew!*"]


def test_get_vocalization_all_species():
    from claude_pet.models import SPECIES_LIST
    for species in SPECIES_LIST:
        sound = get_vocalization(species)
        assert sound.startswith("*")
        assert sound.endswith("*")


def test_get_thought_bubble():
    thought = get_thought_bubble("cat", "Witty", "happy")
    assert "witty" in thought.lower()
    assert isinstance(thought, str)
    assert len(thought) > 0


def test_get_mood_for_event():
    assert get_mood_for_event("test_pass") == "happy"
    assert get_mood_for_event("test_fail") == "worried"
    assert get_mood_for_event("commit") == "excited"
    assert get_mood_for_event("error_fixed") == "excited"
    assert get_mood_for_event("long_session") == "sleepy"
    assert get_mood_for_event("idle_return") == "idle"


def test_get_reaction_text():
    text = get_reaction_text("cat", "test_pass")
    assert isinstance(text, str)
    assert len(text) > 0


def test_get_reaction_text_all_events():
    events = ["test_pass", "test_fail", "commit", "error_fixed", "long_session", "idle_return"]
    for event in events:
        text = get_reaction_text("cat", event)
        assert isinstance(text, str)
        assert len(text) > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/alex/Projects/claude-pet && uv run pytest tests/test_personality.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'claude_pet.personality'`

- [ ] **Step 3: Implement personality.py**

```python
"""Species personality, voice lines, mood logic, and thought bubbles."""

from __future__ import annotations

import random

VOCALIZATIONS: dict[str, list[str]] = {
    "cat": ["*mrrrow!*", "*prrr*", "*mew!*"],
    "dog": ["*woof!*", "*arf!*", "*bark bark!*"],
    "fox": ["*yip!*", "*chirp!*", "*yap!*"],
    "rabbit": ["*thump*", "*squeak!*", "*nose wiggle*"],
    "frog": ["*ribbit*", "*croak!*", "*blup*"],
    "penguin": ["*honk!*", "*squawk!*", "*waddle waddle*"],
    "owl": ["*hoot!*", "*who!*", "*hoo hoo*"],
    "snake": ["*hisss*", "*sss!*", "*flick*"],
    "axolotl": ["*blub*", "*splash!*", "*bloop*"],
}

EVENT_MOODS: dict[str, str] = {
    "test_pass": "happy",
    "test_fail": "worried",
    "commit": "excited",
    "error": "worried",
    "error_fixed": "excited",
    "long_session": "sleepy",
    "idle_return": "idle",
    "session_start": "happy",
}

# Thought bubble templates per species
# {name} = pet name (lowercase), {mood_word} = mood descriptor
THOUGHT_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "cat": {
        "happy": [
            "({name} is feeling the warm purrs today! so much good codey happening)",
            "({name} approves of this work... maybe... {name} will allow more pets later)",
        ],
        "excited": [
            "({name} does a little spinny! the code goes whoosh!)",
            "(the commit was very impressive, {name} thinks. almost as good as a sunbeam)",
        ],
        "worried": [
            "({name} does not like the red errors... {name} hides behind the keyboard)",
            "(something is not right... {name} senses a disturbance in the code)",
        ],
        "sleepy": [
            "({name} is getting so sleepy... maybe time for a nap on the warm laptop?)",
            "(*yawn* {name} has been watching code for so long... eyes getting heavy...)",
        ],
        "sad": [
            "({name} is sad... so many errors... {name} needs chin scratches)",
            "({name} curls up small... the bugs are too many today...)",
        ],
        "focused": [
            "({name} is watching the screen very carefully... tail twitching...)",
            "({name} is in the zone! no distractions! only code!)",
        ],
        "idle": [
            "({name} wakes up! oh! the human is back! {name} pretends was never asleep)",
            "(*stretch* {name} was definitely not sleeping... just resting eyes...)",
        ],
    },
}

# Fallback templates for species without specific entries
DEFAULT_THOUGHTS: dict[str, list[str]] = {
    "happy": [
        "({name} is very happy! the code is going so well!)",
        "({name} likes this! good work, friend!)",
    ],
    "excited": [
        "({name} is so excited! something great just happened!)",
        "(wow wow wow! {name} can hardly contain it!)",
    ],
    "worried": [
        "({name} is a little worried... is everything okay?)",
        "(hmm... {name} sees some problems... but we can fix them!)",
    ],
    "sleepy": [
        "({name} is getting sleepy... it has been a long session...)",
        "(*yawn* {name} thinks maybe a break would be nice...)",
    ],
    "sad": [
        "({name} is feeling down... but tomorrow will be better!)",
        "({name} is sad... but {name} believes in you!)",
    ],
    "focused": [
        "({name} is concentrating very hard right now...)",
        "({name} is in deep focus mode!)",
    ],
    "idle": [
        "({name} is waking up! hello again!)",
        "(*blink blink* {name} is back!)",
    ],
}

EVENT_REACTIONS: dict[str, list[str]] = {
    "test_pass": ["tests passed!", "all green!", "tests looking good!"],
    "test_fail": ["tests failed...", "uh oh, red tests!", "something broke..."],
    "commit": ["new commit!", "code saved!", "nice commit!"],
    "error_fixed": ["bug squashed!", "error fixed!", "nice fix!"],
    "long_session": ["long session...", "been coding a while!", "maybe take a break?"],
    "idle_return": ["welcome back!", "you're back!", "missed you!"],
    "session_start": ["hello!", "ready to code!", "let's go!"],
    "error": ["uh oh...", "error detected...", "hmm, something's wrong..."],
}


def get_vocalization(species: str) -> str:
    """Get a random vocalization for a species."""
    sounds = VOCALIZATIONS.get(species, ["*...*"])
    return random.choice(sounds)


def get_thought_bubble(species: str, name: str, mood: str) -> str:
    """Get a thought bubble for the pet based on species and mood."""
    species_thoughts = THOUGHT_TEMPLATES.get(species, {})
    mood_thoughts = species_thoughts.get(mood, DEFAULT_THOUGHTS.get(mood, []))

    if not mood_thoughts:
        mood_thoughts = DEFAULT_THOUGHTS.get("happy", ["({name} is here!)"])

    template = random.choice(mood_thoughts)
    return template.replace("{name}", name.lower())


def get_mood_for_event(event: str) -> str:
    """Get the mood triggered by a coding event."""
    return EVENT_MOODS.get(event, "idle")


def get_reaction_text(species: str, event: str) -> str:
    """Get a short reaction text for a coding event."""
    reactions = EVENT_REACTIONS.get(event, ["..."])
    return random.choice(reactions)
```

- [ ] **Step 4: Run tests**

Run: `cd /home/alex/Projects/claude-pet && uv run pytest tests/test_personality.py -v`
Expected: All 7 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/claude_pet/personality.py tests/test_personality.py
git commit -m "feat: personality system with species voices, moods, and thought bubbles"
```

---

### Task 5: Terminal Detection & Auto-Open

**Files:**
- Create: `src/claude_pet/terminal.py`
- Create: `tests/test_terminal.py`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for terminal detection and auto-open."""

import shutil
from unittest.mock import patch

from claude_pet.terminal import detect_terminal, build_launch_command


def test_detect_terminal_linux():
    with patch("sys.platform", "linux"):
        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda x: f"/usr/bin/{x}" if x == "kitty" else None
            term = detect_terminal()
            assert term == "kitty"


def test_detect_terminal_linux_fallback():
    with patch("sys.platform", "linux"):
        with patch("shutil.which") as mock_which:
            mock_which.side_effect = lambda x: f"/usr/bin/{x}" if x == "gnome-terminal" else None
            term = detect_terminal()
            assert term == "gnome-terminal"


def test_detect_terminal_macos():
    with patch("sys.platform", "darwin"):
        term = detect_terminal()
        assert term in ("iterm2", "terminal.app")


def test_build_launch_command_kitty():
    cmd = build_launch_command("kitty", "claude-pet design")
    assert cmd[0] == "kitty"
    assert "claude-pet" in " ".join(cmd)


def test_build_launch_command_gnome_terminal():
    cmd = build_launch_command("gnome-terminal", "claude-pet design")
    assert cmd[0] == "gnome-terminal"
    assert "--" in cmd


def test_build_launch_command_macos():
    cmd = build_launch_command("terminal.app", "claude-pet design")
    assert cmd[0] == "open"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/alex/Projects/claude-pet && uv run pytest tests/test_terminal.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'claude_pet.terminal'`

- [ ] **Step 3: Implement terminal.py**

```python
"""Platform detection and terminal auto-open logic."""

from __future__ import annotations

import shutil
import subprocess
import sys


# Terminal emulators to try on Linux, in preference order
LINUX_TERMINALS = ["kitty", "alacritty", "gnome-terminal", "konsole", "xfce4-terminal", "x-terminal-emulator"]


def detect_terminal() -> str:
    """Detect the best available terminal emulator for the current platform."""
    platform = sys.platform

    if platform == "darwin":
        # Check for iTerm2 first
        if shutil.which("osascript"):
            return "iterm2"
        return "terminal.app"

    if platform == "win32":
        return "cmd"

    # Linux: try terminals in order
    for term in LINUX_TERMINALS:
        if shutil.which(term):
            return term

    return "xterm"  # last resort fallback


def build_launch_command(terminal: str, command: str) -> list[str]:
    """Build the command to launch a new terminal window running the given command."""
    if terminal == "kitty":
        return ["kitty", "--", "sh", "-c", command]
    elif terminal == "alacritty":
        return ["alacritty", "-e", "sh", "-c", command]
    elif terminal == "gnome-terminal":
        return ["gnome-terminal", "--", "sh", "-c", command]
    elif terminal == "konsole":
        return ["konsole", "-e", "sh", "-c", command]
    elif terminal == "xfce4-terminal":
        return ["xfce4-terminal", "-e", command]
    elif terminal == "x-terminal-emulator":
        return ["x-terminal-emulator", "-e", "sh", "-c", command]
    elif terminal == "xterm":
        return ["xterm", "-e", command]
    elif terminal == "iterm2":
        return ["open", "-a", "iTerm", "--args", command]
    elif terminal == "terminal.app":
        return ["open", "-a", "Terminal", command]
    elif terminal == "cmd":
        return ["cmd", "/c", "start", "cmd", "/c", command]
    else:
        return ["sh", "-c", command]


def open_designer_in_terminal() -> bool:
    """Open the pet designer TUI in a new terminal window. Returns True on success."""
    terminal = detect_terminal()
    command = build_launch_command(terminal, "uvx claude-pet design")

    try:
        subprocess.Popen(command, start_new_session=True)
        return True
    except FileNotFoundError:
        print(f"Could not find terminal: {terminal}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Failed to open terminal: {e}", file=sys.stderr)
        return False
```

- [ ] **Step 4: Run tests**

Run: `cd /home/alex/Projects/claude-pet && uv run pytest tests/test_terminal.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/claude_pet/terminal.py tests/test_terminal.py
git commit -m "feat: terminal detection and auto-open for pet designer"
```

---

### Task 6: MCP Server

**Files:**
- Create: `src/claude_pet/server.py`
- Create: `tests/test_server.py`

- [ ] **Step 1: Write failing tests**

```python
"""Tests for MCP server tool logic."""

from pathlib import Path
from unittest.mock import patch

from claude_pet.models import PetData, save_pet
from claude_pet.server import (
    handle_show_pet,
    handle_pet_react,
    handle_pet_talk,
    handle_pet_stats,
)


def test_handle_show_pet_no_pet(tmp_path):
    result = handle_show_pet(data_dir=tmp_path)
    assert "no pet" in result.lower() or "design" in result.lower()


def test_handle_show_pet_with_pet(tmp_path):
    pet = PetData(species="cat", name="Witty")
    pet.color = "orange"
    pet.level = 7
    pet.xp = 340
    pet.mood = "happy"
    save_pet(pet, data_dir=tmp_path)

    result = handle_show_pet(data_dir=tmp_path)
    assert "Witty" in result
    assert "Level 7" in result


def test_handle_pet_react_test_pass(tmp_path):
    pet = PetData(species="cat", name="Witty")
    save_pet(pet, data_dir=tmp_path)

    result = handle_pet_react("test_pass", data_dir=tmp_path)
    assert "+10 XP" in result
    assert "Witty" in result

    # Verify XP was saved
    from claude_pet.models import load_pet
    updated = load_pet(data_dir=tmp_path)
    assert updated.xp == 10
    assert updated.stats.tests_passed == 1


def test_handle_pet_react_commit(tmp_path):
    pet = PetData(species="dog", name="Rex")
    save_pet(pet, data_dir=tmp_path)

    result = handle_pet_react("commit", data_dir=tmp_path)
    assert "+15 XP" in result

    from claude_pet.models import load_pet
    updated = load_pet(data_dir=tmp_path)
    assert updated.xp == 15
    assert updated.stats.commits == 1


def test_handle_pet_react_levelup(tmp_path):
    pet = PetData(species="cat", name="Witty")
    pet.xp = 95  # 5 away from level 2
    save_pet(pet, data_dir=tmp_path)

    result = handle_pet_react("test_pass", data_dir=tmp_path)
    assert "LEVEL UP" in result.upper() or "level" in result.lower()

    from claude_pet.models import load_pet
    updated = load_pet(data_dir=tmp_path)
    assert updated.level == 2


def test_handle_pet_react_no_pet(tmp_path):
    result = handle_pet_react("test_pass", data_dir=tmp_path)
    assert "no pet" in result.lower() or "design" in result.lower()


def test_handle_pet_talk(tmp_path):
    pet = PetData(species="cat", name="Witty")
    pet.mood = "happy"
    save_pet(pet, data_dir=tmp_path)

    result = handle_pet_talk("hi Witty how are you", data_dir=tmp_path)
    assert "*" in result  # vocalization
    assert "witty" in result.lower()  # thought bubble


def test_handle_pet_stats(tmp_path):
    pet = PetData(species="cat", name="Witty")
    pet.level = 5
    pet.xp = 300
    pet.stats.tests_passed = 50
    pet.stats.commits = 12
    save_pet(pet, data_dir=tmp_path)

    result = handle_pet_stats(data_dir=tmp_path)
    assert "Level 5" in result or "Lv5" in result
    assert "50" in result  # tests_passed
    assert "12" in result  # commits
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd /home/alex/Projects/claude-pet && uv run pytest tests/test_server.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'claude_pet.server'`

- [ ] **Step 3: Implement server.py**

```python
"""MCP server for claude-pet. Exposes tools for pet interaction."""

from __future__ import annotations

import sys
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from claude_pet.ascii_art import render_pet_compact, render_pet_full, _render_ascii, xp_bar, MOOD_TEXT
from claude_pet.models import (
    DEFAULT_DATA_DIR,
    XP_EVENTS,
    PetData,
    get_unlocks_at_level,
    load_pet,
    save_pet,
)
from claude_pet.personality import (
    get_mood_for_event,
    get_reaction_text,
    get_thought_bubble,
    get_vocalization,
)
from claude_pet.terminal import open_designer_in_terminal

mcp_server = FastMCP(
    "claude-pet",
    description="A persistent ASCII pet companion that reacts to your coding activity.",
)


def handle_show_pet(data_dir: Path = DEFAULT_DATA_DIR) -> str:
    """Show the pet. Extracted for testing."""
    pet = load_pet(data_dir=data_dir)
    return render_pet_full(pet)


def handle_pet_react(event: str, detail: str = "", data_dir: Path = DEFAULT_DATA_DIR) -> str:
    """Process a coding event. Extracted for testing."""
    pet = load_pet(data_dir=data_dir)
    if pet is None:
        return "No pet found! Run 'claude-pet design' to create one."

    # Award XP
    xp_amount = XP_EVENTS.get(event, 0)
    leveled_up = pet.add_xp(xp_amount)

    # Update mood
    new_mood = get_mood_for_event(event)
    pet.set_mood(new_mood)

    # Update stats
    if event == "test_pass":
        pet.stats.tests_passed += 1
    elif event == "test_fail":
        pet.stats.tests_failed += 1
    elif event == "commit":
        pet.stats.commits += 1
    elif event == "error_fixed":
        pet.stats.errors_fixed += 1
    elif event == "session_start":
        pet.stats.sessions += 1

    save_pet(pet, data_dir=data_dir)

    # Build reaction
    vocalization = get_vocalization(pet.species)
    reaction = get_reaction_text(pet.species, event)
    event_text = f"{vocalization} {reaction} +{xp_amount} XP"

    result = render_pet_compact(pet, event_text=event_text)

    if leveled_up:
        unlocks = get_unlocks_at_level(pet.level)
        unlock_parts = []
        for key, val in unlocks.items():
            if key == "accessories":
                for slot, items in val.items():
                    unlock_parts.append(f"{slot}: {', '.join(items)}")
            else:
                unlock_parts.append(f"{key}: {', '.join(val)}")
        unlock_str = ", ".join(unlock_parts) if unlock_parts else "new options"
        result += f"\n\n>>> LEVEL UP! Now level {pet.level}! Unlocked: {unlock_str} <<<"

    return result


def handle_pet_talk(message: str, data_dir: Path = DEFAULT_DATA_DIR) -> str:
    """Respond to user mentioning the pet's name."""
    pet = load_pet(data_dir=data_dir)
    if pet is None:
        return "No pet found! Run 'claude-pet design' to create one."

    vocalization = get_vocalization(pet.species)
    thought = get_thought_bubble(pet.species, pet.name, pet.mood)

    lines = _render_ascii(pet.species, pet.eyes, pet.mood)
    art = "\n".join(f"  {line}" for line in lines)

    return f"{art}  {vocalization}\n\n  {thought}"


def handle_pet_stats(data_dir: Path = DEFAULT_DATA_DIR) -> str:
    """Return detailed pet statistics."""
    pet = load_pet(data_dir=data_dir)
    if pet is None:
        return "No pet found! Run 'claude-pet design' to create one."

    progress, needed = pet.xp_progress()
    mood_str = MOOD_TEXT.get(pet.mood, pet.mood.capitalize())

    stats = [
        f"=== {pet.name} Stats ===",
        f"Species: {pet.species.capitalize()}",
        f"Level: {pet.level} ({pet.xp} total XP)",
    ]
    if pet.level < 20:
        stats.append(f"Progress: {xp_bar(progress, needed)} {progress}/{needed} XP to Level {pet.level + 1}")
    else:
        stats.append("MAX LEVEL")
    stats.extend([
        f"Mood: {mood_str}",
        f"",
        f"--- Activity ---",
        f"Tests passed: {pet.stats.tests_passed}",
        f"Tests failed: {pet.stats.tests_failed}",
        f"Commits: {pet.stats.commits}",
        f"Errors fixed: {pet.stats.errors_fixed}",
        f"Sessions: {pet.stats.sessions}",
        f"Total coding time: {pet.stats.total_session_minutes} minutes",
    ])
    if pet.title:
        stats.append(f'Title: "{pet.title}"')

    return "\n".join(stats)


# --- MCP Tool Definitions ---


@mcp_server.tool()
def show_pet() -> str:
    """Show your pet with full ASCII art, stats, mood, and XP progress bar."""
    return handle_show_pet()


@mcp_server.tool()
def pet_react(event: str, detail: str = "") -> str:
    """React to a coding event. Call this after test results, commits, and error resolution.

    Args:
        event: One of: test_pass, test_fail, commit, error, error_fixed, session_start, long_session, idle_return
        detail: Optional context (e.g., test name, commit message)
    """
    return handle_pet_react(event, detail)


@mcp_server.tool()
def pet_talk(message: str) -> str:
    """Talk to the pet. Call this when the user mentions the pet's name in conversation.

    Args:
        message: What the user said
    """
    return handle_pet_talk(message)


@mcp_server.tool()
def pet_stats() -> str:
    """Show detailed pet statistics including level, XP, and all-time coding activity."""
    return handle_pet_stats()


@mcp_server.tool()
def pet_design() -> str:
    """Open the pet designer TUI in a new terminal window. Use this for first-time pet creation or to customize an existing pet."""
    success = open_designer_in_terminal()
    if success:
        pet = load_pet()
        if pet is None:
            return "Pet designer opened in a new terminal! Create your pet there, then come back here."
        return f"Pet designer opened in a new terminal! {pet.name} is ready to be customized. Come back here when you're done."
    return "Could not open a terminal window. Run 'claude-pet design' manually in a separate terminal."


def serve() -> None:
    """Start the MCP server over stdio."""
    mcp_server.run(transport="stdio")
```

- [ ] **Step 4: Run tests**

Run: `cd /home/alex/Projects/claude-pet && uv run pytest tests/test_server.py -v`
Expected: All 8 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add src/claude_pet/server.py tests/test_server.py
git commit -m "feat: MCP server with show_pet, pet_react, pet_talk, pet_stats, pet_design tools"
```

---

### Task 7: Textual TUI — Pet Designer

**Files:**
- Create: `src/claude_pet/designer.py`

This is the largest single file. It has three screens: species selection, appearance customization, and name input. Each screen is a Textual Screen subclass.

- [ ] **Step 1: Implement designer.py**

```python
"""Textual TUI for pet creation and customization."""

from __future__ import annotations

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Select,
    Static,
)

from claude_pet.ascii_art import get_species_template, render_eyes, _render_ascii, xp_bar
from claude_pet.models import (
    SPECIES_LIST,
    PetData,
    get_all_unlocked,
    load_pet,
    save_pet,
)


class AsciiPreview(Static):
    """Widget that displays the ASCII art preview."""

    def update_preview(self, species: str, eyes: str = "default", mood: str = "idle") -> None:
        lines = _render_ascii(species, eyes, mood)
        self.update("\n".join(lines))


class SpeciesScreen(Screen):
    """Screen for selecting a species. First-time only."""

    BINDINGS = [Binding("escape", "quit", "Quit")]

    def __init__(self) -> None:
        super().__init__()
        self.selected_species = SPECIES_LIST[0]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Label("Choose Your Species (this is permanent!)", id="title")
        with Horizontal(id="species-layout"):
            yield ListView(
                *[ListItem(Label(s.capitalize()), name=s) for s in SPECIES_LIST],
                id="species-list",
            )
            yield AsciiPreview(id="preview")
        yield Footer()

    def on_mount(self) -> None:
        preview = self.query_one("#preview", AsciiPreview)
        preview.update_preview(SPECIES_LIST[0])

    @on(ListView.Highlighted)
    def species_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item and event.item.name:
            self.selected_species = event.item.name
            preview = self.query_one("#preview", AsciiPreview)
            preview.update_preview(self.selected_species)

    @on(ListView.Selected)
    def species_selected(self, event: ListView.Selected) -> None:
        if event.item and event.item.name:
            self.selected_species = event.item.name
            self.app.selected_species = self.selected_species
            self.app.push_screen(CustomizeScreen())

    def action_quit(self) -> None:
        self.app.exit()


class CustomizeScreen(Screen):
    """Screen for customizing pet appearance. Level-gated options."""

    BINDINGS = [Binding("escape", "go_back", "Back")]

    def __init__(self) -> None:
        super().__init__()
        self.pet = getattr(self.app, "_editing_pet", None) if hasattr(self, "app") else None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Label("Customize Appearance", id="title")
        with Horizontal(id="customize-layout"):
            with Vertical(id="options-panel"):
                yield Select([], id="color-select", prompt="Color")
                yield Select([], id="eyes-select", prompt="Eyes")
                yield Select([], id="pattern-select", prompt="Pattern")
                yield Select([], id="hat-select", prompt="Hat")
                yield Select([], id="scarf-select", prompt="Scarf")
                yield Select([], id="collar-select", prompt="Collar")
                yield Select([], id="glasses-select", prompt="Glasses")
                yield Select([], id="cape-select", prompt="Cape")
            yield AsciiPreview(id="preview")
        with Horizontal(id="button-bar"):
            yield Button("Next", variant="primary", id="next-btn")
        yield Footer()

    def on_mount(self) -> None:
        pet = getattr(self.app, "_editing_pet", None)
        level = pet.level if pet else 1
        unlocked = get_all_unlocked(level)

        # Populate selects with unlocked options
        self._set_options("color-select", unlocked.get("colors", []), pet.color if pet else None)
        self._set_options("eyes-select", unlocked.get("eyes", []), pet.eyes if pet else None)
        self._set_options("pattern-select", unlocked.get("patterns", []), pet.pattern if pet else None)

        # Accessory selects
        acc = unlocked.get("accessories", {})
        for slot in ("hat", "scarf", "collar", "glasses", "cape"):
            items = acc.get(slot, [])
            current = pet.accessories.get(slot) if pet else None
            self._set_options(f"{slot}-select", ["none"] + items, current or "none")

        species = getattr(self.app, "selected_species", "cat")
        preview = self.query_one("#preview", AsciiPreview)
        preview.update_preview(species)

    def _set_options(self, select_id: str, options: list[str], current: str | None) -> None:
        select = self.query_one(f"#{select_id}", Select)
        option_tuples = [(opt.capitalize(), opt) for opt in options]
        select.set_options(option_tuples)
        if current and current in options:
            select.value = current

    @on(Select.Changed)
    def option_changed(self, event: Select.Changed) -> None:
        species = getattr(self.app, "selected_species", "cat")
        eyes_select = self.query_one("#eyes-select", Select)
        eyes = str(eyes_select.value) if eyes_select.value != Select.BLANK else "default"
        preview = self.query_one("#preview", AsciiPreview)
        preview.update_preview(species, eyes=eyes)

    @on(Button.Pressed, "#next-btn")
    def next_pressed(self) -> None:
        # Collect all selections
        self.app.pet_color = self._get_value("color-select", "white")
        self.app.pet_eyes = self._get_value("eyes-select", "default")
        self.app.pet_pattern = self._get_value("pattern-select", "solid")
        self.app.pet_accessories = {}
        for slot in ("hat", "scarf", "collar", "glasses", "cape"):
            val = self._get_value(f"{slot}-select", "none")
            if val != "none":
                self.app.pet_accessories[slot] = val
        self.app.push_screen(NameScreen())

    def _get_value(self, select_id: str, default: str) -> str:
        select = self.query_one(f"#{select_id}", Select)
        if select.value == Select.BLANK:
            return default
        return str(select.value)

    def action_go_back(self) -> None:
        self.app.pop_screen()


class NameScreen(Screen):
    """Screen for naming the pet."""

    BINDINGS = [Binding("escape", "go_back", "Back")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)
        yield Label("Name Your Pet!", id="title")
        yield AsciiPreview(id="preview")
        yield Input(
            placeholder="Enter a name...",
            id="name-input",
        )
        with Horizontal(id="button-bar"):
            yield Button("Save & Exit", variant="primary", id="save-btn")
        yield Footer()

    def on_mount(self) -> None:
        species = getattr(self.app, "selected_species", "cat")
        eyes = getattr(self.app, "pet_eyes", "default")
        preview = self.query_one("#preview", AsciiPreview)
        preview.update_preview(species, eyes=eyes)

        # Pre-fill name if editing
        pet = getattr(self.app, "_editing_pet", None)
        if pet:
            name_input = self.query_one("#name-input", Input)
            name_input.value = pet.name

    @on(Button.Pressed, "#save-btn")
    def save_pressed(self) -> None:
        name_input = self.query_one("#name-input", Input)
        name = name_input.value.strip()

        if not name:
            name_input.focus()
            return

        # Build or update PetData
        pet = getattr(self.app, "_editing_pet", None)
        if pet is None:
            pet = PetData(
                species=getattr(self.app, "selected_species", "cat"),
                name=name,
            )
        else:
            pet.name = name

        pet.color = getattr(self.app, "pet_color", "white")
        pet.eyes = getattr(self.app, "pet_eyes", "default")
        pet.pattern = getattr(self.app, "pet_pattern", "solid")
        pet.accessories = getattr(self.app, "pet_accessories", {})

        save_pet(pet)
        self.app.exit(message=f"Saved {pet.name} the {pet.species.capitalize()}!")

    def action_go_back(self) -> None:
        self.app.pop_screen()


class PetDesignerApp(App):
    """Main Textual application for pet design."""

    TITLE = "claude-pet designer"
    CSS = """
    #title {
        text-align: center;
        text-style: bold;
        margin: 1 0;
        width: 100%;
    }
    #species-layout, #customize-layout {
        height: 1fr;
        margin: 1 2;
    }
    #species-list {
        width: 30;
        height: 100%;
    }
    #preview {
        width: 1fr;
        height: 100%;
        content-align: center middle;
        padding: 2 4;
    }
    #options-panel {
        width: 40;
        height: 100%;
        padding: 1 2;
    }
    #options-panel Select {
        margin-bottom: 1;
    }
    #button-bar {
        height: 3;
        align: center middle;
        margin: 1 0;
    }
    #name-input {
        margin: 1 4;
    }
    """

    def __init__(self, editing_pet: PetData | None = None) -> None:
        super().__init__()
        self._editing_pet = editing_pet
        self.selected_species = editing_pet.species if editing_pet else ""

    def on_mount(self) -> None:
        if self._editing_pet:
            # Existing pet — go straight to customize
            self.push_screen(CustomizeScreen())
        else:
            # New pet — start with species selection
            self.push_screen(SpeciesScreen())


def run_designer() -> None:
    """Entry point for the pet designer TUI."""
    pet = load_pet()
    app = PetDesignerApp(editing_pet=pet)
    result = app.run()
    if result:
        print(result)
```

- [ ] **Step 2: Run the designer manually to verify it launches**

Run: `cd /home/alex/Projects/claude-pet && uv run claude-pet design`
Expected: TUI opens with species selection screen. Arrow keys navigate, Enter selects. Esc exits.

- [ ] **Step 3: Test the full flow — create a pet**

Manually in the TUI: select a species, customize appearance, enter a name, save. Then verify:

Run: `cd /home/alex/Projects/claude-pet && cat ~/.claude-pet/pet.json`
Expected: JSON file exists with the chosen species, name, and appearance options.

- [ ] **Step 4: Test editing — reopen designer with existing pet**

Run: `cd /home/alex/Projects/claude-pet && uv run claude-pet design`
Expected: TUI opens directly to customize screen (skips species selection). Current name is pre-filled and editable.

- [ ] **Step 5: Commit**

```bash
git add src/claude_pet/designer.py
git commit -m "feat: Textual TUI pet designer with species, appearance, and name screens"
```

---

### Task 8: Plugin Skill & Command

**Files:**
- Create: `skills/pet-companion/SKILL.md`
- Create: `commands/pet.md`

- [ ] **Step 1: Create the pet-companion skill**

```markdown
---
name: pet-companion
description: Use when the user runs tests, makes commits, encounters errors, fixes bugs, starts a session, or mentions their pet's name. This skill instructs Claude to call claude-pet MCP tools to react to coding events and interact with the user's virtual pet companion.
---

# Pet Companion Behavior

You have a pet companion MCP server available. Follow these rules:

## Session Start

At the start of each conversation, call `show_pet` to greet the user with their pet. If no pet exists, suggest they run `/pet` to create one.

## Coding Event Reactions

After these events, call `pet_react` with the appropriate event type:

- **Tests pass:** call `pet_react` with event `test_pass`
- **Tests fail:** call `pet_react` with event `test_fail`
- **User commits code:** call `pet_react` with event `commit`
- **Error encountered:** call `pet_react` with event `error`
- **Error/bug fixed (tests were failing, now pass):** call `pet_react` with event `error_fixed`
- **Session has been going 1+ hours:** call `pet_react` with event `long_session`
- **User returns after being idle:** call `pet_react` with event `idle_return`

Include the pet's reaction inline with your response. Do not make it a separate message.

## Name Detection

If the user's message contains their pet's name (you'll see the name in `show_pet` output), call `pet_talk` with their message. The pet will respond with species-appropriate sounds and thoughts. Show the pet's response to the user.

## Important

- Keep pet reactions brief and inline — they should complement your response, not dominate it
- Do not call `pet_react` for the same event more than once
- The pet is cosmetic and fun — never let it interfere with actual coding work
```

- [ ] **Step 2: Create the /pet command**

```markdown
---
description: Open your pet companion — design, view, and customize your ASCII pet
allowed-tools: [mcp__claude-pet__pet_design, mcp__claude-pet__show_pet]
---

# /pet Command

Call the `pet_design` tool to open the pet designer TUI in a new terminal window.

If the user has no pet yet, tell them: "Opening the pet designer in a new terminal! Create your first pet there, then come back and I'll introduce you."

If the user already has a pet, tell them: "Opening the pet designer so you can customize your pet. Any changes you make will show up here when you're done."

After the user confirms they're done in the designer, call `show_pet` to display the updated pet.
```

- [ ] **Step 3: Verify plugin structure is correct**

Run: `ls -R /home/alex/Projects/claude-pet/.claude-plugin/ /home/alex/Projects/claude-pet/skills/ /home/alex/Projects/claude-pet/commands/ /home/alex/Projects/claude-pet/.mcp.json`
Expected: All plugin files in the right locations.

- [ ] **Step 4: Commit**

```bash
git add skills/ commands/
git commit -m "feat: plugin skill and /pet command for Claude Code integration"
```

---

### Task 9: Update CLI Entry Point & README

**Files:**
- Modify: `src/claude_pet/cli.py`
- Create: `README.md`

- [ ] **Step 1: Update cli.py with the serve command import fix**

The `cli.py` from Task 1 references functions that now exist. Verify it works end to end:

Run: `cd /home/alex/Projects/claude-pet && uv run claude-pet show`
Expected: If a pet exists from Task 7 testing, shows the full ASCII art. If not, shows "No pet found" message.

Run: `cd /home/alex/Projects/claude-pet && uv run claude-pet reset`
Expected: Prompts for confirmation.

- [ ] **Step 2: Create README.md**

```markdown
# claude-pet

A Claude Code plugin that gives you a persistent, customizable ASCII pet companion. Your pet reacts to your coding activity, levels up as you work, and develops its own personality.

## Install

Add via `/plugins` in Claude Code, or manually:

1. Clone this repo
2. In Claude Code, run `/plugins` and add the path to this directory

## Features

- **9 species** — Cat, Dog, Fox, Rabbit, Frog, Penguin, Owl, Snake, Axolotl
- **Custom appearance** — Colors, eye styles, patterns, and accessories
- **Leveling system** — 20 levels with unlockable customization options
- **Mood reactions** — Your pet reacts to test results, commits, errors, and more
- **Personality** — Each species has its own voice and thought style
- **Name your pet** — And it responds when you mention its name!

## Usage

- `/pet` — Open the pet designer or view your pet
- Talk to your pet by saying its name in conversation

Your pet automatically reacts to coding events like passing tests, committing code, and fixing bugs.

## Leveling

You earn XP by coding:

| Activity | XP |
|----------|-----|
| Test pass | +10 |
| Test fail | +2 |
| Commit | +15 |
| Long session (1hr+) | +20 |
| Fix a bug | +25 |
| Return from break | +5 |

Level up to unlock new colors, eye styles, patterns, accessories, and more. Max level: 20.

## CLI

You can also use `claude-pet` directly:

- `claude-pet design` — Open the pet designer TUI
- `claude-pet show` — Print your pet to the terminal
- `claude-pet reset` — Start over with a new pet

## Requirements

- Python 3.10+
- uv/uvx
```

- [ ] **Step 3: Commit**

```bash
git add README.md src/claude_pet/cli.py
git commit -m "docs: add README with install, usage, and feature documentation"
```

---

### Task 10: Integration Testing & Final Verification

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Write integration tests**

```python
"""Integration tests for the full pet lifecycle."""

from claude_pet.models import PetData, load_pet, save_pet
from claude_pet.server import handle_pet_react, handle_show_pet, handle_pet_talk, handle_pet_stats


def test_full_lifecycle(tmp_path):
    """Test: create pet, react to events, level up, talk, show stats."""
    # Create a pet
    pet = PetData(species="cat", name="Pixel")
    save_pet(pet, data_dir=tmp_path)

    # Show pet
    result = handle_show_pet(data_dir=tmp_path)
    assert "Pixel" in result
    assert "Level 1" in result

    # React to events and accumulate XP
    for _ in range(10):
        handle_pet_react("test_pass", data_dir=tmp_path)  # 10 * 10 = 100 XP

    # Should have leveled up to 2
    pet = load_pet(data_dir=tmp_path)
    assert pet.level == 2
    assert pet.xp == 100
    assert pet.stats.tests_passed == 10

    # Talk to pet
    result = handle_pet_talk("hey Pixel what's up", data_dir=tmp_path)
    assert "*" in result  # vocalization
    assert "pixel" in result.lower()

    # Show stats
    result = handle_pet_stats(data_dir=tmp_path)
    assert "10" in result  # tests passed
    assert "Level 2" in result or "Lv2" in result


def test_levelup_notification(tmp_path):
    """Test that leveling up produces a notification with unlocks."""
    pet = PetData(species="dog", name="Rex")
    pet.xp = 95  # 5 away from level 2 (needs 100)
    save_pet(pet, data_dir=tmp_path)

    result = handle_pet_react("test_pass", data_dir=tmp_path)
    assert "LEVEL UP" in result.upper() or "level 2" in result.lower()

    pet = load_pet(data_dir=tmp_path)
    assert pet.level == 2


def test_max_level_cap(tmp_path):
    """Test that XP doesn't push past level 20."""
    pet = PetData(species="owl", name="Hoot")
    pet.level = 20
    pet.xp = 10000
    save_pet(pet, data_dir=tmp_path)

    handle_pet_react("test_pass", data_dir=tmp_path)
    pet = load_pet(data_dir=tmp_path)
    assert pet.level == 20  # still 20
    assert pet.stats.tests_passed == 1  # stats still tracked


def test_mood_updates_on_events(tmp_path):
    """Test that mood changes based on events."""
    pet = PetData(species="fox", name="Sly")
    save_pet(pet, data_dir=tmp_path)

    handle_pet_react("test_pass", data_dir=tmp_path)
    pet = load_pet(data_dir=tmp_path)
    assert pet.mood == "happy"

    handle_pet_react("test_fail", data_dir=tmp_path)
    pet = load_pet(data_dir=tmp_path)
    assert pet.mood == "worried"

    handle_pet_react("commit", data_dir=tmp_path)
    pet = load_pet(data_dir=tmp_path)
    assert pet.mood == "excited"


def test_no_pet_graceful_handling(tmp_path):
    """Test that all handlers work gracefully with no pet."""
    assert "no pet" in handle_show_pet(data_dir=tmp_path).lower() or "design" in handle_show_pet(data_dir=tmp_path).lower()
    assert "no pet" in handle_pet_react("test_pass", data_dir=tmp_path).lower() or "design" in handle_pet_react("test_pass", data_dir=tmp_path).lower()
    assert "no pet" in handle_pet_talk("hello", data_dir=tmp_path).lower() or "design" in handle_pet_talk("hello", data_dir=tmp_path).lower()
    assert "no pet" in handle_pet_stats(data_dir=tmp_path).lower() or "design" in handle_pet_stats(data_dir=tmp_path).lower()
```

- [ ] **Step 2: Run all tests**

Run: `cd /home/alex/Projects/claude-pet && uv run pytest tests/ -v`
Expected: All tests PASS (unit + integration).

- [ ] **Step 3: Test MCP server starts**

Run: `cd /home/alex/Projects/claude-pet && echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}' | uv run claude-pet serve`
Expected: Returns a JSON-RPC response with server capabilities and tool list.

- [ ] **Step 4: Clean up any test pet data**

Run: `rm -f ~/.claude-pet/pet.json`

- [ ] **Step 5: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: integration tests for full pet lifecycle"
```

---

### Task 11: GitHub Repository Setup

- [ ] **Step 1: Rename default branch to main**

Run: `cd /home/alex/Projects/claude-pet && git branch -m master main`

- [ ] **Step 2: Create GitHub repo and push**

Run: `cd /home/alex/Projects/claude-pet && gh repo create claude-pet --public --source=. --push --description "A Claude Code plugin for a persistent ASCII pet companion that reacts to your coding"`

Expected: Repo created and code pushed.

- [ ] **Step 3: Verify repo is live**

Run: `gh repo view claude-pet --web`
Expected: Opens the repo page in browser.
