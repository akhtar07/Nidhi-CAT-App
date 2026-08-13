import type { SyncTable } from './syncQueue'
import type { Attempt, Bookmark, MasteryState, MockResult, PlanDay, Settings, SrsCard } from '@/types/state'

/** Postgres convention is snake_case; the TS side stays camelCase throughout — these are the
 * only place the two meet. One direction only (JS -> row): SupabaseSyncAdapter never reads back
 * from Supabase, so there's no inverse mapper to keep in sync. */

export const TABLE_KEY_COLUMN: Record<SyncTable, string> = {
  attempts: 'id',
  mastery_states: 'micro_topic_id',
  plan_days: 'date',
  mock_results: 'id',
  item_elo: 'question_id',
  settings: 'id',
  srs_cards: 'id',
  bookmarks: 'id',
}

export function attemptToRow(a: Attempt, userId: string) {
  return {
    id: a.id,
    user_id: userId,
    question_id: a.questionId,
    micro_topic_ids: a.microTopicIds,
    started_at: a.startedAt,
    submitted_at: a.submittedAt,
    time_spent_sec: a.timeSpentSec,
    given: a.given,
    correct: a.correct,
    confidence: a.confidence ?? null,
    error_tag: a.errorTag ?? null,
    mode: a.mode,
    marked_for_review: a.markedForReview,
  }
}

export function masteryStateToRow(m: MasteryState, userId: string) {
  return {
    micro_topic_id: m.microTopicId,
    user_id: userId,
    status: m.status,
    learner_elo: m.learnerElo,
    last_n_correct: m.lastNCorrect,
    median_time_sec: m.medianTimeSec,
    hard_tier_cleared: m.hardTierCleared,
    attempts_count: m.attemptsCount,
    mastered_at: m.masteredAt ?? null,
    criteria123_first_met_at: m.criteria123FirstMetAt ?? null,
    anti_frustration_triggered: m.antiFrustrationTriggered ?? null,
    next_review_at: m.nextReviewAt ?? null,
    stability: m.stability,
    difficulty: m.difficulty,
    last_reviewed_at: m.lastReviewedAt ?? null,
  }
}

export function planDayToRow(p: PlanDay, userId: string) {
  return {
    date: p.date,
    user_id: userId,
    items: p.items,
    status: p.status,
  }
}

export function mockResultToRow(r: MockResult, userId: string) {
  return {
    id: r.id,
    user_id: userId,
    mock_id: r.mockId,
    taken_at: r.takenAt,
    section_scores: r.sectionScores,
    question_timings: r.questionTimings,
    percentile_estimate: r.percentileEstimate ?? null,
    started_at: r.startedAt ?? null,
  }
}

export function itemEloToRow(state: { questionId: string; elo: number }, userId: string) {
  return {
    question_id: state.questionId,
    user_id: userId,
    elo: state.elo,
  }
}

export function settingsToRow(s: Settings, userId: string) {
  return {
    id: 'singleton',
    user_id: userId,
    daily_minutes: s.dailyMinutes,
    exam_date: s.examDate,
    weak_section_bias: s.weakSectionBias,
    email_opt_in: s.emailOptIn,
    diagnostic_completed_at: s.diagnosticCompletedAt ?? null,
    notifications_enabled: s.notificationsEnabled ?? null,
    last_nudge_shown_date: s.lastNudgeShownDate ?? null,
    // jsonb columns, added in supabase/migrations/0003_ntfy_settings.sql — see that file for
    // why these two stay as blobs instead of being flattened into columns.
    ntfy: s.ntfy ?? null,
    ntfy_state: s.ntfyState ?? null,
  }
}

export function srsCardToRow(c: SrsCard, userId: string) {
  return {
    id: c.id,
    user_id: userId,
    card_type: c.cardType,
    ref_id: c.refId,
    micro_topic_id: c.microTopicId,
    stability: c.stability,
    difficulty: c.difficulty,
    next_review_at: c.nextReviewAt,
    last_reviewed_at: c.lastReviewedAt ?? null,
    added_at: c.addedAt,
  }
}

export function bookmarkToRow(b: Bookmark, userId: string) {
  return {
    id: b.id,
    user_id: userId,
    question_id: b.questionId,
    micro_topic_id: b.microTopicId,
    created_at: b.createdAt,
  }
}
