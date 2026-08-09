/**
 * SPEC.md §8.3 — adaptive item selection for a drill queue.
 *
 *   60% items with itemElo in [learnerElo-50, learnerElo+100] — productive struggle
 *   20% deliberately above her level (+150 to +300) — ceiling stretch
 *   10% below (-200) — confidence and fluency
 *   10% interleaved from earlier mastered/decaying topics — non-negotiable
 *   Never repeat an item answered correctly within the last 14 days unless it's an SRS review.
 *
 * SRS review (§8.4) is out of scope for Milestone 5 (it's Milestone 12), so
 * "unless it's an SRS review" has no exception path yet — recently-correct
 * items are simply excluded.
 */

export interface CandidateItem {
  questionId: string
  itemElo: number
}

export interface SelectDrillQueueInput {
  learnerElo: number
  /** Candidate items for the topic being drilled. */
  currentTopicItems: CandidateItem[]
  /** Candidate items from other mastered/decaying topics, for interleaving. */
  interleaveItems: CandidateItem[]
  /** questionIds answered correctly within the last 14 days — excluded. */
  recentlyCorrectIds: ReadonlySet<string>
  size?: number
  /** Injectable for deterministic tests; defaults to Math.random. */
  random?: () => number
}

function shuffle<T>(items: T[], random: () => number): T[] {
  const copy = [...items]
  for (let i = copy.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1))
    ;[copy[i], copy[j]] = [copy[j], copy[i]]
  }
  return copy
}

function take(pool: CandidateItem[], count: number, exclude: Set<string>): CandidateItem[] {
  const picked: CandidateItem[] = []
  for (const item of pool) {
    if (picked.length >= count) break
    if (exclude.has(item.questionId)) continue
    picked.push(item)
    exclude.add(item.questionId)
  }
  return picked
}

export function selectDrillQueue({
  learnerElo,
  currentTopicItems,
  interleaveItems,
  recentlyCorrectIds,
  size = 10,
  random = Math.random,
}: SelectDrillQueueInput): CandidateItem[] {
  const usable = (items: CandidateItem[]) =>
    shuffle(
      items.filter((i) => !recentlyCorrectIds.has(i.questionId)),
      random,
    )

  const productivePool = usable(
    currentTopicItems.filter((i) => i.itemElo >= learnerElo - 50 && i.itemElo <= learnerElo + 100),
  )
  const stretchPool = usable(
    currentTopicItems.filter((i) => i.itemElo >= learnerElo + 150 && i.itemElo <= learnerElo + 300),
  )
  const fluencyPool = usable(currentTopicItems.filter((i) => i.itemElo <= learnerElo - 200))
  const interleavePool = usable(interleaveItems)
  const anyPool = usable(currentTopicItems)

  const interleaveCount = Math.round(size * 0.1)
  const fluencyCount = Math.round(size * 0.1)
  const stretchCount = Math.round(size * 0.2)
  const productiveCount = size - interleaveCount - fluencyCount - stretchCount

  const chosen = new Set<string>()
  const queue: CandidateItem[] = [
    ...take(interleavePool, interleaveCount, chosen),
    ...take(fluencyPool, fluencyCount, chosen),
    ...take(stretchPool, stretchCount, chosen),
    ...take(productivePool, productiveCount, chosen),
  ]

  // Backfill from whatever's left in the current topic if a band's pool was
  // too thin (a young content bank won't always have every band covered) —
  // a short-but-imperfect queue beats an artificially truncated one.
  if (queue.length < size) {
    queue.push(...take(anyPool, size - queue.length, chosen))
  }
  if (queue.length < size) {
    queue.push(...take(interleavePool, size - queue.length, chosen))
  }

  return queue
}
