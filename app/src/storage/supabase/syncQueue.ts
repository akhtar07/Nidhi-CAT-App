/**
 * Milestone 16 (SPEC.md §12 option B). IndexedDB (DexieAdapter) stays the source of truth
 * (CLAUDE.md: "All learner state behind the StorageAdapter interface. IndexedDB is v1") — this
 * queue only tracks which local writes still need pushing to Supabase, so SupabaseSyncAdapter
 * can satisfy SPEC.md §16's "Airplane mode: full drill session works, syncs on reconnect"
 * without ever blocking a write on network availability.
 */

export type SyncTable =
  | 'attempts'
  | 'mastery_states'
  | 'plan_days'
  | 'mock_results'
  | 'item_elo'
  | 'settings'
  | 'srs_cards'
  | 'bookmarks'

export interface SyncQueueEntry {
  /** Dexie auto-increment primary key (`++seq` in schema.ts) — preserves write order for flush. */
  seq?: number
  table: SyncTable
  op: 'upsert' | 'delete'
  /** The row's natural key (matches the Postgres table's key column) — used as the delete target
   * and to de-duplicate superseded queue entries for the same row before flushing. */
  key: string
  /** The full record for 'upsert'; unused for 'delete'. */
  payload?: unknown
  createdAt: number
}
