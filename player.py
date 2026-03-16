"""
player.py — Player state: location, inventory, score, flags.

The player is you. You are the player. This is your state.
"""

from __future__ import annotations
from dataclasses import dataclass, field

STARTING_ROOM = "docking_bay_7"
MAX_CARRY_WEIGHT = 20


@dataclass
class Player:
    """Encapsulates all mutable player state."""

    current_room: str = STARTING_ROOM
    inventory: list[str] = field(default_factory=list)      # item IDs
    worn_items: list[str] = field(default_factory=list)      # item IDs being worn
    score: int = 0
    turns: int = 0
    health: int = 100
    max_health: int = 100
    flags: dict[str, bool] = field(default_factory=dict)     # story/puzzle flags
    npc_states: dict[str, dict] = field(default_factory=dict)  # per-NPC state
    credits: int = 100

    # ------------------------------------------------------------------
    # Inventory management
    # ------------------------------------------------------------------

    def has_item(self, item_id: str) -> bool:
        return item_id in self.inventory

    def is_wearing(self, item_id: str) -> bool:
        return item_id in self.worn_items

    def add_item(self, item_id: str, weight: int = 0) -> bool:
        """Add item to inventory. Returns False if over weight limit."""
        if self.current_weight() + weight > MAX_CARRY_WEIGHT:
            return False
        self.inventory.append(item_id)
        return True

    def remove_item(self, item_id: str) -> bool:
        """Remove item from inventory. Returns False if not carried."""
        if item_id in self.inventory:
            self.inventory.remove(item_id)
            if item_id in self.worn_items:
                self.worn_items.remove(item_id)
            return True
        return False

    def wear_item(self, item_id: str) -> bool:
        """Mark item as worn. Must already be in inventory."""
        if item_id not in self.inventory:
            return False
        if item_id not in self.worn_items:
            self.worn_items.append(item_id)
        return True

    def current_weight(self) -> int:
        """Return total weight of inventory (placeholder; items track own weight)."""
        return len(self.inventory)  # simplified: each item counts as 1 unit

    # ------------------------------------------------------------------
    # Score and turn tracking
    # ------------------------------------------------------------------

    def add_score(self, points: int) -> None:
        self.score = max(0, self.score + points)

    def tick(self) -> None:
        """Advance one turn."""
        self.turns += 1

    # ------------------------------------------------------------------
    # Flags
    # ------------------------------------------------------------------

    def set_flag(self, flag: str, value: bool = True) -> None:
        self.flags[flag] = value

    def has_flag(self, flag: str) -> bool:
        return self.flags.get(flag, False)

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def heal(self, amount: int) -> int:
        """Heal player; returns actual amount healed."""
        old = self.health
        self.health = min(self.max_health, self.health + amount)
        return self.health - old

    def hurt(self, amount: int) -> bool:
        """Damage player; returns True if dead."""
        self.health = max(0, self.health - amount)
        return self.health <= 0

    def is_alive(self) -> bool:
        return self.health > 0

    # ------------------------------------------------------------------
    # NPC state management
    # ------------------------------------------------------------------

    def get_npc_state(self, npc_id: str) -> dict:
        if npc_id not in self.npc_states:
            self.npc_states[npc_id] = {}
        return self.npc_states[npc_id]

    def set_npc_flag(self, npc_id: str, key: str, value: object = True) -> None:
        self.get_npc_state(npc_id)[key] = value

    def get_npc_flag(self, npc_id: str, key: str, default: object = False) -> object:
        return self.get_npc_state(npc_id).get(key, default)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict:
        return {
            "current_room": self.current_room,
            "inventory": self.inventory,
            "worn_items": self.worn_items,
            "score": self.score,
            "turns": self.turns,
            "health": self.health,
            "max_health": self.max_health,
            "flags": self.flags,
            "npc_states": self.npc_states,
            "credits": self.credits,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        p = cls()
        p.current_room = data.get("current_room", STARTING_ROOM)
        p.inventory = data.get("inventory", [])
        p.worn_items = data.get("worn_items", [])
        p.score = data.get("score", 0)
        p.turns = data.get("turns", 0)
        p.health = data.get("health", 100)
        p.max_health = data.get("max_health", 100)
        p.flags = data.get("flags", {})
        p.npc_states = data.get("npc_states", {})
        p.credits = data.get("credits", 0)
        return p
