import type { QuestionIndexEntry } from '@/content/loadContent'
import type { Question } from '@/types/content'

export type Difficulty = Question['difficulty']
/** Derived from the content type rather than imported from types/state, so this module
 * depends only on shipped-content shapes and not on learner-state definitions. */
export type Section = Question['section']

export const ALL_DIFFICULTIES: Difficulty[] = ['easy', 'medium', 'hard', 'very_hard']
export const ALL_SECTIONS: Section[] = ['VARC', 'DILR', 'QA']

/**
 * What the learner asked for. Empty arrays mean "no restriction on this axis" rather
 * than "match nothing" — that's the behaviour a filter UI implies when you tick nothing.
 */
export interface PracticeFilters {
  sections: Section[]
  microTopicIds: string[]
  difficulties: Difficulty[]
  count: number
}

export interface PracticeSelection {
  questionIds: string[]
  /** How many questions matched the filters in total, before capping to `count`. */
  matchedCount: number
  requestedCount: number
  /** requested - selected. Non-zero means the bank couldn't satisfy the request. */
  shortfall: number
  byDifficulty: Record<Difficulty, number>
  byTopic: Record<string, number>
}

export const DEFAULT_FILTERS: PracticeFilters = {
  sections: [],
  microTopicIds: [],
  difficulties: [],
  count: 10,
}

export function matchesFilters(entry: QuestionIndexEntry, filters: PracticeFilters): boolean {
  if (filters.sections.length > 0 && !filters.sections.includes(entry.section)) return false
  if (filters.difficulties.length > 0 && !filters.difficulties.includes(entry.difficulty)) return false
  if (filters.microTopicIds.length > 0) {
    const wanted = new Set(filters.microTopicIds)
    if (!entry.microTopicIds.some((id) => wanted.has(id))) return false
  }
  return true
}

/**
 * Mulberry32 — a tiny deterministic PRNG. Seeded so a given set is reproducible in tests;
 * the UI seeds it from Date.now() so two runs with identical filters differ.
 */
export function makeRng(seed: number): () => number {
  let a = seed >>> 0
  return () => {
    a = (a + 0x6d2b79f5) >>> 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function shuffled<T>(items: T[], rng: () => number): T[] {
  const out = [...items]
  for (let i = out.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1))
    ;[out[i], out[j]] = [out[j], out[i]]
  }
  return out
}

/**
 * Picks a practice set from the shipped question index.
 *
 * Two deliberate choices:
 *
 * 1. **Mock-reserved items can't leak in.** `scripts/sync-content.mjs` omits every
 *    `mockReserved` question from `questions/index.json` entirely, so anything built off
 *    the index is reserved-safe by construction (SPEC.md §9.1 — "the drill engine can
 *    never serve them"). This function therefore takes the index, never raw questions.
 *
 * 2. **The set is spread, not clumped.** Naively taking the first N matches would hand
 *    back 10 questions from one topic at one difficulty, since the index is ordered by
 *    filename. Instead it round-robins across difficulty buckets, and within each bucket
 *    round-robins across topics, so a "mixed" request is genuinely mixed.
 */
export function buildPracticeSet(
  index: QuestionIndexEntry[],
  filters: PracticeFilters,
  rng: () => number = Math.random,
): PracticeSelection {
  const matched = index.filter((entry) => matchesFilters(entry, filters))
  const requestedCount = Math.max(0, Math.floor(filters.count))

  // difficulty -> topic -> shuffled entries
  const buckets = new Map<Difficulty, Map<string, QuestionIndexEntry[]>>()
  for (const entry of shuffled(matched, rng)) {
    const topicKey = entry.microTopicIds[0] ?? 'unknown'
    const byTopic = buckets.get(entry.difficulty) ?? new Map<string, QuestionIndexEntry[]>()
    const list = byTopic.get(topicKey) ?? []
    list.push(entry)
    byTopic.set(topicKey, list)
    buckets.set(entry.difficulty, byTopic)
  }

  // Only walk difficulties that actually produced matches, so an empty band doesn't
  // consume a slot in the rotation and skew the spread.
  const activeDifficulties = ALL_DIFFICULTIES.filter((d) => (buckets.get(d)?.size ?? 0) > 0)

  const picked: QuestionIndexEntry[] = []
  let progressed = true
  while (picked.length < requestedCount && progressed) {
    progressed = false
    for (const difficulty of activeDifficulties) {
      if (picked.length >= requestedCount) break
      const byTopic = buckets.get(difficulty)
      if (!byTopic || byTopic.size === 0) continue
      // Take one from the next topic that still has anything left.
      const topicKey = [...byTopic.keys()][0]
      const list = byTopic.get(topicKey)!
      const entry = list.shift()!
      if (list.length === 0) byTopic.delete(topicKey)
      else {
        // Rotate this topic to the back so the next pass hits a different one.
        byTopic.delete(topicKey)
        byTopic.set(topicKey, list)
      }
      picked.push(entry)
      progressed = true
    }
  }

  const byDifficulty: Record<Difficulty, number> = { easy: 0, medium: 0, hard: 0, very_hard: 0 }
  const byTopic: Record<string, number> = {}
  for (const entry of picked) {
    byDifficulty[entry.difficulty] += 1
    const key = entry.microTopicIds[0] ?? 'unknown'
    byTopic[key] = (byTopic[key] ?? 0) + 1
  }

  return {
    questionIds: picked.map((e) => e.id),
    matchedCount: matched.length,
    requestedCount,
    shortfall: Math.max(0, requestedCount - picked.length),
    byDifficulty,
    byTopic,
  }
}

/**
 * Honest one-line description of what the filters actually yielded, so a shortfall is
 * stated rather than silently swallowed.
 */
export function describeSelection(selection: PracticeSelection): string {
  if (selection.matchedCount === 0) {
    return 'No questions match these filters yet.'
  }
  if (selection.shortfall > 0) {
    return `Only ${selection.questionIds.length} of the ${selection.requestedCount} you asked for — the bank has ${selection.matchedCount} matching question${selection.matchedCount === 1 ? '' : 's'}.`
  }
  return `${selection.questionIds.length} questions, drawn from ${selection.matchedCount} matching the filters.`
}
