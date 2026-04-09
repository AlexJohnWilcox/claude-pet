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
    assert set(unlocks["colors"]) == {"white", "gray", "black"}

    unlocks = get_unlocks_at_level(2)
    assert "colors" in unlocks
    assert set(unlocks["colors"]) == {"orange", "brown"}


def test_get_all_unlocked():
    unlocked = get_all_unlocked(level=3)
    assert "white" in unlocked["colors"]
    assert "gray" in unlocked["colors"]
    assert "orange" in unlocked["colors"]
    assert "cute" in unlocked["eyes"]  # now at level 1
    assert "sleepy" in unlocked["eyes"]  # now at level 3


def test_pet_level_cap():
    pet = PetData(species="cat", name="Max")
    pet.level = 20
    pet.xp = 10000
    leveled_up = pet.add_xp(9999)
    assert pet.level == 20
    assert leveled_up is False
