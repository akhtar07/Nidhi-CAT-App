import type { Lesson, MicroTopic, Question } from '@/types/content'

type Section = Question['section']

/** A formula card lifted out of its lesson, carrying enough topic context to stand alone. */
export interface RevisionCard {
  id: string
  microTopicId: string
  topicName: string
  section: Section
  title: string
  bodyMarkdown: string
  exampleMarkdown: string | null
}

/** A "common trap" line lifted out of its lesson. These have no id in the content schema,
 * so one is synthesised from the topic and position — stable as long as the lesson is. */
export interface RevisionTrap {
  id: string
  microTopicId: string
  topicName: string
  section: Section
  text: string
}

export interface RevisionIndex {
  cards: RevisionCard[]
  traps: RevisionTrap[]
}

/**
 * Flattens every lesson's formulaCards and commonTraps into two browsable lists.
 *
 * This content already ships (188 cards and 263 traps across 86 lessons) but is only
 * reachable by opening each lesson one at a time, which makes it useless for revision —
 * the moment you actually want it is when you cannot remember which topic it belonged to.
 *
 * Lessons whose micro-topic is missing from the syllabus are skipped rather than shown with
 * a blank section, since section is what the hub filters on.
 */
export function buildRevisionIndex(lessons: Lesson[], syllabus: MicroTopic[]): RevisionIndex {
  const topicById = new Map(syllabus.map((t) => [t.id, t]))
  const cards: RevisionCard[] = []
  const traps: RevisionTrap[] = []

  for (const lesson of lessons) {
    const topic = topicById.get(lesson.microTopicId)
    if (!topic) continue

    for (const card of lesson.formulaCards ?? []) {
      cards.push({
        id: card.id,
        microTopicId: lesson.microTopicId,
        topicName: topic.name,
        section: topic.section,
        title: card.title,
        bodyMarkdown: card.bodyMarkdown,
        exampleMarkdown: card.exampleMarkdown ?? null,
      })
    }

    ;(lesson.commonTraps ?? []).forEach((text, i) => {
      traps.push({
        id: `${lesson.microTopicId}.trap-${i}`,
        microTopicId: lesson.microTopicId,
        topicName: topic.name,
        section: topic.section,
        text,
      })
    })
  }

  return { cards, traps }
}

/**
 * Splits a query into lowercase tokens. Every token must appear somewhere in the haystack
 * (AND, not OR), so "percent change" narrows rather than widening — which is what a person
 * typing two words almost always means.
 */
export function tokenise(query: string): string[] {
  return query.toLowerCase().split(/\s+/).filter(Boolean)
}

export function matchesQuery(haystack: string, tokens: string[]): boolean {
  if (tokens.length === 0) return true
  const lower = haystack.toLowerCase()
  return tokens.every((t) => lower.includes(t))
}

export interface RevisionFilters {
  section: Section | null
  query: string
}

export function filterCards(cards: RevisionCard[], filters: RevisionFilters): RevisionCard[] {
  const tokens = tokenise(filters.query)
  return cards.filter((c) => {
    if (filters.section && c.section !== filters.section) return false
    return matchesQuery(`${c.title} ${c.bodyMarkdown} ${c.exampleMarkdown ?? ''} ${c.topicName}`, tokens)
  })
}

export function filterTraps(traps: RevisionTrap[], filters: RevisionFilters): RevisionTrap[] {
  const tokens = tokenise(filters.query)
  return traps.filter((t) => {
    if (filters.section && t.section !== filters.section) return false
    return matchesQuery(`${t.text} ${t.topicName}`, tokens)
  })
}

/** Groups by micro-topic, preserving first-seen order, so the hub can render topic headings. */
export function groupByTopic<T extends { microTopicId: string; topicName: string }>(
  items: T[],
): { microTopicId: string; topicName: string; items: T[] }[] {
  const groups = new Map<string, { microTopicId: string; topicName: string; items: T[] }>()
  for (const item of items) {
    const existing = groups.get(item.microTopicId)
    if (existing) existing.items.push(item)
    else groups.set(item.microTopicId, { microTopicId: item.microTopicId, topicName: item.topicName, items: [item] })
  }
  return [...groups.values()]
}
