"""
items.py — Item registry, Item class, and interaction handlers.

Items do things when used. Some of them do unexpected things.
This is the frontier. Manage your expectations.
"""

from __future__ import annotations
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any

DATA_DIR = Path(__file__).parent / "data"


@dataclass
class Item:
    """Represents a single item in the game world."""

    item_id: str
    name: str
    aliases: list[str]
    description: str
    examine_detail: str
    takeable: bool
    weight: int
    location: str | None           # room_id where item sits (None = in container or inventory)
    container_location: str | None  # item_id of containing item, if any

    # Optional properties
    wearable: bool = False
    worn: bool = False
    container: bool = False
    locked: bool = False
    lock_code: str | None = None
    lock_mechanism: str | None = None
    contents: list[str] = field(default_factory=list)   # item IDs inside this container
    use_on: dict[str, dict] = field(default_factory=dict)  # target_id -> effect dict
    use_text: str = ""
    grants_flag: str | None = None
    score_on_take: int = 0
    score_on_examine: int = 0
    heals: int = 0
    gives_item: str | None = None
    note: str = ""  # internal designer note, not shown to player

    # Container state
    open: bool = True   # containers start open unless locked

    def all_names(self) -> list[str]:
        """Return all names and aliases for matching."""
        return [self.name] + self.aliases

    def is_in_room(self, room_id: str) -> bool:
        return self.location == room_id

    def is_in_container(self, container_id: str) -> bool:
        return self.container_location == container_id

    def move_to_room(self, room_id: str) -> None:
        self.location = room_id
        self.container_location = None

    def move_to_inventory(self) -> None:
        self.location = None
        self.container_location = None

    def move_to_container(self, container_id: str) -> None:
        self.location = None
        self.container_location = container_id


class ItemRegistry:
    """Loads and manages all items in the game."""

    def __init__(self) -> None:
        self._items: dict[str, Item] = {}
        self._load()

    def _load(self) -> None:
        path = DATA_DIR / "items.json"
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        for item_id, idata in data.items():
            use_on_raw = idata.get("use_on", {})
            self._items[item_id] = Item(
                item_id=item_id,
                name=idata["name"],
                aliases=idata.get("aliases", []),
                description=idata["description"],
                examine_detail=idata.get("examine_detail", idata["description"]),
                takeable=idata.get("takeable", True),
                weight=idata.get("weight", 1),
                location=idata.get("location"),
                container_location=idata.get("container_location"),
                wearable=idata.get("wearable", False),
                container=idata.get("container", False),
                locked=idata.get("locked", False),
                lock_code=idata.get("lock_code"),
                lock_mechanism=idata.get("lock_mechanism"),
                contents=list(idata.get("contents", [])),
                use_on=use_on_raw,
                use_text=idata.get("use_text", ""),
                grants_flag=idata.get("grants_flag"),
                score_on_take=idata.get("score_on_take", 0),
                score_on_examine=idata.get("score_on_examine", 0),
                heals=idata.get("heals", 0),
                gives_item=idata.get("gives_item"),
                note=idata.get("note", ""),
                open=not idata.get("locked", False),
            )

    # ------------------------------------------------------------------
    # Accessors
    # ------------------------------------------------------------------

    def get(self, item_id: str) -> Item | None:
        return self._items.get(item_id)

    def all_items(self) -> list[Item]:
        return list(self._items.values())

    def items_in_room(self, room_id: str) -> list[Item]:
        return [i for i in self._items.values() if i.location == room_id]

    def items_in_container(self, container_id: str) -> list[Item]:
        return [i for i in self._items.values() if i.container_location == container_id]

    def name_map(self, item_ids: list[str]) -> dict[str, list[str]]:
        """
        Return {item_id: [name, alias, ...]} for matching.
        Only for the given item_ids.
        """
        result = {}
        for item_id in item_ids:
            item = self.get(item_id)
            if item:
                result[item_id] = item.all_names()
        return result

    def all_name_map(self) -> dict[str, list[str]]:
        return {item_id: item.all_names() for item_id, item in self._items.items()}

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        result = {}
        for item_id, item in self._items.items():
            result[item_id] = {
                "location": item.location,
                "container_location": item.container_location,
                "locked": item.locked,
                "open": item.open,
                "worn": item.worn,
                "contents": item.contents,
            }
        return result

    def from_dict(self, data: dict) -> None:
        for item_id, idata in data.items():
            item = self._items.get(item_id)
            if item:
                item.location = idata.get("location", item.location)
                item.container_location = idata.get("container_location", item.container_location)
                item.locked = idata.get("locked", item.locked)
                item.open = idata.get("open", item.open)
                item.worn = idata.get("worn", item.worn)
                item.contents = idata.get("contents", item.contents)
