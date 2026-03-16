"""
puzzles.py — Puzzle state tracking and solution verification.

Puzzles in this game are generally 'do the right thing in the right order.'
This module tracks that an appropriate number of right things have happened.
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class PuzzleState:
    """
    Tracks all global puzzle/story flags for the game.

    These mirror the flags stored on the Player, but puzzle.py
    provides domain-specific query methods so the engine doesn't
    have to know about string flag names.
    """

    # We delegate to the player's flag dict
    _flags: dict[str, bool] = field(default_factory=dict)

    def sync(self, player_flags: dict[str, bool]) -> None:
        """Keep in sync with player flags (call after any flag change)."""
        self._flags = player_flags

    def flag(self, name: str) -> bool:
        return self._flags.get(name, False)

    # ------------------------------------------------------------------
    # Puzzle states — named queries for use in engine
    # ------------------------------------------------------------------

    def maintenance_hatch_open(self) -> bool:
        return self.flag("maintenance_hatch_open")

    def player_has_spurs(self) -> bool:
        return self.flag("wearing_spurs")

    def found_syndicate(self) -> bool:
        return self.flag("found_syndicate")

    def syndicate_door_open(self) -> bool:
        return self.flag("syndicate_door_open")

    def is_working_with_sheriff(self) -> bool:
        return self.flag("working_with_sheriff")

    def knows_about_third_party(self) -> bool:
        return self.flag("clem_told_you") or self.flag("holloway_revealed_third_party")

    def codicil_recovered(self) -> bool:
        return self.flag("codicil_recovered")

    def game_complete(self) -> bool:
        return self.flag("game_complete")

    # ------------------------------------------------------------------
    # Endgame condition check
    # ------------------------------------------------------------------

    def check_ending(self, player_flags: dict[str, bool]) -> str | None:
        """
        Check if any ending condition has been met.
        Returns ending type string or None.

        Endings:
        - 'sheriff': returned Codicil to Sheriff Vasquez
        - 'syndicate': gave Codicil to Director Holloway
        - 'brotherhood': gave Codicil to Augusto Claim
        - 'keep': kept Codicil and left station
        """
        self.sync(player_flags)
        if player_flags.get("ending_sheriff"):
            return "sheriff"
        if player_flags.get("ending_syndicate"):
            return "syndicate"
        if player_flags.get("ending_brotherhood"):
            return "brotherhood"
        if player_flags.get("ending_keep"):
            return "keep"
        return None

    # ------------------------------------------------------------------
    # Score events — point values for puzzle completions
    # ------------------------------------------------------------------

    SCORE_EVENTS = {
        "maintenance_hatch_open": 10,
        "found_syndicate": 15,
        "syndicate_door_open": 20,
        "clem_told_you": 10,
        "working_with_sheriff": 10,
        "codicil_recovered": 50,
        "game_complete": 25,
    }

    def check_score_events(
        self,
        old_flags: dict[str, bool],
        new_flags: dict[str, bool],
    ) -> int:
        """Return score points earned by newly-set flags."""
        points = 0
        for flag_name, pts in self.SCORE_EVENTS.items():
            if new_flags.get(flag_name) and not old_flags.get(flag_name):
                points += pts
        return points
