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
  /**
   * SPEC.md §8.2 criterion 4 (retention): set the first time criteria 1-3
   * (accuracy/speed/ceiling) are simultaneously true. Status stays
   * 'practising' (UI shows "practising (pending retention)") until a later
   * correct attempt lands >= 3 days after this timestamp, at which point
   * status becomes 'mastered'. Added in Milestone 5 — not in SPEC.md §5.2's
   * literal interface, but required to implement §8.2 criterion 4 at all.
   */
  criteria123FirstMetAt?: number
  /**
   * SPEC.md §8.2 anti-frustration valve tripped for this topic (>=30
   * attempts without meeting criteria 1-3, or <40% accuracy after 15).
   * Added in Milestone 5, alongside criteria123FirstMetAt.
   */
  antiFrustrationTriggered?: boolean
  /** SRS */
  nextReviewAt?: number
  /** FSRS params */
  stability: number
  difficulty: number
}

/**
 * Item-level Elo (SPEC.md §8.3's "both sides"). Not itself in SPEC.md
 * §5.2's literal type list, but required by it: `Question.eloRating` is
 * shipped content (immutable, from /content), so the *live*, adjusted
 * item rating that adapts to how real learners perform against it has to
 * live in learner state instead. Seeded from `Question.eloRating` the
 * first time an item is attempted; keyed by questionId thereafter.
 */
export interface ItemEloState {
  schemaVersion: 1
  questionId: string
  elo: number
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
  /**
   * Milestone 9: set once the first-launch diagnostic (SPEC.md §10.1) has
   * been completed (or explicitly skipped). Not in SPEC.md §5.2's literal
   * interface, but needed to know whether to show the diagnostic on next
   * load — same "add the field, document why" pattern as MasteryState's
   * Milestone 5 additions.
   */
  diagnosticCompletedAt?: number
}
