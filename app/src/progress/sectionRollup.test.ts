import { describe, expect, it } from 'vitest'
import { countByStatus, rollUpBySection, summariseCoverage } from './sectionRollup'
import type { TopicProgressRow } from './topicProgress'
import type { Section } from '@/types/state'

function row(overrides: Partial<TopicProgressRow> = {}): TopicProgressRow {
  return {
    microTopicId: 't1',
    name: 'Topic',
    section: 'QA' as Section,
    roiScore: 3,
    status: 'untouched',
    attempts: 0,
    correct: 0,
    accuracyPct: null,
    medianTimeSec: null,
    targetSecPerQuestion: 60,
    paceRatio: null,
    lastAttemptAt: null,
    ...overrides,
  }
}

describe('rollUpBySection', () => {
  it('aggregates attempts and accuracy per section', () => {
    const rows = [
      row({ section: 'QA', attempts: 10, correct: 7, status: 'practising' }),
      row({ section: 'QA', attempts: 10, correct: 3, status: 'mastered' }),
      row({ section: 'VARC', attempts: 4, correct: 1, status: 'learning' }),
      row({ section: 'DILR' }),
    ]
    const [varc, dilr, qa] = rollUpBySection(rows)

    expect(qa.attempts).toBe(20)
    expect(qa.correct).toBe(10)
    expect(qa.accuracyPct).toBe(50)
    expect(qa.started).toBe(2)
    expect(qa.mastered).toBe(1)

    expect(varc.accuracyPct).toBe(25)
    expect(varc.started).toBe(1)

    // A section with topics but no attempts must report null, not 0% or NaN.
    expect(dilr.topics).toBe(1)
    expect(dilr.attempts).toBe(0)
    expect(dilr.accuracyPct).toBeNull()
  })

  it('always returns all three sections even when the syllabus is empty', () => {
    const rollups = rollUpBySection([])
    expect(rollups.map((r) => r.section)).toEqual(['VARC', 'DILR', 'QA'])
    expect(rollups.every((r) => r.topics === 0 && r.accuracyPct === null)).toBe(true)
  })
})

describe('summariseCoverage', () => {
  it('computes started/mastered shares of the syllabus', () => {
    const rows = [
      row({ attempts: 5, correct: 4, status: 'mastered' }),
      row({ attempts: 5, correct: 1, status: 'practising' }),
      row({ status: 'untouched' }),
      row({ status: 'untouched' }),
    ]
    const summary = summariseCoverage(rows)

    expect(summary.totalTopics).toBe(4)
    expect(summary.started).toBe(2)
    expect(summary.untouched).toBe(2)
    expect(summary.mastered).toBe(1)
    expect(summary.startedPct).toBe(50)
    expect(summary.masteredPct).toBe(25)
    expect(summary.totalAttempts).toBe(10)
    expect(summary.overallAccuracyPct).toBe(50)
  })

  it('reports zeros and a null accuracy for a brand-new learner', () => {
    const summary = summariseCoverage([row(), row()])
    expect(summary.started).toBe(0)
    expect(summary.startedPct).toBe(0)
    expect(summary.masteredPct).toBe(0)
    expect(summary.overallAccuracyPct).toBeNull()
  })

  it('does not divide by zero on an empty syllabus', () => {
    const summary = summariseCoverage([])
    expect(summary.startedPct).toBe(0)
    expect(summary.masteredPct).toBe(0)
    expect(summary.overallAccuracyPct).toBeNull()
    expect(Number.isNaN(summary.startedPct)).toBe(false)
  })
})

describe('countByStatus', () => {
  it('counts every rung including the ones with no topics', () => {
    const counts = countByStatus([
      row({ status: 'mastered' }),
      row({ status: 'mastered' }),
      row({ status: 'decaying' }),
      row({ status: 'untouched' }),
    ])
    expect(counts.mastered).toBe(2)
    expect(counts.decaying).toBe(1)
    expect(counts.untouched).toBe(1)
    expect(counts.learning).toBe(0)
    expect(counts.locked).toBe(0)
  })
})
