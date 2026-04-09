"""Platform detection and terminal auto-open logic."""

from __future__ import annotations

import shutil
import subprocess
import sys

LINUX_TERMINALS = ["kitty", "alacritty", "gnome-terminal", "konsole", "xfce4-terminal", "x-terminal-emulator"]


def detect_terminal() -> str:
    platform = sys.platform
    if platform == "darwin":
        if shutil.which("osascript"):
            return "iterm2"
        return "terminal.app"
    if platform == "win32":
        return "cmd"
    for term in LINUX_TERMINALS:
        if shutil.which(term):
            return term
    return "xterm"


def build_launch_command(terminal: str, command: str) -> list[str]:
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
