import { SupabaseSyncAdapter, type FlushResult } from './supabase/SupabaseSyncAdapter'
import type { StorageAdapter } from './StorageAdapter'

/**
 * Single import site for the storage layer (SPEC.md §1 rule 2). Milestone 16:
 * `SupabaseSyncAdapter` wraps `DexieAdapter` — every read/write still goes straight to
 * IndexedDB (unchanged behaviour for every component built before this milestone), and
 * additionally best-effort syncs to Supabase when configured + signed in. No component needed
 * to change for this swap, exactly as the interface was designed for from Milestone 2.
 */
const adapter = new SupabaseSyncAdapter()
export const storage: StorageAdapter = adapter

/** Not part of StorageAdapter (every other adapter implementation is free to no-op or omit it) —
 * called from App.tsx on mount and on 'online', see pwa/... sibling pattern for why a plain
 * module-level function beats a context here. */
export function flushSyncQueue(): Promise<FlushResult> {
  return adapter.flushQueue()
}

/**
 * Full reset, including the remote copy. `storage.clearAll()` does the same work, but its
 * StorageAdapter signature returns void — this variant reports whether the Supabase side was
 * actually cleared, which Settings needs so it can say "this device only" instead of implying a
 * wipe that did not reach the server.
 */
export function clearAllProgress(): Promise<{ remoteCleared: boolean; error: string | null }> {
  return adapter.clearAllWithRemote()
}

export type { ExportBundle, StorageAdapter } from './StorageAdapter'
export type { FlushResult } from './supabase/SupabaseSyncAdapter'
