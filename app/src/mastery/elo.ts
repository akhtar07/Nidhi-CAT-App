import type { Attempt } from '@/types/state'

/** SPEC.md §8.3: "Elo, both sides." */
export const DEFAULT_LEARNER_ELO = 1200
export const DEFAULT_ITEM_ELO = 1200

const K_ITEM = 8

/** K_L ≈ 24, decaying to 12 after 200 attempts (SPEC.md §8.3), counted per micro-topic. */
function learnerK(topicAttemptsCountSoFar: number): number {
  return topicAttemptsCountSoFar < 200 ? 24 : 12
}

export function expectedScore(itemElo: number, learnerElo: number): number {
  return 1 / (1 + 10 ** ((itemElo - learnerElo) / 400))
}

/**
 * SPEC.md §8.5: a correct-but-guessed answer counts as ~0.4 of a correct
 * answer "in the mastery calculation" — applied here to the Elo actual
 * score (continuous, so it can represent a partial win) rather than to the
 * `lastNCorrect` boolean log, which stays a plain correctness record.
 */
export function effectiveCorrectness(attempt: Pick<Attempt, 'correct' | 'confidence'>): number {
  if (!attempt.correct) return 0
  return attempt.confidence === 'guess' ? 0.4 : 1
}

export interface EloUpdateInput {
  learnerElo: number
  itemElo: number
  /** effectiveCorrectness() of the attempt: 1, 0.4, or 0. */
  actual: number
  /** Attempts already logged on this micro-topic before this one. */
  topicAttemptsCountSoFar: number
}

export interface EloUpdateResult {
  learnerElo: number
  itemElo: number
}

/**
 * SPEC.md §8.3, implemented literally:
 *   expected  = 1 / (1 + 10^((itemElo − learnerElo)/400))
 *   learnerElo += K_L * (actual − expected)
 *   itemElo    += K_I * (expectedItem − actualItem)
 * expectedItem/actualItem are the natural symmetric complements (1 -
 * expected, 1 - actual) — SPEC doesn't spell those out, but there's no
 * other sensible reading of "both sides" Elo.
 */
export function updateElo({ learnerElo, itemElo, actual, topicAttemptsCountSoFar }: EloUpdateInput): EloUpdateResult {
  const expected = expectedScore(itemElo, learnerElo)
  const expectedItem = 1 - expected
  const actualItem = 1 - actual
  const kL = learnerK(topicAttemptsCountSoFar)
  return {
    learnerElo: learnerElo + kL * (actual - expected),
    itemElo: itemElo + K_ITEM * (expectedItem - actualItem),
  }
}
