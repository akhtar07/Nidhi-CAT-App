import { describe, expect, it } from 'vitest'
import { selectDrillQueue, type CandidateItem } from './selectItems'

const LEARNER_ELO = 1200

function items(prefix: string, elo: number, count: number): CandidateItem[] {
  return Array.from({ length: count }, (_, i) => ({ questionId: `${prefix}-${i}`, itemElo: elo }))
}

// A deterministic PRNG (mulberry32) so band-membership assertions aren't order-flaky.
function seededRandom(seed: number): () => number {
  let a = seed
  return () => {
    a |= 0
    a = (a + 0x6d2b79f5) | 0
    let t = Math.imul(a ^ (a >>> 15), 1 | a)
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296
  }
}

function fullPools() {
  return {
    productive: items('p', 1250, 20), // within [1150, 1300]
    stretch: items('s', 1400, 20), // within [1350, 1500]
    fluency: items('f', 900, 20), // <= 1000
    interleave: items('i', 1200, 20),
  }
}

describe('selectDrillQueue', () => {
  it('returns a queue of the requested size with the SPEC.md §8.3 band split (60/20/10/10)', () => {
    const pools = fullPools()
    const currentTopicItems = [...pools.productive, ...pools.stretch, ...pools.fluency]
    const queue = selectDrillQueue({
      learnerElo: LEARNER_ELO,
      currentTopicItems,
      interleaveItems: pools.interleave,
      recentlyCorrectIds: new Set(),
      random: seededRandom(1),
    })

    expect(queue).toHaveLength(10)
    const byPrefix = (p: string) => queue.filter((q) => q.questionId.startsWith(p)).length
    expect(byPrefix('p')).toBe(6)
    expect(byPrefix('s')).toBe(2)
    expect(byPrefix('f')).toBe(1)
    expect(byPrefix('i')).toBe(1)
  })

  it('never includes a recently-correct item', () => {
    const pools = fullPools()
    const currentTopicItems = [...pools.productive, ...pools.stretch, ...pools.fluency]
    const recentlyCorrectIds = new Set(currentTopicItems.slice(0, 5).map((i) => i.questionId))
    const queue = selectDrillQueue({
      learnerElo: LEARNER_ELO,
      currentTopicItems,
      interleaveItems: pools.interleave,
      recentlyCorrectIds,
      random: seededRandom(2),
    })
    for (const q of queue) {
      expect(recentlyCorrectIds.has(q.questionId)).toBe(false)
    }
  })

  it('never repeats an item within the queue', () => {
    const pools = fullPools()
    const currentTopicItems = [...pools.productive, ...pools.stretch, ...pools.fluency]
    const queue = selectDrillQueue({
      learnerElo: LEARNER_ELO,
      currentTopicItems,
      interleaveItems: pools.interleave,
      recentlyCorrectIds: new Set(),
      random: seededRandom(3),
    })
    expect(new Set(queue.map((q) => q.questionId)).size).toBe(queue.length)
  })

  it('backfills from the general pool when a band is empty, rather than truncating the queue', () => {
    // No stretch-band items at all — a thin/young topic.
    const pools = fullPools()
    const currentTopicItems = [...pools.productive, ...pools.fluency] // no 's' items
    const queue = selectDrillQueue({
      learnerElo: LEARNER_ELO,
      currentTopicItems,
      interleaveItems: pools.interleave,
      recentlyCorrectIds: new Set(),
      random: seededRandom(4),
    })
    expect(queue).toHaveLength(10)
    expect(queue.some((q) => q.questionId.startsWith('s'))).toBe(false)
  })

  it('returns fewer than size items rather than crashing when the whole bank is thin', () => {
    const queue = selectDrillQueue({
      learnerElo: LEARNER_ELO,
      currentTopicItems: items('p', 1200, 3),
      interleaveItems: [],
      recentlyCorrectIds: new Set(),
      random: seededRandom(5),
    })
    expect(queue.length).toBe(3)
  })

  it('draws interleave items only from the interleave pool, not the current topic', () => {
    const pools = fullPools()
    const currentTopicItems = [...pools.productive, ...pools.stretch, ...pools.fluency]
    const queue = selectDrillQueue({
      learnerElo: LEARNER_ELO,
      currentTopicItems,
      interleaveItems: pools.interleave,
      recentlyCorrectIds: new Set(),
      random: seededRandom(6),
    })
    const interleaved = queue.filter((q) => q.questionId.startsWith('i'))
    expect(interleaved.length).toBeGreaterThan(0)
    for (const q of interleaved) {
      expect(pools.interleave.some((i) => i.questionId === q.questionId)).toBe(true)
    }
  })
})
