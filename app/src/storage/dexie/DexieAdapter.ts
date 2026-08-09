import type { ExportBundle, StorageAdapter } from '@/storage/StorageAdapter'
import type { Attempt, MasteryState, MockResult, PlanDay, Settings } from '@/types/state'
import { AscentDB, SETTINGS_KEY, type SettingsRow } from './schema'
import {
  migrateAttempt,
  migrateMasteryState,
  migrateMockResult,
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

  async exportAll(): Promise<ExportBundle> {
    const [attempts, masteryStates, planDays, mockResults, settings] = await Promise.all([
      this.listAttempts(),
      this.listMasteryStates(),
      this.listPlanDays(),
      this.listMockResults(),
      this.getSettings(),
    ])
    return {
      exportedAt: new Date().toISOString(),
      attempts,
      masteryStates,
      planDays,
      mockResults,
      settings: settings ?? null,
    }
  }

  async importAll(bundle: ExportBundle): Promise<void> {
    await this.db.transaction(
      'rw',
      [this.db.attempts, this.db.masteryStates, this.db.planDays, this.db.mockResults, this.db.settings],
      async () => {
        await Promise.all([
          this.db.attempts.clear(),
          this.db.masteryStates.clear(),
          this.db.planDays.clear(),
          this.db.mockResults.clear(),
          this.db.settings.clear(),
        ])
        await Promise.all([
          this.db.attempts.bulkPut(bundle.attempts),
          this.db.masteryStates.bulkPut(bundle.masteryStates),
          this.db.planDays.bulkPut(bundle.planDays),
          this.db.mockResults.bulkPut(bundle.mockResults),
          bundle.settings ? this.putSettings(bundle.settings) : Promise.resolve(),
        ])
      },
    )
  }

  async clearAll(): Promise<void> {
    await this.db.transaction(
      'rw',
      [this.db.attempts, this.db.masteryStates, this.db.planDays, this.db.mockResults, this.db.settings],
      async () => {
        await Promise.all([
          this.db.attempts.clear(),
          this.db.masteryStates.clear(),
          this.db.planDays.clear(),
          this.db.mockResults.clear(),
          this.db.settings.clear(),
        ])
      },
    )
  }
}
