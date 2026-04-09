# claude-pet — Design Spec

A Claude Code plugin that gives you a persistent, customizable ASCII pet companion that reacts to your coding activity, levels up as you work, and develops personality.

## Architecture

### Plugin Structure

```
claude-pet/
├── .claude-plugin/
│   └── plugin.json              # plugin metadata (name, description, author)
├── .mcp.json                    # MCP server config (points to Python server)
├── skills/
│   └── pet-companion/
│       └── SKILL.md             # instructs Claude on pet behavior (event reactions, name detection)
├── commands/
│   └── pet.md                   # /pet slash command definition
├── src/
│   └── claude_pet/
│       ├── __init__.py
│       ├── server.py            # MCP server (tools: show_pet, pet_react, pet_talk, pet_stats, pet_design)
│       ├── designer.py          # Textual TUI for pet creation/customization
│       ├── models.py            # pet state, XP calculation, leveling logic
│       ├── ascii_art.py         # species ASCII templates + rendering with accessories/colors
│       └── personality.py       # species voice lines, mood logic, thought bubbles
├── pyproject.toml
└── README.md
```

### Three Layers

1. **Claude Code Plugin** — provides the `/pet` slash command and the `pet-companion` skill. The skill is always loaded in Claude's context and instructs Claude when to call MCP tools (after test results, commits, errors, or when the pet's name is mentioned).

2. **MCP Server** (`server.py`) — Python process running via the MCP protocol. Exposes tools that Claude calls. Reads and writes pet state to disk.

3. **Textual TUI** (`designer.py`) — launched by the `pet_design` tool. Opens in a separate terminal window for the pet creation/customization experience. Level-gated: only shows options the user has unlocked.

### State Persistence

All state stored in `~/.claude-pet/pet.json`:

```json
{
  "species": "cat",
  "name": "Witty",
  "color": "orange",
  "pattern": "tabby",
  "eyes": "cute",
  "accessories": {
    "collar": "bell",
    "scarf": "red"
  },
  "level": 7,
  "xp": 340,
  "mood": "happy",
  "mood_updated": "2026-04-09T14:30:00Z",
  "stats": {
    "tests_passed": 142,
    "tests_failed": 23,
    "commits": 38,
    "errors_fixed": 27,
    "sessions": 15,
    "total_session_minutes": 1240
  },
  "created": "2026-03-15T10:00:00Z"
}
```

## MCP Tools

### `show_pet`

Returns the full ASCII art rendering of the pet with stats, XP bar, and mood. This is what Claude calls when the user types `/pet` or asks to see their pet.

**Returns:**
```
   /\_/\        Witty — Level 7 Orange Tabby Cat
  ( ^.^ )       Mood: Happy :)
   > ^ <        ████████░░░░░░░░ Level 8 (340/400 XP)
  /|   |\
 (_|   |_)      Next unlock: Surprised eyes + Spotted pattern
  ~~~scarf~~~
```

If no pet exists yet, returns a message prompting the user to run the designer.

### `pet_react`

Called by Claude after coding events. Accepts an event type and optional detail.

**Parameters:**
- `event`: one of `test_pass`, `test_fail`, `commit`, `error`, `error_fixed`, `session_start`, `long_session`, `idle_return`
- `detail` (optional): string with context (e.g., test name, commit message)

**Behavior:**
- Awards XP based on event type
- Updates mood based on event
- If XP crosses a level threshold, triggers a level-up message with unlock info
- Returns a compact one-line reaction:

```
 /\_/\ Witty (Lv7) ████████░░ *prrr!* tests passed! +10 XP
( ^.^ )
```

**XP Awards:**

| Event | XP |
|-------|-----|
| test_pass | +10 |
| test_fail | +2 |
| commit | +15 |
| long_session (1hr+) | +20 |
| error_fixed (fail -> pass) | +25 |
| idle_return | +5 |

### `pet_talk`

Called when Claude detects the pet's name in conversation. Returns a species-appropriate response with vocalization and a "thought bubble" in cute species-specific language.

**Parameters:**
- `message`: what the user said

**Returns:**
```
   /\_/\
  ( ^.^ )  *mrrrow!*
   > ^ <
  /|   |\   (witty is doing very good! witty had lots of
 (_|   |_)   codey fun today and is feeling the happy purrs)
```

### `pet_stats`

Returns detailed statistics: level, total XP, XP to next level, all-time stats (tests passed, commits, errors fixed, sessions, total coding time).

### `pet_design`

Launches the Textual TUI in a separate terminal for pet creation or customization. Only shows options the user has unlocked at their current level. If no pet exists, starts the full creation flow (species -> appearance -> name). If a pet exists, opens the customization screen with current selections.

Species selection is permanent — cannot be changed without a full reset (`claude-pet reset` CLI command).

## Pet Designer TUI

### Screen 1: Species Selection (first-time only)

Arrow keys to navigate a list of 10 species. Live ASCII preview updates as user browses. Enter to confirm. This choice is permanent.

**Species:** Cat, Dog, Fox, Rabbit, Frog, Dragon, Penguin, Owl, Snake, Axolotl

### Screen 2: Appearance Customization

Split-pane layout: left side has dropdown selectors, right side shows live ASCII preview updating in real-time.

**Customization options (all level-gated):**
- Color
- Eye style
- Pattern
- Hat
- Scarf
- Collar
- Glasses
- Cape

Locked options appear grayed out with the required level shown, so the user can see what they're working toward.

