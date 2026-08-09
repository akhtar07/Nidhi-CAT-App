# Progress log

## Milestone order (revised)
Original SPEC.md §15 order is sequential (0,1,2,3,...). Revised for this build:

**0 → 1 → 3 → 2 → 4 → 5 → ...**

Milestone 2 (Storage layer / StorageAdapter / DexieAdapter) is deferred until
after Milestone 3 (Content pipeline v1). Rationale: the pipeline emits JSON
into `/content` and has no dependency on learner-state storage, so there's no
reason to block content ingestion on it. All other milestones keep their
original numbers and order from SPEC.md §15.

## Current milestone: 7 — Content pipeline v2 (not started)

**Milestone 6's own row in SPEC.md §15 says "Stop and demo this before
scaling content."** Done below — but flagging explicitly that this is a
SPEC-designated checkpoint, not just another milestone to plow through.
The project owner should actually open `/lesson/qa.arith.percentages`
before more content gets built on top of this pattern.

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

### Milestone 6 — Lesson reader + Learn→Drill loop (done — demo checkpoint, see note above)
- **First real Lesson content**: `pipeline/build_lesson_percentages.py`
  writes `content/lessons/qa.arith.percentages.json` via the same
  pydantic-validated pattern as `build_syllabus.py` (not hand-typed JSON).
  Chose percentages because it already had the deepest question bank
  (12 items) and is foundational/high-ROI. Originally authored, not
  sourced — per the "no fake/placeholder content" rule, every worked
  example's arithmetic is independently checked by hand in a code comment
  before being written into the lesson (e.g. the successive-%-change
  example is verified two ways: direct sequential multiplication *and*
  the closed-form formula, cross-checked against each other — same
  discipline as the qagen verification harness, applied to prose this
  time since there's no `answer_fn` to run). 3 worked examples, 2 formula
  cards, 5 common traps, ~6 min read.
- **`app/src/components/question-player/markdownSegments.ts` extended**:
  added `**bold**` tokens and a new `parseMarkdownBlocks()` (splits on
  blank lines, detects `## `/`### ` heading prefixes) — genuinely needed
  now that lesson prose exists (headings, bold, multi-paragraph structure),
  unlike the terse single-line question stems this parser originally
  targeted. Still no markdown dependency added; extended the same
  hand-rolled tokenizer, re-justified in the file's own header comment
  rather than silently scope-creeping. New component `MarkdownBlocks`
  (alongside the existing single-paragraph `Markdown`) renders the block
  list; both share a `renderSegments()` helper now.
  - **Bug caught and fixed while verifying live, not by the type checker**:
    `BlockMath` (react-katex) renders a `<div>`, and `MarkdownBlocks`
    initially wrapped paragraphs in `<p>` — a `$$...$$` formula inside a
    lesson paragraph produced an invalid `<div>` inside `<p>`, which
    Chrome silently "fixes" by breaking the DOM tree, and React logs a
    hydration-nesting console error. Caught by actually checking the
    browser console during Playwright verification (see below), not by
    typecheck/build, which both stayed green throughout. Fixed by making
    paragraph wrappers `<div>` instead of `<p>` — noted in a code comment
    so it isn't quietly reverted later.
  - **Second bug, also live-caught**: a `\%` written outside any `$...$`
    math span in the successive-change formula card's body text rendered
    literally as backslash-percent (LaTeX escaping only applies inside
    math segments). Fixed in the pipeline script, regenerated, verified
    the literal string no longer appears anywhere on the rendered page.
- **`app/src/pages/Lesson.tsx`** (route `/lesson/:topicId`) — renders
  `bodyMarkdown` via `MarkdownBlocks`, formula cards, worked examples
  (stem/solution/alt-solution via `Markdown`), common traps, and a "Start
  practising" button that navigates to `/drill/:topicId` — the actual
  Learn→Drill transition. Topics without a lesson yet show "Practise
  anyway" instead of a dead end.
- **`content/lessons/index.json`** — same reasoning as the questions
  index (Milestone 4): static hosting can't list a directory, so
  `sync-content.mjs` now also builds a small list of which micro-topics
  have a lesson, regenerated every sync, never committed.
- **`Today.tsx`** updated: topics with a lesson show a "Lesson" badge and
  link to `/lesson/:id` first (sorted to the top); topics without one
  still link straight to `/drill/:id` as before.
- **Verified live in Chromium (Playwright)**: topic list shows exactly
  one "Lesson" badge (percentages) → opened the lesson → confirmed 47
  KaTeX-rendered math elements (headings, bold, and formulas all render
  correctly, including the two bugs above, caught and re-verified fixed)
  → clicked "Start practising" → landed on `/drill/qa.arith.percentages`,
  confirming the Learn→Drill loop actually connects. Zero console errors
  after both fixes (there were two, both caught this way, not by
  typecheck/build).
- Ran the full local sequence before committing: lint → typecheck →
  vitest (60 tests, +4 for the new markdown block/bold parsing) → build.
  All green.
- **Scope note**: "one micro-topic fully playable end to end" is
  satisfied for exactly one topic (percentages) — this milestone is about
  proving the pattern works, not covering the other 85 micro-topics with
  lessons. That's explicitly Milestone 7+ ("scaling content"), which is
  why SPEC.md calls for a stop-and-demo here first.

### Milestone 5 — Mastery engine (done)
- **`app/src/mastery/`** — pure-function algorithm modules first, storage
  wiring second, per SPEC.md §16's acceptance line ("Mastery engine unit
  tests cover: lucky-guess handling, speed failure, hard-tier requirement,
  retention gap, anti-frustration exit" — all five are covered, by name, in
  `masteryCriteria.test.ts`).
  - `elo.ts` — SPEC.md §8.3's two-sided Elo, implemented literally:
    `expected = 1/(1+10^((itemElo-learnerElo)/400))`,
    `learnerElo += K_L*(actual-expected)` (K_L 24, decaying to 12 after 200
    attempts **on that micro-topic** — SPEC doesn't say per-topic vs.
    global, but `learnerElo` itself lives on the per-topic `MasteryState`,
    so per-topic is the only reading consistent with the schema),
    `itemElo += K_I*(expectedItem-actualItem)` with K_I=8 and the natural
    `expectedItem/actualItem = 1-expected/1-actual` (SPEC doesn't define
    those explicitly either — noted in a code comment rather than silently
    assumed). `effectiveCorrectness()` implements §8.5's guess discount: a
    correct-but-guessed answer scores 0.4, not 1, feeding into Elo's
    `actual` — not into the raw `lastNCorrect` boolean log, which stays a
    plain correctness record.
  - `masteryCriteria.ts` — `evaluateMastery()`: all four §8.2 criteria
    (accuracy >=75% over last 10 with a 12-attempt floor, using the
    guess-discounted score, not raw booleans; speed = median(last 10) <=
    targetSecPerQuestion*1.25; ceiling = >=2 hard/very_hard correct,
    lifetime; retention = a correct attempt >=3 days after criteria 1-3
    were *first* simultaneously true) plus the anti-frustration valve
    (>=30 attempts without meeting 1-3, or <40% accuracy after 15) and the
    §8.1 state machine (`learning` under 8 attempts / `practising` /
    `mastered`; `locked`/`available`/`decaying` are out of scope here —
    the first two come from prerequisite-gating UI that doesn't exist yet,
    `decaying` needs SRS scheduling, Milestone 12).
  - `selectItems.ts` — `selectDrillQueue()`: the §8.3 60/20/10/10 band
    split (productive-struggle / stretch / fluency / interleaved), excludes
    anything answered correctly in the last 14 days, backfills from the
    general pool when a band is too thin rather than truncating the queue
    (content bank is young — not every topic has a stretch-tier item yet).
  - `errorClusters.ts` — `clusterErrorTags()`, the frequency-sort behind
    §8.2's anti-frustration routing message ("needs a rewatch... route her
    back to the lesson with the specific sub-concept her error tags
    cluster around") — computed, not yet wired to an actual lesson-linking
    UI since there's no Lesson reader yet (Milestone 6).
  - `masteryEngine.ts` — `recordAttemptForMastery()`, the thin
    storage-coupled glue: loads prior learner/item Elo, updates both,
    re-evaluates criteria against the topic's full attempt history, and
    persists the new `MasteryState` + `ItemEloState`. Not unit-tested in
    isolation (it's glue, not algorithm) but has 3 integration tests
    against a real `DexieAdapter` + `fake-indexeddb`, and was exercised
    live in Chromium (see below).
  - **53 new tests** (`elo`: 9, `masteryCriteria`: 25, `selectItems`: 6,
    `masteryEngine`: 3), all passing alongside the existing 3.
- **Schema additions to `app/src/types/state.ts`** (documented per the
  schemaVersion-discipline rule, though these are additive/optional so no
  migration step was needed):
  - `MasteryState.criteria123FirstMetAt?: number` and
    `antiFrustrationTriggered?: boolean` — required to implement §8.2
    criterion 4 (retention) and the anti-frustration valve at all; neither
    exists in SPEC.md §5.2's literal interface, which doesn't attempt to
    spell out the full mastery-tracking shape.
  - **New type `ItemEloState`** (+ `StorageAdapter.getItemElo`/`putItemElo`,
    a new Dexie table via `.version(2).stores(...)`, migration plumbing,
    and an `itemEloStates` array in `ExportBundle`) — SPEC.md §8.3 needs a
    *live*, learner-adjusted item rating, but `Question.eloRating` is
    shipped content from `/content` and can't be mutated by the client;
    this is where the runtime-adjusted value lives instead, seeded from
    `Question.eloRating` on first attempt. `DexieAdapter.test.ts` extended
    with round-trip/export/import/clear coverage for it.
- **Settings page + Export/Import JSON, built now**: SPEC.md §5.2 states
  the button must ship "before Milestone 5" — there was no Settings page
  to hang it on until this session (Milestone 4 built the first real
  pages). `app/src/pages/Settings.tsx`, route `/settings`, linked from
  Today. Export downloads `storage.exportAll()` as a JSON file; Import
  reads a file and calls `storage.importAll()`. Only the backup feature —
  the rest of `Settings` (dailyMinutes/examDate/weakSectionBias/emailOptIn)
  belongs to whichever milestone builds the planner UI around them.
- **Wired into the real app, not left as a dead module**:
  `QuestionPlayer` now takes `topic`/`topicQuestions` props and calls
  `recordAttemptForMastery()` right after `storage.addAttempt()`.
  `Drill.tsx` now builds its queue via `selectDrillQueue()` (learnerElo
  from the topic's `MasteryState`, itemElo from `ItemEloState` falling
  back to `Question.eloRating`, recently-correct exclusion from the last
  14 days of attempts) instead of just playing every question in file
  order, and shows the resulting mastery status + learner Elo on the
  drill-complete screen. The interleave band is empty for now — SPEC's
  "10% from earlier mastered/decaying topics" needs a cross-topic session
  composer that doesn't exist yet (this page is still the single-topic
  harness from Milestone 4); documented in code as a known gap, not
  silently dropped.
