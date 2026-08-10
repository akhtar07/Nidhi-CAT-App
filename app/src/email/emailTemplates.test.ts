// Tests the plain-JS shared module the Deno Edge Function also imports unmodified
// (supabase/functions/_shared/{emailTemplates,selectEmail}.js) — importing it directly by
// relative path rather than duplicating the logic here. See that module's header comment for
// why it's plain JS, not TypeScript: one file, two runtimes (Deno + this Vite/vitest project),
// no build step in between.
import { describe, expect, it } from 'vitest'
import { dailyNudgeEmail, milestoneEmail, MILESTONE_DAYS, mockReminderEmail, topicCompleteEmail, weeklyDigestEmail } from '../../../supabase/functions/_shared/emailTemplates.js'
import { selectEmailForToday } from '../../../supabase/functions/_shared/selectEmail.js'

const APP_URL = 'https://example.test/'

describe('email templates', () => {
  it('dailyNudgeEmail: one topic, one link, per SPEC.md §11\'s exact example shape', () => {
    const email = dailyNudgeEmail({ topicName: 'Time & Work — Pipes & Cisterns', minutes: 35, appUrl: APP_URL })
    expect(email.subject).toBe('Today: Time & Work — Pipes & Cisterns — 35 min')
    expect(email.text).toContain(APP_URL)
    expect(email.html).toContain(APP_URL)
    expect(email.html).toContain('Pipes &amp; Cisterns')
  })

  it('dailyNudgeEmail escapes HTML in the topic name', () => {
    const email = dailyNudgeEmail({ topicName: '<script>alert(1)</script>', minutes: 10, appUrl: APP_URL })
    expect(email.html).not.toContain('<script>')
    expect(email.html).toContain('&lt;script&gt;')
  })

  it('topicCompleteEmail names the mastery stat and what unlocked next', () => {
    const email = topicCompleteEmail({ topicName: 'Percentages', learnerElo: 1234.6, unlockedNext: 'Profit & Loss', appUrl: APP_URL })
    expect(email.subject).toBe('Mastered: Percentages')
    expect(email.text).toContain('1235')
    expect(email.text).toContain('Profit & Loss')
  })

  it('topicCompleteEmail omits the unlocked line when nothing unlocked', () => {
    const email = topicCompleteEmail({ topicName: 'Percentages', learnerElo: 1200, unlockedNext: null, appUrl: APP_URL })
    expect(email.text).not.toContain('Next up')
  })

  it('weeklyDigestEmail reports a negative accuracy trend correctly', () => {
    const email = weeklyDigestEmail({
      minutesStudied: 240,
      topicsMastered: 2,
      accuracyTrendPct: -5,
      nextWeekTopic: 'Geometry',
      insight: 'Your DILR accuracy is up.',
      appUrl: APP_URL,
    })
    expect(email.text).toContain('down 5%')
  })

  it('mockReminderEmail names the mock', () => {
    const email = mockReminderEmail({ mockTitle: 'Full Mock 3', appUrl: APP_URL })
    expect(email.subject).toBe('Tomorrow: Full Mock 3')
  })

  it('milestoneEmail covers every SPEC.md §11 milestone day with distinct, non-empty focus copy', () => {
    const seen = new Set<string>()
    for (const days of MILESTONE_DAYS) {
      const email = milestoneEmail({ daysOut: days, appUrl: APP_URL })
      expect(email.text.length).toBeGreaterThan(20)
      expect(seen.has(email.text)).toBe(false)
      seen.add(email.text)
    }
  })

  it('milestoneEmail: T-1 gets distinct "tomorrow" phrasing', () => {
    const email = milestoneEmail({ daysOut: 1, appUrl: APP_URL })
    expect(email.subject).toBe('CAT is tomorrow')
  })
})

describe('selectEmailForToday', () => {
  const base = {
    todayIsSundayIST: false,
    daysUntilExam: 62,
    recentlyMasteredTopic: null,
    tomorrowHasMock: null,
    weeklyDigestData: null,
    todayPlanFirstItem: null,
    appUrl: APP_URL,
  }

  it('returns null when nothing is eligible', () => {
    expect(selectEmailForToday(base)).toBeNull()
  })

  it('falls back to the daily nudge when only a plan item is available', () => {
    const result = selectEmailForToday({ ...base, todayPlanFirstItem: { topicName: 'Percentages', minutes: 30 } })
    expect(result?.type).toBe('daily_nudge')
  })

  it('topic-complete outranks everything else, including a milestone day', () => {
    const result = selectEmailForToday({
      ...base,
      daysUntilExam: 100,
      recentlyMasteredTopic: { topicName: 'Percentages', learnerElo: 1300, unlockedNext: null },
      todayPlanFirstItem: { topicName: 'Averages', minutes: 30 },
    })
    expect(result?.type).toBe('topic_complete')
  })

  it('a milestone day outranks a mock reminder and the daily nudge', () => {
    const result = selectEmailForToday({
      ...base,
      daysUntilExam: 7,
      tomorrowHasMock: { mockTitle: 'Full Mock 2' },
      todayPlanFirstItem: { topicName: 'Averages', minutes: 30 },
    })
    expect(result?.type).toBe('milestone')
  })

  it('a mock reminder outranks the Sunday digest and the daily nudge', () => {
    const result = selectEmailForToday({
      ...base,
      todayIsSundayIST: true,
      weeklyDigestData: { minutesStudied: 100, topicsMastered: 1, accuracyTrendPct: 5, nextWeekTopic: 'X', insight: 'Y' },
      tomorrowHasMock: { mockTitle: 'Full Mock 2' },
      todayPlanFirstItem: { topicName: 'Averages', minutes: 30 },
    })
    expect(result?.type).toBe('mock_reminder')
  })

  it('a non-milestone day (e.g. 62 days out) never fires a milestone email', () => {
    const result = selectEmailForToday({ ...base, daysUntilExam: 62, todayPlanFirstItem: { topicName: 'X', minutes: 10 } })
    expect(result?.type).toBe('daily_nudge')
  })
})
