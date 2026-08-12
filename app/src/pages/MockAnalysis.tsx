import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import {
  computeAccuracyVsAttemptsCurve,
  computeBleederReport,
  computeMicroTopicDamage,
  computeSelectionQuality,
  computeTimeWaterfall,
  computeTitaDiscipline,
  type AccuracyVsAttemptsResult,
  type BleederEntry,
  type MicroTopicDamage,
  type SelectionQuality,
  type TimeWaterfallEntry,
  type TitaBlankEntry,
} from '@/mock/analysis'
import { estimatePercentile } from '@/mock/percentile'
import { Skeleton } from '@/components/ui/Skeleton'
import { loadMicroTopic, loadMockDefinition, loadQuestion } from '@/content/loadContent'
import { cn } from '@/lib/utils'
import { storage } from '@/storage'
import type { MockDefinition } from '@/types/content'
import type { MockResult, Section } from '@/types/state'

const SECTION_COLORS: Record<Section, string> = {
  QA: 'var(--color-primary)',
  DILR: '#f59e0b',
  VARC: '#22c55e',
}
const SECTION_ORDER: Section[] = ['VARC', 'DILR', 'QA']

/** Visual sectional score breakdown — same plain-SVG-from-data discipline as PassageSetPlayer's
 * chart renderers (SPEC.md §5.1). MockAnalysis already computed every number here (the waterfall
 * section below shows the same marks per section as text); this is a rendering addition, not a
 * new scoring computation. */
function SectionScoreChart({ sectionScores }: { sectionScores: MockResult['sectionScores'] }) {
  const maxAbs = Math.max(1, ...SECTION_ORDER.map((s) => Math.abs(sectionScores[s]?.score ?? 0)))
  const barHeight = 28
  const gap = 12

  return (
    <div className="space-y-2 rounded-lg border border-border p-4">
      {SECTION_ORDER.map((section) => {
        const score = sectionScores[section]?.score ?? 0
        const widthPct = (Math.abs(score) / maxAbs) * 100
        return (
          <div key={section} className="flex items-center gap-3 text-sm" style={{ height: barHeight }}>
            <span className="w-12 shrink-0 text-muted-foreground">{section}</span>
            <div className="h-full flex-1 overflow-hidden rounded-md bg-muted">
              <div
                className="h-full rounded-md transition-[width]"
                style={{ width: `${widthPct}%`, backgroundColor: score < 0 ? 'var(--color-destructive)' : SECTION_COLORS[section] }}
              />
            </div>
            <span className={cn('w-10 shrink-0 text-right font-medium', score < 0 && 'text-destructive')}>{score}</span>
          </div>
        )
      })}
      <p className="pt-1 text-xs text-muted-foreground" style={{ marginTop: gap - 8 }}>
        Marks per section (negative marking already applied).
      </p>
    </div>
  )
}

const REMEDIATION_TOPIC_COUNT = 3

interface AnalysisData {
  result: MockResult
  mockDef: MockDefinition
  totalScore: number
  percentile: ReturnType<typeof estimatePercentile>
  waterfall: TimeWaterfallEntry[]
  bleeders: BleederEntry[]
  selectionQuality: SelectionQuality
  titaBlanks: TitaBlankEntry[]
  accuracyCurve: AccuracyVsAttemptsResult
  damage: MicroTopicDamage[]
  topicNameById: Map<string, string>
}

