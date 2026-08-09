import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { loadExamMeta, topicsWithContent } from '@/content/loadContent'
import { computeCoverageForecast, type CoverageForecast } from '@/planner/coverageForecast'
import { addDays, daysBetween, todayIso } from '@/planner/dateUtils'
import { generatePlan, MOCK_SENTINEL, REVIEW_SENTINEL } from '@/planner/generatePlan'
import { redistributeMissedDay } from '@/planner/missedDay'
import { storage } from '@/storage'
import type { MicroTopic } from '@/types/content'
import type { Attempt, PlanDay } from '@/types/state'

const HEATMAP_WEEKS = 12

function planItemLabel(microTopicId: string, topicNameById: Map<string, string>): string {
  if (microTopicId === MOCK_SENTINEL) return 'Mock test'
  if (microTopicId === REVIEW_SENTINEL) return 'Review / SRS'
  return topicNameById.get(microTopicId) ?? microTopicId
}

function intensityClass(minutes: number): string {
  if (minutes === 0) return 'bg-muted'
  if (minutes < 20) return 'bg-primary/20'
  if (minutes < 45) return 'bg-primary/45'
  if (minutes < 90) return 'bg-primary/70'
  return 'bg-primary'
}

export function Calendar() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [topics, setTopics] = useState<MicroTopic[]>([])
  const [attempts, setAttempts] = useState<Attempt[]>([])
  const [planDays, setPlanDays] = useState<Map<string, PlanDay>>(new Map())
  const [examDate, setExamDate] = useState<string | null>(null)
  const [registrationCloses, setRegistrationCloses] = useState<string | null>(null)
  const [forecast, setForecast] = useState<CoverageForecast | null>(null)
  const [selectedDate, setSelectedDate] = useState<string | null>(null)
  const [redistributeStatus, setRedistributeStatus] = useState<string | null>(null)

  const today = todayIso()

  const load = useCallback(async () => {
    setLoading(true)
    const [syllabus, meta, settings, allAttempts] = await Promise.all([
      topicsWithContent(),
      loadExamMeta(),
      storage.getSettings(),
      storage.listAttempts(),
    ])
    setTopics(syllabus)
    setAttempts(allAttempts)
    setExamDate(settings?.examDate ?? meta.examDate)
    setRegistrationCloses(meta.registrationClosesDate)

    const from = addDays(today, -HEATMAP_WEEKS * 7)
    const to = addDays(today, 30)
    const days = await storage.listPlanDays({ from, to })
    setPlanDays(new Map(days.map((d) => [d.date, d])))

    if (settings) {
      const masteryStates = await storage.listMasteryStates()
      const masteryByTopicId = new Map(masteryStates.map((m) => [m.microTopicId, m]))
      const plan = generatePlan({
        topics: syllabus,
        masteryByTopicId,
        today,
        examDate: settings.examDate,
        dailyMinutes: settings.dailyMinutes,
      })
      setForecast(computeCoverageForecast(syllabus, plan, settings.examDate))
    }
    setLoading(false)
  }, [today])

  useEffect(() => {
    load().catch((e: Error) => setError(e.message))
  }, [load])

  const minutesByDate = new Map<string, number>()
  for (const a of attempts) {
    const date = new Date(a.submittedAt).toISOString().slice(0, 10)
    minutesByDate.set(date, (minutesByDate.get(date) ?? 0) + a.timeSpentSec / 60)
  }

  const heatmapStart = addDays(today, -HEATMAP_WEEKS * 7)
  const heatmapDates: string[] = []
  for (let i = 0; i <= daysBetween(heatmapStart, today); i++) heatmapDates.push(addDays(heatmapStart, i))

  const missedDays = [...planDays.values()].filter((d) => d.date < today && d.status === 'pending')

  const topicNameById = new Map(topics.map((t) => [t.id, t.name]))

  async function handleRedistribute(missed: PlanDay) {
    setRedistributeStatus('Redistributing…')
    const nextDates = Array.from({ length: 5 }, (_, i) => addDays(missed.date, i + 1))
    const existingNextDays = await Promise.all(
      nextDates.map(async (d) => (await storage.getPlanDay(d)) ?? { schemaVersion: 1 as const, date: d, items: [], status: 'pending' as const }),
    )
    const masteryStates = await storage.listMasteryStates()
    const masteryByTopicId = new Map(masteryStates.map((m) => [m.microTopicId, m]))
    const baselineItemsPerDay = existingNextDays[0]?.items.length || 3

    const { updatedDays, droppedItems } = redistributeMissedDay(
      missed,
      existingNextDays,
      new Map(topics.map((t) => [t.id, t])),
      masteryByTopicId,
      baselineItemsPerDay,
    )

    await storage.putPlanDay({ ...missed, status: 'missed' })
    await Promise.all(updatedDays.map((d) => storage.putPlanDay(d)))

    setRedistributeStatus(
      droppedItems.length === 0
        ? 'Plan updated — redistributed across the next 5 days.'
        : `Plan updated. Dropped ${droppedItems.length} lowest-priority item(s) that didn't fit.`,
    )
    await load()
  }

  /** Regenerates from tomorrow onward using current Settings — never touches today's PlanDay, so
   * anything already marked done today survives a settings change (e.g. adjusting dailyMinutes). */
  async function handleRegenerate() {
    const settings = await storage.getSettings()
    if (!settings) return
    setRedistributeStatus('Regenerating…')
    const masteryStates = await storage.listMasteryStates()
    const masteryByTopicId = new Map(masteryStates.map((m) => [m.microTopicId, m]))
    const tomorrow = addDays(today, 1)
    const plan = generatePlan({
      topics,
      masteryByTopicId,
      today: tomorrow,
      examDate: settings.examDate,
      dailyMinutes: settings.dailyMinutes,
    })
    await Promise.all(plan.days.map((d) => storage.putPlanDay(d)))
    setRedistributeStatus('Plan regenerated from tomorrow onward.')
    await load()
  }

  if (error) {
    return (
      <main className="mx-auto max-w-2xl p-6">
        <p className="text-destructive">Failed to load calendar: {error}</p>
        <Link to="/" className="text-primary underline">
          Back
        </Link>
      </main>
    )
  }

  if (loading) {
    return <main className="mx-auto max-w-2xl p-6 text-muted-foreground">Loading…</main>
  }

  const selectedDay = selectedDate ? planDays.get(selectedDate) : undefined
  const selectedAttempts = selectedDate
    ? attempts.filter((a) => new Date(a.submittedAt).toISOString().slice(0, 10) === selectedDate)
    : []

  return (
    <main className="mx-auto max-w-2xl space-y-6 p-6">
      <div>
        <Link to="/" className="text-sm text-primary underline">
          Back
        </Link>
        <h1 className="mt-2 text-2xl font-semibold">Calendar</h1>
        {examDate && (
          <p className="text-sm text-muted-foreground">
            Exam day: {examDate} ({daysBetween(today, examDate)} days away)
            {registrationCloses && registrationCloses >= today && (
              <span> · Registration closes {registrationCloses}</span>
            )}
          </p>
        )}
      </div>

      {forecast && (
        <div
          className={`rounded-lg border p-3 text-sm ${
            forecast.droppedTopics.length === 0 ? 'border-border' : 'border-amber-500/50 bg-amber-500/10'
          }`}
        >
          {forecast.message}
        </div>
      )}

      {missedDays.length > 0 && (
        <div className="space-y-2 rounded-lg border border-destructive/40 bg-destructive/5 p-3 text-sm">
          <p className="font-medium">Plan updated — here's today.</p>
          <p className="text-muted-foreground">
            {missedDays.length} earlier day{missedDays.length > 1 ? 's' : ''} didn't get finished.
          </p>
          <Button onClick={() => void handleRedistribute(missedDays[0])}>Redistribute oldest missed day</Button>
          {redistributeStatus && <p className="text-xs text-muted-foreground">{redistributeStatus}</p>}
        </div>
      )}

      <section>
        <h2 className="mb-2 text-sm font-medium text-muted-foreground">Last {HEATMAP_WEEKS} weeks</h2>
        <div className="grid grid-flow-col grid-rows-7 gap-1 overflow-x-auto">
          {heatmapDates.map((date) => (
            <button
              key={date}
              type="button"
              title={`${date}: ${Math.round(minutesByDate.get(date) ?? 0)} min`}
              onClick={() => setSelectedDate(date)}
              className={`size-3 rounded-sm ${intensityClass(minutesByDate.get(date) ?? 0)} ${
                date === today ? 'ring-1 ring-primary' : ''
              }`}
            />
          ))}
        </div>
      </section>

      {selectedDate && (
        <section className="rounded-lg border border-border p-4">
          <h2 className="mb-2 text-sm font-medium">{selectedDate}</h2>
          {selectedDay ? (
            <div className="space-y-1 text-sm">
              <p className="text-muted-foreground">Planned:</p>
              <ul className="list-inside list-disc">
                {selectedDay.items.map((item, i) => (
                  <li key={i} className={item.done ? 'text-muted-foreground line-through' : ''}>
                    {item.kind} · {planItemLabel(item.microTopicId, topicNameById)}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Nothing planned this day.</p>
          )}
          <p className="mt-3 text-muted-foreground">
            Actual: {selectedAttempts.length} question{selectedAttempts.length === 1 ? '' : 's'} attempted,{' '}
            {selectedAttempts.filter((a) => a.correct).length} correct,{' '}
            {Math.round(selectedAttempts.reduce((s, a) => s + a.timeSpentSec, 0) / 60)} min
          </p>
        </section>
      )}

      <section>
        <div className="mb-2 flex items-center justify-between">
          <h2 className="text-sm font-medium text-muted-foreground">Coming up</h2>
          <Button variant="outline" onClick={() => void handleRegenerate()}>
            Regenerate plan
          </Button>
        </div>
        <ul className="divide-y divide-border rounded-lg border border-border">
          {[...planDays.values()]
            .filter((d) => d.date >= today)
            .sort((a, b) => a.date.localeCompare(b.date))
            .slice(0, 14)
            .map((day) => (
              <li key={day.date} className="px-4 py-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{day.date}</span>
                  <span className="text-xs text-muted-foreground">{day.items.length} item(s)</span>
                </div>
                <p className="text-xs text-muted-foreground">
                  {day.items.map((i) => planItemLabel(i.microTopicId, topicNameById)).join(', ')}
                </p>
              </li>
            ))}
        </ul>
      </section>
    </main>
  )
}
