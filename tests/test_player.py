"""Tests for the player module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from player import Player


def test_initial_state():
    p = Player()
    assert p.current_room == "docking_bay_7"
    assert p.inventory == []
    assert p.score == 0
    assert p.turns == 0
    assert p.health == 100


def test_add_remove_item():
    p = Player()
    assert p.add_item("wrench", weight=3)
    assert p.has_item("wrench")
    assert p.remove_item("wrench")
    assert not p.has_item("wrench")


def test_score():
    p = Player()
    p.add_score(10)
    assert p.score == 10
    p.add_score(5)
    assert p.score == 15


def test_flags():
    p = Player()
    assert not p.has_flag("test_flag")
    p.set_flag("test_flag")
    assert p.has_flag("test_flag")
    p.set_flag("test_flag", False)
    assert not p.has_flag("test_flag")


def test_wear_item():
    p = Player()
    p.add_item("spurs")
    assert p.wear_item("spurs")
    assert p.is_wearing("spurs")


def test_cannot_wear_uncarried_item():
    p = Player()
    assert not p.wear_item("spurs")


def test_heal():
    p = Player()
    p.health = 80
    healed = p.heal(15)
    assert healed == 15
    assert p.health == 95


def test_heal_cap():
    p = Player()
    healed = p.heal(50)
    assert p.health == 100
    assert healed == 0


def test_hurt():
    p = Player()
    dead = p.hurt(50)
    assert not dead
    assert p.health == 50


def test_hurt_death():
    p = Player()
    dead = p.hurt(100)
    assert dead
    assert p.health == 0
    assert not p.is_alive()


def test_tick():
    p = Player()
    p.tick()
    p.tick()
    assert p.turns == 2


def test_serialization():
    p = Player()
    p.current_room = "rusty_spur"
    p.add_item("wrench")
    p.score = 42
    p.set_flag("working_with_sheriff")

    data = p.to_dict()
    p2 = Player.from_dict(data)

    assert p2.current_room == "rusty_spur"
    assert p2.has_item("wrench")
    assert p2.score == 42
    assert p2.has_flag("working_with_sheriff")


def test_npc_state():
    p = Player()
    p.set_npc_flag("sheriff_vasquez", "greeted", True)
    assert p.get_npc_flag("sheriff_vasquez", "greeted") is True
    assert p.get_npc_flag("sheriff_vasquez", "unknown_key", "default") == "default"
