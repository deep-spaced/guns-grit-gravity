<script>
  import { afterUpdate } from 'svelte';
  import { messages } from './game.js';

  let el;

  // After each Svelte update, scroll to reveal the last staggered message.
  // We delay by the last message's animDelay + a bit so the reveal animation
  // finishes before the scroll locks onto it.
  afterUpdate(() => {
    if (!el) return;
    const msgs = $messages;
    const last  = msgs[msgs.length - 1];
    const delay = (last?.animDelay ?? 0) + 100;
    setTimeout(() => { el.scrollTop = el.scrollHeight; }, delay);
  });

  function msgClass(type) {
    const map = {
      text:            'msg msg-text',
      error:           'msg msg-error',
      system:          'msg msg-system',
      footnote:        'msg msg-footnote',
      item_line:       'msg msg-item-line',
      dialogue_option: 'msg msg-dialogue-option',
      npc_name:        'msg-npc-name',
      location:        'msg-location',
      title_line:      'msg-title-line',
      score:           'msg msg-score',
      death_line:      'msg msg-death-line',
      quit_message:    'msg msg-quit',
      echo:            'msg-echo',
    };
    return map[type] ?? 'msg msg-text';
  }

  function scoreText(m) {
    return `Score: ${m.score}/${m.max_score}  |  Rank: ${m.rank}  |  Turns: ${m.turns}  |  Credits: ${m.credits}`;
  }
</script>

<main
  class="output-area"
  bind:this={el}
  role="log"
  aria-live="polite"
  aria-label="Game output"
>
  {#each $messages as msg (msg._id)}
    {#if msg.type === 'separator'}
      <hr
        class="msg-separator"
        class:msg-stagger={msg.animDelay > 0}
        style:animation-delay="{msg.animDelay}ms"
      />
    {:else if msg.type === 'game_over'}
      <div class="msg-game-over">— GAME OVER —</div>
    {:else if msg.type === 'blank'}
      <div class="msg-blank"></div>
    {:else}
      <div
        class={msgClass(msg.type)}
        class:msg-stagger={msg.animDelay > 0}
        style:animation-delay="{msg.animDelay}ms"
      >{msg.type === 'score' ? scoreText(msg) : (msg.content ?? '')}</div>
    {/if}
  {/each}
</main>

<style>
  .output-area {
    flex: 1;
    overflow-y: auto;
    padding: 12px 18px 4px;
    scroll-behavior: smooth;
  }
  .output-area::-webkit-scrollbar        { width: 6px; }
  .output-area::-webkit-scrollbar-track  { background: var(--bg); }
  .output-area::-webkit-scrollbar-thumb  { background: var(--dim); border-radius: 3px; }

  /* ── Staggered reveal ─────────────────────────────────── */
  :global(.msg-stagger) {
    opacity: 0;
    animation: reveal 80ms ease-out forwards;
  }

  /* ── Base row ─────────────────────────────────────────── */
  :global(.msg) {
    display: block;
    margin: 0;
    padding: 1px 0;
    word-wrap: break-word;
    white-space: pre-wrap;
  }

  /* ── Echo ─────────────────────────────────────────────── */
  :global(.msg-echo) {
    color: var(--green-bright);
    opacity: 0.7;
    font-size: 19px;
    margin: 6px 0 2px;
  }
  :global(.msg-echo)::before { content: '> '; }

  /* ── Structural ───────────────────────────────────────── */
  :global(.msg-blank)     { display: block; height: 0.6em; }
  :global(.msg-separator) {
    display: block; border: none;
    border-top: 1px solid var(--dim);
    margin: 6px 0; opacity: 0.5;
  }

  /* ── Content types ────────────────────────────────────── */
  :global(.msg-location) {
    display: block;
    font-size: 26px;
    letter-spacing: 4px;
    color: var(--green-bright);
    text-shadow: var(--glow-bright);
    margin-top: 10px;
    margin-bottom: 2px;
    padding-bottom: 2px;
    border-bottom: 1px solid var(--border);
  }
  :global(.msg-text) {
    color: var(--green);
    text-shadow: 0 0 4px #33ff5733;
    font-size: 20px;
  }
  :global(.msg-error)  { color: var(--red);   text-shadow: 0 0 6px #ff444555; }
  :global(.msg-system) { color: var(--amber);  text-shadow: var(--glow-amber); font-size: 18px; }
  :global(.msg-npc-name) {
    font-size: 22px;
    letter-spacing: 3px;
    color: var(--amber);
    text-shadow: var(--glow-amber);
    margin-top: 8px;
  }
  :global(.msg-footnote) {
    color: var(--green-dim);
    font-size: 17px;
    font-family: var(--font-mono);
    padding-left: 12px;
    border-left: 2px solid var(--dim);
    margin: 4px 0;
    opacity: 0.75;
  }
  :global(.msg-footnote)::before { content: '* '; }
  :global(.msg-item-line)      { color: var(--green);        padding-left: 8px; font-size: 19px; }
  :global(.msg-dialogue-option){ color: var(--green-bright); padding-left: 4px; font-size: 19px; }
  :global(.msg-title-line) {
    display: block;
    font-size: 28px;
    letter-spacing: 5px;
    color: var(--green-bright);
    text-shadow: var(--glow-bright);
    text-align: center;
    margin: 4px 0;
  }
  :global(.msg-score) {
    font-family: var(--font-mono);
    font-size: 17px;
    color: var(--green-dim);
    padding: 6px 12px;
    border: 1px solid var(--border);
    display: inline-block;
    margin: 4px 0;
  }
  :global(.msg-death-line) { color: var(--red); font-size: 19px; }
  :global(.msg-quit)       { color: var(--green-dim); font-style: italic; font-size: 19px; }
  :global(.msg-game-over) {
    display: block;
    text-align: center;
    font-size: 30px;
    letter-spacing: 6px;
    color: var(--amber);
    text-shadow: var(--glow-amber);
    margin: 16px 0;
    animation: flicker 0.3s step-end 3;
  }
</style>
