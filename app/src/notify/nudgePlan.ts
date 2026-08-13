import type { NtfyMessage } from './ntfy'
import type { PlanDay, Settings } from '@/types/state'

/**
 * Decides which phone reminders today's state calls for. Pure: no fetch, no storage, no clock —
 * `nowMs` and the plan come in as arguments so every branch is testable, and so the "did this
 * already fire today?" logic can be exercised without waiting for evening.
 *
 * ## The rule that shapes all of this
 *
 * SPEC.md §11: "encouraging, never nagging. She did not ask to be monitored." Concretely:
 *
 *  - At most one reminder per day, and only when the day still has unfinished work.
 *  - The reminder is *scheduled ahead* for the chosen time and **cancelled the moment the plan
 *    is finished** (ntfy's sequence id makes cancel/replace possible — see ntfy.ts). Without
 *    the cancel this feature would routinely tell her she is behind twenty minutes after she
 *    finished, which is exactly the "compliance report" §11 forbids.
 *  - If the chosen time has already passed when the app is opened, nothing is sent. A reminder
 *    that arrives after the moment it was meant to help is pure nagging.
 *  - The new-topic note fires once per topic, ever, and is a welcome not an instruction.
 */

export type NudgeAction =
  | { kind: 'publish'; message: NtfyMessage }
  | { kind: 'cancel'; sequenceId: string }

export interface NudgeDecision {
  actions: NudgeAction[]
  /** Merged into Settings.ntfyState by the caller after the actions succeed. */
  statePatch: NonNullable<Settings['ntfyState']> | null
}

export interface NudgeInput {
  settings: Settings
  /** Today's plan in Asia/Kolkata, or null if no plan exists for today. */
  todayPlan: PlanDay | null
  /** Asia/Kolkata date, 'YYYY-MM-DD'. */
  todayIso: string
  nowMs: number
  topicNameById: Map<string, string>
  /** Absolute URL the notification opens, e.g. https://user.github.io/ascent/ */
  appUrl: string
}

/** Stable per-day id so re-publishing replaces, and DELETE cancels. See ntfy.ts. */
export function dailySequenceId(dateIso: string): string {
  return `ascent-daily-${dateIso}`
}

/**
 * Converts 'YYYY-MM-DD' + 'HH:MM' understood as Asia/Kolkata into unix seconds.
 *
 * IST is UTC+5:30 with no daylight saving and no historical changes in any period this app
 * covers, so the fixed offset is exact here — unlike a generic timezone, where this shortcut
 * would be a bug. Doing it arithmetically avoids depending on the host's own timezone, which is
 * the whole point: the reminder must land at 9pm *her* time whatever device scheduled it.
 */
export function istToUnixSeconds(dateIso: string, timeHHMM: string): number | null {
  const dateMatch = /^(\d{4})-(\d{2})-(\d{2})$/.exec(dateIso)
  const timeMatch = /^(\d{2}):(\d{2})$/.exec(timeHHMM)
  if (!dateMatch || !timeMatch) return null
  const [, y, m, d] = dateMatch
  const [, hh, mm] = timeMatch
  const hours = Number(hh)
  const minutes = Number(mm)
  if (hours > 23 || minutes > 59) return null
  const utcMs = Date.UTC(Number(y), Number(m) - 1, Number(d), hours, minutes)
  return Math.round(utcMs / 1000) - 5.5 * 3600
}

function topicLabel(microTopicId: string, names: Map<string, string>): string {
  return names.get(microTopicId) ?? microTopicId
}

export function decideNudges(input: NudgeInput): NudgeDecision {
  const { settings, todayPlan, todayIso, nowMs, topicNameById, appUrl } = input
  const config = settings.ntfy
  const empty: NudgeDecision = { actions: [], statePatch: null }
  if (!config?.enabled || !config.topic) return empty

  const state = settings.ntfyState ?? { announcedTopics: [] }
  const actions: NudgeAction[] = []
  const patch: NonNullable<Settings['ntfyState']> = {
    announcedTopics: [...state.announcedTopics],
    lastScheduledSignature: state.lastScheduledSignature,
    lastCompletionDate: state.lastCompletionDate,
  }
  let changed = false

  const sequenceId = dailySequenceId(todayIso)
  const items = todayPlan?.items ?? []
  const unfinished = items.filter((item) => !item.done)

  // --- A topic the plan is introducing today, announced once, ever. ---------------------
  if (config.newTopicAlerts) {
    const announced = new Set(patch.announcedTopics)
    const fresh = items.filter((item) => item.kind === 'learn' && !announced.has(item.microTopicId))
    if (fresh.length > 0) {
      const names = fresh.map((item) => topicLabel(item.microTopicId, topicNameById))
      actions.push({
        kind: 'publish',
        message: {
          title: names.length === 1 ? 'New topic today' : 'New topics today',
          body:
            names.length === 1
              ? `${names[0]} — the lesson comes first, then the questions.`
              : `${names.join(', ')} — lessons first, then the questions.`,
          tags: ['books'],
          priority: 3,
          click: appUrl,
        },
      })
      for (const item of fresh) patch.announcedTopics.push(item.microTopicId)
      changed = true
    }
  }

  // --- The day's one reminder: schedule it, replace it, or cancel it. -------------------
  if (config.dailyGoalReminder) {
    if (items.length === 0) {
      // No plan for today means nothing to be behind on.
    } else if (unfinished.length === 0) {
      // Finished. Kill any pending reminder before it can fire, and say well done once.
      if (patch.lastScheduledSignature) {
        actions.push({ kind: 'cancel', sequenceId })
        patch.lastScheduledSignature = undefined
        changed = true
      }
      if (patch.lastCompletionDate !== todayIso) {
        actions.push({
          kind: 'publish',
          message: {
            title: "Today's plan is done",
            body: `All ${items.length} item${items.length === 1 ? '' : 's'} finished. Nothing else is owed today.`,
            tags: ['white_check_mark'],
            priority: 2,
            click: appUrl,
          },
        })
        patch.lastCompletionDate = todayIso
        changed = true
      }
    } else {
      const deliverAt = istToUnixSeconds(todayIso, config.reminderTime)
      // Already past the chosen time: say nothing. See the nagging rule above.
      if (deliverAt !== null && deliverAt * 1000 > nowMs) {
        const names = unfinished.map((item) => topicLabel(item.microTopicId, topicNameById))
        const body =
          `${unfinished.length} of ${items.length} left: ${names.slice(0, 3).join(', ')}` +
          (names.length > 3 ? ` and ${names.length - 3} more.` : '.')
        // Only re-publish when the content or the time actually moved. ntfy replaces rather
        // than duplicates, but there is no reason to hit the server on every app open.
        const signature = `${deliverAt}|${body}`
        if (signature !== patch.lastScheduledSignature) {
          actions.push({
            kind: 'publish',
            message: {
              title: "Still open today",
              body,
              tags: ['alarm_clock'],
              priority: 3,
              click: appUrl,
              deliverAt,
              sequenceId,
            },
          })
          patch.lastScheduledSignature = signature
          changed = true
        }
      }
    }
  }

  return { actions, statePatch: changed ? patch : null }
}
