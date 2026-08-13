import { useEffect, useMemo, useState } from 'react'
import { AlertTriangle, RotateCcw, Search } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { loadSyllabus } from '@/content/loadContent'
import { clearAllProgress, storage } from '@/storage'
import type { MicroTopic } from '@/types/content'
import type { Attempt, MasteryState } from '@/types/state'

/**
 * Destructive-actions panel: start a single topic over, or wipe everything.
 *
 * Two separate controls because they answer two different questions. "I half-learned Percentages
 * while I was tired and the accuracy number is now wrong about me" needs one topic cleared —
 * wiping the whole app to fix that is absurd, and until now it was the only option. "Hand this
 * to someone else / start the four months properly" needs the full wipe.
 *
 * Both are guarded, and the guard escalates with the blast radius: one topic takes a second
 * click, everything takes a typed word. Nothing here is undoable, so the copy says the count of
 * what is about to go rather than a vague "are you sure?".
 */

interface TopicWithProgress {
  topic: MicroTopic
  attempts: number
  status: MasteryState['status'] | null
}

function summarise(topic: TopicWithProgress): string {
  const bits: string[] = []
  if (topic.attempts > 0) bits.push(`${topic.attempts} attempt${topic.attempts === 1 ? '' : 's'}`)
  if (topic.status) bits.push(topic.status)
  return bits.join(' · ')
}

