import { describe, expect, it } from 'vitest'
import type { MockDefinition, Question } from '@/types/content'
import type { Attempt, MockResult } from '@/types/state'
import {
  computeAccuracyVsAttemptsCurve,
  computeBleederReport,
  computeMicroTopicDamage,
  computeSelectionQuality,
  computeTimeWaterfall,
  computeTitaDiscipline,
} from './analysis'

function mcq(id: string, correctKey = 'A', eloRating = 1000): Question {
  return {
    id,
    microTopicIds: ['qa.test'],
    section: 'QA',
    format: 'mcq',
    stemMarkdown: `stem for ${id}`,
    options: [
      { key: 'A', markdown: 'a' },
      { key: 'B', markdown: 'b' },
    ],
    correctKey,
    difficulty: 'easy',
    eloRating,
    solutionMarkdown: 'sol',
    targetSeconds: 60,
    source: 'generated',
    verification: { method: 'sympy_verified', verifiedAt: '2026-01-01' },
    tags: [],
  }
}

function tita(id: string, correctValue = 42, eloRating = 1000): Question {
  return {
    id,
    microTopicIds: ['qa.test'],
    section: 'QA',
    format: 'tita',
    stemMarkdown: `stem for ${id}`,
    correctValue,
    titaTolerance: 0.1,
    difficulty: 'easy',
    eloRating,
    solutionMarkdown: 'sol',
    targetSeconds: 60,
    source: 'generated',
    verification: { method: 'sympy_verified', verifiedAt: '2026-01-01' },
    tags: [],
  }
}

function attempt(overrides: Partial<Attempt> & Pick<Attempt, 'questionId'>): Attempt {
  return {
    schemaVersion: 1,
    id: crypto.randomUUID(),
    microTopicIds: ['qa.test'],
    startedAt: 0,
    submittedAt: 1000,
    timeSpentSec: 30,
    given: null,
    correct: false,
    mode: 'mock',
    markedForReview: false,
    ...overrides,
  }
}

describe('computeTimeWaterfall', () => {
  it('sums minutes and score per section', () => {
    const mockDef: MockDefinition = {
      id: 'm1',
      title: 'Mock',
      kind: 'full',
      sections: [{ section: 'QA', minutes: 40, questionIds: ['q1', 'q2'] }],
    }
    const result: MockResult = {
      schemaVersion: 1,
      id: 'r1',
      mockId: 'm1',
      takenAt: 0,
      sectionScores: { QA: { score: 6, correct: 2, incorrect: 0, skipped: 0 }, VARC: { score: 0, correct: 0, incorrect: 0, skipped: 0 }, DILR: { score: 0, correct: 0, incorrect: 0, skipped: 0 } },
      questionTimings: { q1: 60, q2: 120 },
    }
    const waterfall = computeTimeWaterfall(mockDef, result)
    expect(waterfall).toEqual([{ section: 'QA', minutesSpent: 3, marksEarned: 6 }])
  })
})

describe('computeBleederReport', () => {
  it('only includes attempted, wrong, slow questions, sorted by time descending', () => {
    const questionsById = new Map([
      ['fast_wrong', mcq('fast_wrong')],
      ['slow_wrong', mcq('slow_wrong')],
      ['slow_right', mcq('slow_right')],
      ['slow_skipped', mcq('slow_skipped')],
    ])
    const attempts = [
      attempt({ questionId: 'fast_wrong', given: 'B', correct: false, timeSpentSec: 50 }),
      attempt({ questionId: 'slow_wrong', given: 'B', correct: false, timeSpentSec: 200 }),
      attempt({ questionId: 'slow_right', given: 'A', correct: true, timeSpentSec: 300 }),
      attempt({ questionId: 'slow_skipped', given: null, correct: false, timeSpentSec: 400 }),
    ]
    const report = computeBleederReport(attempts, questionsById, 150)
    expect(report.map((r) => r.questionId)).toEqual(['slow_wrong'])
  })
})

describe('computeSelectionQuality', () => {
  it('flags skipping easy (below-median) items as poor selection', () => {
    const questionsById = new Map([
      ['easy1', mcq('easy1', 'A', 800)],
      ['hard1', mcq('hard1', 'A', 1600)],
    ])
    const attempts = [attempt({ questionId: 'easy1', given: null }), attempt({ questionId: 'hard1', given: null })]
    const quality = computeSelectionQuality(attempts, questionsById, new Map())
    expect(quality.skippedCount).toBe(2)
    expect(quality.easySkippedCount).toBe(1)
    expect(quality.easySkipFraction).toBe(0.5)
  })
})

