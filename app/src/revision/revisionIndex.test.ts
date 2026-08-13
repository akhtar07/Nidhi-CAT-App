import { describe, expect, it } from 'vitest'
import {
  buildRevisionIndex,
  filterCards,
  filterTraps,
  groupByTopic,
  matchesQuery,
  tokenise,
} from './revisionIndex'
import type { Lesson, MicroTopic } from '@/types/content'

function topic(id: string, name: string, section: MicroTopic['section']): MicroTopic {
  return {
    id,
    name,
    section,
    topicId: id.split('.').slice(0, 2).join('.'),
    catFrequency: 'high',
    roiScore: 5,
    estLearnMinutes: 20,
    targetSecPerQuestion: 60,
  }
}

function lesson(microTopicId: string, overrides: Partial<Lesson> = {}): Lesson {
  return {
    id: `lesson.${microTopicId}`,
    microTopicId,
    bodyMarkdown: 'body',
    estReadMinutes: 5,
    ...overrides,
  }
}

const syllabus = [
  topic('qa.arith.percentages', 'Percentages', 'QA'),
  topic('qa.numsys.hcf-lcm', 'HCF & LCM', 'QA'),
  topic('varc.va.para-summary', 'Para-summary', 'VARC'),
]

const lessons: Lesson[] = [
  lesson('qa.arith.percentages', {
    formulaCards: [
      {
        id: 'fc1',
        microTopicId: 'qa.arith.percentages',
        title: 'Percentage change',
        bodyMarkdown: 'New minus Old over Old',
        exampleMarkdown: '80 to 100 is 25%',
      },
      {
        id: 'fc2',
        microTopicId: 'qa.arith.percentages',
        title: 'Successive change',
        bodyMarkdown: 'a plus b plus ab over 100',
      },
    ],
    commonTraps: ['Successive changes do not simply add.', 'Always divide by the original value.'],
  }),
  lesson('qa.numsys.hcf-lcm', {
    formulaCards: [
      { id: 'fc3', microTopicId: 'qa.numsys.hcf-lcm', title: 'Product identity', bodyMarkdown: 'HCF times LCM' },
    ],
    commonTraps: ['The product identity only works for two numbers.'],
  }),
  lesson('varc.va.para-summary', { commonTraps: ['Do not pick the most memorable example.'] }),
]

describe('buildRevisionIndex', () => {
  it('flattens formula cards and traps with topic context attached', () => {
    const { cards, traps } = buildRevisionIndex(lessons, syllabus)
    expect(cards).toHaveLength(3)
    expect(traps).toHaveLength(4)
    expect(cards[0]).toMatchObject({
      id: 'fc1',
      topicName: 'Percentages',
      section: 'QA',
      title: 'Percentage change',
      exampleMarkdown: '80 to 100 is 25%',
    })
  })

  it('normalises a missing exampleMarkdown to null', () => {
    const { cards } = buildRevisionIndex(lessons, syllabus)
    expect(cards.find((c) => c.id === 'fc2')?.exampleMarkdown).toBeNull()
  })

  it('synthesises stable trap ids from topic and position', () => {
    const { traps } = buildRevisionIndex(lessons, syllabus)
    expect(traps[0].id).toBe('qa.arith.percentages.trap-0')
    expect(traps[1].id).toBe('qa.arith.percentages.trap-1')
  })

  it('handles a lesson with neither cards nor traps', () => {
    const { cards, traps } = buildRevisionIndex([lesson('qa.arith.percentages')], syllabus)
    expect(cards).toEqual([])
    expect(traps).toEqual([])
  })

  it('skips a lesson whose micro-topic is not in the syllabus', () => {
    const orphan = lesson('qa.ghost.topic', {
      formulaCards: [{ id: 'x', microTopicId: 'qa.ghost.topic', title: 'T', bodyMarkdown: 'B' }],
    })
    const { cards } = buildRevisionIndex([orphan], syllabus)
    expect(cards).toEqual([])
  })

  it('returns empty lists for no lessons', () => {
    expect(buildRevisionIndex([], syllabus)).toEqual({ cards: [], traps: [] })
  })
})

describe('tokenise / matchesQuery', () => {
  it('splits on whitespace and drops empties', () => {
    expect(tokenise('  percent   change ')).toEqual(['percent', 'change'])
    expect(tokenise('')).toEqual([])
  })

  it('requires every token to appear (AND, not OR)', () => {
    expect(matchesQuery('Percentage change formula', ['percent', 'change'])).toBe(true)
    expect(matchesQuery('Percentage change formula', ['percent', 'ratio'])).toBe(false)
  })

  it('matches everything on an empty query', () => {
    expect(matchesQuery('anything', [])).toBe(true)
  })

  it('is case insensitive', () => {
    expect(matchesQuery('HCF and LCM', ['hcf'])).toBe(true)
  })
})

describe('filterCards', () => {
  const { cards } = buildRevisionIndex(lessons, syllabus)

  it('returns everything with no filters', () => {
    expect(filterCards(cards, { section: null, query: '' })).toHaveLength(3)
  })

  it('filters by section', () => {
    expect(filterCards(cards, { section: 'QA', query: '' })).toHaveLength(3)
    expect(filterCards(cards, { section: 'VARC', query: '' })).toHaveLength(0)
  })

  it('searches the title', () => {
    const found = filterCards(cards, { section: null, query: 'successive' })
    expect(found.map((c) => c.id)).toEqual(['fc2'])
  })

  it('searches the body and the example, not just the title', () => {
    expect(filterCards(cards, { section: null, query: 'HCF times' }).map((c) => c.id)).toEqual(['fc3'])
    expect(filterCards(cards, { section: null, query: '80 to 100' }).map((c) => c.id)).toEqual(['fc1'])
  })

  it('searches the topic name too', () => {
    expect(filterCards(cards, { section: null, query: 'lcm' }).map((c) => c.id)).toEqual(['fc3'])
  })

  it('returns nothing when the query matches nothing', () => {
    expect(filterCards(cards, { section: null, query: 'trigonometry' })).toEqual([])
  })

  it('combines section and query', () => {
    expect(filterCards(cards, { section: 'VARC', query: 'percentage' })).toEqual([])
  })
})

describe('filterTraps', () => {
  const { traps } = buildRevisionIndex(lessons, syllabus)

  it('filters by section', () => {
    expect(filterTraps(traps, { section: 'VARC', query: '' })).toHaveLength(1)
  })

  it('searches trap text', () => {
    const found = filterTraps(traps, { section: null, query: 'original value' })
    expect(found).toHaveLength(1)
    expect(found[0].text).toContain('original value')
  })

  it('returns nothing on no match', () => {
    expect(filterTraps(traps, { section: null, query: 'zzzz' })).toEqual([])
  })
})

describe('groupByTopic', () => {
  it('groups items by micro-topic preserving first-seen order', () => {
    const { cards } = buildRevisionIndex(lessons, syllabus)
    const groups = groupByTopic(cards)
    expect(groups.map((g) => g.microTopicId)).toEqual(['qa.arith.percentages', 'qa.numsys.hcf-lcm'])
    expect(groups[0].items).toHaveLength(2)
    expect(groups[1].items).toHaveLength(1)
  })

  it('handles an empty list', () => {
    expect(groupByTopic([])).toEqual([])
  })
})
