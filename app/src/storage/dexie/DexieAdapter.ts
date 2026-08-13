import type { ExportBundle, StorageAdapter } from '@/storage/StorageAdapter'
import type { Attempt, Bookmark, ItemEloState, MasteryState, MockResult, MockSession, PlanDay, Settings, SrsCard } from '@/types/state'
import { AscentDB, MOCK_SESSION_KEY, SETTINGS_KEY, type MockSessionRow, type SettingsRow } from './schema'
import {
  migrateAttempt,
  migrateBookmark,
  migrateItemEloState,
  migrateMasteryState,
  migrateMockResult,
  migrateMockSession,
  migratePlanDay,
  migrateSettings,
  migrateSrsCard,
} from './migrations'

export class DexieAdapter implements StorageAdapter {
  private readonly db: AscentDB

  constructor(dbName?: string) {
    this.db = new AscentDB(dbName)
  }

  async addAttempt(attempt: Attempt): Promise<void> {
    await this.db.attempts.put(attempt)
  }

  async getAttempt(id: string): Promise<Attempt | undefined> {
    const row = await this.db.attempts.get(id)
    return row ? migrateAttempt(row) : undefined
  }

  async listAttempts(filter?: { microTopicId?: string; mode?: Attempt['mode'] }): Promise<Attempt[]> {
    const rows = filter?.microTopicId
      ? await this.db.attempts.where('microTopicIds').equals(filter.microTopicId).toArray()
      : await this.db.attempts.toArray()
    const migrated = rows.map(migrateAttempt)
    return filter?.mode ? migrated.filter((a) => a.mode === filter.mode) : migrated
  }

  async getMasteryState(microTopicId: string): Promise<MasteryState | undefined> {
    const row = await this.db.masteryStates.get(microTopicId)
    return row ? migrateMasteryState(row) : undefined
  }

  async putMasteryState(state: MasteryState): Promise<void> {
    await this.db.masteryStates.put(state)
  }

  async listMasteryStates(): Promise<MasteryState[]> {
    const rows = await this.db.masteryStates.toArray()
    return rows.map(migrateMasteryState)
  }

  async getPlanDay(date: string): Promise<PlanDay | undefined> {
    const row = await this.db.planDays.get(date)
    return row ? migratePlanDay(row) : undefined
  }

  async putPlanDay(day: PlanDay): Promise<void> {
    await this.db.planDays.put(day)
  }

  async listPlanDays(range?: { from: string; to: string }): Promise<PlanDay[]> {
    const rows = range
      ? await this.db.planDays.where('date').between(range.from, range.to, true, true).toArray()
      : await this.db.planDays.toArray()
    return rows.map(migratePlanDay)
  }

  async addMockResult(result: MockResult): Promise<void> {
    await this.db.mockResults.put(result)
  }

  async listMockResults(): Promise<MockResult[]> {
    const rows = await this.db.mockResults.toArray()
    return rows.map(migrateMockResult)
  }

  async getItemElo(questionId: string): Promise<number | undefined> {
    const row = await this.db.itemElo.get(questionId)
    return row ? migrateItemEloState(row).elo : undefined
  }

  async putItemElo(questionId: string, elo: number): Promise<void> {
    const row: ItemEloState = { schemaVersion: 1, questionId, elo }
    await this.db.itemElo.put(row)
  }

  async getSettings(): Promise<Settings | undefined> {
    const row = await this.db.settings.get(SETTINGS_KEY)
    if (!row) return undefined
    const { id: _id, ...settings } = row
    return migrateSettings(settings)
  }

  async putSettings(settings: Settings): Promise<void> {
    const row: SettingsRow = { ...settings, id: SETTINGS_KEY }
    await this.db.settings.put(row)
  }

  async getMockSession(): Promise<MockSession | undefined> {
    const row = await this.db.mockSession.get(MOCK_SESSION_KEY)
    if (!row) return undefined
    const { id: _id, ...session } = row
    return migrateMockSession(session)
  }

  async putMockSession(session: MockSession): Promise<void> {
    const row: MockSessionRow = { ...session, id: MOCK_SESSION_KEY }
    await this.db.mockSession.put(row)
  }

  async clearMockSession(): Promise<void> {
    await this.db.mockSession.delete(MOCK_SESSION_KEY)
  }

  async getSrsCard(id: string): Promise<SrsCard | undefined> {
    const row = await this.db.srsCards.get(id)
    return row ? migrateSrsCard(row) : undefined
  }

  async putSrsCard(card: SrsCard): Promise<void> {
    await this.db.srsCards.put(card)
  }

  async listSrsCards(): Promise<SrsCard[]> {
    const rows = await this.db.srsCards.toArray()
    return rows.map(migrateSrsCard)
  }

  async addBookmark(bookmark: Bookmark): Promise<void> {
    await this.db.bookmarks.put(bookmark)
  }

  async removeBookmark(questionId: string): Promise<void> {
    await this.db.bookmarks.where('questionId').equals(questionId).delete()
  }

