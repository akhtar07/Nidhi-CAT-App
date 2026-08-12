import { cn } from '@/lib/utils'

/** Loading placeholder — a plain pulsing block, no new dependency. Used in place of bare
 * "Loading…" text so a page's shape is visible before its data arrives (professionalization
 * pass — SPEC.md §13 still applies: calm, not flashy, so this is a slow opacity pulse, not a
 * shimmer/sheen animation). */
export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('animate-pulse rounded-md bg-muted', className)} />
}
