import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  loadLessonIndex,
  loadPassageSetIndex,
  loadQuestionIndex,
  loadSyllabus,
  type PassageSetIndexEntry,
} from '@/content/loadContent'
import type { MicroTopic } from '@/types/content'

interface TopicRow {
  topic: MicroTopic
  count: number
  hasLesson: boolean
}

export function Today() {
  const [rows, setRows] = useState<TopicRow[] | null>(null)
  const [sets, setSets] = useState<PassageSetIndexEntry[]>([])
  const [error, setError] = useState<string | null>(null)

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
      })
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <main className="mx-auto min-h-svh max-w-2xl bg-background p-6 text-foreground">
      <div className="mb-1 flex items-baseline justify-between">
        <h1 className="text-2xl font-semibold">Ascent</h1>
        <Link to="/settings" className="text-sm text-primary underline">
          Settings
        </Link>
      </div>
      <p className="mb-6 text-muted-foreground">
        Micro-topics with drillable questions. Pick one to practice.
      </p>

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
    </main>
  )
}
