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
