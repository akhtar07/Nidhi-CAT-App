import { describe, expect, it } from 'vitest'
import { Rating } from './fsrsAdapter'
import { applyDecay, mapAttemptToGrade, withDecayApplied } from './topicReview'
import type { MasteryState } from '@/types/state'

function mastery(overrides: Partial<MasteryState>): MasteryState {
  return {
    schemaVersion: 1,
    microTopicId: 'qa.test',
    status: 'mastered',
    learnerElo: 1200,
    lastNCorrect: [],
    medianTimeSec: 60,
    hardTierCleared: true,
    attemptsCount: 20,
    stability: 5,
    difficulty: 5,
    ...overrides,
  }
}

describe('mapAttemptToGrade', () => {
  it('is Again for any incorrect answer regardless of confidence', () => {
    expect(mapAttemptToGrade({ correct: false, confidence: 'sure' })).toBe(Rating.Again)
    expect(mapAttemptToGrade({ correct: false, confidence: undefined })).toBe(Rating.Again)
  })
  it('is Hard for a correct guess', () => {
    expect(mapAttemptToGrade({ correct: true, confidence: 'guess' })).toBe(Rating.Hard)
  })
  it('is Good for a correct-but-unsure answer', () => {
    expect(mapAttemptToGrade({ correct: true, confidence: 'unsure' })).toBe(Rating.Good)
  })
  it('is Easy for a confident correct answer, or no confidence recorded', () => {
    expect(mapAttemptToGrade({ correct: true, confidence: 'sure' })).toBe(Rating.Easy)
    expect(mapAttemptToGrade({ correct: true, confidence: undefined })).toBe(Rating.Easy)
  })
})

describe('applyDecay', () => {
  const now = 1_000_000

  it('leaves non-mastered topics alone even if nextReviewAt has passed', () => {
    const state = mastery({ status: 'practising', nextReviewAt: now - 1000 })
    expect(applyDecay(state, now).status).toBe('practising')
  })

  it('leaves a mastered topic alone if review is not yet due', () => {
    const state = mastery({ status: 'mastered', nextReviewAt: now + 1000 })
    expect(applyDecay(state, now).status).toBe('mastered')
  })

  it('leaves a mastered topic alone if it has never been FSRS-scheduled at all', () => {
    const state = mastery({ status: 'mastered', nextReviewAt: undefined })
    expect(applyDecay(state, now).status).toBe('mastered')
  })

  it('downgrades a mastered topic to decaying once its review is due', () => {
    const state = mastery({ status: 'mastered', nextReviewAt: now - 1 })
    expect(applyDecay(state, now).status).toBe('decaying')
  })

  it('does not mutate other fields', () => {
    const state = mastery({ status: 'mastered', nextReviewAt: now - 1, learnerElo: 1350 })
    const decayed = applyDecay(state, now)
    expect(decayed.learnerElo).toBe(1350)
    expect(decayed.hardTierCleared).toBe(true)
  })
})

describe('withDecayApplied', () => {
  it('applies decay across a list independently', () => {
    const now = 1_000_000
    const states = [
      mastery({ microTopicId: 'a', status: 'mastered', nextReviewAt: now - 1 }),
      mastery({ microTopicId: 'b', status: 'mastered', nextReviewAt: now + 1 }),
    ]
    const result = withDecayApplied(states, now)
    expect(result.find((s) => s.microTopicId === 'a')?.status).toBe('decaying')
    expect(result.find((s) => s.microTopicId === 'b')?.status).toBe('mastered')
  })
})
