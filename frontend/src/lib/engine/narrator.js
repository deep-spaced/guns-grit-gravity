/**
 * narrator.js — Message buffer (port of web_narrator.py).
 * Collects typed message objects; flush() returns and clears them.
 */

export class Narrator {
  constructor() {
    this.footnotesEnabled = true;
    this._buffer = [];
  }

  flush() {
    const msgs = [...this._buffer];
    this._buffer = [];
    return msgs;
  }

  _push(type, content = '', extra = {}) {
    this._buffer.push({ type, content, ...extra });
  }

  say(text) { this._push('text', text); }
  blank()   { this._push('blank'); }
  separator(){ this._push('separator'); }

  locationHeader(name) { this._push('location', name.toUpperCase()); }

  describeRoom(name, description, footnote = null, brief = false) {
    this.locationHeader(name);
    if (!brief) {
      this.say(description);
      if (footnote && this.footnotesEnabled) this._push('footnote', footnote);
    }
    this.blank();
  }

  describeItem(description) {
    this.blank();
    this.say(description);
    this.blank();
  }

  listExits(exits) {
    const dirs = Object.keys(exits).sort();
    if (!dirs.length) { this.say('There are no obvious exits.'); return; }
    this.say('Exits: ' + dirs.map(d => d[0].toUpperCase() + d.slice(1)).join(', ') + '.');
  }

  inventoryList(items, emptyMsg) {
    this.blank();
    if (!items.length) { this.say(emptyMsg); }
    else { for (const name of items) this._push('item_line', `  ${name}`); }
    this.blank();
  }

  npcSpeaks(npcName, text) {
    this.blank();
    this._push('npc_name', npcName.toUpperCase());
    this.blank();
    this.say(text);
    this.blank();
  }

  dialogueOptions(options) {
    this.blank();
    for (const [number, text] of options) this._push('dialogue_option', `[${number}] ${text}`, { number });
    this.blank();
  }

  system(text) { this._push('system', text); }
  error(text)  { this._push('error', text); }

  scoreDisplay(score, maxScore, turns, rank, credits = 0) {
    this.blank();
    this._push('score', '', { score, max_score: maxScore, turns, rank, credits });
    this.blank();
  }

  death(messageLines, score, maxScore, rank) {
    this.blank(); this.separator(); this.blank();
    for (const line of messageLines) {
      this._push('death_line', line.replace('{score}', score)
                                    .replace('{max_score}', maxScore)
                                    .replace('{rank}', rank));
    }
    this.blank(); this.separator(); this.blank();
  }

  titleScreen(titleLines, introLines) {
    this.blank(); this.separator();
    for (const line of titleLines) this._push('title_line', line);
    this.separator(); this.blank();
    for (const line of introLines) {
      if (line === '') this.blank(); else this.say(line);
    }
    this.blank();
  }

  quitMessage(msg) {
    this.blank(); this.separator(); this.blank();
    this._push('quit_message', msg);
    this.blank();
  }

  setFootnotes(enabled) { this.footnotesEnabled = enabled; }
  toggleFootnotes() {
    this.footnotesEnabled = !this.footnotesEnabled;
    return this.footnotesEnabled;
  }
}
