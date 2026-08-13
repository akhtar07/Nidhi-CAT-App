import { describe, expect, it } from 'vitest'
import {
  buildPracticeSet,
  describeSelection,
  makeRng,
  matchesFilters,
  type PracticeFilters,
  type Section,
} from './buildPracticeSet'
import type { QuestionIndexEntry } from '@/content/loadContent'
import type { Question } from '@/types/content'

function entry(
  id: string,
  section: Section,
  difficulty: Question['difficulty'],
  topics: string[],
): QuestionIndexEntry {
  return { id, microTopicIds: topics, section, format: 'mcq', difficulty, targetSeconds: 60 }
}

function filters(overrides: Partial<PracticeFilters> = {}): PracticeFilters {
  return { sections: [], microTopicIds: [], difficulties: [], count: 10, ...overrides }
}

// A fixed rng keeps every assertion below about the *algorithm*, not about luck.
const rng = () => makeRng(42)()

describe('matchesFilters', () => {
  const e = entry('q1', 'QA', 'medium', ['qa.arith.percentages'])

  it('matches everything when no filters are set', () => {
    expect(matchesFilters(e, filters())).toBe(true)
  })

  it('filters by section', () => {
    expect(matchesFilters(e, filters({ sections: ['QA'] }))).toBe(true)
    expect(matchesFilters(e, filters({ sections: ['VARC'] }))).toBe(false)
  })

  it('filters by difficulty', () => {
    expect(matchesFilters(e, filters({ difficulties: ['medium'] }))).toBe(true)
    expect(matchesFilters(e, filters({ difficulties: ['easy', 'hard'] }))).toBe(false)
  })

  it('filters by micro-topic, matching any of the question topics', () => {
    expect(matchesFilters(e, filters({ microTopicIds: ['qa.arith.percentages'] }))).toBe(true)
    expect(matchesFilters(e, filters({ microTopicIds: ['qa.numsys.hcf-lcm'] }))).toBe(false)
    const multi = entry('q2', 'QA', 'easy', ['a', 'b'])
    expect(matchesFilters(multi, filters({ microTopicIds: ['b'] }))).toBe(true)
  })

  it('requires every set filter to pass at once', () => {
    expect(matchesFilters(e, filters({ sections: ['QA'], difficulties: ['easy'] }))).toBe(false)
  })
})

describe('buildPracticeSet', () => {
  const index: QuestionIndexEntry[] = [
    ...Array.from({ length: 6 }, (_, i) => entry(`e${i}`, 'QA', 'easy', ['qa.a'])),
    ...Array.from({ length: 6 }, (_, i) => entry(`m${i}`, 'QA', 'medium', ['qa.b'])),
    ...Array.from({ length: 6 }, (_, i) => entry(`h${i}`, 'DILR', 'hard', ['dilr.a'])),
  ]

  it('returns exactly the requested number when enough questions match', () => {
    const result = buildPracticeSet(index, filters({ count: 9 }), rng)
    expect(result.questionIds).toHaveLength(9)
    expect(result.shortfall).toBe(0)
    expect(result.requestedCount).toBe(9)
    expect(result.matchedCount).toBe(18)
  })

  it('spreads across difficulty bands rather than draining one', () => {
    // 9 requested across 3 equally sized bands should be 3 each, not 6 easy + 3 medium.
    const result = buildPracticeSet(index, filters({ count: 9 }), rng)
    expect(result.byDifficulty).toEqual({ easy: 3, medium: 3, hard: 3, very_hard: 0 })
  })

  it('spreads across topics within a difficulty band', () => {
    const twoTopics: QuestionIndexEntry[] = [
      ...Array.from({ length: 5 }, (_, i) => entry(`x${i}`, 'QA', 'easy', ['qa.x'])),
      ...Array.from({ length: 5 }, (_, i) => entry(`y${i}`, 'QA', 'easy', ['qa.y'])),
    ]
    const result = buildPracticeSet(twoTopics, filters({ count: 4 }), rng)
    expect(result.byTopic).toEqual({ 'qa.x': 2, 'qa.y': 2 })
  })

  it('reports a shortfall honestly instead of silently returning fewer', () => {
    const result = buildPracticeSet(index, filters({ count: 50 }), rng)
    expect(result.questionIds).toHaveLength(18)
    expect(result.matchedCount).toBe(18)
    expect(result.shortfall).toBe(32)
    expect(describeSelection(result)).toBe(
      'Only 18 of the 50 you asked for — the bank has 18 matching questions.',
    )
  })

  it('returns nothing when the filters exclude everything', () => {
    const result = buildPracticeSet(index, filters({ sections: ['VARC'], count: 5 }), rng)
    expect(result.questionIds).toEqual([])
    expect(result.matchedCount).toBe(0)
    expect(result.shortfall).toBe(5)
    expect(describeSelection(result)).toBe('No questions match these filters yet.')
  })

  it('handles a topic filter that matches a topic with zero questions', () => {
    const result = buildPracticeSet(index, filters({ microTopicIds: ['qa.nothing.here'], count: 5 }), rng)
    expect(result.questionIds).toEqual([])
    expect(result.matchedCount).toBe(0)
  })

  it('handles an empty index', () => {
    const result = buildPracticeSet([], filters({ count: 5 }), rng)
    expect(result.questionIds).toEqual([])
    expect(result.shortfall).toBe(5)
  })

  it('treats a zero or negative count as asking for nothing', () => {
    expect(buildPracticeSet(index, filters({ count: 0 }), rng).questionIds).toEqual([])
    expect(buildPracticeSet(index, filters({ count: -3 }), rng).questionIds).toEqual([])
  })

  it('never repeats a question', () => {
    const result = buildPracticeSet(index, filters({ count: 18 }), rng)
    expect(new Set(result.questionIds).size).toBe(18)
  })

  it('honours a combined section and difficulty filter', () => {
    const result = buildPracticeSet(
      index,
      filters({ sections: ['QA'], difficulties: ['medium'], count: 4 }),
      rng,
    )
    expect(result.questionIds).toHaveLength(4)
    expect(result.byDifficulty.medium).toBe(4)
    expect(result.byDifficulty.easy).toBe(0)
    expect(result.matchedCount).toBe(6)
  })

  it('is deterministic for a given seed', () => {
    const a = buildPracticeSet(index, filters({ count: 9 }), makeRng(7))
    const b = buildPracticeSet(index, filters({ count: 9 }), makeRng(7))
    expect(a.questionIds).toEqual(b.questionIds)
  })
})

describe('describeSelection', () => {
  it('describes a fully satisfied request', () => {
    const result = buildPracticeSet(
      [entry('a', 'QA', 'easy', ['t']), entry('b', 'QA', 'easy', ['t'])],
      filters({ count: 2 }),
      rng,
    )
    expect(describeSelection(result)).toBe('2 questions, drawn from 2 matching the filters.')
  })

  it('uses the singular when exactly one question matches', () => {
    const result = buildPracticeSet([entry('a', 'QA', 'easy', ['t'])], filters({ count: 5 }), rng)
    expect(describeSelection(result)).toBe(
      'Only 1 of the 5 you asked for — the bank has 1 matching question.',
    )
  })
})
