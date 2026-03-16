"""
npcs.py — NPC registry, NPC class, and dialogue system.

NPCs have opinions. They share them. They remember things.
Some of them remember things that are inconvenient for them.
"""

from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, field

DATA_DIR = Path(__file__).parent / "data"


@dataclass
class DialogueTopic:
    """A single conversation topic an NPC can discuss."""
    key: str
    text: str
    sets_flag: str | None = None
    requires_flag: str | None = None
    requires_credits: int = 0
    gives_item: str | None = None


@dataclass
class NPC:
    """A non-player character with location and dialogue."""

    npc_id: str
    name: str
    aliases: list[str]
    description: str
    examine_detail: str
    location: str
    greeting: str
    topics: dict[str, DialogueTopic]
    default_response: str

    def all_names(self) -> list[str]:
        return [self.name] + self.aliases

    def get_topic(self, key: str) -> DialogueTopic | None:
        return self.topics.get(key)

    def available_topics(self, player_flags: dict[str, bool]) -> list[DialogueTopic]:
        """Return topics available given current player flags."""
        result = []
        for topic in self.topics.values():
            req = topic.requires_flag
            if req is None or player_flags.get(req, False):
                result.append(topic)
        return result


class NPCRegistry:
    """Loads and manages all NPCs in the game."""

    def __init__(self) -> None:
        self._npcs: dict[str, NPC] = {}
        self._load()

    def _load(self) -> None:
        path = DATA_DIR / "npcs.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        for npc_id, ndata in data.items():
            topics_raw = ndata.get("dialogue", {}).get("topics", {})
            topics: dict[str, DialogueTopic] = {}
            for topic_key, tdata in topics_raw.items():
                topics[topic_key] = DialogueTopic(
                    key=topic_key,
                    text=tdata["text"],
                    sets_flag=tdata.get("sets_flag"),
                    requires_flag=tdata.get("requires_flag"),
                    requires_credits=tdata.get("requires_credits", 0),
                    gives_item=tdata.get("gives_item"),
                )

            self._npcs[npc_id] = NPC(
                npc_id=npc_id,
                name=ndata["name"],
                aliases=ndata.get("aliases", []),
                description=ndata["description"],
                examine_detail=ndata.get("examine_detail", ndata["description"]),
                location=ndata["location"],
                greeting=ndata["dialogue"]["greeting"],
                topics=topics,
                default_response=ndata["dialogue"].get("default", "They don't respond."),
            )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get(self, npc_id: str) -> NPC | None:
        return self._npcs.get(npc_id)

    def npcs_in_room(self, room_id: str) -> list[NPC]:
        return [n for n in self._npcs.values() if n.location == room_id]

    def name_map(self, npc_ids: list[str]) -> dict[str, list[str]]:
        result = {}
        for npc_id in npc_ids:
            npc = self.get(npc_id)
            if npc:
                result[npc_id] = npc.all_names()
        return result

    def all_name_map(self) -> dict[str, list[str]]:
        return {npc_id: npc.all_names() for npc_id, npc in self._npcs.items()}

    # ------------------------------------------------------------------
    # Dialogue resolution
    # ------------------------------------------------------------------

    def find_topic_for_noun(self, npc: NPC, noun: str) -> str | None:
        """
        Find the best topic key for a given player noun input.
        Checks if any topic key or synonym matches the noun.
        """
        noun = noun.lower().strip()
        # Direct key match
        if noun in npc.topics:
            return noun
        # Keyword search: topic key appears in noun, or noun in topic key
        for key in npc.topics:
            if key in noun or noun in key:
                return key
        # Fuzzy: any word in noun matches any word in a topic key
        noun_words = set(noun.split())
        for key in npc.topics:
            key_words = set(key.split("_"))
            if noun_words & key_words:
                return key
        return None

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {npc_id: {"location": npc.location} for npc_id, npc in self._npcs.items()}

    def from_dict(self, data: dict) -> None:
        for npc_id, ndata in data.items():
            npc = self._npcs.get(npc_id)
            if npc and "location" in ndata:
                npc.location = ndata["location"]
