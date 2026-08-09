import path from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  base: '/Nidhi-CAT-App/',
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(import.meta.dirname, './src'),
    },
  },
  // react-katex ships a UMD bundle that calls require('prop-types') at
  // module-eval time; Rolldown's dev server doesn't polyfill a bare
  // `require` for on-demand-loaded modules, only for ones pre-bundled
  // through optimizeDeps. Forcing both into the pre-bundle gives them
  // proper CJS->ESM interop and fixes a blank-page crash on load.
  optimizeDeps: {
    include: ['react-katex', 'prop-types'],
  },
})
