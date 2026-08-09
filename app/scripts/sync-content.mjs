#!/usr/bin/env node
// Copy /content (repo root, single source of truth) into app/public/content
// so Vite serves it in dev and copies it into dist/ verbatim on build. This
// keeps content data out of the JS bundle — it's fetched at runtime, not
// imported — which matters once the bank grows past a few hundred items,
// and lines up with SPEC.md §16's CONTENT_VERSION service-worker-cache
// design (Milestone 15): a content update shouldn't require a JS rebuild
// to invalidate.
//
// Runs automatically before `dev` and `build` (npm's pre<script> hook).
// app/public/content is gitignored — it's a build artifact, never committed.

import { cp, readdir, readFile, rm, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = path.resolve(__dirname, '..', '..')
const SRC = path.join(REPO_ROOT, 'content')
const DEST = path.join(__dirname, '..', 'public', 'content')

await rm(DEST, { recursive: true, force: true })
await cp(SRC, DEST, { recursive: true })

// Static hosting can't list a directory, so the app needs a manifest to
// find "all questions for micro-topic X" without fetching every file.
// Built here (read-only against the committed /content/questions/*.json)
// rather than in the pipeline, so it's always in sync with whatever is on
// disk and never itself a committed, driftable artifact.
const questionsDir = path.join(DEST, 'questions')
const files = (await readdir(questionsDir)).filter((f) => f.endsWith('.json'))
const index = []
for (const file of files) {
  const q = JSON.parse(await readFile(path.join(questionsDir, file), 'utf-8'))
  index.push({
    id: q.id,
    microTopicIds: q.microTopicIds,
    section: q.section,
    format: q.format,
    difficulty: q.difficulty,
    targetSeconds: q.targetSeconds,
  })
}
await writeFile(path.join(questionsDir, 'index.json'), JSON.stringify(index))

// Same reasoning for lessons: a small index of which micro-topics have a
// lesson, so the app doesn't have to 404-probe all 86 topics to find out.
const lessonsDir = path.join(DEST, 'lessons')
let lessonMicroTopicIds = []
try {
  const lessonFiles = (await readdir(lessonsDir)).filter((f) => f.endsWith('.json') && f !== 'index.json')
  lessonMicroTopicIds = await Promise.all(
    lessonFiles.map(async (file) => {
      const lesson = JSON.parse(await readFile(path.join(lessonsDir, file), 'utf-8'))
      return lesson.microTopicId
    }),
  )
  await writeFile(path.join(lessonsDir, 'index.json'), JSON.stringify(lessonMicroTopicIds))
} catch {
  // No content/lessons/ directory yet — nothing to index.
}

// Same reasoning for passage-sets (Milestone 8): a small index of DILR/RC
// set summaries — the app needs to list "sets available for this
// micro-topic" without fetching every set file just to read its metadata.
const passageSetsDir = path.join(DEST, 'passage-sets')
let passageSetIndex = []
try {
  const setFiles = (await readdir(passageSetsDir)).filter((f) => f.endsWith('.json') && f !== 'index.json')
  passageSetIndex = await Promise.all(
    setFiles.map(async (file) => {
      const set = JSON.parse(await readFile(path.join(passageSetsDir, file), 'utf-8'))
      return {
        id: set.id,
        section: set.section,
        kind: set.kind,
        questionIds: set.questionIds ?? [],
        targetMinutes: set.targetMinutes,
      }
    }),
  )
  await writeFile(path.join(passageSetsDir, 'index.json'), JSON.stringify(passageSetIndex))
} catch {
  // No content/passage-sets/ directory yet — nothing to index.
}

console.log(
  `Synced ${SRC} -> ${DEST} (${index.length} questions, ${lessonMicroTopicIds.length} lessons, ${passageSetIndex.length} passage-sets indexed)`,
)
