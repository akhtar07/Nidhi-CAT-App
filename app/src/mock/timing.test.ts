import { describe, expect, it } from 'vitest'
import { formatMMSS, remainingSeconds } from './timing'

describe('remainingSeconds', () => {
  it('is the full section length right at the start', () => {
    const start = 1000000
    expect(remainingSeconds(start, 40, start)).toBe(40 * 60)
  })

  it('counts down as wall-clock time passes', () => {
    const start = 1000000
    const tenMinutesLater = start + 10 * 60 * 1000
    expect(remainingSeconds(start, 40, tenMinutesLater)).toBe(30 * 60)
  })

  it('never goes negative once time is up', () => {
    const start = 1000000
    const wayLater = start + 999 * 60 * 1000
    expect(remainingSeconds(start, 40, wayLater)).toBe(0)
  })

  it('correctly resumes after a simulated crash (elapsed time survives regardless of when it is read)', () => {
    const start = 1000000
    const rightAfterCrash = remainingSeconds(start, 40, start + 5 * 60 * 1000)
    const readAgainLater = remainingSeconds(start, 40, start + 5 * 60 * 1000 + 1000)
    expect(readAgainLater).toBeLessThanOrEqual(rightAfterCrash)
  })
})

describe('formatMMSS', () => {
  it('pads seconds under 10', () => {
    expect(formatMMSS(65)).toBe('1:05')
  })
  it('formats zero', () => {
    expect(formatMMSS(0)).toBe('0:00')
  })
  it('formats large minute counts without padding minutes', () => {
    expect(formatMMSS(3661)).toBe('61:01')
  })
})
