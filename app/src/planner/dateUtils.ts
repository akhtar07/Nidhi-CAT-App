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
