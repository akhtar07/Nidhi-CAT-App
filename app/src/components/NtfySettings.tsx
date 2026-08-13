import { useState } from 'react'
import { Check, Copy, RefreshCw, Smartphone } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { DEFAULT_NTFY_SERVER, isValidTopic, publish, suggestTopic } from '@/notify/ntfy'
import { storage } from '@/storage'
import type { Settings as SettingsType } from '@/types/state'

/**
 * Phone reminders that reach a closed app, via ntfy (see notify/ntfy.ts for the whole rationale).
 *
 * The setup copy carries two things it would be dishonest to leave out: that the topic name is
 * effectively the password, and that a reminder can only be scheduled while Ascent is open —
 * because the app has no server, the phone gets told about tonight when she opens the app
 * today. Both are real limits of a static build, and a learner who does not know them will
 * eventually be surprised by one.
 */

const DEFAULT_NTFY: NonNullable<SettingsType['ntfy']> = {
  enabled: false,
  topic: '',
  server: DEFAULT_NTFY_SERVER,
  reminderTime: '20:00',
  newTopicAlerts: true,
  dailyGoalReminder: true,
}

interface Props {
  settings: SettingsType
  onChange: (settings: SettingsType) => void
}

export function NtfySettings({ settings, onChange }: Props) {
  const config = settings.ntfy ?? DEFAULT_NTFY
  const [status, setStatus] = useState<string | null>(null)
  const [sending, setSending] = useState(false)
  const [copied, setCopied] = useState(false)

  async function update(patch: Partial<NonNullable<SettingsType['ntfy']>>) {
    const next = { ...settings, ntfy: { ...config, ...patch } }
    onChange(next)
    await storage.putSettings(next)
  }

  async function handleTest() {
    setSending(true)
    const result = await publish(
      { server: config.server, topic: config.topic },
      {
        title: 'Ascent',
        body: 'Reminders are working. This is what a nudge will look like.',
        tags: ['books'],
        priority: 3,
      },
    )
    setSending(false)
    setStatus(result.ok ? 'Sent — check your phone.' : `Could not send: ${result.error}`)
  }

  async function handleCopy() {
    await navigator.clipboard.writeText(`${config.server.replace(/\/+$/, '')}/${config.topic}`)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const topicValid = isValidTopic(config.topic)

  return (
    <section className="space-y-4">
      <div className="space-y-1">
        <h2 className="font-medium">Phone reminders</h2>
        <p className="text-sm text-muted-foreground">
          The browser reminder above only appears while Ascent is open. This one reaches your phone with the
          app closed, using the free{' '}
          <a href="https://ntfy.sh" target="_blank" rel="noreferrer" className="text-primary underline">
            ntfy
          </a>{' '}
          app — no account, no sign-up.
        </p>
      </div>

      <label className="flex items-center gap-2 text-sm">
        <input
          type="checkbox"
          checked={config.enabled}
          onChange={(e) => void update({ enabled: e.target.checked, topic: config.topic || suggestTopic() })}
        />
        Send reminders to my phone
      </label>

      {config.enabled && (
        <div className="space-y-4 rounded-lg border border-border p-4">
          <ol className="space-y-1 text-sm text-muted-foreground">
            <li>1. Install the ntfy app (Android, iOS) or open ntfy.sh in a browser.</li>
            <li>2. Subscribe to the topic below — copy it across exactly.</li>
            <li>3. Send yourself a test.</li>
          </ol>

          <label className="block text-sm">
            <span className="mb-1 block font-medium">Your topic</span>
            <div className="flex gap-2">
              <input
                type="text"
                value={config.topic}
                onChange={(e) => void update({ topic: e.target.value.trim() })}
                spellCheck={false}
                autoCapitalize="none"
                className="min-w-0 flex-1 rounded-lg border border-border bg-background px-3 py-2 font-mono text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              />
              <Button variant="outline" size="icon" aria-label="Generate a new topic" onClick={() => void update({ topic: suggestTopic() })}>
                <RefreshCw className="size-4" aria-hidden />
              </Button>
              <Button variant="outline" size="icon" aria-label="Copy topic URL" onClick={() => void handleCopy()}>
                {copied ? <Check className="size-4" aria-hidden /> : <Copy className="size-4" aria-hidden />}
              </Button>
            </div>
            <span className="mt-1.5 block text-xs text-muted-foreground">
              ntfy has no accounts, so this name is the only thing keeping your reminders private — anyone who
              guesses it can read them. Keep the generated one rather than picking something memorable.
            </span>
            {!topicValid && config.topic !== '' && (
              <span className="mt-1 block text-xs text-destructive">Letters, numbers, hyphens and underscores only.</span>
            )}
          </label>

          <div className="space-y-3">
            <label className="flex items-start gap-2 text-sm">
              <input
                type="checkbox"
                className="mt-1"
                checked={config.newTopicAlerts}
                onChange={(e) => void update({ newTopicAlerts: e.target.checked })}
              />
              <span>
                <span className="block">Tell me when a new topic starts</span>
                <span className="block text-xs text-muted-foreground">
                  Once per topic, the first time your plan introduces it.
                </span>
              </span>
            </label>

            <label className="flex items-start gap-2 text-sm">
              <input
                type="checkbox"
                className="mt-1"
                checked={config.dailyGoalReminder}
                onChange={(e) => void update({ dailyGoalReminder: e.target.checked })}
              />
              <span>
                <span className="block">Remind me if the day&rsquo;s plan is unfinished</span>
                <span className="block text-xs text-muted-foreground">
                  One reminder, at your chosen time — and it is cancelled the moment you finish, so it never
                  arrives after you are already done.
                </span>
              </span>
            </label>

            {config.dailyGoalReminder && (
              <label className="block text-sm">
                <span className="mb-1 block font-medium">Remind me at</span>
                <input
                  type="time"
                  value={config.reminderTime}
                  onChange={(e) => void update({ reminderTime: e.target.value })}
                  className="rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                />
                <span className="mt-1.5 block text-xs text-muted-foreground">
                  India time. Scheduled when you open Ascent earlier that day — Ascent has no server of its
                  own, so a day you never open it is a day it cannot remind you about.
                </span>
              </label>
            )}
          </div>

          <details className="text-sm">
            <summary className="cursor-pointer text-muted-foreground">Use a self-hosted ntfy server</summary>
            <label className="mt-2 block">
              <input
                type="url"
                value={config.server}
                onChange={(e) => void update({ server: e.target.value })}
                placeholder={DEFAULT_NTFY_SERVER}
                className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              />
            </label>
          </details>

          <div className="flex items-center gap-2">
            <Button size="sm" disabled={!topicValid || sending} onClick={() => void handleTest()}>
              <Smartphone className="size-4" aria-hidden />
              {sending ? 'Sending…' : 'Send test'}
            </Button>
            {status && <span className="text-sm text-muted-foreground">{status}</span>}
          </div>
        </div>
      )}
    </section>
  )
}
