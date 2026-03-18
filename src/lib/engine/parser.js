/**
 * parser.js — Text input parser (port of parser.py).
 */

const VERB_SYNONYMS = {
  go: 'go', move: 'go', walk: 'go', travel: 'go', head: 'go', run: 'go', climb: 'go', crawl: 'go',
  look: 'look', l: 'look', describe: 'look',
  examine: 'examine', x: 'examine', inspect: 'examine', check: 'examine',
  read: 'examine', study: 'examine', view: 'examine', search: 'examine',
  take: 'take', get: 'take', grab: 'take', pick: 'take', collect: 'take', retrieve: 'take', acquire: 'take',
  drop: 'drop', put: 'drop', place: 'drop', leave: 'drop', discard: 'drop', throw: 'drop',
  inventory: 'inventory', inv: 'inventory', i: 'inventory', items: 'inventory', pockets: 'inventory', carrying: 'inventory',
  talk: 'talk', speak: 'talk', ask: 'talk', chat: 'talk', converse: 'talk', question: 'talk',
  greet: 'talk', hail: 'talk', address: 'talk',
  use: 'use', apply: 'use', activate: 'use', operate: 'use', insert: 'use', attach: 'use', combine: 'use',
  open: 'open', unlock: 'open', unbar: 'open', unseal: 'open', pry: 'open',
  close: 'close', shut: 'close', seal: 'close', lock: 'close',
  wear: 'wear', don: 'wear', equip: 'wear',
  remove: 'remove', doff: 'remove',
  score: 'score', points: 'score',
  help: 'help', '?': 'help', h: 'help', commands: 'help',
  save: 'save', load: 'load', restore: 'load',
  quit: 'quit', q: 'quit', exit: 'quit', bye: 'quit',
  enter: 'enter', type: 'enter', input: 'enter', dial: 'enter',
  footnotes: 'footnotes',
  hint: 'hint', hints: 'hint',
  wait: 'wait', z: 'wait', rest: 'wait',
  give: 'give', offer: 'give', hand: 'give',
  board: 'board', launch: 'board', depart: 'board', fly: 'board',
  eat: 'eat', drink: 'eat', consume: 'eat',
  // Two-word verbs (checked separately):
  'put on': 'wear', 'take off': 'remove',
};

const DIRECTION_WORDS = {
  north: 'north', n: 'north',
  south: 'south', s: 'south',
  east:  'east',  e: 'east',
  west:  'west',  w: 'west',
  up: 'up', u: 'up', upstairs: 'up',
  down: 'down', d: 'down', downstairs: 'down',
  in: 'in', inside: 'in',
  out: 'out', outside: 'out',
  northeast: 'northeast', ne: 'northeast',
  northwest: 'northwest', nw: 'northwest',
  southeast: 'southeast', se: 'southeast',
  southwest: 'southwest', sw: 'southwest',
};

const PREPOSITIONS = new Set(['on','with','at','to','from','into','onto','in','the','a','an']);
const SPLIT_PREPS  = new Set(['on','with','at','from','onto','into','to']);
const VERB_VALUES  = new Set(Object.values(VERB_SYNONYMS));

export class Command {
  constructor() {
    this.verb       = '';
    this.noun       = '';
    this.secondNoun = '';
    this.raw        = '';
    this.preposition= '';
  }
  get valid() { return !!this.verb; }
}

export class Parser {
  parse(raw) {
    const text = raw.toLowerCase().trim();
    const cmd  = new Command();
    cmd.raw    = raw;
    if (!text) return cmd;

    // Bare direction
    if (DIRECTION_WORDS[text]) {
      cmd.verb = 'go';
      cmd.noun = DIRECTION_WORDS[text];
      return cmd;
    }

    const tokens = text.split(/\s+/);

    // Two-word verb (put on / take off)
    if (tokens.length >= 2) {
      const two = `${tokens[0]} ${tokens[1]}`;
      if (VERB_SYNONYMS[two]) {
        cmd.verb = VERB_SYNONYMS[two];
        this._fillNouns(cmd, tokens.slice(2));
        return cmd;
      }
    }

    const first = tokens[0];
    cmd.verb = VERB_SYNONYMS[first] ?? first;

    const rest = tokens.slice(1);

    if (cmd.verb === 'go' && rest[0] && DIRECTION_WORDS[rest[0]]) {
      cmd.noun = DIRECTION_WORDS[rest[0]];
      return cmd;
    }

    if (!VERB_VALUES.has(cmd.verb) && DIRECTION_WORDS[first]) {
      cmd.verb = 'go';
      cmd.noun = DIRECTION_WORDS[first];
      return cmd;
    }

    this._fillNouns(cmd, rest);
    return cmd;
  }

  _fillNouns(cmd, tokens) {
    let splitIdx = -1;
    let splitPrep = '';
    for (let i = 1; i < tokens.length; i++) {
      if (SPLIT_PREPS.has(tokens[i])) { splitIdx = i; splitPrep = tokens[i]; break; }
    }

    if (splitIdx >= 0) {
      cmd.noun        = tokens.slice(0, splitIdx).filter(t => !PREPOSITIONS.has(t)).join(' ');
      cmd.secondNoun  = tokens.slice(splitIdx + 1).filter(t => !PREPOSITIONS.has(t)).join(' ');
      cmd.preposition = splitPrep;
    } else {
      cmd.noun = tokens.filter(t => !PREPOSITIONS.has(t)).join(' ');
    }
  }

  static matchItem(noun, candidates) {
    noun = noun.toLowerCase().trim();
    if (!noun) return null;
    // Exact ID
    if (candidates[noun]) return noun;
    // Exact name/alias
    for (const [id, names] of Object.entries(candidates)) {
      if (names.map(n => n.toLowerCase()).includes(noun)) return id;
    }
    // Partial
    for (const [id, names] of Object.entries(candidates)) {
      if (names.some(n => n.toLowerCase().includes(noun))) return id;
    }
    return null;
  }
}
