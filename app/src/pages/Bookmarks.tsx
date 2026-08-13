import { useEffect, useState } from 'react'
import { BackLink } from '@/components/ui/PageHeader'
import { Markdown } from '@/components/question-player/Markdown'
import { QuestionPlayer } from '@/components/question-player/QuestionPlayer'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { loadMicroTopic, loadQuestion, loadQuestionsForMicroTopic } from '@/content/loadContent'
import { storage } from '@/storage'
import type { MicroTopic, Question } from '@/types/content'
import type { Bookmark } from '@/types/state'

interface BookmarkEntry {
  bookmark: Bookmark
  question: Question
  topicName: string
}

async function loadBookmarks(): Promise<BookmarkEntry[]> {
  const bookmarks = await storage.listBookmarks()
  const topicNameCache = new Map<string, string>()

  const entries = await Promise.all(
    bookmarks.map(async (bookmark) => {
      let question: Question
      try {
        question = await loadQuestion(bookmark.questionId)
      } catch {
        return null
      }
      if (!topicNameCache.has(bookmark.microTopicId)) {
        const topic = await loadMicroTopic(bookmark.microTopicId)
        topicNameCache.set(bookmark.microTopicId, topic?.name ?? bookmark.microTopicId)
      }
      return { bookmark, question, topicName: topicNameCache.get(bookmark.microTopicId)! } satisfies BookmarkEntry
    }),
  )
  return entries.filter((e): e is BookmarkEntry => e !== null)
}

/** Study-flow feature: a manual "come back to this" flag on any question, independent of the
 * SRS/mistake pipeline (see QuestionPlayer.tsx's star toggle). */
export function Bookmarks() {
  const [entries, setEntries] = useState<BookmarkEntry[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [retrying, setRetrying] = useState<Question[] | null>(null)
  const [retryTopics, setRetryTopics] = useState<Map<string, { topic: MicroTopic; topicQuestions: Question[] }>>(
    new Map(),
  )
  const [retryIndex, setRetryIndex] = useState(0)

  function refresh() {
    loadBookmarks()
      .then(setEntries)
      .catch((e: Error) => setError(e.message))
  }

  useEffect(refresh, [])

  async function removeBookmark(questionId: string) {
    await storage.removeBookmark(questionId)
    setEntries((prev) => prev?.filter((e) => e.question.id !== questionId) ?? null)
  }

  async function startRetry(question: Question) {
    const topicId = question.microTopicIds[0]
    const [topic, topicQuestions] = await Promise.all([
      loadMicroTopic(topicId),
      loadQuestionsForMicroTopic(topicId),
    ])
    if (!topic) return
    setRetryTopics(new Map([[question.id, { topic, topicQuestions }]]))
    setRetrying([question])
    setRetryIndex(0)
  }

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load bookmarks: {error}</p>
      </main>
    )
  }

  if (entries === null) {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-20 w-full" />
      </main>
    )
  }

  if (retrying) {
    if (retryIndex >= retrying.length) {
      return (
        <main className="mx-auto max-w-2xl space-y-4 p-6 text-center">
          <h2 className="text-xl font-semibold">Re-attempt complete</h2>
          <Button
            onClick={() => {
              setRetrying(null)
              refresh()
            }}
          >
            Back to bookmarks
          </Button>
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
      <QuestionPlayer
        key={q.id}
        question={q}
        mode="review"
        topic={info.topic}
        topicQuestions={info.topicQuestions}
        onComplete={() => setRetryIndex((i) => i + 1)}
      />
    )
  }

  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6">
      <div>
        <BackLink to="/" />
        <h1 className="text-2xl font-semibold tracking-tight">Bookmarks</h1>
      </div>

      {entries.length === 0 ? (
        <EmptyState
          title="No bookmarks yet"
          description="Tap the star on any question, in a drill or a mock, to save it here for later — useful for a tricky question you want to revisit without waiting for it to reappear on its own."
          actionLabel="Go practice"
          actionTo="/"
        />
      ) : (
        <ul className="divide-y divide-border rounded-lg border border-border">
          {entries.map(({ bookmark, question, topicName }) => (
            <li key={bookmark.id} className="px-4 py-3 text-sm">
              <div className="mb-1 flex items-center justify-between text-xs text-muted-foreground">
                <span>{topicName}</span>
                <span>{new Date(bookmark.createdAt).toLocaleDateString()}</span>
              </div>
              <Markdown text={question.stemMarkdown} />
              <div className="mt-2 flex gap-2">
                <Button size="sm" variant="outline" onClick={() => void startRetry(question)}>
                  Attempt
                </Button>
                <Button size="sm" variant="ghost" onClick={() => void removeBookmark(question.id)}>
                  Remove
                </Button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </main>
  )
}
