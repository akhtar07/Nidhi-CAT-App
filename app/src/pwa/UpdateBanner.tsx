import { useSyncExternalStore } from 'react'
import { Button } from '@/components/ui/button'
import { applyUpdate, getSnapshot, subscribe } from './pwaUpdate'

/** SPEC.md §12: content/app updates must never silently disrupt a session — this only ever
 * appears after a user click, never auto-reloads. See pwaUpdate.ts for why. */
export function UpdateBanner() {
  const { needRefresh } = useSyncExternalStore(subscribe, getSnapshot, getSnapshot)
  if (!needRefresh) return null

  return (
    <div className="fixed inset-x-0 bottom-0 z-50 flex items-center justify-between gap-3 border-t border-border bg-card px-4 py-3 text-sm shadow-lg">
      <span>A new version of Ascent is ready.</span>
      <Button size="sm" onClick={() => void applyUpdate()}>
        Refresh
      </Button>
    </div>
  )
}
