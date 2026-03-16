"""
world.py — Room graph, location registry, and exit management.

Loads room data from data/rooms.json and provides query and traversal
methods. The world does not move. You do.
"""

from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, field


DATA_DIR = Path(__file__).parent / "data"


@dataclass
class Room:
    """A single location in the game world."""
    room_id: str
    name: str
    description: str
    footnote: str
    exits: dict[str, str]          # direction -> room_id
    item_ids: list[str]            # item IDs present in room
    npc_ids: list[str]             # NPC IDs present in room
    flags: dict[str, object]       # room-specific flags
    visited: bool = False

    def add_item(self, item_id: str) -> None:
        if item_id not in self.item_ids:
            self.item_ids.append(item_id)

    def remove_item(self, item_id: str) -> None:
        if item_id in self.item_ids:
            self.item_ids.remove(item_id)

    def has_item(self, item_id: str) -> bool:
        return item_id in self.item_ids

    def has_npc(self, npc_id: str) -> bool:
        return npc_id in self.npc_ids

    def requires_flag(self) -> str | None:
        """Return a required flag for entry, or None."""
        return self.flags.get("requires_flag")  # type: ignore[return-value]


class World:
    """The game world: all rooms, their connections, and state."""

    def __init__(self) -> None:
        self._rooms: dict[str, Room] = {}
        self._load()

    def _load(self) -> None:
        path = DATA_DIR / "rooms.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        for room_id, rdata in data.items():
            self._rooms[room_id] = Room(
                room_id=room_id,
                name=rdata["name"],
                description=rdata["description"],
                footnote=rdata.get("footnote", ""),
                exits=rdata.get("exits", {}),
                item_ids=list(rdata.get("items", [])),
                npc_ids=list(rdata.get("npcs", [])),
                flags=dict(rdata.get("flags", {})),
            )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get(self, room_id: str) -> Room:
        """Return a Room by ID. Raises KeyError if not found."""
        return self._rooms[room_id]

    def exists(self, room_id: str) -> bool:
        return room_id in self._rooms

    def all_rooms(self) -> list[Room]:
        return list(self._rooms.values())

    # ------------------------------------------------------------------
    # Traversal
    # ------------------------------------------------------------------

    def exit_destination(self, room: Room, direction: str) -> str | None:
        """Return the destination room_id for a direction, or None."""
        return room.exits.get(direction)

    def can_enter(self, room: Room, player_flags: dict[str, bool]) -> tuple[bool, str | None]:
        """
        Check whether a room can be entered given player flags.
        Returns (can_enter, required_flag_or_None).
        """
        req = room.requires_flag()
        if req is None:
            return True, None
        if player_flags.get(req, False):
            return True, None
        return False, req

    # ------------------------------------------------------------------
    # State serialization (for save/load)
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            room_id: {
                "item_ids": room.item_ids,
                "npc_ids": room.npc_ids,
                "visited": room.visited,
                "flags": room.flags,
            }
            for room_id, room in self._rooms.items()
        }

    def from_dict(self, data: dict) -> None:
        for room_id, rdata in data.items():
            if room_id in self._rooms:
                room = self._rooms[room_id]
                room.item_ids = rdata.get("item_ids", room.item_ids)
                room.npc_ids = rdata.get("npc_ids", room.npc_ids)
                room.visited = rdata.get("visited", False)
                room.flags.update(rdata.get("flags", {}))
