import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { ChevronLeft } from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * Every non-immersive page's title block.
 *
 * Replaces the underlined violet "Back" link that each page had hand-rolled above its heading.
 * Once a persistent bottom nav existed, that link was both redundant (Today is one tap away)
 * and visually loud — a saturated underlined link was the first thing the eye hit on every
 * screen, above the actual title. Pages that are genuinely a level deep (a lesson, a mock
 * result) still get a real back affordance, but as a quiet icon aligned with the title rather
 * than a link floating above it.
 */
/**
 * Standalone back affordance for pages that already have their own heading markup. Same quiet
 * treatment as PageHeader's built-in one, so the two can't drift apart.
 */
export function BackLink({ to, label = 'Back' }: { to: string; label?: string }) {
  return (
    <Link
      to={to}
      aria-label={label}
      className="-ml-1.5 mb-1 inline-flex items-center gap-1 rounded-lg py-1 pl-1 pr-2 text-sm text-muted-foreground transition-colors hover:text-foreground"
    >
      <ChevronLeft className="size-4" aria-hidden />
      {label}
    </Link>
  )
}

export function PageHeader({
  title,
  subtitle,
  backTo,
  backLabel = 'Back',
  action,
  className,
}: {
  title: ReactNode
  subtitle?: ReactNode
  backTo?: string
  backLabel?: string
  action?: ReactNode
  className?: string
}) {
  return (
    <header className={cn('space-y-1.5', className)}>
      <div className="flex items-start gap-2">
        {backTo && (
          <Link
            to={backTo}
            aria-label={backLabel}
            className="-ml-2 mt-0.5 rounded-lg p-1.5 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
          >
            <ChevronLeft className="size-5" aria-hidden />
          </Link>
        )}
        <h1 className="min-w-0 flex-1 text-2xl font-semibold tracking-tight">{title}</h1>
        {action}
      </div>
      {subtitle && <p className="text-sm text-muted-foreground">{subtitle}</p>}
    </header>
  )
}
