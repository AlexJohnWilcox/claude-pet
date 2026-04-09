"""Tests for MCP server tool logic."""

from claude_pet.models import PetData, save_pet, load_pet
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

    updated = load_pet(data_dir=tmp_path)
    assert updated.xp == 10
    assert updated.stats.tests_passed == 1


def test_handle_pet_react_commit(tmp_path):
    pet = PetData(species="dog", name="Rex")
    save_pet(pet, data_dir=tmp_path)

    result = handle_pet_react("commit", data_dir=tmp_path)
    assert "+15 XP" in result

    updated = load_pet(data_dir=tmp_path)
    assert updated.xp == 15
    assert updated.stats.commits == 1


def test_handle_pet_react_levelup(tmp_path):
    pet = PetData(species="cat", name="Witty")
    pet.xp = 95
    save_pet(pet, data_dir=tmp_path)

    result = handle_pet_react("test_pass", data_dir=tmp_path)
    assert "LEVEL UP" in result.upper() or "level" in result.lower()

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
    assert "*" in result
    assert "witty" in result.lower()


def test_handle_pet_stats(tmp_path):
    pet = PetData(species="cat", name="Witty")
    pet.level = 5
    pet.xp = 300
    pet.stats.tests_passed = 50
    pet.stats.commits = 12
    save_pet(pet, data_dir=tmp_path)

    result = handle_pet_stats(data_dir=tmp_path)
    assert "Level 5" in result or "Lv5" in result
    assert "50" in result
    assert "12" in result
