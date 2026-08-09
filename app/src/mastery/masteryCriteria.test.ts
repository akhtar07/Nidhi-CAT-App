import { describe, expect, it } from 'vitest'
import { evaluateMastery, type AttemptForMastery } from './masteryCriteria'
import type { Attempt } from '@/types/state'

const TARGET = 60 // seconds; 1.25x threshold = 75s
const DAY = 24 * 60 * 60 * 1000

function attempt(overrides: Partial<AttemptForMastery> & { submittedAt: number }): AttemptForMastery {
  return {
    correct: true,
    confidence: 'sure' as Attempt['confidence'],
    timeSpentSec: 40,
    difficulty: 'medium',
    ...overrides,
  }
}

/** 12 solid attempts: fast, correct, confident, with 2 hard-tier correct — satisfies all of accuracy/speed/ceiling. */
function solidHistory(count = 12, startAt = 0): AttemptForMastery[] {
  return Array.from({ length: count }, (_, i) =>
    attempt({
      submittedAt: startAt + i * 1000,
      difficulty: i < 2 ? 'hard' : 'medium',
    }),
  )
}

describe('evaluateMastery — criteria123 baseline', () => {
  it('meets accuracy/speed/ceiling on a solid 12-attempt history', () => {
    const result = evaluateMastery({ attempts: solidHistory(), targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.accuracyOk).toBe(true)
    expect(result.speedOk).toBe(true)
    expect(result.ceilingOk).toBe(true)
    expect(result.criteria123Met).toBe(true)
  })

  it('stays "learning" under 8 attempts regardless of performance', () => {
    const result = evaluateMastery({ attempts: solidHistory(5), targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.status).toBe('learning')
  })

  it('requires 12 lifetime attempts even if the last 10 are all correct', () => {
    // 10 attempts total, all correct — would be 100% "accuracy" by a naive last-10 check.
    const result = evaluateMastery({ attempts: solidHistory(10), targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.accuracyOk).toBe(false)
  })
})

describe('evaluateMastery — lucky-guess handling (SPEC.md §8.5)', () => {
  it('does not let guess-heavy correct answers satisfy the accuracy criterion', () => {
    // 12 attempts, last 10 all "correct" at face value, but 6 of 10 are guesses.
    // Raw accuracy = 100%; discounted = (6*0.4 + 4*1)/10 = 0.64 < 0.75.
    const attempts = Array.from({ length: 12 }, (_, i) =>
      attempt({
        submittedAt: i * 1000,
        difficulty: i < 2 ? 'hard' : 'medium',
        confidence: i >= 2 && i < 8 ? 'guess' : 'sure',
      }),
    )
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.accuracyOk).toBe(false)
    expect(result.criteria123Met).toBe(false)
  })

  it('a handful of guesses among mostly confident answers still passes', () => {
    const attempts = Array.from({ length: 12 }, (_, i) =>
      attempt({
        submittedAt: i * 1000,
        difficulty: i < 2 ? 'hard' : 'medium',
        confidence: i === 2 ? 'guess' : 'sure',
      }),
    )
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.accuracyOk).toBe(true)
  })
})

describe('evaluateMastery — speed failure', () => {
  it('fails criteria123 when median time exceeds targetSecPerQuestion * 1.25', () => {
    const attempts = solidHistory().map((a) => ({ ...a, timeSpentSec: 90 })) // > 75s threshold
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.accuracyOk).toBe(true)
    expect(result.ceilingOk).toBe(true)
    expect(result.speedOk).toBe(false)
    expect(result.criteria123Met).toBe(false)
  })

  it('a correct-but-slow answer is a wrong answer for mastery purposes', () => {
    // Every answer correct, but consistently slow — SPEC.md §8.2: "a correct
    // answer that takes 4 minutes is a wrong answer in CAT."
    const attempts = solidHistory().map((a) => ({ ...a, timeSpentSec: 240 }))
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.criteria123Met).toBe(false)
  })
})

describe('evaluateMastery — hard-tier requirement (ceiling proof)', () => {
  it('fails criteria123 with zero hard/very_hard correct even at perfect easy/medium accuracy', () => {
    const attempts = Array.from({ length: 12 }, (_, i) => attempt({ submittedAt: i * 1000, difficulty: 'easy' }))
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.accuracyOk).toBe(true)
    expect(result.speedOk).toBe(true)
    expect(result.ceilingOk).toBe(false)
    expect(result.criteria123Met).toBe(false)
  })

  it('one hard-tier correct is not enough — needs at least 2', () => {
    const attempts = Array.from({ length: 12 }, (_, i) =>
      attempt({ submittedAt: i * 1000, difficulty: i === 0 ? 'very_hard' : 'easy' }),
    )
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.ceilingOk).toBe(false)
  })

  it('a hard/very_hard attempt answered incorrectly does not count toward the ceiling', () => {
    const attempts = Array.from({ length: 12 }, (_, i) =>
      attempt({ submittedAt: i * 1000, difficulty: i < 3 ? 'hard' : 'easy', correct: i !== 0 }),
    )
    // Only 2 of the 3 hard attempts are correct — still satisfies (>=2), sanity check the boundary itself:
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.ceilingOk).toBe(true)
  })
})

