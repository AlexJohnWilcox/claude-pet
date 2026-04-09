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
    instructions="A persistent ASCII pet companion that reacts to your coding activity.",
)


def handle_show_pet(data_dir: Path = DEFAULT_DATA_DIR) -> str:
    pet = load_pet(data_dir=data_dir)
    return render_pet_full(pet)


def handle_pet_react(event: str, detail: str = "", data_dir: Path = DEFAULT_DATA_DIR) -> str:
    pet = load_pet(data_dir=data_dir)
    if pet is None:
        return "No pet found! Run 'claude-pet design' to create one."

    xp_amount = XP_EVENTS.get(event, 0)
    leveled_up = pet.add_xp(xp_amount)

    new_mood = get_mood_for_event(event)
    pet.set_mood(new_mood)

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
    pet = load_pet(data_dir=data_dir)
    if pet is None:
        return "No pet found! Run 'claude-pet design' to create one."

    vocalization = get_vocalization(pet.species)
    thought = get_thought_bubble(pet.species, pet.name, pet.mood)

    lines = _render_ascii(pet.species, pet.eyes, pet.mood, pet.pattern)
    art = "\n".join(f"  {line}" for line in lines)

    return f"{art}  {vocalization}\n\n  {thought}"


def handle_pet_stats(data_dir: Path = DEFAULT_DATA_DIR) -> str:
    pet = load_pet(data_dir=data_dir)
    if pet is None:
        return "No pet found! Run 'claude-pet design' to create one."

    progress, needed = pet.xp_progress()
    mood_str = MOOD_TEXT.get(pet.mood, pet.mood.capitalize())

    stats = [
        f"=== {pet.name} Stats ===",
        f"Species: {pet.species.capitalize()}",
        f"Level {pet.level} ({pet.xp} total XP)",
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
