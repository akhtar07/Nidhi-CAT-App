/**
 * Per-micro-topic progress rollup — the data behind the mastery map and the
 * strength/weakness table on /progress.
 *
 * **Attempt population:** every attempt for the topic, regardless of `mode`.
 * This deliberately matches `mastery/masteryEngine.ts`, which feeds
 * `storage.listAttempts({ microTopicId })` unfiltered into `evaluateMastery`.
 * If this module filtered to drill-only, the accuracy shown next to a topic
 * would silently disagree with the mastery status shown beside it, which is
 * worse than including mock attempts. `mockReserved` is a *content* flag on
 * questions that keeps them out of drill selection; it never appears on an
 * Attempt, so it needs no handling here.
 *
 * Every ratio returns `null` rather than `NaN` when its denominator is zero —
 * a brand-new learner has 86 topics with no attempts, and `NaN%` on screen is
 * the failure mode this guards against.
 */

import type { MicroTopic } from '@/types/content'
import type { Attempt, MasteryState, Section } from '@/types/state'

/**
 * Display status. Narrower than `MasteryState['status']`: 'available' (prerequisites
 * met, not started) and a missing MasteryState both collapse to 'untouched', because
 * to the learner they are the same thing — she has not begun.
 */
export type ProgressStatus = 'untouched' | 'locked' | 'learning' | 'practising' | 'mastered' | 'decaying'

/** Rungs of the ordinal progression ladder, in order. 'locked' and 'decaying' sit outside it. */
export const PROGRESSION_LADDER: ProgressStatus[] = ['untouched', 'learning', 'practising', 'mastered']

export interface TopicProgressRow {
  microTopicId: string
  name: string
  section: Section
  roiScore: number
  status: ProgressStatus
  attempts: number
  correct: number
  /** 0-100, or null when there are no attempts. */
  accuracyPct: number | null
  /** null when there are no attempts. */
  medianTimeSec: number | null
  targetSecPerQuestion: number
  /** medianTime / target. >1 means slower than the topic's target pace. null when no attempts. */
  paceRatio: number | null
  lastAttemptAt: number | null
}

function median(values: number[]): number | null {
  if (values.length === 0) return null
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
}

function displayStatus(state: MasteryState | undefined, attempts: number): ProgressStatus {
  if (!state) return attempts > 0 ? 'learning' : 'untouched'
  if (state.status === 'available') return attempts > 0 ? 'learning' : 'untouched'
  return state.status
}

/**
 * Joins the syllabus, every attempt, and the stored mastery states into one row per
 * micro-topic. Topics with no attempts are included — the point of the mastery map is
 * to show what has *not* been touched, so filtering them out would defeat it.
 */
export function buildTopicProgress(
  syllabus: MicroTopic[],
  attempts: Attempt[],
  masteryStates: MasteryState[],
): TopicProgressRow[] {
  const stateById = new Map(masteryStates.map((s) => [s.microTopicId, s]))

  // An attempt can carry several microTopicIds (a DILR set item can belong to two);
  // it counts towards each, the same way listAttempts({ microTopicId }) returns it for each.
  const byTopic = new Map<string, Attempt[]>()
  for (const attempt of attempts) {
    for (const id of attempt.microTopicIds) {
      const bucket = byTopic.get(id)
      if (bucket) bucket.push(attempt)
      else byTopic.set(id, [attempt])
    }
  }

  return syllabus.map((topic) => {
    const topicAttempts = byTopic.get(topic.id) ?? []
    const count = topicAttempts.length
    const correct = topicAttempts.filter((a) => a.correct).length
    const medianTimeSec = median(topicAttempts.map((a) => a.timeSpentSec))

    return {
      microTopicId: topic.id,
      name: topic.name,
      section: topic.section,
      roiScore: topic.roiScore,
      status: displayStatus(stateById.get(topic.id), count),
      attempts: count,
      correct,
      accuracyPct: count === 0 ? null : Math.round((correct / count) * 100),
      medianTimeSec,
      targetSecPerQuestion: topic.targetSecPerQuestion,
      paceRatio:
        medianTimeSec === null || topic.targetSecPerQuestion <= 0
          ? null
          : Math.round((medianTimeSec / topic.targetSecPerQuestion) * 100) / 100,
      lastAttemptAt: count === 0 ? null : Math.max(...topicAttempts.map((a) => a.submittedAt)),
    }
  })
}

/**
 * Topics most worth her next session: attempted enough to trust the number, ranked by
 * accuracy ascending, then by ROI descending so a weak high-ROI topic outranks an equally
 * weak rare one. Topics she has never touched are excluded — "weakest" means demonstrated
 * weakness, and untouched coverage is reported separately by the coverage summary.
 */
export function rankWeakestTopics(
  rows: TopicProgressRow[],
  { minAttempts = 4, limit = 8 }: { minAttempts?: number; limit?: number } = {},
): TopicProgressRow[] {
  return rows
    .filter((r) => r.attempts >= minAttempts && r.accuracyPct !== null && r.status !== 'mastered')
    .sort((a, b) => (a.accuracyPct ?? 0) - (b.accuracyPct ?? 0) || b.roiScore - a.roiScore)
    .slice(0, limit)
}
