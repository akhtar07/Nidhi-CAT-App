import type { QuestionIndexEntry } from '@/content/loadContent'

type Section = QuestionIndexEntry['section']

const SECTIONS: Section[] = ['VARC', 'DILR', 'QA']
const DIFFICULTY_ORDER: QuestionIndexEntry['difficulty'][] = ['easy', 'medium', 'hard', 'very_hard']

interface SectionCursor {
  byDifficulty: Map<QuestionIndexEntry['difficulty'], QuestionIndexEntry[]>
  di: number
  remaining: number
}

function takeNext(cursor: SectionCursor): QuestionIndexEntry | undefined {
  for (let i = 0; i < DIFFICULTY_ORDER.length; i++) {
    const difficulty = DIFFICULTY_ORDER[cursor.di % DIFFICULTY_ORDER.length]
    cursor.di++
    const bucket = cursor.byDifficulty.get(difficulty)
    if (bucket && bucket.length > 0) {
      cursor.remaining--
      return bucket.shift()
    }
  }
  return undefined
}

/**
 * SPEC.md §10.1: "~15 questions spanning sections and difficulty" for the
 * first-launch diagnostic. Splits the target count evenly across the three
 * sections, striding evenly across the difficulty ladder within each
 * section's pool rather than clustering on whatever the bank has most of.
 * A section with no content yet (VARC has none as of Milestone 9 — RC/VA
 * generation is Milestone 13) contributes 0, and its share is topped up
 * from whichever sections do have content, so the diagnostic still returns
 * a full-size set rather than silently coming up short.
 */
export function selectDiagnosticQuestions(index: QuestionIndexEntry[], count = 15): QuestionIndexEntry[] {
  const cursors = new Map<Section, SectionCursor>()
  for (const section of SECTIONS) {
    cursors.set(section, { byDifficulty: new Map(DIFFICULTY_ORDER.map((d) => [d, []])), di: 0, remaining: 0 })
  }
  for (const entry of index) {
    const cursor = cursors.get(entry.section)
    cursor?.byDifficulty.get(entry.difficulty)?.push(entry)
    if (cursor) cursor.remaining++
  }

  const perSection = Math.ceil(count / SECTIONS.length)
  const selected: QuestionIndexEntry[] = []

  for (const section of SECTIONS) {
    const cursor = cursors.get(section)!
    for (let i = 0; i < perSection && selected.length < count; i++) {
      const next = takeNext(cursor)
      if (next) selected.push(next)
    }
  }

  // Top up from whichever sections still have content, round-robin, until
  // `count` is reached or the whole bank is exhausted.
  let madeProgress = true
  while (selected.length < count && madeProgress) {
    madeProgress = false
    for (const section of SECTIONS) {
      if (selected.length >= count) break
      const cursor = cursors.get(section)!
      const next = takeNext(cursor)
      if (next) {
        selected.push(next)
        madeProgress = true
      }
    }
  }

  return selected
}
