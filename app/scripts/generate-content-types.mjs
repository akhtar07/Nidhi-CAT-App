#!/usr/bin/env node
// Generate src/types/content.ts from /content/schemas/*.json.
//
// Usage: node scripts/generate-content-types.mjs [--check]
//
// --check: don't write the file; exit non-zero if regenerated output would
// differ from what's currently committed. Used by CI to catch drift between
// the JSON Schemas and the committed TS types (see PROGRESS.md).

import { compile } from 'json-schema-to-typescript'
import { readFile, readdir, writeFile } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const REPO_ROOT = path.resolve(__dirname, '..', '..')
const SCHEMAS_DIR = path.join(REPO_ROOT, 'content', 'schemas')
const OUT_FILE = path.join(__dirname, '..', 'src', 'types', 'content.ts')

const HEADER = `/* eslint-disable */
/**
 * AUTO-GENERATED — do not hand-edit.
 *
 * Source of truth is /pipeline/schemas.py (pydantic v2). Regenerate via:
 *   python pipeline/generate_json_schemas.py
 *   node app/scripts/generate-content-types.mjs
 * CI fails the build if this file drifts from that source. See
 * PROGRESS.md for the full generation flow.
 */

`

// pydantic auto-titles every field (e.g. `id` -> title "Id"). If left in,
// json-schema-to-typescript hoists each into its own top-level exported type
// alias, named after the title — and those names collide across the four
// schemas once concatenated into one file (multiple `export type Id = ...`).
// Field-level titles carry no type information we need (the property key
// already names the field in the generated interface), so strip them before
// compiling. $defs keep their own title — that's what names the nested
// interfaces (WorkedExample, VerificationRecord, ...) and those don't collide.
function stripPropertyTitles(node) {
  if (!node || typeof node !== 'object') return
  if (node.properties) {
    for (const propSchema of Object.values(node.properties)) {
      delete propSchema.title
      stripPropertyTitles(propSchema)
    }
  }
  if (node.items) stripPropertyTitles(node.items)
}

function cleanSchema(schema) {
  stripPropertyTitles(schema)
  if (schema.$defs) {
    for (const def of Object.values(schema.$defs)) {
      stripPropertyTitles(def)
    }
  }
  return schema
}

async function generate() {
  const files = (await readdir(SCHEMAS_DIR))
    .filter((f) => f.endsWith('.schema.json'))
    .sort()

  const parts = []
  for (const file of files) {
    const raw = await readFile(path.join(SCHEMAS_DIR, file), 'utf-8')
    const schema = cleanSchema(JSON.parse(raw))
    const ts = await compile(schema, schema.title ?? file, {
      bannerComment: '',
      additionalProperties: false,
      style: { semi: false, singleQuote: true },
    })
    parts.push(ts.trim())
  }

  return HEADER + parts.join('\n\n') + '\n'
}

async function main() {
  const check = process.argv.includes('--check')
  const generated = await generate()

  if (check) {
    let existing = ''
    try {
      existing = await readFile(OUT_FILE, 'utf-8')
    } catch {
      // file doesn't exist yet — treat as drift
    }
    if (existing !== generated) {
      console.error(
        'Drift detected between /content/schemas/*.json and src/types/content.ts.',
      )
      console.error('Run: node app/scripts/generate-content-types.mjs')
      process.exit(1)
    }
    console.log('OK — src/types/content.ts matches /content/schemas/*.json.')
    return
  }

  await writeFile(OUT_FILE, generated)
  console.log(`Wrote ${OUT_FILE}`)
}

main().catch((err) => {
  console.error(err)
  process.exit(1)
})
