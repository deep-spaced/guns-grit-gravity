/**
 * game.js — Game state store using the JS engine directly.
 * No WebSocket needed: the engine runs entirely in the browser.
 */

import { writable } from 'svelte/store';
import { Engine }   from './engine/engine.js';
import { Narrator } from './engine/narrator.js';

export const connected = writable(false);
export const gameOver  = writable(false);
export const messages  = writable([]);
export const stats     = writable(null);

let engine   = null;
let narrator = null;
let uid      = 0;

const STAGGER = new Set([
  'text', 'npc_name', 'location', 'title_line', 'death_line',
  'error', 'system', 'footnote', 'score',
]);

function enrich(batch) {
  let delay = 0;
  return batch.map(msg => {
    const stagger = STAGGER.has(msg.type);
    const entry   = { ...msg, _id: uid++, animDelay: stagger ? delay : 0 };
    if (stagger) delay += 30;
    if (msg.type === 'score')     stats.set(msg);
    if (msg.type === 'game_over') gameOver.set(true);
    return entry;
  });
}

function push(batch) {
  messages.update(m => [...m, ...enrich(batch)]);
}

export function connect() {
  narrator = new Narrator();
  engine   = new Engine(narrator);

  engine.start();
  push(narrator.flush());

  connected.set(true);
}

export function sendCommand(text) {
  if (!engine || !engine.isRunning()) return;

  // Echo the player's command immediately
  messages.update(m => [...m, { type: 'echo', content: text, _id: uid++, animDelay: 0 }]);

  engine.process(text);
  const batch = narrator.flush();

  if (!engine.isRunning()) {
    batch.push({ type: 'game_over' });
    gameOver.set(true);
    connected.set(false);
  }

  push(batch);
}