describe('evaluateMastery — retention gap (criterion 4)', () => {
  it('stays "practising" (pending retention) immediately after criteria123 are first met', () => {
    const attempts = solidHistory()
    const now = 11000
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now })
    expect(result.criteria123Met).toBe(true)
    expect(result.criteria123FirstMetAt).toBe(now)
    expect(result.retentionOk).toBe(false)
    expect(result.status).toBe('practising')
  })

  it('does not grant retention from a correct attempt less than 3 days after criteria123 was first met', () => {
    const firstMetAt = 0
    const attempts = [...solidHistory(12, 0), attempt({ submittedAt: DAY, correct: true })]
    const result = evaluateMastery({
      attempts,
      targetSecPerQuestion: TARGET,
      now: DAY,
      criteria123FirstMetAt: firstMetAt,
    })
    expect(result.retentionOk).toBe(false)
    expect(result.status).toBe('practising')
  })

  it('grants mastery from a correct attempt >=3 days after criteria123 was first met', () => {
    const firstMetAt = 0
    const attempts = [...solidHistory(12, 0), attempt({ submittedAt: 3 * DAY + 1, correct: true })]
    const result = evaluateMastery({
      attempts,
      targetSecPerQuestion: TARGET,
      now: 3 * DAY + 1,
      criteria123FirstMetAt: firstMetAt,
    })
    expect(result.retentionOk).toBe(true)
    expect(result.status).toBe('mastered')
  })

  it('an incorrect attempt after the gap does not satisfy retention', () => {
    const firstMetAt = 0
    const attempts = [...solidHistory(12, 0), attempt({ submittedAt: 3 * DAY + 1, correct: false })]
    const result = evaluateMastery({
      attempts,
      targetSecPerQuestion: TARGET,
      now: 3 * DAY + 1,
      criteria123FirstMetAt: firstMetAt,
    })
    expect(result.retentionOk).toBe(false)
  })

  it('preserves an already-recorded criteria123FirstMetAt rather than resetting it', () => {
    const attempts = solidHistory()
    const originalFirstMetAt = -5000
    const result = evaluateMastery({
      attempts,
      targetSecPerQuestion: TARGET,
      now: 20000,
      criteria123FirstMetAt: originalFirstMetAt,
    })
    expect(result.criteria123FirstMetAt).toBe(originalFirstMetAt)
  })
})

describe('evaluateMastery — anti-frustration exit', () => {
  it('triggers after 30 attempts without meeting criteria123', () => {
    // Accuracy just under threshold forever: 7/10 correct, no guesses, so raw and
    // discounted accuracy match at 70% < 75%.
    const attempts = Array.from({ length: 30 }, (_, i) =>
      attempt({ submittedAt: i * 1000, correct: i % 10 < 7, difficulty: 'easy' }),
    )
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 40000 })
    expect(result.criteria123Met).toBe(false)
    expect(result.antiFrustrationTriggered).toBe(true)
  })

  it('does not trigger before 30 attempts just for not meeting criteria123 yet', () => {
    const attempts = Array.from({ length: 20 }, (_, i) =>
      attempt({ submittedAt: i * 1000, correct: i % 10 < 7, difficulty: 'easy' }),
    )
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 25000 })
    expect(result.antiFrustrationTriggered).toBe(false)
  })

  it('triggers early (at 15 attempts) when accuracy drops below 40%', () => {
    const attempts = Array.from({ length: 15 }, (_, i) =>
      attempt({ submittedAt: i * 1000, correct: i < 5, difficulty: 'easy' }), // 5/15 = 33%
    )
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 20000 })
    expect(result.antiFrustrationTriggered).toBe(true)
  })

  it('does not trigger the <40% rule before 15 attempts even at 0% accuracy', () => {
    const attempts = Array.from({ length: 10 }, (_, i) => attempt({ submittedAt: i * 1000, correct: false }))
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 15000 })
    expect(result.antiFrustrationTriggered).toBe(false)
  })

  it('does not trigger once criteria123 is actually met', () => {
    const attempts = solidHistory(30)
    const result = evaluateMastery({ attempts, targetSecPerQuestion: TARGET, now: 40000 })
    expect(result.criteria123Met).toBe(true)
    expect(result.antiFrustrationTriggered).toBe(false)
  })
})
