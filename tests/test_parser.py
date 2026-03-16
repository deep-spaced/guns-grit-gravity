"""Tests for the parser module."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from parser import Parser, Command


def test_bare_direction_north():
    p = Parser()
    cmd = p.parse("n")
    assert cmd.verb == "go"
    assert cmd.noun == "north"


def test_bare_direction_south():
    p = Parser()
    cmd = p.parse("south")
    assert cmd.verb == "go"
    assert cmd.noun == "south"


def test_go_north():
    p = Parser()
    cmd = p.parse("go north")
    assert cmd.verb == "go"
    assert cmd.noun == "north"


def test_synonym_take():
    p = Parser()
    cmd = p.parse("grab the wrench")
    assert cmd.verb == "take"
    assert cmd.noun == "wrench"


def test_synonym_examine():
    p = Parser()
    cmd = p.parse("x locker")
    assert cmd.verb == "examine"
    assert cmd.noun == "locker"


def test_use_on():
    p = Parser()
    cmd = p.parse("use wrench on hatch")
    assert cmd.verb == "use"
    assert cmd.noun == "wrench"
    assert cmd.second_noun == "hatch"


def test_talk_to():
    p = Parser()
    cmd = p.parse("talk to sheriff")
    assert cmd.verb == "talk"
    assert cmd.noun == "sheriff"


def test_inventory():
    p = Parser()
    for alias in ("i", "inv", "inventory"):
        cmd = p.parse(alias)
        assert cmd.verb == "inventory", f"Failed for alias: {alias}"


def test_empty_input():
    p = Parser()
    cmd = p.parse("")
    assert cmd.verb == ""
    assert not cmd


def test_unknown_verb():
    p = Parser()
    cmd = p.parse("flibbertigibbet the thing")
    # Unknown verb kept as-is
    assert cmd.verb == "flibbertigibbet"


def test_match_item_exact():
    p = Parser()
    candidates = {"wrench": ["wrench", "spanner", "tool"]}
    assert p.match_item("wrench", candidates) == "wrench"


def test_match_item_alias():
    p = Parser()
    candidates = {"wrench": ["wrench", "spanner", "tool"]}
    assert p.match_item("spanner", candidates) == "wrench"


def test_match_item_partial():
    p = Parser()
    candidates = {"rustbucket_spurs": ["Rustbucket Spurs", "spurs", "magnetic spurs"]}
    assert p.match_item("spur", candidates) == "rustbucket_spurs"


def test_match_item_none():
    p = Parser()
    candidates = {"wrench": ["wrench", "spanner"]}
    assert p.match_item("banana", candidates) is None


def test_enter_code():
    p = Parser()
    cmd = p.parse("enter 4719 on locker")
    assert cmd.verb == "enter"
    assert cmd.noun == "4719"
    assert cmd.second_noun == "locker"


def test_wear():
    p = Parser()
    cmd = p.parse("wear spurs")
    assert cmd.verb == "wear"
    assert cmd.noun == "spurs"


def test_help():
    p = Parser()
    cmd = p.parse("help")
    assert cmd.verb == "help"


def test_help_question_mark():
    p = Parser()
    cmd = p.parse("?")
    assert cmd.verb == "help"


def test_help_h_alias():
    p = Parser()
    cmd = p.parse("h")
    assert cmd.verb == "help"


def test_help_commands_alias():
    p = Parser()
    cmd = p.parse("commands")
    assert cmd.verb == "help"


def test_give_to_npc():
    p = Parser()
    cmd = p.parse("give codicil to sheriff")
    assert cmd.verb == "give"
    assert cmd.noun == "codicil"
    assert cmd.second_noun == "sheriff"


def test_give_offer_synonym():
    p = Parser()
    cmd = p.parse("offer codicil to holloway")
    assert cmd.verb == "give"
    assert cmd.noun == "codicil"
    assert cmd.second_noun == "holloway"


def test_give_with_articles():
    p = Parser()
    cmd = p.parse("give the codicil to the sheriff")
    assert cmd.verb == "give"
    assert cmd.noun == "codicil"
    assert cmd.second_noun == "sheriff"


def test_board_verb():
    p = Parser()
    cmd = p.parse("board ship")
    assert cmd.verb == "board"


def test_board_depart_synonym():
    p = Parser()
    cmd = p.parse("depart")
    assert cmd.verb == "board"


def test_board_launch_synonym():
    p = Parser()
    cmd = p.parse("launch")
    assert cmd.verb == "board"


def test_talk_to_still_works_after_to_split():
    """Adding 'to' as splitting preposition must not break TALK TO [npc]."""
    p = Parser()
    cmd = p.parse("talk to sheriff")
    assert cmd.verb == "talk"
    assert cmd.noun == "sheriff"
    assert cmd.second_noun == ""


def test_remove_verb():
    p = Parser()
    cmd = p.parse("remove spurs")
    assert cmd.verb == "remove"
    assert cmd.noun == "spurs"


def test_take_off_verb():
    p = Parser()
    cmd = p.parse("take off spurs")
    assert cmd.verb == "remove"
    assert cmd.noun == "spurs"


def test_doff_synonym():
    p = Parser()
    cmd = p.parse("doff spurs")
    assert cmd.verb == "remove"
