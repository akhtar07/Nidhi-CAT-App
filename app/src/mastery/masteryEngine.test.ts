import { describe, expect, it } from 'vitest'
import { DexieAdapter } from '@/storage/dexie/DexieAdapter'
import type { MicroTopic, Question } from '@/types/content'
import type { Attempt } from '@/types/state'
import { recordAttemptForMastery } from './masteryEngine'

let dbCounter = 0
function freshAdapter(): DexieAdapter {
  dbCounter += 1
  return new DexieAdapter(`ascent-mastery-test-${dbCounter}`)
}

const topic: MicroTopic = {
  id: 'qa.arith.percentages',
  name: 'Percentages',
  section: 'QA',
  topicId: 'qa.arith',
  catFrequency: 'high',
  roiScore: 5,
  estLearnMinutes: 20,
  targetSecPerQuestion: 60,
}

function makeQuestion(id: string, difficulty: Question['difficulty'], eloRating = 1200): Question {
  return {
    id,
    microTopicIds: [topic.id],
    section: 'QA',
    format: 'tita',
    stemMarkdown: 'stub',
    difficulty,
    eloRating,
    solutionMarkdown: 'stub',
    targetSeconds: 60,
    source: 'generated',
    verification: { method: 'sympy_verified', verifiedAt: new Date().toISOString() },
  }
}

const topicQuestions: Question[] = [
  makeQuestion('q-easy-1', 'easy'),
  makeQuestion('q-easy-2', 'easy'),
  makeQuestion('q-hard-1', 'hard'),
  makeQuestion('q-hard-2', 'hard'),
]

function makeAttempt(overrides: Partial<Attempt> & { id: string; submittedAt: number }): Attempt {
  return {
    schemaVersion: 1,
    questionId: 'q-easy-1',
    microTopicIds: [topic.id],
    startedAt: overrides.submittedAt - 30_000,
    timeSpentSec: 30,
    given: 'A',
    correct: true,
    confidence: 'sure',
    mode: 'drill',
    markedForReview: false,
    ...overrides,
  }
}

describe('recordAttemptForMastery', () => {
  it('updates learnerElo and persists a per-question itemElo', async () => {
    const storageAdapter = freshAdapter()
    const attempt = makeAttempt({ id: 'a1', submittedAt: 1000, questionId: 'q-easy-1' })
    await storageAdapter.addAttempt(attempt)

    const state = await recordAttemptForMastery({
      attempt,
      question: topicQuestions[0],
      topic,
      topicQuestions,
      storageAdapter,
    })

    expect(state.learnerElo).toBeGreaterThan(1200)
    expect(state.attemptsCount).toBe(1)
    expect(state.status).toBe('learning')
    expect(await storageAdapter.getItemElo('q-easy-1')).not.toBeUndefined()
  })

  it('reaches "practising (pending retention)" after a solid run, then "mastered" after the retention gap', async () => {
    const storageAdapter = freshAdapter()
    const DAY = 24 * 60 * 60 * 1000
    let state
    // 10 solid attempts, 2 of them hard-tier, all fast and confidently correct.
    for (let i = 0; i < 10; i++) {
      const questionId = i < 2 ? `q-hard-${i + 1}` : 'q-easy-1'
      const question = topicQuestions.find((q) => q.id === questionId)!
      const attempt = makeAttempt({ id: `solid-${i}`, submittedAt: i * 1000, questionId, timeSpentSec: 30 })
      await storageAdapter.addAttempt(attempt)
      state = await recordAttemptForMastery({ attempt, question, topic, topicQuestions, storageAdapter })
    }
    // 2 more to clear the 12-lifetime-attempt floor.
    for (let i = 10; i < 12; i++) {
      const attempt = makeAttempt({ id: `solid-${i}`, submittedAt: i * 1000, questionId: 'q-easy-1', timeSpentSec: 30 })
      await storageAdapter.addAttempt(attempt)
      state = await recordAttemptForMastery({ attempt, question: topicQuestions[0], topic, topicQuestions, storageAdapter })
    }

    expect(state!.status).toBe('practising')
    expect(state!.criteria123FirstMetAt).toBeDefined()
    expect(state!.hardTierCleared).toBe(true)

    // A correct attempt >=3 days later should complete retention -> mastered.
    const retentionAttempt = makeAttempt({
      id: 'retention',
      submittedAt: state!.criteria123FirstMetAt! + 3 * DAY + 1,
      questionId: 'q-easy-1',
      timeSpentSec: 30,
    })
    await storageAdapter.addAttempt(retentionAttempt)
    const finalState = await recordAttemptForMastery({
      attempt: retentionAttempt,
      question: topicQuestions[0],
      topic,
      topicQuestions,
      storageAdapter,
    })

    expect(finalState.status).toBe('mastered')
    expect(finalState.masteredAt).toBe(retentionAttempt.submittedAt)
  })

  it('sets antiFrustrationTriggered after 30 attempts stuck below threshold', async () => {
    const storageAdapter = freshAdapter()
    let state
    for (let i = 0; i < 30; i++) {
      const attempt = makeAttempt({
        id: `stuck-${i}`,
        submittedAt: i * 1000,
        questionId: 'q-easy-1',
        correct: i % 10 < 6, // 60% < 75% threshold, never masters
      })
      await storageAdapter.addAttempt(attempt)
      state = await recordAttemptForMastery({ attempt, question: topicQuestions[0], topic, topicQuestions, storageAdapter })
    }
    expect(state!.antiFrustrationTriggered).toBe(true)
    expect(state!.status).toBe('practising')
  })
})
