import type { ExportBundle, StorageAdapter } from '@/storage/StorageAdapter'
import type { Attempt, ItemEloState, MasteryState, MockResult, MockSession, PlanDay, Settings } from '@/types/state'
import { AscentDB, MOCK_SESSION_KEY, SETTINGS_KEY, type MockSessionRow, type SettingsRow } from './schema'
import {
  migrateAttempt,
  migrateItemEloState,
  migrateMasteryState,
  migrateMockResult,
  migrateMockSession,
  migratePlanDay,
  migrateSettings,
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

  async exportAll(): Promise<ExportBundle> {
    const [attempts, masteryStates, planDays, mockResults, itemEloStates, settings, mockSession] = await Promise.all([
      this.listAttempts(),
      this.listMasteryStates(),
      this.listPlanDays(),
      this.listMockResults(),
      this.db.itemElo.toArray().then((rows) => rows.map(migrateItemEloState)),
      this.getSettings(),
      this.getMockSession(),
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
      ])
    })
  }

  async clearAll(): Promise<void> {
    await this.db.transaction('rw', this.allTables(), async () => {
      await Promise.all(this.allTables().map((table) => table.clear()))
    })
  }
}
