// Milestone 16 (SPEC.md §11 Phase 2). Plain, dependency-free ESM JavaScript (not TypeScript) so
// this one file can be imported unmodified by both the Deno Edge Function (supabase/functions/
// daily-nudge/index.ts) and a plain Node/vitest test (app/*.test.ts) — no build step, no shared
// tsconfig to keep in sync between two totally different runtimes.
//
// SPEC.md §11: "Design principle: encouraging, never nagging... every email must be opt-in,
// must have a one-click off switch, and should read like a helpful note, not a compliance
// report." Every subject/body here is deliberately short and specific — one topic, one link,
// nothing else — per the exact daily-email example SPEC.md gives.

function escapeHtml(s) {
  return String(s)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
}

function wrap(bodyHtml, appUrl) {
  return `<div style="font-family:system-ui,sans-serif;max-width:480px;margin:0 auto;padding:24px;">${bodyHtml}<p style="margin-top:24px;font-size:12px;color:#888;">You're getting this because email reminders are on in Ascent. <a href="${appUrl}/#/settings">Turn them off</a> any time.</p></div>`
}

/** SPEC.md §11: "Daily (morning): 'Today: Time & Work — Pipes & Cisterns. 35 min. [Open]' —
 * one topic, one link, nothing else." */
export function dailyNudgeEmail({ topicName, minutes, appUrl }) {
  const subject = `Today: ${topicName} — ${minutes} min`
  const text = `${subject}\n\nOpen Ascent: ${appUrl}`
  const html = wrap(
    `<p style="font-size:16px;">Today: <strong>${escapeHtml(topicName)}</strong> — ${minutes} min.</p>` +
      `<p><a href="${appUrl}" style="display:inline-block;padding:8px 16px;background:#7e14ff;color:#fff;border-radius:8px;text-decoration:none;">Open</a></p>`,
    appUrl,
  )
  return { subject, text, html }
}

/** SPEC.md §11: "Topic-complete: a genuine congratulation with the mastery stat and what
 * unlocked next." */
export function topicCompleteEmail({ topicName, learnerElo, unlockedNext, appUrl }) {
  const subject = `Mastered: ${topicName}`
  const unlockedLine = unlockedNext ? ` Next up: ${unlockedNext}.` : ''
  const text = `You've mastered ${topicName} (learner rating ${Math.round(learnerElo)}).${unlockedLine}\n\n${appUrl}`
  const html = wrap(
    `<p style="font-size:16px;">You've mastered <strong>${escapeHtml(topicName)}</strong> 🎯</p>` +
      `<p>Learner rating: ${Math.round(learnerElo)}.${unlockedLine ? ` ${escapeHtml(unlockedLine.trim())}` : ''}</p>` +
      `<p><a href="${appUrl}">Keep going</a></p>`,
    appUrl,
  )
  return { subject, text, html }
}

/** SPEC.md §11: "Weekly Sunday digest: minutes studied, topics mastered, accuracy trend, next
 * week's plan, one specific insight." */
export function weeklyDigestEmail({ minutesStudied, topicsMastered, accuracyTrendPct, nextWeekTopic, insight, appUrl }) {
  const subject = `Your week: ${minutesStudied} min, ${topicsMastered} topic(s) mastered`
  const trendLine = accuracyTrendPct >= 0 ? `up ${accuracyTrendPct}%` : `down ${Math.abs(accuracyTrendPct)}%`
  const text = [
    `${minutesStudied} minutes studied this week.`,
    `${topicsMastered} topic(s) mastered.`,
    `Accuracy ${trendLine} vs last week.`,
    `Next week: ${nextWeekTopic}.`,
    insight,
    '',
    appUrl,
  ].join('\n')
  const html = wrap(
    `<p style="font-size:16px;">This week: <strong>${minutesStudied} min</strong>, <strong>${topicsMastered}</strong> topic(s) mastered.</p>` +
      `<p>Accuracy ${trendLine} vs last week.</p>` +
      `<p>Next week: ${escapeHtml(nextWeekTopic)}.</p>` +
      `<p style="font-style:italic;">${escapeHtml(insight)}</p>` +
      `<p><a href="${appUrl}">Open Ascent</a></p>`,
    appUrl,
  )
  return { subject, text, html }
}

/** SPEC.md §11: "Mock reminder the evening before." */
export function mockReminderEmail({ mockTitle, appUrl }) {
  const subject = `Tomorrow: ${mockTitle}`
  const text = `${mockTitle} is scheduled for tomorrow. Get a full night's sleep — this one's timed like the real thing.\n\n${appUrl}`
  const html = wrap(
    `<p style="font-size:16px;"><strong>${escapeHtml(mockTitle)}</strong> is scheduled for tomorrow.</p>` +
      `<p>Get a full night's sleep — this one's timed like the real thing.</p>` +
      `<p><a href="${appUrl}">Open Ascent</a></p>`,
    appUrl,
  )
  return { subject, text, html }
}

/** SPEC.md §11: "Milestone emails: 100 days out, 50, 30, 14, 7, 1 — with what to focus on at
 * that stage." */
export const MILESTONE_DAYS = [100, 50, 30, 14, 7, 1]

const MILESTONE_FOCUS = {
  100: 'Base-building phase. Cover breadth before depth — every micro-topic at least once.',
  50: 'Halfway. Shift weight toward your weakest section and start taking sectional mocks.',
  30: "One month. It's full-mock season — sit one every week and drill only what mocks expose.",
  14: 'Two weeks. Stop learning new topics entirely. Consolidate, revise formula cards, sleep well.',
  7: 'One week. Light revision only. One easy mock, then rest — cramming now does more harm than good.',
  1: "Tomorrow's the day. No studying today. Pack your admit card and ID, check your reporting time, and rest.",
}

export function milestoneEmail({ daysOut, appUrl }) {
  const subject = daysOut === 1 ? 'CAT is tomorrow' : `${daysOut} days to CAT`
  const focus = MILESTONE_FOCUS[daysOut]
  const text = `${subject}. ${focus}\n\n${appUrl}`
  const html = wrap(
    `<p style="font-size:16px;"><strong>${escapeHtml(subject)}</strong></p><p>${escapeHtml(focus)}</p>` +
      `<p><a href="${appUrl}">Open Ascent</a></p>`,
    appUrl,
  )
  return { subject, text, html }
}
