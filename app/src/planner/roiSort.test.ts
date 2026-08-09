import { describe, expect, it } from 'vitest'
import type { MicroTopic } from '@/types/content'
import type { MasteryState } from '@/types/state'
import { currentMasteryOf, roiPriorityOf, roiWeightedTopoSort } from './roiSort'

function topic(overrides: Partial<MicroTopic> & Pick<MicroTopic, 'id'>): MicroTopic {
  return {
    name: overrides.id,
    section: 'QA',
    topicId: 'qa.test',
    prerequisites: [],
    catFrequency: 'medium',
    roiScore: 3,
    estLearnMinutes: 20,
    targetSecPerQuestion: 90,
    ...overrides,
  }
}

function mastery(status: MasteryState['status']): MasteryState {
  return {
    schemaVersion: 1,
    microTopicId: 'x',
    status,
    learnerElo: 1200,
    lastNCorrect: [],
    medianTimeSec: 0,
    hardTierCleared: false,
    attemptsCount: 0,
    stability: 0,
    difficulty: 0,
  }
}

describe('currentMasteryOf', () => {
  it('is 0 with no mastery state (untouched topic)', () => {
    expect(currentMasteryOf(undefined)).toBe(0)
  })
  it('is 1 when mastered', () => {
    expect(currentMasteryOf(mastery('mastered'))).toBe(1)
  })
  it('is between 0 and 1 for in-progress states', () => {
    const m = currentMasteryOf(mastery('practising'))
    expect(m).toBeGreaterThan(0)
    expect(m).toBeLessThan(1)
  })
})

describe('roiPriorityOf', () => {
  it('is 0 for a mastered topic regardless of roiScore', () => {
    const t = topic({ id: 'a', roiScore: 5, catFrequency: 'high' })
    expect(roiPriorityOf(t, mastery('mastered'))).toBe(0)
  })

  it('scores a high-roi, high-frequency, untouched topic above a low/low one', () => {
    const high = topic({ id: 'a', roiScore: 5, catFrequency: 'high' })
    const low = topic({ id: 'b', roiScore: 1, catFrequency: 'rare' })
    expect(roiPriorityOf(high, undefined)).toBeGreaterThan(roiPriorityOf(low, undefined))
  })

  it('drops priority as mastery increases, all else equal', () => {
    const t = topic({ id: 'a' })
    expect(roiPriorityOf(t, mastery('practising'))).toBeLessThan(roiPriorityOf(t, undefined))
  })
})

describe('roiWeightedTopoSort', () => {
  it('never schedules a topic before its prerequisite', () => {
    const topics = [
      topic({ id: 'basic', roiScore: 1, catFrequency: 'low' }),
      topic({ id: 'advanced', roiScore: 5, catFrequency: 'high', prerequisites: ['basic'] }),
    ]
    const order = roiWeightedTopoSort(topics, new Map())
    const basicIdx = order.findIndex((t) => t.id === 'basic')
    const advIdx = order.findIndex((t) => t.id === 'advanced')
    expect(basicIdx).toBeLessThan(advIdx)
  })

  it('orders unconstrained topics by descending ROI priority', () => {
    const topics = [
      topic({ id: 'low', roiScore: 1, catFrequency: 'rare' }),
      topic({ id: 'high', roiScore: 5, catFrequency: 'high' }),
      topic({ id: 'mid', roiScore: 3, catFrequency: 'medium' }),
    ]
    const order = roiWeightedTopoSort(topics, new Map()).map((t) => t.id)
    expect(order).toEqual(['high', 'mid', 'low'])
  })

  it('terminates even with a prerequisite cycle', () => {
    const topics = [
      topic({ id: 'a', prerequisites: ['b'] }),
      topic({ id: 'b', prerequisites: ['a'] }),
    ]
    const order = roiWeightedTopoSort(topics, new Map())
    expect(order).toHaveLength(2)
  })

  it('includes every topic exactly once', () => {
    const topics = Array.from({ length: 10 }, (_, i) => topic({ id: `t${i}`, roiScore: ((i % 5) + 1) as 1 | 2 | 3 | 4 | 5 }))
    const order = roiWeightedTopoSort(topics, new Map())
    expect(order).toHaveLength(10)
    expect(new Set(order.map((t) => t.id)).size).toBe(10)
  })
})
