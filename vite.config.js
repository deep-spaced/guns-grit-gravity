import { defineConfig } from 'vite';
import { svelte }       from '@sveltejs/vite-plugin-svelte';
import path             from 'path';

export default defineConfig({
  plugins: [svelte()],

  // GitHub Pages: repo is deep-spaced/guns-grit-gravity
  base: '/guns-grit-gravity/',

  resolve: {
    alias: {
      // @data → data/ (JSON game data)
      '@data': path.resolve(__dirname, 'data'),
    },
  },

  server: {
    port: 5173,
  },
});
