/**
 * player.js — Player state (port of player.py).
 */

const STARTING_ROOM       = 'docking_bay_7';
const MAX_CARRY_WEIGHT    = 20;

export class Player {
  constructor() {
    this.currentRoom  = STARTING_ROOM;
    this.inventory    = [];   // item IDs
    this.wornItems    = [];   // item IDs being worn
    this.score        = 0;
    this.turns        = 0;
    this.health       = 100;
    this.maxHealth    = 100;
    this.flags        = {};
    this.npcStates    = {};
    this.credits      = 100;
  }

  // ── Inventory ──────────────────────────────────────────────
  hasItem(id)     { return this.inventory.includes(id); }
  isWearing(id)   { return this.wornItems.includes(id); }

  addItem(id, weight = 1) {
    if (this.currentWeight() + weight > MAX_CARRY_WEIGHT) return false;
    this.inventory.push(id);
    return true;
  }

  removeItem(id) {
    if (!this.hasItem(id)) return false;
    this.inventory = this.inventory.filter(i => i !== id);
    this.wornItems = this.wornItems.filter(i => i !== id);
    return true;
  }

  wearItem(id) {
    if (!this.hasItem(id)) return false;
    if (!this.isWearing(id)) this.wornItems.push(id);
    return true;
  }

  currentWeight() { return this.inventory.length; }

  // ── Score / turns ──────────────────────────────────────────
  addScore(pts) { this.score = Math.max(0, this.score + pts); }
  tick()        { this.turns++; }

  // ── Flags ──────────────────────────────────────────────────
  setFlag(flag, value = true) { this.flags[flag] = value; }
  hasFlag(flag)               { return !!this.flags[flag]; }

  // ── Health ─────────────────────────────────────────────────
  heal(amount) {
    const old = this.health;
    this.health = Math.min(this.maxHealth, this.health + amount);
    return this.health - old;
  }
  hurt(amount) {
    this.health = Math.max(0, this.health - amount);
    return this.health <= 0;
  }
  isAlive() { return this.health > 0; }

  // ── NPC state ──────────────────────────────────────────────
  getNpcState(id)                      { if (!this.npcStates[id]) this.npcStates[id] = {}; return this.npcStates[id]; }
  setNpcFlag(id, key, value = true)    { this.getNpcState(id)[key] = value; }
  getNpcFlag(id, key, def = false)     { return this.getNpcState(id)[key] ?? def; }

  // ── Serialization ──────────────────────────────────────────
  toDict() {
    return {
      current_room: this.currentRoom, inventory: this.inventory,
      worn_items: this.wornItems, score: this.score, turns: this.turns,
      health: this.health, max_health: this.maxHealth,
      flags: this.flags, npc_states: this.npcStates, credits: this.credits,
    };
  }

  static fromDict(d) {
    const p = new Player();
    p.currentRoom = d.current_room ?? STARTING_ROOM;
    p.inventory   = d.inventory   ?? [];
    p.wornItems   = d.worn_items  ?? [];
    p.score       = d.score       ?? 0;
    p.turns       = d.turns       ?? 0;
    p.health      = d.health      ?? 100;
    p.maxHealth   = d.max_health  ?? 100;
    p.flags       = d.flags       ?? {};
    p.npcStates   = d.npc_states  ?? {};
    p.credits     = d.credits     ?? 0;
    return p;
  }
}
