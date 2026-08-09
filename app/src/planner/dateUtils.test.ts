import { afterEach, describe, expect, it, vi } from 'vitest'
import { addDays, dateRange, dayOfWeek, daysBetween, todayIsoIST } from './dateUtils'

describe('addDays', () => {
  it('adds positive days', () => {
    expect(addDays('2026-08-09', 5)).toBe('2026-08-14')
  })
  it('subtracts with negative days', () => {
    expect(addDays('2026-08-09', -9)).toBe('2026-07-31')
  })
  it('crosses a year boundary', () => {
    expect(addDays('2026-12-30', 5)).toBe('2027-01-04')
  })
})

describe('daysBetween', () => {
  it('is 0 for the same date', () => {
    expect(daysBetween('2026-08-09', '2026-08-09')).toBe(0)
  })
  it('counts forward', () => {
    expect(daysBetween('2026-08-09', '2026-11-29')).toBe(112)
  })
})

describe('dayOfWeek', () => {
  it('identifies a known Sunday', () => {
    // 29 Nov 2026 is a Sunday (SPEC.md §2).
    expect(dayOfWeek('2026-11-29')).toBe(0)
  })
})

describe('dateRange', () => {
  it('is inclusive of both endpoints', () => {
    expect(dateRange('2026-08-09', '2026-08-11')).toEqual(['2026-08-09', '2026-08-10', '2026-08-11'])
  })
})

describe('todayIsoIST', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('rolls over at IST midnight, not UTC midnight (SPEC.md §7)', () => {
    // 19:00 UTC on Aug 9 is 00:30 IST on Aug 10 (UTC+5:30) — already "tomorrow" in IST while
    // still "today" in UTC. This is exactly the 5:30 AM streak-break bug SPEC.md §7 names.
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-08-09T19:00:00Z'))
    expect(todayIsoIST()).toBe('2026-08-10')
  })

  it('agrees with the UTC date well inside the IST day', () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-08-09T10:00:00Z')) // 15:30 IST, same calendar day either way
    expect(todayIsoIST()).toBe('2026-08-09')
  })
})
