"""
save.py — Game save/load system using JSON.

Saves go to ~/.guns_grit_gravity/saves/.
The format is human-readable, which permits both debugging and mild cheating.
The narrator will acknowledge suspiciously good save states.
"""

from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime

SAVE_DIR = Path.home() / ".guns_grit_gravity" / "saves"


def _ensure_save_dir() -> None:
    SAVE_DIR.mkdir(parents=True, exist_ok=True)


def save_game(name: str, player_dict: dict, world_dict: dict, items_dict: dict, npcs_dict: dict) -> bool:
    """
    Serialize game state to JSON.
    Returns True on success, False on failure.
    """
    _ensure_save_dir()
    slot_path = SAVE_DIR / f"{_sanitize(name)}.json"

    save_data = {
        "meta": {
            "save_name": name,
            "saved_at": datetime.now().isoformat(),
            "version": 1,
        },
        "player": player_dict,
        "world": world_dict,
        "items": items_dict,
        "npcs": npcs_dict,
    }

    try:
        with open(slot_path, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        return True
    except OSError:
        return False


def load_game(name: str) -> dict | None:
    """
    Load game state from JSON.
    Returns the save data dict, or None on failure.
    """
    slot_path = SAVE_DIR / f"{_sanitize(name)}.json"

    if not slot_path.exists():
        return None

    try:
        with open(slot_path, encoding="utf-8") as f:
            data = json.load(f)
        return data
    except (OSError, json.JSONDecodeError):
        return None


def list_saves() -> list[str]:
    """Return a list of save names."""
    _ensure_save_dir()
    return [
        p.stem
        for p in sorted(SAVE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    ]


def _sanitize(name: str) -> str:
    """Make a save name safe for use as a filename."""
    safe = "".join(c for c in name if c.isalnum() or c in "-_ ")
    return safe.strip().replace(" ", "_") or "quicksave"
