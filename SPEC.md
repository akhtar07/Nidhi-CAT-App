# BUILD PROMPT — "Ascent": A CAT 2026 Preparation Web App

> **How to use this document (read this part yourself, don't paste it):**
> Do **not** paste this whole file into Sonnet and say "build it." It will produce 3,000 lines of half-working code and lose the thread.
> Paste **Section 0 through Section 6** as the first message (that's the spec). Then paste **one milestone from Section 15 per session**, and start each session with: *"Read SPEC.md and PROGRESS.md in the repo, then implement Milestone N only. Update PROGRESS.md when done."*
> The single highest-leverage instruction in this whole document is **Section 5: freeze the data schema before writing any UI.** If the schema changes at Milestone 8, everything before it gets rewritten.

---

## SECTION 0 — MISSION

You are building **Ascent**, a single-user, offline-first, mastery-based preparation system for the **CAT 2026** exam (India, MBA entrance). It is not a question dump. It is a *system that decides what the learner should do next and proves she has actually learned it.*

The learner is one person. There is no signup flow, no multi-tenant concern, no leaderboard, no social feature. Optimise for: **her opening it daily and knowing exactly what to do in the next 45 minutes.**

**The three things this app must do better than any free alternative:**
1. **Gate progression on demonstrated mastery**, not on "topics ticked off."
2. **Diagnose *why* she got something wrong** (concept gap vs. calculation slip vs. misread vs. time panic) and route her practice accordingly.
3. **Train exam behaviour** — question selection, skipping discipline, sectional time budgeting — which is where most CAT aspirants actually lose marks.

**Success criterion for the whole build:** on any given day she opens the app, sees one clear "Today" card, does the work, and her progress bar and calendar update without her configuring anything.

---

## SECTION 1 — NON-NEGOTIABLE CONSTRAINTS

Violating any of these means a rebuild. Confirm you understand them before writing code.

1. **Deployment target is GitHub Pages** → the app must build to **fully static assets**. No Node server at runtime. No server-side rendering. No secrets in the client bundle.
2. **All learner state lives in the browser (IndexedDB)** as the source of truth, behind a `StorageAdapter` interface. A `SupabaseAdapter` implementing the same interface is added later without touching any component. Design for this from commit one.
3. **All content ships as versioned JSON/Markdown inside the repo.** Content is data, not code. A content update must be a JSON edit + CI validation, never a code change.
4. **Everything must work offline** after first load. It is a PWA with a service worker.
5. **Mobile-first.** Assume she uses a phone 60% of the time and a laptop for mocks. Mocks may be desktop-gated with an explicit message.
6. **Every question renders math with KaTeX** and must be readable on a 360px viewport.
7. **No fabricated content in the shipped bank.** Every question in the repo has passed the verification pipeline in Section 6. A wrong answer key destroys trust permanently — one bad question costs more than fifty missing ones.
8. **Zero-config for the learner.** She never picks a difficulty, never builds a plan, never chooses what to study. The app decides. She can override, but never has to.

---

## SECTION 2 — HARD FACTS ABOUT CAT 2026 (bake these into the app, don't guess)

Store these in `content/exam-meta.json` so they can be corrected in one place.

- **Exam date: Sunday, 29 November 2026.** Conducted by IIM Indore. Three slots: 08:30–10:30, 12:30–14:30, 16:30–18:30 IST.
- Registration window: 3 August – 15 September 2026. Add a dismissible banner reminding her to register, with a hard-stop warning at T-7 days.
- **Format:** Computer-based, **120 minutes total**, **three sections**, **40 minutes per section, hard-locked and sequential**. She cannot return to a previous section. The app's mock engine must replicate this exactly.
- **Section order is fixed:** VARC → DILR → QA.
- **Question count:** ~66–68 total. Recent pattern: VARC 24, DILR 20, QA 22.
- **Marking:** MCQ = +3 correct, −1 wrong. **TITA** (Type In The Answer) = +3 correct, **0 for wrong**. Roughly 1/3 of questions are TITA. This asymmetry is strategically enormous — the app must teach her to *always* attempt TITA and be selective on MCQ. Build this into mock analytics as an explicit metric.
- **On-screen calculator only** — a basic four-function calculator, no scientific functions. Replicate this in the mock UI and **disable the keyboard's ability to use anything else**. She must build the habit of not reaching for a phone calculator.
- Maximum score: ~198–204.

**Timeline note the app must handle:** today is well past the "one year of prep" fantasy. If she starts now, there are roughly **16 weeks / 112 days** to the exam. The plan generator (Section 10) must be built for a *compressed, triage-based* schedule — it must be capable of saying "skip this topic, the ROI isn't there in your remaining time." A 12-month plan template is useless here.

---

## SECTION 3 — THE FULL SYLLABUS TAXONOMY

This is the backbone. Encode it as `content/syllabus.json` with a strict three-level hierarchy: **Section → Topic → Micro-topic**. Every question, lesson, and progress record keys off a `microtopic_id`. Use stable slug IDs (`qa.arith.tsd.boats-streams`), never array indices.

Each micro-topic node carries:
```
{ id, name, section, topic, prerequisites: [ids], cat_frequency: "high|medium|low|rare",
  roi_score: 1-5, est_learn_minutes, target_time_per_question_sec, formula_card_id }
```

`roi_score` and `cat_frequency` drive the triage engine. Assign these from historical CAT paper analysis, not evenly.

### 3.1 VARC — Verbal Ability & Reading Comprehension (24Q / 40min)

**Reading Comprehension (~16Q, 4 passages)** — this is 2/3 of the section, treat it as the priority.
- Passage genres to tag and train separately: Philosophy/Abstract, Economics & Business, Science & Technology, History & Anthropology, Literature & Art Criticism, Sociology & Politics, Environment.
- Question archetypes (tag every RC question with one — this is how you diagnose her weakness): Main Idea / Central Theme; Author's Tone & Attitude; Inference; Direct/Explicit Detail; Vocabulary-in-Context; Structure & Function of a paragraph; Assumption; Strengthen/Weaken; Except/Least-likely (negative questions); Analogy/Application.
- Skills to drill separately: skimming for structure, paraphrasing options, elimination discipline, trap-option recognition (extreme language, out-of-scope, partially true, reversed causality).

**Verbal Ability (~8Q, almost entirely TITA)**
- Para-jumbles (4–5 sentences, TITA — enter the sequence)
- Para-summary (MCQ)
- Odd-sentence-out / Odd-one-out (TITA)
- Para-completion / Sentence insertion
- (Lower priority, occasionally appears): Critical Reasoning, Sentence Correction, Fill in the blanks

### 3.2 DILR — Data Interpretation & Logical Reasoning (20Q / 4 sets / 40min)

**Critical design note:** DILR is not practised question-by-question. It is practised **set-by-set, timed, with a "should I attempt this set?" decision as the first skill.** Build a dedicated Set Player, not a question player, for this section.

- **DI — Tables, Bar/Column, Line, Pie, Stacked, Radar/Spider, Bubble, Combination charts**
- **DI — Caselets** (data given in prose, no chart)
- **DI — Missing/Incomplete data tables** (very common in recent CAT)
- **DI — Data sufficiency**
- **DI — Growth rates, CAGR, indices, market share**
- **LR — Linear & circular arrangements**
- **LR — Distribution / matching / grouping (2D and 3D)**
- **LR — Selection & conditionalities**
- **LR — Ordering & ranking, comparisons**
- **LR — Games & tournaments** (round-robin, knockout, points tables)
- **LR — Scheduling & timetables**
- **LR — Venn diagrams / set-based LR**
- **LR — Network & routes, maxima-minima flow**
- **LR — Binary logic (truth-teller/liar)**
- **LR — Cubes, dice, matrices**
- **LR — Quant-embedded LR** (sets requiring algebra/number properties)
- **LR — Puzzles: number placement, magic squares, Sudoku-like grids**

### 3.3 QA — Quantitative Ability (22Q / 40min)

Weight it as the recent papers do: **Arithmetic is ~40–45% of the section.** Front-load it.

**Arithmetic (highest ROI — teach first)**
- Percentages
- Profit, Loss & Discount
- Simple & Compound Interest, instalments
- Ratio, Proportion & Variation
- Mixtures & Alligation
- Averages & Weighted Averages
- Time, Speed & Distance: relative speed, trains, boats & streams, races, circular tracks
- Time & Work: pipes & cisterns, efficiency, work-wages, chain rule

**Algebra**
- Linear equations, systems, integer solutions
- Quadratic equations: roots, discriminant, sign analysis
- Higher-degree polynomials, remainder & factor theorem
- Inequalities & modulus
- Logarithms
- Surds, indices, simplification
- Functions: composite, inverse, graphs, transformations
- Maxima & Minima (AM-GM, quadratic vertex)
- Progressions: AP, GP, HP, AGP, special series, sum of n terms

**Geometry & Mensuration**
- Lines, angles, parallel lines
- Triangles: congruence, similarity, centres, Pythagorean triples, area formulae
- Quadrilaterals & polygons
- Circles: tangents, chords, cyclic quadrilaterals, sectors
- Coordinate geometry: lines, distance, section formula, circles, loci
- Trigonometry: ratios, identities, heights & distances
- Mensuration 2D & 3D: cube, cuboid, cylinder, cone, sphere, frustum, prism, pyramid, combined solids

**Number System**
- Divisibility rules, factors & multiples
- HCF & LCM
- Remainders: cyclicity, Fermat's little theorem, Euler's totient, Wilson's theorem, Chinese Remainder Theorem
- Number of factors, sum of factors, product of factors
- Base systems / number bases
- Last digit, last two digits, trailing zeroes
- Factorials, highest power of a prime in n!
- Rational/irrational, properties of integers

**Modern Mathematics**
- Permutations & Combinations: arrangements, selections, circular, restrictions, identical objects, distribution/partitioning
- Probability: basic, conditional, independent events
- Set Theory & Venn diagrams
- Binomial theorem (light)
- Logical/quant hybrids, series & sequences

---

## SECTION 4 — PRODUCT SURFACES (what she actually sees)

Build these seven screens. Nothing else in v1.

1. **Today** — the home screen. One primary card ("Continue: Time, Speed & Distance — Relative Motion, 12 min left"), plus a 3-item queue: `Learn → Drill → Review`. A streak counter. A countdown: "112 days to CAT."
2. **Learn** — the lesson reader for a micro-topic: concept notes, worked examples, formula card, common traps, then a "Ready to practise" button that is disabled until she scrolls through / marks the lesson read.
3. **Practice** — the adaptive question player. One question at a time, timer running visibly, options, "Mark for review", solution revealed only after answering, plus a mandatory one-tap **error-reason tag** if she got it wrong.
4. **Mock** — full-screen exam simulator (see Section 9).
5. **Progress** — the mastery map: a grid or tree of all micro-topics coloured by mastery level, plus section-level radar chart, plus accuracy/speed trend lines.
6. **Calendar** — a GitHub-style heatmap of daily activity + the scheduled plan ahead + what she missed and how it got rescheduled.
7. **Review** — the auto-generated mistake notebook and the spaced-repetition queue.

---

## SECTION 5 — DATA MODEL (freeze this first, before any UI)

Write these as TypeScript types **and** JSON Schemas. Add a CI job that validates every content file against the schema on every push. Do this in Milestone 1.

### 5.1 Content types (shipped in repo, read-only)

```ts
type Section = 'VARC' | 'DILR' | 'QA';
type Difficulty = 'easy' | 'medium' | 'hard' | 'very_hard';

interface MicroTopic {
  id: string;                    // 'qa.arith.tsd.circular-tracks'
  name: string;
  section: Section;
  topicId: string;
  prerequisites: string[];
  catFrequency: 'high' | 'medium' | 'low' | 'rare';
  roiScore: 1 | 2 | 3 | 4 | 5;
  estLearnMinutes: number;
  targetSecPerQuestion: number;
}

interface Lesson {
  id: string;
  microTopicId: string;
  bodyMarkdown: string;          // KaTeX-enabled
  workedExamples: WorkedExample[];
  formulaCards: FormulaCard[];   // also feed the SRS deck
  commonTraps: string[];
  estReadMinutes: number;
}

interface Question {
  id: string;                    // stable, content-hash based
  microTopicIds: string[];       // usually 1, can be 2 for hybrids
  section: Section;
  format: 'mcq' | 'tita';
  stemMarkdown: string;
  options?: { key: string; markdown: string }[];   // mcq only
  correctKey?: string;                             // mcq
  correctValue?: string | number;                  // tita; include tolerance
  titaTolerance?: number;
  difficulty: Difficulty;
  eloRating: number;             // item difficulty, seeded from difficulty label
  solutionMarkdown: string;      // step-by-step, MANDATORY, never empty
  altSolutionMarkdown?: string;  // shortcut / smart approach
  targetSeconds: number;
  source: 'official_pyq' | 'generated' | 'authored';
  sourceRef?: string;            // e.g. 'CAT 2023 Slot 2 Q14'
  verification: VerificationRecord;
  tags: string[];                // 'rc:inference', 'trap:extreme-language'
}

interface PassageSet {              // for RC and DILR
  id: string;
  section: 'VARC' | 'DILR';
  kind: 'rc_passage' | 'di_set' | 'lr_set';
  bodyMarkdown: string;
  assets?: { type: 'table' | 'chart'; spec: object }[];  // render charts from data, not images
  questionIds: string[];
  genre?: string;
  wordCount?: number;
  targetMinutes: number;
  licence: string;                 // MANDATORY. see Section 6.
  sourceUrl?: string;
}
```

### 5.2 Learner state types (IndexedDB, mutable)

```ts
interface Attempt {
  id: string; questionId: string; microTopicIds: string[];
  startedAt: number; submittedAt: number; timeSpentSec: number;
  given: string | null;            // null = skipped
  correct: boolean;
  confidence?: 'guess' | 'unsure' | 'sure';   // ask BEFORE revealing answer
  errorTag?: 'concept' | 'calculation' | 'misread' | 'time_pressure'
           | 'careless_option' | 'unknown_formula' | 'guessed';
  mode: 'drill' | 'topic_test' | 'mock' | 'review' | 'warmup';
  markedForReview: boolean;
}

interface MasteryState {
  microTopicId: string;
  status: 'locked' | 'available' | 'learning' | 'practising' | 'mastered' | 'decaying';
  learnerElo: number;
  lastNCorrect: boolean[];         // rolling window of 10
  medianTimeSec: number;
  hardTierCleared: boolean;
  attemptsCount: number;
  masteredAt?: number;
  nextReviewAt?: number;           // SRS
  stability: number; difficulty: number;   // FSRS params
}

interface PlanDay { date: string; items: PlanItem[]; status: 'pending'|'done'|'partial'|'missed'; }
interface MockResult { /* per-section scores, per-question timing, percentile estimate, ... */ }
interface Settings { dailyMinutes: number; examDate: string; weakSectionBias: Section | null; emailOptIn: boolean; }
```

**Rules:** every write goes through the `StorageAdapter`. Every schema gets a `schemaVersion` field and a migration function from day one. Ship an **Export / Import JSON** button in Settings before Milestone 5 — if IndexedDB is cleared, all her work vanishes, and that will happen at least once.

---

## SECTION 6 — CONTENT PIPELINE (this is 80% of the real work — do it first)

**Blunt reality:** the app is a weekend of work; the question bank is the project. A CAT app with 4,000 scraped, unverified, badly-rendered questions is worse than useless — it teaches wrong methods and destroys trust. Target **1,200–1,800 items of verified quality**, not 10,000.

This pipeline is a **separate Python repo/folder (`/pipeline`) that runs offline on the build machine (128 cores, 24 GB A5000)** and emits JSON into `/content`. It never runs in the browser.

**Hard rule — this repo is public: raw source material is never committed.** PYQ PDFs, scraped HTML, third-party solution text, or any other raw ingested material lives only in `/pipeline/raw/`, which is gitignored. Nothing under it ever reaches a commit. The only thing that leaves `/pipeline` and enters version control is pipeline-*generated* JSON written to `/content/`, and every asset there must carry a non-empty `licence` field or the CI content validator fails the build. If you're unsure whether a file counts as "raw," it stays out of git.

### 6.1 Sourcing — the legal and practical hierarchy

**Tier 1 — Official CAT previous-year papers.** ~~The IIMs publish the actual question papers and answer keys after each exam, and they circulate as public PDFs.~~ **Correction (verified during Milestone 3, see PROGRESS.md): this is not accurate.** IIM CAT never releases a standalone question-paper PDF. The only official view of real questions is the response-sheet/answer-key page, gated behind each individual candidate's own CAT login (User ID + password), live only for a ~3-day post-exam objection window. The yearly official mock test — also built from real PYQs — has the same login gate and is only live for ~2 weeks before the exam. Nothing here is a freely, currently downloadable public PDF. What *is* freely available everywhere is coaching-site content (2IIM, Cracku, CatKing, Testbook, ...) — scraping that remains forbidden, unchanged, per the "What NOT to do" list below; a public GitHub repo is not the place to take that risk regardless of who requests it. Treat Tier 1 as **opportunistic, not planned**: if the project owner has legitimately-obtained past papers (their own response sheet, a book they own) to hand over directly, ingest those; otherwise this tier is likely unreachable and Tier 3 (§6.3) is the realistic primary source for QA/DILR. Do not build a scraper against coaching sites to compensate.

**Tier 2 — Open-licence source text for RC passages.** Do **not** generate RC passages with an LLM — CAT RC is drawn from real published non-fiction and LLM prose is too clean, too structured, and trains the wrong reading reflexes. Instead ingest genuinely reusable text:
- Project Gutenberg / Wikisource (public domain essays, history, philosophy)
- arXiv, PLOS, DOAJ, bioRxiv (open-access science — excellent for the Science/Tech genre)
- Government and multilateral reports: RBI, NITI Aayog, Economic Survey, World Bank, IMF, UN, OECD (public/permissive — check each)
- Wikipedia (CC BY-SA — attribute)
- Open-access humanities journals and CC-licensed long-form
Then **generate the questions on top of that real prose.** That is the legally clean and pedagogically correct split: real passages, synthesised questions.

**Tier 3 — Synthesised QA/DILR items.** Generate variants and novel items with the local LLM, verified as in 6.3.

**What NOT to do — and this is not optional advice:**
- Do **not** scrape coaching sites (TIME, IMS, Career Launcher, 2IIM, Cracku, Handa Ka Funda, Bodhee, Oliveboard, etc.). Their questions and solutions are copyrighted commercial assets, their ToS prohibit it, and **a public GitHub repo full of their content is a DMCA takedown waiting to happen** — GitHub will disable the repo, and the link you sent her will die.
- Do not attempt to defeat Cloudflare, login walls, or CAPTCHAs. If a site is protected, it is not a source.
- Do respect `robots.txt` and `Crawl-delay`, set a real User-Agent with a contact address, cap concurrency at 1–2 req/s per host.
- Record a `licence` field on **every** ingested asset. If it's blank, the CI validator rejects it. This forces the discipline.
- If you cannot get a clean licence for something valuable, keep it in a **private** repo and deploy the app from a separate public repo containing only clean content. Or keep the whole repo private and deploy via GitHub Pages from a private repo (available on Pro) or Cloudflare Pages.

### 6.2 PDF → structured question ingestion

For official PYQ PDFs (the highest-value and hardest step):

1. **Layout-aware extraction.** Try in this order and keep whichever wins per-file: `pymupdf` (fast, good text), `pdfplumber` (tables and word boxes), then a document-AI model — `marker-pdf` or `nougat` — for pages with heavy math or diagrams. The A5000 makes these viable at scale.
2. **Math handling.** Convert equations to LaTeX. Where extraction is unreliable, **rasterise the question region to PNG at 300 dpi and keep it as a fallback image** alongside the text — a correct image beats mangled LaTeX.
3. **Diagram handling.** Geometry and DI figures will not extract as text. Crop them as images, store in `/content/assets/`, reference by ID. For DI charts where the underlying numbers are recoverable, **re-encode as data + a chart spec** so they render responsively; use images only when you must.
4. **Segmentation.** Regex + LLM hybrid: detect `Q.\d+`, option markers `(A)/(1)/a.`, "Directions for questions X to Y" blocks (these define passage sets). Emit a draft `Question` / `PassageSet`.
5. **Answer key join.** Parse the official key PDF separately and join on question number + slot. Any question without a matched key is quarantined, not shipped.
6. **Human review UI.** Build a tiny local React or Streamlit app: shows the rendered question next to the original PDF crop, with Approve / Fix / Reject. At ~15–20 seconds per item, reviewing 1,000 items is about 5 hours. Budget it. This is the step everyone skips and it is the step that determines whether the app is good.

### 6.3 LLM generation + verification (where the A5000 earns its place)

Serve a local model with **vLLM** on the A5000. At 24 GB, good fits: `Qwen2.5-32B-Instruct-AWQ` (4-bit), `Qwen3-30B-A3B` (MoE, fast), or `Mistral-Small-24B-Instruct` quantised. Batch aggressively; the 128 cores handle pre/post-processing and the SymPy verification in parallel.

**The verification loop is the whole point. Never ship an unverified item.**

For **QA items** — this is the killer technique, insist on it:
1. Prompt the model to emit, together: the question stem, options, the claimed answer, a step-by-step solution, **and a self-contained Python/SymPy program that computes the answer from the stem's given values.**
2. Execute that program in a sandboxed subprocess with a timeout.
3. **Accept only if the program's output equals the claimed answer.** Mismatch → discard, don't repair.
4. Independently, sample **5 solutions at temperature 0.8** and require ≥4 to agree on the same final answer (self-consistency).
5. Run a **distractor audit** pass: a second call checks that no distractor is also correct, options are mutually exclusive, units are consistent, and the answer isn't guessable from option structure alone (e.g., the only option with a different magnitude).
6. **Deduplicate** against the entire bank using embedding cosine similarity (>0.92 = duplicate) plus a normalised-numbers hash to catch trivial re-skins.

For **RC/VARC items**: verification is harder, so use a different gate — a separate "answerability" pass where the model, given *only the passage and the question* (never the intended answer), must independently select the same option in 4 of 5 samples. Also require the model to quote the exact sentence span in the passage that justifies the answer, and reject if that span doesn't exist verbatim. Ambiguous items get quarantined for human review.

For **DILR sets**: generate the set's underlying data table programmatically first (Python), derive the questions from the data deterministically, and let the LLM only write the natural-language framing. **Never let the LLM invent the numbers** — it will produce inconsistent sets. This inverts the usual approach and it is the correct one.

### 6.4 Difficulty calibration

Do **not** trust an LLM's difficulty label. Compute a composite:
- **Anchor on official PYQs.** Use known CAT-item difficulty (from published slot analyses, or from solve-step counts) to define the scale.
- Empirical proxies: number of distinct concepts invoked, number of solution steps, presence of a non-obvious shortcut, magnitude of arithmetic burden, whether a brute-force path exists.
- Seed each item's `eloRating` from that composite (`easy` 1000, `medium` 1200, `hard` 1400, `very_hard` 1600).
- **Then let it self-correct at runtime:** every attempt updates both the item Elo and her Elo (Section 8). After a few hundred attempts the labels become empirically honest. This is far better than a static tag and costs ~30 lines of code.

### 6.5 Target bank composition

| Section | Items | Notes |
|---|---|---|
| QA | 700–900 | ≥30 per micro-topic; skew toward Arithmetic |
| DILR | 120–160 **sets** (≈500–650 Q) | sets, not loose questions |
| VARC — RC | 60–80 passages (≈250–320 Q) | spread across all 7 genres |
| VARC — VA | 200–250 | para-jumbles, summary, odd-one-out |
| **Every item** | — | has a full step-by-step solution. No exceptions. |

---

## SECTION 7 — TECH STACK (use exactly this unless you have a concrete reason)

**Frontend**
- React 18 + **TypeScript (strict)** + **Vite**
- Tailwind CSS + shadcn/ui (Radix primitives — accessible by default)
- **Zustand** for state (Redux is overkill here), **TanStack Query** only if/when a backend arrives
- **React Router with `HashRouter`** — this avoids the GitHub Pages 404-on-refresh trap. If you insist on `BrowserRouter`, you must add the `404.html` redirect shim; hash routing is simpler and fine here.
- **Dexie.js** over IndexedDB
- **KaTeX** (`react-katex`) for math — not MathJax, KaTeX is far faster
- **Recharts** for analytics charts; **`react-calendar-heatmap`** or a hand-rolled SVG grid for the calendar
- `vite-plugin-pwa` (Workbox) for the service worker + install prompt
- `date-fns` for dates. Pin everything to **Asia/Kolkata** for day boundaries — a "day" must roll over at midnight IST, not UTC, or her streak will break at 5:30 AM.
- **`json-schema-to-typescript`** (dev dependency, Milestone 1) — generates `app/src/types/content.ts` from `/content/schemas/*.json`, which are themselves generated from `/pipeline/schemas.py`. `pipeline/schemas.py` (pydantic v2) is the single source of truth for shipped-content types; never hand-edit either generated output. See PROGRESS.md for the full flow and the CI drift check.

**Content pipeline**
- Python 3.11+, `pydantic` v2 for schemas, `vllm`, `sympy`, `pymupdf`, `pdfplumber`, `marker-pdf`, `sentence-transformers` (dedup), `httpx` + `tenacity` for polite fetching, `pytest`

**CI/CD**
- GitHub Actions: `lint → typecheck → schema-validate-content → vitest → build → deploy to gh-pages`
- **Content validation must fail the build.** Missing solution, missing licence, unverified item, broken KaTeX, orphan `microTopicId` → red build.

**Phase 2 backend (optional but recommended, see Section 12)**
- **Supabase** free tier: Postgres + Row Level Security + magic-link auth + Edge Functions
- **Resend** (free tier) for transactional email
- GitHub Actions `schedule:` cron for the daily nudge job

---

## SECTION 8 — THE LEARNING ENGINE (the actual product)

### 8.1 Topic lifecycle state machine

```
locked → available → learning → practising → mastered → (decaying) → practising
```

- `locked`: prerequisites not yet mastered. Show it, greyed, with "Unlocks after: Percentages."
- `available`: prerequisites met, not started.
- `learning`: lesson opened, fewer than 8 attempts logged.
- `practising`: drilling, mastery threshold not met.
- `mastered`: threshold met (below).
- `decaying`: mastered, but `nextReviewAt` has passed and no recent contact. Auto-injects into the review queue.

### 8.2 Mastery criterion — "until she understands it"

You asked for the app to keep drilling until she understands. Define it precisely; **do not use a simple accuracy percentage**, because it lets her pass by grinding easy items slowly.

Promote to `mastered` only when **all four** hold:
1. **Accuracy:** ≥ 75% over the last 10 attempts in this micro-topic (minimum 12 lifetime attempts).
2. **Speed:** median time on the last 10 ≤ `targetSecPerQuestion × 1.25`. A correct answer that takes 4 minutes is a wrong answer in CAT.
3. **Ceiling proof:** at least 2 items of `hard` or `very_hard` answered correctly. Otherwise she's mastered "easy percentages," not percentages.
4. **Retention:** one successful review ≥ 3 days after criteria 1–3 were first met. Mastery isn't real until it survives a gap.

Between criteria 3 and 4 the status is `practising (pending retention)` — show that honestly in the UI.

**Anti-frustration valve (important, do not skip):** if she fails to reach threshold after 30 attempts, or accuracy is <40% after 15, **do not keep grinding.** Stop, show "This one needs a rewatch, not more reps," route her back to the lesson with the specific sub-concept her error tags cluster around, and offer a prerequisite refresher. Infinite grinding on a topic she doesn't understand is how people quit.

### 8.3 Adaptive item selection

Elo, both sides. Simple, robust, ~40 lines.

```
expected  = 1 / (1 + 10^((itemElo − learnerElo)/400))
learnerElo += K_L * (actual − expected)          // K_L ≈ 24, decaying to 12 after 200 attempts
itemElo    += K_I * (expectedItem − actualItem)  // K_I ≈ 8, small: items should be stable
```

**Selection policy for a drill queue of 10:**
- 60% items with `itemElo` in `[learnerElo − 50, learnerElo + 100]` — the productive-struggle band, target ~70% success
- 20% deliberately above her level (`+150 to +300`) — ceiling stretch
- 10% below (`−200`) — confidence and fluency
- 10% **interleaved from earlier mastered/decaying topics** — this is non-negotiable; blocked practice feels better and teaches worse. Interleaving is one of the most replicated findings in learning science.
- Never repeat an item she answered correctly within the last 14 days unless it's an SRS review.

### 8.4 Spaced repetition

Use **FSRS** (`ts-fsrs` npm package) if you want the best available scheduler; **SM-2** is acceptable if you want zero dependencies. Apply it at two levels:
- **Micro-topic level** — schedules the "decaying → review" cycle.
- **Card level** — formula cards, vocabulary-in-context cards, and every question she got wrong (auto-added as a card).

### 8.5 The error taxonomy (your diagnostic edge)

After any wrong answer, before showing the solution, force a one-tap tag:

| Tag | System response |
|---|---|
| **Conceptual gap** | Link the exact lesson section; reduce topic mastery estimate hard |
| **Calculation error** | Queue a 60-second mental-math drill; do not reduce mastery much |
| **Misread the question** | Enable "highlight the ask" mode for the next 20 questions |
| **Ran out of time** | Feed into the pacing trainer; flag for shortcut-method lesson |
| **Careless option pick** | Trigger elimination-discipline drill |
| **Didn't know formula** | Auto-add the formula card to the SRS deck |
| **Guessed (got it right)** | **Also ask this on correct answers via the confidence prompt** — a lucky guess must not count as mastery |

That last row matters: capture `confidence` **before** revealing the answer, and treat "correct + guess" as ~0.4 of a correct answer in the mastery calculation. Most apps count it as a full win and overestimate readiness.

---

## SECTION 9 — MOCK TEST ENGINE

### 9.1 Full mocks — 5 required

Each is 66 questions / 120 minutes / three hard-locked 40-minute sections in order VARC → DILR → QA.

Must replicate the real interface faithfully:
- Full-screen, exit warning on attempted navigation away, `beforeunload` guard
- Per-section countdown; auto-submit and auto-advance at 0:00 with a 10-second warning
- **No back-navigation to a completed section.** Enforce it.
- Question palette in the real CAT colour convention: Not Visited (grey), Not Answered (red), Answered (green), Marked for Review (purple), Answered & Marked (purple with tick)
- Buttons: `Save & Next`, `Clear`, `Mark for Review & Next`
- TITA questions get a numeric input, not options
- **Basic on-screen calculator only.** Four functions plus percent and square root at most. Draggable.
- **Silently record per-question dwell time and visit count** — this is the goldmine for post-mock analysis
- Crash recovery: persist mock state to IndexedDB every 5 seconds; on reload, resume with the correct remaining time

Compose the 5 full mocks to escalate: Mock 1 slightly easier than CAT, Mocks 2–4 at CAT level, Mock 5 harder. Draw from the item bank with **no overlap** with items she has seen in drills — maintain a `mock_reserved` flag on items so the drill engine can never serve them.

### 9.2 Sectional mocks — 5 required

Actually build more than 5: 5 is the stated minimum but sectional practice is where sections get fixed. Ship 5 × VARC (40 min, 24Q), 5 × DILR (40 min, 4 sets), 5 × QA (40 min, 22Q) if the bank allows; 5 total if not.

### 9.3 Post-mock analysis — do this properly, it's the highest-value screen in the app

Generate automatically, no configuration:

- **Score & estimated percentile.** Be honest about the method: you have no cohort, so map raw score → percentile using **published historical CAT scaled-score-to-percentile tables** (they're widely reported each year) and label it clearly as *"Estimated from historical CAT data — indicative only."* Do not invent a percentile and present it as fact.
- **Time-allocation waterfall** — minutes spent per section vs. marks earned per section.
- **The "Bleeder" report** — questions where she spent >150 seconds and got it wrong. In CAT these are the single biggest source of lost marks. Show them first, ranked by time wasted.
- **Selection quality score** — of the questions she *skipped*, what fraction were actually easy (low itemElo)? High = poor selection. This directly trains the most important CAT skill.
- **TITA discipline check** — did she leave any TITA blank? There is no negative marking; leaving one blank is a pure unforced error. Flag every instance loudly.
- **Accuracy vs. attempts curve** — the classic "should you have attempted 18 or 22?" analysis. Compute what her score *would* have been at each attempt count given her accuracy profile, and show the optimum.
- **Micro-topic damage report** — which topics cost her marks, with one-click "add to practice queue."
- **Auto-generated remediation plan** — the mock's output *must* write back into the plan. A mock that doesn't change tomorrow's schedule is a wasted mock.

---

## SECTION 10 — PLANNER, CALENDAR & TRIAGE

### 10.1 Plan generation

Inputs: exam date (29 Nov 2026), today, `dailyMinutes` (ask once, default 90), diagnostic results.

**Start with a 45-minute diagnostic** on first launch — ~15 questions spanning sections and difficulty, used to seed `learnerElo` per section and to identify starting topics. Do not make her start at "Percentages" if she's already good at arithmetic.

Then generate the plan by **ROI-weighted topological sort**: respect prerequisites, order by `roiScore × catFrequency × (1 − currentMastery)`, and pack into daily budgets.

Reserve, non-negotiably:
- **Sunday = mock day** from week 3 onward (mocks are on the real slot timing — schedule them at 08:30 IST to match Slot 1)
- **20% of every day for review/SRS**, not new material
- **Last 3 weeks = revision + mocks only**, no new topics. Hard-code this cutoff.

### 10.2 Triage — the compressed-timeline feature

With ~16 weeks, full coverage may not be achievable. The planner must be willing to say so. Show a **Coverage Forecast**: "At 90 min/day you will cover 78% of high-ROI topics by 29 Nov. Recommended: drop [Trigonometry heights & distances, Binary logic, Base systems] — 4% of CAT marks, 11 hours of study."

That honesty is a feature. Most apps pretend everything is coverable and she runs out of time having half-learned everything.

### 10.3 Missed days

Do not let missed days pile into guilt. If she misses a day:
- Auto-redistribute across the next 5 days, capped at +25% daily load
- If the deficit exceeds what redistribution can absorb, **drop the lowest-ROI item and tell her plainly** what was dropped and why
- Never show a red "3 days behind!" banner. Show "Plan updated — here's today."
- Streak logic should have one free "rest day" per week that doesn't break the streak

### 10.4 Calendar screen

Heatmap (GitHub-style, minutes-studied intensity), tap a day → what she did / what was planned. Forward view shows the schedule. Add exam-date and registration-deadline markers.

---

## SECTION 11 — NOTIFICATIONS & EMAIL

**Design principle: encouraging, never nagging.** She did not ask to be monitored. An app that emails "you're falling behind" gets deleted, and it's a bad thing to do to someone you care about. Every email must be opt-in, must have a one-click off switch in the app, and should read like a helpful note, not a compliance report.

**Phase 1 (static-only, works on GitHub Pages):**
- **Web Push via service worker** for the daily nudge — works offline, no backend needed for local notifications scheduled by the SW
- In-app "Today" card is the primary mechanism

**Phase 2 (with Supabase):**
- GitHub Actions cron (`0 3 * * *` UTC = 08:30 IST) → calls a Supabase Edge Function → reads her synced progress → sends via Resend
- **Daily (morning):** "Today: Time & Work — Pipes & Cisterns. 35 min. [Open]" — one topic, one link, nothing else
- **Topic-complete:** a genuine congratulation with the mastery stat and what unlocked next
- **Weekly Sunday digest:** minutes studied, topics mastered, accuracy trend, next week's plan, one specific insight ("Your DILR accuracy is up 12% — the set-selection drills are working")
- **Mock reminder** the evening before
- **Milestone emails:** 100 days out, 50, 30, 14, 7, 1 — with what to focus on at that stage
- Never more than one email per day. Hard-limit it in code.

---

## SECTION 12 — DEPLOYMENT (read carefully, this is where the plan breaks)

**The problem with your stated plan:** GitHub Pages serves static files only. It cannot run a database, cannot send email, and cannot sync between her phone and laptop. Progress lives in one browser's IndexedDB — if she clears site data, uses incognito, or switches devices, everything is gone.

**Three options, pick one:**

**A. Pure GitHub Pages (simplest, ship this first)**
Static build, IndexedDB, service-worker notifications, manual JSON export/import for backup. Zero cost, zero infrastructure, works today. Limitation: single-device, no progress-aware email.

**B. GitHub Pages + Supabase (recommended)**
Frontend still on Pages. Supabase free tier holds progress; magic-link auth; Edge Function sends email; GitHub Actions cron triggers it. Multi-device sync, progress-aware emails, real backup. Cost: ₹0 on free tiers. Extra work: ~1 milestone. **Do this — the sync alone justifies it.**

**C. Cloudflare Pages / Vercel free tier**
If you want serverless functions in the same deployment as the frontend, this is cleaner than Pages + Supabase. Also gives you a nicer URL. Still free. GitHub remains the source repo.

**Whichever you choose, configure correctly:**
- `vite.config.ts` → `base: '/repo-name/'` (this is the #1 cause of a blank white page on Pages)
- `HashRouter`, or a `404.html` SPA shim
- Custom domain optional but a big UX win — a real domain feels like a real product, not a hobby link
- GitHub Action deploys `dist/` to `gh-pages` on push to `main`
- Set a `CONTENT_VERSION` constant; on version bump the service worker must invalidate cached content but **must never wipe learner data**. Test this explicitly.

---

## SECTION 13 — UI/UX SPECIFICATION

- **Aesthetic:** calm and focused. This is a study tool used under stress for four months. Dark mode default, warm neutral palette, one accent colour. No neon, no confetti explosions, no aggressive gamification.
- **Typography:** a proper reading font for RC passages (Charter, Source Serif, or Literata) at ~18px / 1.7 line-height. RC is 25% of the exam and she'll read for hours — this matters more than it sounds.
- **Timers:** always visible but visually quiet. Turn amber at 1.5× target, red at 2.5×. Never flash or beep — panic is a learned behaviour and you don't want to teach it.
- **Solutions:** step-by-step, collapsible, with the "smart approach" shown separately from the "textbook approach." CAT is won by the smart approach.
- **Empty states:** every screen needs a good one. "No mistakes to review yet — go break something."
- **Accessibility:** keyboard navigation throughout (mock keys: `1-4` select, `Enter` save & next, `M` mark), ARIA labels, respects `prefers-reduced-motion`.
- **Micro-delight, used sparingly:** a topic-mastered animation, a streak flame, a countdown that feels like an ally not a threat. One personal touch is worth more than ten features — e.g. a short encouraging line on the Today card that changes weekly.

---

## SECTION 14 — ADDITIONAL FEATURES (build in this priority order after core)

1. **Mistake Notebook** — auto-populated, filterable by error tag and topic, with "re-attempt this set" (highest value; build it early)
2. **Daily Warm-up** — 10 mixed questions, 8 minutes, first thing. Builds the habit.
3. **Formula & Vocabulary SRS deck** — swipeable cards, FSRS-scheduled
4. **Skip Trainer** — a timed mode where the *goal* is to correctly classify 20 questions as "attempt / skip" in 5 minutes without solving them. Scores selection ability directly. Nobody builds this and it's one of the highest-ROI CAT skills.
5. **Sectional Pacing Trainer** — VARC: read a passage and answer 4 questions in 8:30 with a visible pace bar
6. **RC Reading Habit** — one open-licence long-form article daily with 3 auto-generated questions; tracks reading speed in WPM over time
7. **Concept Map view** — the prerequisite DAG rendered as an interactive graph, coloured by mastery. Visually satisfying and genuinely useful for orientation.
8. **Printable revision sheets** — per-topic formula PDF, generated client-side
9. **"Explain differently" button** — if she gets an item wrong twice, offer an alternative explanation (pre-generated at pipeline time, second variant per solution — do *not* call an LLM at runtime; you'd need an API key in the client, which is a hard no)
10. **Progress report PDF export** — one page, shareable
11. **Weak-topic sprint** — auto-generated 20-question set from her three weakest micro-topics
12. **Exam-day simulation** — full mock at 08:30 IST, with a pre-exam checklist screen

**Deliberately excluded (do not build):** leaderboards, social feeds, streaks that punish, AI chatbot tutor in v1 (needs a runtime key), video content, discussion forum, anything with a login for other users.

---

## SECTION 15 — BUILD MILESTONES (one per Sonnet session)

Maintain `PROGRESS.md` in the repo. Update it at the end of every milestone with what was built, what was deferred, and any schema changes. Start every session by reading `SPEC.md` and `PROGRESS.md`.

| # | Milestone | Definition of done |
|---|---|---|
| 0 | Repo scaffold | Vite + TS + Tailwind + shadcn, CI green, deploys a "hello" page to GitHub Pages successfully. **Verify the live URL loads before proceeding.** |
| 1 | Schemas & syllabus | All TS types + JSON Schemas from §5; complete `syllabus.json` with every micro-topic from §3; CI validates content |
| 2 | Storage layer | `StorageAdapter` interface, `DexieAdapter`, migrations, export/import JSON, unit tests |
| 3 | Content pipeline v1 | `/pipeline` ingests official PYQ PDFs → validated JSON for ≥200 QA questions with solutions; review UI works |
| 4 | Question Player | Renders MCQ + TITA + KaTeX + images, timer, confidence prompt, error tagging, solution reveal, logs `Attempt` |
| 5 | Mastery engine | Elo, mastery criteria, state machine, adaptive selection, anti-frustration valve — with unit tests on the algorithm |
| 6 | Lesson reader + Learn→Drill loop | One micro-topic fully playable end to end. **Stop and demo this before scaling content.** |
| 7 | Content pipeline v2 | LLM generation + SymPy verification + self-consistency + dedup; bank to ≥800 items |
| 8 | Passage/Set player | RC passages and DILR sets with the set-level timer and "attempt/skip" decision step |
| 9 | Planner + Calendar | Diagnostic, plan generation, triage forecast, heatmap, missed-day redistribution |
| 10 | Mock engine | Full CAT simulator, section locking, palette, calculator, crash recovery |
| 11 | Mock analytics | All reports from §9.3, remediation written back into the plan |
| 12 | Review & SRS | Mistake notebook, FSRS scheduling, formula deck |
| 13 | Content pipeline v3 | RC passages from open-licence sources; VARC bank complete; DILR sets to target |
| 14 | 5 full + 5 sectional mocks | Assembled, reserved from the drill pool, difficulty-graded |
| 15 | PWA + notifications | Service worker, install prompt, offline verified, web push |
| 16 | Supabase sync + email | `SupabaseAdapter`, magic-link auth, Edge Function, GH Actions cron, all email templates |
| 17 | Polish | Empty states, animations, accessibility audit, Lighthouse ≥90, real-device testing on her phone model |

---

## SECTION 16 — ACCEPTANCE CRITERIA

The build is not done until all of these pass:

- [ ] Live GitHub Pages URL loads on a phone and installs as a PWA
- [ ] Airplane mode: full drill session works, syncs on reconnect
- [ ] Every shipped question has a non-empty step-by-step solution — assert this in CI
- [ ] Every shipped asset has a `licence` field — assert this in CI
- [ ] Zero KaTeX render errors across the entire bank (automated check)
- [ ] A full mock can be completed with a mid-mock browser crash and resumed with correct remaining time
- [ ] Clearing the cache does not delete learner progress; a content update does not delete learner progress
- [ ] Export → clear all data → import restores exact state
- [ ] Mastery engine unit tests cover: lucky-guess handling, speed failure, hard-tier requirement, retention gap, anti-frustration exit
- [ ] Lighthouse: Performance ≥90, Accessibility ≥95
- [ ] Full keyboard operability of the mock player
- [ ] Every micro-topic in `syllabus.json` has ≥1 lesson and ≥15 questions, or is explicitly marked `coverage: partial` and excluded from the plan

---

## SECTION 17 — INSTRUCTIONS TO YOU, SONNET

- **Do not build everything at once.** Implement only the milestone named in the current message.
- **Ask before assuming** on: schema changes, adding a dependency not listed in §7, deviating from the mastery criteria in §8.2.
- **Write tests for the algorithms** (Elo, mastery, planner, scoring). UI tests are optional; algorithm tests are not — these are the parts that are silently wrong.
- **Never ship a placeholder question, a `TODO` solution, or lorem ipsum content.** Missing content is fine; fake content is not.
- **Never put an API key in client code.** If a feature needs one, it belongs in the offline pipeline or an Edge Function.
- **Prefer boring, correct code.** This will be maintained by a non-expert under time pressure.
- **When content and code conflict, fix the content.** Code should never special-case a bad question.
- At the end of each milestone, output: what you built, what you deferred, what you'd change in the spec, and the exact commands to run it locally.
