/**
 * save.js — Save/load via localStorage (replaces filesystem save.py).
 */

const PREFIX = 'gg_save_';

function sanitize(name) {
  return name.replace(/[^a-z0-9_-]/gi, '_').toLowerCase().slice(0, 32);
}

export function saveGame(name, playerDict, worldDict, itemsDict, npcsDict) {
  try {
    const data = { player: playerDict, world: worldDict, items: itemsDict, npcs: npcsDict };
    localStorage.setItem(PREFIX + sanitize(name), JSON.stringify(data));
    return true;
  } catch {
    return false;
  }
}

export function loadGame(name) {
  try {
    const raw = localStorage.getItem(PREFIX + sanitize(name));
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}
