"""Species personality, voice lines, mood logic, and thought bubbles."""

from __future__ import annotations

import random

VOCALIZATIONS: dict[str, list[str]] = {
    "cat": ["*mrrrow!*", "*prrr*", "*mew!*"],
    "dog": ["*woof!*", "*arf!*", "*bark bark!*"],
    "fox": ["*yip!*", "*chirp!*", "*yap!*"],
    "rabbit": ["*thump*", "*squeak!*", "*nose wiggle*"],
    "frog": ["*ribbit*", "*croak!*", "*blup*"],
    "penguin": ["*honk!*", "*squawk!*", "*waddle waddle*"],
    "owl": ["*hoot!*", "*who!*", "*hoo hoo*"],
    "snake": ["*hisss*", "*sss!*", "*flick*"],
    "axolotl": ["*blub*", "*splash!*", "*bloop*"],
}

EVENT_MOODS: dict[str, str] = {
    "test_pass": "happy",
    "test_fail": "worried",
    "commit": "excited",
    "error": "worried",
    "error_fixed": "excited",
    "long_session": "sleepy",
    "idle_return": "idle",
    "session_start": "happy",
}

THOUGHT_TEMPLATES: dict[str, dict[str, list[str]]] = {
    "cat": {
        "happy": [
            "({name} is feeling the warm purrs today! so much good codey happening)",
            "({name} approves of this work... maybe... {name} will allow more pets later)",
        ],
        "excited": [
            "({name} does a little spinny! the code goes whoosh!)",
            "(the commit was very impressive, {name} thinks. almost as good as a sunbeam)",
        ],
        "worried": [
            "({name} does not like the red errors... {name} hides behind the keyboard)",
            "(something is not right... {name} senses a disturbance in the code)",
        ],
        "sleepy": [
            "({name} is getting so sleepy... maybe time for a nap on the warm laptop?)",
            "(*yawn* {name} has been watching code for so long... eyes getting heavy...)",
        ],
        "sad": [
            "({name} is sad... so many errors... {name} needs chin scratches)",
            "({name} curls up small... the bugs are too many today...)",
        ],
        "focused": [
            "({name} is watching the screen very carefully... tail twitching...)",
            "({name} is in the zone! no distractions! only code!)",
        ],
        "idle": [
            "({name} wakes up! oh! the human is back! {name} pretends was never asleep)",
            "(*stretch* {name} was definitely not sleeping... just resting eyes...)",
        ],
    },
}

DEFAULT_THOUGHTS: dict[str, list[str]] = {
    "happy": [
        "({name} is very happy! the code is going so well!)",
        "({name} likes this! good work, friend!)",
    ],
    "excited": [
        "({name} is so excited! something great just happened!)",
        "(wow wow wow! {name} can hardly contain it!)",
    ],
    "worried": [
        "({name} is a little worried... is everything okay?)",
        "(hmm... {name} sees some problems... but we can fix them!)",
    ],
    "sleepy": [
        "({name} is getting sleepy... it has been a long session...)",
        "(*yawn* {name} thinks maybe a break would be nice...)",
    ],
    "sad": [
        "({name} is feeling down... but tomorrow will be better!)",
        "({name} is sad... but {name} believes in you!)",
    ],
    "focused": [
        "({name} is concentrating very hard right now...)",
        "({name} is in deep focus mode!)",
    ],
    "idle": [
        "({name} is waking up! hello again!)",
        "(*blink blink* {name} is back!)",
    ],
}

EVENT_REACTIONS: dict[str, list[str]] = {
    "test_pass": ["tests passed!", "all green!", "tests looking good!"],
    "test_fail": ["tests failed...", "uh oh, red tests!", "something broke..."],
    "commit": ["new commit!", "code saved!", "nice commit!"],
    "error_fixed": ["bug squashed!", "error fixed!", "nice fix!"],
    "long_session": ["long session...", "been coding a while!", "maybe take a break?"],
    "idle_return": ["welcome back!", "you're back!", "missed you!"],
    "session_start": ["hello!", "ready to code!", "let's go!"],
    "error": ["uh oh...", "error detected...", "hmm, something's wrong..."],
}


def get_vocalization(species: str) -> str:
    sounds = VOCALIZATIONS.get(species, ["*...*"])
    return random.choice(sounds)


def get_thought_bubble(species: str, name: str, mood: str) -> str:
    species_thoughts = THOUGHT_TEMPLATES.get(species, {})
    mood_thoughts = species_thoughts.get(mood, DEFAULT_THOUGHTS.get(mood, []))
    if not mood_thoughts:
        mood_thoughts = DEFAULT_THOUGHTS.get("happy", ["({name} is here!)"])
    template = random.choice(mood_thoughts)
    return template.replace("{name}", name.lower())


def get_mood_for_event(event: str) -> str:
    return EVENT_MOODS.get(event, "idle")


def get_reaction_text(species: str, event: str) -> str:
    reactions = EVENT_REACTIONS.get(event, ["..."])
    return random.choice(reactions)
