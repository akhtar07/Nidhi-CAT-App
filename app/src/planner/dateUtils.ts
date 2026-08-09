/** All dates in the planner are 'YYYY-MM-DD' strings, handled as UTC noon internally to dodge DST/timezone edge cases in date arithmetic. */

function toDate(iso: string): Date {
  return new Date(`${iso}T12:00:00Z`)
}

function toIso(date: Date): string {
  return date.toISOString().slice(0, 10)
}

export function addDays(iso: string, n: number): string {
  const d = toDate(iso)
  d.setUTCDate(d.getUTCDate() + n)
  return toIso(d)
}

export function daysBetween(fromIso: string, toIso_: string): number {
  const ms = toDate(toIso_).getTime() - toDate(fromIso).getTime()
  return Math.round(ms / (24 * 60 * 60 * 1000))
}

/** 0 = Sunday, matching Date#getUTCDay(). */
export function dayOfWeek(iso: string): number {
  return toDate(iso).getUTCDay()
}

export function dateRange(fromIso: string, toIso_: string): string[] {
  const n = daysBetween(fromIso, toIso_)
  const dates: string[] = []
  for (let i = 0; i <= n; i++) dates.push(addDays(fromIso, i))
  return dates
}

export function todayIso(): string {
  return toIso(new Date())
}

/**
 * SPEC.md §7: "Pin everything to Asia/Kolkata for day boundaries — a 'day' must roll over at
 * midnight IST, not UTC, or her streak will break at 5:30 AM." Unlike todayIso() above (UTC —
 * a pre-existing gap elsewhere in this codebase, out of scope to sweep in this milestone, see
 * PROGRESS.md), this is used for Milestone 15's daily-nudge de-dupe, which is new code with no
 * reason to carry the same bug forward.
 */
export function todayIsoIST(): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata' }).format(new Date())
}
