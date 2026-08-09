import { storage } from '@/storage'
import type { StorageAdapter } from '@/storage/StorageAdapter'
import { gradeReview, type FsrsState } from '@/srs/fsrsAdapter'
import { mapAttemptToGrade } from '@/srs/topicReview'
import type { MicroTopic, Question } from '@/types/content'
import type { Attempt, MasteryState } from '@/types/state'
import { DEFAULT_ITEM_ELO, DEFAULT_LEARNER_ELO, effectiveCorrectness, updateElo } from './elo'
import { evaluateMastery } from './masteryCriteria'

export interface RecordAttemptForMasteryInput {
  attempt: Attempt
  question: Question
  topic: MicroTopic
  /** Every Question belonging to this micro-topic — used to resolve difficulty for the topic's full attempt history without re-fetching content. */
  topicQuestions: Question[]
  storageAdapter?: StorageAdapter
}

/**
 * Called right after an Attempt is logged (see QuestionPlayer.tsx). Updates
 * both sides of Elo (SPEC.md §8.3) and re-evaluates the mastery state
 * machine (§8.1/§8.2) for the attempt's micro-topic, then persists both.
 * Not itself unit-tested in isolation — the algorithm it wires together
 * (elo.ts, masteryCriteria.ts) is; this function is thin, storage-coupled
 * glue, covered by DexieAdapter's existing round-trip guarantees.
 */
export async function recordAttemptForMastery({
  attempt,
  question,
  topic,
  topicQuestions,
  storageAdapter = storage,
}: RecordAttemptForMasteryInput): Promise<MasteryState> {
  const microTopicId = topic.id
  const existing = await storageAdapter.getMasteryState(microTopicId)

  const priorLearnerElo = existing?.learnerElo ?? DEFAULT_LEARNER_ELO
  const priorItemElo = (await storageAdapter.getItemElo(question.id)) ?? question.eloRating ?? DEFAULT_ITEM_ELO
  const topicAttemptsCountSoFar = existing?.attemptsCount ?? 0

  const { learnerElo, itemElo } = updateElo({
    learnerElo: priorLearnerElo,
    itemElo: priorItemElo,
    actual: effectiveCorrectness(attempt),
    topicAttemptsCountSoFar,
  })
  await storageAdapter.putItemElo(question.id, itemElo)

  const difficultyById = new Map(topicQuestions.map((q) => [q.id, q.difficulty]))
  const allAttempts = await storageAdapter.listAttempts({ microTopicId })

  const evaluation = evaluateMastery({
    attempts: allAttempts.map((a) => ({
      correct: a.correct,
      confidence: a.confidence,
      timeSpentSec: a.timeSpentSec,
      submittedAt: a.submittedAt,
      difficulty: difficultyById.get(a.questionId) ?? question.difficulty,
    })),
    targetSecPerQuestion: topic.targetSecPerQuestion,
    now: attempt.submittedAt,
    criteria123FirstMetAt: existing?.criteria123FirstMetAt,
  })

  // SPEC.md §8.4: FSRS at the micro-topic level. Every attempt is treated as an implicit review
  // of that topic's forgetting curve (see topicReview.ts for why) — grade derived from
  // correctness + the same pre-reveal confidence signal §8.5's guess-discount uses.
  const priorFsrsState: FsrsState | undefined =
    existing?.stability || existing?.nextReviewAt
      ? { stability: existing.stability, difficulty: existing.difficulty, nextReviewAt: existing.nextReviewAt ?? attempt.submittedAt, lastReviewedAt: existing.lastReviewedAt }
      : undefined
  const fsrsState = gradeReview(priorFsrsState, mapAttemptToGrade(attempt), attempt.submittedAt)

  const newState: MasteryState = {
    schemaVersion: 1,
    microTopicId,
    status: evaluation.status,
    learnerElo,
    lastNCorrect: evaluation.lastNCorrect,
    medianTimeSec: evaluation.medianTimeSec,
    hardTierCleared: evaluation.ceilingOk,
    attemptsCount: evaluation.attemptsCount,
    masteredAt: evaluation.status === 'mastered' ? (existing?.masteredAt ?? attempt.submittedAt) : existing?.masteredAt,
    criteria123FirstMetAt: evaluation.criteria123FirstMetAt,
    antiFrustrationTriggered: evaluation.antiFrustrationTriggered,
    nextReviewAt: fsrsState.nextReviewAt,
    stability: fsrsState.stability,
    difficulty: fsrsState.difficulty,
    lastReviewedAt: fsrsState.lastReviewedAt,
  }
  await storageAdapter.putMasteryState(newState)
  return newState
}
