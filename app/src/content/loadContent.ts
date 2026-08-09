import type { ExamMeta, Lesson, MicroTopic, MockDefinition, PassageSet, Question } from '@/types/content'

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

let examMetaCache: Promise<ExamMeta> | null = null
export function loadExamMeta(): Promise<ExamMeta> {
  examMetaCache ??= fetchJson<ExamMeta>(contentUrl('exam-meta.json'))
  return examMetaCache
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

export async function loadMicroTopic(microTopicId: string): Promise<MicroTopic | undefined> {
  const syllabus = await loadSyllabus()
  return syllabus.find((t) => t.id === microTopicId)
}

/**
 * Syllabus topics that actually have drillable content — most of §3's
 * taxonomy (all of VARC, most of DILR) has no questions yet (RC/VA/DILR-set
 * generation is Milestone 13), so anything that schedules or lists topics
 * to *do* (the planner, Today's topic list) must filter through this
 * first, or it points at a topic with nothing behind it.
 */
export async function topicsWithContent(): Promise<MicroTopic[]> {
  const [syllabus, index] = await Promise.all([loadSyllabus(), loadQuestionIndex()])
  const idsWithContent = new Set(index.flatMap((entry) => entry.microTopicIds))
  return syllabus.filter((t) => idsWithContent.has(t.id))
}

let lessonIndexCache: Promise<string[]> | null = null
export function loadLessonIndex(): Promise<string[]> {
  lessonIndexCache ??= fetchJson<string[]>(contentUrl('lessons/index.json'))
  return lessonIndexCache
}

export async function loadLesson(microTopicId: string): Promise<Lesson | undefined> {
  const index = await loadLessonIndex()
  if (!index.includes(microTopicId)) return undefined
  return fetchJson<Lesson>(contentUrl(`lessons/${microTopicId}.json`))
}

export interface PassageSetIndexEntry {
  id: string
  section: PassageSet['section']
  kind: PassageSet['kind']
  questionIds: string[]
  targetMinutes: number
}

let passageSetIndexCache: Promise<PassageSetIndexEntry[]> | null = null
export function loadPassageSetIndex(): Promise<PassageSetIndexEntry[]> {
  passageSetIndexCache ??= fetchJson<PassageSetIndexEntry[]>(contentUrl('passage-sets/index.json'))
  return passageSetIndexCache
}

export function loadPassageSet(id: string): Promise<PassageSet> {
  return fetchJson<PassageSet>(contentUrl(`passage-sets/${id}.json`))
}

let mockIndexCache: Promise<string[]> | null = null
export function loadMockIndex(): Promise<string[]> {
  mockIndexCache ??= fetchJson<string[]>(contentUrl('mocks/index.json'))
  return mockIndexCache
}

export function loadMockDefinition(id: string): Promise<MockDefinition> {
  return fetchJson<MockDefinition>(contentUrl(`mocks/${id}.json`))
}
