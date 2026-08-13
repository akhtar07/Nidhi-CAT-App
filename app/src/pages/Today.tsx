import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { BookMarked, ChevronDown, ClipboardList, NotebookPen, Timer } from 'lucide-react'
import { Skeleton } from '@/components/ui/Skeleton'
import {
  loadExamMeta,
  loadLessonIndex,
  loadMockDefinition,
  loadMockIndex,
  loadPassageSetIndex,
  loadQuestionIndex,
  loadSyllabus,
  type PassageSetIndexEntry,
} from '@/content/loadContent'
import { daysBetween, todayIsoIST } from '@/planner/dateUtils'
import { summariseCoverage, type CoverageSummary } from '@/progress/sectionRollup'
import { buildTopicProgress } from '@/progress/topicProgress'
import { MOCK_SENTINEL, REVIEW_SENTINEL } from '@/planner/generatePlan'
import { showLocalNotification } from '@/pwa/notify'
import { storage } from '@/storage'
import { cn } from '@/lib/utils'
import type { MicroTopic } from '@/types/content'
import type { PlanDay, Settings as SettingsType } from '@/types/state'

interface TopicRow {
  topic: MicroTopic
  count: number
  hasLesson: boolean
}

interface MockRow {
  id: string
  title: string
  kind: 'full' | 'sectional'
  difficultyTier?: 'easier' | 'standard' | 'harder'
}

const DIFFICULTY_LABEL: Record<string, string> = {
  easier: 'Easier',
  standard: 'CAT level',
  harder: 'Harder',
}

const SECTIONS = [
  { key: 'qa', label: 'Quantitative Aptitude', short: 'QA' },
  { key: 'dilr', label: 'Data Interpretation & Logical Reasoning', short: 'DILR' },
  { key: 'varc', label: 'Verbal Ability & Reading Comprehension', short: 'VARC' },
] as const

function planItemLabel(microTopicId: string, topicNameById: Map<string, string>): string {
  if (microTopicId === MOCK_SENTINEL) return 'Mock test'
  if (microTopicId === REVIEW_SENTINEL) return 'Review / SRS'
  return topicNameById.get(microTopicId) ?? microTopicId
}

/**
 * Sets are identified as `<microTopicId>.set-<hash>`, so the topic name can be recovered by
 * finding the longest syllabus id the set id starts with. Without this every DI/LR set in the
 * list rendered as the literal string "DI set" — twenty-two indistinguishable rows, which made
 * the section useless for choosing what to practise.
 */
function setTopicName(setId: string, topicNameById: Map<string, string>): string | null {
  let best: string | null = null
  for (const [id, name] of topicNameById) {
    if (setId.startsWith(`${id}.`) && (best === null || id.length > best.length)) best = name
  }
  return best
}

