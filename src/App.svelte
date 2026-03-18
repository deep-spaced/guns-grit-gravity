<script>
  import { onMount }   from 'svelte';
  import { connected, gameOver, connect } from './lib/game.js';
  import OutputArea from './lib/OutputArea.svelte';
  import StatsBar   from './lib/StatsBar.svelte';
  import InputBar   from './lib/InputBar.svelte';

  onMount(connect);

  $: statusLabel = $connected ? 'CONNECTED'
                 : $gameOver  ? 'SESSION ENDED'
                 :              'CONNECTING…';
</script>

<div class="crt-outer">
  <div class="crt-bezel">
    <div class="crt-screen">

      <!-- Overlay effects -->
      <div class="scanlines" aria-hidden="true"></div>
      <div class="vignette"  aria-hidden="true"></div>

      <!-- Terminal -->
      <div class="terminal">

        <header class="term-header">
          <span class="term-title">GUNS, GRIT &amp; GRAVITY</span>
          <span class="term-meta">
            <span
              class="status-dot"
              class:connected={$connected}
              class:disconnected={!$connected}
            ></span>
            <span>{statusLabel}</span>
          </span>
        </header>

        <OutputArea />
        <StatsBar />
        <InputBar />

      </div>
    </div>
  </div>
</div>

<style>
  /* ── CRT shell ──────────────────────────────────────────── */
  .crt-outer  { width: 100vw; height: 100vh; background: #000; }
  .crt-bezel  { width: 100%; height: 100%; background: #000; overflow: hidden; }

  .crt-screen {
    position: relative;
    width: 100%; height: 100%;
    background: var(--bg);
    overflow: hidden;
    box-shadow: inset 0 0 120px rgba(0,0,0,0.5);
    animation: flicker 8s step-end infinite;
  }

  /* Scanlines */
  .scanlines {
    position: absolute; inset: 0;
    background: repeating-linear-gradient(
      to bottom,
      transparent 0px, transparent 3px,
      rgba(0,0,0,0.18) 3px, rgba(0,0,0,0.18) 4px
    );
    pointer-events: none; z-index: 10;
  }

  /* Vignette */
  .vignette {
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at center, transparent 60%, rgba(0,0,0,0.55) 100%);
    pointer-events: none; z-index: 11;
  }

  /* ── Terminal layout ────────────────────────────────────── */
  .terminal {
    position: relative; z-index: 1;
    display: flex; flex-direction: column; height: 100%;
    font-family: var(--font-main);
    font-size: 20px;
    color: var(--green);
    line-height: 1.45;
  }

  /* Header */
  .term-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 6px 16px;
    border-bottom: 1px solid var(--border);
    background: var(--bg-panel);
    flex-shrink: 0;
  }
  .term-title {
    font-size: 22px; letter-spacing: 3px;
    text-shadow: var(--glow); color: var(--green-bright);
  }
  .term-meta {
    display: flex; align-items: center; gap: 6px;
    font-size: 14px; font-family: var(--font-mono);
    color: var(--green-dim); letter-spacing: 1px;
  }

  /* Status dot */
  .status-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green-dim);
    transition: background 0.3s, box-shadow 0.3s;
  }
  .status-dot.connected {
    background: var(--green); box-shadow: var(--glow);
    animation: pulse 2.4s ease-in-out infinite;
  }
  .status-dot.disconnected {
    background: var(--red); box-shadow: 0 0 6px var(--red);
  }

  /* Responsive */
  @media (max-width: 600px) {
    .terminal   { font-size: 17px; }
    .term-title { font-size: 18px; letter-spacing: 1px; }
  }
</style>
