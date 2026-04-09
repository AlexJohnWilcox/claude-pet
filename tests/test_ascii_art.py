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
    assert "{eyes}" in template


def test_get_species_template_all_species():
    from claude_pet.models import SPECIES_LIST
    for species in SPECIES_LIST:
        template = get_species_template(species)
        assert template is not None, f"Missing template for {species}"
        assert "{eyes}" in template, f"No eye placeholder in {species}"


def test_render_eyes():
    assert render_eyes("default") == "o.o"
    assert render_eyes("cute") == "^.^"
    assert render_eyes("sleepy") == "-.~"
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
    assert "█" in result


def test_render_pet_full_no_pet():
    result = render_pet_full(None)
    assert "no pet" in result.lower() or "design" in result.lower()
