# Progress log

## Milestone order (revised)
Original SPEC.md §15 order is sequential (0,1,2,3,...). Revised for this build:

**0 → 1 → 3 → 2 → 4 → 5 → ...**

Milestone 2 (Storage layer / StorageAdapter / DexieAdapter) is deferred until
after Milestone 3 (Content pipeline v1). Rationale: the pipeline emits JSON
into `/content` and has no dependency on learner-state storage, so there's no
reason to block content ingestion on it. All other milestones keep their
original numbers and order from SPEC.md §15.

## Current milestone: 3 — Content pipeline v1 (not started)

## Binding decision (implemented in Milestone 1 — this is now how it works)
So the pipeline (Python) and app (TypeScript) content schemas can never drift:

- **`/pipeline/schemas.py`** (pydantic v2) is the single source of truth for
  every content type in SPEC.md §5.1 (`MicroTopic`, `Lesson`, `Question`,
  `PassageSet`, etc.).
- JSON Schemas are **generated** from the pydantic models into
  `/content/schemas/*.json`.
- TypeScript types are **generated** from those JSON Schemas into
  `/app/src/types/content.ts` via `json-schema-to-typescript` (new dev
  dependency, added to SPEC.md §7 tooling — approved as part of this
  decision, do not ask again).
- Both generated outputs (`/content/schemas/*.json` and
  `/app/src/types/content.ts`) are committed to git.
- CI regenerates both from `/pipeline/schemas.py` on every push and fails the
  build if the regenerated output differs from what's committed (drift
  check).
- **Never hand-edit `/app/src/types/content.ts` or `/content/schemas/*.json`.**
  Change `/pipeline/schemas.py` and regenerate.

Learner-state types (SPEC.md §5.2 — `Attempt`, `MasteryState`, `PlanDay`,
`MockResult`, `Settings`) are NOT part of this generation pipeline; they are
TypeScript-native (Milestone 2, storage layer) since they never need to be
produced or validated by the Python pipeline.

## Completed

### Milestone 1 — Schemas & syllabus (done)
- **`/pipeline/schemas.py`** — pydantic v2 models for every SPEC.md §5.1
  content type: `MicroTopic`, `Lesson`, `Question`, `PassageSet`, plus three
  sub-types SPEC.md references but never defines (`WorkedExample`,
  `FormulaCard`, `VerificationRecord` — shapes proposed and confirmed with
  the project owner before implementation, see below). All models use
  `extra="forbid"` — unknown fields in content JSON are a hard error.
  `Question` has a `model_validator` enforcing the mcq/tita field split
  (mcq needs `options`+`correctKey` matching one option and no
  `correctValue`; tita needs `correctValue` and no `options`/`correctKey`).
- **Two confirmed deviations from SPEC.md §5.1's literal text**, both
  flagged to and approved by the project owner before writing code:
  - `MicroTopic.formulaCardId` (present in §3's prose, absent from §5.1's
    canonical TS interface) is **omitted** — `FormulaCard.microTopicId`
    covers the same relationship in the other direction, so a micro-topic
    can have any number of formula cards without a schema conflict.
  - `WorkedExample`, `FormulaCard`, `VerificationRecord` shapes are new
    (see `pipeline/schemas.py` docstring for the exact fields and the
    SPEC.md sections each field is grounded in).
- **`pipeline/generate_json_schemas.py`** — writes
  `content/schemas/{micro-topic,lesson,question,passage-set}.schema.json`
  from the pydantic models. `--check` mode diffs regenerated output against
  what's committed and exits non-zero on drift (wired into CI).
