/** Remaining time is always computed from wall-clock elapsed since the section started, never a
 * pausable countdown — SPEC.md §9.1's crash recovery ("resume with the correct remaining time")
 * needs this: a closed tab must not freeze the clock. */
export function remainingSeconds(sectionStartedAt: number, minutes: number, now: number): number {
  const elapsedSec = Math.floor((now - sectionStartedAt) / 1000)
  return Math.max(0, minutes * 60 - elapsedSec)
}

export function formatMMSS(totalSeconds: number): string {
  const m = Math.floor(totalSeconds / 60)
  const s = totalSeconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}
