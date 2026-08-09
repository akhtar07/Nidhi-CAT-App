import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Markdown } from '@/components/question-player/Markdown'
import { QuestionPlayer } from '@/components/question-player/QuestionPlayer'
import { Button } from '@/components/ui/button'
import { loadMicroTopic, loadQuestion, loadQuestionsForMicroTopic } from '@/content/loadContent'
import { storage } from '@/storage'
import type { MicroTopic, Question } from '@/types/content'
import type { Attempt } from '@/types/state'

interface MistakeEntry {
  question: Question
  topicName: string
  errorTag: Attempt['errorTag']
  wrongAt: number
}

const ERROR_TAG_LABELS: Record<NonNullable<Attempt['errorTag']>, string> = {
  concept: 'Conceptual gap',
  calculation: 'Calculation error',
  misread: 'Misread the question',
  time_pressure: 'Ran out of time',
  careless_option: 'Careless option pick',
  unknown_formula: "Didn't know formula",
  guessed: 'Guessed',
}

async function loadMistakes(): Promise<MistakeEntry[]> {
  const attempts = await storage.listAttempts()
  const wrong = attempts.filter((a) => !a.correct)

  // Most recent wrong attempt per question — an old mistake she's since fixed shouldn't keep
  // showing up forever, but the notebook should still reflect the latest error tag she gave it.
  const latestByQuestion = new Map<string, Attempt>()
  for (const a of wrong) {
    const existing = latestByQuestion.get(a.questionId)
    if (!existing || a.submittedAt > existing.submittedAt) latestByQuestion.set(a.questionId, a)
  }

  const topicNameCache = new Map<string, string>()
  const entries = await Promise.all(
    [...latestByQuestion.values()].map(async (a) => {
      let question: Question
      try {
        question = await loadQuestion(a.questionId)
      } catch {
        return null
      }
      const topicId = a.microTopicIds[0]
      if (!topicNameCache.has(topicId)) {
        const topic = await loadMicroTopic(topicId)
        topicNameCache.set(topicId, topic?.name ?? topicId)
      }
      return {
        question,
        topicName: topicNameCache.get(topicId)!,
        errorTag: a.errorTag,
        wrongAt: a.submittedAt,
      } satisfies MistakeEntry
    }),
  )
  return entries.filter((e): e is MistakeEntry => e !== null).sort((a, b) => b.wrongAt - a.wrongAt)
}

export function MistakeNotebook() {
  const [mistakes, setMistakes] = useState<MistakeEntry[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [tagFilter, setTagFilter] = useState<string>('')
  const [topicFilter, setTopicFilter] = useState<string>('')
  const [retrying, setRetrying] = useState<Question[] | null>(null)
  const [retryTopics, setRetryTopics] = useState<Map<string, { topic: MicroTopic; topicQuestions: Question[] }>>(
    new Map(),
  )
  const [retryIndex, setRetryIndex] = useState(0)

  useEffect(() => {
    loadMistakes()
      .then(setMistakes)
      .catch((e: Error) => setError(e.message))
  }, [])

  const filtered = (mistakes ?? []).filter(
    (m) =>
      (tagFilter === '' || m.errorTag === tagFilter) &&
      (topicFilter === '' || m.topicName === topicFilter),
  )
  const topics = [...new Set((mistakes ?? []).map((m) => m.topicName))].sort()

  async function startRetry() {
    const questions = filtered.map((m) => m.question)
    const primaryTopicIds = [...new Set(questions.map((q) => q.microTopicIds[0]))]
    const entries = await Promise.all(
      primaryTopicIds.map(async (topicId) => {
        const [topic, topicQuestions] = await Promise.all([
          loadMicroTopic(topicId),
          loadQuestionsForMicroTopic(topicId),
        ])
        return [topicId, topic, topicQuestions] as const
      }),
    )
    const map = new Map<string, { topic: MicroTopic; topicQuestions: Question[] }>()
    for (const q of questions) {
      const entry = entries.find(([id]) => id === q.microTopicIds[0])
      if (entry?.[1]) map.set(q.id, { topic: entry[1], topicQuestions: entry[2] })
    }
    setRetryTopics(map)
    setRetrying(questions)
    setRetryIndex(0)
  }

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load mistakes: {error}</p>
      </main>
    )
  }
  if (mistakes === null) {
    return <main className="mx-auto max-w-2xl p-6 text-muted-foreground">Loading…</main>
  }

  if (retrying) {
    if (retryIndex >= retrying.length) {
      return (
        <main className="mx-auto max-w-2xl space-y-4 p-6 text-center">
          <h2 className="text-xl font-semibold">Re-attempt complete</h2>
          <Button onClick={() => setRetrying(null)}>Back to notebook</Button>
        </main>
      )
    }
    const q = retrying[retryIndex]
    const info = retryTopics.get(q.id)
    if (!info) {
      setRetryIndex((i) => i + 1)
      return null
    }
    return (
      <div>
        <div className="mx-auto max-w-2xl px-4 pt-4 text-sm text-muted-foreground">
          Re-attempt {retryIndex + 1} of {retrying.length}
        </div>
        <QuestionPlayer
          key={q.id}
          question={q}
          mode="review"
          topic={info.topic}
          topicQuestions={info.topicQuestions}
          onComplete={() => setRetryIndex((i) => i + 1)}
        />
      </div>
    )
  }

  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6">
      <div>
        <Link to="/" className="text-sm text-primary underline">
          Back
        </Link>
        <h1 className="mt-2 text-2xl font-semibold">Mistake Notebook</h1>
      </div>

      {mistakes.length === 0 ? (
        <p className="text-muted-foreground">No mistakes to review yet — go break something.</p>
      ) : (
        <>
          <div className="flex flex-wrap gap-2">
            <select
              value={tagFilter}
              onChange={(e) => setTagFilter(e.target.value)}
              className="rounded-lg border border-border bg-background px-2 py-1 text-sm"
            >
              <option value="">All error types</option>
              {Object.entries(ERROR_TAG_LABELS).map(([tag, label]) => (
                <option key={tag} value={tag}>
                  {label}
                </option>
              ))}
            </select>
            <select
              value={topicFilter}
              onChange={(e) => setTopicFilter(e.target.value)}
              className="rounded-lg border border-border bg-background px-2 py-1 text-sm"
            >
              <option value="">All topics</option>
              {topics.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
            <Button variant="outline" onClick={() => void startRetry()} disabled={filtered.length === 0}>
              Re-attempt this set ({filtered.length})
            </Button>
          </div>

          <ul className="divide-y divide-border rounded-lg border border-border">
            {filtered.map((m) => (
              <li key={m.question.id} className="px-4 py-3 text-sm">
                <div className="mb-1 flex items-center justify-between text-xs text-muted-foreground">
                  <span>{m.topicName}</span>
                  <span>{m.errorTag ? ERROR_TAG_LABELS[m.errorTag] : 'untagged'}</span>
                </div>
                <Markdown text={m.question.stemMarkdown} />
              </li>
            ))}
          </ul>
        </>
      )}
    </main>
  )
}
