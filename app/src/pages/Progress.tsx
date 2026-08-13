import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { EmptyState } from '@/components/ui/EmptyState'
import { Skeleton } from '@/components/ui/Skeleton'
import { loadMockDefinition, loadSyllabus } from '@/content/loadContent'
import { computeScoreTrend, type ProgressPoint } from '@/mock/progressTrend'
import { computePracticeTrend, type PracticeWeek } from '@/progress/practiceTrend'
import {
  countByStatus,
  rollUpBySection,
  summariseCoverage,
  type CoverageSummary,
  type SectionRollup,
} from '@/progress/sectionRollup'
import { STATUS_DISPLAY_ORDER, STATUS_PRESENTATION } from '@/progress/statusPresentation'
import { buildTopicProgress, rankWeakestTopics, type ProgressStatus, type TopicProgressRow } from '@/progress/topicProgress'
import { storage } from '@/storage'
import type { Section } from '@/types/state'

const MAX_SCORE = 204

interface TrendRow extends ProgressPoint {
  mockTitle: string
}

interface ProgressData {
  rows: TopicProgressRow[]
  coverage: CoverageSummary
  sections: SectionRollup[]
  weakest: TopicProgressRow[]
  statusCounts: Record<ProgressStatus, number>
  practice: PracticeWeek[]
  mockTrend: TrendRow[]
}

async function loadProgress(): Promise<ProgressData> {
  const [syllabus, attempts, masteryStates, mockResults] = await Promise.all([
    loadSyllabus(),
    storage.listAttempts(),
    storage.listMasteryStates(),
    storage.listMockResults(),
  ])

  const rows = buildTopicProgress(syllabus, attempts, masteryStates)

  const trend = computeScoreTrend(mockResults)
  const byId = new Map(mockResults.map((r) => [r.id, r]))
  const titleCache = new Map<string, string>()
  const mockTrend = await Promise.all(
    trend.map(async (point) => {
      const mockId = byId.get(point.mockResultId)?.mockId
      if (mockId && !titleCache.has(mockId)) {
        const def = await loadMockDefinition(mockId).catch(() => null)
        titleCache.set(mockId, def?.title ?? mockId)
      }
      return { ...point, mockTitle: mockId ? (titleCache.get(mockId) ?? mockId) : 'Mock' }
    }),
  )

  return {
    rows,
    coverage: summariseCoverage(rows),
    sections: rollUpBySection(rows),
    weakest: rankWeakestTopics(rows),
    statusCounts: countByStatus(rows),
    practice: computePracticeTrend(attempts),
    mockTrend,
  }
}

/** Hero figure — the one number the page leads with (SPEC.md §4.5's "how am I doing"). */
function CoverageHeader({ coverage }: { coverage: CoverageSummary }) {
  return (
    <section className="rounded-lg border border-border p-4">
      <p className="text-sm text-muted-foreground">Syllabus covered</p>
      <p className="text-4xl font-semibold tabular-nums">
        {coverage.started}
        <span className="text-2xl text-muted-foreground">/{coverage.totalTopics}</span>
      </p>
      <p className="mt-1 text-sm text-muted-foreground">
        {coverage.startedPct}% of micro-topics started · {coverage.mastered} mastered ·{' '}
        {coverage.untouched} not begun
      </p>
      {/* A meter, not a pie of two slices — a single ratio against a limit. */}
      <div className="mt-3 h-2 w-full overflow-hidden rounded-full bg-muted">
        <div
          className="h-full rounded-full"
          style={{ width: `${coverage.startedPct}%`, background: 'var(--mastery-2)' }}
        />
      </div>
      {coverage.totalAttempts > 0 && (
        <p className="mt-3 text-sm text-muted-foreground">
          {coverage.totalAttempts} questions attempted · {coverage.overallAccuracyPct}% lifetime accuracy
        </p>
      )}
    </section>
  )
}

