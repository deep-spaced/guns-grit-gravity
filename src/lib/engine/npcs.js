/**
 * npcs.js — NPC registry and dialogue (port of npcs.py).
 */

import npcsData from '@data/npcs.json';

class DialogueTopic {
  constructor(key, d) {
    this.key             = key;
    this.text            = d.text;
    this.setsFlag        = d.sets_flag ?? null;
    this.requiresFlag    = d.requires_flag ?? null;
    this.requiresCredits = d.requires_credits || 0;
    this.givesItem       = d.gives_item ?? null;
  }
}

class NPC {
  constructor(id, d) {
    this.npcId          = id;
    this.name           = d.name;
    this.aliases        = d.aliases || [];
    this.description    = d.description;
    this.examineDetail  = d.examine_detail || d.description;
    this.location       = d.location;
    this.greeting       = d.dialogue.greeting;
    this.defaultResponse= d.dialogue.default || "They don't respond.";

    this.topics = {};
    for (const [key, td] of Object.entries(d.dialogue.topics || {})) {
      this.topics[key] = new DialogueTopic(key, td);
    }
  }

  allNames()   { return [this.name, ...this.aliases]; }
  getTopic(key){ return this.topics[key] ?? null; }

  availableTopics(playerFlags) {
    return Object.values(this.topics).filter(t =>
      !t.requiresFlag || playerFlags[t.requiresFlag]
    );
  }
}

export class NPCRegistry {
  constructor() {
    this._npcs = {};
    this._load();
  }

  _load() {
    for (const [id, d] of Object.entries(npcsData)) {
      this._npcs[id] = new NPC(id, d);
    }
  }

  get(id)      { return this._npcs[id] ?? null; }

  nameMap(ids) {
    const result = {};
    for (const id of ids) {
      const npc = this.get(id);
      if (npc) result[id] = npc.allNames();
    }
    return result;
  }

  findTopicForNoun(npc, noun) {
    noun = noun.toLowerCase().trim();
    if (npc.topics[noun]) return noun;
    for (const key of Object.keys(npc.topics)) {
      if (key.includes(noun) || noun.includes(key)) return key;
    }
    const nounWords = new Set(noun.split(' '));
    for (const key of Object.keys(npc.topics)) {
      const keyWords = new Set(key.split('_'));
      if ([...nounWords].some(w => keyWords.has(w))) return key;
    }
    return null;
  }

  toDict() {
    const result = {};
    for (const [id, npc] of Object.entries(this._npcs)) result[id] = { location: npc.location };
    return result;
  }

  fromDict(data) {
    for (const [id, d] of Object.entries(data)) {
      if (this._npcs[id] && d.location) this._npcs[id].location = d.location;
    }
  }
}
