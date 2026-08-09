import type { MicroTopic } from '@/types/content'
import type { MasteryState, PlanDay, PlanItem } from '@/types/state'
import { roiPriorityOf } from './roiSort'

const REDISTRIBUTE_DAYS = 5
const MAX_EXTRA_LOAD_FRACTION = 0.25

export interface RedistributeResult {
  updatedDays: PlanDay[]
  droppedItems: PlanItem[]
}

/**
 * SPEC.md §10.3: auto-redistribute a missed day's undone items across the
 * next 5 days, capped at +25% daily load; if the deficit exceeds what
 * redistribution can absorb, drop the lowest-ROI item(s).
 *
 * `baselineItemsPerDay` approximates "daily load" as item count (PlanItem
 * doesn't carry an explicit minutes cost) — capacity is floor(baseline *
 * 0.25) per day, floored at 1 so a normal 2-3 item day can still absorb
 * something rather than the cap rounding to zero and dropping everything.
 */
export function redistributeMissedDay(
  missedDay: PlanDay,
  nextDays: PlanDay[],
  topicsById: Map<string, MicroTopic>,
  masteryByTopicId: Map<string, MasteryState>,
  baselineItemsPerDay: number,
): RedistributeResult {
  const undone = missedDay.items.filter((i) => !i.done)

  const priorityOf = (item: PlanItem): number => {
    const topic = topicsById.get(item.microTopicId)
    return topic ? roiPriorityOf(topic, masteryByTopicId.get(item.microTopicId)) : 0
  }
  const sorted = [...undone].sort((a, b) => priorityOf(b) - priorityOf(a))

  const capacityPerDay = Math.max(1, Math.floor(baselineItemsPerDay * MAX_EXTRA_LOAD_FRACTION))
  const days = nextDays.slice(0, REDISTRIBUTE_DAYS).map((d) => ({ ...d, items: [...d.items] }))
  const remainingCapacity = days.map(() => capacityPerDay)
  const droppedItems: PlanItem[] = []

  let dayCursor = 0
  for (const item of sorted) {
    let placed = false
    for (let attempt = 0; attempt < days.length && !placed; attempt++) {
      const idx = (dayCursor + attempt) % days.length
      if (remainingCapacity[idx] > 0) {
        days[idx].items.push(item)
        remainingCapacity[idx]--
        dayCursor = (idx + 1) % days.length
        placed = true
      }
    }
    if (!placed) droppedItems.push(item)
  }

  return { updatedDays: days, droppedItems }
}
