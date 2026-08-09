import { describe, expect, it } from 'vitest'
import { migrateAttempt } from './migrations'
import type { Attempt } from '@/types/state'

function makeAttempt(schemaVersion: 1): Attempt {
  return {
    schemaVersion,
    id: 'attempt-1',
    questionId: 'qa.arith.percentages-0001',
    microTopicIds: ['qa.arith.percentages'],
    startedAt: 1000,
    submittedAt: 1030,
    timeSpentSec: 30,
    given: 'B',
    correct: true,
    mode: 'drill',
    markedForReview: false,
  }
}

describe('migrateAttempt', () => {
  it('returns a record already at the current schemaVersion unchanged', () => {
    const attempt = makeAttempt(1)
    expect(migrateAttempt(attempt)).toEqual(attempt)
  })

  it('throws for a schemaVersion below current with no registered migration step', () => {
    // Simulates a record persisted under a hypothetical older schemaVersion;
    // no v0->v1 step is registered (schemaVersion 1 is the only version
    // that has ever shipped), so this must fail loudly rather than
    // silently return a mis-shaped record.
    const legacy = { ...makeAttempt(1), schemaVersion: 0 } as unknown as Attempt
    expect(() => migrateAttempt(legacy)).toThrow(/No migration registered from schemaVersion 0 to 1/)
  })
})
