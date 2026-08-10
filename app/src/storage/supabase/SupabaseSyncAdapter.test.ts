import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { Attempt, Settings } from '@/types/state'

const mockGetSession = vi.fn()
const mockUpsert = vi.fn()
const mockDeleteIn = vi.fn()
let mockClient: unknown

vi.mock('@/lib/supabaseClient', () => ({
  getSupabaseClient: () => mockClient,
}))

// Imported after the mock so SupabaseSyncAdapter picks up the mocked module.
const { SupabaseSyncAdapter } = await import('./SupabaseSyncAdapter')

function makeAttempt(overrides: Partial<Attempt> = {}): Attempt {
  return {
    schemaVersion: 1,
    id: 'attempt-1',
    questionId: 'qa.arith.percentages-0001',
    microTopicIds: ['qa.arith.percentages'],
    startedAt: 1000,
    submittedAt: 1030,
    timeSpentSec: 30,
    given: 'B',
    correct: true,
    mode: 'drill',
    markedForReview: false,
    ...overrides,
  }
}

function makeSettings(overrides: Partial<Settings> = {}): Settings {
  return {
    schemaVersion: 1,
    dailyMinutes: 60,
    examDate: '2026-11-29',
    weakSectionBias: null,
    emailOptIn: false,
    ...overrides,
  }
}

function makeSupabaseClient(session: { user: { id: string } } | null) {
  mockGetSession.mockResolvedValue({ data: { session } })
  mockUpsert.mockResolvedValue({ error: null })
  mockDeleteIn.mockResolvedValue({ error: null })
  return {
    auth: { getSession: mockGetSession },
    from: (_table: string) => ({
      upsert: mockUpsert,
      delete: () => ({ eq: () => ({ in: mockDeleteIn }) }),
    }),
  }
}

describe('SupabaseSyncAdapter', () => {
  let dbCounter = 0
  beforeEach(() => {
    dbCounter++
    mockClient = null
    mockGetSession.mockReset()
    mockUpsert.mockReset()
    mockDeleteIn.mockReset()
  })

  it('writes go straight to Dexie regardless of Supabase configuration (offline-safe)', async () => {
    const adapter = new SupabaseSyncAdapter(`test-${dbCounter}`)
    await adapter.addAttempt(makeAttempt())
    const stored = await adapter.getAttempt('attempt-1')
    expect(stored?.id).toBe('attempt-1')
  })

  it('flushQueue no-ops when Supabase is not configured, leaving the write queued', async () => {
    const adapter = new SupabaseSyncAdapter(`test-${dbCounter}`)
    await adapter.addAttempt(makeAttempt())
    const result = await adapter.flushQueue()
    expect(result).toEqual({ flushed: 0, remaining: 1, error: null })
    expect(mockUpsert).not.toHaveBeenCalled()
  })

  it('flushQueue no-ops when configured but not signed in', async () => {
    mockClient = makeSupabaseClient(null)
    const adapter = new SupabaseSyncAdapter(`test-${dbCounter}`)
    await adapter.addAttempt(makeAttempt())
    const result = await adapter.flushQueue()
    expect(result).toEqual({ flushed: 0, remaining: 1, error: null })
    expect(mockUpsert).not.toHaveBeenCalled()
  })

  it('flushes queued writes once configured and signed in, draining the queue', async () => {
    const adapter = new SupabaseSyncAdapter(`test-${dbCounter}`)
    await adapter.addAttempt(makeAttempt())
    mockClient = makeSupabaseClient({ user: { id: 'user-1' } })

    const result = await adapter.flushQueue()
    expect(result.error).toBeNull()
    expect(result.flushed).toBe(1)
    expect(mockUpsert).toHaveBeenCalledTimes(1)
    const [rows] = mockUpsert.mock.calls[0]
    expect(rows).toEqual([expect.objectContaining({ id: 'attempt-1', user_id: 'user-1', question_id: 'qa.arith.percentages-0001' })])
    expect(await adapter.queueLength()).toBe(0)
  })

  it('de-duplicates repeated writes to the same row before flushing', async () => {
    mockClient = makeSupabaseClient({ user: { id: 'user-1' } })
    const adapter = new SupabaseSyncAdapter(`test-${dbCounter}`)
    await adapter.putSettings(makeSettings({ dailyMinutes: 30 }))
    await adapter.putSettings(makeSettings({ dailyMinutes: 45 }))
    await adapter.putSettings(makeSettings({ dailyMinutes: 60 }))

    await adapter.flushQueue()
    expect(mockUpsert).toHaveBeenCalledTimes(1)
    const [rows] = mockUpsert.mock.calls[0]
    expect(rows).toHaveLength(1)
    expect((rows as { daily_minutes: number }[])[0].daily_minutes).toBe(60)
  })

  it('leaves the queue intact on a Supabase error, so the next flush retries', async () => {
    mockClient = makeSupabaseClient({ user: { id: 'user-1' } })
    mockUpsert.mockResolvedValue({ error: { message: 'network down' } })
    const adapter = new SupabaseSyncAdapter(`test-${dbCounter}`)
    await adapter.addAttempt(makeAttempt())

    const result = await adapter.flushQueue()
    expect(result.error).toContain('network down')
    expect(result.flushed).toBe(0)
    expect(await adapter.queueLength()).toBe(1)
  })

  it('reads never touch Supabase — only Dexie', async () => {
    mockClient = makeSupabaseClient({ user: { id: 'user-1' } })
    const adapter = new SupabaseSyncAdapter(`test-${dbCounter}`)
    await adapter.listAttempts()
    await adapter.getSettings()
    expect(mockGetSession).not.toHaveBeenCalled()
  })
})
