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
