"""
web_narrator.py — WebNarrator: buffers all output as JSON messages
instead of printing to stdout.

Each call appends a typed message dict to an internal buffer.
The FastAPI app calls flush() after each engine.process() to collect
everything that happened and send it to the client.
"""

from __future__ import annotations
import textwrap

WRAP_WIDTH = 78


def _wrap(text: str) -> str:
    lines = text.split("\n")
    wrapped = []
    for line in lines:
        if line.strip() == "":
            wrapped.append("")
        else:
            wrapped.extend(textwrap.wrap(line, width=WRAP_WIDTH))
    return "\n".join(wrapped)


class WebNarrator:
    """Drop-in replacement for Narrator that buffers output as dicts."""

    def __init__(self) -> None:
        self.footnotes_enabled: bool = True
        self._buffer: list[dict] = []

    # ------------------------------------------------------------------
    # Buffer management
    # ------------------------------------------------------------------

    def flush(self) -> list[dict]:
        """Return buffered messages and clear the buffer."""
        msgs = self._buffer.copy()
        self._buffer.clear()
        return msgs

    def _push(self, type_: str, content: str = "", **extra) -> None:
        msg = {"type": type_, "content": content}
        msg.update(extra)
        self._buffer.append(msg)

    # ------------------------------------------------------------------
    # Core output (mirror Narrator interface)
    # ------------------------------------------------------------------

    def say(self, text: str, wrap: bool = True) -> None:
        content = _wrap(text) if wrap else text
        self._push("text", content)

    def blank(self) -> None:
        self._push("blank", "")

    def separator(self) -> None:
        self._push("separator", "")

    # ------------------------------------------------------------------
    # Structured output
    # ------------------------------------------------------------------

    def location_header(self, name: str) -> None:
        self._push("location", name.upper())

    def describe_room(
        self,
        name: str,
        description: str,
        footnote: str | None = None,
        brief: bool = False,
    ) -> None:
        self.location_header(name)
        if not brief:
            self.say(description)
        if footnote and self.footnotes_enabled and not brief:
            self._push("footnote", footnote)
        self.blank()

    def describe_item(self, description: str) -> None:
        self.blank()
        self.say(description)
        self.blank()

    def list_exits(self, exits: dict[str, str]) -> None:
        if not exits:
            self.say("There are no obvious exits.")
            return
        directions = sorted(exits.keys())
        self.say("Exits: " + ", ".join(d.capitalize() for d in directions) + ".")

    def inventory_list(self, items: list[str], empty_msg: str) -> None:
        self.blank()
        if not items:
            self.say(empty_msg)
        else:
            for item_name in items:
                self._push("item_line", f"  {item_name}")
        self.blank()

    # ------------------------------------------------------------------
    # Dialogue
    # ------------------------------------------------------------------

    def npc_speaks(self, npc_name: str, text: str) -> None:
        self.blank()
        self._push("npc_name", npc_name.upper())
        self.blank()
        self.say(text)
        self.blank()

    def dialogue_options(self, options: list[tuple[int, str]]) -> None:
        self.blank()
        for number, text in options:
            self._push("dialogue_option", f"[{number}] {text}", number=number)
        self.blank()

    # ------------------------------------------------------------------
    # System messages
    # ------------------------------------------------------------------

    def system(self, text: str) -> None:
        self._push("system", text)

    def error(self, text: str) -> None:
        self._push("error", text)

    def score_display(self, score: int, max_score: int, turns: int, rank: str, credits: int = 0) -> None:
        self.blank()
        self._push("score", "", score=score, max_score=max_score,
                   turns=turns, rank=rank, credits=credits)
        self.blank()

    def death(self, message_lines: list[str], score: int, max_score: int, rank: str) -> None:
        self.blank()
        self.separator()
        self.blank()
        for line in message_lines:
            line = (line.replace("{score}", str(score))
                       .replace("{max_score}", str(max_score))
                       .replace("{rank}", rank))
            self._push("death_line", line)
        self.blank()
        self.separator()
        self.blank()

    def title_screen(self, title_lines: list[str], intro_lines: list[str]) -> None:
        self.blank()
        self.separator()
        for line in title_lines:
            self._push("title_line", line)
        self.separator()
        self.blank()
        for line in intro_lines:
            if line == "":
                self.blank()
            else:
                self.say(line)
        self.blank()

    def quit_message(self, msg: str) -> None:
        self.blank()
        self.separator()
        self.blank()
        self._push("quit_message", msg)
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
    # Prompt (not used in web mode — input comes via WebSocket)
    # ------------------------------------------------------------------

    def prompt(self) -> str:
        return ""
