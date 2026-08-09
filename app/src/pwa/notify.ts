/**
 * SPEC.md §11 Phase 1: "Web Push via service worker for the daily nudge — works offline, no
 * backend needed for local notifications scheduled by the SW." This is a locally-triggered
 * notification (the app, while open, asks its own active service worker to show one) — not a
 * true background push, which needs a push subscription + a server to trigger it (Phase 2,
 * Supabase). Honest limitation, documented here and in PROGRESS.md: it can only fire while the
 * app has been opened that day, not wake a fully closed tab.
 */

export async function isNotificationSupported(): Promise<boolean> {
  return 'serviceWorker' in navigator && 'Notification' in window
}

export async function requestNotificationPermission(): Promise<NotificationPermission> {
  if (!('Notification' in window)) return 'denied'
  return Notification.requestPermission()
}

export async function showLocalNotification(title: string, body: string, tag = 'ascent-nudge'): Promise<void> {
  if (!('serviceWorker' in navigator) || Notification.permission !== 'granted') return
  const registration = await navigator.serviceWorker.ready
  registration.active?.postMessage({ type: 'SHOW_NOTIFICATION', payload: { title, body, tag } })
}
