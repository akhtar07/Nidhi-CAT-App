/**
 * Section-level (VARC / DILR / QA) and syllabus-wide rollups of the per-topic rows.
 *
 * CAT aspirants think in sections — "my DILR is the problem" — and the app had no
 * surface answering that. This is a pure reduction over `TopicProgressRow[]`; it adds
 * no new notion of correctness or mastery, so it can never disagree with the topic table.
 */

import type { Section } from '@/types/state'
import type { ProgressStatus, TopicProgressRow } from './topicProgress'

export const SECTIONS: Section[] = ['VARC', 'DILR', 'QA']

export interface SectionRollup {
  section: Section
  topics: number
  /** Topics with at least one attempt. */
  started: number
  mastered: number
  attempts: number
  correct: number
  /** 0-100, or null when the section has no attempts at all. */
  accuracyPct: number | null
}

export interface CoverageSummary {
  totalTopics: number
  started: number
  mastered: number
  untouched: number
  /** 0-100 share of the syllabus with at least one attempt logged. */
  startedPct: number
  /** 0-100 share of the syllabus at 'mastered'. */
  masteredPct: number
  totalAttempts: number
  /** 0-100 lifetime accuracy across every attempt, or null when there are none. */
  overallAccuracyPct: number | null
}

function accuracy(correct: number, attempts: number): number | null {
  return attempts === 0 ? null : Math.round((correct / attempts) * 100)
}

export function rollUpBySection(rows: TopicProgressRow[]): SectionRollup[] {
  return SECTIONS.map((section) => {
    const inSection = rows.filter((r) => r.section === section)
    const attempts = inSection.reduce((sum, r) => sum + r.attempts, 0)
    const correct = inSection.reduce((sum, r) => sum + r.correct, 0)
    return {
      section,
      topics: inSection.length,
      started: inSection.filter((r) => r.attempts > 0).length,
      mastered: inSection.filter((r) => r.status === 'mastered').length,
      attempts,
      correct,
      accuracyPct: accuracy(correct, attempts),
    }
  })
}

export function summariseCoverage(rows: TopicProgressRow[]): CoverageSummary {
  const totalTopics = rows.length
  const started = rows.filter((r) => r.attempts > 0).length
  const mastered = rows.filter((r) => r.status === 'mastered').length
  const totalAttempts = rows.reduce((sum, r) => sum + r.attempts, 0)
  const totalCorrect = rows.reduce((sum, r) => sum + r.correct, 0)

  return {
    totalTopics,
    started,
    mastered,
    untouched: totalTopics - started,
    // Guarded so an empty syllabus (a failed content fetch) reports 0, not NaN.
    startedPct: totalTopics === 0 ? 0 : Math.round((started / totalTopics) * 100),
    masteredPct: totalTopics === 0 ? 0 : Math.round((mastered / totalTopics) * 100),
    totalAttempts,
    overallAccuracyPct: accuracy(totalCorrect, totalAttempts),
  }
}

/** Counts per rung of the progression ladder, for the mastery-map legend. */
export function countByStatus(rows: TopicProgressRow[]): Record<ProgressStatus, number> {
  const counts: Record<ProgressStatus, number> = {
    untouched: 0,
    locked: 0,
    learning: 0,
    practising: 0,
    mastered: 0,
    decaying: 0,
  }
  for (const row of rows) counts[row.status] += 1
  return counts
}
