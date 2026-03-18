/**
 * engine.js — Game engine: command dispatch and world interaction.
 * Port of engine.py. Runs entirely in the browser.
 */

import stringsData from '@data/strings.json';
import { Parser }       from './parser.js';
import { World }        from './world.js';
import { Player }       from './player.js';
import { ItemRegistry } from './items.js';
import { NPCRegistry }  from './npcs.js';
import { Narrator }     from './narrator.js';
import { PuzzleState }  from './puzzles.js';
import * as save        from './save.js';

export class Engine {
  constructor(narrator = null) {
    this.strings   = stringsData;
    this.world     = new World();
    this.player    = new Player();
    this.items     = new ItemRegistry();
    this.npcs      = new NPCRegistry();
    this.narrator  = narrator ?? new Narrator();
    this.parser    = new Parser();
    this.puzzles   = new PuzzleState();
    this.puzzles.sync(this.player.flags);
    this._running       = true;
    this._inDialogue    = null;   // npc_id if mid-conversation
    this._dialogueTopics= [];
    this._pendingQuit   = false;
  }

  isRunning() { return this._running; }

  start() {
    this.narrator.titleScreen(this.strings.game_title, this.strings.intro);
    this._look();
  }

  process(raw) {
    raw = raw.trim();
    if (!raw) return;

    // Quit confirmation
    if (this._pendingQuit) {
      const r = raw.toLowerCase();
      this._pendingQuit = false;
      if (r === 'yes' || r === 'y') {
        this.narrator.quitMessage(this.strings.quit_message);
        this._running = false;
      } else {
        this.narrator.say('Cancelled. The frontier persists.');
      }
      return;
    }

    // Dialogue mode
    if (this._inDialogue) {
      const low = raw.toLowerCase().trim();
      if (['quit','q','exit','bye','save','load','score','help','?'].includes(low)) {
        this._inDialogue = null;
      } else if (['leave','farewell','done'].includes(low)) {
        this._inDialogue = null;
        this.narrator.say('You take your leave.');
        return;
      } else {
        this._handleDialogueInput(raw);
        return;
      }
    }

    const cmd = this.parser.parse(raw);
    if (!cmd.verb) { this.narrator.error(this.strings.unknown_command); return; }

    // Intercept quit to avoid needing blocking input()
    if (cmd.verb === 'quit') { this._quit(); return; }

    this.player.tick();
    const oldFlags = { ...this.player.flags };
    this._dispatch(cmd);

    const pts = this.puzzles.checkScoreEvents(oldFlags, this.player.flags);
    if (pts) this.player.addScore(pts);
    this.puzzles.sync(this.player.flags);
  }

  // ── Dispatch ──────────────────────────────────────────────────────────

  _dispatch(cmd) {
    switch (cmd.verb) {
      case 'look':      this._look(); break;
      case 'go':        this._go(cmd.noun); break;
      case 'examine':   this._examine(cmd.noun); break;
      case 'take':      this._take(cmd.noun); break;
      case 'drop':      this._drop(cmd.noun); break;
      case 'inventory': this._inventory(); break;
      case 'talk':      this._talk(cmd.noun); break;
      case 'use':       this._use(cmd.noun, cmd.secondNoun); break;
      case 'open':      this._open(cmd.noun); break;
      case 'close':     this._close(cmd.noun); break;
      case 'wear':      this._wear(cmd.noun); break;
      case 'remove':    this._remove(cmd.noun); break;
      case 'eat':       this._eat(cmd.noun); break;
      case 'enter':     this._enterCode(cmd.noun, cmd.secondNoun); break;
      case 'score':     this._score(); break;
      case 'save':      this._save(cmd.noun || 'quicksave'); break;
      case 'load':      this._load(cmd.noun || 'quicksave'); break;
      case 'footnotes': this._toggleFootnotes(cmd.noun); break;
      case 'wait':      this.narrator.say('Time passes. The universe does not hurry on your account.'); break;
      case 'hint':      this._hint(); break;
      case 'help':      this._help(); break;
      case 'give':      this._give(cmd.noun, cmd.secondNoun); break;
      case 'board':     this._board(); break;
      default:          this.narrator.error(this.strings.unknown_command);
    }
  }

  // ── Handlers ──────────────────────────────────────────────────────────

