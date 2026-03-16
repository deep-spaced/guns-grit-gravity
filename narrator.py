"""
narrator.py — Output formatting, footnote system, and text rendering.

The narrator has opinions. It shares them via footnotes.
"""

import textwrap
import sys

WRAP_WIDTH = 78


def _wrap(text: str) -> str:
    """Wrap a block of text, preserving intentional blank lines."""
    lines = text.split("\n")
    wrapped_lines = []
    for line in lines:
        if line.strip() == "":
            wrapped_lines.append("")
        else:
            wrapped_lines.extend(textwrap.wrap(line, width=WRAP_WIDTH))
    return "\n".join(wrapped_lines)


class Narrator:
    """Handles all text output, footnote display, and formatting."""

    def __init__(self) -> None:
        self.footnotes_enabled: bool = True
        self._pending_footnotes: list[str] = []

    # ------------------------------------------------------------------
    # Core output
    # ------------------------------------------------------------------

    def say(self, text: str, wrap: bool = True) -> None:
        """Print a line or block of text."""
        output = _wrap(text) if wrap else text
        print(output)

    def blank(self) -> None:
        """Print a blank line."""
        print()

    def separator(self) -> None:
        """Print a horizontal rule."""
        print("-" * WRAP_WIDTH)

    # ------------------------------------------------------------------
    # Structured output helpers
    # ------------------------------------------------------------------

    def location_header(self, name: str) -> None:
        """Print a room name header."""
        self.blank()
        print(name.upper())
        print()

    def describe_room(
        self,
        name: str,
        description: str,
        footnote: str | None = None,
        brief: bool = False,
    ) -> None:
        """Output a room description, with optional footnote."""
        self.location_header(name)
        if not brief:
            self.say(description)
        if footnote and self.footnotes_enabled and not brief:
            self.blank()
            self._print_footnote(footnote)
        self.blank()

    def _print_footnote(self, text: str) -> None:
        """Print a narrator footnote."""
        lines = textwrap.wrap(text, width=WRAP_WIDTH - 2)
        for i, line in enumerate(lines):
            prefix = "* " if i == 0 else "  "
            print(prefix + line)

    def describe_item(self, description: str) -> None:
        """Output an item or NPC description."""
        self.blank()
        self.say(description)
        self.blank()

    def list_exits(self, exits: dict[str, str]) -> None:
        """Print available exits."""
        if not exits:
            self.say("There are no obvious exits.")
            return
        directions = sorted(exits.keys())
        self.say("Exits: " + ", ".join(d.capitalize() for d in directions) + ".")

    def inventory_list(self, items: list[str], empty_msg: str) -> None:
        """Print inventory contents."""
        self.blank()
        if not items:
            self.say(empty_msg)
        else:
            for item_name in items:
                print(f"  {item_name}")
        self.blank()

    # ------------------------------------------------------------------
    # Dialogue
    # ------------------------------------------------------------------

    def npc_speaks(self, npc_name: str, text: str) -> None:
        """Output NPC dialogue with name header."""
        self.blank()
        self.say(npc_name.upper())
        self.blank()
        self.say(text)
        self.blank()

    def dialogue_options(self, options: list[tuple[int, str]]) -> None:
        """Print numbered dialogue options."""
        self.blank()
        for number, text in options:
            print(f"  [{number}] {text}")
        self.blank()

    # ------------------------------------------------------------------
    # System messages
    # ------------------------------------------------------------------

    def system(self, text: str) -> None:
        """Print a system/game message."""
        self.say(text)

    def error(self, text: str) -> None:
        """Print an error or failure message."""
        self.say(text)

    def score_display(self, score: int, max_score: int, turns: int, rank: str, credits: int = 0) -> None:
        """Print the score summary."""
        self.blank()
        self.say(f"Score: {score} of {max_score} points, in {turns} turn(s).")
        self.say(f"Rank: {rank}")
        self.say(f"Credits: {credits}")
        self.blank()

    def death(self, message_lines: list[str], score: int, max_score: int, rank: str) -> None:
        """Print a death message."""
        self.blank()
        self.separator()
        self.blank()
        for line in message_lines:
            line = line.replace("{score}", str(score))
            line = line.replace("{max_score}", str(max_score))
            line = line.replace("{rank}", rank)
            print(line)
        self.blank()
        self.separator()
        self.blank()

    def title_screen(self, title_lines: list[str], intro_lines: list[str]) -> None:
        """Print the opening title and intro text."""
        self.blank()
        self.separator()
        for line in title_lines:
            self.blank()
            centered = line.center(WRAP_WIDTH)
            print(centered)
        self.blank()
        self.separator()
        self.blank()
        for line in intro_lines:
            if line == "":
                self.blank()
            else:
                self.say(line)
        self.blank()

    def quit_message(self, msg: str) -> None:
        """Print the quit message."""
        self.blank()
        self.separator()
        self.blank()
        self.say(msg)
        self.blank()

    # ------------------------------------------------------------------
    # Footnote toggle
    # ------------------------------------------------------------------

    def set_footnotes(self, enabled: bool) -> None:
        self.footnotes_enabled = enabled

    def toggle_footnotes(self) -> bool:
        self.footnotes_enabled = not self.footnotes_enabled
        return self.footnotes_enabled

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------

    def prompt(self) -> str:
        """Read a line of input from the player."""
        try:
            return input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            self.blank()
            return "quit"
