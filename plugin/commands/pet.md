---
description: Open your pet companion — design, view, and customize your ASCII pet
allowed-tools: [mcp__plugin_claude-pet_claude-pet__pet_design, mcp__plugin_claude-pet_claude-pet__show_pet]
---

# /pet Command

Call the `pet_design` tool to open the pet designer TUI in a new terminal window.

If the user has no pet yet, tell them: "Opening the pet designer in a new terminal! Create your first pet there, then come back and I'll introduce you."

If the user already has a pet, tell them: "Opening the pet designer so you can customize your pet. Any changes you make will show up here when you're done."

After the user confirms they're done in the designer, call `show_pet` to display the updated pet.
