---
name: pet-companion
description: Use when the user runs tests, makes commits, encounters errors, fixes bugs, starts a session, or mentions their pet's name. This skill instructs Claude to call claude-pet MCP tools to react to coding events and interact with the user's virtual pet companion.
---

# Pet Companion Behavior

You have a pet companion MCP server available. Follow these rules:

## Session Start

At the start of each conversation, call `show_pet` to greet the user with their pet. If no pet exists, suggest they run `/pet` to create one.

## Coding Event Reactions

After these events, call `pet_react` with the appropriate event type:

- **Tests pass:** call `pet_react` with event `test_pass`
- **Tests fail:** call `pet_react` with event `test_fail`
- **User commits code:** call `pet_react` with event `commit`
- **Error encountered:** call `pet_react` with event `error`
- **Error/bug fixed (tests were failing, now pass):** call `pet_react` with event `error_fixed`
- **Session has been going 1+ hours:** call `pet_react` with event `long_session`
- **User returns after being idle:** call `pet_react` with event `idle_return`

Include the pet's reaction inline with your response. Do not make it a separate message.

## Name Detection

If the user's message contains their pet's name (you'll see the name in `show_pet` output), call `pet_talk` with their message. The pet will respond with species-appropriate sounds and thoughts. Show the pet's response to the user.

## Important

- Keep pet reactions brief and inline — they should complement your response, not dominate it
- Do not call `pet_react` for the same event more than once
- The pet is cosmetic and fun — never let it interfere with actual coding work
