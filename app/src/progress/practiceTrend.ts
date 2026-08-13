/**
 * Weekly accuracy and pace from ordinary practice.
 *
 * `/progress` previously trended mock scores only. Mocks are rare (10 exist, and she
 * may sit one a fortnight), so the chart stayed empty while she practised daily and
 * gave no signal about whether that daily work was landing. This trends the
 * `Attempt` log instead, which is where nearly all the data actually is.
 *
 * **Attempt population:** mock attempts are excluded here, unlike in
 * `topicProgress.ts`. A mock is a different task — different pacing, different
 * selection pressure, negative marking — so folding its attempts into a practice
 * trend would make the line jump on mock weeks for reasons that have nothing to do
 * with practice. Mock performance already has its own trend on the same page.
 */

import type { Attempt } from '@/types/state'

export interface PracticeWeek {
  /** ISO date (YYYY-MM-DD) of the Monday that starts this week, in UTC. */
  weekStart: string
  attempts: number
  correct: number
  /** 0-100. Never null: a week only exists in the output if it has attempts. */
  accuracyPct: number
  /** Median seconds per question that week — median, not mean, so one abandoned question does not swamp it. */
  medianTimeSec: number
}

/** Modes that count as practice. 'mock' is deliberately absent — see the module docstring. */
const PRACTICE_MODES: Attempt['mode'][] = ['drill', 'topic_test', 'review', 'warmup']

function mondayOf(timestamp: number): string {
  const d = new Date(timestamp)
  // Work in UTC to match the planner's date handling (planner/dateUtils.ts).
  const utc = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()))
  // getUTCDay: 0 = Sunday. Shift so Monday starts the week.
  const shift = (utc.getUTCDay() + 6) % 7
  utc.setUTCDate(utc.getUTCDate() - shift)
  return utc.toISOString().slice(0, 10)
}

function median(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
}

/**
 * Buckets practice attempts into calendar weeks, oldest first. Weeks with no practice
 * are omitted rather than plotted as zero — a zero-accuracy point would read as "she got
 * everything wrong" when it actually means "she did not practise".
 */
export function computePracticeTrend(attempts: Attempt[], { maxWeeks = 12 }: { maxWeeks?: number } = {}): PracticeWeek[] {
  const practice = attempts.filter((a) => PRACTICE_MODES.includes(a.mode))

  const byWeek = new Map<string, Attempt[]>()
  for (const attempt of practice) {
    const key = mondayOf(attempt.submittedAt)
    const bucket = byWeek.get(key)
    if (bucket) bucket.push(attempt)
    else byWeek.set(key, [attempt])
  }

  return [...byWeek.entries()]
    .sort(([a], [b]) => a.localeCompare(b))
    .slice(-maxWeeks)
    .map(([weekStart, weekAttempts]) => {
      const correct = weekAttempts.filter((a) => a.correct).length
      return {
        weekStart,
        attempts: weekAttempts.length,
        correct,
        accuracyPct: Math.round((correct / weekAttempts.length) * 100),
        medianTimeSec: Math.round(median(weekAttempts.map((a) => a.timeSpentSec))),
      }
    })
}
