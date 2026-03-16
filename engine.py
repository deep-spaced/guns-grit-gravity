"""
engine.py — Game engine: command dispatch, world/player interaction.

The engine is the part that decides what happens when you say something.
It tries to be understanding. It does not always succeed.
"""

from __future__ import annotations
import json
from pathlib import Path

from parser import Command, Parser
from world import World
from player import Player
from items import ItemRegistry, Item
from npcs import NPCRegistry, NPC
from narrator import Narrator
from puzzles import PuzzleState
import save as save_module

DATA_DIR = Path(__file__).parent / "data"


def _load_strings() -> dict:
    path = DATA_DIR / "strings.json"
    with open(path, encoding="utf-8") as f:
        return json.load(f)


class Engine:
    """
    The game engine.

    Owns all game state, the parser, and the narrator.
    The main loop calls engine.process(raw_input) each turn.
    """

    def __init__(self, narrator=None) -> None:
        self.strings = _load_strings()
        self.world = World()
        self.player = Player()
        self.items = ItemRegistry()
        self.npcs = NPCRegistry()
        self.narrator = narrator if narrator is not None else Narrator()
        self.parser = Parser()
        self.puzzles = PuzzleState()
        self.puzzles.sync(self.player.flags)
        self._running = True
        self._pending_death: str | None = None
        self._in_dialogue: str | None = None  # npc_id if mid-conversation

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def is_running(self) -> bool:
        return self._running

    def start(self) -> None:
        """Print title screen and initial room description."""
        self.narrator.title_screen(
            self.strings["game_title"],
            self.strings["intro"],
        )
        self._look()

    def process(self, raw: str) -> None:
        """Parse and execute a player command."""
        raw = raw.strip()
        if not raw:
            return

        # If in dialogue mode, handle numeric choice
        # Allow certain meta-commands to escape dialogue
        if self._in_dialogue:
            stripped = raw.lower().strip()
            if stripped in ("quit", "q", "exit", "bye", "save", "load", "score", "help", "?"):
                self._in_dialogue = None
            elif stripped in ("leave", "bye", "farewell", "exit conversation", "done"):
                self._in_dialogue = None
                self.narrator.say("You take your leave.")
                return
            else:
                self._handle_dialogue_input(raw)
                return

        cmd = self.parser.parse(raw)

        if not cmd.verb:
            self.narrator.error(self.strings["unknown_command"])
            return

        self.player.tick()
        old_flags = dict(self.player.flags)
        self._dispatch(cmd)

        # Check for newly-earned score from puzzle events
        points = self.puzzles.check_score_events(old_flags, self.player.flags)
        if points:
            self.player.add_score(points)

        self.puzzles.sync(self.player.flags)

    # ------------------------------------------------------------------
    # Dispatch
    # ------------------------------------------------------------------

    def _dispatch(self, cmd: Command) -> None:
        match cmd.verb:
            case "look":
                self._look()
            case "go":
                self._go(cmd.noun)
            case "examine":
                self._examine(cmd.noun)
            case "take":
                self._take(cmd.noun)
            case "drop":
                self._drop(cmd.noun)
            case "inventory":
                self._inventory()
            case "talk":
                self._talk(cmd.noun)
            case "use":
                self._use(cmd.noun, cmd.second_noun)
            case "open":
                self._open(cmd.noun)
            case "close":
                self._close(cmd.noun)
            case "wear":
                self._wear(cmd.noun)
            case "remove":
                self._remove(cmd.noun)
            case "eat":
                self._eat(cmd.noun)
            case "enter":
                self._enter_code(cmd.noun, cmd.second_noun)
            case "score":
                self._score()
            case "save":
                self._save(cmd.noun or "quicksave")
            case "load":
                self._load(cmd.noun or "quicksave")
            case "footnotes":
                self._toggle_footnotes(cmd.noun)
            case "wait":
                self.narrator.say("Time passes. The universe does not hurry on your account.")
            case "hint":
                self._hint()
            case "help":
                self._help()
            case "give":
                self._give(cmd.noun, cmd.second_noun)
            case "board":
                self._board()
            case "quit":
                self._quit()
            case _:
                self.narrator.error(self.strings["unknown_command"])

    # ------------------------------------------------------------------
    # Command handlers
    # ------------------------------------------------------------------

    def _look(self, brief: bool = False) -> None:
        room = self.world.get(self.player.current_room)
        room.visited = True

        # Build item list for room description
        visible_items = self._visible_items_in_room()
        visible_npcs = self._visible_npcs_in_room()

        self.narrator.describe_room(
            name=room.name,
            description=room.description,
            footnote=room.footnote or None,
            brief=brief,
        )

        if not brief:
            # List exits
            self.narrator.list_exits(room.exits)
            self.narrator.blank()

    def _go(self, direction: str) -> None:
        if not direction:
            self.narrator.error("Go where? You'll need to specify a direction.")
            return

        room = self.world.get(self.player.current_room)
        destination_id = self.world.exit_destination(room, direction)

        if not destination_id:
            self.narrator.error(self.strings["cannot_go"])
            return

        dest = self.world.get(destination_id)
        can_enter, req_flag = self.world.can_enter(dest, self.player.flags)

        if not can_enter:
            self._blocked_exit_message(destination_id, req_flag)
            return

        self.player.current_room = destination_id
        self._look()

    def _blocked_exit_message(self, room_id: str, flag: str | None) -> None:
        """Give a context-specific blocked exit message."""
        if room_id == "maintenance_shaft":
            self.narrator.error(
                "The maintenance hatch is sealed. There's a pressure-lever mechanism "
                "that seems to require something heavy on the pad while you pull the lever. "
                "Your hands are full just holding the lever."
            )
        elif room_id == "syndicate_anteroom":
            self.narrator.error(
                "The passage is blocked by what looks like a sealed maintenance panel. "
                "Actually, looking more carefully, it's a door. A very well-disguised door. "
                "You're going to need to find the entrance."
            )
        elif room_id == "syndicate_inner_office":
            self.narrator.error(
                "The heavy door is locked. The keycard reader blinks once, expectantly."
            )
        else:
            self.narrator.error(self.strings["cannot_go"])

    def _examine(self, noun: str) -> None:
        if not noun or noun in ("room", "here", "around"):
            self._look()
            return

        if noun in ("me", "myself", "self", "you"):
            self.narrator.describe_item(self.strings["examine_self"])
            return

        # Try item
        item = self._find_item_in_context(noun)
        if item:
            detail = item.examine_detail or item.description
            self.narrator.describe_item(detail)
            if item.score_on_examine and not self.player.has_flag(f"examined_{item.item_id}"):
                self.player.add_score(item.score_on_examine)
                self.player.set_flag(f"examined_{item.item_id}")
            if item.container and item.open:
                contents = self.items.items_in_container(item.item_id)
                if contents:
                    self.narrator.say("It contains:")
                    for c in contents:
                        self.narrator.say(f"  {c.name.capitalize()}")
                else:
                    self.narrator.say(self.strings["container_empty"])
            return

        # Try NPC
        npc = self._find_npc_in_context(noun)
        if npc:
            self.narrator.describe_item(npc.examine_detail)
            return

        self.narrator.error(self.strings["item_not_here"])

    def _take(self, noun: str) -> None:
        if not noun:
            self.narrator.error("Take what?")
            return

        item = self._find_item_in_context(noun, include_containers=True)
        if not item:
            self.narrator.error(self.strings["item_not_here"])
            return

        if not item.takeable:
            self.narrator.error(self.strings["cannot_take"])
            return

        # Remove from room or container
        room = self.world.get(self.player.current_room)
        room.remove_item(item.item_id)
        if item.container_location:
            container = self.items.get(item.container_location)
            if container and item.item_id in container.contents:
                container.contents.remove(item.item_id)

        success = self.player.add_item(item.item_id, item.weight)
        if not success:
            # Put it back
            room.add_item(item.item_id)
            self.narrator.error(self.strings["cannot_take_weight"])
            return

        item.move_to_inventory()
        self.narrator.system(self.strings["item_taken"])

        if item.score_on_take and not self.player.has_flag(f"took_{item.item_id}"):
            self.player.add_score(item.score_on_take)
            self.player.set_flag(f"took_{item.item_id}")

        if item.grants_flag:
            # Don't auto-apply wearable grants; only when worn
            pass

    def _drop(self, noun: str) -> None:
        if not noun:
            self.narrator.error("Drop what?")
            return

        item = self._find_item_in_inventory(noun)
        if not item:
            self.narrator.error(self.strings["item_not_carrying"])
            return

        self.player.remove_item(item.item_id)
        room = self.world.get(self.player.current_room)
        room.add_item(item.item_id)
        item.move_to_room(self.player.current_room)
        self.narrator.system(self.strings["item_dropped"])

    def _inventory(self) -> None:
        if not self.player.inventory:
            self.narrator.inventory_list([], self.strings["inventory_empty"])
            return

        item_names = []
        for item_id in self.player.inventory:
            item = self.items.get(item_id)
            if item:
                name = item.name.capitalize()
                if self.player.is_wearing(item_id):
                    name += " (worn)"
                item_names.append(name)

        self.narrator.say(self.strings["inventory_header"])
        self.narrator.inventory_list(item_names, self.strings["inventory_empty"])

    def _talk(self, noun: str) -> None:
        """Initiate or continue conversation with an NPC."""
        if not noun:
            # No specific NPC; list who's here
            room = self.world.get(self.player.current_room)
            present = self._visible_npcs_in_room()
            if not present:
                self.narrator.error("There's nobody here to talk to.")
            else:
                names = ", ".join(n.name for n in present)
                self.narrator.say(f"You could talk to: {names}")
            return

        npc = self._find_npc_in_context(noun)
        if not npc:
            self.narrator.error(self.strings["npc_not_here"])
            return

        self._start_dialogue(npc)

    def _start_dialogue(self, npc: NPC) -> None:
        """Show NPC greeting and topic list."""
        self.narrator.npc_speaks(npc.name, npc.greeting)

        available = npc.available_topics(self.player.flags)
        if available:
            options = [(i + 1, self._topic_label(t.key)) for i, t in enumerate(available)]
            options.append((len(options) + 1, "Leave"))
            self.narrator.dialogue_options(options)
            self._in_dialogue = npc.npc_id
            self._dialogue_topics = available
        else:
            self.narrator.say("They don't seem to have more to say right now.")

    def _topic_label(self, key: str) -> str:
        """Convert a topic key like 'codicil' or 'unknown_person' to display text."""
        return key.replace("_", " ").capitalize()

    def _handle_dialogue_input(self, raw: str) -> None:
        """Handle player input while in a dialogue menu."""
        npc_id = self._in_dialogue
        npc = self.npcs.get(npc_id)
        if not npc:
            self._in_dialogue = None
            return

        available = getattr(self, "_dialogue_topics", [])
        leave_idx = len(available) + 1

        # Try numeric selection
        try:
            choice = int(raw.strip())
        except ValueError:
            # Try to match topic by keyword
            topic_key = self.npcs.find_topic_for_noun(npc, raw)
            if topic_key:
                topic = npc.get_topic(topic_key)
                if topic:
                    self._handle_topic(npc, topic)
                    return
            self.narrator.error("Choose a number from the list, or type a topic.")
            return

        if choice == leave_idx:
            self._in_dialogue = None
            self.narrator.say("You take your leave.")
            return

        if 1 <= choice <= len(available):
            topic = available[choice - 1]
            self._handle_topic(npc, topic)
        else:
            self.narrator.error("That's not a valid option.")

    def _handle_topic(self, npc: NPC, topic: "DialogueTopic") -> None:
        """Process a dialogue topic selection."""
        # Credit check
        if topic.requires_credits > 0 and self.player.credits < topic.requires_credits:
            self.narrator.say(
                f"That information costs {topic.requires_credits} credits. "
                f"You have {self.player.credits}."
            )
            return

        if topic.requires_credits > 0:
            self.player.credits -= topic.requires_credits

        self.narrator.npc_speaks(npc.name, topic.text)

        if topic.sets_flag:
            self.player.set_flag(topic.sets_flag)

        if topic.gives_item:
            item = self.items.get(topic.gives_item)
            if item and not self.player.has_item(topic.gives_item):
                if self.player.add_item(topic.gives_item, item.weight):
                    item.move_to_inventory()
                    self.narrator.say(f"You receive: {item.name.capitalize()}.")
                    if item.score_on_take and not self.player.has_flag(f"took_{item.item_id}"):
                        self.player.add_score(item.score_on_take)
                        self.player.set_flag(f"took_{item.item_id}")

        # Show updated topic list
        available = npc.available_topics(self.player.flags)
        if available:
            options = [(i + 1, self._topic_label(t.key)) for i, t in enumerate(available)]
            options.append((len(options) + 1, "Leave"))
            self.narrator.dialogue_options(options)
            self._dialogue_topics = available
        else:
            self._in_dialogue = None

    def _use(self, noun: str, second_noun: str) -> None:
        if not noun:
            self.narrator.error("Use what?")
            return

        item = self._find_item_in_inventory(noun)
        if not item:
            # Try room items
            item = self._find_item_in_room(noun)
        if not item:
            self.narrator.error(self.strings["item_not_here"])
            return

        if second_noun:
            # USE item ON target
            self._use_on(item, second_noun)
        else:
            # Generic use
            if item.heals and not second_noun:
                healed = self.player.heal(item.heals)
                if healed > 0:
                    self.narrator.say(f"You use the {item.name}. You feel somewhat better (+{healed} health).")
                else:
                    self.narrator.say("You're already at full health. The frontier is occasionally kind.")
                if self.player.has_item(item.item_id) and item.weight == 0:
                    self.player.remove_item(item.item_id)
            elif item.use_text:
                self.narrator.say(item.use_text)
            else:
                self.narrator.say(f"You examine the {item.name} but aren't sure what to do with it right now.")

    def _use_on(self, item: Item, target_noun: str) -> None:
        """Use an item on a target."""
        # Find target
        target = self._find_item_in_context(target_noun)
        if not target:
            self.narrator.error(f"You don't see '{target_noun}' to use that on.")
            return

        effect_data = item.use_on.get(target.item_id)
        if not effect_data:
            # Try reverse: check if target has use_on entry for item
            self.narrator.say(f"Using the {item.name} on the {target.name} doesn't seem to accomplish anything.")
            return

        # Execute effect
        effect = effect_data.get("effect", "")
        text = effect_data.get("text", "")
        success = effect_data.get("success", True)

        if text:
            self.narrator.say(text)

        if success and effect:
            if effect.startswith("set_flag:"):
                flag_name = effect[len("set_flag:"):]
                self.player.set_flag(flag_name)
                # Special: opening hatch unlocks the maintenance shaft
                if flag_name == "maintenance_hatch_open":
                    self.player.set_flag("found_syndicate")  # hatch leads to shaft leads to Syndicate

    def _open(self, noun: str) -> None:
        if not noun:
            self.narrator.error("Open what?")
            return

        item = self._find_item_in_context(noun)
        if not item:
            # Check exits — player might say "open door" meaning go through it
            self.narrator.error(self.strings["item_not_here"])
            return

        if not item.container and item.lock_mechanism is None:
            self.narrator.error(f"You can't open the {item.name}.")
            return

        if item.open:
            self.narrator.error(self.strings["already_open"])
            return

        if item.locked:
            if item.lock_mechanism == "pressure_lever":
                self.narrator.say(
                    "The hatch has a pressure-lever mechanism — you need something "
                    "heavy on the pressure pad while you pull the lever. "
                    "Try using a heavy item on the hatch."
                )
            elif item.lock_mechanism == "keycard":
                self.narrator.say(
                    "The door requires a keycard. The reader blinks patiently."
                )
                # Check if player has the keycard
                if self.player.has_item("syndicate_keycard"):
                    item.locked = False
                    item.open = True
                    self.player.set_flag("syndicate_door_open")
                    self.narrator.say("You slide the Syndicate keycard through the reader. The door opens.")
            else:
                self.narrator.say(self.strings["locked"])
            return

        item.open = True
        self.narrator.say(self.strings["opened"])

        if item.contents:
            contents = self.items.items_in_container(item.item_id)
            if contents:
                self.narrator.say("Inside you find:")
                for c in contents:
                    self.narrator.say(f"  {c.name.capitalize()}")

    def _close(self, noun: str) -> None:
        if not noun:
            self.narrator.error("Close what?")
            return

        item = self._find_item_in_context(noun)
        if not item or not item.container:
            self.narrator.error(f"You can't close that.")
            return

        if not item.open:
            self.narrator.error(self.strings["already_closed"])
            return

        item.open = False
        self.narrator.say(self.strings["already_closed"].replace("already ", ""))

    def _wear(self, noun: str) -> None:
        if not noun:
            self.narrator.error("Wear what?")
            return

        item = self._find_item_in_inventory(noun)
        if not item:
            self.narrator.error(self.strings["item_not_carrying"])
            return

        if not item.wearable:
            self.narrator.say(f"You can't wear the {item.name}. The frontier has standards, but not that kind.")
            return

        if self.player.is_wearing(item.item_id):
            self.narrator.error(self.strings["item_already_worn"])
            return

        self.player.wear_item(item.item_id)
        item.worn = True
        self.narrator.say(self.strings["item_worn"].replace("{item}", item.name))

        if item.grants_flag:
            self.player.set_flag(item.grants_flag)

    def _remove(self, noun: str) -> None:
        if not noun:
            self.narrator.error("Take off what?")
            return

        item = self._find_item_in_inventory(noun)
        if not item:
            self.narrator.error(self.strings["item_not_carrying"])
            return

        if not self.player.is_wearing(item.item_id):
            self.narrator.say(f"You're not wearing the {item.name}.")
            return

        self.player.worn_items.remove(item.item_id)
        item.worn = False
        if item.grants_flag:
            self.player.set_flag(item.grants_flag, False)
        self.narrator.say(f"You take off the {item.name}.")

    def _eat(self, noun: str) -> None:
        if not noun:
            self.narrator.error("Eat or drink what?")
            return

        item = self._find_item_in_inventory(noun)
        if not item:
            item = self._find_item_in_room(noun)
        if not item:
            self.narrator.error(self.strings["item_not_here"])
            return

        if item.heals:
            if self.player.has_item(item.item_id):
                self.player.remove_item(item.item_id)
            else:
                room = self.world.get(self.player.current_room)
                room.remove_item(item.item_id)
            item.location = None
            healed = self.player.heal(item.heals)
            self.narrator.say(f"You eat the {item.name}. It tastes like function over form. (+{healed} health)")
        else:
            self.narrator.say(f"You're not sure that's meant to be eaten. The {item.name} disagrees with the concept.")

    def _enter_code(self, noun: str, second_noun: str) -> None:
        """Handle ENTER [code] ON [item]."""
        if not noun:
            self.narrator.error("Enter what code?")
            return

        code = noun.replace(" ", "")

        if second_noun:
            target = self._find_item_in_context(second_noun)
        else:
            # Try to find a lockable item in the room
            room = self.world.get(self.player.current_room)
            target = None
            for item_id in room.item_ids:
                item = self.items.get(item_id)
                if item and item.lock_code:
                    target = item
                    break

        if not target:
            self.narrator.error("There's nothing here that accepts a code.")
            return

        if not target.lock_code:
            self.narrator.say(f"The {target.name} doesn't use a code combination.")
            return

        if code == target.lock_code:
            target.locked = False
            target.open = True
            self.narrator.say(self.strings["opened"])
            if target.contents:
                contents = self.items.items_in_container(target.item_id)
                if contents:
                    self.narrator.say("Inside you find:")
                    for c in contents:
                        self.narrator.say(f"  {c.name.capitalize()}")
        else:
            self.narrator.error(self.strings["wrong_code"])

    def _score(self) -> None:
        max_score = self.strings["max_score"]
        rank = self._get_rank()
        self.narrator.score_display(self.player.score, max_score, self.player.turns, rank, self.player.credits)

    def _get_rank(self) -> str:
        ranks = self.strings["score_ranks"]
        rank = "Lost"
        for threshold, label in sorted(ranks.items(), key=lambda x: int(x[0])):
            if self.player.score >= int(threshold):
                rank = label
        return rank

    def _save(self, name: str) -> None:
        success = save_module.save_game(
            name=name,
            player_dict=self.player.to_dict(),
            world_dict=self.world.to_dict(),
            items_dict=self.items.to_dict(),
            npcs_dict=self.npcs.to_dict(),
        )
        if success:
            self.narrator.system(self.strings["save_success"].replace("{name}", name))
        else:
            self.narrator.error(self.strings["save_failed"])

    def _load(self, name: str) -> None:
        data = save_module.load_game(name)
        if not data:
            self.narrator.error(self.strings["load_failed"])
            return

        self.player = Player.from_dict(data["player"])
        self.world.from_dict(data.get("world", {}))
        self.items.from_dict(data.get("items", {}))
        self.npcs.from_dict(data.get("npcs", {}))
        self.puzzles.sync(self.player.flags)
        self.narrator.system(self.strings["load_success"])
        self._look()

    def _toggle_footnotes(self, arg: str) -> None:
        if arg.lower() in ("on", "enable", "yes"):
            self.narrator.set_footnotes(True)
            self.narrator.system(self.strings["footnotes_on"])
        elif arg.lower() in ("off", "disable", "no"):
            self.narrator.set_footnotes(False)
            self.narrator.system(self.strings["footnotes_off"])
        else:
            enabled = self.narrator.toggle_footnotes()
            msg = self.strings["footnotes_on"] if enabled else self.strings["footnotes_off"]
            self.narrator.system(msg)

    def _give(self, noun: str, second_noun: str) -> None:
        """GIVE [item] TO [npc]."""
        if not noun:
            self.narrator.error("Give what?")
            return
        if not second_noun:
            self.narrator.error(self.strings["give_no_target"])
            return

        item = self._find_item_in_inventory(noun)
        if not item:
            self.narrator.error(self.strings["cannot_give"])
            return

        npc = self._find_npc_in_context(second_noun)
        if not npc:
            self.narrator.error(self.strings["give_not_here"])
            return

        # Revolver return
        if item.item_id == "plasma_revolver" and npc.npc_id == "sheriff_vasquez":
            self.player.remove_item(item.item_id)
            self.player.credits += 200
            self.player.set_flag("revolver_returned")
            self.narrator.npc_speaks(
                npc.name,
                "Vasquez stares at the revolver for a moment that has several things in it.\n\n"
                "\"Where did you find this.\" It comes out flat, not a question. She takes it, "
                "checks the cylinder with the practiced motion of someone who has done it ten "
                "thousand times, and sets it on the desk.\n\n"
                "\"My father gave me that.\" A pause. \"Two hundred credits. Don't argue.\""
            )
            return

        # Codicil-specific endings
        if item.item_id == "quantum_codicil":
            if npc.npc_id == "sheriff_vasquez":
                self.player.remove_item(item.item_id)
                self.player.credits += 2000
                self.player.set_flag("ending_sheriff")
                self.player.set_flag("game_complete")
                self.player.add_score(25)  # game_complete bonus
                self._trigger_ending("sheriff")
                return
            elif npc.npc_id == "director_holloway":
                self.player.remove_item(item.item_id)
                self.player.credits += 5000
                self.player.set_flag("ending_syndicate")
                self.player.set_flag("game_complete")
                self.player.add_score(25)
                self._trigger_ending("syndicate")
                return
            elif npc.npc_id == "augusto_claim":
                self.player.remove_item(item.item_id)
                self.player.set_flag("ending_brotherhood")
                self.player.set_flag("game_complete")
                self.player.add_score(25)
                self._trigger_ending("brotherhood")
                return

        self.narrator.say(self.strings["give_no_effect"])

    def _board(self) -> None:
        """Board the Bellerophon — triggers the 'keep' ending if player has the Codicil."""
        if self.player.current_room != "docking_bay_7":
            self.narrator.error("Your ship isn't here.")
            return

        if not self.player.has_item("quantum_codicil"):
            self.narrator.say(self.strings["board_no_codicil"])
            return

        self.player.set_flag("ending_keep")
        self.player.set_flag("game_complete")
        self.player.add_score(25)
        self._trigger_ending("keep")

    def _trigger_ending(self, ending_type: str) -> None:
        """Print the ending screen and halt the game."""
        rank = self._get_rank()
        lines = self.strings["endings"][ending_type]
        for line in lines:
            formatted = (
                line.replace("{score}", str(self.player.score))
                    .replace("{max_score}", str(self.strings["max_score"]))
                    .replace("{rank}", rank)
            )
            self.narrator.say(formatted, wrap=False)
        self._running = False

    def _help(self) -> None:
        for line in self.strings["help_text"]:
            self.narrator.say(line, wrap=False)

    def _hint(self) -> None:
        """Provide a context-sensitive hint."""
        room_id = self.player.current_room
        flags = self.player.flags

        if room_id == "docking_bay_7" and not flags.get("maintenance_hatch_open"):
            self.narrator.say(
                "The maintenance hatch has a pressure-lever mechanism. "
                "You need something heavy to hold the pressure pad down "
                "while you pull the lever. Look around the maintenance shaft "
                "for tools — but first you need to get it open."
            )
        elif not flags.get("working_with_sheriff"):
            self.narrator.say(
                "Talk to Sheriff Vasquez in her office. She's got a case and "
                "she needs someone who isn't already on every faction's list. "
                "That might be you."
            )
        elif not flags.get("clem_told_you"):
            self.narrator.say(
                "Clem Duster at the Rusty Spur sees everything that happens on "
                "this station. Information has a price, but it's worth paying."
            )
        elif not flags.get("found_syndicate"):
            self.narrator.say(
                "The maintenance shaft connects to more than just the docking bay. "
                "You need to get that hatch open first. There's a wrench somewhere "
                "in the maintenance shaft that could help — if you can get there."
            )
        else:
            self.narrator.say(
                "You've come a long way. Trust what you know. Talk to everyone again. "
                "The answer is closer than it feels."
            )

    def _quit(self) -> None:
        self.narrator.say(self.strings["quit_confirm"])
        try:
            response = input().strip().lower()
        except (EOFError, KeyboardInterrupt):
            response = "yes"

        if response in ("yes", "y"):
            self.narrator.quit_message(self.strings["quit_message"])
            self._running = False

    # ------------------------------------------------------------------
    # Lookup helpers
    # ------------------------------------------------------------------

    def _visible_items_in_room(self) -> list[Item]:
        room = self.world.get(self.player.current_room)
        return [self.items.get(iid) for iid in room.item_ids if self.items.get(iid)]

    def _visible_npcs_in_room(self) -> list[NPC]:
        room = self.world.get(self.player.current_room)
        return [self.npcs.get(nid) for nid in room.npc_ids if self.npcs.get(nid)]

    def _find_item_in_context(
        self, noun: str, include_containers: bool = False
    ) -> Item | None:
        """
        Find an item by noun in: player inventory, current room,
        and (if include_containers) open containers in the room.
        """
        room = self.world.get(self.player.current_room)
        candidate_ids = list(self.player.inventory) + list(room.item_ids)

        if include_containers:
            for item_id in room.item_ids:
                container = self.items.get(item_id)
                if container and container.container and container.open:
                    candidate_ids.extend(container.contents)

        name_map = self.items.name_map(candidate_ids)
        match_id = self.parser.match_item(noun, name_map)
        if match_id:
            return self.items.get(match_id)
        return None

    def _find_item_in_inventory(self, noun: str) -> Item | None:
        name_map = self.items.name_map(self.player.inventory)
        match_id = self.parser.match_item(noun, name_map)
        if match_id:
            return self.items.get(match_id)
        return None

    def _find_item_in_room(self, noun: str) -> Item | None:
        room = self.world.get(self.player.current_room)
        name_map = self.items.name_map(room.item_ids)
        match_id = self.parser.match_item(noun, name_map)
        if match_id:
            return self.items.get(match_id)
        return None

    def _find_npc_in_context(self, noun: str) -> NPC | None:
        room = self.world.get(self.player.current_room)
        name_map = self.npcs.name_map(room.npc_ids)
        match_id = self.parser.match_item(noun, name_map)
        if match_id:
            return self.npcs.get(match_id)
        return None
