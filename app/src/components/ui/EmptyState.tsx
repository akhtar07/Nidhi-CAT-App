import { Link } from 'react-router-dom'
import { buttonVariants } from '@/components/ui/button'

/** A calm, specific "nothing here yet" state — SPEC.md §13's "calm and focused" applies to empty
 * states too, so this is a short explanation + one clear next step, not an illustration or a
 * generic "No data" label. The action is optional: some empty states (e.g. "no mistakes yet")
 * have no useful next step beyond "go do the thing that fills this in naturally." */
export function EmptyState({
  title,
  description,
  actionLabel,
  actionTo,
}: {
  title: string
  description: string
  actionLabel?: string
  actionTo?: string
}) {
  return (
    <div className="rounded-lg border border-dashed border-border p-6 text-center">
      <p className="font-medium">{title}</p>
      <p className="mx-auto mt-1 max-w-sm text-sm text-muted-foreground">{description}</p>
      {actionLabel && actionTo && (
        <Link to={actionTo} className={buttonVariants({ variant: 'default', className: 'mt-4' })}>
          {actionLabel}
        </Link>
      )}
    </div>
  )
}
