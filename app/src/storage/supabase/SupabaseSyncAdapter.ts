import { getSupabaseClient } from '@/lib/supabaseClient'
import { DexieAdapter } from '@/storage/dexie/DexieAdapter'
import type { ExportBundle, StorageAdapter } from '@/storage/StorageAdapter'
import type { Attempt, Bookmark, MasteryState, MockResult, MockSession, PlanDay, Settings, SrsCard } from '@/types/state'
import { SyncQueueStore } from './syncQueueStore'
import type { SyncQueueEntry, SyncTable } from './syncQueue'
import {
  attemptToRow,
  bookmarkToRow,
  itemEloToRow,
  masteryStateToRow,
  mockResultToRow,
  planDayToRow,
  settingsToRow,
  srsCardToRow,
  TABLE_KEY_COLUMN,
} from './toRow'

export interface FlushResult {
  flushed: number
  remaining: number
  /** null when nothing was attempted (offline, unauthenticated, or unconfigured) — distinct from
   * 0, which means "attempted and nothing failed." */
  error: string | null
}

/**
 * SPEC.md §1 rule 2 / §12 option B: "A SupabaseAdapter implementing the same [StorageAdapter]
 * interface is added later without touching any component." Every read and every synchronous
 * write still goes straight through `DexieAdapter` — IndexedDB remains the actual source of
 * truth (CLAUDE.md) — this class only *additionally* records mutations into a local outbox
 * (syncQueueStore) and best-effort pushes that outbox to Supabase, so:
 *   - the app behaves identically to plain DexieAdapter when Supabase isn't configured, isn't
 *     signed in, or the network is down (SPEC.md §16: "Airplane mode: full drill session works")
 *   - once online + signed in, `flushQueue()` (called on mount, on 'online', and periodically —
 *     see App.tsx) pushes everything queued since the last successful flush ("syncs on
 *     reconnect").
 * mockSession is deliberately NOT synced — SPEC.md's crash-recovery requirement is local-only
 * ("persist... on reload, resume with correct remaining time"), and there's no requirement to
 * resume an in-progress mock on a *different* device mid-sitting.
 */
export class SupabaseSyncAdapter implements StorageAdapter {
  private readonly dexie: DexieAdapter
  private readonly queue: SyncQueueStore

  constructor(dbName?: string) {
    this.dexie = new DexieAdapter(dbName)
    this.queue = new SyncQueueStore(dbName)
  }

  private async enqueue(table: SyncTable, key: string, payload?: unknown, op: 'upsert' | 'delete' = 'upsert') {
    await this.queue.enqueue({ table, op, key, payload, createdAt: Date.now() })
  }

  async addAttempt(attempt: Attempt): Promise<void> {
    await this.dexie.addAttempt(attempt)
    await this.enqueue('attempts', attempt.id, attempt)
  }

  getAttempt(id: string): Promise<Attempt | undefined> {
    return this.dexie.getAttempt(id)
  }

  listAttempts(filter?: { microTopicId?: string; mode?: Attempt['mode'] }): Promise<Attempt[]> {
    return this.dexie.listAttempts(filter)
  }

  async putMasteryState(state: MasteryState): Promise<void> {
    await this.dexie.putMasteryState(state)
    await this.enqueue('mastery_states', state.microTopicId, state)
  }

  getMasteryState(microTopicId: string): Promise<MasteryState | undefined> {
    return this.dexie.getMasteryState(microTopicId)
  }

  listMasteryStates(): Promise<MasteryState[]> {
    return this.dexie.listMasteryStates()
  }

  async putPlanDay(day: PlanDay): Promise<void> {
    await this.dexie.putPlanDay(day)
    await this.enqueue('plan_days', day.date, day)
  }

  getPlanDay(date: string): Promise<PlanDay | undefined> {
    return this.dexie.getPlanDay(date)
  }

  listPlanDays(range?: { from: string; to: string }): Promise<PlanDay[]> {
    return this.dexie.listPlanDays(range)
  }

  async addMockResult(result: MockResult): Promise<void> {
    await this.dexie.addMockResult(result)
    await this.enqueue('mock_results', result.id, result)
  }

  listMockResults(): Promise<MockResult[]> {
    return this.dexie.listMockResults()
  }

  async putItemElo(questionId: string, elo: number): Promise<void> {
    await this.dexie.putItemElo(questionId, elo)
    await this.enqueue('item_elo', questionId, { questionId, elo })
  }

  getItemElo(questionId: string): Promise<number | undefined> {
    return this.dexie.getItemElo(questionId)
  }

  async putSettings(settings: Settings): Promise<void> {
    await this.dexie.putSettings(settings)
    await this.enqueue('settings', 'singleton', settings)
  }

  getSettings(): Promise<Settings | undefined> {
    return this.dexie.getSettings()
  }

  getMockSession(): Promise<MockSession | undefined> {
    return this.dexie.getMockSession()
  }

  putMockSession(session: MockSession): Promise<void> {
    return this.dexie.putMockSession(session)
  }

