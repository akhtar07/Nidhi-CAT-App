import { AscentDB } from '@/storage/dexie/schema'
import type { SyncQueueEntry } from './syncQueue'

/**
 * Its own small connection to the same-named IndexedDB database DexieAdapter uses — Dexie
 * multiplexes multiple connections to one database name safely, so this doesn't compete with
 * DexieAdapter's own connection. Kept separate rather than reaching into DexieAdapter's private
 * `db` field, so DexieAdapter's public surface (and its existing tests) stay untouched.
 */
export class SyncQueueStore {
  private readonly db: AscentDB

  constructor(dbName?: string) {
    this.db = new AscentDB(dbName)
  }

  async enqueue(entry: Omit<SyncQueueEntry, 'seq'>): Promise<void> {
    await this.db.syncQueue.add(entry as SyncQueueEntry)
  }

  async list(): Promise<SyncQueueEntry[]> {
    return this.db.syncQueue.orderBy('seq').toArray()
  }

  async removeBySeq(seqs: number[]): Promise<void> {
    await this.db.syncQueue.bulkDelete(seqs)
  }

  async length(): Promise<number> {
    return this.db.syncQueue.count()
  }

  /** Drops every pending entry. Only for a full reset — see SupabaseSyncAdapter.clearAll, where
   * flushing a queue full of upserts after the wipe would restore what was just deleted. */
  async clear(): Promise<void> {
    await this.db.syncQueue.clear()
  }
}
