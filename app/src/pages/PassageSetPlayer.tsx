import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Markdown } from '@/components/question-player/Markdown'
import { QuestionPlayer } from '@/components/question-player/QuestionPlayer'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/Skeleton'
import { cn } from '@/lib/utils'
import { loadMicroTopic, loadPassageSet, loadQuestion, loadQuestionsForMicroTopic } from '@/content/loadContent'
import { storage } from '@/storage'
import type { MicroTopic, PassageAsset, PassageSet, Question } from '@/types/content'
import type { Attempt } from '@/types/state'

interface SetSession {
  set: PassageSet
  questions: Question[]
  /** questionId -> the micro-topic to pass to QuestionPlayer for that question (its primary microTopicId). */
  topicsByQuestionId: Map<string, { topic: MicroTopic; topicQuestions: Question[] }>
}

async function buildSession(setId: string): Promise<SetSession | null> {
  const set = await loadPassageSet(setId).catch(() => null)
  if (!set || !set.questionIds || set.questionIds.length === 0) return null

  const questions = await Promise.all(set.questionIds.map((id) => loadQuestion(id)))

  const primaryTopicIds = [...new Set(questions.map((q) => q.microTopicIds[0]))]
  const topicEntries = await Promise.all(
    primaryTopicIds.map(async (topicId) => {
      const [topic, topicQuestions] = await Promise.all([
        loadMicroTopic(topicId),
        loadQuestionsForMicroTopic(topicId),
      ])
      return [topicId, topic, topicQuestions] as const
    }),
  )

  const topicsByQuestionId = new Map<string, { topic: MicroTopic; topicQuestions: Question[] }>()
  for (const q of questions) {
    const primaryId = q.microTopicIds[0]
    const entry = topicEntries.find(([id]) => id === primaryId)
    if (entry?.[1]) {
      topicsByQuestionId.set(q.id, { topic: entry[1], topicQuestions: entry[2] })
    }
  }

  return { set, questions, topicsByQuestionId }
}

