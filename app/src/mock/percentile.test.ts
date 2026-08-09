import { describe, expect, it } from 'vitest'
import { estimatePercentile } from './percentile'

describe('estimatePercentile', () => {
  it('is 0 at a score of 0', () => {
    expect(estimatePercentile(0).percentile).toBe(0)
  })

  it('is near max at the max score', () => {
    expect(estimatePercentile(204).percentile).toBeGreaterThan(99)
  })

  it('increases monotonically with score', () => {
    const scores = [0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200]
    const percentiles = scores.map((s) => estimatePercentile(s).percentile)
    for (let i = 1; i < percentiles.length; i++) {
      expect(percentiles[i]).toBeGreaterThanOrEqual(percentiles[i - 1])
    }
  })

  it('clamps scores above the max', () => {
    expect(estimatePercentile(500).percentile).toBe(estimatePercentile(204).percentile)
  })

  it('clamps negative scores to 0', () => {
    expect(estimatePercentile(-50).percentile).toBe(0)
  })

  it('always carries the indicative-only disclaimer', () => {
    expect(estimatePercentile(100).disclaimer).toMatch(/indicative only/i)
  })
})
