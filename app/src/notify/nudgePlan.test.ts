import { describe, expect, it } from 'vitest'
import { dailySequenceId, decideNudges, istToUnixSeconds, type NudgeInput } from './nudgePlan'
import type { PlanDay, Settings } from '@/types/state'

const TODAY = '2026-08-13'
/** 08:00 IST on TODAY — well before the default 20:00 reminder. */
const MORNING_MS = (istToUnixSeconds(TODAY, '08:00') as number) * 1000

const NAMES = new Map([
  ['qa.arith.percentages', 'Percentages'],
  ['qa.arith.ratio-proportion', 'Ratio & Proportion'],
  ['varc.rc.main-idea', 'Main Idea'],
  ['dilr.di.caselets', 'Caselets'],
])

function settings(overrides: Partial<Settings> = {}): Settings {
  return {
    schemaVersion: 1,
    dailyMinutes: 90,
    examDate: '2026-11-29',
    weakSectionBias: null,
    emailOptIn: false,
    ntfy: {
      enabled: true,
      topic: 'ascent-test-topic',
      server: 'https://ntfy.sh',
      reminderTime: '20:00',
      newTopicAlerts: true,
      dailyGoalReminder: true,
    },
    ...overrides,
  }
}

function plan(items: PlanDay['items']): PlanDay {
  return { schemaVersion: 1, date: TODAY, items, status: 'pending' }
}

function input(overrides: Partial<NudgeInput> = {}): NudgeInput {
  return {
    settings: settings(),
    todayPlan: plan([{ microTopicId: 'qa.arith.percentages', kind: 'drill', done: false }]),
    todayIso: TODAY,
    nowMs: MORNING_MS,
    topicNameById: NAMES,
    appUrl: 'https://example.github.io/ascent/',
    ...overrides,
  }
}

describe('istToUnixSeconds', () => {
  it('treats the time as Asia/Kolkata regardless of the host timezone', () => {
    // 20:00 IST is 14:30 UTC the same day.
    expect(istToUnixSeconds('2026-08-13', '20:00')).toBe(Date.UTC(2026, 7, 13, 14, 30) / 1000)
  })

  it('rejects malformed input rather than guessing', () => {
    expect(istToUnixSeconds('13-08-2026', '20:00')).toBeNull()
    expect(istToUnixSeconds('2026-08-13', '8:00')).toBeNull()
    expect(istToUnixSeconds('2026-08-13', '25:00')).toBeNull()
  })
})

describe('decideNudges', () => {
  it('does nothing when ntfy is off', () => {
    const decision = decideNudges(input({ settings: settings({ ntfy: undefined }) }))
    expect(decision.actions).toEqual([])
    expect(decision.statePatch).toBeNull()
  })

  it('schedules the evening reminder for an unfinished day', () => {
    const decision = decideNudges(input())
    const scheduled = decision.actions.find((a) => a.kind === 'publish' && a.message.deliverAt)
    expect(scheduled).toBeDefined()
    if (scheduled?.kind !== 'publish') throw new Error('expected a publish')
    expect(scheduled.message.deliverAt).toBe(istToUnixSeconds(TODAY, '20:00'))
    expect(scheduled.message.sequenceId).toBe(dailySequenceId(TODAY))
    expect(scheduled.message.body).toContain('Percentages')
  })

  it('sends nothing at all once the reminder time has passed — a late nudge is just nagging', () => {
    const evening = (istToUnixSeconds(TODAY, '21:30') as number) * 1000
    const decision = decideNudges(
      input({
        nowMs: evening,
        settings: settings({ ntfy: { ...settings().ntfy!, newTopicAlerts: false } }),
      }),
    )
    expect(decision.actions).toEqual([])
  })

  it('cancels the pending reminder and congratulates once the day is finished', () => {
    const finished = plan([{ microTopicId: 'qa.arith.percentages', kind: 'drill', done: true }])
    const withPending = settings({
      ntfyState: { announcedTopics: ['qa.arith.percentages'], lastScheduledSignature: 'something' },
    })
    const decision = decideNudges(input({ todayPlan: finished, settings: withPending }))

    expect(decision.actions).toContainEqual({ kind: 'cancel', sequenceId: dailySequenceId(TODAY) })
    const congrats = decision.actions.find((a) => a.kind === 'publish')
    expect(congrats).toBeDefined()
    expect(decision.statePatch?.lastScheduledSignature).toBeUndefined()
    expect(decision.statePatch?.lastCompletionDate).toBe(TODAY)
  })

  it('congratulates only once per day', () => {
    const finished = plan([{ microTopicId: 'qa.arith.percentages', kind: 'drill', done: true }])
    const already = settings({
      ntfyState: { announcedTopics: ['qa.arith.percentages'], lastCompletionDate: TODAY },
    })
    const decision = decideNudges(input({ todayPlan: finished, settings: already }))
    expect(decision.actions).toEqual([])
  })

  it('announces a new topic exactly once, then never again', () => {
    const learning = plan([{ microTopicId: 'varc.rc.main-idea', kind: 'learn', done: false }])
    const first = decideNudges(input({ todayPlan: learning }))
    const announcement = first.actions.find((a) => a.kind === 'publish' && !a.message.deliverAt)
    expect(announcement).toBeDefined()
    if (announcement?.kind !== 'publish') throw new Error('expected a publish')
    expect(announcement.message.body).toContain('Main Idea')
    expect(first.statePatch?.announcedTopics).toContain('varc.rc.main-idea')

    const second = decideNudges(
      input({ todayPlan: learning, settings: settings({ ntfyState: first.statePatch! }) }),
    )
    expect(second.actions.filter((a) => a.kind === 'publish' && !a.message.deliverAt)).toEqual([])
  })

  it('does not re-publish an unchanged reminder on every app open', () => {
    const first = decideNudges(input())
    const second = decideNudges(input({ settings: settings({ ntfyState: first.statePatch! }) }))
    expect(second.actions).toEqual([])
  })

  it('re-publishes when the remaining work changes', () => {
    const twoItems = plan([
      { microTopicId: 'qa.arith.percentages', kind: 'drill', done: false },
      { microTopicId: 'dilr.di.caselets', kind: 'drill', done: false },
    ])
    const first = decideNudges(input({ todayPlan: twoItems }))
    const oneLeft = plan([
      { microTopicId: 'qa.arith.percentages', kind: 'drill', done: true },
      { microTopicId: 'dilr.di.caselets', kind: 'drill', done: false },
    ])
    const second = decideNudges(
      input({ todayPlan: oneLeft, settings: settings({ ntfyState: first.statePatch! }) }),
    )
    const republished = second.actions.find((a) => a.kind === 'publish')
    expect(republished).toBeDefined()
    if (republished?.kind !== 'publish') throw new Error('expected a publish')
    expect(republished.message.body).toContain('1 of 2 left')
    expect(republished.message.body).toContain('Caselets')
    expect(republished.message.body).not.toContain('Percentages')
  })

  it('stays quiet on a day with no plan', () => {
    expect(decideNudges(input({ todayPlan: null })).actions).toEqual([])
  })

  it('respects each toggle independently', () => {
    const learning = plan([{ microTopicId: 'varc.rc.main-idea', kind: 'learn', done: false }])
    const noDaily = settings({ ntfy: { ...settings().ntfy!, dailyGoalReminder: false } })
    const decision = decideNudges(input({ todayPlan: learning, settings: noDaily }))
    expect(decision.actions).toHaveLength(1)
    if (decision.actions[0].kind !== 'publish') throw new Error('expected a publish')
    expect(decision.actions[0].message.deliverAt).toBeUndefined()
  })
})
