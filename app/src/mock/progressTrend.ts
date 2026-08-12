import { estimatePercentile } from './percentile'
import type { MockResult } from '@/types/state'

export interface ProgressPoint {
  mockResultId: string
  takenAt: number
  totalScore: number
  percentile: number
}

/** Score/percentile trend across a learner's mock history (professionalization pass — the
 * single most common "real test-prep app" dashboard feature: a score-over-time chart across a
 * mock series). Sorted ascending by takenAt so callers can render a chart left-to-right without
 * re-sorting. Total score is the sum of all three sections' scores, same computation
 * MockAnalysis.tsx already does per-result — factored out here so it's shared and independently
 * testable rather than duplicated between the two screens. */
export function computeScoreTrend(results: MockResult[]): ProgressPoint[] {
  return results
    .map((r) => {
      const totalScore = Object.values(r.sectionScores).reduce((sum, s) => sum + s.score, 0)
      return {
        mockResultId: r.id,
        takenAt: r.takenAt,
        totalScore,
        percentile: estimatePercentile(totalScore).percentile,
      }
    })
    .sort((a, b) => a.takenAt - b.takenAt)
}
