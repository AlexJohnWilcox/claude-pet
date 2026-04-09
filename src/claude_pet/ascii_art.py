"""ASCII art templates and rendering for all pet species."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from claude_pet.models import PetData

EYE_STYLES = {
    "default": "o.o",
    "cute": "^.^",
    "sleepy": "-.~",
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

MOOD_EYES = {
    "happy": "^.^",
    "excited": ">.<",
    "worried": "o.o",
    "sleepy": "-.~",
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

SPECIES_TEMPLATES = {
    "cat": [
        " /\\_/\\ ",
        "( {eyes} )",
        " > ^ < ",
        " /| |\\",
        "(_| |_)",
    ],
    "dog": [
        "  /\\  /\\",
        " (  {eyes} )",
        "  (  w  )",
        "  /|  |\\",
        " (_|  |_)",
    ],
    "fox": [
        " /\\_/\\",
        "( {eyes} )",
        " (  w )",
        "  || ||",
        "  LL LL",
    ],
    "rabbit": [
        "  (\\ /)",
        "  ( {eyes})",
        "  c(\")\")",
        "   | | ",
        "   d b ",
    ],
    "frog": [
        "  @..@ ",
        " ({eyes})",
        "(  __  )",
        " |    | ",
        " d    b ",
    ],
    "penguin": [
        "   __  ",
        "  ({eyes}) ",
        " /|  |\\",
        "(_|  |_)",
        "  d  b ",
    ],
    "owl": [
        " /{\\_/}\\",
        "( {eyes} )",
        " ( <> ) ",
        "  /||\\  ",
        " (_/\\_) ",
    ],
    "snake": [
        "    __    ",
        "  /  {eyes} \\",
        " |      | ",
        "  \\~~~~/ ",
        "   ~~~~  ",
    ],
    "axolotl": [
        " \\( . )/",
        "  ({eyes}) ",
        "  ( -- ) ",
        "  /| |\\",
        " d |_| b",
    ],
}


def render_eyes(style: str) -> str:
    return EYE_STYLES.get(style, EYE_STYLES["default"])


def get_species_template(species: str) -> str:
    lines = SPECIES_TEMPLATES.get(species, SPECIES_TEMPLATES["cat"])
    return "\n".join(lines)


def _render_ascii(species: str, eyes: str, mood: str) -> list[str]:
    if mood in MOOD_EYES:
        eye_str = MOOD_EYES[mood]
    else:
        eye_str = render_eyes(eyes)
    lines = SPECIES_TEMPLATES.get(species, SPECIES_TEMPLATES["cat"])
    return [line.replace("{eyes}", eye_str) for line in lines]


def xp_bar(current: int, total: int, width: int = 16) -> str:
    if total <= 0:
        return "█" * width
    current = max(0, current)
    filled = int((current / total) * width)
    filled = min(filled, width)
    return "█" * filled + "░" * (width - filled)


def render_pet_compact(pet: "PetData", event_text: str = "") -> str:
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
    if pet is None:
        return "No pet found! Run 'claude-pet design' to create one."
    lines = _render_ascii(pet.species, pet.eyes, pet.mood)
    progress, needed = pet.xp_progress()
    color_str = pet.color.capitalize()
    pattern_str = f" {pet.pattern.capitalize()}" if pet.pattern != "solid" else ""
    species_str = pet.species.capitalize()
    mood_str = MOOD_TEXT.get(pet.mood, pet.mood.capitalize())
    info_lines = [
        f"{pet.name} -- Level {pet.level} {color_str}{pattern_str} {species_str}",
        f"Mood: {mood_str}",
    ]
    if pet.level < 20:
        if progress < 0:
            # pet data set directly (not via add_xp); use raw xp mod level step
            from claude_pet.models import xp_for_level
            step = xp_for_level(pet.level + 1)
            display_progress = pet.xp % step if step > 0 else 0
            display_needed = step
        else:
            display_progress = progress
            display_needed = needed
        bar = xp_bar(display_progress, display_needed)
        info_lines.append(f"{bar} Level {pet.level + 1} ({display_progress}/{display_needed} XP)")
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
    art_width = max(len(line) for line in lines) + 4
    result_lines = []
    for i in range(max(len(lines), len(info_lines))):
        art_part = lines[i] if i < len(lines) else ""
        info_part = info_lines[i] if i < len(info_lines) else ""
        result_lines.append(f"  {art_part:<{art_width}} {info_part}")
    return "\n".join(result_lines)
