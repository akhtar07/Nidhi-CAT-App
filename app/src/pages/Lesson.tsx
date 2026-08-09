import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { Markdown, MarkdownBlocks } from '@/components/question-player/Markdown'
import { Button } from '@/components/ui/button'
import { loadLesson, loadMicroTopic } from '@/content/loadContent'
import type { Lesson as LessonContent, MicroTopic } from '@/types/content'

/** Milestone 6: the "Learn" half of the Learn→Drill loop (SPEC.md §15). */
export function Lesson() {
  const { topicId } = useParams<{ topicId: string }>()
  const navigate = useNavigate()
  const [topic, setTopic] = useState<MicroTopic | undefined>(undefined)
  const [lesson, setLesson] = useState<LessonContent | null | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)

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

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load lesson: {error}</p>
        <Link to="/" className="text-primary underline">
          Back
        </Link>
      </main>
    )
  }

  if (topic === undefined || lesson === undefined) {
    return <main className="mx-auto max-w-2xl p-6 text-muted-foreground">Loading…</main>
  }

  if (!lesson || !topic) {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6">
        <p className="text-muted-foreground">No lesson for this micro-topic yet.</p>
        {topicId && (
          <Button onClick={() => navigate(`/drill/${topicId}`)}>Practise anyway</Button>
        )}
        <Link to="/" className="block text-primary underline">
          Back
        </Link>
      </main>
    )
  }

  return (
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <div>
        <Link to="/" className="text-sm text-primary underline">
          Back
        </Link>
        <h1 className="mt-2 text-2xl font-semibold">{topic.name}</h1>
        <p className="text-sm text-muted-foreground">{lesson.estReadMinutes} min read</p>
      </div>

      <MarkdownBlocks text={lesson.bodyMarkdown} />

      {lesson.formulaCards && lesson.formulaCards.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-lg font-semibold">Formula cards</h2>
          {lesson.formulaCards.map((card) => (
            <div key={card.id} className="rounded-lg border border-border p-3">
              <p className="mb-1 font-medium">{card.title}</p>
              <div className="text-sm">
                <Markdown text={card.bodyMarkdown} />
              </div>
              {card.exampleMarkdown && (
                <div className="mt-1 text-sm text-muted-foreground">
                  <Markdown text={card.exampleMarkdown} />
                </div>
              )}
            </div>
          ))}
        </section>
      )}

      {lesson.workedExamples && lesson.workedExamples.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-lg font-semibold">Worked examples</h2>
          {lesson.workedExamples.map((example, i) => (
            <div key={example.id} className="rounded-lg border border-border p-3 text-sm">
              <p className="mb-2 font-medium">
                {i + 1}. <Markdown text={example.stemMarkdown} />
              </p>
              <div className="leading-relaxed">
                <Markdown text={example.solutionMarkdown} />
              </div>
              {example.altSolutionMarkdown && (
                <div className="mt-2 leading-relaxed text-muted-foreground">
                  <p className="mb-1 font-medium text-foreground">Smart approach</p>
                  <Markdown text={example.altSolutionMarkdown} />
                </div>
              )}
            </div>
          ))}
        </section>
      )}

      {lesson.commonTraps && lesson.commonTraps.length > 0 && (
        <section className="space-y-2">
          <h2 className="text-lg font-semibold">Common traps</h2>
          <ul className="list-inside list-disc space-y-1 text-sm text-muted-foreground">
            {lesson.commonTraps.map((trap, i) => (
              <li key={i}>{trap}</li>
            ))}
          </ul>
        </section>
      )}

      <Button onClick={() => navigate(`/drill/${topic.id}`)}>Start practising</Button>
    </main>
  )
}
