import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import {
  loadLessonIndex,
  loadMockDefinition,
  loadMockIndex,
  loadPassageSetIndex,
  loadQuestionIndex,
  loadSyllabus,
  type PassageSetIndexEntry,
} from '@/content/loadContent'
import { MOCK_SENTINEL, REVIEW_SENTINEL } from '@/planner/generatePlan'
import { storage } from '@/storage'
import type { MicroTopic } from '@/types/content'
import type { PlanDay } from '@/types/state'

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

function planItemLabel(microTopicId: string, topicNameById: Map<string, string>): string {
  if (microTopicId === MOCK_SENTINEL) return 'Mock test'
  if (microTopicId === REVIEW_SENTINEL) return 'Review / SRS'
  return topicNameById.get(microTopicId) ?? microTopicId
}

export function Today() {
  const navigate = useNavigate()
  const [rows, setRows] = useState<TopicRow[] | null>(null)
  const [sets, setSets] = useState<PassageSetIndexEntry[]>([])
  const [mocks, setMocks] = useState<MockRow[]>([])
  const [error, setError] = useState<string | null>(null)
  const [todayPlan, setTodayPlan] = useState<PlanDay | null>(null)
  const [topicNameById, setTopicNameById] = useState<Map<string, string>>(new Map())

  useEffect(() => {
    storage
      .getSettings()
      .then((settings) => {
        if (!settings?.diagnosticCompletedAt) navigate('/diagnostic', { replace: true })
      })
      .catch(() => undefined)
  }, [navigate])

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
            .sort((a, b) => Number(b.hasLesson) - Number(a.hasLesson) || b.count - a.count),
        )
        setSets(passageSets)
        setTopicNameById(new Map(syllabus.map((t) => [t.id, t.name])))
      })
      .catch((e: Error) => setError(e.message))

    const todayIso = new Date().toISOString().slice(0, 10)
    storage
      .getPlanDay(todayIso)
      .then((day) => setTodayPlan(day ?? null))
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

  return (
    <main className="mx-auto min-h-svh max-w-2xl bg-background p-6 text-foreground">
      <div className="mb-1 flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold">Ascent</h1>
        <div className="flex gap-3 text-sm">
          <Link to="/calendar" className="text-primary underline">
            Calendar
          </Link>
          <Link to="/review" className="text-primary underline">
            Review
          </Link>
          <Link to="/mistakes" className="text-primary underline">
            Mistakes
          </Link>
          <Link to="/settings" className="text-primary underline">
            Settings
          </Link>
        </div>
      </div>
      <p className="mb-6 text-muted-foreground">
        Micro-topics with drillable questions. Pick one to practice.
      </p>

      {todayPlan && (
        <section className="mb-6 rounded-lg border border-border p-4">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">Today's plan</h2>
          <ul className="space-y-1 text-sm">
            {todayPlan.items.map((item, i) => (
              <li key={i} className="flex items-center justify-between">
                <span className={item.done ? 'text-muted-foreground line-through' : ''}>
                  {item.kind} · {planItemLabel(item.microTopicId, topicNameById)}
                </span>
                {item.microTopicId === MOCK_SENTINEL && mocks[0] && (
                  <Link to={`/mock/${mocks[0].id}`} className="text-xs text-primary underline">
                    Go
                  </Link>
                )}
                {item.microTopicId !== MOCK_SENTINEL && item.microTopicId !== REVIEW_SENTINEL && (
                  <Link to={`/drill/${item.microTopicId}`} className="text-xs text-primary underline">
                    Go
                  </Link>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}

      {error && <p className="text-destructive">Failed to load content: {error}</p>}
      {!rows && !error && <p className="text-muted-foreground">Loading…</p>}

      {rows && (
        <ul className="divide-y divide-border rounded-lg border border-border">
          {rows.map(({ topic, count, hasLesson }) => (
            <li key={topic.id} className="flex items-center justify-between px-4 py-3 text-sm hover:bg-muted">
              <Link to={hasLesson ? `/lesson/${topic.id}` : `/drill/${topic.id}`} className="flex-1">
                <span>{topic.name}</span>
                {hasLesson && (
                  <span className="ml-2 rounded-full bg-primary/10 px-2 py-0.5 text-xs text-primary">Lesson</span>
                )}
              </Link>
              <span className="text-muted-foreground">{count} questions</span>
            </li>
          ))}
        </ul>
      )}

      {sets.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">Sets</h2>
          <ul className="divide-y divide-border rounded-lg border border-border">
            {sets.map((set) => (
              <li key={set.id} className="flex items-center justify-between px-4 py-3 text-sm hover:bg-muted">
                <Link to={`/set/${set.id}`} className="flex-1">
                  <span>{set.kind === 'di_set' ? 'DI set' : set.kind === 'lr_set' ? 'LR set' : 'RC passage'}</span>
                </Link>
                <span className="text-muted-foreground">
                  {set.questionIds.length} questions · {set.targetMinutes} min
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {mocks.length > 0 && (
        <section className="mt-6">
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">Mocks</h2>
          <ul className="divide-y divide-border rounded-lg border border-border">
            {mocks.map((mock) => (
              <li key={mock.id} className="flex items-center justify-between px-4 py-3 text-sm hover:bg-muted">
                <Link to={`/mock/${mock.id}`} className="flex-1">
                  <span>{mock.title}</span>
                  <span className="ml-2 text-xs text-muted-foreground">
                    {mock.kind === 'full' ? 'Full mock' : 'Sectional'}
                  </span>
                </Link>
                {mock.difficultyTier && (
                  <span className="text-muted-foreground">{DIFFICULTY_LABEL[mock.difficultyTier]}</span>
                )}
              </li>
            ))}
          </ul>
        </section>
      )}
    </main>
  )
}
