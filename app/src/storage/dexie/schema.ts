import Dexie, { type Table } from 'dexie'
import type { Attempt, MasteryState, MockResult, PlanDay, Settings } from '@/types/state'

/** Settings is a singleton row; this fixed key is how it's addressed in the table. */
export const SETTINGS_KEY = 'singleton'
export type SettingsRow = Settings & { id: typeof SETTINGS_KEY }

/**
 * Dexie's own `.version(N).stores(...)` versions the IndexedDB structure
 * (tables/indexes) — separate from the per-record `schemaVersion` field on
 * each stored object (see storage/dexie/migrations.ts), which versions the
 * *shape* of a record independently of the table structure.
 */
export class AscentDB extends Dexie {
  attempts!: Table<Attempt, string>
  masteryStates!: Table<MasteryState, string>
  planDays!: Table<PlanDay, string>
  mockResults!: Table<MockResult, string>
  settings!: Table<SettingsRow, string>

  constructor(name = 'ascent') {
    super(name)
    this.version(1).stores({
      attempts: 'id, mode, startedAt, *microTopicIds',
      masteryStates: 'microTopicId, status',
      planDays: 'date, status',
      mockResults: 'id, mockId, takenAt',
      settings: 'id',
    })
  }
}
