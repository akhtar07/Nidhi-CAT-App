import { computeCorrect } from '@/components/question-player/QuestionPlayer'
import type { Question } from '@/types/content'
import type { MockQuestionState, Section } from '@/types/state'

/** SPEC.md §2's marking scheme: MCQ +3/-1, TITA +3/0 — the asymmetry the whole app is built to
 * teach around (always attempt TITA, be selective on MCQ). */
export function scoreQuestion(question: Question, given: string | null): number {
  if (given === null || given === '') return 0
  const correct = computeCorrect(question, given)
  if (correct) return 3
  return question.format === 'mcq' ? -1 : 0
}

export interface SectionScoreSummary {
  score: number
  correct: number
  incorrect: number
  skipped: number
}

export function computeSectionScore(
  questions: Question[],
  questionStates: Record<string, MockQuestionState>,
): SectionScoreSummary {
  let score = 0
  let correct = 0
  let incorrect = 0
  let skipped = 0
  for (const q of questions) {
    const given = questionStates[q.id]?.given ?? null
    if (given === null || given === '') {
      skipped++
      continue
    }
    if (computeCorrect(q, given)) {
      correct++
    } else {
      incorrect++
    }
    score += scoreQuestion(q, given)
  }
  return { score, correct, incorrect, skipped }
}

export function computeAllSectionScores(
  questionsBySection: Record<Section, Question[]>,
  questionStates: Record<string, MockQuestionState>,
): Record<Section, SectionScoreSummary> {
  const sections: Section[] = ['VARC', 'DILR', 'QA']
  const result = {} as Record<Section, SectionScoreSummary>
  for (const section of sections) {
    result[section] = computeSectionScore(questionsBySection[section] ?? [], questionStates)
  }
  return result
}
