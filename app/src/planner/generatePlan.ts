import type { MicroTopic } from '@/types/content'
import type { MasteryState, PlanDay, PlanItem } from '@/types/state'
import { addDays, dateRange, dayOfWeek, daysBetween } from './dateUtils'
import { roiWeightedTopoSort } from './roiSort'

/** SPEC.md §10.1: "20% of every day for review/SRS, not new material." */
const REVIEW_FRACTION = 0.2
/** SPEC.md §10.1: "Last 3 weeks = revision + mocks only, no new topics. Hard-code this cutoff." */
const LAST_WEEKS_REVISION_ONLY = 3
/** SPEC.md §10.1: "Sunday = mock day from week 3 onward." Week is 0-indexed from `today`. */
const MOCK_DAY_FROM_WEEK = 3
/** Questions per drill PlanItem, used only for time-estimation in the packer — the actual drill
 * queue itself is built at practice time by selectDrillQueue (Milestone 5). */
export const DRILL_BATCH_SIZE = 10

/** Reserved microTopicId values for PlanItems that don't correspond to a single topic — mock days
 * and the daily review/SRS block (full FSRS-scheduled review-item wiring is Milestone 12). */
export const MOCK_SENTINEL = '__mock__'
export const REVIEW_SENTINEL = '__review__'

export function estimatedMinutes(topic: MicroTopic): number {
  return topic.estLearnMinutes + (DRILL_BATCH_SIZE * topic.targetSecPerQuestion) / 60
}

export interface GeneratePlanInput {
  topics: MicroTopic[]
  masteryByTopicId: Map<string, MasteryState>
  today: string
  examDate: string
  dailyMinutes: number
}

export interface GeneratePlanResult {
  days: PlanDay[]
  scheduledTopicIds: Set<string>
  /** Topics that didn't fit before the revision-only cutoff — SPEC.md §10.2's triage list. */
  droppedTopics: MicroTopic[]
}

/** SPEC.md §10.1: plan generation by ROI-weighted topological sort, packed into daily budgets. */
export function generatePlan(input: GeneratePlanInput): GeneratePlanResult {
  const { topics, masteryByTopicId, today, examDate, dailyMinutes } = input

  const queue = roiWeightedTopoSort(topics, masteryByTopicId).filter(
    (t) => (masteryByTopicId.get(t.id)?.status ?? 'available') !== 'mastered',
  )

  const dates = dateRange(today, examDate)
  const revisionOnlyStartDate = addDays(examDate, -(LAST_WEEKS_REVISION_ONLY * 7 - 1))

  const days: PlanDay[] = []
  const scheduledTopicIds = new Set<string>()
  let queueIndex = 0

  for (const date of dates) {
    const weekIndex = Math.floor(daysBetween(today, date) / 7)
    const isSunday = dayOfWeek(date) === 0
    const isRevisionOnly = date >= revisionOnlyStartDate

    if (isSunday && weekIndex >= MOCK_DAY_FROM_WEEK) {
      days.push({
        schemaVersion: 1,
        date,
        items: [{ microTopicId: MOCK_SENTINEL, kind: 'mock', done: false }],
        status: 'pending',
      })
      continue
    }

    const items: PlanItem[] = []
    const reviewMinutes = dailyMinutes * REVIEW_FRACTION
    // ~1 review item/minute (quick-recall pace, faster than fresh practice) — a rough estimate
    // until FSRS-scheduled review items (Milestone 12) replace this with a real due-item count.
    items.push({
      microTopicId: REVIEW_SENTINEL,
      kind: 'review',
      targetCount: Math.max(1, Math.round(reviewMinutes)),
      done: false,
    })

    if (!isRevisionOnly) {
      let newMinutesBudget = dailyMinutes * (1 - REVIEW_FRACTION)
      while (newMinutesBudget > 0 && queueIndex < queue.length) {
        const topic = queue[queueIndex]
        const cost = estimatedMinutes(topic)
        const dayAlreadyHasNewMaterial = items.some((i) => i.kind === 'learn' || i.kind === 'drill')
        if (cost > newMinutesBudget && dayAlreadyHasNewMaterial) {
          // Doesn't fit what's left of today's budget, and today already has something —
          // leave it for tomorrow rather than cramming.
          break
        }
        items.push({ microTopicId: topic.id, kind: 'learn', done: false })
        items.push({ microTopicId: topic.id, kind: 'drill', targetCount: DRILL_BATCH_SIZE, done: false })
        scheduledTopicIds.add(topic.id)
        newMinutesBudget -= cost
        queueIndex++
      }
    }

    days.push({ schemaVersion: 1, date, items, status: 'pending' })
  }

  return { days, scheduledTopicIds, droppedTopics: queue.slice(queueIndex) }
}
