import { describe, expect, it } from 'vitest'
import { gradeReview, initFsrsState, isDue, Rating } from './fsrsAdapter'

const NOW = new Date('2026-08-10T00:00:00Z').getTime()

describe('initFsrsState', () => {
  it('produces a state due immediately (new card)', () => {
    const state = initFsrsState(NOW)
    expect(isDue(state, NOW)).toBe(true)
  })
})

describe('isDue', () => {
  it('is due when there is no prior state at all', () => {
    expect(isDue(undefined, NOW)).toBe(true)
  })
  it('is not due when nextReviewAt is in the future', () => {
    expect(isDue({ stability: 5, difficulty: 5, nextReviewAt: NOW + 100000 }, NOW)).toBe(false)
  })
  it('is due once nextReviewAt has passed', () => {
    expect(isDue({ stability: 5, difficulty: 5, nextReviewAt: NOW - 1 }, NOW)).toBe(true)
  })
})

describe('gradeReview', () => {
  it('schedules a much longer interval for Easy than for Again', () => {
    const again = gradeReview(undefined, Rating.Again, NOW)
    const easy = gradeReview(undefined, Rating.Easy, NOW)
    expect(easy.nextReviewAt).toBeGreaterThan(again.nextReviewAt)
  })

  it('increases stability on repeated Good grades', () => {
    let state = gradeReview(undefined, Rating.Good, NOW)
    const firstStability = state.stability
    // simulate reviewing again well after the scheduled due date
    state = gradeReview(state, Rating.Good, state.nextReviewAt + 24 * 60 * 60 * 1000)
    expect(state.stability).toBeGreaterThan(firstStability)
  })

  it('drops stability sharply on Again after a Good streak (a lapse)', () => {
    let state = gradeReview(undefined, Rating.Good, NOW)
    state = gradeReview(state, Rating.Good, state.nextReviewAt)
    const beforeLapse = state.stability
    state = gradeReview(state, Rating.Again, state.nextReviewAt)
    expect(state.stability).toBeLessThan(beforeLapse)
  })

  it('always returns a future nextReviewAt relative to the review time', () => {
    const reviewedAt = NOW
    const state = gradeReview(undefined, Rating.Good, reviewedAt)
    expect(state.nextReviewAt).toBeGreaterThan(reviewedAt)
  })
})
