import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { QuestionPlayer } from '@/components/question-player/QuestionPlayer'
import { Button } from '@/components/ui/button'
import { loadMicroTopic, loadQuestionsForMicroTopic } from '@/content/loadContent'
import { DEFAULT_LEARNER_ELO } from '@/mastery/elo'
import { selectDrillQueue } from '@/mastery/selectItems'
import { applyDecay } from '@/srs/topicReview'
import { storage } from '@/storage'
import type { MicroTopic, Question } from '@/types/content'
import type { Attempt, MasteryState } from '@/types/state'

const FOURTEEN_DAYS_MS = 14 * 24 * 60 * 60 * 1000

interface DrillSession {
  topic: MicroTopic
  topicQuestions: Question[]
  queue: Question[]
}

async function buildSession(topicId: string): Promise<DrillSession | null> {
  const [topic, allTopicQuestions] = await Promise.all([
    loadMicroTopic(topicId),
    loadQuestionsForMicroTopic(topicId),
  ])
  // SPEC.md §9.1: "maintain a mock_reserved flag on items so the drill
  // engine can never serve them" — filtered here, before anything downstream
  // (item-Elo banding, mastery denominators, the actual queue) ever sees them.
  const topicQuestions = allTopicQuestions.filter((q) => !q.mockReserved)
  if (!topic || topicQuestions.length === 0) return null

  const [masteryState, attempts] = await Promise.all([
    storage.getMasteryState(topicId),
    storage.listAttempts({ microTopicId: topicId }),
  ])
  const learnerElo = masteryState?.learnerElo ?? DEFAULT_LEARNER_ELO

  const now = Date.now()
  const recentlyCorrectIds = new Set(
    attempts.filter((a) => a.correct && now - a.submittedAt < FOURTEEN_DAYS_MS).map((a) => a.questionId),
  )

  const itemEloEntries = await Promise.all(
    topicQuestions.map(async (q) => ({
      questionId: q.id,
      itemElo: (await storage.getItemElo(q.id)) ?? q.eloRating,
    })),
  )

  // SPEC.md §8.3's "interleaved from earlier mastered/decaying topics" band
  // needs a cross-topic session composer that doesn't exist yet (this page
  // is a single-topic drill harness from Milestone 4) — left empty here,
  // so that 10% of the queue backfills from the current topic instead.
  const queueIds = selectDrillQueue({
    learnerElo,
    currentTopicItems: itemEloEntries,
    interleaveItems: [],
    recentlyCorrectIds,
    size: Math.min(10, topicQuestions.length),
  }).map((c) => c.questionId)

  const byId = new Map(topicQuestions.map((q) => [q.id, q]))
  const queue = queueIds.map((id) => byId.get(id)!)

  return { topic, topicQuestions, queue }
}

export function Drill() {
  const { topicId } = useParams<{ topicId: string }>()
  const [session, setSession] = useState<DrillSession | null | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)
  const [index, setIndex] = useState(0)
  const [results, setResults] = useState<Attempt[]>([])
  const [finalMastery, setFinalMastery] = useState<MasteryState | undefined>(undefined)

  useEffect(() => {
    if (!topicId) return
    setSession(undefined)
    setError(null)
    setIndex(0)
    setResults([])
    setFinalMastery(undefined)
    buildSession(topicId)
      .then(setSession)
      .catch((e: Error) => setError(e.message))
  }, [topicId])

  useEffect(() => {
    if (!topicId || !session || index < session.queue.length) return
    storage.getMasteryState(topicId).then((m) => setFinalMastery(m ? applyDecay(m) : m))
  }, [topicId, session, index])

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

  if (session === undefined) {
    return <main className="mx-auto max-w-2xl p-6 text-muted-foreground">Loading…</main>
  }

  if (session === null) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-muted-foreground">No questions for this micro-topic yet.</p>
        <Link to="/" className="text-primary underline">
          Back
        </Link>
      </main>
    )
  }

  const { topic, topicQuestions, queue } = session

  if (index >= queue.length) {
    const correctCount = results.filter((a) => a.correct).length
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6 text-center">
        <h2 className="text-xl font-semibold">Drill complete</h2>
        <p className="text-muted-foreground">
          {correctCount} / {results.length} correct
        </p>
        {finalMastery && (
          <p className="text-sm text-muted-foreground">
            Mastery status: <span className="font-medium text-foreground">{finalMastery.status}</span> · learner elo{' '}
            {Math.round(finalMastery.learnerElo)}
            {finalMastery.antiFrustrationTriggered && (
              <span className="mt-1 block text-destructive">
                This one needs a rewatch, not more reps.
              </span>
            )}
          </p>
        )}
        <Link to="/">
          <Button>Back to topics</Button>
        </Link>
      </main>
    )
  }

  return (
    <div>
      <div className="mx-auto max-w-2xl px-4 pt-4 text-sm text-muted-foreground">
        Question {index + 1} of {queue.length}
      </div>
      <QuestionPlayer
        key={queue[index].id}
        question={queue[index]}
        mode="drill"
        topic={topic}
        topicQuestions={topicQuestions}
        onComplete={(attempt) => {
          setResults((r) => [...r, attempt])
          setIndex((i) => i + 1)
        }}
      />
    </div>
  )
}
