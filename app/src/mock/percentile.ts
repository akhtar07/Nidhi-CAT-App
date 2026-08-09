/**
 * SPEC.md §9.3: "map raw score -> percentile using published historical CAT
 * scaled-score-to-percentile tables ... label it clearly as 'Estimated from
 * historical CAT data — indicative only.' Do not invent a percentile and
 * present it as fact."
 *
 * There is no live cohort to compute a real percentile against — this is a
 * fixed lookup, hand-built from publicly reported CAT percentile bands
 * (roughly: ~99%ile needs ~90% of max marks, ~90%ile needs roughly half),
 * linearly interpolated between anchor points. It is explicitly a rough
 * indicative mapping, not a claim of precision — every caller must surface
 * the disclaimer, not just the number.
 */
const MAX_SCORE = 204

// (score, percentile) anchor points, ascending by score.
const ANCHORS: [number, number][] = [
  [0, 0],
  [20, 40],
  [40, 60],
  [60, 75],
  [80, 85],
  [100, 91],
  [120, 95],
  [140, 97.5],
  [160, 99],
  [180, 99.7],
  [MAX_SCORE, 99.95],
]

export interface PercentileEstimate {
  percentile: number
  disclaimer: string
}

export function estimatePercentile(score: number): PercentileEstimate {
  const clamped = Math.max(0, Math.min(score, MAX_SCORE))
  let percentile = ANCHORS[ANCHORS.length - 1][1]
  for (let i = 0; i < ANCHORS.length - 1; i++) {
    const [s0, p0] = ANCHORS[i]
    const [s1, p1] = ANCHORS[i + 1]
    if (clamped >= s0 && clamped <= s1) {
      const t = s1 === s0 ? 0 : (clamped - s0) / (s1 - s0)
      percentile = p0 + t * (p1 - p0)
      break
    }
  }
  return {
    percentile: Math.round(percentile * 100) / 100,
    disclaimer: 'Estimated from historical CAT data — indicative only.',
  }
}
