import { describe, expect, it } from 'vitest'
import type { MicroTopic } from '@/types/content'
import type { PlanDay } from '@/types/state'
import { redistributeMissedDay } from './missedDay'

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

function emptyDay(date: string): PlanDay {
  return { schemaVersion: 1, date, items: [], status: 'pending' }
}

describe('redistributeMissedDay', () => {
  it('spreads undone items across the next days', () => {
    const missed: PlanDay = {
      schemaVersion: 1,
      date: '2026-08-09',
      items: [
        { microTopicId: 'a', kind: 'learn', done: false },
        { microTopicId: 'a', kind: 'drill', done: false },
      ],
      status: 'missed',
    }
    const nextDays = [emptyDay('2026-08-10'), emptyDay('2026-08-11'), emptyDay('2026-08-12')]
    const topicsById = new Map([['a', topic({ id: 'a' })]])

    const { updatedDays, droppedItems } = redistributeMissedDay(missed, nextDays, topicsById, new Map(), 4)

    const totalPlaced = updatedDays.reduce((sum, d) => sum + d.items.length, 0)
    expect(totalPlaced).toBe(2)
    expect(droppedItems).toHaveLength(0)
  })

  it('ignores already-done items from the missed day', () => {
    const missed: PlanDay = {
      schemaVersion: 1,
      date: '2026-08-09',
      items: [
        { microTopicId: 'a', kind: 'learn', done: true },
        { microTopicId: 'a', kind: 'drill', done: false },
      ],
      status: 'missed',
    }
    const nextDays = [emptyDay('2026-08-10')]
    const { updatedDays } = redistributeMissedDay(missed, nextDays, new Map([['a', topic({ id: 'a' })]]), new Map(), 4)
    expect(updatedDays[0].items).toHaveLength(1)
    expect(updatedDays[0].items[0].kind).toBe('drill')
  })

  it('drops the lowest-ROI item(s) when capacity is exceeded, keeping higher-ROI ones', () => {
    const lowRoiTopic = topic({ id: 'low', roiScore: 1, catFrequency: 'rare' })
    const highRoiTopic = topic({ id: 'high', roiScore: 5, catFrequency: 'high' })
    const missed: PlanDay = {
      schemaVersion: 1,
      date: '2026-08-09',
      items: [
        { microTopicId: 'low', kind: 'learn', done: false },
        { microTopicId: 'high', kind: 'learn', done: false },
      ],
      status: 'missed',
    }
    // capacityPerDay = max(1, floor(baseline * 0.25)); with baseline=1 and one day of zero
    // pre-existing capacity, only one item can fit.
    const nextDays = [emptyDay('2026-08-10')]
    const topicsById = new Map([
      ['low', lowRoiTopic],
      ['high', highRoiTopic],
    ])

    const { updatedDays, droppedItems } = redistributeMissedDay(missed, nextDays, topicsById, new Map(), 1)

    expect(updatedDays[0].items).toEqual([{ microTopicId: 'high', kind: 'learn', done: false }])
    expect(droppedItems).toEqual([{ microTopicId: 'low', kind: 'learn', done: false }])
  })
})
