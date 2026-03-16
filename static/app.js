/**
 * app.js — Guns, Grit & Gravity web client
 *
 * Manages the WebSocket connection, renders typed messages from the
 * server into the terminal output area, and handles player input.
 */

'use strict';

// ── DOM refs ──────────────────────────────────────────────────────────────────
const output    = document.getElementById('output');
const input     = document.getElementById('cmd-input');
const sendBtn   = document.getElementById('send-btn');
const statusDot = document.getElementById('status-dot');
const statusLbl = document.getElementById('status-label');
const statsBar  = document.getElementById('stats-bar');
const statScore   = document.getElementById('stat-score');
const statCredits = document.getElementById('stat-credits');
const statTurns   = document.getElementById('stat-turns');
const statRank    = document.getElementById('stat-rank');

// ── State ─────────────────────────────────────────────────────────────────────
let ws         = null;
let cmdHistory = [];
let historyIdx = -1;
let gameOver   = false;

// ── WebSocket setup ───────────────────────────────────────────────────────────
function connect() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws';
  ws = new WebSocket(`${proto}://${location.host}/ws`);

  ws.onopen = () => {
    setStatus('connected', 'CONNECTED');
    input.disabled  = false;
    sendBtn.disabled = false;
    input.focus();
  };

  ws.onmessage = (event) => {
    const messages = JSON.parse(event.data);
    enqueue(messages);
  };

  ws.onclose = () => {
    setStatus('disconnected', 'DISCONNECTED');
    input.disabled  = true;
    sendBtn.disabled = true;
  };

  ws.onerror = () => {
    setStatus('disconnected', 'ERROR');
  };
}

function setStatus(cls, label) {
  statusDot.className = 'status-dot ' + cls;
  statusLbl.textContent = label;
}

// ── Message rendering ─────────────────────────────────────────────────────────
// Render all messages from a server response synchronously in a single
// requestAnimationFrame so the browser does one layout/paint pass.

function enqueue(messages) {
  requestAnimationFrame(() => {
    const frag = document.createDocumentFragment();
    let delay = 0;
    messages.forEach(msg => {
      const el = renderMessage(msg, frag);
      if (el && needsStagger(msg)) {
        el.style.animationDelay = delay + 'ms';
        el.classList.add('msg-stagger');
        delay += 30;
      }
    });
    output.appendChild(frag);
    // Scroll after the last staggered message lands
    setTimeout(scrollToBottom, delay + 50);
  });
}

function needsStagger(msg) {
  return ['text', 'npc_name', 'location', 'title_line', 'death_line',
          'error', 'system', 'footnote', 'score'].includes(msg.type);
}

// ── Render a single message ────────────────────────────────────────────────────
function renderMessage(msg, frag) {
  switch (msg.type) {

    case 'blank':
      return appendEl('div', 'msg-blank', undefined, frag);

    case 'separator':
      return appendEl('hr', 'msg-separator', undefined, frag);

    case 'location':
      return appendEl('div', 'msg-location', msg.content, frag);

    case 'text':
      return appendEl('div', 'msg msg-text', msg.content, frag);

    case 'error':
      return appendEl('div', 'msg msg-error', msg.content, frag);

    case 'system':
      return appendEl('div', 'msg msg-system', msg.content, frag);

    case 'npc_name':
      return appendEl('div', 'msg-npc-name', msg.content, frag);

    case 'footnote':
      return appendEl('div', 'msg msg-footnote', msg.content, frag);

    case 'item_line':
      return appendEl('div', 'msg msg-item-line', msg.content, frag);

    case 'dialogue_option':
      return appendEl('div', 'msg msg-dialogue-option', msg.content, frag);

    case 'title_line':
      return appendEl('div', 'msg-title-line', msg.content, frag);

    case 'score': {
      updateStats(msg);
      const scoreEl = makeEl('div', 'msg msg-score',
        `Score: ${msg.score}/${msg.max_score}  |  Rank: ${msg.rank}  |  ` +
        `Turns: ${msg.turns}  |  Credits: ${msg.credits}`);
      frag.appendChild(scoreEl);
      return scoreEl;
    }

    case 'death_line':
      return appendEl('div', 'msg msg-death-line', msg.content, frag);

    case 'quit_message':
      return appendEl('div', 'msg msg-quit', msg.content, frag);

    case 'game_over':
      gameOver = true;
      input.disabled   = true;
      sendBtn.disabled = true;
      setStatus('disconnected', 'SESSION ENDED');
      return appendEl('div', 'msg-game-over', '— GAME OVER —', frag);

    default:
      if (msg.content) return appendEl('div', 'msg msg-text', msg.content, frag);
      break;
  }
}

function makeEl(tag, classes, text) {
  const el = document.createElement(tag);
  el.className = classes;
  if (text !== undefined) el.textContent = text;
  return el;
}

function appendEl(tag, classes, text, frag) {
  const el = makeEl(tag, classes, text);
  (frag || output).appendChild(el);
  return el;
}

function updateStats(msg) {
  statsBar.style.display = 'flex';
  flashStat(statScore,   `SCORE: ${msg.score}/${msg.max_score}`);
  flashStat(statCredits, `CREDITS: ${msg.credits}`);
  flashStat(statTurns,   `TURN: ${msg.turns}`);
  flashStat(statRank,    `RANK: ${msg.rank.toUpperCase()}`);
}

function flashStat(el, text) {
  el.textContent = text;
  el.classList.add('updated');
  setTimeout(() => el.classList.remove('updated'), 800);
}

function scrollToBottom() {
  output.scrollTop = output.scrollHeight;
}

// ── Send a command ─────────────────────────────────────────────────────────────
function sendCommand() {
  if (gameOver || !ws || ws.readyState !== WebSocket.OPEN) return;
  const text = input.value.trim();
  if (!text) return;

  // Echo the player's command
  appendEl('div', 'msg-echo', text, output);
  scrollToBottom();

  // History
  if (cmdHistory[cmdHistory.length - 1] !== text) {
    cmdHistory.push(text);
  }
  historyIdx = cmdHistory.length;

  ws.send(JSON.stringify({ text }));
  input.value = '';
}

// ── Input events ──────────────────────────────────────────────────────────────
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter') {
    sendCommand();
    return;
  }

  // Command history navigation
  if (e.key === 'ArrowUp') {
    e.preventDefault();
    if (historyIdx > 0) {
      historyIdx--;
      input.value = cmdHistory[historyIdx];
      // Move cursor to end
      setTimeout(() => input.setSelectionRange(input.value.length, input.value.length), 0);
    }
    return;
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault();
    if (historyIdx < cmdHistory.length - 1) {
      historyIdx++;
      input.value = cmdHistory[historyIdx];
    } else {
      historyIdx = cmdHistory.length;
      input.value = '';
    }
    return;
  }
});

sendBtn.addEventListener('click', sendCommand);

// Keep focus on input whenever user clicks anywhere on the terminal
document.querySelector('.terminal').addEventListener('click', () => {
  if (!input.disabled) input.focus();
});

// ── Boot ──────────────────────────────────────────────────────────────────────
connect();
