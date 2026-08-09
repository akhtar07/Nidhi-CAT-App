import { describe, expect, it } from 'vitest'
import type { Question } from '@/types/content'
import type { MockQuestionState } from '@/types/state'
import { computeAllSectionScores, computeSectionScore, scoreQuestion } from './scoring'

function mcq(id: string, correctKey = 'A'): Question {
  return {
    id,
    microTopicIds: ['qa.test'],
    section: 'QA',
    format: 'mcq',
    stemMarkdown: 'stem',
    options: [
      { key: 'A', markdown: 'a' },
      { key: 'B', markdown: 'b' },
    ],
    correctKey,
    difficulty: 'easy',
    eloRating: 1000,
    solutionMarkdown: 'sol',
    targetSeconds: 60,
    source: 'generated',
    verification: { method: 'sympy_verified', verifiedAt: '2026-01-01' },
    tags: [],
  }
}

function tita(id: string, correctValue: number = 42, tolerance = 0.1): Question {
  return {
    id,
    microTopicIds: ['qa.test'],
    section: 'QA',
    format: 'tita',
    stemMarkdown: 'stem',
    correctValue,
    titaTolerance: tolerance,
    difficulty: 'easy',
    eloRating: 1000,
    solutionMarkdown: 'sol',
    targetSeconds: 60,
    source: 'generated',
    verification: { method: 'sympy_verified', verifiedAt: '2026-01-01' },
    tags: [],
  }
}

describe('scoreQuestion', () => {
  it('is 0 for a skipped question (null given)', () => {
    expect(scoreQuestion(mcq('q1'), null)).toBe(0)
  })

  it('is +3 for a correct MCQ', () => {
    expect(scoreQuestion(mcq('q1', 'A'), 'A')).toBe(3)
  })

  it('is -1 for a wrong MCQ', () => {
    expect(scoreQuestion(mcq('q1', 'A'), 'B')).toBe(-1)
  })

  it('is +3 for a correct TITA', () => {
    expect(scoreQuestion(tita('q1', 42), '42')).toBe(3)
  })

  it('is 0 (not negative) for a wrong TITA — SPEC.md §2 asymmetry', () => {
    expect(scoreQuestion(tita('q1', 42), '99')).toBe(0)
  })
})

describe('computeSectionScore', () => {
  it('tallies correct/incorrect/skipped and total score across a section', () => {
    const questions = [mcq('q1', 'A'), mcq('q2', 'A'), tita('q3', 42)]
    const states: Record<string, MockQuestionState> = {
      q1: { given: 'A', markedForReview: false, visitCount: 1, dwellSec: 10 }, // correct +3
      q2: { given: 'B', markedForReview: false, visitCount: 1, dwellSec: 10 }, // wrong -1
      // q3 not attempted at all -> skipped
    }
    const summary = computeSectionScore(questions, states)
    expect(summary.correct).toBe(1)
    expect(summary.incorrect).toBe(1)
    expect(summary.skipped).toBe(1)
    expect(summary.score).toBe(2)
  })
})

describe('computeAllSectionScores', () => {
  it('computes a summary per section independently', () => {
    const qa = [mcq('qa1', 'A')]
    const varc = [mcq('varc1', 'A')]
    const states: Record<string, MockQuestionState> = {
      qa1: { given: 'A', markedForReview: false, visitCount: 1, dwellSec: 0 },
      varc1: { given: 'B', markedForReview: false, visitCount: 1, dwellSec: 0 },
    }
    const result = computeAllSectionScores({ QA: qa, VARC: varc, DILR: [] }, states)
    expect(result.QA.correct).toBe(1)
    expect(result.VARC.incorrect).toBe(1)
    expect(result.DILR.skipped).toBe(0)
  })
})
