import { loadLesson } from '@/content/loadContent'
import type { StorageAdapter } from '@/storage/StorageAdapter'
import type { SrsCard } from '@/types/state'
import { initFsrsState } from './fsrsAdapter'

/** SPEC.md §8.4: "Card level — ... every question she got wrong (auto-added as a card)." Never
 * resets an already-tracked card's schedule just because she got it wrong again — that's what
 * grading the review as Again is for, not re-adding it. */
export async function addMistakeCard(
  questionId: string,
  microTopicId: string,
  storageAdapter: StorageAdapter,
  now: number = Date.now(),
): Promise<void> {
  const id = `mistake:${questionId}`
  if (await storageAdapter.getSrsCard(id)) return
  const fsrs = initFsrsState(now)
  const card: SrsCard = { schemaVersion: 1, id, cardType: 'mistake', refId: questionId, microTopicId, ...fsrs, addedAt: now }
  await storageAdapter.putSrsCard(card)
}

/** SPEC.md §8.5's error-taxonomy table: "Didn't know formula -> Auto-add the formula card to the
 * SRS deck." Adds every formula card for the topic (a lesson usually has one or two, and Question
 * doesn't reference which specific formula it needed — safer to add all of the topic's than
 * guess wrong and add none). */
export async function addFormulaCardsForTopic(
  microTopicId: string,
  storageAdapter: StorageAdapter,
  now: number = Date.now(),
): Promise<void> {
  const lesson = await loadLesson(microTopicId)
  if (!lesson?.formulaCards) return
  for (const fc of lesson.formulaCards) {
    const id = `formula:${fc.id}`
    if (await storageAdapter.getSrsCard(id)) continue
    const fsrs = initFsrsState(now)
    const card: SrsCard = { schemaVersion: 1, id, cardType: 'formula', refId: fc.id, microTopicId, ...fsrs, addedAt: now }
    await storageAdapter.putSrsCard(card)
  }
}
