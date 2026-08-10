// Milestone 16 (SPEC.md §11 Phase 2 / §12 option B). Deno Edge Function, deployed with the
// Supabase CLI (`supabase functions deploy daily-nudge`) — NOT part of the Vite app's build or
// CI (a completely separate runtime). Triggered once a day by .github/workflows/
// daily-nudge-cron.yml via SPEC.md §11's exact cron expression.
//
// Reads every opted-in user's synced Settings/PlanDay/MasteryState rows, picks at most one
// email per user via selectEmailForToday (../functions/_shared/selectEmail.js), and sends it
// through Resend. The (user_id, sent_date) primary key on email_log is the actual hard stop
// against ever sending two emails to the same user on the same day — this function's own
// pre-check is a courtesy (avoids a wasted Resend call), not the enforcement mechanism.
//
// Never runs with the anon key: SUPABASE_SERVICE_ROLE_KEY and RESEND_API_KEY are Edge Function
// secrets (`supabase secrets set ...`), set once outside this repo — never committed, never
// shipped to the browser. This file is inert (nothing to run) until a real Supabase project and
// those secrets exist; see PROGRESS.md's Milestone 16 setup steps.

import { createClient } from 'jsr:@supabase/supabase-js@2'
import { selectEmailForToday } from '../_shared/selectEmail.js'

const SUPABASE_URL = Deno.env.get('SUPABASE_URL')!
const SERVICE_ROLE_KEY = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
const RESEND_API_KEY = Deno.env.get('RESEND_API_KEY')!
const CRON_SECRET = Deno.env.get('CRON_SECRET')!
const APP_URL = Deno.env.get('APP_URL') ?? 'https://akhtar07.github.io/Nidhi-CAT-App/'
const MILESTONE_DAYS = new Set([100, 50, 30, 14, 7, 1])

function todayIsoIST(): string {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata' }).format(new Date())
}

function isSundayIST(): boolean {
  const weekday = new Intl.DateTimeFormat('en-US', { timeZone: 'Asia/Kolkata', weekday: 'short' }).format(new Date())
  return weekday === 'Sun'
}

function daysUntil(examDateIso: string): number {
  const today = new Date(`${todayIsoIST()}T00:00:00Z`)
  const exam = new Date(`${examDateIso}T00:00:00Z`)
  return Math.round((exam.getTime() - today.getTime()) / (24 * 60 * 60 * 1000))
}

async function sendViaResend(to: string, email: { subject: string; text: string; html: string }) {
  const res = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: 'Ascent <ascent@resend.dev>', // replace with a verified sending domain once one exists
      to,
      subject: email.subject,
      text: email.text,
      html: email.html,
    }),
  })
  if (!res.ok) throw new Error(`Resend ${res.status}: ${await res.text()}`)
}

Deno.serve(async (req) => {
  if (req.headers.get('x-cron-secret') !== CRON_SECRET) {
    return new Response('Unauthorized', { status: 401 })
  }

  const supabase = createClient(SUPABASE_URL, SERVICE_ROLE_KEY)
  const today = todayIsoIST()
  const sunday = isSundayIST()

  const { data: settingsRows, error: settingsError } = await supabase
    .from('settings')
    .select('user_id, exam_date, email_opt_in')
    .eq('email_opt_in', true)

  if (settingsError) return new Response(`settings query failed: ${settingsError.message}`, { status: 500 })

  let sent = 0
  let skipped = 0
  const errors: string[] = []

  for (const row of settingsRows ?? []) {
    try {
      const { data: alreadySent } = await supabase
        .from('email_log')
        .select('user_id')
        .eq('user_id', row.user_id)
        .eq('sent_date', today)
        .maybeSingle()
      if (alreadySent) {
        skipped++
        continue
      }

      const { data: authUser } = await supabase.auth.admin.getUserById(row.user_id)
      const email = authUser?.user?.email
      if (!email) {
        skipped++
        continue
      }

      const { data: planDay } = await supabase.from('plan_days').select('items').eq('user_id', row.user_id).eq('date', today).maybeSingle()
      const firstUndone = (planDay?.items as { microTopicId: string; done: boolean }[] | undefined)?.find((i) => !i.done)

      const chosen = selectEmailForToday({
        todayIsSundayIST: sunday,
        daysUntilExam: daysUntil(row.exam_date),
        recentlyMasteredTopic: null, // topic-complete detection needs a mastery-history query; deferred, see PROGRESS.md
        tomorrowHasMock: null, // same — needs tomorrow's plan_day read, deferred
        weeklyDigestData: null, // needs a week's worth of attempts aggregated; deferred
        todayPlanFirstItem: firstUndone ? { topicName: firstUndone.microTopicId, minutes: 30 } : null,
        appUrl: APP_URL,
      })

      if (!chosen) {
        skipped++
        continue
      }

      await sendViaResend(email, chosen)
      const { error: logError } = await supabase
        .from('email_log')
        .insert({ user_id: row.user_id, sent_date: today, email_type: chosen.type })
      if (logError) throw new Error(`email_log insert: ${logError.message}`)
      sent++
    } catch (e) {
      errors.push(`${row.user_id}: ${(e as Error).message}`)
    }
  }

  return new Response(JSON.stringify({ sent, skipped, errors }), {
    headers: { 'Content-Type': 'application/json' },
  })
})
