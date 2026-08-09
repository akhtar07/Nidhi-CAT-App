import type { MockQuestionState, PaletteStatus } from '@/types/state'

/** SPEC.md §9.1's real-CAT palette convention: Not Visited (grey), Not Answered (red),
 * Answered (green), Marked for Review (purple), Answered & Marked (purple with tick). */
export function derivePaletteStatus(state: MockQuestionState | undefined): PaletteStatus {
  if (!state || state.visitCount === 0) return 'not_visited'
  const answered = state.given !== null && state.given !== ''
  if (answered && state.markedForReview) return 'answered_marked'
  if (state.markedForReview) return 'marked'
  if (answered) return 'answered'
  return 'not_answered'
}
