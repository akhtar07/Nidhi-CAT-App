import type { MicroTopic } from '@/types/content'
import type { MasteryState } from '@/types/state'

const FREQUENCY_WEIGHT: Record<MicroTopic['catFrequency'], number> = {
  high: 4,
  medium: 3,
  low: 2,
  rare: 1,
}

/** No continuous mastery scalar exists in MasteryState (SPEC.md §5.2's status is categorical) — this
 * maps the state machine (§8.1) onto [0, 1] for the ROI formula's (1 - currentMastery) term. A
 * `mastered` topic scores 0 further ROI; an untouched one scores full ROI. */
const STATUS_MASTERY: Record<MasteryState['status'], number> = {
  locked: 0,
  available: 0,
  learning: 0.3,
  practising: 0.6,
  mastered: 1,
  decaying: 0.7,
}

export function currentMasteryOf(state: MasteryState | undefined): number {
  return state ? STATUS_MASTERY[state.status] : 0
}

/** SPEC.md §10.1: roiScore * catFrequency * (1 - currentMastery). */
export function roiPriorityOf(topic: MicroTopic, masteryState: MasteryState | undefined): number {
  return topic.roiScore * FREQUENCY_WEIGHT[topic.catFrequency] * (1 - currentMasteryOf(masteryState))
}

/**
 * ROI-weighted topological sort (SPEC.md §10.1): respects `prerequisites`,
 * and among topics whose prerequisites are already scheduled, always picks
 * the highest ROI-priority one next. O(n^2) — fine at syllabus scale
 * (~90 micro-topics).
 */
export function roiWeightedTopoSort(
  topics: MicroTopic[],
  masteryByTopicId: Map<string, MasteryState>,
): MicroTopic[] {
  const byId = new Map(topics.map((t) => [t.id, t]))
  const remaining = new Set(topics.map((t) => t.id))
  const scheduled = new Set<string>()
  const result: MicroTopic[] = []

  function prereqsSatisfied(topic: MicroTopic): boolean {
    return (topic.prerequisites ?? []).every((p) => scheduled.has(p) || !byId.has(p))
  }

  while (remaining.size > 0) {
    let best: MicroTopic | null = null
    let bestScore = -Infinity
    for (const id of remaining) {
      const topic = byId.get(id)!
      if (!prereqsSatisfied(topic)) continue
      const score = roiPriorityOf(topic, masteryByTopicId.get(id))
      if (score > bestScore) {
        bestScore = score
        best = topic
      }
    }
    if (!best) {
      // A prerequisite cycle (or a prerequisite id outside `topics`) would
      // otherwise loop forever — break it by taking any remaining topic
      // rather than never terminating. Shouldn't happen with a clean
      // syllabus, but a plan generator must terminate no matter what.
      best = byId.get([...remaining][0])!
    }
    result.push(best)
    scheduled.add(best.id)
    remaining.delete(best.id)
  }

  return result
}
