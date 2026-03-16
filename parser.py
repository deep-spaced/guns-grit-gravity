"""
parser.py — Text input parser for Guns, Grit & Gravity.

Handles verb/noun extraction and synonym resolution.
The parser tries hard before giving up.
"""

from __future__ import annotations
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Synonym tables
# ---------------------------------------------------------------------------

VERB_SYNONYMS: dict[str, str] = {
    # Movement
    "go": "go", "move": "go", "walk": "go", "travel": "go", "head": "go",
    "run": "go", "climb": "go", "crawl": "go",
    # Look
    "look": "look", "l": "look", "describe": "look",
    # Examine
    "examine": "examine", "x": "examine", "inspect": "examine",
    "check": "examine", "read": "examine", "study": "examine",
    "view": "examine", "search": "examine",
    # Take
    "take": "take", "get": "take", "grab": "take", "pick": "take",
    "collect": "take", "retrieve": "take", "acquire": "take",
    # Drop
    "drop": "drop", "put": "drop", "place": "drop", "leave": "drop",
    "discard": "drop", "throw": "drop",
    # Inventory
    "inventory": "inventory", "inv": "inventory", "i": "inventory",
    "items": "inventory", "pockets": "inventory", "carrying": "inventory",
    # Talk
    "talk": "talk", "speak": "talk", "ask": "talk", "chat": "talk",
    "converse": "talk", "question": "talk", "greet": "talk",
    "hail": "talk", "address": "talk",
    # Use
    "use": "use", "apply": "use", "activate": "use", "operate": "use",
    "insert": "use", "attach": "use", "combine": "use",
    # Open
    "open": "open", "unlock": "open", "unbar": "open", "unseal": "open",
    "pry": "open",
    # Close
    "close": "close", "shut": "close", "seal": "close", "lock": "close",
    # Wear
    "wear": "wear", "put on": "wear", "don": "wear", "equip": "wear",
    # Remove (clothing)
    "remove": "remove", "take off": "remove", "doff": "remove",
    # Score
    "score": "score", "points": "score",
    # Help
    "help": "help", "?": "help", "h": "help", "commands": "help",
    # Save / Load
    "save": "save", "load": "load", "restore": "load",
    # Quit
    "quit": "quit", "q": "quit", "exit": "quit", "bye": "quit",
    # Enter (code)
    "enter": "enter", "type": "enter", "input": "enter", "dial": "enter",
    # Footnotes toggle
    "footnotes": "footnotes",
    # Hints
    "hint": "hint", "hints": "hint",
    # Wait
    "wait": "wait", "z": "wait", "rest": "wait",
    # Give
    "give": "give", "offer": "give", "hand": "give",
    # Board ship (keep ending)
    "board": "board", "launch": "board", "depart": "board", "fly": "board",
    # Eat/drink
    "eat": "eat", "drink": "eat", "consume": "eat",
}

DIRECTION_WORDS: dict[str, str] = {
    "north": "north", "n": "north",
    "south": "south", "s": "south",
    "east": "east", "e": "east",
    "west": "west", "w": "west",
    "up": "up", "u": "up", "upstairs": "up",
    "down": "down", "d": "down", "downstairs": "down",
    "in": "in", "inside": "in", "enter": "in",
    "out": "out", "outside": "out", "exit": "out",
    "northeast": "northeast", "ne": "northeast",
    "northwest": "northwest", "nw": "northwest",
    "southeast": "southeast", "se": "southeast",
    "southwest": "southwest", "sw": "southwest",
}

# Prepositions we strip from the middle of commands
PREPOSITIONS = {"on", "with", "at", "to", "from", "into", "onto", "in", "the", "a", "an"}


# ---------------------------------------------------------------------------
# Command dataclass
# ---------------------------------------------------------------------------

@dataclass
class Command:
    verb: str = ""
    noun: str = ""
    second_noun: str = ""
    raw: str = ""
    preposition: str = ""  # the prep connecting noun and second_noun

    def __bool__(self) -> bool:
        return bool(self.verb)


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    """
    Parses raw text input into structured Command objects.

    Strategy:
    1. Lowercase, strip whitespace
    2. Check for bare direction (n/s/go north/etc.)
    3. Extract verb from first token, normalize via synonym table
    4. Extract noun/second_noun from remainder, stripping prepositions
    """

    def parse(self, raw: str) -> Command:
        text = raw.lower().strip()
        if not text:
            return Command(raw=raw)

        cmd = Command(raw=raw)

        # --- Single-word direction shortcuts ---
        if text in DIRECTION_WORDS:
            cmd.verb = "go"
            cmd.noun = DIRECTION_WORDS[text]
            return cmd

        tokens = text.split()

        # --- Two-token "put on" / "take off" combos ---
        if len(tokens) >= 2:
            two_word = f"{tokens[0]} {tokens[1]}"
            if two_word in VERB_SYNONYMS:
                cmd.verb = VERB_SYNONYMS[two_word]
                rest = tokens[2:]
                self._fill_nouns(cmd, rest)
                return cmd

        # --- Single verb ---
        first = tokens[0]
        cmd.verb = VERB_SYNONYMS.get(first, first)  # unknown verbs kept as-is

        rest = tokens[1:]

        # If the verb was "go" and next token is a direction, done
        if cmd.verb == "go" and rest and rest[0] in DIRECTION_WORDS:
            cmd.noun = DIRECTION_WORDS[rest[0]]
            return cmd

        # If verb unrecognized but bare token is a direction, treat as "go"
        if cmd.verb not in VERB_SYNONYMS.values() and first in DIRECTION_WORDS:
            cmd.verb = "go"
            cmd.noun = DIRECTION_WORDS[first]
            return cmd

        self._fill_nouns(cmd, rest)
        return cmd

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _fill_nouns(self, cmd: Command, tokens: list[str]) -> None:
        """
        Extract noun and optional second_noun from token list.
        Splits on prepositions: USE [noun] ON [second_noun].
        """
        # Look for a splitting preposition
        split_idx = None
        split_prep = ""
        for i, t in enumerate(tokens):
            if t in ("on", "with", "at", "from", "onto", "into", "to") and i > 0:
                split_idx = i
                split_prep = t
                break

        if split_idx is not None:
            noun_tokens = [t for t in tokens[:split_idx] if t not in PREPOSITIONS]
            second_tokens = [t for t in tokens[split_idx + 1:] if t not in PREPOSITIONS]
            cmd.noun = " ".join(noun_tokens)
            cmd.second_noun = " ".join(second_tokens)
            cmd.preposition = split_prep
        else:
            # Handle "talk to [npc]"
            filtered = [t for t in tokens if t not in PREPOSITIONS]
            cmd.noun = " ".join(filtered)

    # ------------------------------------------------------------------
    # Matching helpers (used by engine to resolve item/npc names)
    # ------------------------------------------------------------------

    @staticmethod
    def match_item(noun: str, candidates: dict[str, list[str]]) -> str | None:
        """
        Given a noun and a dict of {item_id: [name, alias, alias...]},
        return the best-matching item_id or None.
        """
        noun = noun.lower().strip()
        if not noun:
            return None

        # Exact ID match
        if noun in candidates:
            return noun

        # Exact name/alias match
        for item_id, names in candidates.items():
            if noun in [n.lower() for n in names]:
                return item_id

        # Partial match (noun is a substring of any alias)
        for item_id, names in candidates.items():
            for name in names:
                if noun in name.lower():
                    return item_id

        return None
