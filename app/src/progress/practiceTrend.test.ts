import { describe, expect, it } from 'vitest'
import { computePracticeTrend } from './practiceTrend'
import type { Attempt } from '@/types/state'

/** 2026-08-10 is a Monday; 2026-08-12 a Wednesday; 2026-08-17 the next Monday. */
const MON_AUG10 = Date.UTC(2026, 7, 10, 9, 0)
const WED_AUG12 = Date.UTC(2026, 7, 12, 9, 0)
const SUN_AUG16 = Date.UTC(2026, 7, 16, 22, 0)
const MON_AUG17 = Date.UTC(2026, 7, 17, 9, 0)

function attempt(overrides: Partial<Attempt> = {}): Attempt {
  return {
    schemaVersion: 1,
    id: 'a1',
    questionId: 'q1',
    microTopicIds: ['t1'],
    startedAt: 0,
    submittedAt: MON_AUG10,
    timeSpentSec: 60,
    given: 'A',
    correct: true,
    mode: 'drill',
    markedForReview: false,
    ...overrides,
  }
}

describe('computePracticeTrend', () => {
  it('buckets attempts into Monday-started weeks', () => {
    const trend = computePracticeTrend([
      attempt({ id: 'a1', submittedAt: MON_AUG10, correct: true }),
      attempt({ id: 'a2', submittedAt: WED_AUG12, correct: false }),
      attempt({ id: 'a3', submittedAt: SUN_AUG16, correct: true }),
      attempt({ id: 'a4', submittedAt: MON_AUG17, correct: true }),
    ])

    expect(trend).toHaveLength(2)
    expect(trend[0].weekStart).toBe('2026-08-10')
    // Sunday the 16th belongs to the week that started Monday the 10th.
    expect(trend[0].attempts).toBe(3)
    expect(trend[0].correct).toBe(2)
    expect(trend[0].accuracyPct).toBe(67) // 2/3 = 66.67 -> 67
    expect(trend[1].weekStart).toBe('2026-08-17')
    expect(trend[1].attempts).toBe(1)
  })

  it('excludes mock attempts, which are a different task', () => {
    const trend = computePracticeTrend([
      attempt({ id: 'a1', mode: 'drill', correct: true }),
      attempt({ id: 'a2', mode: 'mock', correct: false }),
      attempt({ id: 'a3', mode: 'mock', correct: false }),
    ])
    expect(trend).toHaveLength(1)
    expect(trend[0].attempts).toBe(1)
    expect(trend[0].accuracyPct).toBe(100)
  })

  it('includes review, warmup and topic_test as practice', () => {
    const trend = computePracticeTrend([
      attempt({ id: 'a1', mode: 'review' }),
      attempt({ id: 'a2', mode: 'warmup' }),
      attempt({ id: 'a3', mode: 'topic_test' }),
    ])
    expect(trend[0].attempts).toBe(3)
  })

  it('takes the median time, so one abandoned question does not swamp the week', () => {
    const trend = computePracticeTrend([
      attempt({ id: 'a1', timeSpentSec: 30 }),
      attempt({ id: 'a2', timeSpentSec: 40 }),
      attempt({ id: 'a3', timeSpentSec: 900 }),
    ])
    expect(trend[0].medianTimeSec).toBe(40)
  })

  it('omits weeks with no practice rather than plotting them as zero accuracy', () => {
    // A three-week gap between two practice weeks.
    const threeWeeksLater = MON_AUG10 + 21 * 24 * 60 * 60 * 1000
    const trend = computePracticeTrend([
      attempt({ id: 'a1', submittedAt: MON_AUG10 }),
      attempt({ id: 'a2', submittedAt: threeWeeksLater }),
    ])
    expect(trend).toHaveLength(2)
    expect(trend.every((w) => w.attempts > 0)).toBe(true)
  })

  it('returns an empty array when there are no attempts at all', () => {
    expect(computePracticeTrend([])).toEqual([])
  })

  it('returns an empty array when every attempt is a mock', () => {
    expect(computePracticeTrend([attempt({ mode: 'mock' })])).toEqual([])
  })

  it('keeps only the most recent maxWeeks buckets', () => {
    const week = 7 * 24 * 60 * 60 * 1000
    const attempts = Array.from({ length: 20 }, (_, i) =>
      attempt({ id: `a${i}`, submittedAt: MON_AUG10 + i * week }),
    )
    const trend = computePracticeTrend(attempts, { maxWeeks: 5 })
    expect(trend).toHaveLength(5)
    // The retained window must be the newest, and still oldest-first within itself.
    expect(trend[trend.length - 1].weekStart).toBe(
      new Date(MON_AUG10 + 19 * week).toISOString().slice(0, 10),
    )
    expect([...trend].sort((a, b) => a.weekStart.localeCompare(b.weekStart))).toEqual(trend)
  })
})
