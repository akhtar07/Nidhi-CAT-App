import type { Attempt } from '@/types/state'

export interface ErrorTagCluster {
  tag: NonNullable<Attempt['errorTag']>
  count: number
}

/**
 * SPEC.md §8.2's anti-frustration valve routes the learner "back to the
 * lesson with the specific sub-concept her error tags cluster around" —
 * this picks that cluster out of the topic's attempt history, most
 * frequent first.
 */
export function clusterErrorTags(attempts: Pick<Attempt, 'errorTag'>[]): ErrorTagCluster[] {
  const counts = new Map<NonNullable<Attempt['errorTag']>, number>()
  for (const a of attempts) {
    if (!a.errorTag) continue
    counts.set(a.errorTag, (counts.get(a.errorTag) ?? 0) + 1)
  }
  return [...counts.entries()].map(([tag, count]) => ({ tag, count })).sort((a, b) => b.count - a.count)
}
