/**
 * Minimal external store (useSyncExternalStore, no state library needed) for the service
 * worker's update lifecycle. registerType is 'prompt' (see vite.config.ts) precisely so this
 * never reloads on its own — SPEC.md §12: a content/app update must never disrupt a
 * mid-session learner, e.g. mid-mock. applyUpdate() only runs when the user clicks the banner.
 */

interface PwaUpdateState {
  needRefresh: boolean
  offlineReady: boolean
}

let snapshot: PwaUpdateState = { needRefresh: false, offlineReady: false }
let doUpdate: ((reloadPage?: boolean) => Promise<void>) | null = null
const listeners = new Set<() => void>()

function setSnapshot(patch: Partial<PwaUpdateState>): void {
  snapshot = { ...snapshot, ...patch }
  for (const listener of listeners) listener()
}

export function reportNeedRefresh(updateFn: (reloadPage?: boolean) => Promise<void>): void {
  doUpdate = updateFn
  setSnapshot({ needRefresh: true })
}

export function reportOfflineReady(): void {
  setSnapshot({ offlineReady: true })
}

export function subscribe(listener: () => void): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function getSnapshot(): PwaUpdateState {
  return snapshot
}

export async function applyUpdate(): Promise<void> {
  if (doUpdate) await doUpdate(true)
}
