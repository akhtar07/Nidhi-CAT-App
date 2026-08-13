import { useEffect } from 'react'
import { loadSyllabus } from '@/content/loadContent'
import { todayIsoIST } from '@/planner/dateUtils'
import { storage } from '@/storage'
import { cancelScheduled, publish, type NtfyConfig } from './ntfy'
import { decideNudges } from './nudgePlan'

/**
 * Runs the reminder decision (nudgePlan.ts) against live state and performs whatever it asks
 * for. Mounted once, from App.tsx.
 *
 * Fires on mount and whenever the tab becomes visible again, rather than on a timer. The two
 * moments that matter are "she opened the app" (schedule or refresh this evening's reminder)
 * and "she came back after finishing a drill" (cancel it, because the plan is now done) — a
 * poll would add nothing and would keep hitting the network in a background tab.
 *
 * Everything here is best-effort and silent. A notification server being unreachable must never
 * surface as an error in a study session; Settings has an explicit "Send test" button for when
 * the learner actually wants to know whether the channel works.
 */
export function useNtfyNudges(): void {
  useEffect(() => {
    let cancelled = false

    async function run() {
      const settings = await storage.getSettings()
      if (cancelled || !settings?.ntfy?.enabled || !settings.ntfy.topic) return

      const todayIso = todayIsoIST()
      const [todayPlan, syllabus] = await Promise.all([storage.getPlanDay(todayIso), loadSyllabus()])
      if (cancelled) return

      const decision = decideNudges({
        settings,
        todayPlan: todayPlan ?? null,
        todayIso,
        nowMs: Date.now(),
        topicNameById: new Map(syllabus.map((t) => [t.id, t.name])),
        appUrl: new URL(import.meta.env.BASE_URL, window.location.origin).href,
      })
      if (decision.actions.length === 0) return

      const config: NtfyConfig = { server: settings.ntfy.server, topic: settings.ntfy.topic }
      let allOk = true
      for (const action of decision.actions) {
        if (action.kind === 'publish') {
          const result = await publish(config, action.message)
          if (!result.ok) allOk = false
        } else {
          await cancelScheduled(config, action.sequenceId)
        }
      }

      // Only record that a nudge went out if it actually went out. Persisting the bookkeeping
      // after a failed publish would mean the reminder is never retried on the next app open,
      // and the learner would silently get nothing.
      if (allOk && decision.statePatch && !cancelled) {
        const latest = await storage.getSettings()
        if (latest) await storage.putSettings({ ...latest, ntfyState: decision.statePatch })
      }
    }

    void run()

    const onVisible = () => {
      if (document.visibilityState === 'visible') void run()
    }
    document.addEventListener('visibilitychange', onVisible)
    return () => {
      cancelled = true
      document.removeEventListener('visibilitychange', onVisible)
    }
  }, [])
}
