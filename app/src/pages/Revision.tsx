import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { BackLink } from '@/components/ui/PageHeader'
import { Markdown } from '@/components/question-player/Markdown'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/lib/utils'
import { loadLesson, loadLessonIndex, loadSyllabus } from '@/content/loadContent'
import {
  buildRevisionIndex,
  filterCards,
  filterTraps,
  groupByTopic,
  type RevisionIndex,
} from '@/revision/revisionIndex'
import type { Lesson, Question } from '@/types/content'

type Section = Question['section']
type Tab = 'formulas' | 'traps'

const SECTIONS: Section[] = ['QA', 'DILR', 'VARC']

/**
 * Formula & revision hub.
 *
 * The 188 formula cards and 263 common traps in the lesson bank were previously reachable
 * only by opening each of the 86 lessons individually — which is precisely useless for
 * revision, since the moment you want a formula is the moment you have forgotten which
 * topic it lives under. This surfaces all of them in one searchable place.
 */
export function Revision() {
  const [index, setIndex] = useState<RevisionIndex | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [tab, setTab] = useState<Tab>('formulas')
  const [section, setSection] = useState<Section | null>(null)
  const [query, setQuery] = useState('')
  const [expanded, setExpanded] = useState<Set<string>>(new Set())

  useEffect(() => {
    async function load() {
      const [lessonIds, syllabus] = await Promise.all([loadLessonIndex(), loadSyllabus()])
      // 86 small JSON files, fetched in parallel and served from the same origin (and
      // precached by the service worker), so this is one round-trip's latency in practice.
      const lessons = (await Promise.all(lessonIds.map((id) => loadLesson(id)))).filter(
        (l): l is Lesson => l !== undefined,
      )
      setIndex(buildRevisionIndex(lessons, syllabus))
    }
    load().catch((e: Error) => setError(e.message))
  }, [])

  const filters = useMemo(() => ({ section, query }), [section, query])
  const cards = useMemo(() => (index ? filterCards(index.cards, filters) : []), [index, filters])
  const traps = useMemo(() => (index ? filterTraps(index.traps, filters) : []), [index, filters])
  const cardGroups = useMemo(() => groupByTopic(cards), [cards])
  const trapGroups = useMemo(() => groupByTopic(traps), [traps])

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load revision content: {error}</p>
        <BackLink to="/" />
      </main>
    )
  }

  if (!index) {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6">
        <Skeleton className="h-8 w-44" />
        <Skeleton className="h-9 w-full" />
        <Skeleton className="h-28 w-full" />
        <Skeleton className="h-28 w-full" />
      </main>
    )
  }

  const showing = tab === 'formulas' ? cards.length : traps.length
  const total = tab === 'formulas' ? index.cards.length : index.traps.length

  // Topic groups collapse by default. Rendering all 188 formula cards at once produced a
  // 31,000px page (~35 screens) with 434 KaTeX nodes and a 2s render — a wall of text with
  // no way to navigate it, which is the opposite of what revision needs. Collapsed, the page
  // is a scannable list of topics. An active search auto-expands, since the results are
  // already narrow at that point and hiding them behind another click would be silly.
  const searching = query.trim() !== ''
  const isOpen = (microTopicId: string) => searching || expanded.has(microTopicId)
  const toggleGroup = (microTopicId: string) =>
    setExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(microTopicId)) next.delete(microTopicId)
      else next.add(microTopicId)
      return next
    })

  return (
    <main className="mx-auto max-w-2xl space-y-5 p-6">
      <div>
        <BackLink to="/" />
        <h1 className="text-2xl font-semibold tracking-tight">Revision</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Every formula and every common trap from the lessons, in one place.
        </p>
      </div>

      <div className="flex gap-2">
        {(['formulas', 'traps'] as Tab[]).map((t) => (
          <button
            key={t}
            type="button"
            onClick={() => setTab(t)}
            aria-pressed={tab === t}
            className={cn(
              'rounded-lg border px-3 py-1.5 text-sm transition-colors',
              tab === t ? 'border-primary bg-primary/10' : 'border-border text-muted-foreground hover:bg-muted',
            )}
          >
            {t === 'formulas' ? `Formulas (${index.cards.length})` : `Traps (${index.traps.length})`}
          </button>
        ))}
      </div>

      <input
        type="search"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={tab === 'formulas' ? 'Search formulas…' : 'Search traps…'}
        aria-label={tab === 'formulas' ? 'Search formulas' : 'Search traps'}
        className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
      />

      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => setSection(null)}
          aria-pressed={section === null}
          className={cn(
            'rounded-full border px-3 py-1 text-xs transition-colors',
            section === null ? 'border-primary bg-primary/10' : 'border-border text-muted-foreground hover:bg-muted',
          )}
        >
          All sections
        </button>
        {SECTIONS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => setSection(s)}
            aria-pressed={section === s}
            className={cn(
              'rounded-full border px-3 py-1 text-xs transition-colors',
              section === s ? 'border-primary bg-primary/10' : 'border-border text-muted-foreground hover:bg-muted',
            )}
          >
            {s}
          </button>
        ))}
      </div>

      <p className="text-xs text-muted-foreground">
        Showing {showing} of {total}
      </p>

      {showing === 0 ? (
        <EmptyState
          title="Nothing matches"
          description="No formulas or traps match this search in this section. Try a different word, or switch to all sections."
        />
      ) : (
        <div className="space-y-2">
          {(tab === 'formulas' ? cardGroups : trapGroups).map((group) => {
            const open = isOpen(group.microTopicId)
            return (
              <section key={group.microTopicId} className="rounded-lg border border-border">
                <div className="flex items-center gap-2 px-3 py-2">
                  <button
                    type="button"
                    onClick={() => toggleGroup(group.microTopicId)}
                    aria-expanded={open}
                    className="flex flex-1 items-center gap-2 text-left"
                  >
                    <span aria-hidden className="w-3 shrink-0 text-xs text-muted-foreground">
                      {open ? '▾' : '▸'}
                    </span>
                    <span className="flex-1 text-sm font-medium">{group.topicName}</span>
                    <span className="text-xs text-muted-foreground">{group.items.length}</span>
                  </button>
                  <Link to={`/lesson/${group.microTopicId}`} className="text-xs text-primary underline">
                    Lesson
                  </Link>
                </div>

                {open && tab === 'formulas' && (
                  <ul className="space-y-2 border-t border-border p-3">
                    {(group.items as typeof cards).map((card) => (
                      <li key={card.id} className="rounded-lg bg-muted/40 p-3">
                        <p className="text-sm font-medium">{card.title}</p>
                        <div className="mt-1 text-sm">
                          <Markdown text={card.bodyMarkdown} />
                        </div>
                        {card.exampleMarkdown && (
                          <div className="mt-2 border-t border-border pt-2 text-xs text-muted-foreground">
                            <Markdown text={card.exampleMarkdown} />
                          </div>
                        )}
                      </li>
                    ))}
                  </ul>
                )}

                {open && tab === 'traps' && (
                  <ul className="space-y-1.5 border-t border-border p-3">
                    {(group.items as typeof traps).map((trap) => (
                      <li key={trap.id} className="flex gap-2 text-sm">
                        <span aria-hidden className="text-muted-foreground">
                          •
                        </span>
                        <span>
                          <Markdown text={trap.text} />
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </section>
            )
          })}
        </div>
      )}

      <div className="pt-2">
        <Link to="/practice/new">
          <Button variant="outline">Practise what you just revised</Button>
        </Link>
      </div>
    </main>
  )
}
