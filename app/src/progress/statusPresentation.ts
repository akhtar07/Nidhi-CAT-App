/**
 * Presentation mapping for mastery status. Kept out of the page component so the
 * ordinal ramp is declared once and the map and the legend can never drift apart.
 *
 * Colour is never the only channel: every use of these carries the label too
 * (legend text, table column, or an aria-label on the map cell).
 */

import type { ProgressStatus } from './topicProgress'

export interface StatusPresentation {
  label: string
  /** CSS colour for the mastery-map cell fill. */
  fill: string
  /** Short line explaining what the state means, for the legend. */
  hint: string
}

export const STATUS_PRESENTATION: Record<ProgressStatus, StatusPresentation> = {
  untouched: {
    label: 'Not started',
    fill: 'var(--mastery-0)',
    hint: 'No attempts logged yet.',
  },
  learning: {
    label: 'Learning',
    fill: 'var(--mastery-1)',
    hint: 'Lesson opened, fewer than 8 attempts.',
  },
  practising: {
    label: 'Practising',
    fill: 'var(--mastery-2)',
    hint: 'Drilling, mastery threshold not met yet.',
  },
  mastered: {
    label: 'Mastered',
    fill: 'var(--mastery-3)',
    hint: 'Accuracy, speed, hard items and retention all cleared.',
  },
  decaying: {
    label: 'Needs review',
    fill: 'var(--mastery-decaying)',
    hint: 'Was mastered, but it has been a while — due for review.',
  },
  locked: {
    label: 'Locked',
    fill: 'transparent',
    hint: 'Prerequisites not mastered yet.',
  },
}

/** Order the legend and the map group by: the ladder, then the two off-ladder states. */
export const STATUS_DISPLAY_ORDER: ProgressStatus[] = [
  'untouched',
  'learning',
  'practising',
  'mastered',
  'decaying',
  'locked',
]
