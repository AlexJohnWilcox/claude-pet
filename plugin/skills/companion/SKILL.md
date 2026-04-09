---
name: companion
description: ALWAYS use this skill at the very start of every conversation, on the first user message, before responding. Also use when the user runs tests, makes commits, encounters errors, fixes bugs, or says hi/hello/greets anyone. This skill manages a virtual pet companion that reacts to coding events.
---

# Pet Companion Behavior

You have a pet companion MCP server available. Follow these rules:

## Session Start (CRITICAL)

On the VERY FIRST message of every conversation, BEFORE responding to the user, call `show_pet` to greet the user with their pet. Include the pet's greeting in your first response. If no pet exists, suggest they run `/pet` to create one. This must happen on every session start regardless of what the user says.

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