  _look(brief = false) {
    const room = this.world.get(this.player.currentRoom);
    room.visited = true;
    this.narrator.describeRoom(room.name, room.description, room.footnote || null, brief);
    if (!brief) { this.narrator.listExits(room.exits); this.narrator.blank(); }
  }

  _go(direction) {
    if (!direction) { this.narrator.error('Go where? You\'ll need to specify a direction.'); return; }
    const room = this.world.get(this.player.currentRoom);
    const destId = this.world.exitDestination(room, direction);
    if (!destId) { this.narrator.error(this.strings.cannot_go); return; }

    const dest = this.world.get(destId);
    const [canEnter] = this.world.canEnter(dest, this.player.flags);
    if (!canEnter) { this._blockedExitMessage(destId); return; }

    this.player.currentRoom = destId;
    this._look();
  }

  _blockedExitMessage(roomId) {
    if (roomId === 'maintenance_shaft') {
      this.narrator.error(
        'The maintenance hatch is sealed. There\'s a pressure-lever mechanism ' +
        'that seems to require something heavy on the pad while you pull the lever. ' +
        'Your hands are full just holding the lever.'
      );
    } else if (roomId === 'syndicate_anteroom') {
      this.narrator.error(
        'The passage is blocked by what looks like a sealed maintenance panel. ' +
        'Actually, looking more carefully, it\'s a door. A very well-disguised door. ' +
        'You\'re going to need to find the entrance.'
      );
    } else if (roomId === 'syndicate_inner_office') {
      this.narrator.error('The heavy door is locked. The keycard reader blinks once, expectantly.');
    } else {
      this.narrator.error(this.strings.cannot_go);
    }
  }

  _examine(noun) {
    if (!noun || ['room','here','around'].includes(noun)) { this._look(); return; }
    if (['me','myself','self','you'].includes(noun)) {
      this.narrator.describeItem(this.strings.examine_self); return;
    }

    const item = this._findItemInContext(noun);
    if (item) {
      this.narrator.describeItem(item.examineDetail || item.description);
      if (item.scoreOnExamine && !this.player.hasFlag(`examined_${item.itemId}`)) {
        this.player.addScore(item.scoreOnExamine);
        this.player.setFlag(`examined_${item.itemId}`);
      }
      if (item.container && item.open) {
        const contents = this.items.itemsInContainer(item.itemId);
        if (contents.length) {
          this.narrator.say('It contains:');
          for (const c of contents) this.narrator.say(`  ${c.name[0].toUpperCase() + c.name.slice(1)}`);
        } else {
          this.narrator.say(this.strings.container_empty);
        }
      }
      return;
    }

    const npc = this._findNpcInContext(noun);
    if (npc) { this.narrator.describeItem(npc.examineDetail); return; }

    this.narrator.error(this.strings.item_not_here);
  }

  _take(noun) {
    if (!noun) { this.narrator.error('Take what?'); return; }
    const item = this._findItemInContext(noun, true);
    if (!item) { this.narrator.error(this.strings.item_not_here); return; }
    if (!item.takeable) { this.narrator.error(this.strings.cannot_take); return; }

    const room = this.world.get(this.player.currentRoom);
    room.removeItem(item.itemId);
    if (item.containerLocation) {
      const container = this.items.get(item.containerLocation);
      if (container) container.contents = container.contents.filter(i => i !== item.itemId);
    }

    if (!this.player.addItem(item.itemId, item.weight)) {
      room.addItem(item.itemId);
      this.narrator.error(this.strings.cannot_take_weight);
      return;
    }

    item.moveToInventory();
    this.narrator.system(this.strings.item_taken);

    if (item.scoreOnTake && !this.player.hasFlag(`took_${item.itemId}`)) {
      this.player.addScore(item.scoreOnTake);
      this.player.setFlag(`took_${item.itemId}`);
    }
  }

  _drop(noun) {
    if (!noun) { this.narrator.error('Drop what?'); return; }
    const item = this._findItemInInventory(noun);
    if (!item) { this.narrator.error(this.strings.item_not_carrying); return; }

    this.player.removeItem(item.itemId);
    const room = this.world.get(this.player.currentRoom);
    room.addItem(item.itemId);
    item.moveToRoom(this.player.currentRoom);
    this.narrator.system(this.strings.item_dropped);
  }

