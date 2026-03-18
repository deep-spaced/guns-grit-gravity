/**
 * items.js — Item registry (port of items.py).
 */

import itemsData from '@data/items.json';

export class Item {
  constructor(id, d) {
    this.itemId            = id;
    this.name              = d.name;
    this.aliases           = d.aliases || [];
    this.description       = d.description;
    this.examineDetail     = d.examine_detail || d.description;
    this.takeable          = d.takeable !== false;
    this.weight            = d.weight ?? 1;
    this.location          = d.location ?? null;
    this.containerLocation = d.container_location ?? null;
    this.wearable          = !!d.wearable;
    this.worn              = false;
    this.container         = !!d.container;
    this.locked            = !!d.locked;
    this.open              = !d.locked;
    this.lockCode          = d.lock_code ?? null;
    this.lockMechanism     = d.lock_mechanism ?? null;
    this.contents          = [...(d.contents || [])];
    this.useOn             = d.use_on || {};
    this.useText           = d.use_text || '';
    this.grantsFlag        = d.grants_flag ?? null;
    this.scoreOnTake       = d.score_on_take || 0;
    this.scoreOnExamine    = d.score_on_examine || 0;
    this.heals             = d.heals || 0;
    this.note              = d.note || '';
  }

  allNames() { return [this.name, ...this.aliases]; }

  moveToRoom(roomId) {
    this.location          = roomId;
    this.containerLocation = null;
  }
  moveToInventory() {
    this.location          = null;
    this.containerLocation = null;
  }
  moveToContainer(containerId) {
    this.location          = null;
    this.containerLocation = containerId;
  }
}

export class ItemRegistry {
  constructor() {
    this._items = {};
    this._load();
  }

  _load() {
    for (const [id, d] of Object.entries(itemsData)) {
      this._items[id] = new Item(id, d);
    }
  }

  get(id)        { return this._items[id] ?? null; }
  allItems()     { return Object.values(this._items); }

  itemsInContainer(containerId) {
    return Object.values(this._items).filter(i => i.containerLocation === containerId);
  }

  nameMap(ids) {
    const result = {};
    for (const id of ids) {
      const item = this.get(id);
      if (item) result[id] = item.allNames();
    }
    return result;
  }

  toDict() {
    const result = {};
    for (const [id, item] of Object.entries(this._items)) {
      result[id] = {
        location: item.location, container_location: item.containerLocation,
        locked: item.locked, open: item.open, worn: item.worn, contents: item.contents,
      };
    }
    return result;
  }

  fromDict(data) {
    for (const [id, d] of Object.entries(data)) {
      const item = this._items[id];
      if (item) {
        item.location          = d.location          ?? item.location;
        item.containerLocation = d.container_location ?? item.containerLocation;
        item.locked            = d.locked             ?? item.locked;
        item.open              = d.open               ?? item.open;
        item.worn              = d.worn               ?? item.worn;
        item.contents          = d.contents           ?? item.contents;
      }
    }
  }
}
