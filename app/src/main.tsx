import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { HashRouter } from 'react-router-dom'
import { registerSW } from 'virtual:pwa-register'
import './index.css'
import App from './App.tsx'
import { reportNeedRefresh, reportOfflineReady } from './pwa/pwaUpdate'

// registerType: 'prompt' (vite.config.ts) — onNeedRefresh only records that an update is
// available; nothing reloads until the user clicks the UpdateBanner. SPEC.md §12.
const updateSW = registerSW({
  onNeedRefresh() {
    reportNeedRefresh(updateSW)
  },
  onOfflineReady() {
    reportOfflineReady()
  },
})

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <HashRouter>
      <App />
    </HashRouter>
  </StrictMode>,
)
