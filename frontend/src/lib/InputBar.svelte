<script>
  import { connected, gameOver, sendCommand } from './game.js';

  let inputEl;
  let text      = '';
  let history   = [];
  let histIdx   = -1;

  $: disabled = !$connected || $gameOver;

  function submit() {
    const cmd = text.trim();
    if (!cmd || disabled) return;
    sendCommand(cmd);
    if (history[history.length - 1] !== cmd) history = [...history, cmd];
    histIdx = history.length;
    text = '';
  }

  function onKeydown(e) {
    if (e.key === 'Enter') { submit(); return; }

    if (e.key === 'ArrowUp') {
      e.preventDefault();
      if (histIdx > 0) {
        histIdx--;
        text = history[histIdx];
        // move cursor to end on next tick
        setTimeout(() => inputEl?.setSelectionRange(text.length, text.length), 0);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      if (histIdx < history.length - 1) {
        histIdx++;
        text = history[histIdx];
      } else {
        histIdx = history.length;
        text = '';
      }
      return;
    }
  }

  // Re-focus input on any click in the terminal
  function focusInput() {
    if (!disabled) inputEl?.focus();
  }
</script>

<svelte:window on:click={focusInput} />

<footer class="input-area">
  <span class="prompt-glyph" aria-hidden="true">&gt;</span>
  <input
    bind:this={inputEl}
    bind:value={text}
    on:keydown={onKeydown}
    type="text"
    class="cmd-input"
    autocomplete="off"
    autocorrect="off"
    autocapitalize="off"
    spellcheck="false"
    placeholder="type a command…"
    aria-label="Command input"
    {disabled}
  />
  <button class="send-btn" on:click={submit} {disabled}>SEND</button>
</footer>

<style>
  .input-area {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-top: 1px solid var(--border);
    background: var(--bg-panel);
    flex-shrink: 0;
  }

  .prompt-glyph {
    color: var(--green-bright);
    font-size: 22px;
    text-shadow: var(--glow-bright);
    flex-shrink: 0;
    user-select: none;
  }

  .cmd-input {
    flex: 1;
    background: transparent;
    border: none;
    outline: none;
    color: var(--green-bright);
    font-family: var(--font-main);
    font-size: 20px;
    caret-color: var(--green-bright);
    text-shadow: var(--glow);
    letter-spacing: 1px;
  }
  .cmd-input::placeholder { color: var(--dim); text-shadow: none; }
  .cmd-input:disabled      { opacity: 0.4; cursor: not-allowed; }

  .send-btn {
    background: transparent;
    border: 1px solid var(--dim);
    color: var(--green-dim);
    font-family: var(--font-main);
    font-size: 16px;
    letter-spacing: 2px;
    padding: 4px 14px;
    cursor: pointer;
    transition: all 0.15s;
    flex-shrink: 0;
  }
  .send-btn:hover:not(:disabled) {
    border-color: var(--green);
    color: var(--green-bright);
    text-shadow: var(--glow);
    box-shadow: 0 0 8px rgba(51,255,87,0.3);
  }
  .send-btn:disabled { opacity: 0.3; cursor: not-allowed; }
</style>