function formatSeconds(total: number): string {
  const m = Math.floor(total / 60)
  const s = total % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

function TableAsset({ asset }: { asset: PassageAsset }) {
  const columns = (asset.spec.columns as string[] | undefined) ?? []
  const rows = (asset.spec.rows as (string | number)[][] | undefined) ?? []
  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-muted">
            {columns.map((col) => (
              <th key={col} className="px-3 py-2 text-left font-medium">
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className="border-t border-border">
              {row.map((cell, j) => (
                <td key={j} className="px-3 py-2">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

const BAR_COLORS = ['var(--color-primary)', '#94a3b8', '#f59e0b', '#22c55e', '#a855f7']

interface BarChartSeries {
  name: string
  values: number[]
}

/** Every chart type needs the same swatch row, so it lives here rather than being copied per chart. */
function ChartLegend({ names, suffixes }: { names: string[]; suffixes?: (string | undefined)[] }) {
  if (names.length < 2) return null
  return (
    <div className="mt-2 flex flex-wrap gap-3 text-xs text-muted-foreground">
      {names.map((name, i) => (
        <span key={name} className="flex items-center gap-1">
          <span
            className="inline-block size-2.5 rounded-sm"
            style={{ backgroundColor: BAR_COLORS[i % BAR_COLORS.length] }}
          />
          {name}
          {suffixes?.[i] ? ` (${suffixes[i]})` : ''}
        </span>
      ))}
    </div>
  )
}

/** Renders from the underlying {categories, series} data, not an image — SPEC.md §5.1: "render
 * charts from data, not images, so they render responsively." Plain SVG, no charting library. */
function BarChartAsset({ asset }: { asset: PassageAsset }) {
  const categories = (asset.spec.categories as string[] | undefined) ?? []
  const series = (asset.spec.series as BarChartSeries[] | undefined) ?? []
  const unit = (asset.spec.unit as string | undefined) ?? ''

  const maxValue = Math.max(1, ...series.flatMap((s) => s.values))
  const chartHeight = 200
  const groupWidth = 90
  const barGap = 4
  const barWidth = series.length > 0 ? (groupWidth - barGap * (series.length + 1)) / series.length : 0
  const chartWidth = categories.length * groupWidth

  return (
    <div className="overflow-x-auto rounded-lg border border-border p-3">
      <svg width={chartWidth} height={chartHeight + 40} role="img" aria-label="Bar chart">
        {categories.map((cat, ci) => (
          <g key={cat} transform={`translate(${ci * groupWidth}, 0)`}>
            {series.map((s, si) => {
              const value = s.values[ci] ?? 0
              const barHeight = (value / maxValue) * chartHeight
              const x = barGap + si * (barWidth + barGap)
              const y = chartHeight - barHeight
              return (
                <g key={s.name}>
                  <rect x={x} y={y} width={barWidth} height={barHeight} fill={BAR_COLORS[si % BAR_COLORS.length]} />
                  <text x={x + barWidth / 2} y={y - 4} fontSize={10} textAnchor="middle" className="fill-foreground">
                    {value}
                  </text>
                </g>
              )
            })}
            <text
              x={groupWidth / 2}
              y={chartHeight + 16}
              fontSize={11}
              textAnchor="middle"
              className="fill-muted-foreground"
            >
              {cat}
            </text>
          </g>
        ))}
      </svg>
      <ChartLegend names={series.map((s) => s.name)} />
      {unit && <p className="mt-1 text-xs text-muted-foreground">Values in {unit}</p>}
    </div>
  )
}

/** Same data-driven-SVG approach as BarChartAsset, one polyline per series. */
function LineChartAsset({ asset }: { asset: PassageAsset }) {
  const categories = (asset.spec.categories as string[] | undefined) ?? []
  const series = (asset.spec.series as BarChartSeries[] | undefined) ?? []
  const unit = (asset.spec.unit as string | undefined) ?? ''

  const maxValue = Math.max(1, ...series.flatMap((s) => s.values))
  const chartHeight = 200
  const stepWidth = 90
  const chartWidth = Math.max(1, categories.length - 1) * stepWidth + 40

  const pointFor = (value: number, ci: number) => {
    const x = 20 + ci * stepWidth
    const y = chartHeight - (value / maxValue) * chartHeight
    return { x, y }
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-border p-3">
      <svg width={chartWidth} height={chartHeight + 40} role="img" aria-label="Line chart">
        {series.map((s, si) => {
          const points = s.values.map((v, ci) => pointFor(v, ci))
          const path = points.map((p) => `${p.x},${p.y}`).join(' ')
          const color = BAR_COLORS[si % BAR_COLORS.length]
          return (
            <g key={s.name}>
              <polyline points={path} fill="none" stroke={color} strokeWidth={2} />
              {points.map((p, ci) => (
                <g key={ci}>
                  <circle cx={p.x} cy={p.y} r={3} fill={color} />
                  <text x={p.x} y={p.y - 8} fontSize={10} textAnchor="middle" className="fill-foreground">
                    {s.values[ci]}
                  </text>
                </g>
              ))}
            </g>
          )
        })}
        {categories.map((cat, ci) => (
          <text
            key={cat}
            x={20 + ci * stepWidth}
            y={chartHeight + 16}
            fontSize={11}
            textAnchor="middle"
            className="fill-muted-foreground"
          >
            {cat}
          </text>
        ))}
      </svg>
      <ChartLegend names={series.map((s) => s.name)} />
      {unit && <p className="mt-1 text-xs text-muted-foreground">Values in {unit}</p>}
    </div>
  )
}

/** Stacked columns from the same {categories, series} shape as BarChartAsset — each series is a
 * segment stacked cumulatively within one column per category, instead of side-by-side groups. */
function StackedBarChartAsset({ asset }: { asset: PassageAsset }) {
  const categories = (asset.spec.categories as string[] | undefined) ?? []
  const series = (asset.spec.series as BarChartSeries[] | undefined) ?? []
  const unit = (asset.spec.unit as string | undefined) ?? ''

  const totals = categories.map((_, ci) => series.reduce((sum, s) => sum + (s.values[ci] ?? 0), 0))
  const maxTotal = Math.max(1, ...totals)
  const chartHeight = 200
  const groupWidth = 90
  const barWidth = 48
  const chartWidth = categories.length * groupWidth

  return (
    <div className="overflow-x-auto rounded-lg border border-border p-3">
      <svg width={chartWidth} height={chartHeight + 40} role="img" aria-label="Stacked bar chart">
        {categories.map((cat, ci) => {
          let cumulative = 0
          const x = (groupWidth - barWidth) / 2
          return (
            <g key={cat} transform={`translate(${ci * groupWidth}, 0)`}>
              {series.map((s, si) => {
                const value = s.values[ci] ?? 0
                const segHeight = (value / maxTotal) * chartHeight
                const y = chartHeight - cumulative - segHeight
                cumulative += value
                return (
                  <g key={s.name}>
                    <rect x={x} y={y} width={barWidth} height={segHeight} fill={BAR_COLORS[si % BAR_COLORS.length]} />
                    {segHeight > 14 && (
                      <text x={x + barWidth / 2} y={y + segHeight / 2 + 4} fontSize={10} textAnchor="middle" fill="var(--color-primary-foreground)">
                        {value}
                      </text>
                    )}
                  </g>
                )
              })}
              <text x={groupWidth / 2} y={chartHeight - cumulative - 6} fontSize={10} textAnchor="middle" className="fill-foreground">
                {totals[ci]}
              </text>
              <text
                x={groupWidth / 2}
                y={chartHeight + 16}
                fontSize={11}
                textAnchor="middle"
                className="fill-muted-foreground"
              >
                {cat}
              </text>
            </g>
          )
        })}
      </svg>
      <ChartLegend names={series.map((s) => s.name)} />
      {unit && <p className="mt-1 text-xs text-muted-foreground">Values in {unit}</p>}
    </div>
  )
}

interface PieSlice {
  name: string
  value: number
}

/** Pure-SVG pie chart built from cumulative angle math, not a library — same reasoning as
 * BarChartAsset: render from the underlying {slices} data so it stays crisp and responsive. */
function PieChartAsset({ asset }: { asset: PassageAsset }) {
  const slices = (asset.spec.slices as PieSlice[] | undefined) ?? []
  const unit = (asset.spec.unit as string | undefined) ?? ''
  const total = slices.reduce((sum, s) => sum + s.value, 0) || 1
  const radius = 90
  const cx = 100
  const cy = 100

  let cumulativeAngle = -Math.PI / 2
  const arcs = slices.map((s, i) => {
    const angle = (s.value / total) * 2 * Math.PI
    const startAngle = cumulativeAngle
    const endAngle = cumulativeAngle + angle
    cumulativeAngle = endAngle
    const x1 = cx + radius * Math.cos(startAngle)
    const y1 = cy + radius * Math.sin(startAngle)
    const x2 = cx + radius * Math.cos(endAngle)
    const y2 = cy + radius * Math.sin(endAngle)
    const largeArc = angle > Math.PI ? 1 : 0
    const path = `M ${cx} ${cy} L ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2} Z`
    return { path, color: BAR_COLORS[i % BAR_COLORS.length], name: s.name, value: s.value }
  })

  return (
    <div className="overflow-x-auto rounded-lg border border-border p-3">
      <div className="flex flex-wrap items-center gap-4">
        <svg width={200} height={200} role="img" aria-label="Pie chart">
          {arcs.map((a) => (
            <path key={a.name} d={a.path} fill={a.color} stroke="var(--color-card)" strokeWidth={1} />
          ))}
        </svg>
        <div className="flex flex-col gap-1 text-xs text-muted-foreground">
          {arcs.map((a) => (
            <span key={a.name} className="flex items-center gap-1.5">
              <span className="inline-block size-2.5 rounded-sm" style={{ backgroundColor: a.color }} />
              {unit === '%'
                ? `${a.name}: ${a.value}%`
                : `${a.name}: ${a.value}${unit ? ` ${unit}` : ''} (${Math.round((a.value / total) * 1000) / 10}%)`}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

/** Paints a background-coloured outline behind label text before the fill, so a value stays
 * readable where it lands on a bar, a bubble or another series' label. Cheaper and more robust
 * than trying to lay labels out so they never overlap. */
const HALO: React.CSSProperties = {
  paintOrder: 'stroke',
  stroke: 'var(--color-card)',
  strokeWidth: 3,
  strokeLinejoin: 'round',
}

/** Rounds an axis maximum up to a readable gridline value (1/2/2.5/5 x a power of ten), so tick
 * labels land on round numbers instead of on whatever the largest data point happens to be. */
function niceCeil(value: number): number {
  if (value <= 0) return 1
  const magnitude = 10 ** Math.floor(Math.log10(value))
  const normalised = value / magnitude
  const step = normalised <= 1 ? 1 : normalised <= 2 ? 2 : normalised <= 2.5 ? 2.5 : normalised <= 5 ? 5 : 10
  return step * magnitude
}

/** Radar (spider) chart: one spoke per axis, one closed polygon per series.
 *
 * Values are printed at each vertex for the same reason BarChartAsset prints them above its bars —
 * a learner has to be able to read an exact figure off the chart, and interpolating between grid
 * rings by eye would make any arithmetic question ambiguous. The rings are visual guides only. */
function RadarChartAsset({ asset }: { asset: PassageAsset }) {
  const axes = (asset.spec.axes as string[] | undefined) ?? []
  const series = (asset.spec.series as BarChartSeries[] | undefined) ?? []
  const unit = (asset.spec.unit as string | undefined) ?? ''
  const scaleMax = (asset.spec.max as number | undefined) ?? niceCeil(Math.max(1, ...series.flatMap((s) => s.values)))

  const radius = 92
  const labelRadius = radius * 1.22
  // Axis names sit outside the rim, anchored away from the centre, so the box has to be wide
  // enough for the longest of them or a name like "Data Interpretation" is clipped by the
  // viewBox. Estimated at ~6.2px per character at font-size 11 rather than measured, since
  // measuring text would mean a layout pass and a re-render.
  const sideMargin = Math.max(...axes.map((a) => a.length), 1) * 6.2
  const cx = labelRadius + sideMargin
  const cy = radius + 26
  const width = 2 * cx
  const height = 2 * cy
  const rings = [0.25, 0.5, 0.75, 1]

  const angleAt = (i: number) => -Math.PI / 2 + (i * 2 * Math.PI) / Math.max(1, axes.length)
  const pointAt = (i: number, fraction: number) => ({
    x: cx + radius * fraction * Math.cos(angleAt(i)),
    y: cy + radius * fraction * Math.sin(angleAt(i)),
  })
  const polygon = (fraction: number) =>
    axes
      .map((_, i) => {
        const p = pointAt(i, fraction)
        return `${p.x.toFixed(1)},${p.y.toFixed(1)}`
      })
      .join(' ')

  return (
    <div className="overflow-x-auto rounded-lg border border-border p-3">
      <svg width={width} height={height} role="img" aria-label="Radar chart">
        {rings.map((r) => (
          <polygon
            key={r}
            points={polygon(r)}
            fill="none"
            stroke="var(--color-border)"
            strokeWidth={1}
          />
        ))}
        {axes.map((axis, i) => {
          const end = pointAt(i, 1)
          const label = pointAt(i, labelRadius / radius)
          const cos = Math.cos(angleAt(i))
          const anchor = Math.abs(cos) < 0.25 ? 'middle' : cos > 0 ? 'start' : 'end'
          return (
            <g key={axis}>
              <line x1={cx} y1={cy} x2={end.x} y2={end.y} stroke="var(--color-border)" strokeWidth={1} />
              <text x={label.x} y={label.y + 4} fontSize={11} textAnchor={anchor} className="fill-muted-foreground">
                {axis}
              </text>
            </g>
          )
        })}
        {series.map((s, si) => {
          const color = BAR_COLORS[si % BAR_COLORS.length]
          const points = axes.map((_, i) => pointAt(i, (s.values[i] ?? 0) / scaleMax))
          return (
            <g key={s.name}>
              <polygon
                points={points.map((p) => `${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')}
                fill={color}
                fillOpacity={0.12}
                stroke={color}
                strokeWidth={2}
              />
              {points.map((p, i) => {
                // Two series that score similarly on one attribute put their vertices within a
                // few pixels of each other, so a fixed label offset stacks "72" on top of "66"
                // and neither is readable. Each series is nudged along the tangent instead, which
                // separates the labels while keeping each one next to its own vertex.
                const angle = angleAt(i)
                const spread = (si - (series.length - 1) / 2) * 18
                const lx = p.x + Math.cos(angle) * 11 - Math.sin(angle) * spread
                const ly = p.y + Math.sin(angle) * 11 + Math.cos(angle) * spread
                return (
                  <g key={axes[i]}>
                    <circle cx={p.x} cy={p.y} r={3} fill={color} />
                    <text
                      x={lx}
                      y={ly + 3}
                      fontSize={10}
                      textAnchor="middle"
                      className="fill-foreground"
                      style={HALO}
                    >
                      {s.values[i]}
                    </text>
                  </g>
                )
              })}
            </g>
          )
        })}
      </svg>
      <ChartLegend names={series.map((s) => s.name)} />
      {unit && <p className="mt-1 text-xs text-muted-foreground">Values in {unit}</p>}
    </div>
  )
}

interface BubblePoint {
  name: string
  x: number
  y: number
  size: number
}

/** Bubble chart: two positional dimensions plus a third carried by bubble *area*.
 *
 * Area, not radius, is proportional to `size` — scaling the radius linearly would overstate a
 * large bubble by squaring the difference, which is the classic way a bubble chart lies. The
 * size value is printed inside each bubble so the third dimension is readable exactly. */
function BubbleChartAsset({ asset }: { asset: PassageAsset }) {
  const points = (asset.spec.points as BubblePoint[] | undefined) ?? []
  const xLabel = (asset.spec.xLabel as string | undefined) ?? ''
  const yLabel = (asset.spec.yLabel as string | undefined) ?? ''
  const sizeLabel = (asset.spec.sizeLabel as string | undefined) ?? ''

  const plotWidth = 360
  const plotHeight = 220
  const marginLeft = 52
  const marginTop = 14
  const marginBottom = 46
  const marginRight = 18

  const xMax = (asset.spec.xMax as number | undefined) ?? niceCeil(Math.max(1, ...points.map((p) => p.x)))
  const yMax = (asset.spec.yMax as number | undefined) ?? niceCeil(Math.max(1, ...points.map((p) => p.y)))
  const sizeMax = Math.max(1, ...points.map((p) => p.size))
  // Gridline count is the generator's call: it picks divisions such that every plotted point
  // lands exactly on a labelled gridline, so a value can be read off without interpolating.
  const xDivisions = (asset.spec.xDivisions as number | undefined) ?? 4
  const yDivisions = (asset.spec.yDivisions as number | undefined) ?? 4
  const fractions = (n: number) => Array.from({ length: n + 1 }, (_, i) => i / n)
  const xTicks = fractions(xDivisions)
  const yTicks = fractions(yDivisions)

  const px = (x: number) => marginLeft + (x / xMax) * plotWidth
  const py = (y: number) => marginTop + plotHeight - (y / yMax) * plotHeight
  const pr = (size: number) => 8 + 18 * Math.sqrt(size / sizeMax)

  return (
    <div className="overflow-x-auto rounded-lg border border-border p-3">
      <svg
        width={marginLeft + plotWidth + marginRight}
        height={marginTop + plotHeight + marginBottom}
        role="img"
        aria-label="Bubble chart"
      >
        {yTicks.map((t) => (
          <g key={`y${t}`}>
            <line
              x1={marginLeft}
              y1={py(t * yMax)}
              x2={marginLeft + plotWidth}
              y2={py(t * yMax)}
              stroke="var(--color-border)"
              strokeWidth={1}
            />
            <text x={marginLeft - 8} y={py(t * yMax) + 4} fontSize={10} textAnchor="end" className="fill-muted-foreground">
              {Math.round(t * yMax * 100) / 100}
            </text>
          </g>
        ))}
        {xTicks.map((t) => (
          <g key={`x${t}`}>
            <line
              x1={px(t * xMax)}
              y1={marginTop}
              x2={px(t * xMax)}
              y2={marginTop + plotHeight}
              stroke="var(--color-border)"
              strokeWidth={1}
            />
            <text
              x={px(t * xMax)}
              y={marginTop + plotHeight + 16}
              fontSize={10}
              textAnchor="middle"
              className="fill-muted-foreground"
            >
              {Math.round(t * xMax * 100) / 100}
            </text>
          </g>
        ))}
        {/* Circles first, then every label — otherwise a bubble drawn later paints over the
            name of one drawn earlier, which is exactly what happens when two points sit close
            together and the right-hand one is large. */}
        {points.map((p, i) => {
          const color = BAR_COLORS[i % BAR_COLORS.length]
          return (
            <circle
              key={p.name}
              cx={px(p.x)}
              cy={py(p.y)}
              r={pr(p.size)}
              fill={color}
              fillOpacity={0.35}
              stroke={color}
              strokeWidth={1.5}
            />
          )
        })}
        {points.map((p) => (
          <g key={p.name}>
            <text x={px(p.x)} y={py(p.y) + 4} fontSize={10} textAnchor="middle" className="fill-foreground" style={HALO}>
              {p.size}
            </text>
            <text
              x={px(p.x)}
              y={py(p.y) - pr(p.size) - 4}
              fontSize={10}
              textAnchor="middle"
              className="fill-muted-foreground"
              style={HALO}
            >
              {p.name}
            </text>
          </g>
        ))}
        {xLabel && (
          <text
            x={marginLeft + plotWidth / 2}
            y={marginTop + plotHeight + 38}
            fontSize={11}
            textAnchor="middle"
            className="fill-muted-foreground"
          >
            {xLabel}
          </text>
        )}
        {yLabel && (
          <text
            x={12}
            y={marginTop + plotHeight / 2}
            fontSize={11}
            textAnchor="middle"
            transform={`rotate(-90, 12, ${marginTop + plotHeight / 2})`}
            className="fill-muted-foreground"
          >
            {yLabel}
          </text>
        )}
      </svg>
      {sizeLabel && (
        <p className="mt-1 text-xs text-muted-foreground">Bubble area is proportional to {sizeLabel} (printed inside each bubble).</p>
      )}
    </div>
  )
}

/** Combination chart: bars on the left axis, lines on the right axis.
 *
 * The whole point of this chart type in CAT is that the two axes carry *different units* — sales
 * in crores against margin in percent — so a question can only be answered by reading each series
 * against its own scale. Sharing one axis would quietly destroy that. */
function ComboChartAsset({ asset }: { asset: PassageAsset }) {
  const categories = (asset.spec.categories as string[] | undefined) ?? []
  const bars = (asset.spec.bars as BarChartSeries[] | undefined) ?? []
  const lines = (asset.spec.lines as BarChartSeries[] | undefined) ?? []
  const leftUnit = (asset.spec.leftUnit as string | undefined) ?? ''
  const rightUnit = (asset.spec.rightUnit as string | undefined) ?? ''

  const chartHeight = 200
  const groupWidth = 96
  const marginLeft = 44
  const marginRight = 44
  // Enough headroom for a value label sitting above a point that reaches the top gridline.
  const marginTop = 24
  const plotWidth = Math.max(1, categories.length) * groupWidth

  const leftMax = niceCeil(Math.max(1, ...bars.flatMap((s) => s.values)))
  const rightMax = niceCeil(Math.max(1, ...lines.flatMap((s) => s.values)))
  // Both axes share gridlines, so the division count has to give round steps on *both*. Four
  // divisions of a right-axis max of 25 reads 6.25 / 12.5 / 18.75, which is unreadable on a
  // percentage axis; five gives 5 / 10 / 15 / 20. Falls back to 4 if nothing divides cleanly.
  const divisions =
    [4, 5, 6].find((d) => Number.isInteger((leftMax / d) * 2) && Number.isInteger((rightMax / d) * 2)) ?? 4
  const ticks = Array.from({ length: divisions + 1 }, (_, i) => i / divisions)

  const barGap = 6
  const barWidth = bars.length > 0 ? (groupWidth - barGap * (bars.length + 1)) / bars.length : 0
  const yLeft = (v: number) => marginTop + chartHeight - (v / leftMax) * chartHeight
  const yRight = (v: number) => marginTop + chartHeight - (v / rightMax) * chartHeight
  const xCentre = (ci: number) => marginLeft + ci * groupWidth + groupWidth / 2

  return (
    <div className="overflow-x-auto rounded-lg border border-border p-3">
      <svg
        width={marginLeft + plotWidth + marginRight}
        height={marginTop + chartHeight + 40}
        role="img"
        aria-label="Combination bar and line chart"
      >
        {ticks.map((t) => (
          <g key={t}>
            <line
              x1={marginLeft}
              y1={yLeft(t * leftMax)}
              x2={marginLeft + plotWidth}
              y2={yLeft(t * leftMax)}
              stroke="var(--color-border)"
              strokeWidth={1}
            />
            <text x={marginLeft - 6} y={yLeft(t * leftMax) + 4} fontSize={10} textAnchor="end" className="fill-muted-foreground">
              {Math.round(t * leftMax * 100) / 100}
            </text>
            <text
              x={marginLeft + plotWidth + 6}
              y={yRight(t * rightMax) + 4}
              fontSize={10}
              textAnchor="start"
              className="fill-muted-foreground"
            >
              {Math.round(t * rightMax * 100) / 100}
            </text>
          </g>
        ))}
        {categories.map((cat, ci) => (
          <g key={cat}>
            {bars.map((s, si) => {
              const value = s.values[ci] ?? 0
              const x = marginLeft + ci * groupWidth + barGap + si * (barWidth + barGap)
              const y = yLeft(value)
              return (
                <g key={s.name}>
                  <rect x={x} y={y} width={barWidth} height={marginTop + chartHeight - y} fill={BAR_COLORS[si % BAR_COLORS.length]} />
                  <text x={x + barWidth / 2} y={y - 4} fontSize={10} textAnchor="middle" className="fill-foreground" style={HALO}>
                    {value}
                  </text>
                </g>
              )
            })}
            <text
              x={xCentre(ci)}
              y={marginTop + chartHeight + 16}
              fontSize={11}
              textAnchor="middle"
              className="fill-muted-foreground"
            >
              {cat}
            </text>
          </g>
        ))}
        {lines.map((s, li) => {
          const color = BAR_COLORS[(bars.length + li) % BAR_COLORS.length]
          const pts = categories.map((_, ci) => ({ x: xCentre(ci), y: yRight(s.values[ci] ?? 0) }))
          return (
            <g key={s.name}>
              <polyline points={pts.map((p) => `${p.x},${p.y}`).join(' ')} fill="none" stroke={color} strokeWidth={2} />
              {pts.map((p, ci) => {
                // Above the point normally, but below it when the point sits lower than the
                // tallest bar in that category — otherwise the line's value lands on top of the
                // bar's value, which is where the two labels would collide.
                const tallestBarTop = yLeft(Math.max(0, ...bars.map((b) => b.values[ci] ?? 0)))
                const below = p.y > tallestBarTop
                return (
                  <g key={ci}>
                    <circle cx={p.x} cy={p.y} r={3.5} fill={color} />
                    <text
                      x={p.x}
                      y={below ? p.y + 15 : p.y - 8}
                      fontSize={10}
                      textAnchor="middle"
                      className="fill-foreground"
                      style={HALO}
                    >
                      {s.values[ci]}
                    </text>
                  </g>
                )
              })}
            </g>
          )
        })}
      </svg>
      <ChartLegend
        names={[...bars.map((s) => s.name), ...lines.map((s) => s.name)]}
        suffixes={[...bars.map(() => leftUnit), ...lines.map(() => rightUnit)]}
      />
      <p className="mt-1 text-xs text-muted-foreground">
        Bars read against the left axis{leftUnit ? ` (${leftUnit})` : ''}; the line reads against the right axis
        {rightUnit ? ` (${rightUnit})` : ''}.
      </p>
    </div>
  )
}

function SetAsset({ asset }: { asset: PassageAsset }) {
  if (asset.type === 'table') return <TableAsset asset={asset} />
  if (asset.type === 'chart' && asset.spec.chartKind === 'bar') return <BarChartAsset asset={asset} />
  if (asset.type === 'chart' && asset.spec.chartKind === 'line') return <LineChartAsset asset={asset} />
  if (asset.type === 'chart' && asset.spec.chartKind === 'pie') return <PieChartAsset asset={asset} />
  if (asset.type === 'chart' && asset.spec.chartKind === 'stacked-bar') return <StackedBarChartAsset asset={asset} />
  if (asset.type === 'chart' && asset.spec.chartKind === 'radar') return <RadarChartAsset asset={asset} />
  if (asset.type === 'chart' && asset.spec.chartKind === 'bubble') return <BubbleChartAsset asset={asset} />
  if (asset.type === 'chart' && asset.spec.chartKind === 'combo') return <ComboChartAsset asset={asset} />
  return (
    <p className="text-sm text-muted-foreground">
      [chart rendering not yet implemented for this chart type]
    </p>
  )
}

/** SPEC.md §13: timer stays visually quiet until 1.5x target, amber at 1.5x, red at 2.5x. */
function timerColorClass(elapsedSec: number, targetSec: number): string {
  if (elapsedSec >= targetSec * 2.5) return 'text-destructive'
  if (elapsedSec >= targetSec * 1.5) return 'text-amber-500'
  return 'text-muted-foreground'
}

type Phase = 'intro' | 'answering' | 'complete'

/** Milestone 8: RC passages / DILR sets, with a set-level timer and the "attempt/skip" decision step. */
export function PassageSetPlayer() {
  const { setId } = useParams<{ setId: string }>()
  const [session, setSession] = useState<SetSession | null | undefined>(undefined)
  const [error, setError] = useState<string | null>(null)
  const [phase, setPhase] = useState<Phase>('intro')
  const [index, setIndex] = useState(0)
  const [results, setResults] = useState<Attempt[]>([])
  const [elapsedSec, setElapsedSec] = useState(0)
  const startedAtRef = useRef(Date.now())

  useEffect(() => {
    if (!setId) return
    setSession(undefined)
    setError(null)
    setPhase('intro')
    setIndex(0)
    setResults([])
    setElapsedSec(0)
    startedAtRef.current = Date.now()
    buildSession(setId)
      .then(setSession)
      .catch((e: Error) => setError(e.message))
  }, [setId])

  useEffect(() => {
    if (phase === 'complete') return
    const interval = setInterval(() => setElapsedSec((s) => s + 1), 1000)
    return () => clearInterval(interval)
  }, [phase])

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load set: {error}</p>
        <Link to="/" className="text-primary underline">
          Back
        </Link>
      </main>
    )
  }

  if (session === undefined) {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6">
        <Skeleton className="h-4 w-16" />
        <Skeleton className="h-8 w-2/3" />
        <Skeleton className="h-40 w-full" />
      </main>
    )
  }

  if (session === null) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-muted-foreground">This set isn't available yet.</p>
        <Link to="/" className="text-primary underline">
          Back
        </Link>
      </main>
    )
  }

  const { set, questions, topicsByQuestionId } = session
  const targetSec = set.targetMinutes * 60

  async function skipEntireSet() {
    const now = Date.now()
    await Promise.all(
      questions.map((q) =>
        storage.addAttempt({
          schemaVersion: 1,
          id: crypto.randomUUID(),
          questionId: q.id,
          microTopicIds: q.microTopicIds,
          startedAt: now,
          submittedAt: now,
          timeSpentSec: 0,
          given: null,
          correct: false,
          mode: 'drill',
          markedForReview: false,
        }),
      ),
    )
    setResults([])
    setPhase('complete')
  }

  if (phase === 'intro') {
    return (
      <main className="mx-auto max-w-2xl space-y-4 p-6">
        <div>
          <Link to="/" className="text-sm text-primary underline">
            Back
          </Link>
          <div className="mt-2 flex items-center justify-between">
            <h1 className="text-xl font-semibold">
              {set.kind === 'di_set' ? 'Data Interpretation set' : set.kind === 'lr_set' ? 'Logical Reasoning set' : 'Reading Comprehension passage'}
            </h1>
            <span className={cn('text-sm tabular-nums', timerColorClass(elapsedSec, targetSec))}>
              {formatSeconds(elapsedSec)}
            </span>
          </div>
          <p className="text-sm text-muted-foreground">
            {questions.length} questions · target {set.targetMinutes} min
          </p>
        </div>

        <Markdown text={set.bodyMarkdown} />

        {set.assets?.map((asset, i) => <SetAsset key={i} asset={asset} />)}

        <div className="rounded-lg border border-border p-4">
          <p className="mb-3 text-sm font-medium">Attempt this set, or skip it and move on?</p>
          <p className="mb-3 text-sm text-muted-foreground">
            Skipping counts as a strategic call, not a failure — some sets aren't worth the time. It'll be
            logged as skipped for all {questions.length} questions.
          </p>
          <div className="flex gap-2">
            <Button variant="ghost" onClick={() => void skipEntireSet()}>
              Skip set
            </Button>
            <Button onClick={() => setPhase('answering')}>Attempt set</Button>
          </div>
        </div>
      </main>
    )
  }

  if (phase === 'answering') {
    if (index >= questions.length) {
      setPhase('complete')
      return null
    }

    const question = questions[index]
    const topicInfo = topicsByQuestionId.get(question.id)

    if (!topicInfo) {
      setPhase('complete')
      return null
    }

    return (
      <div>
        <div className="mx-auto max-w-2xl space-y-3 px-4 pt-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              Question {index + 1} of {questions.length}
            </span>
            <span className={cn('tabular-nums', timerColorClass(elapsedSec, targetSec))}>
              Set time {formatSeconds(elapsedSec)}
            </span>
          </div>
          {set.assets?.map((asset, i) => <SetAsset key={i} asset={asset} />)}
        </div>
        <QuestionPlayer
          key={question.id}
          question={question}
          mode="drill"
          topic={topicInfo.topic}
          topicQuestions={topicInfo.topicQuestions}
          onComplete={(attempt) => {
            setResults((r) => [...r, attempt])
            setIndex((i) => i + 1)
          }}
        />
      </div>
    )
  }

  const correctCount = results.filter((a) => a.correct).length
  const skipped = results.length === 0
  return (
    <main className="mx-auto max-w-2xl space-y-4 p-6 text-center">
      <h2 className="text-xl font-semibold">Set complete</h2>
      {skipped ? (
        <p className="text-muted-foreground">Skipped — logged for all {questions.length} questions.</p>
      ) : (
        <p className="text-muted-foreground">
          {correctCount} / {results.length} correct · {formatSeconds(elapsedSec)} elapsed (target{' '}
          {formatSeconds(targetSec)})
        </p>
      )}
      <Link to="/">
        <Button>Back to topics</Button>
      </Link>
    </main>
  )
}
