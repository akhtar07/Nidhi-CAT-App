import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { BackLink } from '@/components/ui/PageHeader'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { loadLesson, loadLessonIndex, loadQuestionIndex, loadSyllabus } from '@/content/loadContent'
import { buildRevisionIndex } from '@/revision/revisionIndex'
import { search, type SearchCorpus, type SearchResultKind } from '@/search/globalSearch'
import type { Lesson } from '@/types/content'

const KIND_LABEL: Record<SearchResultKind, string> = {
  topic: 'Topic',
  lesson: 'Lesson',
  formula: 'Formula',
}

/** One box that finds a micro-topic, a lesson, or a formula and jumps straight to it. */
export function Search() {
  const [corpus, setCorpus] = useState<SearchCorpus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')

  useEffect(() => {
    async function load() {
      const [syllabus, lessonIds, questionIndex] = await Promise.all([
        loadSyllabus(),
        loadLessonIndex(),
        loadQuestionIndex(),
      ])
      const lessons = (await Promise.all(lessonIds.map((id) => loadLesson(id)))).filter(
        (l): l is Lesson => l !== undefined,
      )
      const { cards } = buildRevisionIndex(lessons, syllabus)
      setCorpus({
        topics: syllabus,
        lessonTopicIds: lessonIds,
        // The question index already excludes mock-reserved items, so "has questions" here
        // means "has questions you can actually practise".
        topicIdsWithQuestions: new Set(questionIndex.flatMap((e) => e.microTopicIds)),
        formulaCards: cards,
      })
    }
    load().catch((e: Error) => setError(e.message))
  }, [])

  const results = useMemo(() => (corpus ? search(corpus, query) : []), [corpus, query])

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load search index: {error}</p>
        <BackLink to="/" />
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6">
      <div>
        <BackLink to="/" />
        <h1 className="text-2xl font-semibold tracking-tight">Search</h1>
      </div>

      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search topics, lessons and formulas…"
        aria-label="Search topics, lessons and formulas"
        autoFocus
        disabled={!corpus}
        className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50 disabled:opacity-60"
      />

      {!corpus ? (
        <div className="space-y-2">
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
          <Skeleton className="h-14 w-full" />
        </div>
      ) : query.trim() === '' ? (
        <EmptyState
          title="Start typing"
          description="Search across all 86 micro-topics, their lessons, and every formula card — for example “alligation”, “remainder”, or “para-summary”."
        />
      ) : results.length === 0 ? (
        <EmptyState
          title="No matches"
          description={`Nothing matches “${query}”. Try a shorter phrase, or a single keyword.`}
        />
      ) : (
        <>
          <p className="text-xs text-muted-foreground">
            {results.length} result{results.length === 1 ? '' : 's'}
          </p>
          <ul className="divide-y divide-border rounded-lg border border-border">
            {results.map((r) => (
              <li key={r.key}>
                <Link to={r.to} className="flex items-center gap-3 px-4 py-3 hover:bg-muted">
                  <span className="shrink-0 rounded-full border border-border px-2 py-0.5 text-[10px] tracking-wide text-muted-foreground uppercase">
                    {KIND_LABEL[r.kind]}
                  </span>
                  <span className="min-w-0">
                    <span className="block truncate text-sm font-medium">{r.title}</span>
                    <span className="block truncate text-xs text-muted-foreground">{r.subtitle}</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </>
      )}
    </main>
  )
}
