import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { AlertTriangle, ArrowRight, BookOpen, Lightbulb } from 'lucide-react'
import { Markdown, MarkdownBlocks } from '@/components/question-player/Markdown'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/Card'
import { BackLink } from '@/components/ui/PageHeader'
import { Skeleton } from '@/components/ui/Skeleton'
import { loadLesson, loadMicroTopic } from '@/content/loadContent'
import { cn } from '@/lib/utils'
import type { Lesson as LessonContent, MicroTopic } from '@/types/content'

/**
 * Milestone 6: the "Learn" half of the Learn→Drill loop (SPEC.md §15).
 *
 * Rebuilt for long lessons. The original laid a whole lesson out as one undifferentiated
 * column, which was survivable when a lesson was ~150 words and is not once a lesson actually
 * teaches a topic end to end: no way to see what a lesson covers before committing to it, no
 * way to get back to a section, solutions all open at once so the page was mostly answers, and
 * body text in the UI sans-serif at 14px — against SPEC.md §13's explicit "~18px / 1.7 line
 * height" reading font, which exists precisely because this is read for hours under stress.
 *
 * So: a contents strip built from the lesson's own `## ` headings, a reading measure, and
 * worked-example solutions collapsed by default — SPEC.md §13, "Solutions: step-by-step,
 * collapsible, with the 'smart approach' shown separately from the 'textbook approach'."
 * Collapsed matters pedagogically, not just visually: a worked example whose answer is already
 * on screen is a worked example nobody attempts first.
 */

/** Section headings, so the contents strip is derived from the lesson rather than hardcoded. */
function extractHeadings(body: string): string[] {
  return body
    .split('\n')
    .filter((line) => line.startsWith('## '))
    .map((line) => line.slice(3).trim())
}

function slugify(heading: string): string {
  return heading.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '')
}

