import { describe, expect, it } from 'vitest'
import type { MicroTopic } from '@/types/content'
import { computeCoverageForecast } from './coverageForecast'
import type { GeneratePlanResult } from './generatePlan'

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

describe('computeCoverageForecast', () => {
  it('reports 100% coverage and no drops when everything is scheduled', () => {
    const topics = [topic({ id: 'a', roiScore: 4 }), topic({ id: 'b', roiScore: 5 })]
    const result: GeneratePlanResult = {
      days: [],
      scheduledTopicIds: new Set(['a', 'b']),
      droppedTopics: [],
    }
    const forecast = computeCoverageForecast(topics, result, '29 Nov')
    expect(forecast.coveragePct).toBe(100)
    expect(forecast.droppedTopics).toHaveLength(0)
    expect(forecast.message).toContain('On track')
  })

  it('computes partial coverage and names dropped high-roi topics honestly', () => {
    const covered = topic({ id: 'covered', roiScore: 5, name: 'Covered Topic' })
    const dropped = topic({ id: 'dropped', roiScore: 4, name: 'Dropped Topic', estLearnMinutes: 60 })
    const lowRoi = topic({ id: 'low', roiScore: 1 }) // below HIGH_ROI_THRESHOLD, shouldn't count toward the headline
    const result: GeneratePlanResult = {
      days: [],
      scheduledTopicIds: new Set(['covered']),
      droppedTopics: [dropped],
    }
    const forecast = computeCoverageForecast([covered, dropped, lowRoi], result, '29 Nov')
    expect(forecast.totalHighRoiTopics).toBe(2) // covered + dropped, not lowRoi
    expect(forecast.coveredHighRoiTopics).toBe(1)
    expect(forecast.coveragePct).toBe(50)
    expect(forecast.droppedTopics).toContain(dropped)
    expect(forecast.message).toContain('Dropped Topic')
    expect(forecast.droppedHoursEstimate).toBeGreaterThan(0)
  })
})