  async listBookmarks(): Promise<Bookmark[]> {
    const rows = await this.db.bookmarks.orderBy('createdAt').reverse().toArray()
    return rows.map(migrateBookmark)
  }

  async isBookmarked(questionId: string): Promise<boolean> {
    const count = await this.db.bookmarks.where('questionId').equals(questionId).count()
    return count > 0
  }

  /**
   * See StorageAdapter.resetMicroTopic for what is and isn't cleared, and why.
   *
   * Returns the affected keys so SupabaseSyncAdapter can queue the same deletions remotely —
   * it cannot recompute them afterwards, because by then the local rows are already gone.
   */
  async resetMicroTopicCollecting(microTopicId: string): Promise<{
    attemptIds: string[]
    srsCardIds: string[]
    bookmarkIds: string[]
    questionIds: string[]
    hadMastery: boolean
  }> {
    return this.db.transaction(
      'rw',
      [this.db.attempts, this.db.masteryStates, this.db.srsCards, this.db.bookmarks, this.db.itemElo],
      async () => {
        const attempts = await this.db.attempts.where('microTopicIds').equals(microTopicId).toArray()
        const attemptIds = attempts.map((a) => a.id)
        const touchedQuestionIds = [...new Set(attempts.map((a) => a.questionId))]

        const srsCards = await this.db.srsCards.where('microTopicId').equals(microTopicId).toArray()
        const bookmarks = await this.db.bookmarks.where('microTopicId').equals(microTopicId).toArray()
        const hadMastery = (await this.db.masteryStates.get(microTopicId)) !== undefined

        await this.db.attempts.bulkDelete(attemptIds)
        await this.db.masteryStates.delete(microTopicId)
        await this.db.srsCards.bulkDelete(srsCards.map((c) => c.id))
        await this.db.bookmarks.bulkDelete(bookmarks.map((b) => b.id))

        // Item Elo is keyed by question, and a question can belong to a set that spans more than
        // one micro-topic. Only drop the rating once the question has no surviving attempt —
        // otherwise resetting one topic would quietly reset an unrelated one's calibration.
        // One scan of what survived, rather than a count() per question — a topic reset can
        // touch a few hundred questions and `attempts` has no questionId index.
        const survivingQuestionIds = new Set((await this.db.attempts.toArray()).map((a) => a.questionId))
        const orphaned = touchedQuestionIds.filter((id) => !survivingQuestionIds.has(id))
        await this.db.itemElo.bulkDelete(orphaned)

        return {
          attemptIds,
          srsCardIds: srsCards.map((c) => c.id),
          bookmarkIds: bookmarks.map((b) => b.id),
          questionIds: orphaned,
          hadMastery,
        }
      },
    )
  }

  async resetMicroTopic(microTopicId: string): Promise<void> {
    await this.resetMicroTopicCollecting(microTopicId)
  }

  async exportAll(): Promise<ExportBundle> {
    const [attempts, masteryStates, planDays, mockResults, itemEloStates, settings, mockSession, srsCards, bookmarks] =
      await Promise.all([
        this.listAttempts(),
        this.listMasteryStates(),
        this.listPlanDays(),
        this.listMockResults(),
        this.db.itemElo.toArray().then((rows) => rows.map(migrateItemEloState)),
        this.getSettings(),
        this.getMockSession(),
        this.listSrsCards(),
        this.listBookmarks(),
      ])
    return {
      exportedAt: new Date().toISOString(),
      attempts,
      masteryStates,
      planDays,
      mockResults,
      itemEloStates,
      settings: settings ?? null,
      mockSession: mockSession ?? null,
      srsCards,
      bookmarks,
    }
  }

  private allTables() {
    return [
      this.db.attempts,
      this.db.masteryStates,
      this.db.planDays,
      this.db.mockResults,
      this.db.itemElo,
      this.db.settings,
      this.db.mockSession,
      this.db.srsCards,
      this.db.bookmarks,
    ]
  }

  async importAll(bundle: ExportBundle): Promise<void> {
    await this.db.transaction('rw', this.allTables(), async () => {
      await Promise.all(this.allTables().map((table) => table.clear()))
      await Promise.all([
        this.db.attempts.bulkPut(bundle.attempts),
        this.db.masteryStates.bulkPut(bundle.masteryStates),
        this.db.planDays.bulkPut(bundle.planDays),
        this.db.mockResults.bulkPut(bundle.mockResults),
        this.db.itemElo.bulkPut(bundle.itemEloStates),
        bundle.settings ? this.putSettings(bundle.settings) : Promise.resolve(),
        bundle.mockSession ? this.putMockSession(bundle.mockSession) : Promise.resolve(),
        this.db.srsCards.bulkPut(bundle.srsCards ?? []),
        this.db.bookmarks.bulkPut(bundle.bookmarks ?? []),
      ])
    })
  }

  async clearAll(): Promise<void> {
    await this.db.transaction('rw', this.allTables(), async () => {
      await Promise.all(this.allTables().map((table) => table.clear()))
    })
  }
}
