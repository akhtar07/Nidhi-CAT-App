import { Rating, type Grade } from './fsrsAdapter'
import type { Attempt, MasteryState } from '@/types/state'

/** Maps a practice attempt onto FSRS's 4-point grade scale — every attempt is treated as an
 * implicit review signal for that topic's forgetting curve, not just a dedicated "review session"
 * (SPEC.md §8.4 doesn't define a separate topic-review UI, unlike card-level SRS). Confidence
 * (captured before the answer is revealed, same signal SPEC.md §8.5 uses for the guess-discount)
 * distinguishes a shaky correct answer from a confident one. */
export function mapAttemptToGrade(attempt: Pick<Attempt, 'correct' | 'confidence'>): Grade {
  if (!attempt.correct) return Rating.Again
  if (attempt.confidence === 'guess') return Rating.Hard
  if (attempt.confidence === 'unsure') return Rating.Good
  return Rating.Easy
}

/** SPEC.md §8.4: FSRS "schedules the decaying -> review cycle" at the micro-topic level. A
 * mastered topic whose FSRS review has come due is downgraded to 'decaying' for display/planning
 * purposes — the underlying competency data (lastNCorrect, hardTierCleared, etc.) is untouched;
 * only `status` changes, and only until she practises it again (which re-runs through
 * recordAttemptForMastery and re-evaluates from scratch). Read-time, not stored: `status` in
 * storage can lag until the next explicit check, same trade-off as everything else in this
 * static, serverless app with no background job to run it continuously. */
export function applyDecay(state: MasteryState, now: number = Date.now()): MasteryState {
  if (state.status !== 'mastered') return state
  if (state.nextReviewAt === undefined || state.nextReviewAt > now) return state
  return { ...state, status: 'decaying' }
}

export function withDecayApplied(states: MasteryState[], now: number = Date.now()): MasteryState[] {
  return states.map((s) => applyDecay(s, now))
}
