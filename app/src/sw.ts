/// <reference lib="webworker" />
import { cleanupOutdatedCaches, precacheAndRoute } from 'workbox-precaching'
import { registerRoute } from 'workbox-routing'
import { StaleWhileRevalidate } from 'workbox-strategies'

declare let self: ServiceWorkerGlobalScope

/**
 * SPEC.md §12: "Set a CONTENT_VERSION constant; on version bump the service worker must
 * invalidate cached content but must never wipe learner data." Bump this string whenever
 * /content changes in a way that should force a fresh fetch instead of serving a stale
 * cached copy. This only names a CacheStorage bucket — IndexedDB (learner data) is a
 * completely separate storage API this file never touches.
 */
const CONTENT_VERSION = 'v1'
const CONTENT_CACHE_NAME = `ascent-content-${CONTENT_VERSION}`
const ICON_BASE = '/Nidhi-CAT-App/icons'

precacheAndRoute(self.__WB_MANIFEST)
cleanupOutdatedCaches()

// /content/**.json (questions, syllabus, mocks, etc.) is fetched at runtime, not bundled
// (see app/scripts/sync-content.mjs's header comment) — cache it separately from the
// precached app shell so a content update doesn't require a full JS rebuild to take effect.
registerRoute(
  ({ url }) => url.pathname.includes('/content/'),
  new StaleWhileRevalidate({ cacheName: CONTENT_CACHE_NAME }),
)

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key.startsWith('ascent-content-') && key !== CONTENT_CACHE_NAME)
          .map((key) => caches.delete(key)),
      ),
    ),
  )
})

self.addEventListener('message', (event) => {
  const data = event.data as { type?: string; payload?: { title: string; body: string; tag?: string } } | undefined
  if (data?.type === 'SKIP_WAITING') {
    void self.skipWaiting()
  }
  if (data?.type === 'SHOW_NOTIFICATION' && data.payload) {
    const { title, body, tag } = data.payload
    event.waitUntil(
      self.registration.showNotification(title, {
        body,
        tag: tag ?? 'ascent-notification',
        icon: `${ICON_BASE}/icon-192.png`,
      }),
    )
  }
})

// Local-only notification (SPEC.md §11 Phase 1: "works offline, no backend needed for local
// notifications scheduled by the SW") — clicking it focuses an existing tab or opens a new one.
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  event.waitUntil(
    self.clients.matchAll({ type: 'window' }).then((clients) => {
      const existing = clients[0]
      if (existing) return existing.focus()
      return self.clients.openWindow('/Nidhi-CAT-App/')
    }),
  )
})
