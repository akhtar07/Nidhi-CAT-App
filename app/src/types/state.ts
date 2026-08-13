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
  /**
   * Milestone 12: when this topic was last graded through FSRS (elo.ts's updateElo also runs
   * every attempt, but FSRS's stability-growth math specifically needs to know the *actual*
   * elapsed time since the last review, not just now-vs-due — not in SPEC.md §5.2's literal
   * interface, added for the same reason app/src/srs/fsrsAdapter.ts documents its own addition
   * of this field).
   */
  lastReviewedAt?: number
}

/**
 * Milestone 12 (SPEC.md §8.4): "Apply it [FSRS] at ... Card level — formula cards,
 * vocabulary-in-context cards, and every question she got wrong (auto-added as a card)."
 * Not in SPEC.md §5.2's literal type list (that section predates SRS cards being scoped out as
 * their own storage concern) but required to implement §8.4's card level at all — same
 * add-and-document pattern as everything else added this build.
 */
export interface SrsCard {
  schemaVersion: 1
  id: string
  cardType: 'formula' | 'mistake'
  /** FormulaCard.id for 'formula' cards, Question.id for 'mistake' cards. */
  refId: string
  microTopicId: string
  stability: number
  difficulty: number
  nextReviewAt: number
  lastReviewedAt?: number
  addedAt: number
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
  /**
   * Milestone 11: every Attempt logged from one mock sitting shares the exact same startedAt
   * (set from MockSession.startedAt in MockPlayer.finishMock) — the join key post-mock analysis
   * uses to find "this result's attempts" specifically, since a mock can be retaken and Attempt
   * itself carries no mock/result id. Not in SPEC.md §5.2's literal interface, same
   * add-and-document pattern as every other learner-state addition this build.
   */
  startedAt?: number
}

export type PaletteStatus = 'not_visited' | 'not_answered' | 'answered' | 'marked' | 'answered_marked'

export interface MockQuestionState {
  given: string | null
  markedForReview: boolean
  visitCount: number
  /** Cumulative seconds actually spent on this question — SPEC.md §9.1's "silently record
   * per-question dwell time." */
  dwellSec: number
}

/**
 * Milestone 10: the *in-progress* mock (SPEC.md §9.1's crash recovery —
 * "persist mock state to IndexedDB every 5 seconds; on reload, resume with
 * the correct remaining time"). Distinct from MockResult, which only exists
 * once a mock is finished. A singleton like Settings: SPEC.md's flow is
 * "resume THE in-progress mock," never several at once.
 */
export interface MockSession {
  schemaVersion: 1
  mockId: string
  startedAt: number
  currentSectionIndex: number
  /** Wall-clock timestamp the current section started — remaining time is computed from this on
   * every read, not a pausable countdown, so a closed tab doesn't freeze the clock. */
  sectionStartedAt: number
  currentQuestionIndex: number
  questionStates: Record<string, MockQuestionState>
  completedSectionIndices: number[]
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
  /**
   * Milestone 15: opt-in for the local daily-nudge notification (SPEC.md §11 Phase 1 — "Web
   * Push via service worker... works offline, no backend needed"). Not in SPEC.md §5.2's
   * literal interface for the same reason diagnosticCompletedAt isn't — added when the feature
   * needing it was built, documented here per the project's schema-change rule.
   */
  notificationsEnabled?: boolean
  /**
   * Milestone 15: the local date (YYYY-MM-DD, Asia/Kolkata) the daily-nudge notification was
   * last shown, so opening the app twice in one day doesn't fire it twice.
   */
  lastNudgeShownDate?: string
  /**
   * Professionalization pass: the last filters used in the custom practice builder, so the
   * page reopens where the learner left it rather than resetting every visit. Optional and
   * purely a convenience — nothing reads it for scheduling or scoring, so an absent or stale
   * value is harmless. Added as an optional field on the existing settings record, which is
   * why `schemaVersion` stays 1 and no migration step is needed (an old row simply reads
   * `undefined` here).
   */
  practiceBuilderPrefs?: {
    sections: Section[]
    microTopicIds: string[]
    difficulties: ('easy' | 'medium' | 'hard' | 'very_hard')[]
    count: number
    timeLimitMinutes: number | null
  }
  /**
   * Phone reminders via ntfy (see notify/ntfy.ts for why ntfy, and why the topic name is not
   * an API key). Separate from `notificationsEnabled`, which is the in-browser service-worker
   * notification: that one can only fire while Ascent is open, this one reaches a closed phone.
   * Both can be on, off, or either one alone.
   */
  ntfy?: {
    enabled: boolean
    /** Doubles as the password — see notify/ntfy.ts. Generated, not chosen. */
    topic: string
    /** Base URL. Defaults to https://ntfy.sh; a self-hosted server works unchanged. */
    server: string
    /** 'HH:MM' in Asia/Kolkata: when an unfinished day gets its one reminder. */
    reminderTime: string
    /** Announce a topic the first time the plan introduces it. */
    newTopicAlerts: boolean
    /** Send the evening reminder when the day's plan still has unfinished items. */
    dailyGoalReminder: boolean
  }
  /**
   * Bookkeeping for the above, kept separate from the settings the learner actually edits so
   * that Settings' own save button never has to round-trip it. Not user-facing.
   */
  ntfyState?: {
    /** Micro-topic ids already announced, so a topic is introduced exactly once. */
    announcedTopics: string[]
    /** What the pending scheduled reminder currently says, so an unchanged day is not
     * re-published to the server on every single app open. */
    lastScheduledSignature?: string
    /** Asia/Kolkata date whose "plan complete" note has already gone out. */
    lastCompletionDate?: string
  }
}

/**
 * Study-flow feature (professionalization pass, not in SPEC.md's original type list — same
 * add-and-document pattern as every other learner-state addition this build). Lets the learner
 * flag any question during a drill/mock/review for later revisit, independent of the SRS/mistake
 * pipeline (a bookmark is a manual "come back to this," not an auto-scheduled review card).
 */
export interface Bookmark {
  schemaVersion: 1
  id: string
  questionId: string
  microTopicId: string
  createdAt: number
}
