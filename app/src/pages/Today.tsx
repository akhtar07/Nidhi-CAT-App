import { Button } from '@/components/ui/button'

export function Today() {
  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-4 bg-background p-6 text-center text-foreground">
      <h1 className="text-2xl font-semibold">Ascent</h1>
      <p className="text-muted-foreground">
        Milestone 0 — repo scaffold. The Today screen lands in a later
        milestone.
      </p>
      <Button>Placeholder</Button>
    </main>
  )
}
