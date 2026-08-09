import type { Attempt, ItemEloState, MasteryState, MockResult, PlanDay, Settings } from '@/types/state'

/**
 * Full snapshot of learner state, for the Export/Import JSON feature
 * (SPEC.md §5.2: "Ship an Export / Import JSON button in Settings before
 * Milestone 5 — if IndexedDB is cleared, all her work vanishes").
 */
export interface ExportBundle {
  exportedAt: string
  attempts: Attempt[]
  masteryStates: MasteryState[]
  planDays: PlanDay[]
  mockResults: MockResult[]
  itemEloStates: ItemEloState[]
  settings: Settings | null
}

/**
 * Every write to learner state goes through this interface (SPEC.md §5.2,
 * §1 rule 2). `DexieAdapter` (IndexedDB) is the v1 implementation; a future
 * `SupabaseAdapter` (Milestone 16) implements the same interface without
 * any component needing to change.
 */
export interface StorageAdapter {
  addAttempt(attempt: Attempt): Promise<void>
  getAttempt(id: string): Promise<Attempt | undefined>
  listAttempts(filter?: { microTopicId?: string; mode?: Attempt['mode'] }): Promise<Attempt[]>

  getMasteryState(microTopicId: string): Promise<MasteryState | undefined>
  putMasteryState(state: MasteryState): Promise<void>
  listMasteryStates(): Promise<MasteryState[]>

  getPlanDay(date: string): Promise<PlanDay | undefined>
  putPlanDay(day: PlanDay): Promise<void>
  listPlanDays(range?: { from: string; to: string }): Promise<PlanDay[]>

  addMockResult(result: MockResult): Promise<void>
  listMockResults(): Promise<MockResult[]>

  getItemElo(questionId: string): Promise<number | undefined>
  putItemElo(questionId: string, elo: number): Promise<void>

  /** Settings is a singleton row. */
  getSettings(): Promise<Settings | undefined>
  putSettings(settings: Settings): Promise<void>

  exportAll(): Promise<ExportBundle>
  /** Replaces all existing learner state with the bundle's contents. */
  importAll(bundle: ExportBundle): Promise<void>

  /** Wipes all learner state. Never called from app code outside tests/explicit reset. */
  clearAll(): Promise<void>
}
