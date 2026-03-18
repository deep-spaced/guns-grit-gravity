/**
 * world.js — Room graph (port of world.py).
 * Loads from data/rooms.json via Vite's JSON import.
 */

import roomsData from '@data/rooms.json';

class Room {
  constructor(id, data) {
    this.roomId      = id;
    this.name        = data.name;
    this.description = data.description;
    this.footnote    = data.footnote || '';
    this.exits       = { ...(data.exits || {}) };
    this.itemIds     = [...(data.items || [])];
    this.npcIds      = [...(data.npcs  || [])];
    this.flags       = { ...(data.flags || {}) };
    this.visited     = false;
  }

  addItem(id)    { if (!this.itemIds.includes(id)) this.itemIds.push(id); }
  removeItem(id) { this.itemIds = this.itemIds.filter(i => i !== id); }
  hasItem(id)    { return this.itemIds.includes(id); }
  hasNpc(id)     { return this.npcIds.includes(id); }
  requiresFlag() { return this.flags.requires_flag ?? null; }
}

export class World {
  constructor() {
    this._rooms = {};
    this._load();
  }

  _load() {
    for (const [id, data] of Object.entries(roomsData)) {
      this._rooms[id] = new Room(id, data);
    }
  }

  get(roomId)    { return this._rooms[roomId]; }
  exists(roomId) { return roomId in this._rooms; }
  allRooms()     { return Object.values(this._rooms); }

  exitDestination(room, direction) { return room.exits[direction] ?? null; }

  canEnter(room, playerFlags) {
    const req = room.requiresFlag();
    if (!req) return [true, null];
    return playerFlags[req] ? [true, null] : [false, req];
  }

  toDict() {
    const result = {};
    for (const [id, room] of Object.entries(this._rooms)) {
      result[id] = { item_ids: room.itemIds, npc_ids: room.npcIds, visited: room.visited, flags: room.flags };
    }
    return result;
  }

  fromDict(data) {
    for (const [id, d] of Object.entries(data)) {
      if (this._rooms[id]) {
        const r = this._rooms[id];
        r.itemIds  = d.item_ids ?? r.itemIds;
        r.npcIds   = d.npc_ids  ?? r.npcIds;
        r.visited  = d.visited  ?? false;
        Object.assign(r.flags, d.flags || {});
      }
    }
  }
}
