<script>
  import { stats } from './game.js';

  let prevStats = null;
  let flashFields = {};

  // Flash a field when its value changes
  $: if ($stats) {
    if (prevStats) {
      ['score', 'credits', 'turns', 'rank'].forEach(k => {
        if ($stats[k] !== prevStats[k]) {
          flashFields[k] = true;
          setTimeout(() => { flashFields[k] = false; flashFields = flashFields; }, 800);
        }
      });
    }
    prevStats = { ...$stats };
  }
</script>

{#if $stats}
  <div class="stats-bar">
    <span class:updated={flashFields.score}>
      SCORE: {$stats.score}/{$stats.max_score}
    </span>
    <span class:updated={flashFields.credits}>
      CREDITS: {$stats.credits}
    </span>
    <span class:updated={flashFields.turns}>
      TURN: {$stats.turns}
    </span>
    <span class:updated={flashFields.rank}>
      RANK: {$stats.rank.toUpperCase()}
    </span>
  </div>
{/if}

<style>
  .stats-bar {
    display: flex;
    gap: 24px;
    padding: 4px 18px;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    background: var(--bg-panel);
    font-size: 14px;
    font-family: var(--font-mono);
    color: var(--green-dim);
    letter-spacing: 1px;
    flex-shrink: 0;
  }

  span { transition: color 0.2s; }
  span.updated {
    color: var(--green-bright);
    text-shadow: var(--glow-bright);
  }

  @media (max-width: 600px) {
    .stats-bar { font-size: 12px; gap: 12px; }
  }
</style>
