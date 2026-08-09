import { describe, expect, it } from 'vitest'
import type { MockQuestionState } from '@/types/state'
import { derivePaletteStatus } from './paletteStatus'

function state(overrides: Partial<MockQuestionState>): MockQuestionState {
  return { given: null, markedForReview: false, visitCount: 1, dwellSec: 0, ...overrides }
}

describe('derivePaletteStatus', () => {
  it('is not_visited when there is no state at all', () => {
    expect(derivePaletteStatus(undefined)).toBe('not_visited')
  })

  it('is not_visited when visitCount is 0', () => {
    expect(derivePaletteStatus(state({ visitCount: 0 }))).toBe('not_visited')
  })

  it('is not_answered when visited but no answer given', () => {
    expect(derivePaletteStatus(state({ given: null }))).toBe('not_answered')
  })

  it('is answered when a value is given and not marked', () => {
    expect(derivePaletteStatus(state({ given: 'A' }))).toBe('answered')
  })

  it('is marked when marked for review with no answer', () => {
    expect(derivePaletteStatus(state({ given: null, markedForReview: true }))).toBe('marked')
  })

  it('is answered_marked when both answered and marked', () => {
    expect(derivePaletteStatus(state({ given: 'A', markedForReview: true }))).toBe('answered_marked')
  })

  it('treats an empty string given as unanswered', () => {
    expect(derivePaletteStatus(state({ given: '' }))).toBe('not_answered')
  })
})