  _inventory() {
    if (!this.player.inventory.length) {
      this.narrator.inventoryList([], this.strings.inventory_empty); return;
    }
    const names = this.player.inventory.map(id => {
      const item = this.items.get(id);
      if (!item) return id;
      let name = item.name[0].toUpperCase() + item.name.slice(1);
      if (this.player.isWearing(id)) name += ' (worn)';
      return name;
    });
    this.narrator.say(this.strings.inventory_header);
    this.narrator.inventoryList(names, this.strings.inventory_empty);
  }

  _talk(noun) {
    if (!noun) {
      const present = this._visibleNpcsInRoom();
      if (!present.length) { this.narrator.error("There's nobody here to talk to."); return; }
      this.narrator.say('You could talk to: ' + present.map(n => n.name).join(', '));
      return;
    }
    const npc = this._findNpcInContext(noun);
    if (!npc) { this.narrator.error(this.strings.npc_not_here); return; }
    this._startDialogue(npc);
  }

  _startDialogue(npc) {
    this.narrator.npcSpeaks(npc.name, npc.greeting);
    const available = npc.availableTopics(this.player.flags);
    if (available.length) {
      const options = available.map((t, i) => [i + 1, this._topicLabel(t.key)]);
      options.push([options.length + 1, 'Leave']);
      this.narrator.dialogueOptions(options);
      this._inDialogue     = npc.npcId;
      this._dialogueTopics = available;
    } else {
      this.narrator.say("They don't seem to have more to say right now.");
    }
  }

