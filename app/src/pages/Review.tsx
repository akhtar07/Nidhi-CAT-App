import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Markdown } from '@/components/question-player/Markdown'
import { Button } from '@/components/ui/button'
import { loadLesson, loadQuestion } from '@/content/loadContent'
import { gradeReview, isDue, Rating, type Grade } from '@/srs/fsrsAdapter'
import { storage } from '@/storage'
import type { FormulaCard, Question } from '@/types/content'
import type { SrsCard } from '@/types/state'

interface ReviewItem {
  card: SrsCard
  front: string
  back: string
}

async function loadReviewItem(card: SrsCard): Promise<ReviewItem | null> {
  if (card.cardType === 'mistake') {
    let question: Question
    try {
      question = await loadQuestion(card.refId)
    } catch {
      return null
    }
    return { card, front: question.stemMarkdown, back: question.solutionMarkdown }
  }
  const lesson = await loadLesson(card.microTopicId)
  const formula: FormulaCard | undefined = lesson?.formulaCards?.find((fc) => fc.id === card.refId)
  if (!formula) return null
  return {
    card,
    front: formula.title,
    back: formula.exampleMarkdown ? `${formula.bodyMarkdown}\n\n${formula.exampleMarkdown}` : formula.bodyMarkdown,
  }
}

const GRADE_BUTTONS: { grade: Grade; label: string }[] = [
  { grade: Rating.Again, label: 'Again' },
  { grade: Rating.Hard, label: 'Hard' },
  { grade: Rating.Good, label: 'Good' },
  { grade: Rating.Easy, label: 'Easy' },
]

/** SPEC.md §8.4/§14 item 3: the swipeable, FSRS-scheduled formula + mistake-question deck. */
export function Review() {
  const [queue, setQueue] = useState<ReviewItem[] | null>(null)
  const [index, setIndex] = useState(0)
  const [showBack, setShowBack] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    storage
      .listSrsCards()
      .then(async (cards) => {
        const due = cards.filter((c) => isDue({ stability: c.stability, difficulty: c.difficulty, nextReviewAt: c.nextReviewAt, lastReviewedAt: c.lastReviewedAt }))
        const items = await Promise.all(due.map(loadReviewItem))
        setQueue(items.filter((i): i is ReviewItem => i !== null))
      })
      .catch((e: Error) => setError(e.message))
  }, [])

  async function grade(g: Grade) {
    if (!queue) return
    const item = queue[index]
    const fsrs = gradeReview(
      { stability: item.card.stability, difficulty: item.card.difficulty, nextReviewAt: item.card.nextReviewAt, lastReviewedAt: item.card.lastReviewedAt },
      g,
    )
    await storage.putSrsCard({ ...item.card, ...fsrs })
    setShowBack(false)
    setIndex((i) => i + 1)
  }

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load review deck: {error}</p>
      </main>
    )
  }
  if (queue === null) {
    return <main className="mx-auto max-w-2xl p-6 text-muted-foreground">Loading…</main>
  }

  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6">
      <div>
        <Link to="/" className="text-sm text-primary underline">
          Back
        </Link>
        <h1 className="mt-2 text-2xl font-semibold">Review</h1>
      </div>

      {index >= queue.length ? (
        <p className="text-muted-foreground">
          {queue.length === 0 ? 'No cards due for review — nice.' : "That's everything due today."}
        </p>
      ) : (
        <div className="space-y-4 rounded-lg border border-border p-4">
          <p className="text-xs text-muted-foreground">
            {queue[index].card.cardType === 'formula' ? 'Formula card' : 'Mistake card'} · card {index + 1} of{' '}
            {queue.length}
          </p>
          <div className="text-base leading-relaxed">
            <Markdown text={queue[index].front} />
          </div>
          {showBack ? (
            <>
              <div className="border-t border-border pt-3 text-sm leading-relaxed">
                <Markdown text={queue[index].back} />
              </div>
              <div className="flex flex-wrap gap-2 pt-2">
                {GRADE_BUTTONS.map((b) => (
                  <Button key={b.label} variant="outline" onClick={() => void grade(b.grade)}>
                    {b.label}
                  </Button>
                ))}
              </div>
            </>
          ) : (
            <Button onClick={() => setShowBack(true)}>Show answer</Button>
          )}
        </div>
      )}
    </main>
  )
}
