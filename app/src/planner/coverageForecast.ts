import type { MicroTopic } from '@/types/content'
import { estimatedMinutes, type GeneratePlanResult } from './generatePlan'

/** roiScore >= this counts as "high-ROI" for the forecast headline — matches SPEC.md §10.2's own
 * example framing ("78% of high-ROI topics"). */
const HIGH_ROI_THRESHOLD = 3

export interface CoverageForecast {
  totalHighRoiTopics: number
  coveredHighRoiTopics: number
  coveragePct: number
  droppedTopics: MicroTopic[]
  droppedHoursEstimate: number
  message: string
}

/** SPEC.md §10.2 (Triage): "Show a Coverage Forecast ... that honesty is a feature." */
export function computeCoverageForecast(
  allTopics: MicroTopic[],
  result: GeneratePlanResult,
  examDateLabel: string,
): CoverageForecast {
  const highRoi = allTopics.filter((t) => t.roiScore >= HIGH_ROI_THRESHOLD)
  const coveredHighRoi = highRoi.filter((t) => result.scheduledTopicIds.has(t.id))
  const coveragePct = highRoi.length === 0 ? 100 : Math.round((coveredHighRoi.length / highRoi.length) * 100)

  const droppedHoursEstimate = Math.round(
    result.droppedTopics.reduce((sum, t) => sum + estimatedMinutes(t), 0) / 60,
  )

  const message =
    result.droppedTopics.length === 0
      ? `On track to cover all high-ROI topics by ${examDateLabel}.`
      : `At your current pace you'll cover ${coveragePct}% of high-ROI topics by ${examDateLabel}. ` +
        `Recommended: drop ${result.droppedTopics
          .slice(0, 3)
          .map((t) => t.name)
          .join(', ')}${result.droppedTopics.length > 3 ? ', ...' : ''} — ` +
        `${droppedHoursEstimate}h of study.`

  return {
    totalHighRoiTopics: highRoi.length,
    coveredHighRoiTopics: coveredHighRoi.length,
    coveragePct,
    droppedTopics: result.droppedTopics,
    droppedHoursEstimate,
    message,
  }
}
