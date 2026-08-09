import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { QuestionPlayer } from '@/components/question-player/QuestionPlayer'
import { Button } from '@/components/ui/button'
import { loadQuestionsForMicroTopic } from '@/content/loadContent'
import type { Question } from '@/types/content'
import type { Attempt } from '@/types/state'

export function Drill() {
  const { topicId } = useParams<{ topicId: string }>()
  const [questions, setQuestions] = useState<Question[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [index, setIndex] = useState(0)
  const [results, setResults] = useState<Attempt[]>([])

  useEffect(() => {
    if (!topicId) return
    setQuestions(null)
    setError(null)
    setIndex(0)
    setResults([])
    loadQuestionsForMicroTopic(topicId)
      .then(setQuestions)
      .catch((e: Error) => setError(e.message))
  }, [topicId])

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load questions: {error}</p>
        <Link to="/" className="text-primary underline">
          Back
        </Link>
      </main>
    )
  }

  if (!questions) {
    return (
      <main className="mx-auto max-w-2xl p-6 text-muted-foreground">Loading…</main>
    )
  }

  if (questions.length === 0) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-muted-foreground">No questions for this micro-topic yet.</p>
        <Link to="/" className="text-primary underline">
          Back
        </Link>
      </main>
    )
  }

  if (index >= questions.length) {
    const correctCount = results.filter((a) => a.correct).length
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6 text-center">
        <h2 className="text-xl font-semibold">Drill complete</h2>
        <p className="text-muted-foreground">
          {correctCount} / {results.length} correct
        </p>
        <Link to="/">
          <Button>Back to topics</Button>
        </Link>
      </main>
    )
  }

  return (
    <div>
      <div className="mx-auto max-w-2xl px-4 pt-4 text-sm text-muted-foreground">
        Question {index + 1} of {questions.length}
      </div>
      <QuestionPlayer
        key={questions[index].id}
        question={questions[index]}
        mode="drill"
        onComplete={(attempt) => {
          setResults((r) => [...r, attempt])
          setIndex((i) => i + 1)
        }}
      />
    </div>
  )
}
