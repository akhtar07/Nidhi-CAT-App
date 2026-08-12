import { describe, expect, it } from 'vitest'
import { computeScoreTrend } from './progressTrend'
import { estimatePercentile } from './percentile'
import type { MockResult } from '@/types/state'

function result(overrides: Partial<MockResult> = {}): MockResult {
  return {
    schemaVersion: 1,
    id: 'r1',
    mockId: 'full-mock-1',
    takenAt: 1000,
    sectionScores: {
      VARC: { score: 40, correct: 10, incorrect: 4, skipped: 2 },
      DILR: { score: 30, correct: 8, incorrect: 3, skipped: 3 },
      QA: { score: 50, correct: 12, incorrect: 2, skipped: 2 },
    },
    questionTimings: {},
    ...overrides,
  }
}

describe('computeScoreTrend', () => {
  it('sums section scores and attaches the matching percentile estimate', () => {
    const [point] = computeScoreTrend([result()])
    expect(point.totalScore).toBe(120)
    expect(point.percentile).toBe(estimatePercentile(120).percentile)
    expect(point.mockResultId).toBe('r1')
    expect(point.takenAt).toBe(1000)
  })

  it('sorts ascending by takenAt regardless of input order', () => {
    const results = [
      result({ id: 'r3', takenAt: 3000 }),
      result({ id: 'r1', takenAt: 1000 }),
      result({ id: 'r2', takenAt: 2000 }),
    ]
    expect(computeScoreTrend(results).map((p) => p.mockResultId)).toEqual(['r1', 'r2', 'r3'])
  })

  it('returns an empty array for no mock history', () => {
    expect(computeScoreTrend([])).toEqual([])
  })
})
