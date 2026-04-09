# claude-pet

A Claude Code plugin that gives you a persistent, customizable ASCII pet companion. Your pet reacts to your coding activity, levels up as you work, and develops its own personality.

## Install

```
claude plugins marketplace add AlexJohnWilcox/claude-pet
claude plugins install claude-pet
```

## Features

- **9 species** — Cat, Dog, Fox, Rabbit, Frog, Penguin, Owl, Snake, Axolotl
- **Custom appearance** — Colors, eye styles, patterns, and accessories
- **Leveling system** — 20 levels with unlockable customization options
- **Mood reactions** — Your pet reacts to test results, commits, errors, and more
- **Personality** — Each species has its own voice and thought style
- **Name your pet** — And it responds when you mention its name!

## Usage

- `/pet` — Open the pet designer or view your pet
- Talk to your pet by saying its name in conversation

Your pet automatically reacts to coding events like passing tests, committing code, and fixing bugs.

## Leveling

You earn XP by coding:

| Activity | XP |
|----------|-----|
| Test pass | +10 |
| Test fail | +2 |
| Commit | +15 |
| Long session (1hr+) | +20 |
| Fix a bug | +25 |
| Return from break | +5 |

Level up to unlock new colors, eye styles, patterns, accessories, and more. Max level: 20.

## Requirements

- Python 3.10+
- uv/uvx
