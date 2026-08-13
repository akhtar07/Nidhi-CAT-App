import { describe, expect, it } from 'vitest'
import { buildTopicProgress, rankWeakestTopics } from './topicProgress'
import type { MicroTopic } from '@/types/content'
import type { Attempt, MasteryState } from '@/types/state'

function topic(overrides: Partial<MicroTopic> = {}): MicroTopic {
  return {
    id: 't1',
    name: 'Percentages',
    section: 'QA',
    topicId: 'qa.arith',
    catFrequency: 'high',
    roiScore: 5,
    estLearnMinutes: 30,
    targetSecPerQuestion: 60,
    ...overrides,
  }
}

function attempt(overrides: Partial<Attempt> = {}): Attempt {
  return {
    schemaVersion: 1,
    id: 'a1',
    questionId: 'q1',
    microTopicIds: ['t1'],
    startedAt: 0,
    submittedAt: 1000,
    timeSpentSec: 60,
    given: 'A',
    correct: true,
    mode: 'drill',
    markedForReview: false,
    ...overrides,
  }
}

function mastery(overrides: Partial<MasteryState> = {}): MasteryState {
  return {
    schemaVersion: 1,
    microTopicId: 't1',
    status: 'practising',
    learnerElo: 1200,
    lastNCorrect: [],
    medianTimeSec: 60,
    hardTierCleared: false,
    attemptsCount: 0,
    stability: 1,
    difficulty: 5,
    ...overrides,
  }
}

describe('buildTopicProgress', () => {
  it('computes accuracy, median time and pace against the topic target', () => {
    const attempts = [
      attempt({ id: 'a1', correct: true, timeSpentSec: 30 }),
      attempt({ id: 'a2', correct: true, timeSpentSec: 90 }),
      attempt({ id: 'a3', correct: false, timeSpentSec: 60 }),
      attempt({ id: 'a4', correct: false, timeSpentSec: 120 }),
    ]
    const [row] = buildTopicProgress([topic()], attempts, [mastery()])

    expect(row.attempts).toBe(4)
    expect(row.correct).toBe(2)
    expect(row.accuracyPct).toBe(50)
    // sorted times 30/60/90/120 -> median is (60+90)/2 = 75
    expect(row.medianTimeSec).toBe(75)
    // 75 / 60 target = 1.25
    expect(row.paceRatio).toBe(1.25)
    expect(row.status).toBe('practising')
  })

  it('reports nulls, never NaN, for a topic with no attempts', () => {
    const [row] = buildTopicProgress([topic()], [], [])

    expect(row.attempts).toBe(0)
    expect(row.accuracyPct).toBeNull()
    expect(row.medianTimeSec).toBeNull()
    expect(row.paceRatio).toBeNull()
    expect(row.lastAttemptAt).toBeNull()
    expect(row.status).toBe('untouched')
  })

  it('handles a single attempt without dividing by zero', () => {
    const [row] = buildTopicProgress([topic()], [attempt({ correct: false, timeSpentSec: 45 })], [])
    expect(row.accuracyPct).toBe(0)
    expect(row.medianTimeSec).toBe(45)
    expect(row.paceRatio).toBe(0.75)
  })

  it('keeps untouched topics in the output so the mastery map can show gaps', () => {
    const rows = buildTopicProgress([topic({ id: 't1' }), topic({ id: 't2', name: 'Ratios' })], [attempt()], [])
    expect(rows).toHaveLength(2)
    expect(rows[1].attempts).toBe(0)
  })

  it('counts an attempt towards every micro-topic it is tagged with', () => {
    const rows = buildTopicProgress(
      [topic({ id: 't1' }), topic({ id: 't2' })],
      [attempt({ microTopicIds: ['t1', 't2'] })],
      [],
    )
    expect(rows[0].attempts).toBe(1)
    expect(rows[1].attempts).toBe(1)
  })

  it("treats a stored 'available' state with attempts as learning, and without as untouched", () => {
    const [withAttempts] = buildTopicProgress([topic()], [attempt()], [mastery({ status: 'available' })])
    expect(withAttempts.status).toBe('learning')

    const [none] = buildTopicProgress([topic()], [], [mastery({ status: 'available' })])
    expect(none.status).toBe('untouched')
  })

  it('passes through locked and decaying statuses unchanged', () => {
    const [locked] = buildTopicProgress([topic()], [], [mastery({ status: 'locked' })])
    expect(locked.status).toBe('locked')

    const [decaying] = buildTopicProgress([topic()], [attempt()], [mastery({ status: 'decaying' })])
    expect(decaying.status).toBe('decaying')
  })

  it('takes the most recent submittedAt as lastAttemptAt', () => {
    const [row] = buildTopicProgress(
      [topic()],
      [attempt({ id: 'a1', submittedAt: 500 }), attempt({ id: 'a2', submittedAt: 9000 })],
      [],
    )
    expect(row.lastAttemptAt).toBe(9000)
  })

  it('guards paceRatio when a topic has a zero target time', () => {
    const [row] = buildTopicProgress([topic({ targetSecPerQuestion: 0 })], [attempt()], [])
    expect(row.paceRatio).toBeNull()
  })
})

describe('rankWeakestTopics', () => {
  it('ranks by accuracy ascending, breaking ties on ROI', () => {
    const rows = buildTopicProgress(
      [
        topic({ id: 'lowAcc', name: 'Low', roiScore: 1 }),
        topic({ id: 'midHighRoi', name: 'MidHigh', roiScore: 5 }),
        topic({ id: 'midLowRoi', name: 'MidLow', roiScore: 2 }),
      ],
      [
        // lowAcc: 1/4 = 25%
        ...[true, false, false, false].map((c, i) =>
          attempt({ id: `l${i}`, microTopicIds: ['lowAcc'], correct: c }),
        ),
        // midHighRoi: 2/4 = 50%
        ...[true, true, false, false].map((c, i) =>
          attempt({ id: `h${i}`, microTopicIds: ['midHighRoi'], correct: c }),
        ),
        // midLowRoi: 2/4 = 50%
        ...[true, true, false, false].map((c, i) =>
          attempt({ id: `m${i}`, microTopicIds: ['midLowRoi'], correct: c }),
        ),
      ],
      [],
    )

    const ranked = rankWeakestTopics(rows)
    expect(ranked.map((r) => r.microTopicId)).toEqual(['lowAcc', 'midHighRoi', 'midLowRoi'])
  })

  it('excludes topics below the attempt threshold and mastered topics', () => {
    const rows = buildTopicProgress(
      [topic({ id: 'thin' }), topic({ id: 'done' })],
      [
        attempt({ id: 'x', microTopicIds: ['thin'], correct: false }),
        ...[false, false, false, false].map((c, i) =>
          attempt({ id: `d${i}`, microTopicIds: ['done'], correct: c }),
        ),
      ],
      [mastery({ microTopicId: 'done', status: 'mastered' })],
    )

    expect(rankWeakestTopics(rows)).toEqual([])
  })

  it('returns an empty list when nothing has been attempted', () => {
    expect(rankWeakestTopics(buildTopicProgress([topic()], [], []))).toEqual([])
  })

  it('respects the limit', () => {
    const topics = Array.from({ length: 12 }, (_, i) => topic({ id: `t${i}` }))
    const attempts = topics.flatMap((t, ti) =>
      Array.from({ length: 4 }, (_, i) => attempt({ id: `${ti}-${i}`, microTopicIds: [t.id], correct: false })),
    )
    expect(rankWeakestTopics(buildTopicProgress(topics, attempts, []), { limit: 3 })).toHaveLength(3)
  })
})
