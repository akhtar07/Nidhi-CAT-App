import { describe, expect, it } from 'vitest'
import { addDays, dateRange, dayOfWeek, daysBetween } from './dateUtils'

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
