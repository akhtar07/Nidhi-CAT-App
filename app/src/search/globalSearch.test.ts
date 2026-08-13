import { describe, expect, it } from 'vitest'
import { search, type SearchCorpus } from './globalSearch'
import type { MicroTopic } from '@/types/content'
import type { RevisionCard } from '@/revision/revisionIndex'

function topic(id: string, name: string, section: MicroTopic['section'] = 'QA'): MicroTopic {
  return {
    id,
    name,
    section,
    topicId: 'qa.arith',
    catFrequency: 'high',
    roiScore: 5,
    estLearnMinutes: 20,
    targetSecPerQuestion: 60,
  }
}

function card(id: string, title: string, body: string, topicName: string, microTopicId: string): RevisionCard {
  return {
    id,
    microTopicId,
    topicName,
    section: 'QA',
    title,
    bodyMarkdown: body,
    exampleMarkdown: null,
  }
}

const corpus: SearchCorpus = {
  topics: [
    topic('qa.arith.percentages', 'Percentages'),
    topic('qa.numsys.hcf-lcm', 'HCF & LCM'),
    topic('varc.va.para-summary', 'Para-summary', 'VARC'),
  ],
  lessonTopicIds: ['qa.arith.percentages', 'varc.va.para-summary'],
  topicIdsWithQuestions: new Set(['qa.arith.percentages', 'qa.numsys.hcf-lcm']),
  formulaCards: [
    card('fc1', 'Percentage change', 'New minus Old over Old', 'Percentages', 'qa.arith.percentages'),
    card('fc2', 'Product identity', 'HCF times LCM equals the product', 'HCF & LCM', 'qa.numsys.hcf-lcm'),
  ],
}

describe('search', () => {
  it('returns nothing for a blank query rather than everything', () => {
    expect(search(corpus, '')).toEqual([])
    expect(search(corpus, '   ')).toEqual([])
  })

  it('finds a micro-topic by name', () => {
    const results = search(corpus, 'percentages')
    expect(results.some((r) => r.kind === 'topic' && r.title === 'Percentages')).toBe(true)
  })

  it('returns a lesson result only for topics that have a lesson', () => {
    const withLesson = search(corpus, 'percentages').filter((r) => r.kind === 'lesson')
    expect(withLesson).toHaveLength(1)
    const withoutLesson = search(corpus, 'hcf').filter((r) => r.kind === 'lesson')
    expect(withoutLesson).toHaveLength(0)
  })

  it('finds a formula card by its body text, not just its title', () => {
    const results = search(corpus, 'equals the product')
    expect(results.map((r) => r.key)).toContain('formula:fc2')
  })

  it('ranks topics above lessons above formulas', () => {
    const kinds = search(corpus, 'percentage').map((r) => r.kind)
    expect(kinds.indexOf('topic')).toBeLessThan(kinds.indexOf('formula'))
  })

  it('ranks a title match above a body-only match within the same kind', () => {
    const local: SearchCorpus = {
      ...corpus,
      topics: [],
      lessonTopicIds: [],
      formulaCards: [
        card('body', 'Unrelated name', 'mentions alligation here', 'Mixtures', 'qa.arith.mixtures'),
        card('title', 'Alligation rule', 'nothing else', 'Mixtures', 'qa.arith.mixtures'),
      ],
    }
    expect(search(local, 'alligation').map((r) => r.key)).toEqual(['formula:title', 'formula:body'])
  })

  it('requires every token to match (AND)', () => {
    expect(search(corpus, 'percentage change').map((r) => r.key)).toContain('formula:fc1')
    expect(search(corpus, 'percentage trigonometry')).toEqual([])
  })

  it('is case insensitive', () => {
    expect(search(corpus, 'HCF').length).toBeGreaterThan(0)
    expect(search(corpus, 'hcf').length).toBeGreaterThan(0)
  })

  it('flags a topic that has no questions yet in its subtitle', () => {
    const result = search(corpus, 'para-summary').find((r) => r.kind === 'topic')
    expect(result?.subtitle).toContain('no questions yet')
  })

  it('routes every result to a real in-app path', () => {
    for (const r of search(corpus, 'percentage')) {
      expect(r.to.startsWith('/lesson/')).toBe(true)
    }
  })

  it('gives every result a unique key', () => {
    const results = search(corpus, 'percentage')
    expect(new Set(results.map((r) => r.key)).size).toBe(results.length)
  })

  it('respects the result limit', () => {
    expect(search(corpus, 'percentage', 1)).toHaveLength(1)
  })

  it('returns nothing when the query matches nothing', () => {
    expect(search(corpus, 'zzzznotathing')).toEqual([])
  })

  it('handles an entirely empty corpus', () => {
    const empty: SearchCorpus = {
      topics: [],
      lessonTopicIds: [],
      topicIdsWithQuestions: new Set(),
      formulaCards: [],
    }
    expect(search(empty, 'anything')).toEqual([])
  })
})