function SectionGroup({
  label,
  short,
  rows,
  defaultOpen,
}: {
  label: string
  short: string
  rows: TopicRow[]
  defaultOpen: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  if (rows.length === 0) return null
  const totalQuestions = rows.reduce((sum, r) => sum + r.count, 0)

  return (
    <section className="overflow-hidden rounded-xl border border-border">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center justify-between gap-3 px-4 py-3 text-left hover:bg-muted/60"
      >
        <span className="min-w-0">
          <span className="block truncate text-sm font-medium">{label}</span>
          <span className="block text-xs text-muted-foreground">
            {rows.length} topics · {totalQuestions} questions
          </span>
        </span>
        <span className="flex shrink-0 items-center gap-2">
          <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">{short}</span>
          <ChevronDown className={cn('size-4 text-muted-foreground transition-transform', open && 'rotate-180')} />
        </span>
      </button>

      {open && (
        <ul className="divide-y divide-border border-t border-border">
          {rows.map(({ topic, count, hasLesson }) => (
            <li key={topic.id}>
              <Link
                to={`/lesson/${topic.id}`}
                className="flex items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-muted/60"
              >
                <span className="min-w-0">
                  <span className="block truncate">{topic.name}</span>
                  {hasLesson && <span className="text-xs text-primary">Lesson included</span>}
                </span>
                <span className="shrink-0 text-xs tabular-nums text-muted-foreground">{count} Qs</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </section>
  )
}

export function Today() {
  const navigate = useNavigate()
  const [rows, setRows] = useState<TopicRow[] | null>(null)
  const [sets, setSets] = useState<PassageSetIndexEntry[]>([])
  const [mocks, setMocks] = useState<MockRow[]>([])
  const [error, setError] = useState<string | null>(null)
  const [todayPlan, setTodayPlan] = useState<PlanDay | null>(null)
  const [topicNameById, setTopicNameById] = useState<Map<string, string>>(new Map())
  const [settings, setSettings] = useState<SettingsType | null>(null)
  const [daysToExam, setDaysToExam] = useState<number | null>(null)
  const [coverage, setCoverage] = useState<CoverageSummary | null>(null)
  const [showAllSets, setShowAllSets] = useState(false)

  useEffect(() => {
    storage
      .getSettings()
      .then((s) => {
        setSettings(s ?? null)
        if (!s?.diagnosticCompletedAt) navigate('/diagnostic', { replace: true })
      })
      .catch(() => undefined)
  }, [navigate])

  // SPEC.md §11 Phase 1: "In-app 'Today' card is the primary mechanism" for the daily nudge —
  // the local notification (notify.ts) is a same-session supplement, not a replacement, and
  // only ever fires once per Asia/Kolkata calendar day (todayIsoIST, not UTC — see dateUtils.ts).
  useEffect(() => {
    if (!settings?.notificationsEnabled || !todayPlan) return
    if (typeof Notification === 'undefined' || Notification.permission !== 'granted') return
    const today = todayIsoIST()
    if (settings.lastNudgeShownDate === today) return
    const firstUnfinished = todayPlan.items.find((item) => !item.done)
    if (!firstUnfinished) return
    const label = planItemLabel(firstUnfinished.microTopicId, topicNameById)
    void showLocalNotification('Today on Ascent', `${label} — ${todayPlan.items.length} item(s) planned today.`).then(
      () => {
        const updated = { ...settings, lastNudgeShownDate: today }
        setSettings(updated)
        void storage.putSettings(updated)
      },
    )
  }, [settings, todayPlan, topicNameById])

  useEffect(() => {
    Promise.all([loadSyllabus(), loadQuestionIndex(), loadLessonIndex(), loadPassageSetIndex()])
      .then(([syllabus, index, lessonTopicIds, passageSets]) => {
        const counts = new Map<string, number>()
        for (const entry of index) {
          for (const microTopicId of entry.microTopicIds) {
            counts.set(microTopicId, (counts.get(microTopicId) ?? 0) + 1)
          }
        }
        const lessonSet = new Set(lessonTopicIds)
        setRows(
          syllabus
            .map((topic) => ({ topic, count: counts.get(topic.id) ?? 0, hasLesson: lessonSet.has(topic.id) }))
            .filter((row) => row.count > 0)
            .sort((a, b) => b.count - a.count),
        )
        setSets(passageSets)
        setTopicNameById(new Map(syllabus.map((t) => [t.id, t.name])))
      })
      .catch((e: Error) => setError(e.message))

    storage
      .getPlanDay(todayIsoIST())
      .then((day) => setTodayPlan(day ?? null))
      .catch(() => undefined)

    // SPEC.md §4.1 asks the Today card for "A countdown: '112 days to CAT'". Settings override
    // the shipped exam date, matching Calendar.tsx's precedence.
    Promise.all([loadExamMeta(), storage.getSettings()])
      .then(([meta, s]) => setDaysToExam(daysBetween(todayIsoIST(), s?.examDate ?? meta.examDate)))
      .catch(() => undefined)

    // Same pure reduction the Progress page uses, so the two can never disagree.
    Promise.all([loadSyllabus(), storage.listAttempts(), storage.listMasteryStates()])
      .then(([syllabus, attempts, masteryStates]) =>
        setCoverage(summariseCoverage(buildTopicProgress(syllabus, attempts, masteryStates))),
      )
      .catch(() => undefined)

    loadMockIndex()
      .then((ids) => Promise.all(ids.map((id) => loadMockDefinition(id))))
      .then((defs) => {
        const sorted = [...defs].sort(
          (a, b) => Number(b.kind === 'full') - Number(a.kind === 'full') || a.id.localeCompare(b.id),
        )
        setMocks(sorted)
      })
      .catch(() => undefined)
  }, [])

  const bySection = useMemo(() => {
    const map = new Map<string, TopicRow[]>()
    for (const row of rows ?? []) {
      const key = row.topic.id.split('.')[0]
      map.set(key, [...(map.get(key) ?? []), row])
    }
    return map
  }, [rows])

  const coveragePct = coverage ? Math.round((coverage.started / coverage.totalTopics) * 100) : null
  const pendingToday = todayPlan?.items.filter((i) => !i.done).length ?? 0
  const visibleSets = showAllSets ? sets : sets.slice(0, 6)

  return (
    <main className="mx-auto min-h-svh max-w-2xl bg-background px-5 pb-24 pt-6 text-foreground">
      <header className="mb-5">
        <h1 className="text-xl font-semibold tracking-tight">Ascent</h1>
        <p className="text-sm text-muted-foreground">CAT 2026 preparation</p>
      </header>

      {/* Countdown and coverage: the two numbers that orient everything else. */}
      <section className="mb-5 rounded-xl border border-border bg-card p-4">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-3xl font-semibold tabular-nums leading-none">
              {daysToExam !== null ? Math.max(daysToExam, 0) : '—'}
            </p>
            <p className="mt-1 text-xs text-muted-foreground">days to CAT</p>
          </div>
          {coverage && (
            <div className="text-right">
              <p className="text-3xl font-semibold tabular-nums leading-none">
                {coverage.started}
                <span className="text-base text-muted-foreground">/{coverage.totalTopics}</span>
              </p>
              <p className="mt-1 text-xs text-muted-foreground">topics started</p>
            </div>
          )}
        </div>
        {coveragePct !== null && (
          <>
            <div className="mt-3 h-1.5 w-full overflow-hidden rounded-full bg-muted">
              <div className="h-full rounded-full bg-primary transition-all" style={{ width: `${coveragePct}%` }} />
            </div>
            <p className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
              <span>
                {coveragePct}% of the syllabus touched
                {coverage?.overallAccuracyPct !== null && <> · {coverage?.overallAccuracyPct}% accuracy</>}
              </span>
              <Link to="/progress" className="text-primary">
                Details
              </Link>
            </p>
          </>
        )}
      </section>

      {/* Today's plan sits above the browse list: it is the answer to "what now?". */}
      <section className="mb-5 rounded-xl border border-border bg-card p-4">
        <h2 className="mb-2 flex items-center gap-2 text-sm font-medium">
          <ClipboardList className="size-4 text-primary" aria-hidden />
          Today&apos;s plan
        </h2>
        {todayPlan && todayPlan.items.length > 0 ? (
          <>
            <ul className="space-y-1.5 text-sm">
              {todayPlan.items.map((item, i) => (
                <li key={i} className="flex items-center justify-between gap-3">
                  <span className={cn('min-w-0 truncate', item.done && 'text-muted-foreground line-through')}>
                    <span className="text-muted-foreground">{item.kind}</span>{' '}
                    {planItemLabel(item.microTopicId, topicNameById)}
                  </span>
                  {item.microTopicId === MOCK_SENTINEL && mocks[0] ? (
                    <Link to={`/mock/${mocks[0].id}`} className="shrink-0 text-xs text-primary">
                      Start
                    </Link>
                  ) : item.microTopicId !== REVIEW_SENTINEL ? (
                    <Link to={`/lesson/${item.microTopicId}`} className="shrink-0 text-xs text-primary">
                      Start
                    </Link>
                  ) : (
                    <Link to="/review" className="shrink-0 text-xs text-primary">
                      Start
                    </Link>
                  )}
                </li>
              ))}
            </ul>
            {pendingToday > 0 && (
              <p className="mt-2.5 text-xs text-muted-foreground">{pendingToday} item(s) still to do today.</p>
            )}
          </>
        ) : (
          <p className="text-sm text-muted-foreground">
            No plan for today yet.{' '}
            <Link to="/calendar" className="text-primary">
              Open the planner
            </Link>{' '}
            to generate one, or just pick a topic below.
          </p>
        )}
      </section>

      {/* Shortcuts to the things that are otherwise buried. */}
      <nav aria-label="Shortcuts" className="mb-6 grid grid-cols-3 gap-2">
        {[
          { to: '/review', label: 'Review', Icon: NotebookPen },
          { to: '/mistakes', label: 'Mistakes', Icon: ClipboardList },
          { to: '/bookmarks', label: 'Bookmarks', Icon: BookMarked },
        ].map(({ to, label, Icon }) => (
          <Link
            key={to}
            to={to}
            className="flex flex-col items-center gap-1.5 rounded-xl border border-border bg-card px-2 py-3
                       text-xs hover:bg-muted/60"
          >
            <Icon className="size-4 text-primary" aria-hidden />
            {label}
          </Link>
        ))}
      </nav>

      {error && <p className="text-destructive">Failed to load content: {error}</p>}
      {!rows && !error && (
        <div className="space-y-3">
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
          <Skeleton className="h-16 w-full" />
        </div>
      )}

      {rows && rows.length === 0 && (
        <p className="text-sm text-muted-foreground">
          No drillable topics found. If you just set this up, the content bundle may not have synced yet — try
          reloading.
        </p>
      )}

      {rows && rows.length > 0 && (
        <>
          <h2 className="mb-2 text-sm font-medium">Browse by section</h2>
          <p className="mb-3 text-xs text-muted-foreground">
            Every topic opens with a short lesson before its questions.
          </p>
          <div className="space-y-2.5">
            {SECTIONS.map(({ key, label, short }, i) => (
              <SectionGroup
                key={key}
                label={label}
                short={short}
                rows={bySection.get(key) ?? []}
                defaultOpen={i === 0}
              />
            ))}
          </div>
        </>
      )}

      {sets.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-2 flex items-center gap-2 text-sm font-medium">
            <Timer className="size-4 text-primary" aria-hidden />
            Timed sets
          </h2>
          <ul className="divide-y divide-border overflow-hidden rounded-xl border border-border">
            {visibleSets.map((set) => {
              const topicName = setTopicName(set.id, topicNameById)
              const kindLabel = set.kind === 'di_set' ? 'DI' : set.kind === 'lr_set' ? 'LR' : 'RC'
              return (
                <li key={set.id}>
                  <Link
                    to={`/set/${set.id}`}
                    className="flex items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-muted/60"
                  >
                    <span className="min-w-0">
                      <span className="block truncate">{topicName ?? `${kindLabel} set`}</span>
                      <span className="text-xs text-muted-foreground">
                        {kindLabel} · {set.questionIds.length} questions · {set.targetMinutes} min
                      </span>
                    </span>
                  </Link>
                </li>
              )
            })}
          </ul>
          {sets.length > 6 && (
            <button
              type="button"
              onClick={() => setShowAllSets((v) => !v)}
              className="mt-2 text-xs text-primary"
            >
              {showAllSets ? 'Show fewer' : `Show all ${sets.length} sets`}
            </button>
          )}
        </section>
      )}

      {mocks.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-2 text-sm font-medium">Mock tests</h2>
          <ul className="divide-y divide-border overflow-hidden rounded-xl border border-border">
            {mocks.map((mock) => (
              <li key={mock.id}>
                <Link
                  to={`/mock/${mock.id}`}
                  className="flex items-center justify-between gap-3 px-4 py-3 text-sm hover:bg-muted/60"
                >
                  <span className="min-w-0">
                    <span className="block truncate">{mock.title}</span>
                    <span className="text-xs text-muted-foreground">
                      {mock.kind === 'full' ? 'Full mock' : 'Sectional'}
                    </span>
                  </span>
                  {mock.difficultyTier && (
                    <span className="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[11px] text-muted-foreground">
                      {DIFFICULTY_LABEL[mock.difficultyTier]}
                    </span>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  )
}
