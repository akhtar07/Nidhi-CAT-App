import { describe, expect, it } from 'vitest'
import type { QuestionIndexEntry } from '@/content/loadContent'
import { selectDiagnosticQuestions } from './diagnosticSelection'

function q(overrides: Partial<QuestionIndexEntry> & Pick<QuestionIndexEntry, 'id'>): QuestionIndexEntry {
  return {
    microTopicIds: ['qa.test'],
    section: 'QA',
    format: 'mcq',
    difficulty: 'easy',
    targetSeconds: 60,
    ...overrides,
  }
}

describe('selectDiagnosticQuestions', () => {
  it('never returns more than requested', () => {
    const index = Array.from({ length: 50 }, (_, i) => q({ id: `q${i}`, section: 'QA' }))
    expect(selectDiagnosticQuestions(index, 15)).toHaveLength(15)
  })

  it('never returns duplicates', () => {
    const index = Array.from({ length: 50 }, (_, i) => q({ id: `q${i}`, section: 'QA' }))
    const selected = selectDiagnosticQuestions(index, 15)
    expect(new Set(selected.map((s) => s.id)).size).toBe(selected.length)
  })

  it('spans multiple sections when available', () => {
    const index = [
      ...Array.from({ length: 10 }, (_, i) => q({ id: `qa${i}`, section: 'QA' })),
      ...Array.from({ length: 10 }, (_, i) => q({ id: `dilr${i}`, section: 'DILR' })),
    ]
    const selected = selectDiagnosticQuestions(index, 12)
    const sections = new Set(selected.map((s) => s.section))
    expect(sections.size).toBeGreaterThan(1)
  })

  it('spans multiple difficulties within a section', () => {
    const index = [
      ...Array.from({ length: 5 }, (_, i) => q({ id: `e${i}`, difficulty: 'easy' })),
      ...Array.from({ length: 5 }, (_, i) => q({ id: `m${i}`, difficulty: 'medium' })),
      ...Array.from({ length: 5 }, (_, i) => q({ id: `h${i}`, difficulty: 'hard' })),
    ]
    const selected = selectDiagnosticQuestions(index, 9)
    const difficulties = new Set(selected.map((s) => s.difficulty))
    expect(difficulties.size).toBeGreaterThan(1)
  })

  it('degrades gracefully when a section has zero content (e.g. VARC pre-Milestone-13)', () => {
    const index = Array.from({ length: 20 }, (_, i) => q({ id: `qa${i}`, section: 'QA' }))
    const selected = selectDiagnosticQuestions(index, 15)
    expect(selected.length).toBeGreaterThan(0)
    expect(selected.every((s) => s.section === 'QA')).toBe(true)
  })

  it('returns fewer than requested if the whole bank is smaller than the target', () => {
    const index = Array.from({ length: 5 }, (_, i) => q({ id: `qa${i}` }))
    expect(selectDiagnosticQuestions(index, 15)).toHaveLength(5)
  })
})
