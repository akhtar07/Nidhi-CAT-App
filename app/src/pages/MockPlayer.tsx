import { useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { Markdown } from '@/components/question-player/Markdown'
import { computeCorrect } from '@/components/question-player/QuestionPlayer'
import { Button } from '@/components/ui/button'
import { Calculator } from '@/components/mock-player/Calculator'
import { Palette } from '@/components/mock-player/Palette'
import { loadMicroTopic, loadMockDefinition, loadQuestion, loadQuestionsForMicroTopic } from '@/content/loadContent'
import { recordAttemptForMastery } from '@/mastery/masteryEngine'
import { computeAllSectionScores } from '@/mock/scoring'
import { formatMMSS, remainingSeconds } from '@/mock/timing'
import { storage } from '@/storage'
import type { MockDefinition, Question } from '@/types/content'
import type { Attempt, MockQuestionState, MockSession, Section } from '@/types/state'

const PERSIST_INTERVAL_MS = 5000
const WARNING_THRESHOLD_SEC = 10

function freshSession(mockId: string): MockSession {
  const now = Date.now()
  return {
    schemaVersion: 1,
    mockId,
    startedAt: now,
    currentSectionIndex: 0,
    sectionStartedAt: now,
    currentQuestionIndex: 0,
    questionStates: {},
    completedSectionIndices: [],
  }
}

function withDwell(session: MockSession, questionId: string | undefined, sinceMs: number): MockSession {
  if (!questionId) return session
  const elapsed = Math.max(0, Math.round((Date.now() - sinceMs) / 1000))
  const prev = session.questionStates[questionId] ?? {
    given: null,
    markedForReview: false,
    visitCount: 0,
    dwellSec: 0,
  }
  return {
    ...session,
    questionStates: { ...session.questionStates, [questionId]: { ...prev, dwellSec: prev.dwellSec + elapsed } },
  }
}

function withVisit(session: MockSession, questionId: string | undefined): MockSession {
  if (!questionId) return session
  const prev = session.questionStates[questionId] ?? {
    given: null,
    markedForReview: false,
    visitCount: 0,
    dwellSec: 0,
  }
  return {
    ...session,
    questionStates: { ...session.questionStates, [questionId]: { ...prev, visitCount: prev.visitCount + 1 } },
  }
}

export function MockPlayer() {
  const { mockId } = useParams<{ mockId: string }>()
  const navigate = useNavigate()

  const [mockDef, setMockDef] = useState<MockDefinition | null>(null)
  const [questionsById, setQuestionsById] = useState<Map<string, Question>>(new Map())
  const [error, setError] = useState<string | null>(null)
  const [session, setSession] = useState<MockSession | null>(null)
  const [phase, setPhase] = useState<'intro' | 'in_progress' | 'complete'>('intro')
  const [now, setNow] = useState(() => Date.now())
  const [showCalculator, setShowCalculator] = useState(false)
  const [titaValue, setTitaValue] = useState('')

  const visitStartedAtRef = useRef(Date.now())
  const finishingRef = useRef(false)

  useEffect(() => {
    if (!mockId) return
    Promise.all([loadMockDefinition(mockId), storage.getMockSession()])
      .then(async ([def, existingSession]) => {
        const questions = await Promise.all(
          def.sections.flatMap((s) => s.questionIds ?? []).map((id) => loadQuestion(id)),
        )
        setQuestionsById(new Map(questions.map((q) => [q.id, q])))
        setMockDef(def)
        if (existingSession && existingSession.mockId === mockId) {
          setSession(existingSession)
          setPhase('in_progress')
        }
      })
      .catch((e: Error) => setError(e.message))
  }, [mockId])

  useEffect(() => {
    const t = setInterval(() => setNow(Date.now()), 1000)
    return () => clearInterval(t)
  }, [])

  useEffect(() => {
    if (phase !== 'in_progress') return
    const t = setInterval(() => {
      setSession((s) => {
        if (!s) return s
        void storage.putMockSession(s)
        return s
      })
    }, PERSIST_INTERVAL_MS)
    return () => clearInterval(t)
  }, [phase])

  // SPEC.md §9.1: exit warning on attempted navigation away.
  useEffect(() => {
    if (phase !== 'in_progress') return
    function handler(e: BeforeUnloadEvent) {
      e.preventDefault()
      e.returnValue = ''
    }
    window.addEventListener('beforeunload', handler)
    return () => window.removeEventListener('beforeunload', handler)
  }, [phase])

  const currentSection = mockDef?.sections[session?.currentSectionIndex ?? -1]
  const currentSectionQuestionIds = useMemo(() => currentSection?.questionIds ?? [], [currentSection])
  const remaining =
    session && currentSection ? remainingSeconds(session.sectionStartedAt, currentSection.minutes, now) : 0

  function finishMock(finalSession?: MockSession) {
    const activeSession = finalSession ?? session
    if (finishingRef.current || !mockDef || !activeSession) return
    finishingRef.current = true
    void (async () => {
      const questionsBySection: Record<Section, Question[]> = { VARC: [], DILR: [], QA: [] }
      for (const s of mockDef.sections) {
        questionsBySection[s.section] = (s.questionIds ?? []).map((id) => questionsById.get(id)!).filter(Boolean)
      }
      const sectionScores = computeAllSectionScores(questionsBySection, activeSession.questionStates)
      const questionTimings: Record<string, number> = {}
      for (const [qid, state] of Object.entries(activeSession.questionStates)) questionTimings[qid] = state.dwellSec

      await storage.addMockResult({
        schemaVersion: 1,
        id: crypto.randomUUID(),
        mockId: mockDef.id,
        takenAt: Date.now(),
        sectionScores,
        questionTimings,
      })

      // Log a real Attempt (mode: 'mock') per question that was shown, and feed mastery — same
      // pipeline QuestionPlayer/Diagnostic use, so mock performance isn't invisible to the engine.
      for (const s of mockDef.sections) {
        for (const qid of s.questionIds ?? []) {
          const question = questionsById.get(qid)
          if (!question) continue
          const qState = activeSession.questionStates[qid]
          const given = qState?.given ?? null
          const attempt: Attempt = {
            schemaVersion: 1,
            id: crypto.randomUUID(),
            questionId: qid,
            microTopicIds: question.microTopicIds,
            startedAt: activeSession.startedAt,
            submittedAt: Date.now(),
            timeSpentSec: qState?.dwellSec ?? 0,
            given,
            correct: given !== null ? computeCorrect(question, given) : false,
            mode: 'mock',
            markedForReview: qState?.markedForReview ?? false,
          }
          await storage.addAttempt(attempt)
          const topic = await loadMicroTopic(question.microTopicIds[0])
          if (topic) {
            const topicQuestions = await loadQuestionsForMicroTopic(topic.id)
            await recordAttemptForMastery({ attempt, question, topic, topicQuestions })
          }
        }
      }

      await storage.clearMockSession()
      setPhase('complete')
    })()
  }

  useEffect(() => {
    if (phase === 'in_progress' && remaining <= 0 && currentSection) {
      advanceSection()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [remaining, phase])

  function advanceSection() {
    if (!mockDef || !session) return
    const isLast = session.currentSectionIndex >= mockDef.sections.length - 1
    const withFinalDwell = withDwell(session, currentSectionQuestionIds[session.currentQuestionIndex], visitStartedAtRef.current)
    if (isLast) {
      const finalSession: MockSession = {
        ...withFinalDwell,
        completedSectionIndices: [...withFinalDwell.completedSectionIndices, session.currentSectionIndex],
      }
      setSession(finalSession)
      finishMock(finalSession)
      return
    }
    const nextIndex = session.currentSectionIndex + 1
    const nextQid = mockDef.sections[nextIndex]?.questionIds?.[0]
    let next: MockSession = {
      ...withFinalDwell,
      completedSectionIndices: [...withFinalDwell.completedSectionIndices, session.currentSectionIndex],
      currentSectionIndex: nextIndex,
      sectionStartedAt: Date.now(),
      currentQuestionIndex: 0,
    }
    next = withVisit(next, nextQid)
    visitStartedAtRef.current = Date.now()
    setSession(next)
    void storage.putMockSession(next)
    setTitaValue('')
  }

  function begin() {
    if (!mockDef) return
    const s = withVisit(freshSession(mockDef.id), mockDef.sections[0]?.questionIds?.[0])
    visitStartedAtRef.current = Date.now()
    setSession(s)
    setPhase('in_progress')
    void storage.putMockSession(s)
    document.documentElement.requestFullscreen?.().catch(() => undefined)
  }

  function currentAnswerInput(question: Question | undefined): string {
    if (!question) return ''
    const state = session?.questionStates[question.id]
    return question.format === 'tita' ? titaValue : (state?.given ?? '')
  }

  /** The single atomic state transition for "leave the current question": commits its dwell
   * time, applies any given/markedForReview override, optionally moves to a new index within the
   * section, and marks the destination visited. Every navigation/answer action goes through this
   * one functional setSession call so nothing composes two stale-closure updates in a row. */
  /** commitAndGoTo is only ever invoked once per event handler (never composed back-to-back
   * synchronously), so — unlike a functional setSession updater, whose callback React defers to
   * the render pass rather than running inline (confirmed via live testing: an immediate
   * post-setSession read of a value captured inside the updater was reliably still null) —
   * computing `next` directly from the current `session` closure here is safe, and lets the
   * result be persisted immediately rather than waiting for the next 5-second autosave tick. */
  function commitAndGoTo(newIndex: number, overrides?: Partial<Pick<MockQuestionState, 'given' | 'markedForReview'>>) {
    if (!session) return
    const dwellSince = visitStartedAtRef.current
    visitStartedAtRef.current = Date.now()

    const currentQid = currentSectionQuestionIds[session.currentQuestionIndex]
    let next = withDwell(session, currentQid, dwellSince)
    if (currentQid && overrides) {
      const priorState = next.questionStates[currentQid] ?? {
        given: null,
        markedForReview: false,
        visitCount: 0,
        dwellSec: 0,
      }
      next = {
        ...next,
        questionStates: { ...next.questionStates, [currentQid]: { ...priorState, ...overrides } },
      }
    }
    const newQid = currentSectionQuestionIds[newIndex]
    next = { ...next, currentQuestionIndex: newIndex }
    if (newIndex !== session.currentQuestionIndex) next = withVisit(next, newQid)

    setSession(next)
    void storage.putMockSession(next)
    const nq = newQid ? questionsById.get(newQid) : undefined
    if (nq?.format === 'tita') {
      const priorGiven =
        newIndex === session?.currentQuestionIndex && overrides?.given !== undefined
          ? overrides.given
          : session?.questionStates[newQid!]?.given
      setTitaValue(priorGiven ?? '')
    } else {
      setTitaValue('')
    }
  }

  function goToQuestionInSection(newIndex: number) {
    commitAndGoTo(newIndex)
  }

  function setGiven(given: string | null) {
    if (!session) return
    commitAndGoTo(session.currentQuestionIndex, { given })
  }

  function clearAnswer() {
    setGiven(null)
    setTitaValue('')
  }

  function saveAndNext() {
    if (!session) return
    const question = questionsById.get(currentSectionQuestionIds[session.currentQuestionIndex])
    const given = question?.format === 'tita' ? titaValue || null : undefined
    const nextIndex = Math.min(session.currentQuestionIndex + 1, currentSectionQuestionIds.length - 1)
    commitAndGoTo(nextIndex, given !== undefined ? { given } : undefined)
  }

  function markForReviewAndNext() {
    if (!session) return
    const qid = currentSectionQuestionIds[session.currentQuestionIndex]
    const question = questionsById.get(qid)
    const currentlyMarked = session.questionStates[qid]?.markedForReview ?? false
    const given = question?.format === 'tita' ? titaValue || null : session.questionStates[qid]?.given
    const nextIndex = Math.min(session.currentQuestionIndex + 1, currentSectionQuestionIds.length - 1)
    commitAndGoTo(nextIndex, { markedForReview: !currentlyMarked, given: given ?? null })
  }

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load mock: {error}</p>
      </main>
    )
  }

  if (!mockDef) {
    return <main className="mx-auto max-w-2xl p-6 text-muted-foreground">Loading…</main>
  }

  if (phase === 'intro') {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6">
        <h1 className="text-2xl font-semibold">{mockDef.title}</h1>
        <div className="space-y-1 text-sm text-muted-foreground">
          {mockDef.sections.map((s) => (
            <p key={s.section}>
              {s.section}: {s.minutes} min, {(s.questionIds ?? []).length} question
              {(s.questionIds ?? []).length === 1 ? '' : 's'}
            </p>
          ))}
        </div>
        {mockDef.composedNote && (
          <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-3 text-sm">
            {mockDef.composedNote}
          </div>
        )}
        <div className="rounded-lg border border-border p-3 text-sm text-muted-foreground">
          Sections run in order and are hard-locked — once a section's time is up (or you finish
          it), you cannot go back. The whole test attempts to go full-screen.
        </div>
        <Button onClick={begin}>Begin mock</Button>
      </main>
    )
  }

  if (phase === 'complete') {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6 text-center">
        <h2 className="text-xl font-semibold">Mock complete</h2>
        <p className="text-muted-foreground">
          Detailed analysis is coming in a later milestone — for now, your attempts and section
          scores are saved.
        </p>
        <Button onClick={() => navigate('/')}>Back to today</Button>
      </main>
    )
  }

  // phase === 'in_progress'
  if (!session || !currentSection) {
    return <main className="mx-auto max-w-2xl p-6 text-muted-foreground">Finishing up…</main>
  }
  const currentQid = currentSectionQuestionIds[session.currentQuestionIndex]
  const question = questionsById.get(currentQid)

  return (
    <div className="mx-auto max-w-5xl p-4">
      <div className="mb-3 flex items-center justify-between rounded-lg border border-border px-3 py-2 text-sm">
        <span className="font-medium">
          {currentSection.section} · Question {session.currentQuestionIndex + 1} of {currentSectionQuestionIds.length}
        </span>
        <span className={remaining <= WARNING_THRESHOLD_SEC ? 'font-semibold text-destructive' : 'tabular-nums'}>
          {formatMMSS(remaining)}
          {remaining <= WARNING_THRESHOLD_SEC && remaining > 0 && ' — section ending!'}
        </span>
        <Button variant="outline" onClick={() => setShowCalculator((v) => !v)}>
          Calculator
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-[1fr_auto]">
        <div className="space-y-4 rounded-lg border border-border p-4">
          {question ? (
            <>
              <div className="text-base leading-relaxed">
                <Markdown text={question.stemMarkdown} />
              </div>
              {question.format === 'mcq' ? (
                <div className="space-y-2" role="radiogroup" aria-label="Answer options">
                  {question.options?.map((opt) => (
                    <button
                      key={opt.key}
                      type="button"
                      role="radio"
                      aria-checked={currentAnswerInput(question) === opt.key}
                      onClick={() => setGiven(opt.key)}
                      className={`flex w-full items-start gap-2 rounded-lg border px-3 py-2 text-left text-sm transition-colors ${
                        currentAnswerInput(question) === opt.key
                          ? 'border-primary bg-primary/10'
                          : 'border-border hover:bg-muted'
                      }`}
                    >
                      <span className="font-medium">{opt.key}.</span>
                      <span>
                        <Markdown text={opt.markdown} />
                      </span>
                    </button>
                  ))}
                </div>
              ) : (
                <input
                  type="text"
                  inputMode="decimal"
                  value={titaValue}
                  onChange={(e) => setTitaValue(e.target.value)}
                  placeholder="Enter your answer"
                  className="w-full rounded-lg border border-border bg-background px-3 py-2 text-sm outline-none focus-visible:ring-3 focus-visible:ring-ring/50"
                />
              )}
              <div className="flex flex-wrap gap-2 pt-2">
                <Button variant="ghost" onClick={clearAnswer}>
                  Clear
                </Button>
                <Button variant="outline" onClick={markForReviewAndNext}>
                  Mark for Review &amp; Next
                </Button>
                <Button onClick={saveAndNext}>Save &amp; Next</Button>
              </div>
            </>
          ) : (
            <p className="text-muted-foreground">No question available.</p>
          )}
        </div>

        <div className="w-full md:w-48">
          <p className="mb-2 text-sm font-medium text-muted-foreground">Questions</p>
          <Palette
            questionIds={currentSectionQuestionIds}
            questionStates={session.questionStates}
            currentIndex={session.currentQuestionIndex}
            onJump={goToQuestionInSection}
          />
        </div>
      </div>

      {showCalculator && <Calculator onClose={() => setShowCalculator(false)} />}
    </div>
  )
}
