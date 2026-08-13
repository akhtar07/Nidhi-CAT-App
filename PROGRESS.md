# Progress log

## Milestone order (revised)
Original SPEC.md §15 order is sequential (0,1,2,3,...). Revised for this build:

**0 → 1 → 3 → 2 → 4 → 5 → ...**

Milestone 2 (Storage layer / StorageAdapter / DexieAdapter) is deferred until
after Milestone 3 (Content pipeline v1). Rationale: the pipeline emits JSON
into `/content` and has no dependency on learner-state storage, so there's no
reason to block content ingestion on it. All other milestones keep their
original numbers and order from SPEC.md §15.

## Current milestone: 17 — Polish (not started)

Milestones 7 through 16 are done (see below). Milestone 7's content-bank
scale-up is a long-running background process, not a one-session task — see
its entry for current bank size and how to check/resume it. **Milestone 16
is code-complete but not live** — read its entry before assuming sync/email
work; nothing runs until a real Supabase project + Resend account exist.

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

### Professionalization pass 1 — empty states/skeletons, sectional + trend charts, question bookmarks

Direct follow-up request: "make this like a professional app... bring the idea from professional
apps like this CAT exam prep and mirror it." Narrowed via a multi-select question to three
concrete areas (visual/UX polish, score analytics, study-flow features) rather than guessing at
scope — real prep-app "professionalism" here means information density and polish, not badges or
streak gamification (SPEC.md §13 explicitly rules that out).

**Visual polish — empty states and loading skeletons.** Added `components/ui/Skeleton.tsx` (a
plain `animate-pulse` block, no new dependency) and `components/ui/EmptyState.tsx` (title +
specific description + optional action link), then swapped bare "Loading…" text for
layout-shaped skeletons across Today, Drill, Lesson, Calendar, MistakeNotebook, Review,
PassageSetPlayer, MockPlayer, Diagnostic, and MockAnalysis, and upgraded genuinely bare "no data"
messages (MistakeNotebook, Bookmarks, Progress, Today's zero-topics edge case, Drill's
zero-questions case) to explain what's missing and give one clear next action. Left a few
already-adequate states alone (Review's "no cards due" — a completion state, not a broken empty
one; Lesson's existing "practise anyway" fallback) rather than reflexively wrapping everything in
`EmptyState` for its own sake.

**Score analytics — sectional chart + a new Progress trend page.** `MockAnalysis.tsx` already
computed rich per-mock data (waterfall, bleeder report, selection quality, TITA discipline,
accuracy-vs-attempts, micro-topic damage) but rendered all of it as plain text lists. Added:
- `SectionScoreChart` in `MockAnalysis.tsx` — a horizontal bar per section (VARC/DILR/QA) showing
  marks earned, same plain-SVG/no-library discipline as PassageSetPlayer's chart renderers
  (SPEC.md §5.1). A negative section score renders in the destructive color instead of its
  section color, so a real loss is visually distinct from a small positive bar, not just implied
  by the number's sign.
- A new `/progress` route (`pages/Progress.tsx`) showing score + estimated percentile trend
  across every mock taken — the single most common "real test-prep app" dashboard feature that
  was completely missing. Backed by a new pure function, `mock/progressTrend.ts`'s
  `computeScoreTrend()` (sums `sectionScores`, reuses the existing `estimatePercentile()` — no
  new scoring logic, just aggregation across history), covered by its own vitest file. The trend
  chart is deliberately single-axis: percentile is a direct label per point, not a second y-axis
  (a dual-axis chart with two different scales is the most common chart-reading mistake).
- Linked from Today's nav and from MockAnalysis's score card ("View trend across mocks").

**Study-flow — question bookmarks, wired through the full storage stack.** A manual "come back to
this" star toggle on any question (`QuestionPlayer.tsx`, next to the difficulty/timer row, using
the already-available `lucide-react` dependency — no new package), independent of the SRS/mistake
pipeline. Threaded through every layer the existing patterns (`itemElo`, `srsCards`) established,
so nothing here is a special case:
- New `Bookmark` type (`types/state.ts`), added to `StorageAdapter`
  (`addBookmark`/`removeBookmark`/`listBookmarks`/`isBookmarked`) and `ExportBundle`.
