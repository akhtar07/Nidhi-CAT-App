import type { MicroTopic, Question } from '@/types/content'

/**
 * All shipped content is fetched at runtime from static JSON under
 * `/content` (synced from the repo-root `/content` by
 * scripts/sync-content.mjs — see that file for why it's fetched rather
 * than bundled). Never hardcode question/content data in components
 * (CLAUDE.md hard rule) — everything goes through these functions.
 */

export interface QuestionIndexEntry {
  id: string
  microTopicIds: string[]
  section: Question['section']
  format: Question['format']
  difficulty: Question['difficulty']
  targetSeconds: number
}

function contentUrl(relativePath: string): string {
  return `${import.meta.env.BASE_URL}content/${relativePath}`
}

async function fetchJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (!res.ok) {
    throw new Error(`Failed to fetch ${url}: ${res.status} ${res.statusText}`)
  }
  return res.json() as Promise<T>
}

let syllabusCache: Promise<MicroTopic[]> | null = null
export function loadSyllabus(): Promise<MicroTopic[]> {
  syllabusCache ??= fetchJson<MicroTopic[]>(contentUrl('syllabus.json'))
  return syllabusCache
}

let questionIndexCache: Promise<QuestionIndexEntry[]> | null = null
export function loadQuestionIndex(): Promise<QuestionIndexEntry[]> {
  questionIndexCache ??= fetchJson<QuestionIndexEntry[]>(contentUrl('questions/index.json'))
  return questionIndexCache
}

export function loadQuestion(id: string): Promise<Question> {
  return fetchJson<Question>(contentUrl(`questions/${id}.json`))
}

export async function loadQuestionsForMicroTopic(microTopicId: string): Promise<Question[]> {
  const index = await loadQuestionIndex()
  const ids = index.filter((entry) => entry.microTopicIds.includes(microTopicId)).map((entry) => entry.id)
  return Promise.all(ids.map(loadQuestion))
}
