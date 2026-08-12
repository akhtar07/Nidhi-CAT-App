import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { loadMockDefinition } from '@/content/loadContent'
import { computeScoreTrend, type ProgressPoint } from '@/mock/progressTrend'
import { storage } from '@/storage'

const MAX_SCORE = 204

interface TrendRow extends ProgressPoint {
  mockTitle: string
}

async function loadTrend(): Promise<TrendRow[]> {
  const results = await storage.listMockResults()
  const trend = computeScoreTrend(results)
  const byId = new Map(results.map((r) => [r.id, r]))
  const titleCache = new Map<string, string>()

  return Promise.all(
    trend.map(async (point) => {
      const mockId = byId.get(point.mockResultId)?.mockId
      if (mockId && !titleCache.has(mockId)) {
        const def = await loadMockDefinition(mockId).catch(() => null)
        titleCache.set(mockId, def?.title ?? mockId)
      }
      return { ...point, mockTitle: mockId ? (titleCache.get(mockId) ?? mockId) : 'Mock' }
    }),
  )
}

/** Single-axis SVG line chart of total score across a learner's mock history — same plain-SVG,
 * no-charting-library discipline as PassageSetPlayer's chart renderers (SPEC.md §5.1).
 * Percentile is shown as a direct label per point rather than a second y-axis (a dual-axis chart
 * with two different scales is the #1 chart-reading mistake — score and percentile are shown
 * together per point instead). */
function ScoreTrendChart({ points }: { points: TrendRow[] }) {
  const width = Math.max(280, points.length * 90)
  const height = 220
  const padTop = 24
  const padBottom = 32
  const padX = 24
  const plotHeight = height - padTop - padBottom
  const plotWidth = width - padX * 2

  const xFor = (i: number) => padX + (points.length > 1 ? (i / (points.length - 1)) * plotWidth : plotWidth / 2)
  const yFor = (score: number) => padTop + plotHeight - (score / MAX_SCORE) * plotHeight

  const linePoints = points.map((p, i) => `${xFor(i)},${yFor(p.totalScore)}`).join(' ')

  return (
    <div className="overflow-x-auto rounded-lg border border-border p-3">
      <svg width={width} height={height} role="img" aria-label="Score trend across mocks">
        {/* Recessive gridlines at 25/50/75% of max score, per the calm/data-forward aesthetic. */}
        {[0.25, 0.5, 0.75, 1].map((frac) => (
          <line
            key={frac}
            x1={padX}
            x2={width - padX}
            y1={padTop + plotHeight * (1 - frac)}
            y2={padTop + plotHeight * (1 - frac)}
            stroke="var(--color-border)"
            strokeWidth={1}
          />
        ))}
        <polyline points={linePoints} fill="none" stroke="var(--color-primary)" strokeWidth={2} />
        {points.map((p, i) => (
          <g key={p.mockResultId}>
            <circle cx={xFor(i)} cy={yFor(p.totalScore)} r={4} fill="var(--color-primary)" />
            <text x={xFor(i)} y={yFor(p.totalScore) - 10} fontSize={11} textAnchor="middle" className="fill-foreground">
              {p.totalScore}
            </text>
            <text
              x={xFor(i)}
              y={yFor(p.totalScore) + 18}
              fontSize={9}
              textAnchor="middle"
              className="fill-muted-foreground"
            >
              {p.percentile}%ile
            </text>
            <text x={xFor(i)} y={height - 8} fontSize={10} textAnchor="middle" className="fill-muted-foreground">
              {new Date(p.takenAt).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
            </text>
          </g>
        ))}
      </svg>
    </div>
  )
}

/** Professionalization pass: the score/percentile trend across every mock taken — the dashboard
 * feature real test-prep apps (TIME, IMS, Byju's Exam Prep) always lead with. Not a new scoring
 * computation: reuses MockResult.sectionScores + the same estimatePercentile() MockAnalysis.tsx
 * already uses, just aggregated across history instead of one result at a time. */
export function Progress() {
  const [trend, setTrend] = useState<TrendRow[] | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadTrend()
      .then(setTrend)
      .catch((e: Error) => setError(e.message))
  }, [])

  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6">
      <div>
        <Link to="/" className="text-sm text-primary underline">
          Back
        </Link>
        <h1 className="mt-2 text-2xl font-semibold">Progress</h1>
        <p className="text-sm text-muted-foreground">Score and estimated percentile across every mock you've taken.</p>
      </div>

      {error && <p className="text-destructive">Failed to load progress: {error}</p>}

      {trend === null && !error && (
        <div className="space-y-4">
          <Skeleton className="h-56 w-full" />
        </div>
      )}

      {trend && trend.length === 0 && (
        <EmptyState
          title="No mocks taken yet"
          description="Once you finish your first full or sectional mock, your score and percentile trend across attempts will show up here."
          actionLabel="See today's plan"
          actionTo="/"
        />
      )}

      {trend && trend.length > 0 && (
        <>
          <ScoreTrendChart points={trend} />
          <ul className="divide-y divide-border rounded-lg border border-border">
            {[...trend].reverse().map((p) => (
              <li key={p.mockResultId} className="flex items-center justify-between px-4 py-2 text-sm">
                <Link to={`/mock-result/${p.mockResultId}`} className="text-primary underline">
                  {p.mockTitle}
                </Link>
                <span className="text-muted-foreground">
                  {p.totalScore} marks · {p.percentile}%ile · {new Date(p.takenAt).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        </>
      )}
    </main>
  )
}
