"""Tests for terminal detection and auto-open."""

import shutil
from unittest.mock import patch

from claude_pet.terminal import detect_terminal, build_launch_command


def test_detect_terminal_linux():
    with patch("sys.platform", "linux"):
        with patch("claude_pet.terminal.shutil.which") as mock_which:
            mock_which.side_effect = lambda x: f"/usr/bin/{x}" if x == "kitty" else None
            term = detect_terminal()
            assert term == "kitty"


def test_detect_terminal_linux_fallback():
    with patch("sys.platform", "linux"):
        with patch("claude_pet.terminal.shutil.which") as mock_which:
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