  clearMockSession(): Promise<void> {
    return this.dexie.clearMockSession()
  }

  async putSrsCard(card: SrsCard): Promise<void> {
    await this.dexie.putSrsCard(card)
    await this.enqueue('srs_cards', card.id, card)
  }

  getSrsCard(id: string): Promise<SrsCard | undefined> {
    return this.dexie.getSrsCard(id)
  }

  listSrsCards(): Promise<SrsCard[]> {
    return this.dexie.listSrsCards()
  }

  async addBookmark(bookmark: Bookmark): Promise<void> {
    await this.dexie.addBookmark(bookmark)
    await this.enqueue('bookmarks', bookmark.id, bookmark)
  }

  async removeBookmark(questionId: string): Promise<void> {
    // The bookmarks table's sync key is the bookmark's own id (matches Supabase's primary key),
    // not questionId — look up which row(s) are being deleted locally first so the delete queue
    // entry carries the right key.
    const existing = await this.dexie.listBookmarks()
    const toRemove = existing.filter((b) => b.questionId === questionId)
    await this.dexie.removeBookmark(questionId)
    await Promise.all(toRemove.map((b) => this.enqueue('bookmarks', b.id, undefined, 'delete')))
  }

  listBookmarks(): Promise<Bookmark[]> {
    return this.dexie.listBookmarks()
  }

  isBookmarked(questionId: string): Promise<boolean> {
    return this.dexie.isBookmarked(questionId)
  }

  exportAll(): Promise<ExportBundle> {
    return this.dexie.exportAll()
  }

  importAll(bundle: ExportBundle): Promise<void> {
    return this.dexie.importAll(bundle)
  }

  clearAll(): Promise<void> {
    return this.dexie.clearAll()
  }

  async queueLength(): Promise<number> {
    return this.queue.length()
  }

  /** Converts one queue entry to a Supabase row, given the caller already resolved userId. */
  private toRow(entry: SyncQueueEntry, userId: string): Record<string, unknown> {
    const payload = entry.payload
    switch (entry.table) {
      case 'attempts':
        return attemptToRow(payload as Attempt, userId)
      case 'mastery_states':
        return masteryStateToRow(payload as MasteryState, userId)
      case 'plan_days':
        return planDayToRow(payload as PlanDay, userId)
      case 'mock_results':
        return mockResultToRow(payload as MockResult, userId)
      case 'item_elo':
        return itemEloToRow(payload as { questionId: string; elo: number }, userId)
      case 'settings':
        return settingsToRow(payload as Settings, userId)
      case 'srs_cards':
        return srsCardToRow(payload as SrsCard, userId)
      case 'bookmarks':
        return bookmarkToRow(payload as Bookmark, userId)
    }
  }

  /** SPEC.md §16: "syncs on reconnect." Best-effort: any failure (offline, RLS, etc.) leaves the
   * queue untouched so the next flush attempt retries everything, in order. */
  async flushQueue(): Promise<FlushResult> {
    const supabase = getSupabaseClient()
    if (!supabase) return { flushed: 0, remaining: await this.queue.length(), error: null }

    const {
      data: { session },
    } = await supabase.auth.getSession()
    if (!session) return { flushed: 0, remaining: await this.queue.length(), error: null }
    const userId = session.user.id

    const entries = await this.queue.list()
    if (entries.length === 0) return { flushed: 0, remaining: 0, error: null }

    // Only the latest queued entry per (table, key) needs to reach Supabase — earlier ones for
    // the same row are superseded (e.g. putSettings called repeatedly before ever going online).
    const latestByRowKey = new Map<string, SyncQueueEntry>()
    for (const entry of entries) latestByRowKey.set(`${entry.table}:${entry.key}`, entry)

    const byTable = new Map<SyncTable, SyncQueueEntry[]>()
    for (const entry of latestByRowKey.values()) {
      const bucket = byTable.get(entry.table) ?? []
      bucket.push(entry)
      byTable.set(entry.table, bucket)
    }

    try {
      for (const [table, tableEntries] of byTable) {
        const upserts = tableEntries.filter((e) => e.op === 'upsert')
        const deletes = tableEntries.filter((e) => e.op === 'delete')
        if (upserts.length > 0) {
          const rows = upserts.map((e) => this.toRow(e, userId))
          const { error } = await supabase.from(table).upsert(rows)
          if (error) throw new Error(`${table} upsert: ${error.message}`)
        }
        if (deletes.length > 0) {
          const keyColumn = TABLE_KEY_COLUMN[table]
          const { error } = await supabase
            .from(table)
            .delete()
            .eq('user_id', userId)
            .in(
              keyColumn,
              deletes.map((e) => e.key),
            )
          if (error) throw new Error(`${table} delete: ${error.message}`)
        }
      }
    } catch (e) {
      return { flushed: 0, remaining: entries.length, error: (e as Error).message }
    }

    const seqs = entries.map((e) => e.seq).filter((s): s is number => s !== undefined)
    await this.queue.removeBySeq(seqs)
    return { flushed: entries.length, remaining: 0, error: null }
  }
}
