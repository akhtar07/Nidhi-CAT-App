import type { Attempt, Bookmark, ItemEloState, MasteryState, MockResult, MockSession, PlanDay, Settings, SrsCard } from '@/types/state'

/**
 * Per-record schema migrations (SPEC.md §5.2: "Every schema gets a
 * schemaVersion field and a migration function from day one"). Only
 * schemaVersion 1 exists for every type today, so each migration map below
 * is empty — this is the plumbing being in place, not a claim that a
 * version-2 migration exists yet. When a record's shape changes, bump
 * CURRENT_SCHEMA_VERSION for that type and add a step here keyed by the
 * *source* version; migrateRecord() chains steps until the record reaches
 * current.
 */
export const CURRENT_SCHEMA_VERSION = {
  attempt: 1,
  masteryState: 1,
  planDay: 1,
  mockResult: 1,
  settings: 1,
  itemEloState: 1,
  mockSession: 1,
  srsCard: 1,
  bookmark: 1,
} as const

type Migration<T> = (record: T) => T

const attemptMigrations: Record<number, Migration<Attempt>> = {}
const masteryStateMigrations: Record<number, Migration<MasteryState>> = {}
const planDayMigrations: Record<number, Migration<PlanDay>> = {}
const mockResultMigrations: Record<number, Migration<MockResult>> = {}
const settingsMigrations: Record<number, Migration<Settings>> = {}
const itemEloStateMigrations: Record<number, Migration<ItemEloState>> = {}
const mockSessionMigrations: Record<number, Migration<MockSession>> = {}
const srsCardMigrations: Record<number, Migration<SrsCard>> = {}
const bookmarkMigrations: Record<number, Migration<Bookmark>> = {}

function migrateRecord<T extends { schemaVersion: number }>(
  record: T,
  migrations: Record<number, Migration<T>>,
  currentVersion: number,
): T {
  let migrated = record
  while (migrated.schemaVersion < currentVersion) {
    const step = migrations[migrated.schemaVersion]
    if (!step) {
      throw new Error(
        `No migration registered from schemaVersion ${migrated.schemaVersion} to ${migrated.schemaVersion + 1}`,
      )
    }
    migrated = step(migrated)
  }
  return migrated
}

export function migrateAttempt(record: Attempt): Attempt {
  return migrateRecord(record, attemptMigrations, CURRENT_SCHEMA_VERSION.attempt)
}
export function migrateMasteryState(record: MasteryState): MasteryState {
  return migrateRecord(record, masteryStateMigrations, CURRENT_SCHEMA_VERSION.masteryState)
}
export function migratePlanDay(record: PlanDay): PlanDay {
  return migrateRecord(record, planDayMigrations, CURRENT_SCHEMA_VERSION.planDay)
}
export function migrateMockResult(record: MockResult): MockResult {
  return migrateRecord(record, mockResultMigrations, CURRENT_SCHEMA_VERSION.mockResult)
}
export function migrateSettings(record: Settings): Settings {
  return migrateRecord(record, settingsMigrations, CURRENT_SCHEMA_VERSION.settings)
}
export function migrateItemEloState(record: ItemEloState): ItemEloState {
  return migrateRecord(record, itemEloStateMigrations, CURRENT_SCHEMA_VERSION.itemEloState)
}
export function migrateMockSession(record: MockSession): MockSession {
  return migrateRecord(record, mockSessionMigrations, CURRENT_SCHEMA_VERSION.mockSession)
}
export function migrateSrsCard(record: SrsCard): SrsCard {
  return migrateRecord(record, srsCardMigrations, CURRENT_SCHEMA_VERSION.srsCard)
}
export function migrateBookmark(record: Bookmark): Bookmark {
  return migrateRecord(record, bookmarkMigrations, CURRENT_SCHEMA_VERSION.bookmark)
}