function WorkedExample({
  index,
  stem,
  solution,
  altSolution,
}: {
  index: number
  stem: string
  solution: string
  altSolution?: string | null
}) {
  const [revealed, setRevealed] = useState(false)
  return (
    <Card className="overflow-hidden">
      <div className="space-y-3 p-4">
        <div className="flex gap-3">
          <span className="mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full bg-secondary text-xs font-medium">
            {index}
          </span>
          <div className="reading min-w-0 flex-1 text-[0.95rem]">
            <Markdown text={stem} />
          </div>
        </div>
        {!revealed ? (
          <Button variant="outline" size="sm" className="ml-9" onClick={() => setRevealed(true)}>
            Show the solution
          </Button>
        ) : (
          <div className="ml-9 space-y-4 border-l-2 border-border pl-4">
            <div className="reading text-[0.95rem]">
              <Markdown text={solution} />
            </div>
            {altSolution && (
              <div className="rounded-lg bg-secondary/50 p-3">
                <p className="mb-1.5 flex items-center gap-1.5 text-xs font-medium text-primary">
                  <Lightbulb className="size-3.5" aria-hidden />
                  The faster way
                </p>
                <div className="reading text-[0.9rem] text-muted-foreground">
                  <Markdown text={altSolution} />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  )
}

export function Lesson() {
  const { topicId } = useParams<{ topicId: string }>()
  const navigate = useNavigate()
  const [topic, setTopic] = useState<MicroTopic | undefined>(undefined)
  const [lesson, setLesson] = useState<LessonContent | null | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)
  const bodyRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!topicId) return
    setTopic(undefined)
    setLesson(undefined)
    setError(null)
    Promise.all([loadMicroTopic(topicId), loadLesson(topicId)])
      .then(([t, l]) => {
        setTopic(t)
        setLesson(l ?? null)
      })
      .catch((e: Error) => setError(e.message))
  }, [topicId])

  const headings = useMemo(() => (lesson ? extractHeadings(lesson.bodyMarkdown) : []), [lesson])

  /**
   * The tokenizer emits headings without ids, and adding them there would mean touching a
   * parser shared with every question stem. Stamping them on after render keeps that blast
   * radius at zero, and the contents strip is the only thing that needs them.
   */
  useEffect(() => {
    if (!bodyRef.current) return
    for (const el of bodyRef.current.querySelectorAll('h2')) {
      el.id = slugify(el.textContent ?? '')
      el.style.scrollMarginTop = '1rem'
    }
  }, [lesson])

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <BackLink to="/" />
        <p className="text-destructive">Failed to load lesson: {error}</p>
      </main>
    )
  }

  if (topic === undefined || lesson === undefined) {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-10 w-40" />
      </main>
    )
  }

  if (!lesson || !topic) {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6">
        <BackLink to="/" />
        <p className="text-muted-foreground">No lesson for this micro-topic yet.</p>
        {topicId && <Button onClick={() => navigate(`/drill/${topicId}`)}>Practise anyway</Button>}
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-2xl px-5 pb-28 pt-5">
      <BackLink to="/" />
      <header className="mb-6">
        <h1 className="text-2xl font-semibold tracking-tight">{topic.name}</h1>
        <p className="mt-1 flex items-center gap-1.5 text-sm text-muted-foreground">
          <BookOpen className="size-3.5" aria-hidden />
          {lesson.estReadMinutes} min read
          {lesson.workedExamples?.length ? <> · {lesson.workedExamples.length} worked examples</> : null}
        </p>
      </header>

      {/* What this lesson covers, before committing to reading it. */}
      {headings.length > 1 && (
        <Card variant="quiet" className="mb-6 p-4">
          <p className="eyebrow mb-2">In this lesson</p>
          <ol className="space-y-1.5">
            {headings.map((heading, i) => (
              <li key={heading} className="flex gap-2.5 text-sm">
                <span className="text-muted-foreground tabular-nums">{i + 1}.</span>
                <a href={`#${slugify(heading)}`} className="text-foreground hover:text-primary hover:underline">
                  {heading}
                </a>
              </li>
            ))}
          </ol>
        </Card>
      )}

      <div ref={bodyRef} className="reading lesson-body">
        <MarkdownBlocks text={lesson.bodyMarkdown} />
      </div>

      {lesson.workedExamples && lesson.workedExamples.length > 0 && (
        <section className="mt-8 space-y-3">
          <h2 className="text-lg font-semibold tracking-tight">Worked examples</h2>
          <p className="text-sm text-muted-foreground">
            Try each one before opening the solution — reading a solution feels like learning and mostly isn&apos;t.
          </p>
          {lesson.workedExamples.map((example, i) => (
            <WorkedExample
              key={example.id}
              index={i + 1}
              stem={example.stemMarkdown}
              solution={example.solutionMarkdown}
              altSolution={example.altSolutionMarkdown}
            />
          ))}
        </section>
      )}

      {lesson.formulaCards && lesson.formulaCards.length > 0 && (
        <section className="mt-8 space-y-3">
          <h2 className="text-lg font-semibold tracking-tight">Formulas to remember</h2>
          <div className="grid gap-2.5">
            {lesson.formulaCards.map((card) => (
              <Card key={card.id} className="p-4">
                <p className="mb-2 text-xs font-medium uppercase tracking-wide text-primary">{card.title}</p>
                <div className="text-[0.95rem]">
                  <Markdown text={card.bodyMarkdown} />
                </div>
                {card.exampleMarkdown && (
                  <div className="mt-2 border-t border-border pt-2 text-sm text-muted-foreground">
                    <Markdown text={card.exampleMarkdown} />
                  </div>
                )}
              </Card>
            ))}
          </div>
        </section>
      )}

      {lesson.commonTraps && lesson.commonTraps.length > 0 && (
        <section className="mt-8 space-y-3">
          <h2 className="flex items-center gap-2 text-lg font-semibold tracking-tight">
            <AlertTriangle className="size-4 text-[var(--mastery-decaying)]" aria-hidden />
            Where people lose marks
          </h2>
          <Card variant="quiet" className="divide-y divide-border">
            {lesson.commonTraps.map((trap, i) => (
              <p key={i} className="px-4 py-3 text-sm text-muted-foreground">
                {trap}
              </p>
            ))}
          </Card>
        </section>
      )}

      {/* Pinned, because the whole point of the lesson is the practice that follows it, and on
          a long lesson that button would otherwise be several screens below the fold. */}
      <div
        className={cn(
          'fixed inset-x-0 bottom-0 z-30 border-t border-border bg-background/95 px-5 py-3 backdrop-blur',
          'supports-[backdrop-filter]:bg-background/80',
        )}
      >
        <div className="mx-auto flex max-w-2xl items-center gap-3">
          <Button className="flex-1" onClick={() => navigate(`/drill/${topic.id}`)}>
            Start practising
            <ArrowRight className="size-4" aria-hidden />
          </Button>
        </div>
      </div>
    </main>
  )
}
