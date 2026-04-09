"""Integration tests for the full pet lifecycle."""

from claude_pet.models import PetData, load_pet, save_pet
from claude_pet.server import handle_pet_react, handle_show_pet, handle_pet_talk, handle_pet_stats


def test_full_lifecycle(tmp_path):
    """Test: create pet, react to events, level up, talk, show stats."""
    pet = PetData(species="cat", name="Pixel")
    save_pet(pet, data_dir=tmp_path)

    result = handle_show_pet(data_dir=tmp_path)
    assert "Pixel" in result
    assert "Level 1" in result

    for _ in range(10):
        handle_pet_react("test_pass", data_dir=tmp_path)

    pet = load_pet(data_dir=tmp_path)
    assert pet.level == 2
    assert pet.xp == 100
    assert pet.stats.tests_passed == 10

    result = handle_pet_talk("hey Pixel what's up", data_dir=tmp_path)
    assert "*" in result
    assert "pixel" in result.lower()

    result = handle_pet_stats(data_dir=tmp_path)
    assert "10" in result
    assert "Level 2" in result or "Lv2" in result


def test_levelup_notification(tmp_path):
    """Test that leveling up produces a notification with unlocks."""
    pet = PetData(species="dog", name="Rex")
    pet.xp = 95
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
    assert pet.level == 20
    assert pet.stats.tests_passed == 1


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
