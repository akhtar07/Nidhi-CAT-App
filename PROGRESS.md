# Progress log

## Milestone order (revised)
Original SPEC.md §15 order is sequential (0,1,2,3,...). Revised for this build:

**0 → 1 → 3 → 2 → 4 → 5 → ...**

Milestone 2 (Storage layer / StorageAdapter / DexieAdapter) is deferred until
after Milestone 3 (Content pipeline v1). Rationale: the pipeline emits JSON
into `/content` and has no dependency on learner-state storage, so there's no
reason to block content ingestion on it. All other milestones keep their
original numbers and order from SPEC.md §15.

## Current milestone: 2 — Storage layer (not started)

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

### Milestone 3 — Content pipeline v1 (done, via a sourcing pivot — read this first)

**SPEC.md §6.1's Tier 1 plan (official PYQ PDFs "circulate as public PDFs")
does not hold up.** Verified by research before writing any ingestion code:
IIM CAT never publishes a standalone question-paper PDF. The only official
view of real questions is the response-sheet/answer-key page, gated behind
each candidate's own CAT login (User ID + password), live only for a ~3-day
objection window right after the exam. The official mock test — also built
from real PYQs — has the same login gate and is only live for ~2 weeks
before the exam (not this time of year). What's actually freely
downloadable everywhere is coaching-site content (2IIM, Cracku, CatKing,
Testbook, ...), which SPEC.md §6.1 already forbids scraping, in its own
words: *"a public GitHub repo full of their content is a DMCA takedown
waiting to happen."*

This was put to the project owner directly, including an explicit request
to scrape those coaching sites anyway — **declined**: reproducing
copyrighted commercial question banks and solutions in a public repo is
infringement regardless of instruction, not a risk that's the requester's
alone to accept, since the infringing act (the reproduction) happens the
moment it's generated and committed.

**Resolution: Tier 3 instead of Tier 1 for this milestone.** SPEC.md §6.3
already specifies exactly this fallback — originally-authored items,
verified by an independent, executable check rather than sourced from a
third party. Every item here has `source: 'generated'` (not
`'official_pyq'`), is honestly labelled as such, and is real content, not
fabricated: every claimed answer is checked by running code that computes
it independently before the item is kept.

- **`pipeline/qagen/`** — the generation + verification harness.
  - `harness.py`: an `ItemSpec` carries a stem, a claimed answer, and an
    `answer_fn` that recomputes the answer independently. `verify_and_build()`
    runs `answer_fn()` and only constructs a `Question` if it matches the
    claim (numeric tolerance for TITA, exact for strings) — mismatch means
    **discarded, not repaired**, per §6.3. MCQ items also get a distractor
    audit (no duplicate option values). `run_generators()` also dedupes on
    `(microtopic_id, stem)` — a small random-parameter space can draw the
    same question twice; the second draw is dropped rather than let it
    silently overwrite the first item's file (10 duplicates caught this way
    across 249 initial draws → 239 unique items shipped).
  - `generators/{arithmetic,algebra,geometry,numsys,modern}.py` — one
    generator function per QA micro-topic (all 45 of them), each
    parameterized and randomized, producing 2–8 instances per topic
    (weighted by `roiScore`: 8/6/4/3/2 for roiScore 5/4/3/2/1 — more
    generation effort on higher-ROI topics, per the triage philosophy in
    §10.2). **Caught a real bug this way**: the first version of the
    percentages/profit-loss generators used the *same* buggy closed-form
    formula for both the claimed answer and the "independent" check, so a
    genuine arithmetic error (`-99.41%` instead of the correct `-40.60%`)
    passed verification — the two paths weren't actually independent.
    Fixed by making every `answer_fn` a genuinely different computation
    method than whatever produced the displayed solution (sequential
    float simulation vs. closed-form; brute-force enumeration vs. formula;
    `sympy` symbolic vs. direct arithmetic; direct-factorial vs. Legendre's
    formula), and manually spot-checked ≥1 sample per generator (45/45) by
    hand after that fix, not just trusted the "verified" flag.
  - `syllabus_lookup.py` — pulls `targetSecPerQuestion` per micro-topic
    from `content/syllabus.json` so generated items' timing ties back to
    the syllabus rather than being re-guessed.
  - `run.py` — orchestrates all 45 generators, verifies, writes
    `content/questions/<id>.json` (one file per question; ids are
    content-hash based on `microtopic_id + stem + claimed_value`).
