import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { QuestionPlayer } from '@/components/question-player/QuestionPlayer'
import { Button } from '@/components/ui/button'
import {
  loadExamMeta,
  loadMicroTopic,
  loadQuestion,
  loadQuestionIndex,
  loadQuestionsForMicroTopic,
  topicsWithContent,
} from '@/content/loadContent'
import { generatePlan } from '@/planner/generatePlan'
import { selectDiagnosticQuestions } from '@/planner/diagnosticSelection'
import { storage } from '@/storage'
import type { MicroTopic, Question } from '@/types/content'
import type { Attempt } from '@/types/state'

type Phase = 'intro' | 'loading' | 'questions' | 'done'

/** SPEC.md §10.1: "Start with a 45-minute diagnostic on first launch — ~15 questions spanning
 * sections and difficulty, used to seed learnerElo per section and to identify starting topics."
 * Each attempt goes through the existing QuestionPlayer/recordAttemptForMastery pipeline
 * (Milestone 5), which is what actually seeds MasteryState.learnerElo for whichever micro-topics
 * the diagnostic happens to sample — there's no separate seeding mechanism to build or maintain. */
export function Diagnostic() {
  const navigate = useNavigate()
  const [phase, setPhase] = useState<Phase>('intro')
  const [dailyMinutes, setDailyMinutes] = useState(90)
  const [examDate, setExamDate] = useState('2026-11-29')
  const [questions, setQuestions] = useState<Question[]>([])
  const [topicsByQuestionId, setTopicsByQuestionId] = useState<
    Map<string, { topic: MicroTopic; topicQuestions: Question[] }>
  >(new Map())
  const [index, setIndex] = useState(0)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadExamMeta()
      .then((meta) => setExamDate(meta.examDate))
      .catch(() => undefined)
  }, [])

  async function start() {
    setPhase('loading')
    try {
      const questionIndex = await loadQuestionIndex()
      const picked = selectDiagnosticQuestions(questionIndex, 15)
      const loadedQuestions = await Promise.all(picked.map((entry) => loadQuestion(entry.id)))

      const primaryTopicIds = [...new Set(loadedQuestions.map((q) => q.microTopicIds[0]))]
      const topicEntries = await Promise.all(
        primaryTopicIds.map(async (topicId) => {
          const [topic, topicQuestions] = await Promise.all([
            loadMicroTopic(topicId),
            loadQuestionsForMicroTopic(topicId),
          ])
          return [topicId, topic, topicQuestions] as const
        }),
      )
      const byQuestionId = new Map<string, { topic: MicroTopic; topicQuestions: Question[] }>()
      for (const q of loadedQuestions) {
        const entry = topicEntries.find(([id]) => id === q.microTopicIds[0])
        if (entry?.[1]) byQuestionId.set(q.id, { topic: entry[1], topicQuestions: entry[2] })
      }

      setQuestions(loadedQuestions)
      setTopicsByQuestionId(byQuestionId)
      setIndex(0)
      setPhase('questions')
    } catch (e) {
      setError((e as Error).message)
    }
  }

  async function finish() {
    setPhase('loading')
    const [syllabus, masteryStates] = await Promise.all([topicsWithContent(), storage.listMasteryStates()])
    const masteryByTopicId = new Map(masteryStates.map((m) => [m.microTopicId, m]))
    const today = new Date().toISOString().slice(0, 10)

    const plan = generatePlan({ topics: syllabus, masteryByTopicId, today, examDate, dailyMinutes })
    await Promise.all(plan.days.map((day) => storage.putPlanDay(day)))
    await storage.putSettings({
      schemaVersion: 1,
      dailyMinutes,
      examDate,
      weakSectionBias: null,
      emailOptIn: false,
      diagnosticCompletedAt: Date.now(),
    })
    setPhase('done')
  }

  async function skip() {
    await storage.putSettings({
      schemaVersion: 1,
      dailyMinutes,
      examDate,
      weakSectionBias: null,
      emailOptIn: false,
      diagnosticCompletedAt: Date.now(),
    })
    navigate('/')
  }

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load diagnostic: {error}</p>
      </main>
    )
  }

  if (phase === 'intro') {
    return (
      <main className="mx-auto max-w-2xl space-y-6 p-6">
        <div>
          <h1 className="text-2xl font-semibold">Let's get started</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            A short diagnostic (~15 questions, about 15-20 minutes for now — the full bank will grow
            to a proper 45-minute spread) to see where you're starting from. No pressure — this just
            tells the planner what to skip and what to focus on.
          </p>
        </div>

        <div className="space-y-3 rounded-lg border border-border p-4">
          <label className="block text-sm">
            <span className="mb-1 block font-medium">Minutes you can study per day</span>
            <input
              type="number"
              min={15}
              step={5}
              value={dailyMinutes}
              onChange={(e) => setDailyMinutes(Number(e.target.value))}
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </label>
          <label className="block text-sm">
            <span className="mb-1 block font-medium">Exam date</span>
            <input
              type="date"
              value={examDate}
              onChange={(e) => setExamDate(e.target.value)}
              className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
            />
          </label>
        </div>

        <div className="flex gap-2">
          <Button variant="ghost" onClick={() => void skip()}>
            Skip for now
          </Button>
          <Button onClick={() => void start()}>Start diagnostic</Button>
        </div>
      </main>
    )
  }

  if (phase === 'loading') {
    return <main className="mx-auto max-w-2xl p-6 text-muted-foreground">Loading…</main>
  }

  if (phase === 'done') {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6 text-center">
        <h2 className="text-xl font-semibold">You're set up</h2>
        <p className="text-muted-foreground">Your plan is ready — check the calendar or dive into today's topics.</p>
        <div className="flex justify-center gap-2">
          <Button variant="outline" onClick={() => navigate('/calendar')}>
            View plan
          </Button>
          <Button onClick={() => navigate('/')}>Go to today</Button>
        </div>
      </main>
    )
  }

  // phase === 'questions'
  if (index >= questions.length) {
    void finish()
    return <main className="mx-auto max-w-2xl p-6 text-muted-foreground">Building your plan…</main>
  }

  const question = questions[index]
  const topicInfo = topicsByQuestionId.get(question.id)
  if (!topicInfo) {
    setIndex((i) => i + 1)
    return null
  }

  return (
    <div>
      <div className="mx-auto max-w-2xl px-4 pt-4 text-sm text-muted-foreground">
        Diagnostic — question {index + 1} of {questions.length}
      </div>
      <QuestionPlayer
        key={question.id}
        question={question}
        mode="warmup"
        topic={topicInfo.topic}
        topicQuestions={topicInfo.topicQuestions}
        onComplete={(_attempt: Attempt) => setIndex((i) => i + 1)}
      />
    </div>
  )
}
