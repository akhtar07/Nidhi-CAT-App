import { useEffect, useRef, useState } from 'react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { recordAttemptForMastery } from '@/mastery/masteryEngine'
import { addFormulaCardsForTopic, addMistakeCard } from '@/srs/addToDeck'
import { storage } from '@/storage'
import type { MicroTopic, Question } from '@/types/content'
import type { Attempt } from '@/types/state'
import { Markdown } from './Markdown'

const ERROR_TAGS: NonNullable<Attempt['errorTag']>[] = [
  'concept',
  'calculation',
  'misread',
  'time_pressure',
  'careless_option',
  'unknown_formula',
  'guessed',
]

const CONFIDENCE_LEVELS: NonNullable<Attempt['confidence']>[] = ['guess', 'unsure', 'sure']

function formatSeconds(total: number): string {
  const m = Math.floor(total / 60)
  const s = total % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

/** Shared with the mock engine's scoring (app/src/mock/scoring.ts) — same correctness rule
 * everywhere an Attempt's `correct` flag is derived. */
export function computeCorrect(question: Question, given: string | null): boolean {
  if (given === null) return false
  if (question.format === 'mcq') {
    return given === question.correctKey
  }
  const correctValue = question.correctValue
  if (typeof correctValue === 'number') {
    const numGiven = Number(given)
    if (Number.isNaN(numGiven)) return false
    const tolerance = question.titaTolerance ?? 0
    return Math.abs(numGiven - correctValue) <= tolerance
  }
  return given.trim().toLowerCase() === String(correctValue).trim().toLowerCase()
}

type Phase = 'answering' | 'confidence' | 'revealed'

export interface QuestionPlayerProps {
  question: Question
  mode: Attempt['mode']
  /** The micro-topic being drilled, and all of its questions — used to update the Milestone 5 mastery engine after each attempt. */
  topic: MicroTopic
  topicQuestions: Question[]
  onComplete: (attempt: Attempt) => void
}

export function QuestionPlayer({ question, mode, topic, topicQuestions, onComplete }: QuestionPlayerProps) {
  const [phase, setPhase] = useState<Phase>('answering')
  const [selectedKey, setSelectedKey] = useState<string | null>(null)
  const [titaValue, setTitaValue] = useState('')
  const [markedForReview, setMarkedForReview] = useState(false)
  const [confidence, setConfidence] = useState<Attempt['confidence']>(undefined)
  const [errorTag, setErrorTag] = useState<Attempt['errorTag']>(undefined)
  const [elapsedSec, setElapsedSec] = useState(0)

  const startedAtRef = useRef(Date.now())
  const submittedAtRef = useRef<number | null>(null)
  const givenRef = useRef<string | null>(null)

  // Reset all state when a new question is shown.
  useEffect(() => {
    setPhase('answering')
    setSelectedKey(null)
    setTitaValue('')
    setMarkedForReview(false)
    setConfidence(undefined)
    setErrorTag(undefined)
    setElapsedSec(0)
    startedAtRef.current = Date.now()
    submittedAtRef.current = null
    givenRef.current = null
  }, [question.id])

  useEffect(() => {
    if (phase !== 'answering') return
    const interval = setInterval(() => setElapsedSec((s) => s + 1), 1000)
    return () => clearInterval(interval)
  }, [phase])

  const canSubmit = question.format === 'mcq' ? selectedKey !== null : titaValue.trim() !== ''

  function submit() {
    givenRef.current = question.format === 'mcq' ? selectedKey : titaValue.trim()
    submittedAtRef.current = Date.now()
    setPhase('confidence')
  }

  function skip() {
    givenRef.current = null
    submittedAtRef.current = Date.now()
    setPhase('revealed')
  }

  function chooseConfidence(level: NonNullable<Attempt['confidence']>) {
    setConfidence(level)
    setPhase('revealed')
  }

  const correct = computeCorrect(question, givenRef.current)

  function next() {
    const attempt: Attempt = {
      schemaVersion: 1,
      id: crypto.randomUUID(),
      questionId: question.id,
      microTopicIds: question.microTopicIds,
      startedAt: startedAtRef.current,
      submittedAt: submittedAtRef.current ?? Date.now(),
      timeSpentSec: Math.round(((submittedAtRef.current ?? Date.now()) - startedAtRef.current) / 1000),
      given: givenRef.current,
      correct,
      ...(confidence ? { confidence } : {}),
      ...(errorTag ? { errorTag } : {}),
      mode,
      markedForReview,
    }
    void storage.addAttempt(attempt).then(() => recordAttemptForMastery({ attempt, question, topic, topicQuestions }))
    if (!correct) {
      void addMistakeCard(question.id, topic.id, storage)
      if (errorTag === 'unknown_formula') void addFormulaCardsForTopic(topic.id, storage)
    }
    onComplete(attempt)
  }

  return (
    <div className="mx-auto max-w-2xl space-y-4 p-4">
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <span>
          {question.difficulty} · {question.format.toUpperCase()}
        </span>
        <span>
          {formatSeconds(elapsedSec)} <span className="opacity-60">/ target {formatSeconds(question.targetSeconds)}</span>
        </span>
      </div>

      <div className="text-base leading-relaxed">
        <Markdown text={question.stemMarkdown} />
      </div>

      {phase === 'answering' && (
        <>
          {question.format === 'mcq' ? (
            <div className="space-y-2" role="radiogroup" aria-label="Answer options">
              {question.options?.map((opt) => (
                <button
                  key={opt.key}
                  type="button"
                  role="radio"
                  aria-checked={selectedKey === opt.key}
                  onClick={() => setSelectedKey(opt.key)}
                  className={cn(
                    'flex w-full items-start gap-2 rounded-lg border px-3 py-2 text-left text-sm transition-colors',
                    selectedKey === opt.key
                      ? 'border-primary bg-primary/10'
                      : 'border-border hover:bg-muted',
                  )}
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

          <div className="flex items-center justify-between pt-2">
            <label className="flex items-center gap-2 text-sm text-muted-foreground">
              <input
                type="checkbox"
                checked={markedForReview}
                onChange={(e) => setMarkedForReview(e.target.checked)}
              />
              Mark for review
            </label>
            <div className="flex gap-2">
              <Button variant="ghost" onClick={skip}>
                Skip
              </Button>
              <Button disabled={!canSubmit} onClick={submit}>
                Submit
              </Button>
            </div>
          </div>
        </>
      )}

      {phase === 'confidence' && (
        <div className="space-y-2">
          <p className="text-sm font-medium">How confident were you?</p>
          <div className="flex gap-2">
            {CONFIDENCE_LEVELS.map((level) => (
              <Button key={level} variant="outline" onClick={() => chooseConfidence(level)}>
                {level}
              </Button>
            ))}
          </div>
        </div>
      )}

      {phase === 'revealed' && (
        <div className="space-y-4">
          <div
            className={cn(
              'rounded-lg px-3 py-2 text-sm font-medium',
              correct ? 'bg-primary/10 text-primary' : 'bg-destructive/10 text-destructive',
            )}
          >
            {givenRef.current === null ? 'Skipped.' : correct ? 'Correct!' : 'Incorrect.'}
            {question.format === 'tita' && !correct && (
              <span className="ml-1 font-normal">Correct answer: {question.correctValue}</span>
            )}
            {question.format === 'mcq' && !correct && (
              <span className="ml-1 font-normal">Correct answer: {question.correctKey}</span>
            )}
          </div>

          <div className="text-sm leading-relaxed">
            <p className="mb-1 font-medium">Solution</p>
            <Markdown text={question.solutionMarkdown} />
          </div>

          {question.altSolutionMarkdown && (
            <div className="text-sm leading-relaxed">
              <p className="mb-1 font-medium">Smart approach</p>
              <Markdown text={question.altSolutionMarkdown} />
            </div>
          )}

          {!correct && (
            <div className="space-y-2">
              <p className="text-sm font-medium">What went wrong? (optional)</p>
              <div className="flex flex-wrap gap-2">
                {ERROR_TAGS.map((tag) => (
                  <button
                    key={tag}
                    type="button"
                    onClick={() => setErrorTag(tag)}
                    className={cn(
                      'rounded-full border px-2.5 py-1 text-xs transition-colors',
                      errorTag === tag ? 'border-primary bg-primary/10' : 'border-border hover:bg-muted',
                    )}
                  >
                    {tag.replace(/_/g, ' ')}
                  </button>
                ))}
              </div>
            </div>
          )}

          <Button onClick={next}>Next</Button>
        </div>
      )}
    </div>
  )
}