export function ResetProgress() {
  const [topics, setTopics] = useState<TopicWithProgress[] | null>(null)
  const [query, setQuery] = useState('')
  const [confirmingTopic, setConfirmingTopic] = useState<string | null>(null)
  const [confirmText, setConfirmText] = useState('')
  const [busy, setBusy] = useState(false)
  const [status, setStatus] = useState<string | null>(null)

  async function refresh() {
    const [syllabus, attempts, mastery] = await Promise.all([
      loadSyllabus(),
      storage.listAttempts(),
      storage.listMasteryStates(),
    ])
    const attemptsByTopic = new Map<string, number>()
    for (const attempt of attempts as Attempt[]) {
      for (const id of attempt.microTopicIds) {
        attemptsByTopic.set(id, (attemptsByTopic.get(id) ?? 0) + 1)
      }
    }
    const statusByTopic = new Map(mastery.map((m) => [m.microTopicId, m.status]))

    const withProgress = syllabus
      .map((topic) => ({
        topic,
        attempts: attemptsByTopic.get(topic.id) ?? 0,
        status: statusByTopic.get(topic.id) ?? null,
      }))
      // 'available' is what the planner marks a topic as when it merely becomes eligible — no
      // practice has happened, so it is not progress and listing it would bury the real rows.
      .filter((row) => row.attempts > 0 || (row.status !== null && row.status !== 'available' && row.status !== 'locked'))
      .sort((a, b) => b.attempts - a.attempts || a.topic.name.localeCompare(b.topic.name))

    setTopics(withProgress)
  }

  useEffect(() => {
    void refresh()
  }, [])

  const filtered = useMemo(() => {
    if (!topics) return []
    const q = query.trim().toLowerCase()
    if (!q) return topics
    return topics.filter(
      (row) => row.topic.name.toLowerCase().includes(q) || row.topic.section.toLowerCase().includes(q),
    )
  }, [topics, query])

  async function handleResetTopic(row: TopicWithProgress) {
    setBusy(true)
    await storage.resetMicroTopic(row.topic.id)
    setConfirmingTopic(null)
    await refresh()
    setBusy(false)
    setStatus(`${row.topic.name} reset — ${row.attempts} attempt${row.attempts === 1 ? '' : 's'} cleared.`)
  }

  async function handleResetEverything() {
    setBusy(true)
    const result = await clearAllProgress()
    setConfirmText('')
    await refresh()
    setBusy(false)
    if (result.error) {
      setStatus(`This device is wiped, but the synced copy could not be cleared: ${result.error}. Try again once you are online.`)
    } else if (result.remoteCleared) {
      setStatus('Everything cleared, on this device and in your synced account.')
    } else {
      setStatus('Everything cleared on this device.')
    }
  }

  const totalAttempts = topics?.reduce((sum, row) => sum + row.attempts, 0) ?? 0

  return (
    <section className="space-y-6">
      <div className="space-y-1">
        <h2 className="font-medium">Reset progress</h2>
        <p className="text-sm text-muted-foreground">
          Clearing a topic removes its attempts, its accuracy and mastery record, its review cards and its
          bookmarks. Your plan and your mock results are left alone — those are a record of days and sittings
          that really happened, not of what you currently know.
        </p>
      </div>

      <div className="space-y-3">
        <div className="flex items-center justify-between gap-3">
          <h3 className="text-sm font-medium">One topic at a time</h3>
          {topics && topics.length > 0 && (
            <span className="text-xs text-muted-foreground">
              {topics.length} with progress · {totalAttempts} attempts
            </span>
          )}
        </div>

        {topics === null ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : topics.length === 0 ? (
          <p className="rounded-lg border border-dashed border-border px-4 py-6 text-center text-sm text-muted-foreground">
            Nothing to reset — no topic has any recorded practice yet.
          </p>
        ) : (
          <>
            <label className="relative block">
              <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" aria-hidden />
              <input
                type="search"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Find a topic"
                aria-label="Find a topic to reset"
                className="w-full rounded-lg border border-border bg-background py-2 pl-9 pr-3 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
              />
            </label>

            <ul className="divide-y divide-border rounded-lg border border-border">
              {filtered.map((row) => (
                <li key={row.topic.id} className="flex flex-wrap items-center gap-3 px-3 py-2.5">
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm">{row.topic.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {row.topic.section} · {summarise(row)}
                    </p>
                  </div>
                  {confirmingTopic === row.topic.id ? (
                    <div className="flex items-center gap-2">
                      <Button
                        size="sm"
                        variant="destructive"
                        disabled={busy}
                        onClick={() => void handleResetTopic(row)}
                      >
                        Confirm reset
                      </Button>
                      <Button size="sm" variant="ghost" onClick={() => setConfirmingTopic(null)}>
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setStatus(null)
                        setConfirmingTopic(row.topic.id)
                      }}
                    >
                      <RotateCcw className="size-3.5" aria-hidden />
                      Reset
                    </Button>
                  )}
                </li>
              ))}
              {filtered.length === 0 && (
                <li className="px-3 py-6 text-center text-sm text-muted-foreground">No topic matches “{query}”.</li>
              )}
            </ul>
          </>
        )}
      </div>

      <div className="space-y-3 rounded-lg border border-destructive/40 bg-destructive/5 p-4">
        <div className="flex items-start gap-2">
          <AlertTriangle className="mt-0.5 size-4 shrink-0 text-destructive" aria-hidden />
          <div className="space-y-1">
            <h3 className="text-sm font-medium">Start completely over</h3>
            <p className="text-sm text-muted-foreground">
              Deletes every attempt, all mastery, the plan, mock results, review cards, bookmarks and your
              settings — on this device and, if you are signed in, in your synced account too. There is no undo.
              Export a backup first if there is any chance you want this back.
            </p>
          </div>
        </div>
        <label className="block text-sm">
          <span className="mb-1 block">
            Type <strong>RESET</strong> to enable the button
          </span>
          <input
            type="text"
            value={confirmText}
            onChange={(e) => setConfirmText(e.target.value)}
            autoComplete="off"
            className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
          />
        </label>
        <Button
          variant="destructive"
          disabled={confirmText.trim().toUpperCase() !== 'RESET' || busy}
          onClick={() => void handleResetEverything()}
        >
          {busy ? 'Clearing…' : 'Reset everything'}
        </Button>
      </div>

      {status && (
        <p role="status" className="text-sm text-muted-foreground">
          {status}
        </p>
      )}
    </section>
  )
}