  _topicLabel(key) { return key.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase()); }

  _handleDialogueInput(raw) {
    const npc = this.npcs.get(this._inDialogue);
    if (!npc) { this._inDialogue = null; return; }

    const available  = this._dialogueTopics;
    const leaveIdx   = available.length + 1;
    const num        = parseInt(raw.trim(), 10);

    if (!isNaN(num)) {
      if (num === leaveIdx) {
        this._inDialogue = null;
        this.narrator.say('You take your leave.');
        return;
      }
      if (num >= 1 && num <= available.length) {
        this._handleTopic(npc, available[num - 1]);
        return;
      }
      this.narrator.error("That's not a valid option.");
      return;
    }

    // Keyword match
    const key = this.npcs.findTopicForNoun(npc, raw);
    if (key) { const t = npc.getTopic(key); if (t) { this._handleTopic(npc, t); return; } }
    this.narrator.error('Choose a number from the list, or type a topic.');
  }

  _handleTopic(npc, topic) {
    if (topic.requiresCredits > 0 && this.player.credits < topic.requiresCredits) {
      this.narrator.say(`That information costs ${topic.requiresCredits} credits. You have ${this.player.credits}.`);
      return;
    }
    if (topic.requiresCredits > 0) this.player.credits -= topic.requiresCredits;

    this.narrator.npcSpeaks(npc.name, topic.text);
    if (topic.setsFlag) this.player.setFlag(topic.setsFlag);

    if (topic.givesItem) {
      const item = this.items.get(topic.givesItem);
      if (item && !this.player.hasItem(topic.givesItem)) {
        if (this.player.addItem(topic.givesItem, item.weight)) {
          item.moveToInventory();
          this.narrator.say(`You receive: ${item.name[0].toUpperCase() + item.name.slice(1)}.`);
          if (item.scoreOnTake && !this.player.hasFlag(`took_${item.itemId}`)) {
            this.player.addScore(item.scoreOnTake);
            this.player.setFlag(`took_${item.itemId}`);
          }
        }
      }
    }

    const available = npc.availableTopics(this.player.flags);
    if (available.length) {
      const options = available.map((t, i) => [i + 1, this._topicLabel(t.key)]);
      options.push([options.length + 1, 'Leave']);
      this.narrator.dialogueOptions(options);
      this._dialogueTopics = available;
    } else {
      this._inDialogue = null;
    }
  }

  _use(noun, secondNoun) {
    if (!noun) { this.narrator.error('Use what?'); return; }
    let item = this._findItemInInventory(noun) ?? this._findItemInRoom(noun);
    if (!item) { this.narrator.error(this.strings.item_not_here); return; }

    if (secondNoun) { this._useOn(item, secondNoun); return; }

    if (item.heals) {
      const healed = this.player.heal(item.heals);
      if (healed > 0) {
        this.narrator.say(`You use the ${item.name}. You feel somewhat better (+${healed} health).`);
        if (this.player.hasItem(item.itemId) && item.weight === 0) this.player.removeItem(item.itemId);
      } else {
        this.narrator.say("You're already at full health. The frontier is occasionally kind.");
      }
    } else if (item.useText) {
      this.narrator.say(item.useText);
    } else {
      this.narrator.say(`You examine the ${item.name} but aren't sure what to do with it right now.`);
    }
  }

  _useOn(item, targetNoun) {
    const target = this._findItemInContext(targetNoun);
    if (!target) { this.narrator.error(`You don't see '${targetNoun}' to use that on.`); return; }

    const effect = item.useOn[target.itemId];
    if (!effect) {
      this.narrator.say(`Using the ${item.name} on the ${target.name} doesn't seem to accomplish anything.`);
      return;
    }

    if (effect.text) this.narrator.say(effect.text);

    if (effect.success !== false && effect.effect) {
      if (effect.effect.startsWith('set_flag:')) {
        const flag = effect.effect.slice('set_flag:'.length);
        this.player.setFlag(flag);
        if (flag === 'maintenance_hatch_open') this.player.setFlag('found_syndicate');
      }
    }
  }

  _open(noun) {
    if (!noun) { this.narrator.error('Open what?'); return; }
    const item = this._findItemInContext(noun);
    if (!item) { this.narrator.error(this.strings.item_not_here); return; }
    if (!item.container && !item.lockMechanism) { this.narrator.error(`You can't open the ${item.name}.`); return; }
    if (item.open) { this.narrator.error(this.strings.already_open); return; }

    if (item.locked) {
      if (item.lockMechanism === 'pressure_lever') {
        this.narrator.say('The hatch has a pressure-lever mechanism — you need something heavy on the pressure pad while you pull the lever. Try using a heavy item on the hatch.');
      } else if (item.lockMechanism === 'keycard') {
        this.narrator.say('The door requires a keycard. The reader blinks patiently.');
        if (this.player.hasItem('syndicate_keycard')) {
          item.locked = false; item.open = true;
          this.player.setFlag('syndicate_door_open');
          this.narrator.say('You slide the Syndicate keycard through the reader. The door opens.');
        }
      } else {
        this.narrator.say(this.strings.locked);
      }
      return;
    }

    item.open = true;
    this.narrator.say(this.strings.opened);
    if (item.contents.length) {
      const contents = this.items.itemsInContainer(item.itemId);
      if (contents.length) {
        this.narrator.say('Inside you find:');
        for (const c of contents) this.narrator.say(`  ${c.name[0].toUpperCase() + c.name.slice(1)}`);
      }
    }
  }

  _close(noun) {
    if (!noun) { this.narrator.error('Close what?'); return; }
    const item = this._findItemInContext(noun);
    if (!item || !item.container) { this.narrator.error("You can't close that."); return; }
    if (!item.open) { this.narrator.error(this.strings.already_closed); return; }
    item.open = false;
    this.narrator.say('Closed.');
  }

  _wear(noun) {
    if (!noun) { this.narrator.error('Wear what?'); return; }
    const item = this._findItemInInventory(noun);
    if (!item) { this.narrator.error(this.strings.item_not_carrying); return; }
    if (!item.wearable) { this.narrator.say(`You can't wear the ${item.name}. The frontier has standards, but not that kind.`); return; }
    if (this.player.isWearing(item.itemId)) { this.narrator.error(this.strings.item_already_worn); return; }
    this.player.wearItem(item.itemId);
    item.worn = true;
    this.narrator.say(this.strings.item_worn.replace('{item}', item.name));
    if (item.grantsFlag) this.player.setFlag(item.grantsFlag);
  }

  _remove(noun) {
    if (!noun) { this.narrator.error('Take off what?'); return; }
    const item = this._findItemInInventory(noun);
    if (!item) { this.narrator.error(this.strings.item_not_carrying); return; }
    if (!this.player.isWearing(item.itemId)) { this.narrator.say(`You're not wearing the ${item.name}.`); return; }
    this.player.wornItems = this.player.wornItems.filter(i => i !== item.itemId);
    item.worn = false;
    if (item.grantsFlag) this.player.setFlag(item.grantsFlag, false);
    this.narrator.say(`You take off the ${item.name}.`);
  }

  _eat(noun) {
    if (!noun) { this.narrator.error('Eat or drink what?'); return; }
    const item = this._findItemInInventory(noun) ?? this._findItemInRoom(noun);
    if (!item) { this.narrator.error(this.strings.item_not_here); return; }
    if (item.heals) {
      if (this.player.hasItem(item.itemId)) this.player.removeItem(item.itemId);
      else this.world.get(this.player.currentRoom).removeItem(item.itemId);
      item.location = null;
      const healed = this.player.heal(item.heals);
      this.narrator.say(`You eat the ${item.name}. It tastes like function over form. (+${healed} health)`);
    } else {
      this.narrator.say(`You're not sure that's meant to be eaten. The ${item.name} disagrees with the concept.`);
    }
  }

  _enterCode(noun, secondNoun) {
    if (!noun) { this.narrator.error('Enter what code?'); return; }
    const code = noun.replace(/\s/g, '');
    let target = null;

    if (secondNoun) {
      target = this._findItemInContext(secondNoun);
    } else {
      const room = this.world.get(this.player.currentRoom);
      for (const id of room.itemIds) {
        const item = this.items.get(id);
        if (item && item.lockCode) { target = item; break; }
      }
    }

    if (!target) { this.narrator.error("There's nothing here that accepts a code."); return; }
    if (!target.lockCode) { this.narrator.say(`The ${target.name} doesn't use a code combination.`); return; }

    if (code === target.lockCode) {
      target.locked = false; target.open = true;
      this.narrator.say(this.strings.opened);
      if (target.contents.length) {
        const contents = this.items.itemsInContainer(target.itemId);
        if (contents.length) {
          this.narrator.say('Inside you find:');
          for (const c of contents) this.narrator.say(`  ${c.name[0].toUpperCase() + c.name.slice(1)}`);
        }
      }
    } else {
      this.narrator.error(this.strings.wrong_code);
    }
  }

  _score() {
    const rank = this._getRank();
    this.narrator.scoreDisplay(this.player.score, this.strings.max_score, this.player.turns, rank, this.player.credits);
  }

  _getRank() {
    const ranks = this.strings.score_ranks;
    let rank = 'Lost';
    for (const [threshold, label] of Object.entries(ranks).sort((a,b) => +a[0] - +b[0])) {
      if (this.player.score >= +threshold) rank = label;
    }
    return rank;
  }

  _save(name) {
    const ok = save.saveGame(name, this.player.toDict(), this.world.toDict(), this.items.toDict(), this.npcs.toDict());
    if (ok) this.narrator.system(this.strings.save_success.replace('{name}', name));
    else    this.narrator.error(this.strings.save_failed);
  }

  _load(name) {
    const data = save.loadGame(name);
    if (!data) { this.narrator.error(this.strings.load_failed); return; }
    this.player = Player.fromDict(data.player);
    this.world.fromDict(data.world || {});
    this.items.fromDict(data.items || {});
    this.npcs.fromDict(data.npcs  || {});
    this.puzzles.sync(this.player.flags);
    this.narrator.system(this.strings.load_success);
    this._look();
  }

  _toggleFootnotes(arg) {
    const low = (arg || '').toLowerCase();
    if (['on','enable','yes'].includes(low)) {
      this.narrator.setFootnotes(true);
      this.narrator.system(this.strings.footnotes_on);
    } else if (['off','disable','no'].includes(low)) {
      this.narrator.setFootnotes(false);
      this.narrator.system(this.strings.footnotes_off);
    } else {
      const enabled = this.narrator.toggleFootnotes();
      this.narrator.system(enabled ? this.strings.footnotes_on : this.strings.footnotes_off);
    }
  }

  _give(noun, secondNoun) {
    if (!noun)       { this.narrator.error('Give what?'); return; }
    if (!secondNoun) { this.narrator.error(this.strings.give_no_target); return; }

    const item = this._findItemInInventory(noun);
    if (!item) { this.narrator.error(this.strings.cannot_give); return; }

    const npc = this._findNpcInContext(secondNoun);
    if (!npc) { this.narrator.error(this.strings.give_not_here); return; }

    if (item.itemId === 'plasma_revolver' && npc.npcId === 'sheriff_vasquez') {
      this.player.removeItem(item.itemId);
      this.player.credits += 200;
      this.player.setFlag('revolver_returned');
      this.narrator.npcSpeaks(npc.name,
        'Vasquez stares at the revolver for a moment that has several things in it.\n\n' +
        '"Where did you find this." It comes out flat, not a question. She takes it, ' +
        'checks the cylinder with the practiced motion of someone who has done it ten ' +
        'thousand times, and sets it on the desk.\n\n' +
        '"My father gave me that." A pause. "Two hundred credits. Don\'t argue."'
      );
      return;
    }

    if (item.itemId === 'quantum_codicil') {
      if (npc.npcId === 'sheriff_vasquez') {
        this.player.removeItem(item.itemId);
        this.player.credits += 2000;
        this.player.setFlag('ending_sheriff');
        this.player.setFlag('game_complete');
        this.player.addScore(25);
        this._triggerEnding('sheriff');
        return;
      }
      if (npc.npcId === 'director_holloway') {
        this.player.removeItem(item.itemId);
        this.player.credits += 5000;
        this.player.setFlag('ending_syndicate');
        this.player.setFlag('game_complete');
        this.player.addScore(25);
        this._triggerEnding('syndicate');
        return;
      }
      if (npc.npcId === 'augusto_claim') {
        this.player.removeItem(item.itemId);
        this.player.setFlag('ending_brotherhood');
        this.player.setFlag('game_complete');
        this.player.addScore(25);
        this._triggerEnding('brotherhood');
        return;
      }
    }

    this.narrator.say(this.strings.give_no_effect);
  }

  _board() {
    if (this.player.currentRoom !== 'docking_bay_7') {
      this.narrator.error("Your ship isn't here."); return;
    }
    if (!this.player.hasItem('quantum_codicil')) {
      this.narrator.say(this.strings.board_no_codicil); return;
    }
    this.player.setFlag('ending_keep');
    this.player.setFlag('game_complete');
    this.player.addScore(25);
    this._triggerEnding('keep');
  }

  _triggerEnding(type) {
    const rank  = this._getRank();
    const lines = this.strings.endings[type];
    for (const line of lines) {
      this.narrator.say(
        line.replace('{score}', this.player.score)
            .replace('{max_score}', this.strings.max_score)
            .replace('{rank}', rank),
        false
      );
    }
    this._running = false;
  }

  _help() {
    for (const line of this.strings.help_text) this.narrator.say(line);
  }

  _hint() {
    const r = this.player.currentRoom;
    const f = this.player.flags;
    if (r === 'docking_bay_7' && !f.maintenance_hatch_open) {
      this.narrator.say('The maintenance hatch has a pressure-lever mechanism. You need something heavy to hold the pressure pad down while you pull the lever.');
    } else if (!f.working_with_sheriff) {
      this.narrator.say("Talk to Sheriff Vasquez in her office. She's got a case and she needs someone who isn't already on every faction's list.");
    } else if (!f.clem_told_you) {
      this.narrator.say('Clem Duster at the Rusty Spur sees everything that happens on this station. Information has a price, but it\'s worth paying.');
    } else if (!f.found_syndicate) {
      this.narrator.say('The maintenance shaft connects to more than just the docking bay. You need to get that hatch open first.');
    } else {
      this.narrator.say("You've come a long way. Trust what you know. Talk to everyone again. The answer is closer than it feels.");
    }
  }

  _quit() {
    this.narrator.say(this.strings.quit_confirm);
    this._pendingQuit = true;
  }

  // ── Lookup helpers ────────────────────────────────────────────────────

  _visibleNpcsInRoom() {
    const room = this.world.get(this.player.currentRoom);
    return room.npcIds.map(id => this.npcs.get(id)).filter(Boolean);
  }

  _findItemInContext(noun, includeContainers = false) {
    const room = this.world.get(this.player.currentRoom);
    const ids  = [...this.player.inventory, ...room.itemIds];
    if (includeContainers) {
      for (const id of room.itemIds) {
        const c = this.items.get(id);
        if (c && c.container && c.open) ids.push(...c.contents);
      }
    }
    const matchId = Parser.matchItem(noun, this.items.nameMap(ids));
    return matchId ? this.items.get(matchId) : null;
  }

  _findItemInInventory(noun) {
    const matchId = Parser.matchItem(noun, this.items.nameMap(this.player.inventory));
    return matchId ? this.items.get(matchId) : null;
  }

  _findItemInRoom(noun) {
    const room    = this.world.get(this.player.currentRoom);
    const matchId = Parser.matchItem(noun, this.items.nameMap(room.itemIds));
    return matchId ? this.items.get(matchId) : null;
  }

  _findNpcInContext(noun) {
    const room    = this.world.get(this.player.currentRoom);
    const matchId = Parser.matchItem(noun, this.npcs.nameMap(room.npcIds));
    return matchId ? this.npcs.get(matchId) : null;
  }
}
