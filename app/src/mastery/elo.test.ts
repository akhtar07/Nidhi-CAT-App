import { describe, expect, it } from 'vitest'
import { effectiveCorrectness, expectedScore, updateElo } from './elo'

describe('expectedScore', () => {
  it('is 0.5 when learner and item elo are equal', () => {
    expect(expectedScore(1200, 1200)).toBeCloseTo(0.5)
  })

  it('is lower for the learner when the item is much harder', () => {
    expect(expectedScore(1600, 1200)).toBeLessThan(0.1)
  })

  it('is higher for the learner when the item is much easier', () => {
    expect(expectedScore(800, 1200)).toBeGreaterThan(0.9)
  })
})

describe('effectiveCorrectness', () => {
  it('is 1 for a confident correct answer', () => {
    expect(effectiveCorrectness({ correct: true, confidence: 'sure' })).toBe(1)
    expect(effectiveCorrectness({ correct: true, confidence: undefined })).toBe(1)
  })

  it('is 0.4 for a correct answer marked as a guess (SPEC.md §8.5)', () => {
    expect(effectiveCorrectness({ correct: true, confidence: 'guess' })).toBe(0.4)
  })

  it('is 0 for an incorrect answer regardless of confidence', () => {
    expect(effectiveCorrectness({ correct: false, confidence: 'sure' })).toBe(0)
    expect(effectiveCorrectness({ correct: false, confidence: 'guess' })).toBe(0)
  })
})

describe('updateElo', () => {
  it('raises learnerElo when the learner outperforms expectation', () => {
    const result = updateElo({ learnerElo: 1200, itemElo: 1200, actual: 1, topicAttemptsCountSoFar: 0 })
    expect(result.learnerElo).toBeGreaterThan(1200)
  })

  it('lowers learnerElo when the learner underperforms expectation', () => {
    const result = updateElo({ learnerElo: 1200, itemElo: 1200, actual: 0, topicAttemptsCountSoFar: 0 })
    expect(result.learnerElo).toBeLessThan(1200)
  })

  it('moves learnerElo by K_L * (actual - expected) with K_L=24 under 200 attempts', () => {
    const result = updateElo({ learnerElo: 1200, itemElo: 1200, actual: 1, topicAttemptsCountSoFar: 50 })
    expect(result.learnerElo).toBeCloseTo(1200 + 24 * 0.5)
  })

  it('decays K_L to 12 once 200+ attempts are logged on the topic', () => {
    const result = updateElo({ learnerElo: 1200, itemElo: 1200, actual: 1, topicAttemptsCountSoFar: 200 })
    expect(result.learnerElo).toBeCloseTo(1200 + 12 * 0.5)
  })

  it('moves a guessed-correct answer (actual=0.4) less than a confident correct answer', () => {
    const guessed = updateElo({ learnerElo: 1200, itemElo: 1200, actual: 0.4, topicAttemptsCountSoFar: 0 })
    const confident = updateElo({ learnerElo: 1200, itemElo: 1200, actual: 1, topicAttemptsCountSoFar: 0 })
    expect(guessed.learnerElo - 1200).toBeLessThan(confident.learnerElo - 1200)
  })
})
