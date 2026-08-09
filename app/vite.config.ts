import path from 'node:path'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { VitePWA } from 'vite-plugin-pwa'

// https://vite.dev/config/
export default defineConfig({
  base: '/Nidhi-CAT-App/',
  plugins: [
    react(),
    tailwindcss(),
    // SPEC.md §7: "vite-plugin-pwa (Workbox) for the service worker + install prompt."
    // injectManifest (not the default generateSW) because the service worker needs custom
    // logic beyond precaching: the CONTENT_VERSION-scoped runtime cache and the message-based
    // local-notification handler both live in src/sw.ts.
    VitePWA({
      strategies: 'injectManifest',
      srcDir: 'src',
      filename: 'sw.ts',
      injectRegister: false,
      // 'prompt', not 'autoUpdate' — SPEC.md §12 says a content/app update must never silently
      // disrupt learner state; auto-reloading mid-mock would do exactly that. The app surfaces
      // its own "update available" banner (src/pwa/pwaUpdate.ts) and only reloads on click.
      registerType: 'prompt',
      devOptions: { enabled: true, type: 'module' },
      manifest: {
        id: '/Nidhi-CAT-App/',
        name: 'Ascent — CAT 2026 Prep',
        short_name: 'Ascent',
        description: 'Adaptive CAT 2026 preparation: drills, mocks, planner, and spaced review.',
        start_url: '/Nidhi-CAT-App/',
        scope: '/Nidhi-CAT-App/',
        display: 'standalone',
        // #0a0a0a is the sRGB equivalent of index.css's dark --background (oklch(0.145 0 0)) —
        // hex here, not oklch(), since manifest parsers vary in CSS Color 4 support and this
        // field controls OS-level chrome (splash screen, status bar), unlike in-app CSS.
        background_color: '#0a0a0a',
        theme_color: '#0a0a0a',
        icons: [
          { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
          { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
          { src: 'icons/icon-maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        ],
      },
    }),
  ],
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