- **Result: 239 verified QA questions** across all 45 QA micro-topics
  (≥200 target met with headroom). Every item has `verification.method =
  'sympy_verified'`, a mandatory non-empty `solutionMarkdown`, and (where
  useful) an `altSolutionMarkdown` "smart approach" per §13. Difficulty is
  cycled (easy/medium/hard/very_hard) within each topic's item count, so
  topics with ≥6 items have hard-tier coverage; the 2–3 item topics
  (lowest roiScore) don't — flagged under Known issues below.
- **`pipeline/review_ui/app.py`** — the human review UI SPEC.md §6.2 step 6
  calls for ("Approve / Fix / Reject"), built with Streamlit per the
  spec's own suggestion. No PDF crop to show alongside (nothing here came
  from a PDF) — shows the rendered question, options/correct value,
  solution(s), and verification metadata instead. Decisions log to
  `pipeline/review_log.json` keyed by question id; **never mutates
  `content/questions/*.json` directly** — rejecting an item logs the
  rejection but doesn't delete it, so removal is always a deliberate,
  reviewable second step. Smoke-tested headless (`streamlit run ... 
  --server.headless true`, confirmed HTTP 200, no errors in server log) —
  the project owner hasn't done an interactive review pass yet; that's
  still open, see Known issues.
- **`validate_content.py`** (built in Milestone 1, unchanged) now
  validates all 239 real items — schema conformance, orphan
  `microTopicIds` — with no code changes needed, since it was already
  written to scan `content/questions/*.json` generically.
- Also ran a bank-wide KaTeX delimiter balance check (`$...$` pairing) as a
  cheap sanity pass — not the full automated KaTeX-render check SPEC.md
  §16 wants (that needs an actual KaTeX renderer, more natural once the
  question player exists), but catches the most common breakage. Clean
  across all 239 items.
- CI: no changes needed to the "Validate content" step — it already ran
  `validate_content.py` generically. Added `pipeline/requirements-review.txt`
  (streamlit, `-r requirements.txt`) split out from `pipeline/requirements.txt`
  (pydantic, sympy) so CI's installs stay fast — CI never touches the
  review UI, only schema/content validation.
- Ran the full local CI sequence (lint → typecheck → JSON-Schema drift →
  TS-types drift → validate content → build) before pushing; all green.

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
- SPEC.md §6.1: corrected the Tier 1 sourcing claim ("official PYQ PDFs
  circulate publicly") — verified false during Milestone 3, see the
  Milestone 3 writeup above for the full account. Tier 1 is now marked
  opportunistic rather than planned; Tier 3 (§6.3) is the realistic
  primary QA/DILR source going forward, unless the project owner supplies
  legitimately-obtained papers directly.

## Known issues / deferred
- Milestone 2 (Storage layer) deferred until after Milestone 3 — see
  "Milestone order" above.
- Content bank is QA only (239 items, all `source: 'generated'`). No
  official PYQ items exist in the bank at all — see the Tier 1 correction
  above. VARC, DILR, and lessons are still empty; DILR sets in particular
  need programmatically-generated underlying data tables per §6.3's "never
  let the LLM invent the numbers" rule, which this milestone didn't touch.
- The lowest-`roiScore` QA topics (2–3 items each: `tsd-races`,
  `time-work-chain-rule`, `base-systems`, `maxima-minima`, `trigonometry`,
  `binomial-theorem`, `series-sequences-hybrids`) don't have hard/very_hard
  items — too few items per topic for the difficulty cycle to reach that
  tier. Fine for now (matches their low-ROI/triage status per §10.2) but
  will matter once the mastery engine's "ceiling proof" criterion (§8.2.3,
  ≥2 hard/very_hard correct) is implemented against these topics.
- `pipeline/review_ui/app.py` is built and smoke-tested (starts cleanly,
  serves HTTP 200, no server errors) but the project owner has not yet done
  an interactive Approve/Fix/Reject pass over the 239 items. Run `streamlit
  run review_ui/app.py` from `/pipeline` to do that pass; nothing in the
  bank is blocked on it, but it's the "step everyone skips" §6.2 warns
  about.
