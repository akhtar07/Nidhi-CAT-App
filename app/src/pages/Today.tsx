import { useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  BookMarked,
  ChevronDown,
  ChevronRight,
  ClipboardList,
  NotebookPen,
  Search as SearchIcon,
  SlidersHorizontal,
  Sparkles,
  Timer,
} from 'lucide-react'
import { Card, CardHeading } from '@/components/ui/Card'
import { Skeleton } from '@/components/ui/Skeleton'
import { Meter, StatusChip } from '@/components/ui/StatusChip'
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
import { buildTopicProgress, type ProgressStatus, type TopicProgressRow } from '@/progress/topicProgress'
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

/** A topic row joined with where the learner actually stands on it. */
interface TopicRowWithProgress extends TopicRow {
  status: ProgressStatus
  accuracyPct: number | null
  attempts: number
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

/**
 * One section of the syllabus, collapsed to a single summary row until opened.
 *
 * Collapsed by default, all three. The previous version opened QA on load, which put 44
 * near-identical rows on screen before anything else — the learner had to scroll past the
 * entire Quantitative syllabus to discover that timed sets and mocks existed at all. Closed,
 * the whole of "browse" is three rows and everything below it is reachable.
 *
 * The summary line carries a progress meter rather than only a question count, so the closed
 * state still answers "how far into QA am I?" — which is the question that makes someone open
 * it in the first place.
 */
function SectionGroup({
  label,
  short,
  rows,
  defaultOpen,
}: {
  label: string
  short: string
  rows: TopicRowWithProgress[]
  defaultOpen: boolean
}) {
  const [open, setOpen] = useState(defaultOpen)
  if (rows.length === 0) return null
  const totalQuestions = rows.reduce((sum, r) => sum + r.count, 0)
  const started = rows.filter((r) => r.status !== 'untouched' && r.status !== 'locked').length

  return (
    <Card variant="quiet" className="overflow-hidden">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
        className="flex w-full items-center gap-3 px-4 py-3 text-left transition-colors hover:bg-secondary/50"
      >
        <span className="min-w-0 flex-1">
          <span className="flex items-center gap-2">
            <span className="truncate text-sm font-medium">{label}</span>
            <span className="shrink-0 rounded-full bg-secondary px-1.5 py-0.5 text-[10px] text-muted-foreground">
              {short}
            </span>
          </span>
          <span className="mt-1 block text-xs text-muted-foreground">
            {started} of {rows.length} started · {totalQuestions} questions
          </span>
          <Meter value={started} max={rows.length} label={`${label} progress`} className="mt-2" />
        </span>
        <ChevronDown
          className={cn('size-4 shrink-0 text-muted-foreground transition-transform', open && 'rotate-180')}
          aria-hidden
        />
      </button>

      {open && (
        <ul className="divide-y divide-border border-t border-border">
          {rows.map(({ topic, count, status, accuracyPct }) => (
            <li key={topic.id}>
              <Link
                to={`/lesson/${topic.id}`}
                className="flex items-center gap-3 px-4 py-3 text-sm transition-colors hover:bg-secondary/50"
              >
                <span className="min-w-0 flex-1">
                  <span className="block truncate">{topic.name}</span>
                  <span className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1">
                    <StatusChip status={status} />
                    <span className="text-xs text-muted-foreground">
                      {count} questions
                      {accuracyPct !== null && <> · {accuracyPct}% correct</>}
                    </span>
                  </span>
                </span>
                <ChevronRight className="size-4 shrink-0 text-muted-foreground" aria-hidden />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </Card>
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
  const [progressByTopic, setProgressByTopic] = useState<Map<string, TopicProgressRow>>(new Map())
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

    // Same pure reduction the Progress page uses, so the two can never disagree. The per-topic
    // rows are kept as well as the rolled-up summary, so each browse row can show its own state
    // instead of the identical "Lesson included" label every topic used to carry.
    Promise.all([loadSyllabus(), storage.listAttempts(), storage.listMasteryStates()])
      .then(([syllabus, attempts, masteryStates]) => {
        const progress = buildTopicProgress(syllabus, attempts, masteryStates)
        setCoverage(summariseCoverage(progress))
        setProgressByTopic(new Map(progress.map((row) => [row.microTopicId, row])))
      })
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
    const map = new Map<string, TopicRowWithProgress[]>()
    for (const row of rows ?? []) {
      const key = row.topic.id.split('.')[0]
      const progress = progressByTopic.get(row.topic.id)
      const withProgress: TopicRowWithProgress = {
        ...row,
        status: progress?.status ?? 'untouched',
        accuracyPct: progress?.accuracyPct ?? null,
        attempts: progress?.attempts ?? 0,
      }
      map.set(key, [...(map.get(key) ?? []), withProgress])
    }
    return map
  }, [rows, progressByTopic])

  const coveragePct = coverage ? Math.round((coverage.started / coverage.totalTopics) * 100) : null
  const pendingToday = todayPlan?.items.filter((i) => !i.done).length ?? 0
  const visibleSets = showAllSets ? sets : sets.slice(0, 6)

  /**
   * The one thing to do next when there is no plan for today. A learner opening the app to a
   * "no plan yet" card and a list of 86 topics has been handed a research task, not a study
   * session; this picks the highest-ROI topic she has not started.
   */
  const suggestedTopic = useMemo(() => {
    if (!rows || rows.length === 0) return null
    const candidates = rows
      .map((row) => ({ row, progress: progressByTopic.get(row.topic.id) }))
      .filter(({ progress }) => !progress || progress.status === 'untouched')
      .sort((a, b) => (b.row.topic.roiScore ?? 0) - (a.row.topic.roiScore ?? 0) || b.row.count - a.row.count)
    return candidates[0]?.row ?? null
  }, [rows, progressByTopic])

  return (
    <main className="mx-auto min-h-svh max-w-2xl bg-background px-5 pb-24 pt-6 text-foreground">
      <header className="mb-5">
        <h1 className="text-xl font-semibold tracking-tight">Ascent</h1>
        <p className="text-sm text-muted-foreground">CAT 2026 preparation</p>
      </header>

      {/* Countdown and coverage: the two numbers that orient everything else. */}
      <Card variant="accent" className="mb-5 p-4">
        <div className="flex items-end justify-between gap-4">
          <div>
            <p className="text-4xl font-semibold leading-none">
              {daysToExam !== null ? Math.max(daysToExam, 0) : '—'}
            </p>
            <p className="mt-1.5 text-xs text-muted-foreground">days to CAT</p>
          </div>
          {coverage && (
            <div className="text-right">
              <p className="text-4xl font-semibold leading-none">
                {coverage.started}
                <span className="text-lg text-muted-foreground">/{coverage.totalTopics}</span>
              </p>
              <p className="mt-1.5 text-xs text-muted-foreground">topics started</p>
            </div>
          )}
        </div>
        {coveragePct !== null && (
          <>
            <Meter value={coveragePct} label="Syllabus coverage" className="mt-4" />
            <p className="mt-2.5 flex items-center justify-between gap-3 text-xs text-muted-foreground">
              <span>
                {coveragePct}% of the syllabus touched
                {coverage?.overallAccuracyPct !== null && <> · {coverage?.overallAccuracyPct}% accuracy</>}
              </span>
              <Link to="/progress" className="shrink-0 font-medium text-primary hover:underline">
                Details
              </Link>
            </p>
          </>
        )}
      </Card>

      {/* Today's plan sits above the browse list: it is the answer to "what now?". */}
      <Card className="mb-5 p-4">
        <CardHeading
          title={
            <span className="flex items-center gap-2">
              <ClipboardList className="size-4 text-primary" aria-hidden />
              Today&apos;s plan
            </span>
          }
          action={
            todayPlan && todayPlan.items.length > 0 ? (
              <span className="text-xs text-muted-foreground">
                {todayPlan.items.length - pendingToday}/{todayPlan.items.length} done
              </span>
            ) : undefined
          }
          className="mb-3"
        />
        {todayPlan && todayPlan.items.length > 0 ? (
          <ul className="space-y-1">
            {todayPlan.items.map((item, i) => {
              const to =
                item.microTopicId === MOCK_SENTINEL && mocks[0]
                  ? `/mock/${mocks[0].id}`
                  : item.microTopicId === REVIEW_SENTINEL
                    ? '/review'
                    : `/lesson/${item.microTopicId}`
              return (
                <li key={i}>
                  <Link
                    to={to}
                    className="-mx-2 flex items-center gap-3 rounded-lg px-2 py-2 transition-colors hover:bg-secondary/50"
                  >
                    {/* A filled dot rather than a checkbox: this reports state, it does not take
                        input — a plan item is completed by doing it, not by ticking it. */}
                    <span
                      aria-hidden
                      className={cn(
                        'size-2 shrink-0 rounded-full',
                        item.done ? 'bg-primary' : 'bg-transparent ring-1 ring-muted-foreground/50',
                      )}
                    />
                    <span className="min-w-0 flex-1">
                      <span className={cn('block truncate text-sm', item.done && 'text-muted-foreground line-through')}>
                        {planItemLabel(item.microTopicId, topicNameById)}
                      </span>
                      <span className="text-xs capitalize text-muted-foreground">{item.kind}</span>
                    </span>
                    {!item.done && <span className="shrink-0 text-xs font-medium text-primary">Start</span>}
                  </Link>
                </li>
              )
            })}
          </ul>
        ) : suggestedTopic ? (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              No plan for today yet.{' '}
              <Link to="/calendar" className="font-medium text-primary hover:underline">
                Build one
              </Link>{' '}
              — or just start here:
            </p>
            <Link
              to={`/lesson/${suggestedTopic.topic.id}`}
              className="flex items-center gap-3 rounded-lg bg-secondary/60 px-3 py-2.5 transition-colors hover:bg-secondary"
            >
              <Sparkles className="size-4 shrink-0 text-primary" aria-hidden />
              <span className="min-w-0 flex-1">
                <span className="block truncate text-sm font-medium">{suggestedTopic.topic.name}</span>
                <span className="text-xs text-muted-foreground">
                  High return · {suggestedTopic.count} questions
                </span>
              </span>
              <ChevronRight className="size-4 shrink-0 text-muted-foreground" aria-hidden />
            </Link>
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">
            No plan for today yet.{' '}
            <Link to="/calendar" className="font-medium text-primary hover:underline">
              Open the planner
            </Link>{' '}
            to generate one, or pick a topic below.
          </p>
        )}
      </Card>

      {/* Shortcuts. Practice, Formulas and Search live only here — they have no nav tab, and
          without this row the practice builder and the 188-card formula hub are unreachable
          except by typing a URL. */}
      <nav aria-label="Shortcuts" className="mb-6 grid grid-cols-3 gap-2">
        {[
          { to: '/practice/new', label: 'Practice', Icon: SlidersHorizontal },
          { to: '/revision', label: 'Formulas', Icon: NotebookPen },
          { to: '/mistakes', label: 'Mistakes', Icon: ClipboardList },
          { to: '/bookmarks', label: 'Bookmarks', Icon: BookMarked },
          { to: '/search', label: 'Search', Icon: SearchIcon },
          { to: '/calendar', label: 'Planner', Icon: Timer },
        ].map(({ to, label, Icon }) => (
          <Link
            key={to}
            to={to}
            className="flex flex-col items-center gap-1.5 rounded-xl border border-border bg-card px-2 py-3
                       text-xs shadow-sm transition-colors hover:bg-secondary/50"
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
          <h2 className="eyebrow mb-1">Browse by section</h2>
          <p className="mb-3 text-xs text-muted-foreground">
            Every topic opens with its lesson before the questions.
          </p>
          <div className="space-y-2.5">
            {SECTIONS.map(({ key, label, short }) => (
              <SectionGroup
                key={key}
                label={label}
                short={short}
                rows={bySection.get(key) ?? []}
                defaultOpen={false}
              />
            ))}
          </div>
        </>
      )}

      {sets.length > 0 && (
        <section className="mt-6">
          <h2 className="eyebrow mb-2 flex items-center gap-1.5">
            <Timer className="size-3.5" aria-hidden />
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
          <h2 className="eyebrow mb-2">Mock tests</h2>
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
