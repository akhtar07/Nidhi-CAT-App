import { matchesQuery, tokenise, type RevisionCard } from '@/revision/revisionIndex'
import type { MicroTopic, Question } from '@/types/content'

type Section = Question['section']

export type SearchResultKind = 'topic' | 'lesson' | 'formula'

export interface SearchResult {
  kind: SearchResultKind
  /** Unique within a result list — kind is included because a topic and its lesson share an id. */
  key: string
  title: string
  /** Short context line under the title. */
  subtitle: string
  section: Section
  /** In-app route to jump straight to the thing. */
  to: string
}

export interface SearchCorpus {
  topics: MicroTopic[]
  /** Micro-topic ids that have a lesson (content/lessons/index.json). */
  lessonTopicIds: string[]
  /** Micro-topic ids that have at least one non-reserved question. */
  topicIdsWithQuestions: Set<string>
  formulaCards: RevisionCard[]
}

/**
 * Ordering: exact-ish topic matches first, then lessons, then formulas. Within a kind,
 * a title match outranks a body-only match, because someone typing "percentages" wants the
 * topic before a formula that merely mentions the word.
 */
function rank(result: SearchResult, tokens: string[]): number {
  const title = result.title.toLowerCase()
  const titleHit = tokens.every((t) => title.includes(t))
  const kindWeight = result.kind === 'topic' ? 0 : result.kind === 'lesson' ? 1 : 2
  return kindWeight * 10 + (titleHit ? 0 : 5)
}

/**
 * One search across micro-topics, lessons and formula cards.
 *
 * Deliberately dumb matching: lowercase substring, every token required. No fuzzy-matching
 * dependency, and over a corpus of ~86 topics plus ~188 cards it runs in well under a frame,
 * so there is nothing to gain from an index.
 *
 * A blank query returns nothing rather than everything — a search page showing 350 results
 * before you have typed is noise, not help.
 */
export function search(corpus: SearchCorpus, query: string, limit = 40): SearchResult[] {
  const tokens = tokenise(query)
  if (tokens.length === 0) return []

  const lessonIds = new Set(corpus.lessonTopicIds)
  const results: SearchResult[] = []

  for (const topic of corpus.topics) {
    if (!matchesQuery(topic.name, tokens)) continue
    const hasQuestions = corpus.topicIdsWithQuestions.has(topic.id)
    results.push({
      kind: 'topic',
      key: `topic:${topic.id}`,
      title: topic.name,
      subtitle: hasQuestions ? `${topic.section} · practise this topic` : `${topic.section} · no questions yet`,
      section: topic.section,
      // Route through the lesson, matching the app's teaching-before-practice flow; Lesson
      // itself falls back to "practise anyway" when a topic has no lesson.
      to: `/lesson/${topic.id}`,
    })
    if (lessonIds.has(topic.id)) {
      results.push({
        kind: 'lesson',
        key: `lesson:${topic.id}`,
        title: `${topic.name} — lesson`,
        subtitle: `${topic.section} · read the lesson`,
        section: topic.section,
        to: `/lesson/${topic.id}`,
      })
    }
  }

  for (const card of corpus.formulaCards) {
    if (!matchesQuery(`${card.title} ${card.bodyMarkdown} ${card.topicName}`, tokens)) continue
    results.push({
      kind: 'formula',
      key: `formula:${card.id}`,
      title: card.title,
      subtitle: `${card.section} · formula in ${card.topicName}`,
      section: card.section,
      to: `/lesson/${card.microTopicId}`,
    })
  }

  return results.sort((a, b) => rank(a, tokens) - rank(b, tokens)).slice(0, limit)
}
