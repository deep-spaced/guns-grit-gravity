"""Tests for the world module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from world import World


def test_load_rooms():
    w = World()
    room = w.get("docking_bay_7")
    assert room is not None
    assert room.name == "Docking Bay 7"


def test_exits():
    w = World()
    room = w.get("docking_bay_7")
    assert "north" in room.exits
    assert room.exits["north"] == "main_concourse"


def test_room_items():
    w = World()
    room = w.get("docking_bay_7")
    assert "battered_locker" in room.item_ids
    assert "maintenance_hatch" in room.item_ids


def test_room_npcs():
    w = World()
    room = w.get("main_concourse")
    assert "deputy_tack7" in room.npc_ids


def test_add_remove_item():
    w = World()
    room = w.get("docking_bay_7")
    room.add_item("test_item")
    assert room.has_item("test_item")
    room.remove_item("test_item")
    assert not room.has_item("test_item")


def test_exit_destination():
    w = World()
    room = w.get("docking_bay_7")
    assert w.exit_destination(room, "north") == "main_concourse"
    assert w.exit_destination(room, "east") is None


def test_can_enter_no_flag():
    w = World()
    room = w.get("main_concourse")
    can, req = w.can_enter(room, {})
    assert can is True
    assert req is None


def test_can_enter_requires_flag_missing():
    w = World()
    room = w.get("maintenance_shaft")
    can, req = w.can_enter(room, {})
    assert can is False
    assert req == "maintenance_hatch_open"


def test_can_enter_requires_flag_present():
    w = World()
    room = w.get("maintenance_shaft")
    can, req = w.can_enter(room, {"maintenance_hatch_open": True})
    assert can is True


def test_all_rooms():
    w = World()
    rooms = w.all_rooms()
    assert len(rooms) >= 8  # We defined at least 8 rooms


def test_serialization():
    w = World()
    room = w.get("docking_bay_7")
    room.visited = True
    data = w.to_dict()
    assert data["docking_bay_7"]["visited"] is True

    # Load into fresh world
    w2 = World()
    w2.from_dict(data)
    assert w2.get("docking_bay_7").visited is True