describe('computeTitaDiscipline', () => {
  it('flags only blank TITA questions, not MCQ or answered TITA', () => {
    const questionsById = new Map([
      ['tita_blank', tita('tita_blank')],
      ['tita_answered', tita('tita_answered')],
      ['mcq_blank', mcq('mcq_blank')],
    ])
    const attempts = [
      attempt({ questionId: 'tita_blank', given: null }),
      attempt({ questionId: 'tita_answered', given: '42' }),
      attempt({ questionId: 'mcq_blank', given: null }),
    ]
    const blanks = computeTitaDiscipline(attempts, questionsById)
    expect(blanks.map((b) => b.questionId)).toEqual(['tita_blank'])
  })
})

describe('computeAccuracyVsAttemptsCurve', () => {
  it('orders by difficulty and finds the score-maximizing attempt count', () => {
    // easy correct (+3), medium wrong (-1), hard correct (+3) — stopping after 1 or 3 both peak at
    // a local max, but continuing to include the wrong one first drops the running score.
    const questionsById = new Map([
      ['easy', mcq('easy', 'A', 800)],
      ['medium', mcq('medium', 'A', 1200)],
      ['hard', mcq('hard', 'A', 1600)],
    ])
    const attempts = [
      attempt({ questionId: 'medium', given: 'B', correct: false }), // wrong -> -1
      attempt({ questionId: 'hard', given: 'A', correct: true }), // right -> +3
      attempt({ questionId: 'easy', given: 'A', correct: true }), // right -> +3
    ]
    const result = computeAccuracyVsAttemptsCurve(attempts, questionsById, new Map())
    // sorted easiest-first: easy(+3) -> medium(-1) -> hard(+3); cumulative: 0,3,2,5
    expect(result.curve.map((p) => p.score)).toEqual([0, 3, 2, 5])
    expect(result.optimalAttemptCount).toBe(3)
    expect(result.actualAttemptCount).toBe(3)
  })

  it('excludes skipped questions from the curve entirely', () => {
    const questionsById = new Map([['q1', mcq('q1')]])
    const attempts = [attempt({ questionId: 'q1', given: null })]
    const result = computeAccuracyVsAttemptsCurve(attempts, questionsById, new Map())
    expect(result.actualAttemptCount).toBe(0)
    expect(result.curve).toEqual([{ attemptCount: 0, score: 0 }])
  })
})

describe('computeMicroTopicDamage', () => {
  it('sums marks lost per micro-topic from wrong MCQ attempts, sorted descending', () => {
    const questionsById = new Map([
      ['a1', { ...mcq('a1'), microTopicIds: ['topicA'] as [string] }],
      ['a2', { ...mcq('a2'), microTopicIds: ['topicA'] as [string] }],
      ['b1', { ...mcq('b1'), microTopicIds: ['topicB'] as [string] }],
    ])
    const attempts = [
      attempt({ questionId: 'a1', microTopicIds: ['topicA'], given: 'B', correct: false }),
      attempt({ questionId: 'a2', microTopicIds: ['topicA'], given: 'B', correct: false }),
      attempt({ questionId: 'b1', microTopicIds: ['topicB'], given: 'B', correct: false }),
    ]
    const damage = computeMicroTopicDamage(attempts, questionsById)
    expect(damage[0]).toEqual({ microTopicId: 'topicA', marksLost: 2, incorrectCount: 2 })
    expect(damage[1]).toEqual({ microTopicId: 'topicB', marksLost: 1, incorrectCount: 1 })
  })

  it('does not count wrong TITA as marks lost (SPEC.md §2: TITA wrong = 0, not negative)', () => {
    const questionsById = new Map([['t1', { ...tita('t1'), microTopicIds: ['topicA'] as [string] }]])
    const attempts = [attempt({ questionId: 't1', microTopicIds: ['topicA'], given: '99', correct: false })]
    const damage = computeMicroTopicDamage(attempts, questionsById)
    expect(damage).toEqual([])
  })
})
