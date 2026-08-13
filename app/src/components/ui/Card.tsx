import type { ReactNode } from 'react'
import { cn } from '@/lib/utils'

/**
 * The app's one surface primitive.
 *
 * Before this existed, every page hand-rolled its own `rounded-lg border border-border p-4`
 * with slightly different padding and radius each time, and several pages used no container at
 * all — which is why the app read as one flat sheet of text rather than a set of things. One
 * component means one radius, one padding rhythm and one border treatment everywhere.
 *
 * Three levels, and no more, because a fourth would only invite arbitrary choices:
 *   - `plain`    — the default raised surface.
 *   - `quiet`    — no fill, just an outline. For groups that must not compete with the content
 *                  inside them (a list wrapper, a collapsed section).
 *   - `accent`   — the one card on a screen that is the point of the screen. Used sparingly:
 *                  SPEC.md §13 asks for one accent colour, not an accented interface.
 */

type Variant = 'plain' | 'quiet' | 'accent'

const VARIANTS: Record<Variant, string> = {
  plain: 'bg-card border-border shadow-sm',
  quiet: 'bg-transparent border-border',
  accent: 'bg-card border-primary/30 shadow-sm ring-1 ring-primary/10',
}

export function Card({
  variant = 'plain',
  className,
  children,
}: {
  variant?: Variant
  className?: string
  children: ReactNode
}) {
  return <div className={cn('rounded-xl border', VARIANTS[variant], className)}>{children}</div>
}

/** Title row inside a Card. `action` sits on the right — a link, a count, a toggle. */
export function CardHeading({
  title,
  action,
  className,
}: {
  title: ReactNode
  action?: ReactNode
  className?: string
}) {
  return (
    <div className={cn('flex items-baseline justify-between gap-3', className)}>
      <h2 className="text-sm font-medium">{title}</h2>
      {action}
    </div>
  )
}
