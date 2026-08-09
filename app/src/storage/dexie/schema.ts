import Dexie, { type Table } from 'dexie'
import type { Attempt, ItemEloState, MasteryState, MockResult, MockSession, PlanDay, Settings, SrsCard } from '@/types/state'

/** Settings is a singleton row; this fixed key is how it's addressed in the table. */
export const SETTINGS_KEY = 'singleton'
export type SettingsRow = Settings & { id: typeof SETTINGS_KEY }

/** MockSession is also a singleton row (SPEC.md §9.1 — at most one in-progress mock). */
export const MOCK_SESSION_KEY = 'singleton'
export type MockSessionRow = MockSession & { id: typeof MOCK_SESSION_KEY }

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
  itemElo!: Table<ItemEloState, string>
  settings!: Table<SettingsRow, string>
  mockSession!: Table<MockSessionRow, string>
  srsCards!: Table<SrsCard, string>

  constructor(name = 'ascent') {
    super(name)
    this.version(1).stores({
      attempts: 'id, mode, startedAt, *microTopicIds',
      masteryStates: 'microTopicId, status',
      planDays: 'date, status',
      mockResults: 'id, mockId, takenAt',
      settings: 'id',
    })
    // Milestone 5: item-level Elo (SPEC.md §8.3), keyed by questionId.
    this.version(2).stores({
      itemElo: 'questionId',
    })
    // Milestone 10: in-progress mock crash recovery (SPEC.md §9.1).
    this.version(3).stores({
      mockSession: 'id',
    })
    // Milestone 12: card-level SRS (SPEC.md §8.4) — formula cards + mistake questions.
    this.version(4).stores({
      srsCards: 'id, cardType, microTopicId, nextReviewAt',
    })
  }
}