async function loadAnalysis(resultId: string): Promise<AnalysisData | null> {
  const results = await storage.listMockResults()
  const result = results.find((r) => r.id === resultId)
  if (!result) return null

  const mockDef = await loadMockDefinition(result.mockId)
  const allQuestionIds = mockDef.sections.flatMap((s) => s.questionIds ?? [])
  const questions = await Promise.all(allQuestionIds.map((id) => loadQuestion(id)))
  const questionsById = new Map(questions.map((q) => [q.id, q]))

  const allAttempts = await storage.listAttempts({ mode: 'mock' })
  const attempts = allAttempts.filter((a) => a.startedAt === result.startedAt && questionsById.has(a.questionId))

  const itemEloByQuestionId = new Map<string, number>(
    await Promise.all(
      questions.map(async (q) => [q.id, (await storage.getItemElo(q.id)) ?? q.eloRating] as [string, number]),
    ),
  )

  const totalScore = Object.values(result.sectionScores).reduce((sum, s) => sum + s.score, 0)
  const damage = computeMicroTopicDamage(attempts, questionsById)

  const topicNames = await Promise.all(
    damage.map(async (d) => [d.microTopicId, (await loadMicroTopic(d.microTopicId))?.name ?? d.microTopicId] as [
      string,
      string,
    ]),
  )

  return {
    result,
    mockDef,
    totalScore,
    percentile: estimatePercentile(totalScore),
    waterfall: computeTimeWaterfall(mockDef, result),
    bleeders: computeBleederReport(attempts, questionsById),
    selectionQuality: computeSelectionQuality(attempts, questionsById, itemEloByQuestionId),
    titaBlanks: computeTitaDiscipline(attempts, questionsById),
    accuracyCurve: computeAccuracyVsAttemptsCurve(attempts, questionsById, itemEloByQuestionId),
    damage,
    topicNameById: new Map(topicNames),
  }
}

/** SPEC.md §9.3: "the mock's output *must* write back into the plan. A mock that doesn't change
 * tomorrow's schedule is a wasted mock." Adds a review item for each of the top damaged topics to
 * tomorrow's PlanDay (if not already present) — automatic, not a manual per-topic click, since a
 * report nobody acts on doesn't fulfil the requirement either. */
async function writeRemediationIntoPlan(damage: MicroTopicDamage[]): Promise<string[]> {
  const top = damage.slice(0, REMEDIATION_TOPIC_COUNT).map((d) => d.microTopicId)
  if (top.length === 0) return []

  const tomorrow = new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString().slice(0, 10)
  const existing = (await storage.getPlanDay(tomorrow)) ?? {
    schemaVersion: 1 as const,
    date: tomorrow,
    items: [],
    status: 'pending' as const,
  }

  const alreadyPlanned = new Set(existing.items.map((i) => i.microTopicId))
  const added = top.filter((id) => !alreadyPlanned.has(id))
  if (added.length === 0) return []

  const updated = {
    ...existing,
    items: [
      ...existing.items,
      ...added.map((microTopicId) => ({ microTopicId, kind: 'review' as const, done: false })),
    ],
  }
  await storage.putPlanDay(updated)
  return added
}

