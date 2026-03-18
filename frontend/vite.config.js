import { defineConfig } from 'vite';
import { svelte }       from '@sveltejs/vite-plugin-svelte';
import path             from 'path';

export default defineConfig({
  plugins: [svelte()],

  // GitHub Pages: repo is deep-spaced/claude-exploration
  base: '/claude-exploration/',

  resolve: {
    alias: {
      // @data → guns-grit-gravity-web/data/ (JSON game data, shared with Python backend)
      '@data': path.resolve(__dirname, '../data'),
    },
  },

  // Local dev: proxy WebSocket to Python server if you want to test
  // the Python backend side-by-side. Not needed for GH Pages build.
  server: {
    port: 5173,
  },
});
