import { createEmptyCard, fsrs, State, type Card, type Grade } from 'ts-fsrs'

export { Rating } from 'ts-fsrs'
export type { Grade } from 'ts-fsrs'

const scheduler = fsrs()

/**
 * SPEC.md §8.4: "Use FSRS (ts-fsrs npm package) if you want the best available scheduler" —
 * explicitly named in the spec itself, so this is pre-approved the same way §7's tech stack is
 * (CLAUDE.md's "ask before adding a dependency" is about undocumented additions, not this).
 *
 * Persisted state is {stability, difficulty, nextReviewAt} matching SPEC.md §5.2's frozen
 * MasteryState shape, plus `lastReviewedAt` (not in that frozen list — added here, and to
 * MasteryState/the new SrsCard type, because FSRS's stability-growth math is driven by the
 * *actual* elapsed time since the previous review, not just "now vs. when it was due"; without
 * it, reviewing early or late all looked identical, caught by a test asserting stability should
 * grow across two well-spaced Good reviews and reliably not moving at all). Reconstructing a full
 * ts-fsrs Card from these four treats every review as the long-interval "Review" state (not
 * FSRS's short-term "Learning" steps) — correct for this app's use case (spaced-out topic/card
 * reviews, not minutes-apart flashcard cramming), and reps/lapses are bookkeeping FSRS's core
 * scheduling math doesn't depend on.
 */
export interface FsrsState {
  stability: number
  difficulty: number
  nextReviewAt: number
  lastReviewedAt?: number
}

export function initFsrsState(now: number = Date.now()): FsrsState {
  const card = createEmptyCard(new Date(now))
  return { stability: card.stability, difficulty: card.difficulty, nextReviewAt: card.due.getTime() }
}

function toCard(state: FsrsState): Card {
  return {
    due: new Date(state.nextReviewAt),
    stability: state.stability,
    difficulty: state.difficulty,
    elapsed_days: 0,
    scheduled_days: 0,
    learning_steps: 0,
    reps: 1,
    lapses: 0,
    state: State.Review,
    last_review: state.lastReviewedAt !== undefined ? new Date(state.lastReviewedAt) : undefined,
  }
}

export function isDue(state: FsrsState | undefined, now: number = Date.now()): boolean {
  return !state || state.nextReviewAt <= now
}

/** Grades a review (Again/Hard/Good/Easy) and returns the updated schedule. `state` undefined
 * means this is the item's first-ever review. */
export function gradeReview(state: FsrsState | undefined, grade: Grade, now: number = Date.now()): FsrsState {
  const card = state ? toCard(state) : createEmptyCard(new Date(now))
  const result = scheduler.next(card, new Date(now), grade)
  return {
    stability: result.card.stability,
    difficulty: result.card.difficulty,
    nextReviewAt: result.card.due.getTime(),
    lastReviewedAt: now,
  }
}
