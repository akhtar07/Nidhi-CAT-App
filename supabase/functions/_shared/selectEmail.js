// Milestone 16. Pure decision function — given today's facts about one user, picks at most one
// email (SPEC.md §11: "Never more than one email per day. Hard-limit it in code."). The
// database-level cap (email_log's (user_id, sent_date) primary key, see
// supabase/migrations/0001_init.sql) is the actual hard guarantee against double-sends; this
// function is the *choice* of which single email wins when several are eligible the same day.
// Same plain-JS reasoning as emailTemplates.js: importable by both Deno and Node/vitest.

import {
  dailyNudgeEmail,
  milestoneEmail,
  MILESTONE_DAYS,
  mockReminderEmail,
  topicCompleteEmail,
  weeklyDigestEmail,
} from './emailTemplates.js'

/**
 * Priority, highest first: a genuine achievement (topic-complete) or a hard exam-date milestone
 * always wins over the routine daily nudge; a mock the next day matters more than a Sunday
 * digest, which itself is more useful than just "here's today's topic" if both would otherwise
 * fire the same day.
 *
 * @param {{
 *   todayIsSundayIST: boolean,
 *   daysUntilExam: number,
 *   recentlyMasteredTopic: {topicName: string, learnerElo: number, unlockedNext: string | null} | null,
 *   tomorrowHasMock: {mockTitle: string} | null,
 *   weeklyDigestData: {minutesStudied: number, topicsMastered: number, accuracyTrendPct: number, nextWeekTopic: string, insight: string} | null,
 *   todayPlanFirstItem: {topicName: string, minutes: number} | null,
 *   appUrl: string,
 * }} ctx
 */
export function selectEmailForToday(ctx) {
  const { appUrl } = ctx

  if (ctx.recentlyMasteredTopic) {
    return { type: 'topic_complete', ...topicCompleteEmail({ ...ctx.recentlyMasteredTopic, appUrl }) }
  }
  if (MILESTONE_DAYS.includes(ctx.daysUntilExam)) {
    return { type: 'milestone', ...milestoneEmail({ daysOut: ctx.daysUntilExam, appUrl }) }
  }
  if (ctx.tomorrowHasMock) {
    return { type: 'mock_reminder', ...mockReminderEmail({ ...ctx.tomorrowHasMock, appUrl }) }
  }
  if (ctx.todayIsSundayIST && ctx.weeklyDigestData) {
    return { type: 'weekly_digest', ...weeklyDigestEmail({ ...ctx.weeklyDigestData, appUrl }) }
  }
  if (ctx.todayPlanFirstItem) {
    return { type: 'daily_nudge', ...dailyNudgeEmail({ ...ctx.todayPlanFirstItem, appUrl }) }
  }
  return null
}
