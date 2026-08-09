import { scoreQuestion } from './scoring'
import type { MockDefinition, Question } from '@/types/content'
import type { Attempt, MockResult, Section } from '@/types/state'

/** SPEC.md §9.3: minutes spent vs marks earned, per section. */
export interface TimeWaterfallEntry {
  section: Section
  minutesSpent: number
  marksEarned: number
}

export function computeTimeWaterfall(mockDef: MockDefinition, result: MockResult): TimeWaterfallEntry[] {
  return mockDef.sections.map((s) => {
    const secondsSpent = (s.questionIds ?? []).reduce((sum, qid) => sum + (result.questionTimings[qid] ?? 0), 0)
    return {
      section: s.section,
      minutesSpent: Math.round((secondsSpent / 60) * 10) / 10,
      marksEarned: result.sectionScores[s.section]?.score ?? 0,
    }
  })
}

/** SPEC.md §9.3: "questions where she spent >150 seconds and got it wrong ... ranked by time wasted." */
export interface BleederEntry {
  questionId: string
  timeSpentSec: number
  microTopicIds: string[]
  stemPreview: string
}

export function computeBleederReport(
  attempts: Attempt[],
  questionsById: Map<string, Question>,
  thresholdSec = 150,
): BleederEntry[] {
  return attempts
    .filter((a) => a.given !== null && !a.correct && a.timeSpentSec > thresholdSec)
    .sort((a, b) => b.timeSpentSec - a.timeSpentSec)
    .map((a) => ({
      questionId: a.questionId,
      timeSpentSec: a.timeSpentSec,
      microTopicIds: a.microTopicIds,
      stemPreview: (questionsById.get(a.questionId)?.stemMarkdown ?? '').slice(0, 120),
    }))
}

/** SPEC.md §9.3: "of the questions she skipped, what fraction were actually easy (low itemElo)?
 * High = poor selection." "Easy" is relative to this mock's own item difficulty spread (median
 * itemElo among questions actually offered), not a fixed absolute cutoff — a mock composed of all
 * hard items shouldn't have every skip flagged as a poor choice just because it's below some
 * unrelated global number. */
export interface SelectionQuality {
  skippedCount: number
  easySkippedCount: number
  /** Fraction of skips that were easy relative to this mock — higher is worse selection. */
  easySkipFraction: number
}

export function computeSelectionQuality(
  attempts: Attempt[],
  questionsById: Map<string, Question>,
  itemEloByQuestionId: Map<string, number>,
): SelectionQuality {
  const allElos = [...questionsById.values()].map((q) => itemEloByQuestionId.get(q.id) ?? q.eloRating)
  const sorted = [...allElos].sort((a, b) => a - b)
  const median = sorted.length === 0 ? 0 : sorted[Math.floor(sorted.length / 2)]

  const skipped = attempts.filter((a) => a.given === null)
  const easySkipped = skipped.filter((a) => {
    const q = questionsById.get(a.questionId)
    const elo = itemEloByQuestionId.get(a.questionId) ?? q?.eloRating ?? median
    return elo < median
  })

  return {
    skippedCount: skipped.length,
    easySkippedCount: easySkipped.length,
    easySkipFraction: skipped.length === 0 ? 0 : easySkipped.length / skipped.length,
  }
}

/** SPEC.md §9.3: "did she leave any TITA blank? ... Flag every instance loudly." */
export interface TitaBlankEntry {
  questionId: string
  stemPreview: string
}

export function computeTitaDiscipline(attempts: Attempt[], questionsById: Map<string, Question>): TitaBlankEntry[] {
  return attempts
    .filter((a) => a.given === null && questionsById.get(a.questionId)?.format === 'tita')
    .map((a) => ({
      questionId: a.questionId,
      stemPreview: (questionsById.get(a.questionId)?.stemMarkdown ?? '').slice(0, 120),
    }))
}

/** SPEC.md §9.3: "compute what her score *would* have been at each attempt count given her
 * accuracy profile, and show the optimum." Only questions she actually attempted have a known
 * outcome — skipped ones can't be scored counterfactually — so the curve orders her attempted
 * questions easiest-first (by item difficulty) and asks: if she'd stopped after only her N
 * easiest attempts (using how she actually did on each), what would the score be? */
export interface AccuracyVsAttemptsPoint {
  attemptCount: number
  score: number
}

export interface AccuracyVsAttemptsResult {
  curve: AccuracyVsAttemptsPoint[]
  optimalAttemptCount: number
  actualAttemptCount: number
}

export function computeAccuracyVsAttemptsCurve(
  attempts: Attempt[],
  questionsById: Map<string, Question>,
  itemEloByQuestionId: Map<string, number>,
): AccuracyVsAttemptsResult {
  const attempted = attempts.filter((a) => a.given !== null)
  const sorted = [...attempted].sort((a, b) => {
    const eloA = itemEloByQuestionId.get(a.questionId) ?? questionsById.get(a.questionId)?.eloRating ?? 0
    const eloB = itemEloByQuestionId.get(b.questionId) ?? questionsById.get(b.questionId)?.eloRating ?? 0
    return eloA - eloB
  })

  const curve: AccuracyVsAttemptsPoint[] = [{ attemptCount: 0, score: 0 }]
  let running = 0
  for (let i = 0; i < sorted.length; i++) {
    const a = sorted[i]
    const q = questionsById.get(a.questionId)
    if (q) running += scoreQuestion(q, a.given)
    curve.push({ attemptCount: i + 1, score: running })
  }

  let optimal = curve[0]
  for (const point of curve) {
    if (point.score > optimal.score) optimal = point
  }

  return { curve, optimalAttemptCount: optimal.attemptCount, actualAttemptCount: attempted.length }
}

/** SPEC.md §9.3: "which topics cost her marks, with one-click 'add to practice queue.'" */
export interface MicroTopicDamage {
  microTopicId: string
  marksLost: number
  incorrectCount: number
}

export function computeMicroTopicDamage(attempts: Attempt[], questionsById: Map<string, Question>): MicroTopicDamage[] {
  const byTopic = new Map<string, { marksLost: number; incorrectCount: number }>()
  for (const a of attempts) {
    if (a.given === null || a.correct) continue
    const q = questionsById.get(a.questionId)
    if (!q) continue
    const lost = -scoreQuestion(q, a.given) // scoreQuestion is -1 for wrong MCQ, 0 for wrong TITA
    if (lost <= 0) continue
    for (const topicId of a.microTopicIds) {
      const entry = byTopic.get(topicId) ?? { marksLost: 0, incorrectCount: 0 }
      entry.marksLost += lost
      entry.incorrectCount += 1
      byTopic.set(topicId, entry)
    }
  }
  return [...byTopic.entries()]
    .map(([microTopicId, v]) => ({ microTopicId, ...v }))
    .sort((a, b) => b.marksLost - a.marksLost)
}