export function MockAnalysis() {
  const { resultId } = useParams<{ resultId: string }>()
  const [data, setData] = useState<AnalysisData | null | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)
  const [remediationStatus, setRemediationStatus] = useState<string | null>(null)

  useEffect(() => {
    if (!resultId) return
    setData(undefined)
    setError(null)
    setRemediationStatus(null)
    loadAnalysis(resultId)
      .then(async (d) => {
        setData(d)
        if (d && d.damage.length > 0) {
          const added = await writeRemediationIntoPlan(d.damage)
          if (added.length > 0) {
            const names = added.map((id) => d.topicNameById.get(id) ?? id).join(', ')
            setRemediationStatus(`Added to tomorrow's plan: ${names}`)
          }
        }
      })
      .catch((e: Error) => setError(e.message))
  }, [resultId])

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load analysis: {error}</p>
      </main>
    )
  }
  if (data === undefined) {
    return (
      <main className="mx-auto max-w-2xl space-y-6 p-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-40 w-full" />
      </main>
    )
  }
  if (data === null) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-muted-foreground">No such mock result.</p>
        <Link to="/" className="text-primary underline">
          Back
        </Link>
      </main>
    )
  }

  const {
    result,
    totalScore,
    percentile,
    waterfall,
    bleeders,
    selectionQuality,
    titaBlanks,
    accuracyCurve,
    damage,
    topicNameById,
  } = data

  return (
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <div>
        <Link to="/" className="text-sm text-primary underline">
          Back
        </Link>
        <h1 className="mt-2 text-2xl font-semibold">{data.mockDef.title} — Analysis</h1>
      </div>

      <section className="rounded-lg border border-border p-4">
        <div className="flex items-baseline justify-between">
          <p className="text-3xl font-semibold">{totalScore}</p>
          <Link to="/progress" className="text-xs text-primary underline">
            View trend across mocks
          </Link>
        </div>
        <p className="text-sm text-muted-foreground">
          Estimated {percentile.percentile}%ile · {percentile.disclaimer}
        </p>
      </section>

      <SectionScoreChart sectionScores={result.sectionScores} />

      {remediationStatus && (
        <div className="rounded-lg border border-primary/40 bg-primary/10 p-3 text-sm">{remediationStatus}</div>
      )}

      <section>
        <h2 className="mb-2 text-sm font-medium text-muted-foreground">Time vs. marks by section</h2>
        <ul className="divide-y divide-border rounded-lg border border-border">
          {waterfall.map((w) => (
            <li key={w.section} className="flex items-center justify-between px-4 py-2 text-sm">
              <span>{w.section}</span>
              <span className="text-muted-foreground">
                {w.minutesSpent} min · {w.marksEarned} marks
              </span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h2 className="mb-2 text-sm font-medium text-muted-foreground">
          Bleeder report — slow and wrong (&gt;150s)
        </h2>
        {bleeders.length === 0 ? (
          <p className="text-sm text-muted-foreground">None — no question both wasted time and lost marks.</p>
        ) : (
          <ul className="divide-y divide-border rounded-lg border border-border">
            {bleeders.map((b) => (
              <li key={b.questionId} className="px-4 py-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-destructive">{Math.round(b.timeSpentSec / 60)} min, wrong</span>
                </div>
                <p className="text-muted-foreground">{b.stemPreview}…</p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="rounded-lg border border-border p-4 text-sm">
        <h2 className="mb-1 font-medium text-muted-foreground">Selection quality</h2>
        <p>
          Skipped {selectionQuality.skippedCount} question{selectionQuality.skippedCount === 1 ? '' : 's'}
          {selectionQuality.skippedCount > 0 && (
            <>
              , {Math.round(selectionQuality.easySkipFraction * 100)}% of them easier than this mock's median item.
              {selectionQuality.easySkipFraction > 0.3 && (
                <span className="ml-1 text-amber-500">High — you're skipping questions you could likely solve.</span>
              )}
            </>
          )}
        </p>
      </section>

      {titaBlanks.length > 0 && (
        <section className="rounded-lg border border-destructive/40 bg-destructive/5 p-4 text-sm">
          <h2 className="mb-1 font-medium">
            TITA discipline: {titaBlanks.length} blank TITA question{titaBlanks.length === 1 ? '' : 's'}
          </h2>
          <p className="text-muted-foreground">
            TITA has no negative marking — leaving one blank is a pure unforced error. Always guess.
          </p>
        </section>
      )}

      <section>
        <h2 className="mb-2 text-sm font-medium text-muted-foreground">Accuracy vs. attempts</h2>
        <p className="text-sm">
          You attempted {accuracyCurve.actualAttemptCount}; the score-maximizing cutoff (attempting your easiest
          questions first) was <span className="font-medium">{accuracyCurve.optimalAttemptCount}</span>.
        </p>
      </section>

      {damage.length > 0 && (
        <section>
          <h2 className="mb-2 text-sm font-medium text-muted-foreground">Micro-topic damage</h2>
          <ul className="divide-y divide-border rounded-lg border border-border">
            {damage.map((d) => (
              <li key={d.microTopicId} className="flex items-center justify-between px-4 py-2 text-sm">
                <span>{topicNameById.get(d.microTopicId) ?? d.microTopicId}</span>
                <span className="flex items-center gap-2">
                  <span className="text-destructive">-{d.marksLost}</span>
                  <Link to={`/lesson/${d.microTopicId}`} className="text-xs text-primary underline">
                    Practice
                  </Link>
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}

      <p className="text-xs text-muted-foreground">Mock taken {new Date(result.takenAt).toLocaleString()}</p>
    </main>
  )
}
