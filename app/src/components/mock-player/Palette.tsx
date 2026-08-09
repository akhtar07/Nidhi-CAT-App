import { cn } from '@/lib/utils'
import { derivePaletteStatus } from '@/mock/paletteStatus'
import type { MockQuestionState, PaletteStatus } from '@/types/state'

/** SPEC.md §9.1's real-CAT colour convention. */
const STATUS_CLASS: Record<PaletteStatus, string> = {
  not_visited: 'bg-muted text-muted-foreground',
  not_answered: 'bg-red-500 text-white',
  answered: 'bg-green-600 text-white',
  marked: 'bg-purple-600 text-white',
  answered_marked: 'bg-purple-600 text-white ring-2 ring-inset ring-green-400',
}

export function Palette({
  questionIds,
  questionStates,
  currentIndex,
  onJump,
}: {
  questionIds: string[]
  questionStates: Record<string, MockQuestionState>
  currentIndex: number
  onJump: (index: number) => void
}) {
  return (
    <div className="grid grid-cols-6 gap-1.5 sm:grid-cols-5">
      {questionIds.map((qid, i) => {
        const status = derivePaletteStatus(questionStates[qid])
        return (
          <button
            key={qid}
            type="button"
            onClick={() => onJump(i)}
            title={status.replace('_', ' ')}
            className={cn(
              'flex size-8 items-center justify-center rounded text-xs font-medium transition-transform',
              STATUS_CLASS[status],
              i === currentIndex && 'scale-110 ring-2 ring-foreground',
            )}
          >
            {i + 1}
          </button>
        )
      })}
    </div>
  )
}