function SectionRollupTable({ sections }: { sections: SectionRollup[] }) {
  return (
    <section>
      <h2 className="mb-2 text-sm font-medium text-muted-foreground">By section</h2>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-muted text-left">
              <th className="px-3 py-2 font-medium">Section</th>
              <th className="px-3 py-2 text-right font-medium">Started</th>
              <th className="px-3 py-2 text-right font-medium">Mastered</th>
              <th className="px-3 py-2 text-right font-medium">Attempts</th>
              <th className="px-3 py-2 text-right font-medium">Accuracy</th>
            </tr>
          </thead>
          <tbody>
            {sections.map((s) => (
              <tr key={s.section} className="border-t border-border">
                <td className="px-3 py-2">{s.section}</td>
                <td className="px-3 py-2 text-right tabular-nums text-muted-foreground">
                  {s.started}/{s.topics}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-muted-foreground">{s.mastered}</td>
                <td className="px-3 py-2 text-right tabular-nums text-muted-foreground">{s.attempts}</td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {s.accuracyPct === null ? <span className="text-muted-foreground">—</span> : `${s.accuracyPct}%`}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

/**
 * The mastery map (SPEC.md §4.5): every micro-topic as a cell, coloured by its rung on
 * the ordinal ladder. Grouped by section so the grid is navigable rather than 86
 * undifferentiated squares. Identity is never colour-alone — each cell carries a title
 * and aria-label naming the topic and its state, and the legend is always present.
 */
function MasteryMap({
  rows,
  statusCounts,
}: {
  rows: TopicProgressRow[]
  statusCounts: Record<ProgressStatus, number>
}) {
  const sections: Section[] = ['VARC', 'DILR', 'QA']
  return (
    <section>
      <h2 className="mb-2 text-sm font-medium text-muted-foreground">Mastery map</h2>
      <div className="space-y-3 rounded-lg border border-border p-4">
        {sections.map((section) => {
          const inSection = rows.filter((r) => r.section === section)
          if (inSection.length === 0) return null
          return (
            <div key={section}>
              <p className="mb-1.5 text-xs text-muted-foreground">
                {section} · {inSection.length} topics
              </p>
              <div className="flex flex-wrap gap-1">
                {inSection.map((row) => {
                  const presentation = STATUS_PRESENTATION[row.status]
                  const detail =
                    row.attempts === 0
                      ? 'no attempts yet'
                      : `${row.attempts} attempts, ${row.accuracyPct}% accuracy`
                  return (
                    <Link
                      key={row.microTopicId}
                      to={`/lesson/${row.microTopicId}`}
                      title={`${row.name} — ${presentation.label} (${detail})`}
                      aria-label={`${row.name}, ${presentation.label}, ${detail}`}
                      // 2px surface gap between fills comes from the flex gap; the ring
                      // keeps 'locked' (transparent fill) visible as an outline.
                      className="size-5 rounded-sm ring-1 ring-border transition-transform hover:scale-125"
                      style={{ background: presentation.fill }}
                    />
                  )
                })}
              </div>
            </div>
          )
        })}

        <div className="flex flex-wrap gap-x-4 gap-y-1.5 border-t border-border pt-3 text-xs text-muted-foreground">
          {STATUS_DISPLAY_ORDER.filter((s) => statusCounts[s] > 0).map((status) => (
            <span key={status} className="flex items-center gap-1.5">
              <span
                className="inline-block size-2.5 rounded-sm ring-1 ring-border"
                style={{ background: STATUS_PRESENTATION[status].fill }}
              />
              {STATUS_PRESENTATION[status].label} ({statusCounts[status]})
            </span>
          ))}
        </div>
      </div>
    </section>
  )
}

function WeakestTopics({ rows }: { rows: TopicProgressRow[] }) {
  return (
    <section>
      <h2 className="mb-2 text-sm font-medium text-muted-foreground">Weakest topics</h2>
      <div className="overflow-x-auto rounded-lg border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-muted text-left">
              <th className="px-3 py-2 font-medium">Topic</th>
              <th className="px-3 py-2 text-right font-medium">Accuracy</th>
              <th className="px-3 py-2 text-right font-medium">Pace</th>
              <th className="px-3 py-2 text-right font-medium">Attempts</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.microTopicId} className="border-t border-border">
                <td className="px-3 py-2">
                  <Link to={`/lesson/${row.microTopicId}`} className="text-primary underline">
                    {row.name}
                  </Link>
                  <span className="ml-2 text-xs text-muted-foreground">{row.section}</span>
                </td>
                <td className="px-3 py-2 text-right tabular-nums">{row.accuracyPct}%</td>
                <td className="px-3 py-2 text-right tabular-nums text-muted-foreground">
                  {row.paceRatio === null ? '—' : `${row.paceRatio}x`}
                </td>
                <td className="px-3 py-2 text-right tabular-nums text-muted-foreground">{row.attempts}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <p className="mt-1.5 text-xs text-muted-foreground">
        Pace is your median time against the topic's target. Above 1x means slower than CAT pace.
      </p>
    </section>
  )
}

/**
 * Weekly practice accuracy. One series, so no legend box — the heading names it.
 * Plain SVG from data, no charting library (SPEC.md §5.1), matching the chart
 * renderers in PassageSetPlayer.tsx.
 */
function PracticeTrendChart({ weeks }: { weeks: PracticeWeek[] }) {
  const width = Math.max(280, weeks.length * 74)
  const height = 190
  const padTop = 22
  const padBottom = 34
  // Left padding clears the y-axis numbers so the first point's label cannot collide with them.
  const padX = 36
  const plotHeight = height - padTop - padBottom
  const plotWidth = width - padX * 2

  const xFor = (i: number) => padX + (weeks.length > 1 ? (i / (weeks.length - 1)) * plotWidth : plotWidth / 2)
  const yFor = (pct: number) => padTop + plotHeight - (pct / 100) * plotHeight
  const linePoints = weeks.map((w, i) => `${xFor(i)},${yFor(w.accuracyPct)}`).join(' ')

  // Selective direct labels, not a number on every point: over twelve weeks that becomes
  // noise and buries the shape of the line. First, last, best and worst are the four the
  // reader actually needs; the rest are readable off the gridlines.
  const accuracies = weeks.map((w) => w.accuracyPct)
  const labelled = new Set<number>([
    0,
    weeks.length - 1,
    accuracies.indexOf(Math.max(...accuracies)),
    accuracies.indexOf(Math.min(...accuracies)),
  ])

  return (
    <div className="overflow-x-auto rounded-lg border border-border p-3">
      <svg width={width} height={height} role="img" aria-label="Weekly practice accuracy">
        {[0, 25, 50, 75, 100].map((pct) => (
          <g key={pct}>
            <line
              x1={padX}
              x2={width - padX}
              y1={yFor(pct)}
              y2={yFor(pct)}
              stroke="var(--color-border)"
              strokeWidth={1}
            />
            <text x={4} y={yFor(pct) + 3} fontSize={9} className="fill-muted-foreground">
              {pct}
            </text>
          </g>
        ))}
        <polyline points={linePoints} fill="none" stroke="var(--color-primary)" strokeWidth={2} />
        {weeks.map((w, i) => (
          <g key={w.weekStart}>
            <circle cx={xFor(i)} cy={yFor(w.accuracyPct)} r={4} fill="var(--color-primary)" />
            {labelled.has(i) && (
              <text
                x={xFor(i)}
                y={yFor(w.accuracyPct) - 9}
                fontSize={10}
                textAnchor="middle"
                className="fill-foreground"
              >
                {w.accuracyPct}%
              </text>
            )}
            <text x={xFor(i)} y={height - 18} fontSize={9} textAnchor="middle" className="fill-muted-foreground">
              {new Date(`${w.weekStart}T12:00:00Z`).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric',
              })}
            </text>
            <text x={xFor(i)} y={height - 5} fontSize={9} textAnchor="middle" className="fill-muted-foreground">
              {w.attempts}q · {w.medianTimeSec}s
            </text>
          </g>
        ))}
      </svg>
    </div>
  )
}

/** Mock score trend — unchanged from the previous version of this page. */
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

/**
 * The "how am I doing" hub (SPEC.md §4.5). Previously this page trended mock scores only,
 * which left the mastery engine's per-topic state — the thing the whole learning engine
 * computes — invisible to the learner, and showed nothing at all until her first mock.
 */
export function Progress() {
  const [data, setData] = useState<ProgressData | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadProgress()
      .then(setData)
      .catch((e: Error) => setError(e.message))
  }, [])

  const hasAnyActivity = useMemo(
    () => (data ? data.coverage.totalAttempts > 0 || data.mockTrend.length > 0 : false),
    [data],
  )

  return (
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">Progress</h1>
        <p className="text-sm text-muted-foreground">
          Where you stand across the syllabus, which topics are weakest, and whether practice is landing.
        </p>
      </div>

      {error && <p className="text-destructive">Failed to load progress: {error}</p>}

      {data === null && !error && (
        <div className="space-y-4">
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-40 w-full" />
          <Skeleton className="h-56 w-full" />
        </div>
      )}

      {data && !hasAnyActivity && (
        <>
          <CoverageHeader coverage={data.coverage} />
          <EmptyState
            title="No practice logged yet"
            description="Once you attempt some questions, this page will show your accuracy per topic, which section is lagging, and whether your weekly practice is improving."
            actionLabel="See today's plan"
            actionTo="/"
          />
        </>
      )}

      {data && hasAnyActivity && (
        <>
          <CoverageHeader coverage={data.coverage} />
          <SectionRollupTable sections={data.sections} />
          <MasteryMap rows={data.rows} statusCounts={data.statusCounts} />

          {data.weakest.length > 0 && <WeakestTopics rows={data.weakest} />}

          <section>
            <h2 className="mb-2 text-sm font-medium text-muted-foreground">Weekly practice accuracy</h2>
            {data.practice.length === 0 ? (
              <EmptyState
                title="No practice attempts yet"
                description="Drill some questions and your weekly accuracy and pace will trend here. Mock attempts are tracked separately below."
                actionLabel="Start practising"
                actionTo="/"
              />
            ) : (
              <PracticeTrendChart weeks={data.practice} />
            )}
          </section>

          <section>
            <h2 className="mb-2 text-sm font-medium text-muted-foreground">Mock scores</h2>
            {data.mockTrend.length === 0 ? (
              <EmptyState
                title="No mocks taken yet"
                description="Your score and estimated percentile across full and sectional mocks will appear here after your first one."
                actionLabel="See available mocks"
                actionTo="/"
              />
            ) : (
              <>
                <ScoreTrendChart points={data.mockTrend} />
                <ul className="mt-3 divide-y divide-border rounded-lg border border-border">
                  {[...data.mockTrend].reverse().map((p) => (
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
          </section>
        </>
      )}
    </main>
  )
}
