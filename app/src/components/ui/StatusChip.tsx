import { STATUS_PRESENTATION } from '@/progress/statusPresentation'
import type { ProgressStatus } from '@/progress/topicProgress'
import { cn } from '@/lib/utils'

/**
 * A topic's state, as a pill.
 *
 * The topic list used to print the literal string "Lesson included" under all 86 rows — the
 * same eleven characters 86 times, telling the learner nothing about where she stood. This is
 * the replacement: what state this topic is actually in.
 *
 * Colour comes from the mastery ramp already declared in index.css, so the pill, the mastery
 * map and the legend can never drift apart. Colour is never the only channel — the label is
 * always present, per the accessibility note on STATUS_PRESENTATION.
 */
export function StatusChip({ status, className }: { status: ProgressStatus; className?: string }) {
  const { label, fill } = STATUS_PRESENTATION[status]
  const untouched = status === 'untouched' || status === 'locked'
  return (
    <span
      className={cn(
        'inline-flex shrink-0 items-center gap-1.5 rounded-full px-2 py-0.5 text-[11px] font-medium',
        untouched ? 'bg-secondary text-muted-foreground' : 'bg-secondary text-foreground',
        className,
      )}
    >
      <span
        aria-hidden
        className="size-1.5 rounded-full ring-1 ring-inset ring-black/10"
        style={{ backgroundColor: fill }}
      />
      {label}
    </span>
  )
}

/**
 * A thin horizontal fill. Used for coverage, per-section progress and accuracy, all of which
 * were previously bare percentages in prose — a number you have to read and compare, where a
 * bar is comparable at a glance.
 */
export function Meter({
  value,
  max = 100,
  label,
  className,
  tone = 'primary',
}: {
  value: number
  max?: number
  /** Screen-reader description; the visual context supplies it for sighted users. */
  label: string
  className?: string
  tone?: 'primary' | 'muted'
}) {
  const pct = max <= 0 ? 0 : Math.max(0, Math.min(100, (value / max) * 100))
  return (
    <div
      role="progressbar"
      aria-valuenow={Math.round(pct)}
      aria-valuemin={0}
      aria-valuemax={100}
      aria-label={label}
      className={cn('h-1.5 w-full overflow-hidden rounded-full bg-secondary', className)}
    >
      <div
        className={cn('h-full rounded-full transition-[width] duration-500', tone === 'primary' ? 'bg-primary' : 'bg-muted-foreground')}
        style={{ width: `${pct}%` }}
      />
    </div>
  )
}
