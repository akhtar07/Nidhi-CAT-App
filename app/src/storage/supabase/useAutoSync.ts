import { useEffect } from 'react'
import { flushSyncQueue } from '@/storage'

const PERIODIC_FLUSH_MS = 5 * 60 * 1000

/** SPEC.md §16: "syncs on reconnect." Flushes on mount (covers "app was opened offline, wrote
 * things, closed, reopened online"), on the browser's 'online' event, and periodically as a
 * fallback for long sessions — same reasoning as MockPlayer's 5-second crash-recovery interval,
 * just a much longer period since this isn't safety-critical. A no-op whenever Supabase isn't
 * configured or no one's signed in (see SupabaseSyncAdapter.flushQueue). */
export function useAutoSync(): void {
  useEffect(() => {
    void flushSyncQueue()
    function onOnline() {
      void flushSyncQueue()
    }
    window.addEventListener('online', onOnline)
    const interval = setInterval(() => void flushSyncQueue(), PERIODIC_FLUSH_MS)
    return () => {
      window.removeEventListener('online', onOnline)
      clearInterval(interval)
    }
  }, [])
}
