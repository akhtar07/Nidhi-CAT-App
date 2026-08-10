import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useSupabaseAuth } from '@/auth/useSupabaseAuth'
import { Button } from '@/components/ui/button'
import { isNotificationSupported, requestNotificationPermission, showLocalNotification } from '@/pwa/notify'
import { useInstallPrompt } from '@/pwa/useInstallPrompt'
import { flushSyncQueue, storage } from '@/storage'
import type { Section, Settings as SettingsType } from '@/types/state'

const SECTIONS: Section[] = ['VARC', 'DILR', 'QA']

/**
 * SPEC.md §5.2: "Ship an Export / Import JSON button in Settings before
 * Milestone 5 — if IndexedDB is cleared, all her work vanishes." Export/
 * import shipped in Milestone 5; the dailyMinutes/examDate/weakSectionBias
 * fields (set once by the Milestone 9 diagnostic) are editable here since
 * this is the natural place to adjust them afterward.
 */
export function Settings() {
  const [status, setStatus] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [planSettings, setPlanSettings] = useState<SettingsType | null>(null)
  const [planStatus, setPlanStatus] = useState<string | null>(null)
  const [notificationStatus, setNotificationStatus] = useState<string | null>(null)
  const [notificationsSupported, setNotificationsSupported] = useState(false)
  const { canInstall, installed, promptInstall } = useInstallPrompt()
  const { configured: syncConfigured, email: syncedEmail, loading: authLoading, sendMagicLink, signOut } = useSupabaseAuth()
  const [syncEmailInput, setSyncEmailInput] = useState('')
  const [syncStatus, setSyncStatus] = useState<string | null>(null)
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    storage
      .getSettings()
      .then((s) => setPlanSettings(s ?? null))
      .catch(() => undefined)
    void isNotificationSupported().then(setNotificationsSupported)
  }, [])

  async function toggleNotifications(enabled: boolean) {
    if (!planSettings) return
    if (enabled) {
      const permission = await requestNotificationPermission()
      if (permission !== 'granted') {
        setNotificationStatus(
          permission === 'denied'
            ? 'Notifications are blocked in your browser settings — enable them there first.'
            : 'Permission not granted.',
        )
        return
      }
    }
    const updated = { ...planSettings, notificationsEnabled: enabled }
    setPlanSettings(updated)
    await storage.putSettings(updated)
    setNotificationStatus(enabled ? 'Daily reminders on.' : 'Daily reminders off.')
  }

  async function sendTestNotification() {
    await showLocalNotification('Ascent', "This is what your daily reminder will look like — you're all set.")
    setNotificationStatus('Test notification sent.')
  }

  async function savePlanSettings() {
    if (!planSettings) return
    await storage.putSettings(planSettings)
    setPlanStatus('Saved. Use "Regenerate plan" on the Calendar page to apply this to upcoming days.')
  }

  async function handleExport() {
    const bundle = await storage.exportAll()
    const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ascent-backup-${new Date().toISOString().slice(0, 10)}.json`
    a.click()
    URL.revokeObjectURL(url)
    setStatus('Exported.')
  }

  async function handleSendMagicLink() {
    setSyncStatus('Sending...')
    const { error } = await sendMagicLink(syncEmailInput)
    setSyncStatus(error ?? 'Check your email for a sign-in link.')
  }

  async function handleSyncNow() {
    setSyncing(true)
    const result = await flushSyncQueue()
    setSyncing(false)
    setSyncStatus(result.error ? `Sync failed: ${result.error}` : `Synced ${result.flushed} change(s).`)
  }

  async function handleImportFile(file: File) {
    try {
      const text = await file.text()
      const bundle = JSON.parse(text)
      await storage.importAll(bundle)
      setStatus('Imported — this replaced all existing local data.')
    } catch (e) {
      setStatus(`Import failed: ${(e as Error).message}`)
    }
  }

  return (
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <div>
        <Link to="/" className="text-sm text-primary underline">
          Back
        </Link>
        <h1 className="mt-2 text-2xl font-semibold">Settings</h1>
      </div>

      {planSettings && (
        <section className="space-y-3">
          <h2 className="font-medium">Plan</h2>
          <label className="block text-sm">
            <span className="mb-1 block font-medium">Minutes you can study per day</span>
            <input
              type="number"
              min={15}
              step={5}
              value={planSettings.dailyMinutes}
              onChange={(e) => setPlanSettings({ ...planSettings, dailyMinutes: Number(e.target.value) })}
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block font-medium">Exam date</span>
            <input
              type="date"
              value={planSettings.examDate}
              onChange={(e) => setPlanSettings({ ...planSettings, examDate: e.target.value })}
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block font-medium">Weak section (optional bias)</span>
            <select
              value={planSettings.weakSectionBias ?? ''}
              onChange={(e) =>
                setPlanSettings({ ...planSettings, weakSectionBias: (e.target.value || null) as Section | null })
              }
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
            >
              <option value="">None</option>
              {SECTIONS.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <Button onClick={() => void savePlanSettings()}>Save</Button>
          {planStatus && <p className="text-sm text-muted-foreground">{planStatus}</p>}
        </section>
      )}

      <section className="space-y-2">
        <h2 className="font-medium">Backup</h2>
        <p className="text-sm text-muted-foreground">
          All progress lives only in this browser. Export regularly — clearing site data or switching devices
          loses everything otherwise.
        </p>
        <div className="flex gap-2">
          <Button onClick={() => void handleExport()}>Export JSON</Button>
          <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
            Import JSON
          </Button>
          <input
            ref={fileInputRef}
            type="file"
            accept="application/json"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0]
              if (file) void handleImportFile(file)
              e.target.value = ''
            }}
          />
        </div>
        {status && <p className="text-sm text-muted-foreground">{status}</p>}
      </section>

      <section className="space-y-2">
        <h2 className="font-medium">Sync across devices</h2>
        {!syncConfigured ? (
          <p className="text-sm text-muted-foreground">
            Not set up yet — this build doesn't have a Supabase project configured, so progress stays on this
            device only. Export/Import above is the only backup for now.
          </p>
        ) : authLoading ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : syncedEmail ? (
          <>
            <p className="text-sm text-muted-foreground">Signed in as {syncedEmail}.</p>
            <div className="flex gap-2">
              <Button size="sm" onClick={() => void handleSyncNow()} disabled={syncing}>
                {syncing ? 'Syncing…' : 'Sync now'}
              </Button>
              <Button size="sm" variant="outline" onClick={() => void signOut()}>
                Sign out
              </Button>
            </div>
          </>
        ) : (
          <>
            <p className="text-sm text-muted-foreground">
              Sign in with a magic link to back up progress and pick up where you left off on another device.
            </p>
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="you@example.com"
                value={syncEmailInput}
                onChange={(e) => setSyncEmailInput(e.target.value)}
                className="min-w-0 flex-1 rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              />
              <Button onClick={() => void handleSendMagicLink()} disabled={!syncEmailInput}>
                Send link
              </Button>
            </div>
          </>
        )}
        {syncStatus && <p className="text-sm text-muted-foreground">{syncStatus}</p>}
      </section>

      <section className="space-y-2">
        <h2 className="font-medium">Install app</h2>
        {installed ? (
          <p className="text-sm text-muted-foreground">Installed — Ascent runs as its own app from here on.</p>
        ) : canInstall ? (
          <>
            <p className="text-sm text-muted-foreground">
              Install Ascent for offline access and a normal app icon, no browser chrome.
            </p>
            <Button onClick={() => void promptInstall()}>Install Ascent</Button>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">
            Not available right now — either it's already installed, or your browser doesn't support an in-page
            install prompt (Safari/iOS: use Share → Add to Home Screen instead).
          </p>
        )}
      </section>

      {planSettings && (
        <section className="space-y-2">
          <h2 className="font-medium">Notifications</h2>
          <p className="text-sm text-muted-foreground">
            A daily reminder of today's plan, shown while the app is open — never more than one a day, and always
            off unless you turn it on.
          </p>
          {notificationsSupported ? (
            <>
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={planSettings.notificationsEnabled ?? false}
                  onChange={(e) => void toggleNotifications(e.target.checked)}
                />
                Daily reminder
              </label>
              {planSettings.notificationsEnabled && (
                <Button variant="outline" size="sm" onClick={() => void sendTestNotification()}>
                  Send test notification
                </Button>
              )}
            </>
          ) : (
            <p className="text-sm text-muted-foreground">Not supported in this browser.</p>
          )}
          {notificationStatus && <p className="text-sm text-muted-foreground">{notificationStatus}</p>}
        </section>
      )}
    </main>
  )
}