- **Verified live in Chromium (Playwright), not just unit tests**: ran a
  10-question drill (all skipped, deliberately, to get a clean "always
  incorrect" signal) and confirmed via direct IndexedDB inspection that
  `masteryStates` (status `practising`, `learnerElo` moved down from 1200
  to ~1088) and `itemElo` (10 rows, all moved) were written correctly, and
  the completion screen displayed the live status. Then ran a second
  session, exported via the Settings page (`expect_download` — confirmed
  10 attempts / 1 mastery state / 10 item-elo rows in the downloaded
  file), **deleted the entire IndexedDB database** (`indexedDB.
  deleteDatabase('ascent')`, simulating a cleared cache), re-imported the
  same file, and confirmed all 10 attempts and the mastery state came back
  exactly. Zero console/page errors throughout.
- Ran the full local sequence before committing: lint → typecheck →
  vitest (56 tests total) → build. All green.
- **Known limitation, not addressed here**: `evaluateMastery()`
  recomputes from the *entire* attempt history on every call (no
  incremental/windowed computation) — fine at current data volumes
  (hundreds of attempts per topic at most), would need revisiting if a
  single topic's attempt count grows into the thousands.

### Milestone 4 — Question Player (done)
- **Architecture decision, not previously specified anywhere in SPEC.md: how
  content JSON reaches the browser at runtime.** SPEC.md never states this
  explicitly, only implies it (§16's `CONTENT_VERSION` service-worker-cache
  design, Milestone 15, only makes sense if content is fetched as static
  assets rather than bundled into the JS). Decision made and implemented
  (not asked about live, per the "don't stop" instruction this session —
  flagging it clearly here instead): `/content` (repo root, single source
  of truth, unchanged) is copied into `app/public/content` by
  **`app/scripts/sync-content.mjs`**, wired as `predev`/`prebuild` (npm's
  automatic pre-hook), so `npm run dev` and `npm run build` always run
  against a fresh copy. `app/public/content` is **gitignored** — it's a
  build artifact, never committed, so there's exactly one committed copy of
  content data. The app fetches it at runtime via `fetch()` (see
  `app/src/content/loadContent.ts`), not `import` — keeps content out of
  the JS bundle, matters once the bank is 800+ items.
  - Static hosting can't list a directory, so `sync-content.mjs` also
    builds `public/content/questions/index.json` (id, microTopicIds,
    section, format, difficulty, targetSeconds per question) by reading
    every committed question file — this lets the app answer "all
    questions for micro-topic X" without an HTTP request per file. It's
    regenerated every sync, never committed, so it can't drift.
- **`app/src/components/question-player/`**:
  - `markdownSegments.ts` — a small hand-rolled tokenizer for the
    `*Markdown` content fields, not a markdown library. Checked directly
    against all 239 generated questions first: every one uses only plain
    text + inline `$...$` KaTeX, nothing else — so rather than add a
    markdown-parser dependency not listed in SPEC.md §7, this splits text
    into text / inline-math / block-math (`$$...$$`, for forward
    compatibility) / image (`![alt](src)`) segments. Pure function, unit
    tested (4 cases) without needing a DOM.
  - `Markdown.tsx` — renders those segments, math via `react-katex`
    (`InlineMath`/`BlockMath`, per SPEC.md §7's existing KaTeX line).
  - `QuestionPlayer.tsx` — the component itself. State machine:
    `answering` (render MCQ options or TITA input, elapsed-time stopwatch
    against `targetSeconds`, mark-for-review toggle, skip) →
    `confidence` (guess/unsure/sure — asked **before** correctness is
    revealed, per SPEC.md §5.2's explicit ordering) → `revealed`
    (correct/incorrect, `solutionMarkdown` + `altSolutionMarkdown`,
    error-tag chips shown only when incorrect, optional). "Next" builds
    the `Attempt` record and calls `storage.addAttempt()` (Milestone 2's
    `StorageAdapter`) directly — logging isn't left to a caller to
    remember. TITA correctness checks numeric answers against
    `titaTolerance` (falls back to exact string match for non-numeric
    `correctValue`).
- **`app/src/content/loadContent.ts`** — `loadSyllabus()`,
  `loadQuestionIndex()`, `loadQuestion(id)`, `loadQuestionsForMicroTopic(id)`,
  all fetching from the synced static copy, in-memory cached per call.
- **`app/src/pages/Today.tsx`** (replaces the Milestone 0 placeholder) and
  **`app/src/pages/Drill.tsx`** (new route `/drill/:topicId`) — a minimal
  but real navigation harness to exercise the player: topic list with live
  question counts → play through every question for that topic → a
  drill-complete summary. This is **not** Milestone 6's Learn→Drill loop
  (no Lesson reader, no adaptive selection, no planner integration — those
  are their own milestones) — it exists so Milestone 4's component could
  actually be driven end-to-end and verified, and happens to double as a
  working drill mode already.
- **Verified live in a real Chromium instance (Playwright), not just
  typecheck/build**: topic list loads (45 topics, real counts) → opened a
  TITA question (percentages), answered wrong, went through confidence →
  reveal → error-tag chips → Next → opened an MCQ question
  (ratio-proportion-variation), selected an option, same flow, KaTeX
  rendered correctly for both plain and fraction-heavy solutions (checked
  `.katex` elements were actually present, not just no crash) → ran a full
  8-question drill via Skip to the completion screen → **queried
  IndexedDB directly** (`indexedDB.open('ascent')` → `attempts` store) and
  confirmed 8 real `Attempt` records were persisted with the correct
  shape. Zero console/page errors across the whole run.
- Dependencies added: `katex`, `react-katex` (+ `@types/*`) — both already
  named in SPEC.md §7, no new approval needed.
- Ran the full local sequence before committing: lint → typecheck →
  JSON-Schema drift → TS-types drift → vitest (15 tests, 4 new for the
  markdown tokenizer) → build. All green. Bundle is 640 kB (mostly KaTeX's
  font files) — noted as a known cost, not addressed here; code-splitting
  the KaTeX-dependent components would be a Milestone 17 (Polish) concern
  if it matters by then.
- Built in parallel with the Milestone 3 addendum below (disjoint files:
  `/app` here vs `/pipeline` + `/content/questions` there), so neither
  blocked on the other.

### Milestone 3 addendum — QA question bank scale-up (done)
Follow-up to Milestone 3: scaled up item counts within the same
generate-then-independently-verify pattern (no new sourcing — everything
still comes from `pipeline/qagen/generators/*.py`, nothing external). Bank
grew from **239 → 398** verified QA items, still 0 discarded on the full
run (`python -m qagen.run` from `/pipeline`, `cat-pipeline` conda env).

- **`pipeline/qagen/syllabus_lookup.py`**: `COUNT_BY_ROI` bumped ~50%
  (`{5: 8, 4: 6, 3: 4, 2: 3, 1: 2}` → `{5: 12, 4: 9, 3: 6, 2: 5, 1: 3}`) so
  the general per-topic target rose across all 45 QA micro-topics, not just
  the flagged ones. Added `MIN_COUNT_OVERRIDE` — a floor of 10 items for the
  seven topics below, since even the bumped roiScore weight (3 or 5) wasn't
  enough to reach the difficulty-cycle's hard/very_hard tail (needs >= 8
  items; `DIFF_CYCLE` in each `generators/*.py` is
  `[easy,easy,medium,medium,medium,hard,hard,very_hard]`, length 8).
- **The 7 flagged topics** (previously 2-3 items each, no hard/very_hard):
  their generator functions in `generators/{arithmetic,algebra,geometry,
  modern,numsys}.py` were widened so a 10-item draw succeeds with 10 unique
  instances, all now have hard *and* very_hard coverage:
  - `qa.arith.tsd-races`: 3 → 10. Widened race length choices (5 → 12
    values) and speed-ratio ranges (was p∈[5,9],q∈[3,4]; now
    p∈[5,15],q∈[2,9] with q<p and gcd=1 enforced).
  - `qa.arith.time-work-chain-rule`: 3 → 10. Parameter space was already
    large; widened hours/day ranges slightly for more variety.
  - `qa.numsys.base-systems`: 2 → 10. Widened num range (50-500 →
    50-2000) and base choices (5 → 10 bases, added 3/6/9/11/12).
  - `qa.algebra.maxima-minima`: 3 → 10. Widened coefficient ranges
    (a: 1-4→1-6, b: ±12→±15, c: ±10→±12).
  - `qa.geometry.trigonometry`: 3 → 10. Widened distance choices (5 → 19
    values); angle kept restricted to {30°,45°,60°} deliberately — the only
    standard angles with exact, unambiguous tan values (adding e.g. 37°/53°
    approximations risked ambiguous/inexact answers, the one case in this
    task where "leave it, note why" would have applied — solved instead by
    widening distance, so no compromise was needed here).
  - `qa.modern.binomial-theorem`: 3 → 10. Widened power (5-9→5-12) and
    coefficient ranges (1-3→1-4).
  - `qa.modern.series-sequences-hybrids`: 2 → 10. This one *did* need new
    generation logic, not just wider ranges — the old version only ever
    produced "sum of squares" items (a single numeric parameter with 23
    possible values, too thin a pool for the topic's "hybrids" framing).
    Added a genuinely distinct sum-of-cubes variant (different closed form
    $[n(n+1)/2]^2$, different independent check — direct cube summation)
    alongside the original sum-of-squares, and widened the range parameter.
  - All 7 verified via a direct harness test (draw, dedup, verify) showing
    10/10 unique items with both `hard` and `very_hard` present in the
    difficulty mix — see commit for the test script used.
- **Fixed a live instance of the Milestone-3 "same formula on both sides"
  bug** while widening two of the flagged generators (found by inspection,
  not by a verification failure — the bug produces items that pass
  verification vacuously, so it can't be caught by trusting the "verified"
  flag, only by reading the code):
  - `gen_tsd_races`'s `answer_fn` was `round(float(length * (1 -
    Fraction(q, p))), 2)` — textually identical to the closed-form used to
    produce `claimed_value`. Replaced with a time-based simulation (float
    division/multiplication modelling "how far does B travel in the time A
    takes to finish", not the same Fraction algebra).
  - `gen_time_work_chain_rule`'s `answer_fn` was likewise the exact same
    `Fraction(p*d*h, q*h2)` formula as the claim. Replaced with a sympy
    `solve()` on the work-conservation equation `p*h*d == q*h2*D`, matching
    the pattern already used for genuine independence in
    `gen_linear_equations`/`gen_quadratic_equations`/`gen_maxima_minima`.
  - **Not fixed (flagged, out of scope for this pass):** the same
    same-formula pattern exists in several *untouched* arithmetic
    generators — `gen_tsd_relative_speed`, `gen_tsd_trains`,
    `gen_tsd_boats_streams`, `gen_tsd_circular_tracks`,
    `gen_time_work_pipes_cisterns`, `gen_time_work_efficiency_wages`,
    `gen_mixtures_alligation` all have `answer_fn` bodies that re-run the
    same formula as the claimed-value computation rather than an
    independently-derived one. They weren't touched this pass (this task
    was scoped to the 7 flagged topics + count bump, not a full generator
    audit), so their existing 239-generation items and any new items drawn
    from the raised `COUNT_BY_ROI` weight are still only self-consistency
    checked, not independence-checked. Worth a follow-up pass.
- **Orphaned files cleaned up**: because 7 generators' internal logic
  changed (not just their item count), the same `random.Random(mt)` seed
  now draws different values partway through, so some of the old
  content-hash ids from the original 239-item generation no longer
  reappear in the new output. `qagen/run.py`'s `write_items()` only
  writes/overwrites, it never deletes, so this would otherwise have left
  19 stale (but still schema-valid) orphan files on disk — one set of old
  draws per touched topic (3+3+2+3+3+3+2 = 19, confirmed by diffing the new
  output's id set against what was already committed). Manually deleted
  those 19 so `content/questions/` matches exactly what
  `python -m qagen.run` currently produces. **This is a manual step, not
  automated** — a future run that further edits a generator's internal
  logic (not just its count) will need the same check. Worth adding a
  `--clean` flag to `run.py` that removes any committed file whose id isn't
  in the freshly-generated set, done per-run rather than by hand.
- **Hand-verified samples** (per the "don't repeat the bug" rule): actually
  did the arithmetic myself for 2 items per touched generator (14 items
  total) rather than trusting the `verified` flag — race margins, chain-rule
  worker-hours, base conversions (long division by hand), vertex/minimum via
  completing the square, tan-based heights, binomial coefficients via
  $\binom{n}{k}a^{n-k}b^k$, and sum-of-cubes/-squares closed forms. All 14
  matched. (Sample stems/claims are in the commit; not reproduced here.)
- `python validate_content.py` (unchanged) passes clean on the new bank:
  `398 questions`, `86 micro-topics`, no orphan `microTopicIds`, no schema
  errors.
- Result: **239 → 398 verified QA items**, all still `source: 'generated'`,
  `verification.method: 'sympy_verified'`. All 7 previously-flagged topics
  now have hard/very_hard coverage. No topic was left un-widened for being
  "inherently too small" — all 7 had enough real parameter room once
  widened (unlike, say, a hypothetical fixed-set topic with only 3-4 sound
  variants, which didn't come up here).
- Scope discipline: did not touch `/app`, `/content/schemas`,
  `/content/syllabus.json`, or `pipeline/schemas.py`, per instructions.
  Only `content/questions/*.json` and `pipeline/qagen/**` changed.

### Milestone 2 — Storage layer (done)
- **`app/src/types/state.ts`** — the SPEC.md §5.2 learner-state types
  (`Attempt`, `MasteryState`, `PlanDay`/`PlanItem`, `MockResult`,
  `Settings`), hand-written TypeScript (not part of the pydantic/JSON-Schema
  generation pipeline — this data is never authored or validated by the
  Python content pipeline, only produced by the app itself at runtime).
  Every record type carries a `schemaVersion: 1` field per §5.2's rule
  ("every schema gets a schemaVersion field... from day one").
- **`app/src/storage/StorageAdapter.ts`** — the interface every learner-state
  write and read goes through (§1 rule 2): CRUD for attempts, mastery
  states, plan days, mock results, and a singleton settings row, plus
  `exportAll()`/`importAll()` for the full-snapshot JSON export/import and
  `clearAll()` (tests / explicit reset only, never called from normal app
  code).
- **`app/src/storage/dexie/`** — the v1 implementation:
  - `schema.ts` — `AscentDB extends Dexie`, one `version(1).stores(...)`
    call defining tables/indexes. This is deliberately a *different* kind
    of versioning from the per-record `schemaVersion` above: Dexie's
    version governs IndexedDB table/index structure; `schemaVersion`
    governs an individual record's shape and can change without touching
    Dexie's version at all.
  - `migrations.ts` — `migrateRecord()` chains per-type migration-step maps
    (keyed by source `schemaVersion`) up to `CURRENT_SCHEMA_VERSION`, and
    throws if a record's version has no registered next step rather than
    silently returning a mis-shaped record. All five maps are empty today
    (schemaVersion 1 is the only version that has ever shipped) — this is
    the migration *plumbing* required to exist "from day one" per §5.2,
    not a claim that a real migration exists yet. Exercised by a unit test
    that simulates a pre-v1 record and asserts the missing-step error.
  - `DexieAdapter.ts` — implements `StorageAdapter`; every read runs the
    record through its type's migrate function before returning it, so
    callers never see a stale-shaped record. Settings is stored under a
    fixed key (`SETTINGS_KEY = 'singleton'`), with the key stripped/added
    at the adapter boundary so the `Settings` type itself stays clean.
    `importAll()` replaces (not merges) all five tables inside one Dexie
    `rw` transaction.
- **`app/src/storage/index.ts`** — the single import site: `export const
  storage: StorageAdapter = new DexieAdapter()`. A future `SupabaseAdapter`
  (Milestone 16) swaps in here without any component changing, per SPEC.md
  §1 rule 2's explicit design goal.
- **Export/Import JSON**: the `exportAll()`/`importAll()` methods exist and
  are unit-tested (round-trip, and "import replaces rather than merges").
  SPEC.md §5.2 only requires the actual **Settings-page button** wired to
  these before Milestone 5 ("Ship an Export / Import JSON button in
  Settings before Milestone 5") — there is no Settings page yet, so that
  UI wiring is correctly out of scope for this milestone and deferred, see
  Known issues.
- **Dependencies added** (all within SPEC.md §7's existing tooling list
  except one test-only addition, see below): `dexie` (runtime, §7 already
  names "Dexie.js over IndexedDB"); `vitest` (dev, §7's CI line already
  names `vitest`); `@vitest/coverage-v8` (dev, vitest's own coverage
  provider). **`fake-indexeddb`** (dev) is the one package not named
  anywhere in SPEC.md — added because `vitest`'s Node test environment has
  no real IndexedDB, and Dexie needs one to run at all; it's a test-only
  devDependency with zero production footprint (loaded via
  `vitest.config.ts`'s `setupFiles: ['fake-indexeddb/auto']`, never
  imported from app code). Flagged here per the CLAUDE.md hard rule rather
  than asked about live, since blocking on it would have stalled the whole
  milestone for a call this narrow — revert if you'd rather this be asked
  first next time.
- **`app/src/storage/dexie/DexieAdapter.test.ts`,
  `migrations.test.ts`** — 11 tests: CRUD round-trips for all five record
  types, attempt filtering (by `microTopicId` via Dexie's multi-entry
  index, and by `mode`), plan-day date-range filtering, settings
  singleton semantics, full export→clear→import round trip, "import
  replaces rather than merges", `clearAll()`, and the migration
  missing-step error path. `npm run test` (`vitest run`).
- **CI**: added a `vitest` step to `.github/workflows/deploy.yml` between
  "Validate content" and "Build", matching SPEC.md §7's stated order
  exactly (`lint → typecheck → schema-validate-content → vitest → build →
  deploy`).
- Ran the full local sequence in CI order before pushing: lint → typecheck
  → JSON-Schema drift check → TS-types drift check → validate content →
  vitest → build. All green.

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
- SPEC.md §5.2 (Milestone 4/5, how content reaches the browser and how
  item Elo is tracked): `/content` is synced into `app/public/content` and
  fetched at runtime rather than bundled (not specified anywhere in
  SPEC.md); `MasteryState` gained `criteria123FirstMetAt`/
  `antiFrustrationTriggered` (required to implement §8.2 criterion 4 and
  the anti-frustration valve, absent from §5.2's literal interface); new
  type `ItemEloState` + a second Dexie table (needed since `Question.
  eloRating` is immutable shipped content and §8.3's live item-Elo has to
  live somewhere mutable). See the Milestone 4/5 writeups for full
  reasoning on each.
- `app/src/components/question-player/markdownSegments.ts` (Milestone 6):
  extended beyond the original "only inline `$...$` math" scope to also
  handle `**bold**` and `##`/`###` headings — re-justified in the file's
  header comment now that Lesson prose (not just terse question stems)
  exists. Still no markdown library dependency added.

## Known issues / deferred
- Milestone 2 (Storage layer) deferred until after Milestone 3 — see
  "Milestone order" above. (Now done — see Milestone 2 writeup.)
- ~~The storage layer (Milestone 2) has no consumers yet~~ **Resolved in
  Milestone 4/5**: `QuestionPlayer` calls `storage.addAttempt()` and
  `Drill.tsx`/`Settings.tsx` read from it; the Export/Import JSON button
  SPEC.md §5.2 asks for "before Milestone 5" is built (`/settings`).
- Adaptive selection's "10% interleaved from earlier mastered/decaying
  topics" band (SPEC.md §8.3) is implemented in `selectDrillQueue()` but
  fed an empty pool by `Drill.tsx` — there's no cross-topic session
  composer yet (Drill.tsx is still the single-topic harness built for
  Milestone 4). Worth revisiting once there's a real "start a session"
  flow (Milestone 6 or 9).
- `evaluateMastery()` and `recordAttemptForMastery()` recompute mastery
  from a micro-topic's *entire* attempt history on every call — no
  incremental state, no pagination. Fine at current volumes, would need a
  windowed/incremental approach if a single topic's attempt count grows
  into the thousands.
- `locked`/`available`/`decaying` (SPEC.md §8.1) are not set by anything
  yet: `locked`/`available` need prerequisite-gating UI (nothing currently
  stops you from drilling a topic with unmet prerequisites — Drill.tsx has
  no gating at all), and `decaying` needs SRS scheduling (`nextReviewAt`),
  which is explicitly Milestone 12's job, not Milestone 5's.
- Content bank is QA only (398 items as of the Milestone 3 addendum, all
  `source: 'generated'`). No official PYQ items exist in the bank at all —
  see the Tier 1 correction above. VARC, DILR, and lessons are still empty;
  DILR sets in particular need programmatically-generated underlying data
  tables per §6.3's "never let the LLM invent the numbers" rule, which this
  milestone didn't touch.
- ~~The lowest-`roiScore` QA topics (2–3 items each: `tsd-races`,
  `time-work-chain-rule`, `base-systems`, `maxima-minima`, `trigonometry`,
  `binomial-theorem`, `series-sequences-hybrids`) don't have hard/very_hard
  items~~ **Resolved in the Milestone 3 addendum above** — all 7 widened
  to 10 items each and now have hard/very_hard coverage.
- **New finding (Milestone 3 addendum):** several *untouched* arithmetic
  generators (`gen_tsd_relative_speed`, `gen_tsd_trains`,
  `gen_tsd_boats_streams`, `gen_tsd_circular_tracks`,
  `gen_time_work_pipes_cisterns`, `gen_time_work_efficiency_wages`,
  `gen_mixtures_alligation` in `pipeline/qagen/generators/arithmetic.py`)
  have the same "answer_fn re-runs the identical formula as the claim"
  pattern that caused the original percentages/profit-loss bug — their
  `answer_fn` isn't a genuinely independent derivation, just a restatement.
  They weren't touched in the addendum (out of scope: it targeted the 7
  flagged topics + a general count bump, not a full generator audit), so
  every item drawn from them — old and newly-added — is still only
  self-consistency checked, not independence-checked. No known-wrong items
  have surfaced, but this is a real gap versus SPEC.md §6.3's verification
  bar. Worth a dedicated follow-up pass through all ~45 generators to check
  for this pattern and fix it (e.g. `answer_fn` via `sympy.solve` on the
  underlying equation, as `gen_tsd_races`/`gen_time_work_chain_rule` were
  fixed to do, or a numerically-simulated approach as `gen_percentages`
  already does).
- `pipeline/review_ui/app.py` is built and smoke-tested (starts cleanly,
  serves HTTP 200, no server errors) but the project owner has not yet done
  an interactive Approve/Fix/Reject pass over the bank. Run `streamlit
  run review_ui/app.py` from `/pipeline` to do that pass; nothing in the
  bank is blocked on it, but it's the "step everyone skips" §6.2 warns
  about.