- `storage/dexie/schema.ts` version 6 (`bookmarks: 'id, questionId, microTopicId, createdAt'`) —
  Dexie's additive versioning means existing users' IndexedDB just gains a new empty table, no
  migration of existing data needed. `migrations.ts` gained the matching
  `CURRENT_SCHEMA_VERSION.bookmark`/`migrateBookmark` plumbing (empty migration map, same as every
  other type — schemaVersion 1 is the only version that's ever shipped for anything in this app).
  `DexieAdapter` implements the four methods and includes bookmarks in `exportAll`/`importAll`/
  `clearAll`, with tests added to `DexieAdapter.test.ts` (round-trip, most-recent-first ordering,
  remove-by-questionId, full export/re-import, clearAll).
- `SupabaseSyncAdapter` gained the same enqueue-on-write wrapping every other synced type has
  (`storage/supabase/syncQueue.ts`'s `SyncTable`, `toRow.ts`'s `bookmarkToRow`), plus a new
  `supabase/migrations/0002_bookmarks.sql` table + RLS policy, inert until a real Supabase project
  exists — same as `0001_init.sql`. `removeBookmark` has one real subtlety: the bookmarks table's
  sync key is the bookmark's own `id` (matching its Postgres primary key), not `questionId`, so
  the adapter looks up which row(s) are being deleted locally *before* deleting, to enqueue the
  delete with the right key.
- New `pages/Bookmarks.tsx` (route `/bookmarks`, linked from Today's nav) lists bookmarked
  questions with topic name and date, an "Attempt" button that re-plays the question through
  `QuestionPlayer` in `review` mode (same pattern as `MistakeNotebook`'s retry flow), and a
  "Remove" button.

**Verification.** Full CI (lint, typecheck, 174 vitest tests — 4 new: 1 bookmark round-trip test,
3 for `computeScoreTrend`) green throughout. Live-verified in Chromium via Playwright: seeded a
settings row + two mock results, screenshotted the Progress trend chart (correct score/percentile
labels, correct chronological order regardless of insertion order), the MockAnalysis section chart
(negative DILR score correctly rendered in the destructive color), every new/updated empty state,
and the full bookmark round-trip live — starred a question in Drill, confirmed the star fills and
persists, confirmed it appears in `/bookmarks` with the right topic/date, clicked "Attempt" and
confirmed `QuestionPlayer` reloads the same question in review mode. Zero console/page errors
across every screen. (One process note, not a bug: mock titles in a from-scratch Playwright
session only resolve correctly when the seeded `mockId` matches a real file under
`content/mocks/` — an invented id degrades to showing the raw id, which is the intended fallback
behavior, not broken; caught during verification and the seed script fixed, not the app.)

**Deferred, explicitly out of scope for this pass:** global search across topics/lessons, an
onboarding walkthrough, and a full accessibility audit (keyboard-nav sweep, ARIA labeling pass,
Lighthouse run) — all mentioned as options when scoping this request but not selected, and (for
the accessibility audit specifically) that's Milestone 17's job, not started here. Also deferred:
extending the same empty-state/skeleton treatment to `Settings.tsx`'s small inline auth-loading
text and `MockPlayer`'s mid-session states — both low-visibility, not full-page loads, judged
lower priority than the rest of this pass.

### Aesthetic/theme fix, Calendar bug fix, and content scale-up round 3 (7 new DILR topics + chart renderers)

Three direct follow-up requests handled in sequence: a Calendar display bug report ("Review /
SRS, Tables, Tables" with no explanation), "my app is just black and white, make it look
aesthetic," then "lots of questions, tough/medium/easy, in all topics, relevant."

**Calendar bug** (`app/src/pages/Calendar.tsx`): root cause was display-only, not a data bug —
`generatePlan.ts` correctly pushes both a `learn` and a `drill` PlanItem for the same topic by
design, but the "Coming up" summary line rendered each occurrence of a topic name with no `kind`
label, so two legitimate plan items looked like an accidental duplicate. Added
`summarizeDayItems()`, which collapses same-topic entries into `"Topic (learn + drill)"`.
Reproduced the exact reported shape with seeded IndexedDB data before and after the fix. Committed
`d926185`.

**Theme** (`app/src/index.css`, `app/index.html`, `app/vite.config.ts`, PWA icons): every CSS
token in both `:root` and `.dark` was pure achromatic gray (0 chroma), and `.dark` was never
applied anywhere in the codebase — SPEC.md §13's "dark mode default, warm neutral palette, one
accent colour" had never actually been built. Replaced with a warm-neutral (hue ~55) base and one
violet accent (hue ~300, matching the existing brand mark, not a new color invented from nothing),
`class="dark"` hardcoded on `<html>`, and every text/background pairing checked against WCAG AA
via a purpose-built oklch→sRGB→contrast-ratio Python script before shipping (one real fix: the
initial dark-mode accent lightness gave only 3.00:1 button-text contrast, tuned to 4.90:1). PWA
icons and manifest/theme-color regenerated to match. Full CI green; verified live via Playwright
screenshots across Today/Lesson/Drill/Settings/Calendar. Committed `8c2e3bd`.

**Content round 3** — same zero-LLM-required discipline as round 2, plus infrastructure fixes that
unblock future LLM batches:

- **`COUNT_BY_ROI` in `pipeline/qagen/syllabus_lookup.py` was capping below SPEC.md §16's own bar.**
  Previous table `{5: 12, 4: 9, 3: 6, 2: 5, 1: 3}` meant even a roiScore-5 topic could never reach
  "≥15 questions" — no amount of re-running `run_llm.py` could ever close the gap. Raised to
  `{5: 24, 4: 20, 3: 17, 2: 15, 1: 15}` (floor of 15 everywhere, more for higher ROI); removed the
  now-redundant `MIN_COUNT_OVERRIDE` special-case dict. This alone doesn't generate anything — it's
  the target `run_llm.py --shortfall-only` reads — but the old numbers made "complete" structurally
  impossible regardless of how many generation passes ran.
- **`pipeline/qagen/llm_harness.py` observability fix**: `generate_one()`'s only log line used to
  print after a full attempt (up to 1 draft + 1 audit + 5 self-consistency calls) returned, so a
  legitimately slow attempt under load was indistinguishable from a hang for up to ~35 minutes (see
  round 2's stuck-batch diagnosis). Added a print at every stage transition (draft/verify/audit/each
  self-consistency sample), each `flush=True`. Root cause of the hang itself is still unfixed — this
  only makes a live run's progress visible.
- **QA/VARC LLM generation deliberately deferred, not run, this round** — the project owner's GPU
  was in active use by another process when this work started (confirmed via `nvidia-smi`-adjacent
  `ps aux`: a separate `vllm serve Qwen3-8B` process already running). `qagen.run_llm
  --shortfall-only` has a ~649-item queue ready to go across all 45 QA topics once the GPU is free
  (VARC's RC/VA topics need `rc_harness.py`/LLM generation too, not started). This is the single
  largest remaining content gap — see "Known issues" below.
- **7 new DILR generators, all zero-LLM, all independently re-verified with a second, differently-
  written script before committing** (not the generator's own internal checks):
  - `build_dilr_di_line_charts.py` (`dilr.di.line-charts`, roi=4) and
    `build_dilr_di_pie_charts.py` (`dilr.di.pie-charts`, roi=4) — needed new frontend renderers
    first (see below); questions computed directly from the same data dict the chart displays.
  - `build_dilr_di_stacked_charts.py` (`dilr.di.stacked-charts`, roi=3) — same pattern, needed a
    new `StackedBarChartAsset` renderer.
  - `build_dilr_lr_selection_conditionalities.py` (`dilr.lr.selection-conditionalities`, roi=4) —
    "pick a team of 3 from 6 subject to 3 conditional rules" puzzle; valid teams computed by
    brute-forcing all C(6,3)=20 combinations against the rules, re-verified with a second,
    separately-written rule-check pass.
  - `build_dilr_lr_venn_set.py` (`dilr.lr.venn-set`, roi=3) — 3-set survey/Venn puzzle; the 8
    ground-truth disjoint regions are picked first, every aggregate the learner is given (|A|,
    pairwise overlaps, etc.) is *derived* via inclusion-exclusion, then independently re-verified
    by a genuinely different method: an explicit synthetic-student-ID simulation using real Python
    set operations, not the inclusion-exclusion formulas used to build the stem.
  - `build_dilr_lr_ordering_ranking.py` (`dilr.lr.ordering-ranking`, roi=3) — linear ranking puzzle
    (6 students, ranks 1-6), same generate-clues-until-unique brute force as the circular-
    arrangement/distribution-grouping generators, over all 6!=720 permutations; independently
    re-verified per-set with a fresh regex clue parser + separate brute force.
  - `build_dilr_di_data_sufficiency.py` (`dilr.di.data-sufficiency`, roi=3) — standard 5-option
    CAT DS format (A/B/C/D/E). No PassageSet needed (`validate_content.py` doesn't require DILR
    questions to belong to one; they load by `microTopicId` like any other question). Every
    sufficient/not-sufficient verdict is derived by actually solving the system (`sympy.solve` for
    the algebraic cases, bounded exhaustive enumeration for the parity case) and asserted against
    the fixed-option answer before writing, not hand-labeled.
- **Frontend: `LineChartAsset`, `PieChartAsset`, `StackedBarChartAsset` added to
  `PassageSetPlayer.tsx`** (`app/src/pages/PassageSetPlayer.tsx`) — previously only `chartKind:
  'bar'` had a renderer; `line-charts`/`pie-charts`/`stacked-charts` questions would have shipped
  with "[chart rendering not yet implemented for this chart type]" instead of the actual chart.
  Same "render from data, not images" plain-SVG approach as the existing `BarChartAsset` (SPEC.md
  §5.1). **One real bug caught in Playwright screenshot review, not by CI**: the pie chart's legend
  showed "40% (40%)" — a duplicated percentage — because the generator's slice values are already
  percentages but the renderer unconditionally appended a second, recomputed `(x%)`. Fixed by
  skipping the recomputed percentage when `unit === '%'`.
- Full CI (lint, typecheck, 170 vitest tests, build) green after every change. Content re-synced
  via `sync-content.mjs`, `validate_content.py` clean (86 micro-topics, 13 lessons, 544 question
  files including `mockReserved` items).

**Honest re-audit, same script as every round** (excludes `mockReserved` items, matches SPEC.md
§16's literal bar): zero-question topics **30 → 23** (QA 2, DILR 16→9, VARC still 12, untouched
this round — no LLM/RC pipeline run needed for the DILR wins, but VARC's remaining 12 need either
LLM generation or real source text, same as QA). **0 of 86 micro-topics still meet the full ≥15-
questions-+-lesson bar** — every DILR topic this round has exactly 4 questions (or 8-12 for the
brute-force multi-set generators), nowhere near 15. This round closed structural gaps (impossible
target numbers, missing chart renderers, unreliable LLM observability) more than it closed the
raw content gap — recorded here as the same kind of honest checkpoint as round 2, not a finish
line.

### Content scale-up, round 2 — teaching-first routing, more DILR, a stuck-batch diagnosis

Direct follow-up requests: "complete the full syllabus... zero tolerance... don't fabricate,"
then "teach like a kid before every question." Honest framing up front, re-audited with the same
script each time, not just asserted: **still 0 of 86 micro-topics meet SPEC.md §16's real bar
(≥15 questions + a lesson).** Progress this round: lessons 6→13, DILR topics-with-any-content
5→8 of 24, zero-question topics 33→30. This is nowhere near "complete" — recorded here as an
honest checkpoint, not a finish line.

**Teaching-first routing (structural, not content)**: `Today.tsx` and `MockAnalysis.tsx`
previously linked straight to `/drill/:id` for any topic without a lesson, skipping teaching
entirely for the 80+ topics that had none. Every entry point now routes through `/lesson/:id`
first — `Lesson.tsx` already had a graceful "No lesson yet — Practise anyway" fallback, so this
makes the gate universal with no dead ends. Mistake-review flows (`MistakeNotebook`, `Review`)
are untouched — re-attempting an already-seen missed question is a different, legitimate flow.

**3 more DILR generators**, same code-verified, no-LLM discipline as round 1:
- `build_dilr_lr_games_tournaments.py` (`dilr.lr.games-tournaments`, roi=5): simulates a
  round-robin tournament (seeded RNG per match, no draws), retries the seed until standings have
  a unique top/bottom team, derives every question from the real computed standings.
- `build_dilr_lr_distribution_grouping.py` (`dilr.lr.distribution-grouping`, roi=5): a
  matching-grid puzzle (4 people × pet × job, two linked permutations), same
  generate-clues-until-unique brute-force pattern as the circular-arrangement generator, over all
  4!×4!=576 combined possibilities. **Verified with a genuinely independent second script** — not
  the generator's own logic — that re-parses each set's raw English clues with a fresh regex
  parser and re-runs its own from-scratch brute-force search; confirmed exactly one solution for
  all 3 generated sets and cross-checked all 12 questions against it.
- `build_dilr_di_caselets.py` (`dilr.di.caselets`, roi=5): DI data embedded in narrative prose
  instead of a table/chart (headcount/salary and factory-production/defect-rate scenarios) — the
  tested skill is extraction as much as computation. Independently re-verified against the
  generated JSON with fresh computation before committing.

**7 more lessons** (`pipeline/build_lessons_batch3.py`), deliberately spread across all three
sections since round 1 was QA-only and DILR/VARC had zero lessons each: permutations-
combinations, progressions, divisibility-factors (QA); arrangements, tables (DILR); para-jumbles,
main-idea (VARC). Written in a warmer, "explain it simply before the formula" tone per direct
instruction.

**3 more real bugs found and fixed**, via live re-verification across *all* 13 lessons (not just
new ones) — the same rigor that's caught something every single lesson-writing pass this session:
1. A markdown pipe-table in the divisibility-rules lesson rendered as literal `|`/`---` text —
   the hand-rolled tokenizer never supported table syntax. Fixed by converting to a bullet list
   (a content fix, not a renderer feature addition — a list conveys the same information).
2. 9 instances of single-asterisk `*italic*` markdown (also unsupported by the tokenizer,
   renders as literal asterisks) across both new lessons and two already-shipped ones from round
   1. Found via a systematic grep distinguishing real content bugs from arithmetic-verification
   code comments (which don't ship). Fixed by converting all 9 to `**bold**`.
3. A constructed para-jumble teaching example had a genuine order ambiguity (two sentences could
   plausibly both open the paragraph) — caught on review, not by any tool. Fixed by adding
   explicit connector words ("As a result," "Indeed,") so each link is forced, not just
   topically plausible.

**The QA generation batch genuinely hung — diagnosed, not just retried.** Left running in the
background, it produced zero output for 37 minutes on `qa.arith.si-ci-instalments`. Killed it,
confirmed Ollama itself responds normally within 2.5s the instant the batch process is gone
(ruling out a general server problem), restarted as a smaller 3-topic canary — it hung on the
*same* topic again, reproducibly, with real (non-zero) CPU usage throughout, not a classic
deadlock. Working theory: Ollama is in the degraded 77%/23% GPU/CPU split mode documented back in
Milestone 7 (context not fitting fully on GPU); in that mode a single generation can run for a
very long time if the model falls into a verbose/repetitive completion that never hits a stop
token, and because Ollama streams tokens, the HTTP client's 300s read-timeout keeps resetting on
each trickling token and never fires even though the call is effectively stuck. **Not yet fixed**
— paused the LLM-dependent QA path rather than keep burning shared GPU time on blind retries, and
put full effort into deterministic (no-LLM) DILR generation instead, which has been reliable and
fully independently verifiable all session. Next step if revisited: bound `max_tokens` on the
draft call more tightly, or replace the `requests` timeout with a true wall-clock deadline that
doesn't reset on partial data.

### Content scale-up, round 1 (ad hoc, requested directly — "more questions for practice, more for teaching")

Not tied to a specific SPEC.md milestone number — a direct content request after Milestone 16.
Targeted the two most glaring gaps a coverage audit turned up:

**DILR was almost entirely empty**: 22 of 24 DILR micro-topics had zero questions (only the two
Milestone 8/13 demo sets existed). Built 3 new deterministic, code-verified generators for the
highest-ROI (roi=5) empty topics — same SPEC.md §6.3 DILR-inversion discipline as every prior
DILR script (data/solution generated first, questions derived, answer verified in code, no LLM):

- **`pipeline/build_dilr_lr_arrangement.py`** (`dilr.lr.arrangements`, 3 sets × 4 questions): a
  genuine logic-puzzle generator, not just a data table. Generates a random circular seating,
  then adds candidate clues one at a time, brute-forcing all 120 permutations after each addition
  until **exactly one** circular arrangement (up to rotation) satisfies every clue so far —
  the actual uniqueness guarantee a real LR puzzle needs, not just "clues that happen to be
  true." **Caught and fixed a real bug during its own verification**: the first generated set's
  "X sits immediately clockwise of Y" clue sentences had the relationship backwards from what
  the code actually verified (a self-consistent-but-wrong bug — the uniqueness check used the
  correct direction internally, but the English sentence printed the reverse) — caught by
  independently re-deriving each clue's truth against the stated solution with a fresh parser,
  not by trusting the generator's own internal checks. Fixed and every regenerated set
  re-verified the same independent way.
- **`pipeline/build_dilr_growth_cagr.py`** (`dilr.di.growth-cagr`, 1 set × 4 questions): two
  companies' revenue over 5 years, YoY-growth and CAGR questions. Every answer hand-recomputed
  independently (not just re-running the generator's own asserts) and matched exactly.
- **`pipeline/build_dilr_missing_data.py`** (`dilr.di.missing-data`, 1 set × 4 questions): a
  table with some cells blanked, placed so each blank is alone in its row and column (like
  non-attacking rooks) — guaranteeing each is recoverable from either its row or column total
  alone, and the script asserts both recoveries agree. Independently reconstructed by hand from
  the raw table JSON and cross-checked against both row and column totals.

All three chart/table/LR renderings verified live via Playwright — `PassageSetPlayer` already
supported `lr_set`/`di_set`/table/bar-chart, so no UI changes were needed.

**Teaching content (lessons)**: only `qa.arith.percentages` had a lesson (Milestone 6's "one
topic end to end" scope). Added 5 more for the next-highest-ROI QA topics that already have a
healthy question bank (`profit-loss-discount`, `averages-weighted-averages`, `hcf-lcm`,
`time-work-pipes-cisterns`, `ratio-proportion-variation`) — same authored-and-hand-verified
discipline as the Percentages lesson: every worked example's arithmetic independently
recomputed via Python before being written (not generated and trusted), each with a formula
card and common-traps list. **One real bug caught in live verification, not by the generator's
own code**: two worked examples wrote `Profit\%`/`loss\%` in plain connector text between two
`$...$` math spans rather than inside one — the exact same "\% outside a math span renders
literally" bug class Milestone 7's Percentages lesson caught, in new content. Fixed by wrapping
both in their own `$\text{...}\%$` span; re-verified via Playwright that no lesson page shows a
literal `\%` and every KaTeX element renders (12-37 per lesson).

**Also hit the same stale-long-lived-dev-server artifact from Milestone 15 again** (a valid,
freshly-synced content file served as the SPA HTML fallback) — recognized immediately from the
error signature, fixed the same way (restart `npm run dev`), didn't waste time re-diagnosing it
as a content bug this time.

**QA practice-question top-up**: a coverage audit also found Milestone 14's mock composition had
an unintended side effect — spreading picks across "as many distinct micro-topics as possible"
fully drained several already-thin topics (e.g. `qa.modern.series-sequences-hybrids`: all 10
items became `mockReserved`, leaving zero drillable). Started a background batch
(`qagen.run_llm --topics <24 thinnest QA topics> --per-topic 12`) targeting exactly the topics at
≤5 unreserved questions. Long-running (LLM-bound, same one-request-at-a-time Ollama constraint
documented in Milestone 7) — **still running as of this write-up**, not yet reflected in the
question count below or committed; check `ps aux | grep run_llm` / the batch's log to resume
monitoring, same as every other background-batch note in this file.

Result so far: **+20 DILR questions across 3 previously-empty topics, +5 lessons (6 total)**,
content validator green throughout (485 questions, 6 lessons), full app CI still green
(typecheck/170 tests — no app code changed this round, only `/content` and `/pipeline`).

### Milestone 16 — Supabase sync + email (code-complete, not live)

**Read this before touching anything sync/email-related: every line of code below is real,
typechecked, and unit-tested, but nothing actually runs.** No live Supabase project or Resend
account exists — there was no way to create either from this session (needs real external
accounts), and CLAUDE.md/SPEC.md both forbid inventing or hardcoding credentials. The user
explicitly chose "build the code, defer live setup" over pausing or skipping to Milestone 17.

**`SupabaseSyncAdapter`** (`app/src/storage/supabase/`), the `SupabaseAdapter` SPEC.md §1 rule 2
predicted from Milestone 2 ("added later without touching any component"): wraps `DexieAdapter`,
not a replacement for it — every read and every synchronous write still goes straight through
Dexie/IndexedDB, which stays the actual source of truth (CLAUDE.md: "IndexedDB is v1"). Every
mutating call additionally records the write into a new Dexie `syncQueue` outbox table
(`schema.ts` version 5), and `flushQueue()` best-effort pushes that outbox to Supabase —
de-duplicating superseded writes to the same row first, leaving the whole queue untouched on any
failure so the next attempt retries in order. This is what makes SPEC.md §16's "Airplane mode:
full drill session works, syncs on reconnect" true by construction rather than by careful
sequencing: a write can never block on network, and syncing is a separate, retriable, best-effort
step layered on top. `mockSession` is deliberately excluded from sync — SPEC.md's crash-recovery
requirement is local-only, and cross-device mid-mock resumption was never asked for.
`storage/index.ts` now constructs `SupabaseSyncAdapter` unconditionally (no env-based branching
needed) — with no Supabase project configured, `flushQueue()` is a verified no-op and the app is
byte-for-byte the same experience as plain `DexieAdapter`. **7 new unit tests** covering: writes
land in Dexie regardless of configuration; flush no-ops when unconfigured or signed-out; a
successful flush drains the queue and sends the right rows; repeated writes to the same row
de-duplicate to one upsert; a Supabase error leaves the queue intact for retry; reads never touch
Supabase at all.

**Magic-link auth** (`app/src/auth/useSupabaseAuth.ts`, wired into Settings' new "Sync across
devices" section): `signInWithOtp`/`onAuthStateChange`/`signOut` via `@supabase/supabase-js`
(added to SPEC.md §7's approved stack — Supabase is named explicitly there). Single-user app, so
this is purely the cross-device *sync* login SPEC.md §12 option B describes, not a product
signup flow (SPEC.md §0 is explicit there is no such thing here).

**`app/src/lib/supabaseClient.ts`**: reads `VITE_SUPABASE_URL`/`VITE_SUPABASE_ANON_KEY`
(`app/.env.example` documents both, real values go in a gitignored `.env.local`), returns `null`
when either is missing — every consumer (`SupabaseSyncAdapter`, `useSupabaseAuth`) already
handles a null client as "sync feature inert," so an unconfigured build needs no special-casing
anywhere else. **This is not a CLAUDE.md "no API keys in client code" violation**: Supabase's
anon key is the one credential explicitly designed to ship in a browser bundle — access control
is entirely Row Level Security (below), not secrecy of this key. The one genuinely secret key
(service-role, which bypasses RLS) never appears in `/app` at all — only inside the Edge
Function, which runs on Supabase's servers.

**`supabase/migrations/0001_init.sql`**: one table per synced learner-state type (`attempts`,
`mastery_states`, `plan_days`, `mock_results`, `item_elo`, `settings`, `srs_cards`), each
`primary key (user_id, <natural key>)`, RLS enabled with an `auth.uid() = user_id` policy on
every table — the anon key can only ever touch its own signed-in user's rows. Plus `email_log`
(`primary key (user_id, sent_date)`) enforcing SPEC.md §11's "never more than one email per day"
**at the database level**, not just in application logic — a duplicated cron trigger can't
double-send even if the Edge Function's own pre-check somehow raced. Column names are hand-kept
in lockstep with `app/src/storage/supabase/toRow.ts`'s camelCase→snake_case mapping; there's no
generation pipeline tying the two together the way `/content`'s schemas.py↔content.ts link is
automated, since this is a one-way, Postgres-specific mapping with nothing to validate against
in CI (no live database to check it against). Apply via `supabase db push` or the SQL editor,
once a project exists.

**Edge Function** (`supabase/functions/daily-nudge/index.ts`, Deno, deployed separately via the
Supabase CLI — not part of the Vite build or CI): reads every `email_opt_in` user's synced
settings/plan/mastery rows, picks at most one email via `selectEmailForToday` (priority:
topic-complete > exam-milestone > mock-reminder > Sunday digest > daily nudge), sends through
Resend, logs to `email_log`. Gated by an `x-cron-secret` header check, not Supabase auth (this
is a server-to-server call from GitHub Actions, not a user action). **Two things scoped out,
flagged honestly rather than faked**: topic-complete/mock-reminder/weekly-digest detection needs
queries this pass didn't wire up (a mastery-history lookback, tomorrow's plan read, and a week of
aggregated attempts respectively) — the `selectEmailForToday` function and its templates fully
support all five email types and are tested for all of them, but `index.ts` currently only ever
populates `todayPlanFirstItem`, so only the daily nudge and (once the exam date is real) the
milestone emails will actually fire until those three queries are added.

**Email templates** (`supabase/functions/_shared/{emailTemplates,selectEmail}.js`) — deliberately
plain, dependency-free ESM **JavaScript**, not TypeScript: this is the one file both the Deno
Edge Function and this Vite/vitest project import unmodified, and keeping it framework-free
sidesteps needing a shared build step between two unrelated runtimes. `app/tsconfig.app.json`
gained `allowJs: true` and an extra `include` entry pointing at this directory so `tsc -b` can
still typecheck the app-side test that imports it. **14 new unit tests**
(`app/src/email/emailTemplates.test.ts`) cover all 5 template types (including the exact SPEC.md
§11 daily-email example shape, HTML-escaping of user-controlled topic names, and non-empty
distinct copy for all 6 milestone days) plus every priority ordering in `selectEmailForToday`.

**GitHub Actions cron** (`.github/workflows/daily-nudge-cron.yml`): SPEC.md §11's exact
expression (`0 3 * * *` UTC = 08:30 IST), gated on two repo secrets
(`SUPABASE_FUNCTION_URL`/`CRON_SECRET`) that don't exist yet — the job fails loudly with a clear
message if they're missing, rather than silently no-op'ing (a missing secret should never look
like "ran fine, nothing to send").

**Full local CI green** throughout (lint/typecheck/170 tests, up from 149/build) — every file
above that CAN be exercised without a live backend was exercised: the sync queue's offline/retry/
dedup behaviour (mocked Supabase client), and every email template + selection rule, both via
real automated tests, not just written-and-hoped.

**Setup steps for when a real Supabase project exists** (not done in this session — needs
accounts this environment can't create):
1. Create the Supabase project; run `supabase/migrations/0001_init.sql` against it (SQL editor
   or `supabase db push`).
2. `app/.env.local` (gitignored): `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY` from the
   project's API settings.
3. `supabase secrets set RESEND_API_KEY=... SUPABASE_SERVICE_ROLE_KEY=... CRON_SECRET=<any random string>`,
   then `supabase functions deploy daily-nudge`.
4. A verified sending domain in Resend; update the `from:` address in `index.ts` (currently a
   placeholder `ascent@resend.dev`).
5. GitHub repo secrets: `SUPABASE_FUNCTION_URL` (the deployed function's URL) and `CRON_SECRET`
   (must match step 3's value).
6. Rebuild/redeploy the app (`VITE_SUPABASE_URL`/`VITE_SUPABASE_ANON_KEY` must also be available
   to the GitHub Pages build — add them as repo secrets and reference them in `deploy.yml`'s
   build step, which doesn't happen automatically).

Run locally (everything except live sync): `cd app && npm run test -- --run` exercises the sync
queue and email logic without any of the above.

### Milestone 15 — PWA + notifications (done)

SPEC.md §7/§11/§12/§16: `vite-plugin-pwa` (Workbox), named explicitly in SPEC.md §7, wired with
the `injectManifest` strategy (not the default `generateSW`) since the service worker needs
real custom logic beyond precaching — `app/src/sw.ts`:

- **App shell precache** via `precacheAndRoute(self.__WB_MANIFEST)` + `cleanupOutdatedCaches()`.
- **`CONTENT_VERSION`-scoped runtime cache** for `/content/**` (`StaleWhileRevalidate`, cache
  name `ascent-content-${CONTENT_VERSION}`), with an `activate` handler that deletes any
  `ascent-content-*` bucket not matching the current version — SPEC.md §12's exact ask ("on
  version bump the service worker must invalidate cached content but must never wipe learner
  data. Test this explicitly.").
- **Message-based local notification** (`SHOW_NOTIFICATION`) and `notificationclick` handling —
  SPEC.md §11 Phase 1's "Web Push via service worker for the daily nudge — works offline, no
  backend needed for local notifications scheduled by the SW." Honestly scoped: this is the
  page asking its own active SW to show a notification while open, not true background push
  (which needs a push subscription + a server to trigger it — Phase 2/Supabase, Milestone 16).
  Documented in `app/src/pwa/notify.ts`'s own header comment so this isn't mistaken for more
  than it is later.

**`CONTENT_VERSION` bump — tested explicitly, live, per SPEC.md §12's instruction, not just
asserted:** seeded a real `Attempt` into IndexedDB and warmed the `ascent-content-v1` cache,
bumped the constant to `v2` and rebuilt, forced a service-worker update check, and clicked the
app's own "Refresh" banner (see below). Confirmed directly via `caches.keys()`: `ascent-content-
v1` was gone and `ascent-content-v2` existed after the swap, while the seeded attempt was still
present in IndexedDB, byte-for-byte — the version bump invalidated content and left learner data
completely untouched, exactly as required.

**Install prompt** (`app/src/pwa/useInstallPrompt.ts`, wired into Settings): captures
`beforeinstallprompt` (Chrome/Android-family only — Safari/iOS has no programmatic prompt and
relies on Share → Add to Home Screen, noted in the UI text rather than presented as broken).
New PNG icons (`app/public/icons/icon-{192,512,maskable-512}.png`) generated from the existing
brand mark in `favicon.svg` — rendered via a headless-Chromium screenshot rather than a new
image-processing dependency, since no SVG rasterizer (`rsvg-convert`/`cairosvg`/`sharp`) was
available in this environment and Playwright was already at hand.

**Update banner** (`app/src/pwa/pwaUpdate.ts` + `UpdateBanner.tsx`): `registerType: 'prompt'`,
deliberately not `'autoUpdate'` — SPEC.md §12 warns an update must never silently disrupt a
session (imagine it firing mid-mock), so a new service worker only activates when the user
clicks "Refresh" in a small persistent banner. Implemented as a tiny `useSyncExternalStore`
store rather than pulling in a state library — SPEC.md §7 names Zustand but nothing in this
codebase has needed it yet, and one banner's worth of state didn't justify adding the first
usage here.

**Daily nudge in `Today.tsx`**: new `Settings.notificationsEnabled`/`lastNudgeShownDate` fields
(additive/optional, same pattern as every prior schema addition this build). SPEC.md §11: "the
in-app 'Today' card is the primary mechanism" — the local notification is a same-session
supplement, fires at most once per **Asia/Kolkata** calendar day (not UTC), naming the first
unfinished plan item.

**Real bug fixed in the course of this, not a new one introduced:** SPEC.md §7 says "pin
everything to Asia/Kolkata for day boundaries... or her streak will break at 5:30 AM" — the new
nudge de-dupe logic needed a genuinely-correct IST day boundary, so `dateUtils.ts` gained
`todayIsoIST()` (`Intl.DateTimeFormat` with `timeZone: 'Asia/Kolkata'`, no new dependency),
unit-tested against the exact 5:30 AM UTC/IST-boundary case SPEC.md names by name. `Today.tsx`'s
own `todayPlan` lookup was also switched from the old UTC `toISOString().slice(0,10)` to this —
directly adjacent code in the same file, otherwise the nudge and the plan-day lookup would've
disagreed about what day it is. **Not fixed, flagged instead:** `Diagnostic.tsx`, `Calendar.tsx`
(3 call sites), and `MockAnalysis.tsx`'s "tomorrow" calculation still use UTC slicing — a
pre-existing gap from Milestones 9/11, out of this milestone's scope to sweep, worth a dedicated
pass since it's the exact named failure mode.

**Verified live** (Playwright against `vite preview`'s production build, not just `vite dev`,
since Workbox's generated SW behaves differently in dev mode):
- Manifest fetches correctly with all 3 icon entries; SW registers, `scope`/`activeScriptURL`
  correct.
- **Full offline drill session** (SPEC.md §16: "Airplane mode: full drill session works"):
  warmed caches online, `context.set_offline(True)`, reloaded the same drill URL — real question
  content rendered from cache — answered all 10 questions (skip → reveal → error-tag → next,
  cycling correctly), reached "Drill complete," and confirmed 10 real `Attempt` rows written to
  IndexedDB, entirely offline. Zero console errors.
- Settings' install/notification sections render correctly; toggling the notification checkbox
  persists `notificationsEnabled: true` and requesting permission resolves.
- **One thing this environment could not verify**: actually seeing the notification appear
  on-screen. `Notification.requestPermission()` resolves `'granted'` under Playwright's
  `permissions: ["notifications"]` context grant, but the deeper permission
  `ServiceWorkerRegistration.showNotification()` checks doesn't get elevated by that same grant
  in headless Chromium (`showNotification` throws "No notification permission has been granted
  for this origin" even though `Notification.permission` reports `'granted'`) — a known
  headless-browser limitation, not a code defect: the request→permission→toggle→SW-message
  plumbing was verified error-free end to end, but the actual on-screen result needs a real
  browser/device, same class of gap as SPEC.md §17's "real-device testing on her phone model,"
  which this session was never going to be able to do either.

Run locally: `cd app && npm run build && npm run preview`, visit the printed URL, install from
the browser's address-bar icon or Settings → Install app. `npm run dev` also runs the service
worker in dev mode (`devOptions.enabled: true`) for quick iteration.

### Milestone 14 — 5 full + 5 sectional mocks (done, content-scoped)

SPEC.md §9.1/§9.2. `pipeline/compose_mocks_m14.py` extends Milestone 10's
`compose_mock_1.py` pattern (never invents a question, only selects
already-verified ids and flags them `mockReserved`) into the full set:
mock-1 (Milestone 10, already `difficultyTier: easier`) plus mock-2..mock-5
(full) and `sectional-qa-1`..`sectional-qa-5` (sectional), 10 mocks total,
220 QA questions reserved with **zero id overlap** across any of them
(checked directly, not assumed).

- **Difficulty escalation, §9.1's exact wording** ("Mock 1 slightly easier
  than CAT, Mocks 2-4 at CAT level, Mock 5 harder"): implemented as a fixed
  `{easy, medium, hard, very_hard}` count mix per tier (10/9/3/0 easier,
  6/9/5/2 standard, 3/7/8/4 harder — always summing to 22), not just an
  itemElo filter, which would have made a "harder" mock topic-thin given
  how few very_hard items exist per topic. Applied to both full and
  sectional mocks for consistency, even though §9.1 only mandates it for
  full mocks — there was no reason to leave sectionals ungraded once the
  content was there to support it.
- **Selection still spreads across micro-topics** within each difficulty
  bucket (same shuffle-and-round-robin logic `compose_mock_1.py`
  introduced), popped from a shared pool across all 10 compositions in one
  script run so two mocks can never draw the same question.
- **Content-scoped, not content-complete — same call as mock-1 and every
  prior milestone's honest framing.** VARC has 7 questions (need 24/mock)
  and DILR has 2 sets (need ~5/mock); every mock here is QA-only, same as
  mock-1, with an explicit `composedNote` rather than a silently-empty or
  padded section. §9.2's own wording anticipates this exact shortfall
  ("ship 5 × VARC / 5 × DILR / 5 × QA sectional **if the bank allows; 5
  total if not**") — 5 QA sectionals is that documented fallback, not a
  shortfall against spec.
- **`Today.tsx` mock list upgraded** from bare ids to title + kind ("Full
  mock"/"Sectional") + a difficulty label ("Easier"/"CAT level"/"Harder") —
  fetches every `MockDefinition` (10 small files, cheap) rather than just
  the id index, since a milestone about difficulty grading needs the
  grading to actually be visible somewhere, not just present in the JSON.

**One real bug caught by live Playwright testing, not by CI** (typecheck/
lint/tests/build were all green throughout): after composing the new
mocks and re-syncing content, `MockPlayer` failed to load `mock-5` and
`sectional-qa-1` with `Unexpected token '<'... is not valid JSON` — one
specific question file (`qa.arith.tsd-relative-speed.gen-aae6b60d06.json`,
confirmed present on disk, valid JSON, checksum-matched between `/content`
and the synced `/app/public/content` copy) was being served as the SPA's
`index.html` fallback (200, `text/html`) instead of its real JSON, only
through the dev server that had been running continuously since early in
this session across many `rm -rf` + recursive-`cp` content syncs. A full
dev-server restart (not a content or app-code fix) resolved it immediately
and the same URL served correctly afterward — a long-lived Vite dev
session's static-file layer going stale under repeated bulk directory
replacement, not a bug in anything committed. Documented here since it's
exactly the kind of thing that looks like a content bug at first glance;
if this recurs, restart `npm run dev` before suspecting the content pipeline.

Verified live end to end: `Today.tsx`'s Mocks section lists all 10 with
correct titles/kind/difficulty labels; `mock-5` (harder) and
`sectional-qa-1` (easier) both load their intro screens with the correct
section (QA, 40 min, 22 questions), the correct `composedNote` text, and
the hard-lock/no-back-navigation copy — zero console errors. Full mock
attempt-to-completion (sitting through a real 40-minute section) wasn't
re-exercised here since Milestone 10 already proved the section-timer/
palette/crash-recovery/scoring mechanics live on `mock-1` with the same
`MockPlayer` component — this milestone only changed *which* questions get
composed into *which* mock ids, not the player itself.

Run locally: `cd pipeline && conda run -n cat-pipeline python
compose_mocks_m14.py`, then `cd app && npm run dev`, visit `/#/` to see
all 10 mocks listed, or `/#/mock/mock-5` / `/#/mock/sectional-qa-1`
directly.

### Milestone 13 — Content pipeline v3 (done, content-scoped)

SPEC.md §6.1 Tier 2's discipline ("RC passages must be real open-licence
text — Gutenberg/Wikisource/arXiv/gov reports/Wikipedia CC BY-SA — never
LLM-generated; only the questions are synthesised on top of real prose")
extended from QA (Milestone 7) into RC, DILR-sets, and VA — the three
content types Milestone 7's write-up explicitly deferred to this milestone.

**RC pipeline** (`pipeline/qagen/rc_harness.py` + `pipeline/build_rc_passage_1.py`):
- Source text: a 511-word excerpt of W. L. Courtney's 1901 introduction to
  Mill's *On Liberty*, Project Gutenberg #34901 — definitively public
  domain (Mill d. 1873, Courtney's intro published 1901). Fetched via the
  Gutendex API, hand-word-counted to land on clean sentence boundaries.
- **Two-part verification gate per SPEC.md §6.3**, both real, both fired
  during the actual run (not formalities):
  1. `span_exists_verbatim()` — the model's claimed `justifying_span` must
     be a whitespace-normalized *exact* substring of the passage. Caught a
     real rejection live: the model paraphrased `', but in 1851 her husband
     died, and then Mill made her his wife.'` instead of quoting it, and
     the item was discarded.
  2. `answerability_check()` — 5 independent chat calls given only
     passage+stem+options (never the claimed answer); requires ≥4/5
     agreement *and* that the majority answer matches the claimed
     `correct_key`. An ambiguous or wrong-keyed question fails silently
     otherwise; this is what would catch it.
  - Rejected items are discarded, never repaired, same rule as Milestone
    7's QA harness.
- Result: `varc.rc.on-liberty-intro.set-01`, 4 questions (main_idea, detail,
  inference, tone types), `licence: "Public domain (Project Gutenberg
  #34901)"`. Manually read all 4 post-generation, not just trusted the
  gate — genuinely well-formed CAT-style RC questions.

**DILR bar-chart set** (`pipeline/build_dilr_barchart_demo.py`): second DILR
set, proving SPEC.md §6.3's DILR inversion (data generated programmatically
first, questions derived deterministically, no LLM involved at all)
generalises beyond Milestone 8's table format to a chart. Original
synthetic two-product/four-month unit-sales data; every question's answer
computed by a `_totals()`/`_month_with_highest_combined()`/etc. helper and
`assert`-checked against hand-computed values before being written —
e.g. `assert totals == {"A": 540, "B": 430}`. `licence: CC0-1.0` (original
data, nothing to attribute).

**New chart rendering** (`app/src/pages/PassageSetPlayer.tsx`): closes the
gap Milestone 8's write-up explicitly flagged ("chart rendering not yet
implemented for this asset type"). `BarChartAsset` — plain SVG grouped bar
chart driven from the asset's `{categories, series, unit}` spec data, no
charting library, per SPEC.md §5.1 ("render charts from data, not images").
`SetAsset` dispatches on `asset.type`/`spec.chartKind`; only `bar` is wired
so far — pie/line/stacked/radar/bubble chart kinds still fall through to
the existing "not yet implemented" placeholder text, honestly, rather than
silently mis-rendering. Verified live: 8 `<rect>`s rendered (4 months × 2
products) with correct per-bar values, legend, and unit label.

**VA para-jumbles** (`pipeline/build_va_parajumbles.py`): a third pattern,
cheaper than either RC or QA — real prose (3 clusters of 4-5 consecutive
sentences, verbatim, same Gutenberg #34901 source, different excerpts than
the RC passage) is shuffled with a seeded RNG, and the "correct answer" is
simply the sentences' true original order, computed and *asserted* in code
(`reconstructed == original_order`) rather than typed by hand — so there is
nothing for an LLM to get wrong or need verifying, sidestepping RC/QA's
verification cost entirely for this question type. 3 questions written
(`varc.va.para-jumbles.authored-*`), answers `BDCEA`/`BADC`/`BCAD`,
`format: tita`, `source: authored`.

**Verified live end to end** (Playwright, dev server, fresh content sync):
RC set intro screen renders the full passage + correct target-time; "Attempt
set" → Q1 shows the passage still visible above the question stem/options
(the same single-column layout Milestone 8 established), zero console
errors. DILR bar-chart set: SVG renders with correct values/legend. Full
local CI re-run after all additions: lint (pre-existing warnings only),
`tsc -b` clean, 147/147 vitest, production build succeeds, and
`validate_content.py` passes (427 questions, 86 micro-topics — count is
climbing further since Milestone 7's QA batch is still running in the
background, unaffected by this milestone's work).

**Content-scoped, not content-complete** — same honest framing as
Milestones 7, 8, and 10. Against SPEC.md §6.5's target composition:
RC has **1 of 60-80** target passages, DILR-as-sets has **2 of 120-160**
target sets (1 table + 1 bar-chart), VA has **3 of 200-250** target
para-jumbles. This milestone's job was proving each of the three pipelines
end-to-end (source discipline, verification gate, deterministic-answer
pattern) and closing the chart-rendering UI gap blocking DILR entirely —
not scaling any of them to target volume. Scaling RC/DILR/VA the way
Milestone 3's addendum scaled QA (239→398) is unstarted follow-up work, as
is building the other 5 chart kinds `PassageSetPlayer` doesn't render yet.

Run locally: `cd pipeline && conda run -n cat-pipeline python build_rc_passage_1.py`
/ `build_dilr_barchart_demo.py` / `build_va_parajumbles.py`, then
`cd app && npm run dev`, visit `/#/set/varc.rc.on-liberty-intro.set-01` or
`/#/set/dilr.di.bar-column.set-01`.

### Milestone 12 — Review & SRS (done)

SPEC.md §8.4/§14: `ts-fsrs` (explicitly named in SPEC.md §8.4 as the recommended scheduler — "if
you want the best available" — so treated as pre-approved the same way §7's tech stack is, not
an undocumented dependency needing a stop-and-ask). `app/src/srs/` wraps it:

- **`fsrsAdapter.ts`** — `gradeReview()`/`initFsrsState()`/`isDue()`. Persisted state is
  `{stability, difficulty, nextReviewAt, lastReviewedAt}`. The `lastReviewedAt` field is a
  Milestone 12 addition on top of SPEC.md §5.2's frozen three (`nextReviewAt`/`stability`/
  `difficulty`) — caught by a failing test (`gradeReview` produced the *identical* stability
  across two well-spaced "Good" reviews) that FSRS's stability-growth math needs the actual
  elapsed time since the last review, not just "is it past its due date," and there was nowhere
  to persist that without a new field.
- **`topicReview.ts`** — `mapAttemptToGrade()` (correctness + the same pre-reveal confidence
  signal §8.5's guess-discount uses → Again/Hard/Good/Easy) and `applyDecay()`
  (SPEC.md §8.4: FSRS "schedules the decaying → review cycle" — a `mastered` topic whose FSRS
  review has come due reads back as `decaying` for display/planning). Every practice attempt is
  treated as an implicit topic-level review — SPEC.md doesn't define a separate topic-review
  session, unlike cards. Wired into `masteryEngine.recordAttemptForMastery` (replacing the inert
  `stability: 0, difficulty: 0` placeholder Milestone 5 left there) and into every place that
  *reads* MasteryState for display or planning (`Drill.tsx`, `Diagnostic.tsx`, `Calendar.tsx` ×3)
  via `applyDecay`/`withDecayApplied` — decay is computed at read time, not stored continuously,
  same trade-off as everything else in this static app with no background job.
- **`addToDeck.ts`** — SPEC.md §8.4's card level. `addMistakeCard()`: every wrong attempt, from
  `QuestionPlayer.tsx`'s existing `next()` (never resets an already-tracked card's schedule just
  because she got it wrong again — that's what grading it Again is for). `addFormulaCardsForTopic()`:
  wired to the `unknown_formula` errorTag specifically — SPEC.md §8.5's table: "Didn't know
  formula → Auto-add the formula card to the SRS deck." New `SrsCard` learner-state type, full
  StorageAdapter → Dexie v4 → migrations → ExportBundle plumbing (same pattern as every prior
  addition this build).

**Mistake Notebook** (`pages/MistakeNotebook.tsx`, `/mistakes`) — SPEC.md §14 item 1: auto-populated
from wrong Attempts (most recent per question, so a since-fixed mistake doesn't linger forever),
filterable by error tag and topic, **"Re-attempt this set"** replays exactly the filtered
questions through `QuestionPlayer` (not generic topic practice — the literal missed questions).

**Review / formula deck** (`pages/Review.tsx`, `/review`) — SPEC.md §14 item 3: due `SrsCard`s
(formula cards render title/formula/example; mistake cards render the question stem), a
"Show answer" flip, then Again/Hard/Good/Easy grading that calls `gradeReview` and reschedules.

Verified live end to end: answered a Percentages question wrong, tagged "didn't know formula",
confirmed 3 real `SrsCard` rows in IndexedDB (1 mistake + 2 formula cards — Percentages' lesson
has two), confirmed both appear as due and render correctly in `/review` including live KaTeX,
confirmed the Mistake Notebook shows the tagged entry with working filters, and confirmed
"Re-attempt this set" actually launches `QuestionPlayer` on the exact missed question. Zero
console errors throughout.

**Deliberately out of scope**: SPEC.md §8.5's other error-tag responses (highlight-the-ask mode
for misreads, a pacing trainer for time-outs, an elimination-discipline drill for careless picks)
are each their own standalone feature, not part of this milestone's terse three-part definition
("Mistake notebook, FSRS scheduling, formula deck") — only the formula-card row of that table is
implemented. Vocabulary-in-context cards (§8.4's third card type) need VARC content that doesn't
exist yet (Milestone 13).

### Milestone 11 — Mock analytics (done)

SPEC.md §9.3's post-mock analysis, in `app/src/mock/{analysis,percentile}.ts` (pure,
unit-tested — 21 more tests) plus `pages/MockAnalysis.tsx` at `/mock-result/:resultId`:

- **Score & estimated percentile**: a hand-built anchor-point lookup table (`percentile.ts`)
  interpolated between roughly-known CAT percentile bands, since there's no live cohort to compute
  a real one against. Every result carries the exact disclaimer SPEC.md §9.3 requires verbatim
  ("Estimated from historical CAT data — indicative only") — tested that the disclaimer is always
  present, not just the number.
- **Time-allocation waterfall**: minutes spent vs. marks earned, per section, from
  `MockResult.questionTimings` (already recorded by Milestone 10's dwell tracking).
- **Bleeder report**: attempted, wrong, and over 150 seconds — sorted worst first. Explicitly
  excludes skips (not "wrong," just unattempted) and slow-but-*correct* attempts.
- **Selection quality**: what fraction of skipped questions were "easy" — defined as below this
  mock's own median item-Elo (not a fixed absolute cutoff, which would misfire on a mock that's
  uniformly hard or easy) — with a call-out when that fraction is high.
- **TITA discipline**: every blank TITA flagged explicitly, with the "no negative marking, this is
  a pure unforced error" framing SPEC.md §9.3 calls for.
- **Accuracy vs. attempts curve**: only her attempted questions have a known outcome (an unattempted
  question's counterfactual result is unknowable), so the curve orders attempted questions
  easiest-first by item-Elo and asks "if she'd stopped after only her N easiest, what would the
  cumulative score be" — directly answering SPEC's "should you have attempted 18 or 22."
- **Micro-topic damage report**: marks lost per micro-topic from wrong attempts (MCQ only — wrong
  TITA costs 0 marks per SPEC.md §2's asymmetry, so it contributes no "damage"), sorted worst
  first, each with a one-click **Practice** link straight to `/drill/:topicId`.
- **Auto-generated remediation, writing back into the plan** — SPEC.md §9.3: "a mock that doesn't
  change tomorrow's schedule is a wasted mock." Fully automatic on loading the analysis page (not
  a manual per-topic button, since a report nobody has to act on doesn't satisfy that line either):
  the top 3 damaged topics get a real `kind: 'review'` PlanItem added to tomorrow's PlanDay via
  the existing `storage.putPlanDay`, skipping any topic already planned. Verified live by reading
  IndexedDB directly after a mock with one deliberately-wrong MCQ: the exact micro-topic showed up
  in tomorrow's `planDays` row, not just in the UI banner claiming it had.

**New field**: `MockResult.startedAt` (optional, backward-compatible) — every `Attempt` from one
mock sitting already shared the session's `startedAt` (Milestone 10), so this is the join key the
analysis page uses to find "this specific result's attempts" without needing a new attempt-to-
result id anywhere; a mock can be retaken and each sitting's attempts stay distinguishable.

Verified live end to end with a short-duration test mock (same technique as Milestone 10, real
mocks run 40-minute sections): answered questions with deliberately wrong answers, confirmed the
score, damage report, and remediation banner all matched, and confirmed the actual IndexedDB write
independently of what the UI claimed happened. Also caught, while composing the first live test,
that most of `mock-1`'s reserved bank is TITA-format (21 of 22) — not a bug, just meant the first
naive test slice happened to sample zero MCQs and produced a score of exactly 0 with no damage;
had to deliberately pick an MCQ id to exercise the damage/remediation path at all.

### Milestone 10 — Mock engine (done, content-scoped)

SPEC.md §9.1's full mechanics, in `app/src/mock/` (pure, unit-tested: `paletteStatus.ts`,
`scoring.ts`, `timing.ts` — 20 tests) plus `pages/MockPlayer.tsx` and
`components/mock-player/{Palette,Calculator}.tsx`:

- **Full-screen** on start (`requestFullscreen`), **exit warning** via `beforeunload` while a mock
  is in progress.
- **Per-section hard-locked countdown**, computed from wall-clock elapsed since
  `session.sectionStartedAt` (never a pausable in-memory countdown — required for crash recovery
  to show correct remaining time), amber/red styling under the 10-second SPEC.md-mandated warning
  threshold, **auto-advance at 0:00**.
- **No back-navigation**: `completedSectionIndices` tracks finished sections; the player only ever
  renders the current section, nothing offers jumping back into a finished one.
- **Real CAT palette convention** (`paletteStatus.ts`): not_visited (grey) / not_answered (red) /
  answered (green) / marked (purple) / answered_marked (purple + ring) — deriving purely from
  `{given, markedForReview, visitCount}`, no separate "status" field to keep in sync.
- **Save & Next / Clear / Mark for Review & Next**, TITA numeric input vs. MCQ radio options.
- **Draggable 4-function + %+ √ calculator** (pointer-event drag, no library).
- **Dwell time + visit count per question**, accumulated via wall-clock deltas on every navigation.
- **Crash recovery**: `MockSession` (new singleton-row learner-state type, full StorageAdapter →
  Dexie v3 → migrations → ExportBundle plumbing, same pattern as every other learner-state type —
  going through localStorage instead would have violated CLAUDE.md's "all learner state behind
  StorageAdapter" rule) persisted every 5 seconds *and* immediately after every explicit
  answer/navigation action. On mount, an existing session for the same mockId resumes instead of
  restarting.
- **`mock_reserved` flag** (SPEC.md §9.1 exact wording): new optional `Question.mockReserved`
  field (schemas.py, backward-compatible default `False`). Reserved items are excluded from
  `questions/index.json` entirely at sync time (`sync-content.mjs`), not just filtered at
  selection time — nothing that scans the index (drill queue, the diagnostic) can discover one.
  `Drill.tsx` also filters defensively at the point of use.
- **Marking scheme** (`scoring.ts`): MCQ +3/-1, TITA +3/0 (SPEC.md §2's asymmetry), computed via
  the same `computeCorrect()` QuestionPlayer already used — exported from there rather than
  duplicated, so there's exactly one definition of "correct" anywhere in the app.
- **New content type**: `MockDefinition`/`MockSectionDef` (schemas.py), validated in
  `validate_content.py` with a question-id cross-reference check (a mock referencing a
  non-existent question fails CI). `pipeline/compose_mock_1.py` composes one real mock from the
  already-verified QA bank and flags the chosen items reserved — never invents a question.

**Content-scoped, not content-complete.** SPEC.md §9.1 wants 5 full mocks (VARC 24Q / DILR 20Q as
sets / QA 22Q, escalating difficulty). VARC has zero content and DILR has one set (already used in
the Milestone 8 demo, not reserved), so **`mock-1` ships with only its QA section** (22 questions,
spread across topics/difficulty). Initially composed with empty 40-minute VARC/DILR sections
included "for format fidelity" — caught in live testing that this is actively worse than omitting
them: the per-section timer runs for the section's full duration regardless of question count, so
that would force sitting through two dead 40-minute blocks before ever reaching real content.
Recomposed to include only sections with real content. The rest of the 5-mock, all-sections target
is blocked on Milestone 13 (Content pipeline v3), same dependency Milestone 7's write-up already
flagged for VARC/DILR-set generation.

**Three real bugs caught via live Playwright testing** (not by typecheck — all logic bugs):
1. `questions[index].id` was read before bounds-checking `index` against `questions.length` in an
   early draft — same class of bug as Milestone 8's, from copying that page's end-of-list pattern
   without re-deriving it; caught and fixed before it shipped.
2. **Stale-closure double-update**: `markForReviewAndNext` originally composed two separate
   `setSession(...)` calls in the same synchronous handler (toggle-mark, then save-and-advance);
   both read the same pre-update `session` closure, so the first call's effect was silently lost.
   Fixed by consolidating every answer/navigation path through one `commitAndGoTo()` that computes
   the full next state once.
3. **The crash-recovery persistence itself didn't work**, discovered by an actual reload-mid-mock
   test: the first fix attempt captured the computed next-state from *inside* a functional
   `setSession(prev => ...)` updater and tried to persist it immediately after — but React doesn't
   invoke that updater synchronously inline (it's deferred to the render pass), so the captured
   value was reliably still `null` right where it was read. Since `commitAndGoTo` is only ever
   called once per handler (bug 2's fix made this safe), switched to computing `next` directly
   from the `session` closure instead of a functional update, which *is* available synchronously
   for persisting. Reconfirmed with the same reload test: resumes at the exact question and
   remaining time.

Verified live with a short-duration test mock (real mocks run 40-minute sections, impractical to
sit through in an agent session): section auto-advances/auto-submits at 0:00 into "Mock complete,"
a `MockResult` is written with correct per-section scores, one `Attempt` (`mode: 'mock'`) per
question feeds `recordAttemptForMastery` same as Drill/Diagnostic, and `MockSession` is cleared
after finishing.

**Known gap**: mock-attempted questions are excluded from `topicQuestions` (since they're
`mockReserved`, hence absent from the question index `loadQuestionsForMicroTopic` reads), so a
mock attempt on a hard/very_hard item may not correctly register for that topic's ceiling-mastery
criterion (SPEC.md §8.2). Elo updates are unaffected. Narrow enough to leave for now — full fix
would mean threading reserved items back into mastery's topic-composition view without letting
them leak into the drill queue.

Run locally: `cd app && npm run dev`, then `/#/mock/mock-1`.

### Milestone 9 — Planner, Calendar & Triage (done)

SPEC.md §10 in full: `app/src/planner/` is four pure, independently unit-tested
modules (28 tests) with no framework dependency —

- **`roiSort.ts`** — `roiWeightedTopoSort()`: topological sort over
  `MicroTopic.prerequisites` where topics with satisfied prerequisites are
  ordered by `roiScore * catFrequencyWeight * (1 - currentMastery)`.
  `currentMastery` has no direct source (MasteryState.status is categorical,
  not a 0-1 scalar) — mapped via a fixed table
  (`locked/available`→0, `learning`→0.3, `practising`→0.6, `decaying`→0.7,
  `mastered`→1). A prerequisite cycle can't infinite-loop the sort; it just
  breaks the cycle by taking any remaining topic.
- **`generatePlan.ts`** — packs the sorted queue into `PlanDay[]` from today
  to exam date: 20% of every day reserved for `kind: 'review'` (sentinel
  `microTopicId: '__review__'` — real FSRS-scheduled review items are
  Milestone 12), Sundays from week 3 onward become a single `kind: 'mock'`
  day (sentinel `'__mock__'`), the last 3 weeks before the exam get zero new
  `learn`/`drill` items (hard cutoff per spec), and topics costed at
  `estLearnMinutes + 10 questions * targetSecPerQuestion` don't start on a
  day that can't fit them if the day already has something else scheduled.
  Already-`mastered` topics are excluded from the queue entirely.
- **`coverageForecast.ts`** — SPEC.md §10.2's Triage: "high-ROI" = `roiScore
  >= 3`; reports % of those actually scheduled before the cutoff, and names
  the specific dropped topics + an hours estimate, not just a percentage.
- **`missedDay.ts`** — SPEC.md §10.3: redistributes a missed day's undone
  items across the next 5 days, capped at `max(1, floor(baselineItemsPerDay *
  0.25))` per day (item-count is a proxy for "daily load" — PlanItem carries
  no explicit minutes field), round-robin by day, dropping lowest
  ROI-priority items first if capacity runs out.

**Diagnostic** (`pages/Diagnostic.tsx`): ~15 questions via
`diagnosticSelection.ts`, split evenly across VARC/DILR/QA and striding
across difficulty within each section's pool, with an explicit top-up pass
so a section with no content (VARC has none yet) doesn't shrink the total —
its share gets redistributed to sections that do have content. Every
attempt goes through the **existing, unmodified** `QuestionPlayer` →
`recordAttemptForMastery` pipeline from Milestone 5 — there's no separate
Elo-seeding mechanism to build or keep in sync; whatever topics the
diagnostic happens to sample get a real, engine-computed `MasteryState`
exactly like a normal drill attempt would produce. On completion,
`generatePlan()` runs once and every `PlanDay` is written via
`storage.putPlanDay`; `Settings.diagnosticCompletedAt` (new optional field,
same "add it, document it" pattern as Milestone 5's `MasteryState`
additions) gates the first-launch redirect in `Today.tsx`.

**Calendar** (`pages/Calendar.tsx`): GitHub-style heatmap (last 12 weeks,
intensity from `Attempt.timeSpentSec` summed per day), tap-a-day detail
(planned items vs. actual attempts/correct/minutes), a 14-day forward list,
exam-date + registration-deadline display (from the new `exam-meta.json`),
the Coverage Forecast banner, and a missed-day banner with a "Redistribute"
action wired to `missedDay.ts`. A "Regenerate plan" button reruns
`generatePlan()` from **tomorrow** onward only — today's `PlanDay` is never
touched, so a settings change (e.g. adjusting `dailyMinutes`) can't wipe out
`done: true` flags on items already completed today.

**Settings** (`pages/Settings.tsx`) gained the `dailyMinutes` / `examDate` /
`weakSectionBias` editing fields SPEC.md §5.2 always specified but that had
no UI to live in before this milestone.

**New content type**: `content/exam-meta.json` (SPEC.md §2's hard facts —
exam date, slots, registration window, marking scheme) is now a
`schemas.py`-validated content type like everything else in `/content`,
generated by `pipeline/build_exam_meta.py`. Not a directory-of-many-files
like `questions/`, so `validate_content.py` validates it with a few
dedicated lines rather than the shared `validate_dir()` helper.

**Two real bugs caught by live Playwright testing, fixed before commit**
(not by typecheck — both were logic bugs, not type errors):
1. `diagnosticSelection`'s difficulty-striding loop had a guard bound
   (`pool.length * 2`) that was too tight whenever a section's pool
   clustered in one difficulty bucket (exactly this repo's current DILR
   content — one set, mostly `easy`/`medium`) — it returned far fewer
   questions than requested. Also didn't top up an empty section's share
   from sections that do have content, so `selectDiagnosticQuestions(index,
   15)` could return as few as 5. Rewrote with a per-section cursor and an
   explicit top-up pass; both fixed and covered by new tests
   (`diagnosticSelection.test.ts`).
2. `generatePlan` was scheduling from the **entire syllabus**, including
   VARC topics with zero questions in the bank — the generated plan
   confidently scheduled "learn: Main Idea / Central Theme" with a "Go"
   link to a topic that has no drillable content at all. Fixed with a new
   `topicsWithContent()` helper in `loadContent.ts` (syllabus ∩ topics
   present in the question index), used at both call sites (`Diagnostic`,
   `Calendar`) instead of the raw `loadSyllabus()`.

Run locally: `cd app && npm run dev`, visit on a fresh IndexedDB (or after
`storage.clearAll()`) to see the diagnostic → plan → calendar flow.

### Milestone 8 — Passage/Set player (done)

One real DILR set for `dilr.di.tables`, same "one micro-topic fully playable
end to end" approach as Milestone 6's single lesson:
`pipeline/build_dilr_table_demo.py` generates a 5-company × 4-quarter
revenue table and derives 4 questions from it, each answer computed by a
`_expected()`-style function *from the same `DATA` dict the learner sees*
and asserted in-script — not hand-typed separately, so a transcription slip
would fail the script instead of shipping quietly wrong. `licence:
CC0-1.0` (original synthetic data, nothing to attribute).

`PassageSetPlayer.tsx` (route `/set/:setId`): renders the passage/table via
a small `SetAsset`/`TableAsset` renderer (chart assets not implemented yet —
no chart-type DILR content exists to build against), a set-level timer
(amber at 1.5x target, red at 2.5x per SPEC.md §13 — the per-question timer
in `QuestionPlayer` still doesn't have this, out of scope here), and the
**attempt/skip decision step** SPEC.md §15's Milestone 8 row calls for
explicitly. Skipping logs every question in the set as skipped
(`given: null`) via `storage.addAttempt` directly, same semantics as an
individual question's skip button, so mastery/SRS state doesn't silently
drop them. Attempting reuses `QuestionPlayer` per question with the
table/passage kept visible above it (single-column, matching this app's
existing mobile-first layout — no split-pane).

New content-loading plumbing: `loadPassageSetIndex()` / `loadPassageSet()`
in `loadContent.ts`, a `passage-sets/index.json` manifest built by
`sync-content.mjs` (same reasoning as the existing questions/lessons
indexes — static hosting can't list a directory). `Today.tsx` gained a
"Sets" section listing available sets.

**One real bug caught by live Playwright testing**: the end-of-set
completion check read `questions[index].id` before checking `index` against
`questions.length` — crashed on `undefined.id` after the last question
instead of reaching the "Set complete" screen. Fixed by reordering the
bounds check first.

### Milestone 7 — Content pipeline v2 (infrastructure done, generation ongoing)

SPEC.md §6.3's full verification loop, implemented in `pipeline/qagen/`:

- **`sandbox.py`** — runs an LLM-emitted `compute()` function in a
  subprocess with a static import allowlist (`math`/`sympy`/`fractions`/
  `itertools`/`decimal`/`statistics`/`cmath` only, regex-rejects
  `os`/`subprocess`/`eval`/`exec`/etc. before ever executing), CPU/memory
  `rlimit`s, and a timeout. Not a full seccomp jail — this runs
  LLM-generated arithmetic code on the project owner's own machine, not
  arbitrary untrusted internet input; the controls match what SPEC.md §6.3
  actually asks for ("sandboxed subprocess with a timeout").
- **`llm_harness.py`** — per item: draft (stem + options/value + solution +
  verifier code) → run the verifier and require its output equal the
  claimed value → for MCQ, a distractor-audit call → 5-sample
  self-consistency at temperature 0.8 requiring ≥4 agreement → embedding
  (`sentence-transformers`, `all-MiniLM-L6-v2`, cosine >0.92) + a
  normalised-number hash dedup against the whole existing bank. Any failure
  at any stage discards the item — never repaired, per SPEC.md §6.3's
  explicit rule.
- **`llm_client.py`** — thin OpenAI-compatible chat client. Points at
  **Ollama** (`http://localhost:11434/v1`, model `qwen2.5:32b`), not vLLM as
  SPEC.md §6.3 names specifically. Ollama was already running on this
  machine as a stable service with the model pre-pulled; standing up vLLM
  instead turned into a multi-hour fight (its current PyPI wheel hard-links
  `libcudart.so.13` at the native-extension level — this box's driver only
  supports CUDA 12.9, and no combination of reinstalling torch for a
  matching CUDA build fixed it, since vLLM's own compiled `.so` is what's
  pinned to 13, independent of whatever torch version sits next to it;
  eventually resolved by pinning `vllm==0.8.5.post1`, which is old enough to
  predate the CUDA 13 default, before abandoning that path entirely once
  Ollama turned out to already be available). Both speak the identical
  `/v1/chat/completions` contract, so swapping back to a real vLLM server
  later is a one-line env var change (`VLLM_BASE_URL`), nothing else in the
  harness needs to change. The now-unused `serve_llm.sh` vLLM launch script
  is left in place for that eventuality.
- **`run_llm.py`** — CLI entry point, iterates QA micro-topics generating a
  requested count each, prints per-topic accept/reject summaries.

**Model/pip environment lives on `/data`, not the home directory** — this
machine's root filesystem had only ~7GB free (shared box, many users'
conda envs). `HF_HOME` and the `cat-llm` conda env are both under
`/data/Nidhi_backup_run/`.

**One real crash, caught and fixed**: the first background batch run died
~2 hours in on an uncaught `requests.exceptions.ReadTimeout` —
`llm_client._chat()` only wrapped HTTP-status failures in the harness's own
`LLMError`, so a single slow call on this shared, one-request-at-a-time
Ollama instance (no free concurrency to parallelize — confirmed by timing
two concurrent requests against one sequential baseline, identical total
time) took the whole multi-hour process down instead of being retried like
every other failure mode already was. Fixed in `llm_client.py` (wrap
`requests.RequestException` too) and hardened `run_llm.py` (per-item
try/except inside `generate_for_topic`, not just per-topic in `main()`, so
partial progress within a topic survives an unexpected failure). Resumed
from where it died rather than restarting from scratch.

**Status as of this write-up**: bank at 405 questions (398 from Milestone
3's deterministic generators + 4 hand-authored DILR + 3 LLM-verified so
far), climbing at roughly one verified item per 1-3 minutes with the batch
still running in the background. Yield is running ~40-50% (rejections are
mostly self-consistency disagreement and the model occasionally truncating
a long solution against the `max_tokens=2048` cap on the draft call — both
benign, just retried). This is nowhere near SPEC.md §6.5's target
composition (QA 700-900, DILR 500-650 as *sets*, VARC-RC 250-320, VARC-VA
200-250) — only the QA generation path is built; DILR-set and VARC (RC/VA)
generation need their own pipelines per SPEC.md §6.3's inversion (DILR:
generate data programmatically first, let the LLM only write the framing;
RC: real open-licence source text, never LLM-generated passages) and are
not started. Milestone 13 ("Content pipeline v3") is explicitly where the
RC/DILR-set work belongs — QA scale-up continuing in the background in the
meantime doesn't block moving on to Milestone 10.

**To check on or resume the batch**: `ps aux | grep run_llm`, or
`tail -f` whatever log it's writing to. To restart after a stop, diff
`content/questions/*.llm-*.json` topic counts against `syllabus.json`
targets and pass `--topics` with whatever's left, same as the resume after
the crash above — regenerating already-complete topics from scratch wastes
GPU time for no benefit since dedup will reject exact repeats anyway but
still costs a full generation+verification cycle to find that out.


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
- **QA/VARC LLM generation queued but not run (content round 3)** — deliberately deferred because
  the project owner's GPU was busy with another process. `pipeline/qagen/run_llm.py
  --shortfall-only` (from `/pipeline`, `cat-llm` conda env, needs Ollama up at
  `localhost:11434`) will fill the ~649-item QA shortfall against the new (correct) `COUNT_BY_ROI`
  targets once the GPU is free. VARC's 12 zero-question topics need `rc_harness.py` (RC) or a new
  LLM pipeline (VA) — neither run this round.
- **The QA-batch "hang" root cause (round 2) is still not fixed**, only made observable —
  `llm_harness.py` now prints per-stage progress (see content round 3) so a live run's state is
  visible, but the actual fix (bounding `max_tokens` more tightly, or a true wall-clock deadline
  that doesn't reset on partial streamed tokens) has not been implemented.
- **A pre-existing LaTeX-rendering bug was spotted incidentally** (during the theme-fix
  screenshot pass) in at least one LLM-generated QA question's `solutionMarkdown`: raw, unescaped
  `\%`/`\times` printed literally instead of rendering, and one instance of a mangled
  `\text{...}` (lost backslash, showing " ext..."). Flagged to the project owner, not
  investigated — scope across the ~465+ LLM-generated questions is unknown.
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

---

## Session: reset controls, ntfy reminders, design pass, lesson depth

Four things were asked for: the aesthetic was still poor, progress needed to
be resettable (all of it, and per topic), lessons were far too shallow, and
reminders should reach a phone via ntfy.

### Reset progress (new)

- `StorageAdapter.resetMicroTopic(id)` clears one topic's attempts, mastery
  record, SRS cards, bookmarks, and the item-Elo rows for questions left with
  no attempt. It deliberately does **not** touch plan days or mock results:
  those record what happened on a given day, not what she currently knows, and
  silently rewriting them would make the calendar and score history lie.
- Item Elo is only dropped once a question has no surviving attempt, so
  resetting one topic cannot reset a set-mate topic's calibration. Covered by
  a test using a question carrying two micro-topic ids.
- **Bug found while building this:** `clearAll()` cleared IndexedDB only. With
  Supabase configured, the pending sync outbox still held upserts of the data
  just deleted, so the next flush would have written all of it back. Full
  reset now drops the outbox, deletes remote rows, then clears local — in that
  order — and reports whether the remote step actually happened rather than
  implying a wipe that never reached the server.
- Both surfaced in Settings, with the guard scaled to the blast radius: one
  topic takes a second click, everything takes the typed word RESET.
- Supabase migration `0003_ntfy_settings.sql` adds the two jsonb columns the
  new settings need.

### Phone reminders via ntfy (new)

SPEC.md §11's Phase 1 notification can only fire while the app is open, and
Phase 2's backend only sends email — so nothing reached a closed phone.

- `notify/ntfy.ts` publishes to a learner-supplied ntfy topic. No API key is
  involved: ntfy topics are unauthenticated, the topic is entered at runtime
  and stored in learner state, and nothing is baked into the bundle. Because
  the topic name *is* the password, Settings generates a random one and says
  so plainly.
- The daily reminder is scheduled ahead using ntfy's `delay`, and **cancelled
  by sequence id the moment the day's plan is finished**, so it cannot arrive
  after she is already done. Nothing is sent at all once the chosen time has
  passed — a late nudge is the "compliance report" §11 forbids.
- `notify/nudgePlan.ts` is pure and holds every decision; 12 tests cover the
  cancel-on-completion path, the once-per-topic announcement, the
  don't-re-publish-unchanged case and the past-the-time silence.
- Verified against ntfy.sh directly, not just against the docs: CORS preflight
  (`access-control-allow-origin: *`, POST/DELETE allowed), JSON publish with
  tags/click/priority, scheduled publish with `delay` + `sequence_id`, and
  DELETE cancellation returning 200.

### Design pass

- New primitives: `Card`, `PageHeader`/`BackLink`, `StatusChip`, `Meter`.
  Pages had been hand-rolling one-off containers with different padding and
  radius each time.
- Dark surfaces re-stepped (background 0.16 → 0.145, card 0.20 → 0.22). At the
  old 0.04 lightness gap the app read as one flat sheet with hairlines on it,
  which was most of why it looked unfinished.
- SPEC.md §13's reading font finally applied to lessons: 18px / 1.7 serif from
  a device-font stack (Charter → Source Serif → Literata → Georgia), so no
  webfont download and nothing added to the offline cache.
- **Today** was the worst screen. QA alone rendered 44 open rows above the
  fold, every one labelled "Lesson included" — the same eleven characters 86
  times. Sections are now collapsed with a per-section progress meter, and
  each topic row shows its real status and accuracy. Page height dropped from
  ~9,700px to ~4,400px.
- Shortcuts now reach the practice builder, formula hub and search, which had
  been merged but had **no entry point anywhere in the UI**.
- Lesson rebuilt for long lessons: contents strip derived from the lesson's
  own headings, solutions collapsed by default (SPEC.md §13 — and a worked
  example whose answer is already on screen is one nobody attempts), pinned
  practice CTA.
- Redundant "Back" links dropped from every page that owns a nav tab.

### Lesson depth

The complaint was that lessons did not teach enough to solve the questions.
Measured, that was right: median 158 words, typically a definition and one
example, against topics whose banks span six or seven distinct archetypes.

- `LessonSpec` gains `methods` — one `Method` per archetype the topic's
  questions actually come in, each with how to **recognise** it (choosing the
  method is the hard part in a timed paper), the steps, and a worked instance.
  Plus `prereq` and a closing `checklist`.
- Archetypes were taken from `qagen/templates/*` and the tags on
  `content/questions/*.json`, so coverage tracks the real bank.
- The markdown tokenizer gained ordered/unordered lists, which procedural
  steps need. All-or-nothing per block, so a paragraph like "the ratio came to
  1. 5 times the original" stays a paragraph. 5 tests.
- **Nine lessons had JSON on disk but were declared nowhere in the package** —
  unbuildable and unchecked. All nine are now declared, so every QA lesson in
  /content is reproducible from source.
- Result: **QA lessons median 433 words across 45 topics** (from ~150), with
  101 methods, and the longest at 1,144 words.
- **Every numeric claim was re-derived independently** (fractions, `comb`,
  Legendre counts, brute-forced solution sets) rather than re-read. That caught
  three real errors in text written this session: a linear-equations example
  that trailed off mid-solution, an integer-solutions example claiming `y` must
  be a multiple of 3 for `3x + 5y = 100` (false — `y = 3` gives `3x = 85`), and
  an unanswered non-negative variant. 239 claims verified in total.

### Verified

CI green throughout: typecheck, 276 tests (+17), content validation (86
lessons, 1,428 questions). Live in Chromium with zero console errors: the
per-topic reset was exercised through the UI and confirmed against IndexedDB
(6 attempts → 2, only the target topic's four removed, mastery row cleared).

### Not done — do not read this section as complete

- **DILR lessons (median 150 words) and VARC lessons (median 219 words) have
  not had the `methods` treatment.** Only QA does. This is the largest
  outstanding piece of the "teach every topic properly" request.
- Two lessons are still undeclared: `varc.rc.main-idea`,
  `varc.va.para-jumbles`.
- 9 topics still have zero questions: 6 VARC RC types (need real open-licence
  passages), 3 DILR chart types (need radar/bubble/combination SVG renderers).
- `pipeline/qagen/templates/series.py` is written but still not wired into the
  templates registry or run.
- The QA LLM batch (~649 items) is still blocked on the GPU.
- ntfy delivery was verified against the server with curl; it has not been
  confirmed arriving on a real handset, which only the phone's owner can do.
