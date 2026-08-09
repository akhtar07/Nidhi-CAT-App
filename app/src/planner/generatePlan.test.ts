import { describe, expect, it } from 'vitest'
import type { MicroTopic } from '@/types/content'
import { addDays, dayOfWeek } from './dateUtils'
import { generatePlan, MOCK_SENTINEL, REVIEW_SENTINEL } from './generatePlan'

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

// A Sunday (SPEC.md §2's exam date is also a Sunday; matches this repo's currentDate too).
const TODAY = '2026-08-09'

describe('generatePlan', () => {
  it('schedules a mock on Sundays from week 3 onward, and nothing else that day', () => {
    const examDate = addDays(TODAY, 5 * 7) // 5 weeks out
    const result = generatePlan({
      topics: [topic({ id: 'a' })],
      masteryByTopicId: new Map(),
      today: TODAY,
      examDate,
      dailyMinutes: 90,
    })

    const week0Sunday = result.days.find((d) => d.date === TODAY)!
    expect(week0Sunday.items.some((i) => i.kind === 'mock')).toBe(false)

    const week3Sunday = result.days.find((d) => d.date === addDays(TODAY, 3 * 7))!
    expect(dayOfWeek(week3Sunday.date)).toBe(0)
    expect(week3Sunday.items).toEqual([{ microTopicId: MOCK_SENTINEL, kind: 'mock', done: false }])
  })

  it('gives every non-mock day a review item', () => {
    const examDate = addDays(TODAY, 10)
    const result = generatePlan({
      topics: [topic({ id: 'a' })],
      masteryByTopicId: new Map(),
      today: TODAY,
      examDate,
      dailyMinutes: 90,
    })
    for (const day of result.days) {
      if (day.items.some((i) => i.kind === 'mock')) continue
      expect(day.items.some((i) => i.microTopicId === REVIEW_SENTINEL)).toBe(true)
    }
  })

  it('schedules no new learn/drill items in the last 3 weeks before the exam', () => {
    const examDate = addDays(TODAY, 8 * 7)
    const manyTopics = Array.from({ length: 40 }, (_, i) => topic({ id: `t${i}`, roiScore: 5, catFrequency: 'high' }))
    const result = generatePlan({
      topics: manyTopics,
      masteryByTopicId: new Map(),
      today: TODAY,
      examDate,
      dailyMinutes: 90,
    })

    const revisionCutoff = addDays(examDate, -(3 * 7 - 1))
    for (const day of result.days) {
      if (day.date < revisionCutoff) continue
      expect(day.items.some((i) => i.kind === 'learn' || i.kind === 'drill')).toBe(false)
    }
  })

  it('never schedules a topic before its prerequisite', () => {
    const examDate = addDays(TODAY, 6 * 7)
    const topics = [
      topic({ id: 'basic', roiScore: 1, catFrequency: 'low' }),
      topic({ id: 'advanced', roiScore: 5, catFrequency: 'high', prerequisites: ['basic'] }),
    ]
    const result = generatePlan({
      topics,
      masteryByTopicId: new Map(),
      today: TODAY,
      examDate,
      dailyMinutes: 60,
    })

    const firstDayWith = (id: string) =>
      result.days.findIndex((d) => d.items.some((i) => i.microTopicId === id && i.kind === 'learn'))
    const basicDay = firstDayWith('basic')
    const advDay = firstDayWith('advanced')
    expect(basicDay).toBeGreaterThanOrEqual(0)
    expect(advDay).toBeGreaterThanOrEqual(0)
    expect(basicDay).toBeLessThanOrEqual(advDay)
  })

  it('drops topics that do not fit before the exam and reports them', () => {
    const examDate = addDays(TODAY, 3) // barely any time
    const manyTopics = Array.from({ length: 50 }, (_, i) => topic({ id: `t${i}` }))
    const result = generatePlan({
      topics: manyTopics,
      masteryByTopicId: new Map(),
      today: TODAY,
      examDate,
      dailyMinutes: 30,
    })
    expect(result.droppedTopics.length).toBeGreaterThan(0)
    expect(result.scheduledTopicIds.size + result.droppedTopics.length).toBe(manyTopics.length)
  })

  it('excludes already-mastered topics from scheduling', () => {
    const examDate = addDays(TODAY, 6 * 7)
    const topics = [topic({ id: 'done' }), topic({ id: 'todo' })]
    const masteryByTopicId = new Map([
      [
        'done',
        {
          schemaVersion: 1 as const,
          microTopicId: 'done',
          status: 'mastered' as const,
          learnerElo: 1200,
          lastNCorrect: [],
          medianTimeSec: 0,
          hardTierCleared: true,
          attemptsCount: 20,
          stability: 0,
          difficulty: 0,
        },
      ],
    ])
    const result = generatePlan({ topics, masteryByTopicId, today: TODAY, examDate, dailyMinutes: 60 })
    expect(result.scheduledTopicIds.has('done')).toBe(false)
    expect(result.scheduledTopicIds.has('todo')).toBe(true)
  })
})
