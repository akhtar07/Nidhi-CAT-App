import { beforeEach, describe, expect, it } from 'vitest'
import { DexieAdapter } from './DexieAdapter'
import type { Attempt, MasteryState, MockResult, PlanDay, Settings } from '@/types/state'

function makeAttempt(overrides: Partial<Attempt> = {}): Attempt {
  return {
    schemaVersion: 1,
    id: 'attempt-1',
    questionId: 'qa.arith.percentages-0001',
    microTopicIds: ['qa.arith.percentages'],
    startedAt: 1000,
    submittedAt: 1030,
    timeSpentSec: 30,
    given: 'B',
    correct: true,
    mode: 'drill',
    markedForReview: false,
    ...overrides,
  }
}

function makeMasteryState(overrides: Partial<MasteryState> = {}): MasteryState {
  return {
    schemaVersion: 1,
    microTopicId: 'qa.arith.percentages',
    status: 'learning',
    learnerElo: 1200,
    lastNCorrect: [],
    medianTimeSec: 45,
    hardTierCleared: false,
    attemptsCount: 0,
    stability: 0,
    difficulty: 0,
    ...overrides,
  }
}

function makePlanDay(overrides: Partial<PlanDay> = {}): PlanDay {
  return {
    schemaVersion: 1,
    date: '2026-08-09',
    items: [{ microTopicId: 'qa.arith.percentages', kind: 'drill', done: false }],
    status: 'pending',
    ...overrides,
  }
}

function makeMockResult(overrides: Partial<MockResult> = {}): MockResult {
  return {
    schemaVersion: 1,
    id: 'mock-1',
    mockId: 'full-mock-1',
    takenAt: 2000,
    sectionScores: {
      VARC: { score: 40, correct: 10, incorrect: 4, skipped: 2 },
      DILR: { score: 30, correct: 8, incorrect: 3, skipped: 3 },
      QA: { score: 50, correct: 12, incorrect: 2, skipped: 2 },
    },
    questionTimings: {},
    ...overrides,
  }
}

function makeSettings(overrides: Partial<Settings> = {}): Settings {
  return {
    schemaVersion: 1,
    dailyMinutes: 60,
    examDate: '2026-11-29',
    weakSectionBias: null,
    emailOptIn: false,
    ...overrides,
  }
}

let dbCounter = 0
function freshAdapter(): DexieAdapter {
  dbCounter += 1
  return new DexieAdapter(`ascent-test-${dbCounter}`)
}

describe('DexieAdapter', () => {
  let adapter: DexieAdapter

  beforeEach(() => {
    adapter = freshAdapter()
  })

  it('round-trips an attempt', async () => {
    await adapter.addAttempt(makeAttempt())
    expect(await adapter.getAttempt('attempt-1')).toEqual(makeAttempt())
  })

  it('filters attempts by microTopicId and mode', async () => {
    await adapter.addAttempt(makeAttempt({ id: 'a1', microTopicIds: ['qa.arith.percentages'], mode: 'drill' }))
    await adapter.addAttempt(makeAttempt({ id: 'a2', microTopicIds: ['qa.algebra.linear-equations'], mode: 'drill' }))
    await adapter.addAttempt(makeAttempt({ id: 'a3', microTopicIds: ['qa.arith.percentages'], mode: 'mock' }))

    const byTopic = await adapter.listAttempts({ microTopicId: 'qa.arith.percentages' })
    expect(byTopic.map((a) => a.id).sort()).toEqual(['a1', 'a3'])

    const byMode = await adapter.listAttempts({ mode: 'mock' })
    expect(byMode.map((a) => a.id)).toEqual(['a3'])
  })

  it('round-trips mastery state', async () => {
    await adapter.putMasteryState(makeMasteryState())
    expect(await adapter.getMasteryState('qa.arith.percentages')).toEqual(makeMasteryState())
    expect(await adapter.listMasteryStates()).toEqual([makeMasteryState()])
  })

  it('round-trips plan days and filters by date range', async () => {
    await adapter.putPlanDay(makePlanDay({ date: '2026-08-08' }))
    await adapter.putPlanDay(makePlanDay({ date: '2026-08-09' }))
    await adapter.putPlanDay(makePlanDay({ date: '2026-08-10' }))

    const inRange = await adapter.listPlanDays({ from: '2026-08-09', to: '2026-08-10' })
    expect(inRange.map((d) => d.date).sort()).toEqual(['2026-08-09', '2026-08-10'])
  })

  it('round-trips mock results', async () => {
    await adapter.addMockResult(makeMockResult())
    expect(await adapter.listMockResults()).toEqual([makeMockResult()])
  })

  it('round-trips settings as a singleton', async () => {
    expect(await adapter.getSettings()).toBeUndefined()
    await adapter.putSettings(makeSettings())
    expect(await adapter.getSettings()).toEqual(makeSettings())
    await adapter.putSettings(makeSettings({ dailyMinutes: 90 }))
    expect(await adapter.getSettings()).toEqual(makeSettings({ dailyMinutes: 90 }))
  })

  it('exports and re-imports a full snapshot', async () => {
    await adapter.addAttempt(makeAttempt())
    await adapter.putMasteryState(makeMasteryState())
    await adapter.putPlanDay(makePlanDay())
    await adapter.addMockResult(makeMockResult())
    await adapter.putSettings(makeSettings())

    const bundle = await adapter.exportAll()
    expect(bundle.attempts).toEqual([makeAttempt()])
    expect(bundle.masteryStates).toEqual([makeMasteryState()])
    expect(bundle.planDays).toEqual([makePlanDay()])
    expect(bundle.mockResults).toEqual([makeMockResult()])
    expect(bundle.settings).toEqual(makeSettings())

    const restored = freshAdapter()
    await restored.importAll(bundle)
    expect(await restored.listAttempts()).toEqual([makeAttempt()])
    expect(await restored.listMasteryStates()).toEqual([makeMasteryState()])
    expect(await restored.listPlanDays()).toEqual([makePlanDay()])
    expect(await restored.listMockResults()).toEqual([makeMockResult()])
    expect(await restored.getSettings()).toEqual(makeSettings())
  })

  it('importAll replaces existing data rather than merging', async () => {
    await adapter.addAttempt(makeAttempt({ id: 'stale' }))
    const bundle = await freshAdapter().exportAll() // empty bundle
    await adapter.importAll(bundle)
    expect(await adapter.listAttempts()).toEqual([])
  })

  it('clearAll wipes every table', async () => {
    await adapter.addAttempt(makeAttempt())
    await adapter.putMasteryState(makeMasteryState())
    await adapter.putPlanDay(makePlanDay())
    await adapter.addMockResult(makeMockResult())
    await adapter.putSettings(makeSettings())

    await adapter.clearAll()

    expect(await adapter.listAttempts()).toEqual([])
    expect(await adapter.listMasteryStates()).toEqual([])
    expect(await adapter.listPlanDays()).toEqual([])
    expect(await adapter.listMockResults()).toEqual([])
    expect(await adapter.getSettings()).toBeUndefined()
  })
})
