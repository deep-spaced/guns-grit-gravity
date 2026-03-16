"""Tests for the engine module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from unittest.mock import patch
from engine import Engine


def _make_engine():
    """Return a fresh Engine with narrator output suppressed."""
    e = Engine()
    e.narrator.say = lambda *a, **kw: None
    e.narrator.system = lambda *a, **kw: None
    e.narrator.error = lambda *a, **kw: None
    return e


def test_help_dispatch_calls_help_method():
    """HELP command should invoke _help, not fall through to unknown_command."""
    e = _make_engine()
    called = []
    e._help = lambda: called.append(True)
    e.process("help")
    assert called, "HELP command did not dispatch to _help()"


def test_help_question_mark_dispatch():
    """? alias should also dispatch to _help."""
    e = _make_engine()
    called = []
    e._help = lambda: called.append(True)
    e.process("?")
    assert called, "? alias did not dispatch to _help()"


def test_help_outputs_help_text():
    """_help() should print lines from strings['help_text']."""
    e = _make_engine()
    output = []
    e.narrator.say = lambda text, **kw: output.append(text)
    e._help()
    assert output, "_help() produced no output"
    assert any("LOOK" in line for line in output), "help_text missing LOOK command"
    assert any("QUIT" in line for line in output), "help_text missing QUIT command"


def test_help_does_not_trigger_unknown_command():
    """HELP must not produce an unknown_command error response."""
    e = _make_engine()
    errors = []
    e.narrator.error = lambda text, **kw: errors.append(text)
    # Patch _help so it doesn't print anything
    e._help = lambda: None
    e.process("help")
    assert not errors, f"HELP triggered error: {errors}"


# ------------------------------------------------------------------
# GIVE verb tests
# ------------------------------------------------------------------

def _engine_with_codicil(room="sheriffs_office"):
    """Engine with codicil in inventory and player in specified room."""
    e = _make_engine()
    e.player.current_room = room
    e.player.inventory.append("quantum_codicil")
    return e


def test_give_codicil_to_sheriff_triggers_ending():
    e = _engine_with_codicil("sheriffs_office")
    e._trigger_ending = lambda t: None  # suppress output
    e.process("give codicil to sheriff")
    assert e.player.has_flag("ending_sheriff"), "ending_sheriff flag not set"
    assert e.player.has_flag("game_complete"), "game_complete flag not set"
    assert not e.player.has_item("quantum_codicil"), "codicil still in inventory"


def test_give_codicil_to_holloway_triggers_ending():
    e = _engine_with_codicil("syndicate_inner_office")
    e.player.set_flag("syndicate_door_open")
    e._trigger_ending = lambda t: None
    e.process("give codicil to holloway")
    assert e.player.has_flag("ending_syndicate")
    assert e.player.has_flag("game_complete")
    assert not e.player.has_item("quantum_codicil")


def test_give_codicil_to_augusto_triggers_ending():
    e = _engine_with_codicil("rusty_spur")
    e._trigger_ending = lambda t: None
    e.process("give codicil to augusto")
    assert e.player.has_flag("ending_brotherhood")
    assert e.player.has_flag("game_complete")
    assert not e.player.has_item("quantum_codicil")


def test_give_wrong_item_no_ending():
    e = _make_engine()
    e.player.current_room = "sheriffs_office"
    e.player.inventory.append("wrench")
    output = []
    e.narrator.say = lambda t, **kw: output.append(t)
    e.process("give wrench to sheriff")
    assert not e.player.has_flag("ending_sheriff")
    assert not e.is_running() is False  # game still running


def test_give_without_item_errors():
    e = _make_engine()
    e.player.current_room = "sheriffs_office"
    errors = []
    e.narrator.error = lambda t, **kw: errors.append(t)
    e.process("give codicil to sheriff")
    assert errors, "Expected error when not carrying item"


def test_give_npc_not_present_errors():
    e = _engine_with_codicil("docking_bay_7")
    errors = []
    e.narrator.error = lambda t, **kw: errors.append(t)
    e.process("give codicil to sheriff")  # sheriff not in docking bay
    assert errors, "Expected error when NPC not in room"


# ------------------------------------------------------------------
# BOARD / keep ending tests
# ------------------------------------------------------------------

def test_board_with_codicil_in_docking_bay_triggers_keep():
    e = _engine_with_codicil("docking_bay_7")
    e._trigger_ending = lambda t: None
    e.process("board")
    assert e.player.has_flag("ending_keep")
    assert e.player.has_flag("game_complete")


def test_board_without_codicil_does_not_end_game():
    e = _make_engine()
    e.player.current_room = "docking_bay_7"
    output = []
    e.narrator.say = lambda t, **kw: output.append(t)
    e.process("board")
    assert not e.player.has_flag("ending_keep")
    assert e.is_running()
    assert output, "Expected flavor text when boarding without codicil"


def test_board_wrong_room_errors():
    e = _engine_with_codicil("sheriffs_office")
    errors = []
    e.narrator.error = lambda t, **kw: errors.append(t)
    e.process("board")
    assert errors, "Expected error when boarding from wrong room"
    assert not e.player.has_flag("ending_keep")


# ------------------------------------------------------------------
# Augusto NPC tests
# ------------------------------------------------------------------

def test_augusto_present_in_rusty_spur():
    e = _make_engine()
    e.player.current_room = "rusty_spur"
    npcs = e._visible_npcs_in_room()
    npc_ids = [n.npc_id for n in npcs]
    assert "augusto_claim" in npc_ids, "Augusto not found in Rusty Spur"


def test_augusto_not_present_in_docking_bay():
    e = _make_engine()
    e.player.current_room = "docking_bay_7"
    npcs = e._visible_npcs_in_room()
    npc_ids = [n.npc_id for n in npcs]
    assert "augusto_claim" not in npc_ids


# ------------------------------------------------------------------
# Ending output tests
# ------------------------------------------------------------------

def test_trigger_ending_stops_game():
    e = _make_engine()
    e.narrator.say = lambda *a, **kw: None
    e._trigger_ending("sheriff")
    assert not e.is_running(), "Game should stop after ending"


def test_all_four_endings_produce_output():
    for ending in ("sheriff", "syndicate", "brotherhood", "keep"):
        e = _make_engine()
        output = []
        e.narrator.say = lambda t, **kw: output.append(t)
        e._trigger_ending(ending)
        assert output, f"Ending '{ending}' produced no output"


# ------------------------------------------------------------------
# REMOVE verb tests
# ------------------------------------------------------------------

def test_remove_worn_item():
    e = _make_engine()
    e.player.inventory.append("rustbucket_spurs")
    e.player.wear_item("rustbucket_spurs")
    e.player.set_flag("wearing_spurs")
    e.narrator.say = lambda *a, **kw: None
    e.process("remove spurs")
    assert not e.player.is_wearing("rustbucket_spurs"), "Spurs still worn after remove"
    assert not e.player.has_flag("wearing_spurs"), "wearing_spurs flag not cleared"


def test_remove_not_wearing():
    e = _make_engine()
    e.player.inventory.append("rustbucket_spurs")
    output = []
    e.narrator.say = lambda t, **kw: output.append(t)
    e.process("remove spurs")
    assert any("not wearing" in line.lower() for line in output)
    assert "rustbucket_spurs" in e.player.inventory


def test_remove_not_carrying():
    e = _make_engine()
    errors = []
    e.narrator.error = lambda t, **kw: errors.append(t)
    e.process("remove spurs")
    assert errors


def test_take_off_synonym():
    e = _make_engine()
    e.player.inventory.append("rustbucket_spurs")
    e.player.wear_item("rustbucket_spurs")
    e.narrator.say = lambda *a, **kw: None
    e.process("take off spurs")
    assert not e.player.is_wearing("rustbucket_spurs")


# ------------------------------------------------------------------
# Credits system tests
# ------------------------------------------------------------------

def test_player_starts_with_credits():
    from player import Player
    p = Player()
    assert p.credits > 0, "Player should start with credits to afford Clem's info"


def test_player_starts_with_enough_for_clem():
    from player import Player
    p = Player()
    assert p.credits >= 50, "Player needs at least 50 credits for Clem's codicil info"


def test_sheriff_ending_awards_credits():
    e = _engine_with_codicil("sheriffs_office")
    starting_credits = e.player.credits
    e._trigger_ending = lambda t: None
    e.process("give codicil to sheriff")
    assert e.player.credits == starting_credits + 2000


def test_syndicate_ending_awards_credits():
    e = _engine_with_codicil("syndicate_inner_office")
    e.player.set_flag("syndicate_door_open")
    starting_credits = e.player.credits
    e._trigger_ending = lambda t: None
    e.process("give codicil to holloway")
    assert e.player.credits == starting_credits + 5000


def test_score_command_shows_credits():
    e = _make_engine()
    output = []
    e.narrator.say = lambda t, **kw: output.append(t)
    e.narrator.blank = lambda: None
    e.process("score")
    assert any("credits" in line.lower() for line in output), "SCORE does not show credits"


# ------------------------------------------------------------------
# Plasma revolver tests
# ------------------------------------------------------------------

def test_plasma_revolver_in_maintenance_shaft():
    e = _make_engine()
    e.player.current_room = "maintenance_shaft"
    e.player.set_flag("maintenance_hatch_open")
    items = e._visible_items_in_room()
    item_ids = [i.item_id for i in items]
    assert "plasma_revolver" in item_ids, "Plasma revolver not found in maintenance shaft"


def test_give_revolver_to_sheriff_awards_credits():
    e = _make_engine()
    e.player.current_room = "sheriffs_office"
    e.player.inventory.append("plasma_revolver")
    e.narrator.npc_speaks = lambda *a, **kw: None
    starting_credits = e.player.credits
    e.process("give revolver to sheriff")
    assert e.player.credits == starting_credits + 200
    assert e.player.has_flag("revolver_returned")
    assert not e.player.has_item("plasma_revolver")


def test_give_revolver_to_wrong_npc():
    e = _make_engine()
    e.player.current_room = "rusty_spur"
    e.player.inventory.append("plasma_revolver")
    output = []
    e.narrator.say = lambda t, **kw: output.append(t)
    e.process("give revolver to augusto")
    assert not e.player.has_flag("revolver_returned")
    assert e.player.has_item("plasma_revolver"), "Revolver should stay with player"


# ------------------------------------------------------------------
# Stimulant tabs tests
# ------------------------------------------------------------------

def test_stimulant_tabs_heal():
    e = _make_engine()
    e.player.health = 50
    e.player.inventory.append("stimulant_tabs")
    e.narrator.say = lambda *a, **kw: None
    e.process("use stimulants")
    assert e.player.health > 50, "Stimulant tabs did not heal player"


def test_stimulant_tabs_have_heals_value():
    e = _make_engine()
    item = e.items.get("stimulant_tabs")
    assert item is not None
    assert item.heals and item.heals > 0, "stimulant_tabs missing heals value"