- **`app/scripts/generate-content-types.mjs`** — reads
  `content/schemas/*.json`, strips pydantic's auto-generated per-field
  `title`s before compiling (left in, they'd hoist every field into its own
  top-level exported type alias, e.g. `Id`, `Bodymarkdown` — and those
  collide once four schemas' output lands in one file), then runs
  `json-schema-to-typescript` and writes `app/src/types/content.ts`.
  `--check` mode (`npm run generate:types:check`) diffs the same way.
- **`content/syllabus.json`** — all 86 micro-topics from SPEC.md §3 (VARC
  17, DILR 24, QA 45), built via `pipeline/build_syllabus.py` (a Python
  script constructing + pydantic-validating the list, not hand-typed JSON).
  Stable dotted slug ids (`qa.arith.tsd-boats-streams`), three-level
  `section` → `topicId` → micro-topic hierarchy, a prerequisite DAG
  (verified acyclic), and `catFrequency`/`roiScore` assigned per topic.
  **These two fields are pipeline-author judgment calls**, not measured
  data — anchored on the relative-weight language SPEC.md §3 itself already
  uses (RC ≈ 2/3 of VARC, Arithmetic ≈ 40–45% of QA) and on the explicit
  "drop Trigonometry heights & distances / Binary logic / Base systems"
  triage example in §10.2 (those three are deliberately scored
  `catFrequency: low`/`rare`, `roiScore` 1–2, to match that example). Per
  §6.4, expect these to be superseded by empirical Elo data once there's
  attempt history — nothing downstream should treat them as fixed truth.
- **`pipeline/validate_content.py`** — the "schema-validate-content" CI
  job. Validates `syllabus.json` (schema + unique ids + no orphan
  prerequisites + acyclic graph), and will validate `content/lessons/`,
  `content/questions/`, `content/passage-sets/` once those exist (empty
  directories are skipped, not an error — no content yet is fine, fake
  content is not). Also checks every `Lesson.microTopicId` /
  `Question.microTopicIds` resolves to a real syllabus entry.
- **CI** (`.github/workflows/deploy.yml`): now
  `lint → typecheck → JSON-Schema drift check → TS-types drift check →
  validate content → build → deploy`, matching SPEC.md §7's pipeline order
  (`vitest` step still absent — no tests exist yet, nothing to run).
  Ran the full sequence locally in CI order before pushing; all green.

### Milestone 0 — Repo scaffold (done)
- `/app`: Vite + React 18 + TypeScript strict + Tailwind CSS v4 + shadcn/ui
  (`base-nova` style, neutral base color, `dark` class variant support).
  `Button` component installed as the first shadcn primitive.
- Path alias `@/*` → `app/src/*` wired in `tsconfig.json`/`tsconfig.app.json`
  (no `baseUrl` — deprecated in the installed TS 6.0 toolchain, `paths`
  resolves relative to the tsconfig file instead) and `vite.config.ts`.
- `react-router-dom` with `HashRouter` (avoids the GitHub Pages
  404-on-refresh trap per SPEC.md §7). Single placeholder route at `/`
  rendering `src/pages/Today.tsx`.
- `vite.config.ts` → `base: '/Nidhi-CAT-App/'` for the
  `akhtar07/Nidhi-CAT-App` GitHub Pages deployment. Verified via
  `vite preview` that all asset URLs resolve under that base.
- Lint via `oxlint` (installed by the shadcn CLI in place of ESLint;
  equivalent role — fails CI on errors). `npm run typecheck` (`tsc -b`)
  separated from `npm run build` (`vite build`) so CI can run them as
  distinct steps.
- Top-level `/content` and `/pipeline` folders created (each with a short
  README) as placeholders for Milestones 1 and 3; both empty pending those
  milestones. `/pipeline/raw/` exists locally and is gitignored per the new
  hard rule.
- `.github/workflows/deploy.yml`: on push to `main`, runs
  `npm ci → lint → typecheck → build` in `/app`, then deploys `app/dist` to
  GitHub Pages via `actions/configure-pages` +
  `actions/upload-pages-artifact` + `actions/deploy-pages` (Pages source =
  GitHub Actions, already configured on the repo).
- Verified live: pushed to `main`, workflow run succeeded
  (run id 31280771973), `https://akhtar07.github.io/Nidhi-CAT-App/` returns
  200 with the placeholder page and correctly prefixed asset paths.

## Schema changes since SPEC.md
- SPEC.md §6: added a hard rule — raw source material (PYQ PDFs, scraped
  HTML, third-party solution text) is never committed; lives in
  `/pipeline/raw/` (gitignored). Only pipeline-generated JSON in `/content/`
  is committed, and every asset must carry a `licence` field or CI fails.
- SPEC.md §7: added `json-schema-to-typescript` as a frontend dev
  dependency, and documented the schemas.py → JSON Schema → TS generation
  flow, per the binding decision above (implemented in Milestone 1).
- `MicroTopic.formulaCardId`, present in §3's prose but absent from §5.1's
  canonical TS interface, is **not** implemented — §5.1 was treated as
  authoritative. `FormulaCard.microTopicId` covers the relationship in the
  other direction. Confirmed with the project owner before implementation.
- `WorkedExample`, `FormulaCard`, `VerificationRecord` — referenced in
  §5.1 (`Lesson.workedExamples`/`formulaCards`, `Question.verification`)
  but never defined anywhere in SPEC.md. Shapes proposed and confirmed
  with the project owner before implementation; see
  `pipeline/schemas.py` for the exact fields.

## Known issues / deferred
- Milestone 2 (Storage layer) deferred until after Milestone 3 — see
  "Milestone order" above.
