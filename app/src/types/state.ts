/**
 * Learner-state types (SPEC.md §5.2) — mutable, lives in IndexedDB via
 * StorageAdapter. NOT part of the pydantic/JSON-Schema generation pipeline
 * that produces content.ts: this data is never authored or validated by
 * the Python content pipeline, only by the app itself.
 *
 * Every stored record type carries its own `schemaVersion`, independent of
 * Dexie's table-level version (see storage/dexie/schema.ts). Dexie's
 * version handles IndexedDB structure (tables/indexes); schemaVersion
 * handles the shape of an individual record, so a future field rename/add
 * can migrate existing rows in place. Per SPEC.md §5.2: "Every schema gets
 * a schemaVersion field and a migration function from day one."
 */

export type Section = 'VARC' | 'DILR' | 'QA'

export interface Attempt {
  schemaVersion: 1
  id: string
  questionId: string
  microTopicIds: string[]
  startedAt: number
  submittedAt: number
  timeSpentSec: number
  /** null = skipped */
  given: string | null
  correct: boolean
  /** ask BEFORE revealing the answer */
  confidence?: 'guess' | 'unsure' | 'sure'
  errorTag?:
    | 'concept'
    | 'calculation'
    | 'misread'
    | 'time_pressure'
    | 'careless_option'
    | 'unknown_formula'
    | 'guessed'
  mode: 'drill' | 'topic_test' | 'mock' | 'review' | 'warmup'
  markedForReview: boolean
}

export interface MasteryState {
  schemaVersion: 1
  microTopicId: string
  status: 'locked' | 'available' | 'learning' | 'practising' | 'mastered' | 'decaying'
  learnerElo: number
  /** rolling window of 10 */
  lastNCorrect: boolean[]
  medianTimeSec: number
  hardTierCleared: boolean
  attemptsCount: number
  masteredAt?: number
  /** SRS */
  nextReviewAt?: number
  /** FSRS params */
  stability: number
  difficulty: number
}

export interface PlanItem {
  microTopicId: string
  kind: 'learn' | 'drill' | 'review' | 'mock'
  targetCount?: number
  done: boolean
}

export interface PlanDay {
  schemaVersion: 1
  date: string
  items: PlanItem[]
  status: 'pending' | 'done' | 'partial' | 'missed'
}

export interface MockResult {
  schemaVersion: 1
  id: string
  mockId: string
  takenAt: number
  sectionScores: Record<Section, { score: number; correct: number; incorrect: number; skipped: number }>
  questionTimings: Record<string, number>
  percentileEstimate?: number
}

export interface Settings {
  schemaVersion: 1
  dailyMinutes: number
  examDate: string
  weakSectionBias: Section | null
  emailOptIn: boolean
}
