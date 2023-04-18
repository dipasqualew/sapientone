import { defineConfig } from 'vite'
import { resolve } from 'path'

import vue from '@vitejs/plugin-vue'
import { crx } from '@crxjs/vite-plugin'
import manifest from './src/manifest.json' assert { type: 'json' } // Node >=17


// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue(), crx({ manifest })],
})
