import { NavLink, useLocation } from 'react-router-dom'
import { BarChart3, BookOpen, CalendarDays, Home, Settings as SettingsIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * Persistent bottom navigation.
 *
 * The app previously exposed every destination as a row of small underlined text links
 * crammed into the Today header — six of them, wrapping on a phone, with no indication of
 * where you currently were. On a study app that is opened on a phone several times a day,
 * that is the difference between "an app" and "a page". A fixed bottom bar with a visible
 * active state is the convention learners already know from every other app on the device.
 *
 * Hidden during focused activities (drills, mocks, sets, lessons, the diagnostic): those are
 * timed or single-task screens where an ever-present nav bar invites accidental exits and
 * eats vertical space that the question needs. Matches SPEC.md §13's "calm and focused".
 */

const TABS = [
  { to: '/', label: 'Today', Icon: Home, end: true },
  { to: '/calendar', label: 'Plan', Icon: CalendarDays, end: false },
  { to: '/progress', label: 'Progress', Icon: BarChart3, end: false },
  { to: '/review', label: 'Review', Icon: BookOpen, end: false },
  { to: '/settings', label: 'Settings', Icon: SettingsIcon, end: false },
]

/** Route prefixes that take over the whole screen. */
const IMMERSIVE = ['/drill/', '/mock/', '/set/', '/lesson/', '/diagnostic', '/mock-result/']

export function BottomNav() {
  const { pathname } = useLocation()
  if (IMMERSIVE.some((prefix) => pathname.startsWith(prefix))) return null

  return (
    <nav
      aria-label="Primary"
      className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-card/95 backdrop-blur
                 supports-[backdrop-filter]:bg-card/80"
    >
      {/* pb keeps the bar clear of the iOS home indicator. */}
      <ul className="mx-auto flex max-w-2xl items-stretch pb-[env(safe-area-inset-bottom)]">
        {TABS.map(({ to, label, Icon, end }) => (
          <li key={to} className="flex-1">
            <NavLink
              to={to}
              end={end}
              className={({ isActive }) =>
                cn(
                  'flex flex-col items-center gap-1 py-2.5 text-[11px] transition-colors',
                  isActive ? 'text-primary' : 'text-muted-foreground hover:text-foreground',
                )
              }
            >
              {({ isActive }) => (
                <>
                  <Icon className="size-5" strokeWidth={isActive ? 2.4 : 1.8} aria-hidden />
                  <span className={isActive ? 'font-medium' : undefined}>{label}</span>
                </>
              )}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  )
}

/** Bottom padding so fixed-nav pages can scroll their last row clear of the bar. */
export function navSpacerClass(pathname: string): string {
  return IMMERSIVE.some((prefix) => pathname.startsWith(prefix)) ? '' : 'pb-24'
}
