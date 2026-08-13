import { useEffect, useMemo, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { QuestionPlayer } from '@/components/question-player/QuestionPlayer'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/lib/utils'
import {
  loadMicroTopic,
  loadQuestion,
  loadQuestionIndex,
  loadQuestionsForMicroTopic,
  loadSyllabus,
  type QuestionIndexEntry,
} from '@/content/loadContent'
import {
  ALL_DIFFICULTIES,
  ALL_SECTIONS,
  buildPracticeSet,
  describeSelection,
  makeRng,
  matchesFilters,
  type Difficulty,
  type PracticeFilters,
  type Section,
} from '@/practice/buildPracticeSet'
import { storage } from '@/storage'
import type { MicroTopic, Question } from '@/types/content'
import type { Attempt } from '@/types/state'

const COUNT_CHOICES = [5, 10, 15, 20, 30]
const TIME_CHOICES: (number | null)[] = [null, 5, 10, 20, 30]
const DIFFICULTY_LABELS: Record<Difficulty, string> = {
  easy: 'Easy',
  medium: 'Medium',
  hard: 'Hard',
  very_hard: 'Very hard',
}

/** A pill toggle — the same affordance the question player's error tags use. */
function Chip({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-pressed={active}
      className={cn(
        'rounded-full border px-3 py-1 text-xs transition-colors',
        active ? 'border-primary bg-primary/10 text-foreground' : 'border-border text-muted-foreground hover:bg-muted',
      )}
    >
      {children}
    </button>
  )
}

function toggle<T>(list: T[], value: T): T[] {
  return list.includes(value) ? list.filter((v) => v !== value) : [...list, value]
}

function formatClock(total: number): string {
  const m = Math.floor(total / 60)
  const s = total % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

interface RunningSession {
  questions: Question[]
  /** questionId -> the topic context QuestionPlayer needs to update the mastery engine. */
  contextByQuestionId: Map<string, { topic: MicroTopic; topicQuestions: Question[] }>
  timeLimitMinutes: number | null
}

type Phase = 'configure' | 'loading' | 'running' | 'done'

/**
 * Custom practice test builder: pick sections / topics / difficulty / length, and the app
 * assembles a set from the shipped bank and runs it through the normal QuestionPlayer.
 *
 * Attempts are recorded with `mode: 'topic_test'` — a real Attempt mode from SPEC.md §5.2,
 * distinct from 'drill' so the Progress dashboard's practice trends can tell a self-built
 * test apart from a scheduled drill, while both still count as practice (neither is 'mock').
 *
 * Mock-reserved questions cannot appear here: sync-content.mjs omits them from
 * questions/index.json entirely and this page selects only from that index.
 */
export function PracticeBuilder() {
  const [phase, setPhase] = useState<Phase>('configure')
  const [index, setIndex] = useState<QuestionIndexEntry[] | null>(null)
  const [syllabus, setSyllabus] = useState<MicroTopic[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [sections, setSections] = useState<Section[]>([])
  const [microTopicIds, setMicroTopicIds] = useState<string[]>([])
  const [difficulties, setDifficulties] = useState<Difficulty[]>([])
  const [count, setCount] = useState(10)
  const [timeLimitMinutes, setTimeLimitMinutes] = useState<number | null>(null)
  const [showTopicPicker, setShowTopicPicker] = useState(false)

  const [session, setSession] = useState<RunningSession | null>(null)
  const [current, setCurrent] = useState(0)
  const [results, setResults] = useState<Attempt[]>([])
  const [remainingSec, setRemainingSec] = useState<number | null>(null)
  const startedAtRef = useRef<number>(0)

  useEffect(() => {
    Promise.all([loadQuestionIndex(), loadSyllabus(), storage.getSettings()])
      .then(([idx, syl, settings]) => {
        setIndex(idx)
        setSyllabus(syl)
        const prefs = settings?.practiceBuilderPrefs
        if (prefs) {
          setSections(prefs.sections)
          setMicroTopicIds(prefs.microTopicIds)
          setDifficulties(prefs.difficulties)
          setCount(prefs.count)
          setTimeLimitMinutes(prefs.timeLimitMinutes)
        }
      })
      .catch((e: Error) => setError(e.message))
  }, [])

  const filters: PracticeFilters = useMemo(
    () => ({ sections, microTopicIds, difficulties, count }),
    [sections, microTopicIds, difficulties, count],
  )

  // A live preview of how many questions the current filters actually reach, so the learner
  // sees an impossible combination before pressing Start rather than after.
  const matchedCount = useMemo(
    () => (index ? index.filter((e) => matchesFilters(e, filters)).length : 0),
    [index, filters],
  )

  const topicsForPicker = useMemo(() => {
    if (!syllabus || !index) return []
    const withContent = new Set(index.flatMap((e) => e.microTopicIds))
    return syllabus.filter(
      (t) => withContent.has(t.id) && (sections.length === 0 || sections.includes(t.section)),
    )
  }, [syllabus, index, sections])

  // Countdown for an optional time limit. Wall-clock based off startedAtRef so a backgrounded
  // tab can't pause the clock (same reasoning as MockSession's sectionStartedAt).
  useEffect(() => {
    if (phase !== 'running' || !session?.timeLimitMinutes) return
    const totalSec = session.timeLimitMinutes * 60
    const tick = () => {
      const elapsed = Math.floor((Date.now() - startedAtRef.current) / 1000)
      const left = totalSec - elapsed
      setRemainingSec(Math.max(0, left))
      if (left <= 0) setPhase('done')
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [phase, session])

  async function start() {
    if (!index) return
    setPhase('loading')
    try {
      const selection = buildPracticeSet(index, filters, makeRng(Date.now()))
      if (selection.questionIds.length === 0) {
        setPhase('configure')
        return
      }
      const questions = await Promise.all(selection.questionIds.map(loadQuestion))

      // QuestionPlayer needs each question's topic and that topic's full question list to
      // update the mastery engine. Cache per topic so a 30-question set spanning 6 topics
      // does 6 loads, not 30.
      const topicIds = [...new Set(questions.map((q) => q.microTopicIds[0]))]
      const contexts = await Promise.all(
        topicIds.map(async (id) => {
          const [topic, topicQuestions] = await Promise.all([
            loadMicroTopic(id),
            loadQuestionsForMicroTopic(id),
          ])
          return [id, topic, topicQuestions] as const
        }),
      )
      const byTopicId = new Map(contexts.map(([id, topic, qs]) => [id, { topic, topicQuestions: qs }]))
      const contextByQuestionId = new Map<string, { topic: MicroTopic; topicQuestions: Question[] }>()
      for (const q of questions) {
        const ctx = byTopicId.get(q.microTopicIds[0])
        if (ctx?.topic) contextByQuestionId.set(q.id, { topic: ctx.topic, topicQuestions: ctx.topicQuestions })
      }

      void storage.getSettings().then((settings) => {
        if (!settings) return
        return storage.putSettings({
          ...settings,
          practiceBuilderPrefs: { sections, microTopicIds, difficulties, count, timeLimitMinutes },
        })
      })

      startedAtRef.current = Date.now()
      setSession({ questions, contextByQuestionId, timeLimitMinutes })
      setCurrent(0)
      setResults([])
      setRemainingSec(timeLimitMinutes ? timeLimitMinutes * 60 : null)
      setPhase('running')
    } catch (e) {
      setError((e as Error).message)
      setPhase('configure')
    }
  }

  function reset() {
    setSession(null)
    setCurrent(0)
    setResults([])
    setRemainingSec(null)
    setPhase('configure')
  }

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to build practice set: {error}</p>
        <Link to="/" className="text-primary underline">
          Back
        </Link>
      </main>
    )
  }

  if (!index || !syllabus) {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-10 w-full" />
      </main>
    )
  }

  if (phase === 'loading') {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6">
        <Skeleton className="h-6 w-40" />
        <Skeleton className="h-32 w-full" />
      </main>
    )
  }

  if (phase === 'running' && session) {
    if (current >= session.questions.length) {
      setPhase('done')
      return null
    }
    const q = session.questions[current]
    const ctx = session.contextByQuestionId.get(q.id)
    if (!ctx) {
      // A question whose topic is missing from the syllabus can't drive the mastery engine;
      // skip rather than crash, and let the run continue.
      setCurrent((i) => i + 1)
      return null
    }
    return (
      <div>
        <div className="mx-auto flex max-w-2xl items-center justify-between px-4 pt-4 text-sm text-muted-foreground">
          <span>
            Question {current + 1} of {session.questions.length}
          </span>
          <span className="flex items-center gap-3">
            {remainingSec !== null && (
              <span className={cn(remainingSec <= 60 && 'text-destructive')}>{formatClock(remainingSec)} left</span>
            )}
            <button type="button" onClick={() => setPhase('done')} className="underline hover:text-foreground">
              End
            </button>
          </span>
        </div>
        <QuestionPlayer
          key={q.id}
          question={q}
          mode="topic_test"
          topic={ctx.topic}
          topicQuestions={ctx.topicQuestions}
          onComplete={(attempt) => {
            setResults((r) => [...r, attempt])
            setCurrent((i) => i + 1)
          }}
        />
      </div>
    )
  }

  if (phase === 'done' && session) {
    const correct = results.filter((a) => a.correct).length
    const attempted = results.length
    const accuracy = attempted > 0 ? Math.round((correct / attempted) * 100) : 0
    const totalSec = results.reduce((s, a) => s + a.timeSpentSec, 0)
    const ranOut = session.timeLimitMinutes !== null && remainingSec === 0
    return (
      <main className="mx-auto max-w-2xl space-y-5 p-6">
        <div>
          <h1 className="text-2xl font-semibold">Practice test complete</h1>
          {ranOut && <p className="mt-1 text-sm text-destructive">Time ran out.</p>}
        </div>
        <div className="grid grid-cols-3 gap-3">
          {[
            ['Attempted', `${attempted}/${session.questions.length}`],
            ['Correct', `${correct}`],
            ['Accuracy', attempted > 0 ? `${accuracy}%` : '—'],
          ].map(([label, value]) => (
            <div key={label} className="rounded-lg border border-border p-3">
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="mt-1 text-xl font-semibold">{value}</p>
            </div>
          ))}
        </div>
        <p className="text-sm text-muted-foreground">
          {attempted > 0
            ? `Total time ${formatClock(totalSec)} · about ${Math.round(totalSec / attempted)}s per question.`
            : 'No questions were attempted in this run.'}
        </p>
        <div className="flex gap-2">
          <Button onClick={reset}>Build another</Button>
          <Link to="/progress">
            <Button variant="outline">See progress</Button>
          </Link>
        </div>
      </main>
    )
  }

  const previewSelection = buildPracticeSet(index, filters, makeRng(1))
  const canStart = matchedCount > 0

  return (
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <div>
        <Link to="/" className="text-sm text-primary underline">
          Back
        </Link>
        <h1 className="mt-2 text-2xl font-semibold">Build a practice test</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Choose what to practise and how long for. Leave a filter untouched to include everything in it.
        </p>
      </div>

      <section className="space-y-2">
        <h2 className="text-sm font-medium">Sections</h2>
        <div className="flex flex-wrap gap-2">
          {ALL_SECTIONS.map((s) => (
            <Chip
              key={s}
              active={sections.includes(s)}
              onClick={() => {
                setSections((prev) => toggle(prev, s))
                setMicroTopicIds([]) // topics belong to sections; a section change invalidates them
              }}
            >
              {s}
            </Chip>
          ))}
        </div>
      </section>

      <section className="space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-medium">
            Topics{' '}
            <span className="font-normal text-muted-foreground">
              {microTopicIds.length === 0 ? '(all)' : `(${microTopicIds.length} selected)`}
            </span>
          </h2>
          <div className="flex gap-2">
            {microTopicIds.length > 0 && (
              <Button size="xs" variant="ghost" onClick={() => setMicroTopicIds([])}>
                Clear
              </Button>
            )}
            <Button size="xs" variant="outline" onClick={() => setShowTopicPicker((v) => !v)}>
              {showTopicPicker ? 'Hide' : 'Choose topics'}
            </Button>
          </div>
        </div>
        {showTopicPicker && (
          <div className="max-h-64 space-y-1 overflow-y-auto rounded-lg border border-border p-2">
            {topicsForPicker.length === 0 ? (
              <p className="p-2 text-sm text-muted-foreground">No topics with questions in this section yet.</p>
            ) : (
              topicsForPicker.map((t) => (
                <label
                  key={t.id}
                  className="flex cursor-pointer items-center gap-2 rounded-md px-2 py-1.5 text-sm hover:bg-muted"
                >
                  <input
                    type="checkbox"
                    checked={microTopicIds.includes(t.id)}
                    onChange={() => setMicroTopicIds((prev) => toggle(prev, t.id))}
                  />
                  <span className="flex-1">{t.name}</span>
                  <span className="text-xs text-muted-foreground">{t.section}</span>
                </label>
              ))
            )}
          </div>
        )}
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-medium">Difficulty</h2>
        <div className="flex flex-wrap gap-2">
          {ALL_DIFFICULTIES.map((d) => (
            <Chip key={d} active={difficulties.includes(d)} onClick={() => setDifficulties((prev) => toggle(prev, d))}>
              {DIFFICULTY_LABELS[d]}
            </Chip>
          ))}
        </div>
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-medium">Number of questions</h2>
        <div className="flex flex-wrap gap-2">
          {COUNT_CHOICES.map((c) => (
            <Chip key={c} active={count === c} onClick={() => setCount(c)}>
              {c}
            </Chip>
          ))}
        </div>
      </section>

      <section className="space-y-2">
        <h2 className="text-sm font-medium">Time limit</h2>
        <div className="flex flex-wrap gap-2">
          {TIME_CHOICES.map((t) => (
            <Chip key={String(t)} active={timeLimitMinutes === t} onClick={() => setTimeLimitMinutes(t)}>
              {t === null ? 'No limit' : `${t} min`}
            </Chip>
          ))}
        </div>
      </section>

      <div className="rounded-lg border border-border p-4">
        <p className="text-sm">{describeSelection(previewSelection)}</p>
        {matchedCount > 0 && previewSelection.shortfall === 0 && (
          <p className="mt-1 text-xs text-muted-foreground">
            Difficulty mix:{' '}
            {ALL_DIFFICULTIES.filter((d) => previewSelection.byDifficulty[d] > 0)
              .map((d) => `${previewSelection.byDifficulty[d]} ${DIFFICULTY_LABELS[d].toLowerCase()}`)
              .join(' · ')}
          </p>
        )}
      </div>

      {canStart ? (
        <Button onClick={() => void start()} className="w-full">
          Start practice test
        </Button>
      ) : (
        <EmptyState
          title="Nothing matches these filters"
          description="No questions in the bank match this combination yet. Try widening the difficulty range, or clearing the topic selection."
        />
      )}
    </main>
  )
}
