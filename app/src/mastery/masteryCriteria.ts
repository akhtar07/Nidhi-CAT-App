import { effectiveCorrectness } from './elo'
import type { Attempt } from '@/types/state'
import type { Question } from '@/types/content'

const THREE_DAYS_MS = 3 * 24 * 60 * 60 * 1000
const HARD_TIERS: Question['difficulty'][] = ['hard', 'very_hard']

export interface AttemptForMastery {
  correct: boolean
  confidence?: Attempt['confidence']
  timeSpentSec: number
  submittedAt: number
  difficulty: Question['difficulty']
}

export interface MasteryCriteriaInput {
  /** Every attempt ever logged for this micro-topic, oldest first. */
  attempts: AttemptForMastery[]
  targetSecPerQuestion: number
  now: number
  /** Carried over from MasteryState.criteria123FirstMetAt; undefined until first met. */
  criteria123FirstMetAt?: number
}

export type NonLockedStatus = 'learning' | 'practising' | 'mastered'

export interface MasteryEvaluation {
  attemptsCount: number
  /** Criterion 1 (SPEC.md §8.2): >=75% over the last 10, min 12 lifetime attempts. */
  accuracyOk: boolean
  /** Criterion 2: median time on the last 10 <= targetSecPerQuestion * 1.25. */
  speedOk: boolean
  /** Criterion 3: >=2 hard/very_hard items answered correctly, lifetime. */
  ceilingOk: boolean
  criteria123Met: boolean
  criteria123FirstMetAt: number | undefined
  /** Criterion 4: a correct attempt >=3 days after criteria123FirstMetAt. */
  retentionOk: boolean
  /** SPEC.md §8.2 anti-frustration valve. */
  antiFrustrationTriggered: boolean
  status: NonLockedStatus
  medianTimeSec: number
  /** rolling window of 10, for MasteryState.lastNCorrect */
  lastNCorrect: boolean[]
}

function median(values: number[]): number {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
}

/** SPEC.md §8.2 — "do not use a simple accuracy percentage": all four criteria must hold. */
export function evaluateMastery({
  attempts,
  targetSecPerQuestion,
  now,
  criteria123FirstMetAt,
}: MasteryCriteriaInput): MasteryEvaluation {
  const attemptsCount = attempts.length
  const last10 = attempts.slice(-10)
  const last15 = attempts.slice(-15)

  const accuracyOk =
    attemptsCount >= 12 &&
    last10.length > 0 &&
    last10.reduce((sum, a) => sum + effectiveCorrectness(a), 0) / last10.length >= 0.75

  const medianTimeSec = median(last10.map((a) => a.timeSpentSec))
  const speedOk = last10.length > 0 && medianTimeSec <= targetSecPerQuestion * 1.25

  const ceilingOk = attempts.filter((a) => a.correct && HARD_TIERS.includes(a.difficulty)).length >= 2

  const criteria123Met = accuracyOk && speedOk && ceilingOk
  const resolvedFirstMetAt = criteria123FirstMetAt ?? (criteria123Met ? now : undefined)

  const retentionOk =
    resolvedFirstMetAt !== undefined &&
    attempts.some((a) => a.correct && a.submittedAt >= resolvedFirstMetAt + THREE_DAYS_MS)

  const antiFrustrationTriggered =
    (attemptsCount >= 30 && !criteria123Met) ||
    (attemptsCount >= 15 &&
      last15.reduce((sum, a) => sum + effectiveCorrectness(a), 0) / last15.length < 0.4)

  let status: NonLockedStatus
  if (attemptsCount < 8) {
    status = 'learning'
  } else if (criteria123Met && retentionOk) {
    status = 'mastered'
  } else {
    status = 'practising'
  }

  return {
    attemptsCount,
    accuracyOk,
    speedOk,
    ceilingOk,
    criteria123Met,
    criteria123FirstMetAt: resolvedFirstMetAt,
    retentionOk,
    antiFrustrationTriggered,
    status,
    medianTimeSec,
    lastNCorrect: last10.map((a) => a.correct),
  }
}