### Screen 3: Name Input (first-time only)

Text input field. Final preview of the pet with all selections. Enter to save, Esc to go back.

## Leveling System

**XP curve:** `level * 50` XP per level. Level 2 = 100 XP, level 10 = 500 XP, level 20 = 1000 XP. Early levels come fast, later ones require sustained coding.

### Unlock Table

| Level | XP Required | Unlock |
|-------|-------------|--------|
| 1 | 0 | Species, name, 2 colors (white, gray) |
| 2 | 100 | +3 colors (orange, black, brown) |
| 3 | 150 | Cute eyes |
| 4 | 200 | Collar slot |
| 5 | 250 | Tabby pattern + Sleepy eyes |
| 6 | 300 | Scarf slot |
| 7 | 350 | +2 colors (golden, blue) |
| 8 | 400 | Surprised eyes + Spotted pattern |
| 9 | 450 | Hat slot |
| 10 | 500 | 2 hat options + Striped pattern |
| 11 | 550 | Glasses slot |
| 12 | 600 | Purple color + Wink eyes |
| 13 | 650 | Cape slot |
| 14 | 700 | Tuxedo pattern + new hat option |
| 15 | 750 | Cool eyes + new scarf option |
| 16 | 800 | 2 new collar options |
| 17 | 850 | 2 new cape options |
| 18 | 900 | New glasses + hat option |
| 19 | 950 | 2 new accessories (any slot) |
| 20 | 1000 | Title badge ("Master Coder", etc.) |

## Mood System

Moods are set by the most recent coding event and decay toward "idle" over time.

| Mood | Trigger | ASCII Face | Status Text |
|------|---------|-----------|-------------|
| Happy | Tests passing | `( ^.^ )` | Mood: Happy :) |
| Excited | Just committed | `( >.< )` | Mood: Excited :D |
| Worried | Tests failing | `( o.o )` | Mood: Worried :/ |
| Sleepy | Long session (2hr+) | `( -.- )` | Mood: Sleepy zzz |
| Sad | Repeated errors | `( ;.; )` | Mood: Sad :( |
| Focused | Active coding | `( -.o )` | Mood: Focused |
| Idle | Returned from break | `( o.O )` | Mood: Waking up... |

## Pet Personality & Voice

Each species has a distinct voice for vocalizations and thought bubbles.

| Species | Sounds | Thought Style |
|---------|--------|---------------|
| Cat | *mrrrow*, *prrr*, *mew!* | Cozy, aloof, refers to self in third person |
| Dog | *woof!*, *arf!*, *bark bark!* | Excitable, loyal, lots of enthusiasm |
| Fox | *yip!*, *chirp!* | Clever, sly, a bit mischievous |
| Rabbit | *thump*, *squeak!* | Shy, gentle, cautious |
| Frog | *ribbit*, *croak!* | Chill, zen, philosophical |
| Dragon | *grr*, *roar!*, *snort* | Dramatic, noble, grandiose |
| Penguin | *honk!*, *squawk!* | Formal, polite, a bit stiff |
| Owl | *hoot!*, *who!* | Wise, measured, cryptic |
| Snake | *hisss*, *sss!* | Smooth, calculating, dry wit |
| Axolotl | *blub*, *splash!* | Cheerful, innocent, easily amazed |

Thought bubbles use cute broken English specific to the species. Example for cat: "(witty is doing very good! witty had lots of codey fun today and is feeling the happy purrs)"

## Plugin Integration

### Skill: `pet-companion`

Always loaded in Claude's context. Instructs Claude to:
- Call `pet_react` after test results, commits, and error resolution
- Call `pet_talk` when the pet's name appears in user messages
- Call `show_pet` at the start of each session (greeting)
- Include the compact pet reaction inline rather than a separate message when responding to coding events

### Command: `/pet`

Slash command that tells Claude to call `show_pet` and display the full pet view with stats.

## Distribution

- **GitHub repo:** `claude-pet`
- **Install:** users add via `/plugins` in Claude Code
- **Requirements:** Python 3.10+, uv/uvx
- **Dependencies:** mcp (Python SDK), textual, rich
- **Reset:** `claude-pet reset` CLI command wipes `~/.claude-pet/pet.json` for a fresh start

### .mcp.json

The plugin's `.mcp.json` launches the MCP server via uvx:

```json
{
  "claude-pet": {
    "command": "uvx",
    "args": ["claude-pet", "serve"]
  }
}
```

The `serve` subcommand starts the MCP server over stdio. This is separate from the `design`, `reset`, and `show` CLI commands.

## CLI Commands

The `claude-pet` package also installs a CLI entry point:

- `claude-pet design` — launch the Textual TUI directly
- `claude-pet reset` — wipe pet data and start over (confirms before deleting)
- `claude-pet show` — print current pet to stdout (for use outside Claude)

## ASCII Art Approach

Each species has a base template (multi-line ASCII art, ~5-8 lines tall). The rendering pipeline:

1. Start with species base template
2. Swap in the current eye style based on mood or customization
3. Apply color via ANSI color codes (for terminals that support it)
4. Overlay accessories (hat above head, scarf below neck, glasses on face, cape behind, collar at neck)
5. Pattern affects the body characters (e.g., tabby uses `~` marks, spotted uses `o` marks)

Templates are stored as string constants in `ascii_art.py`, one per species. Each template has marked insertion points for eyes, accessories, and pattern overlays.
