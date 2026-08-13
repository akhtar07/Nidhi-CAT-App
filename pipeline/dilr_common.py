"""
Shared machinery for the DILR set generators (content pipeline v5).

## Why this exists

Each earlier DILR generator (`build_dilr_di_line_charts.py` and friends) was a standalone
script that hand-rolled its own ids, its own Question construction and its own emit loop.
That was fine at one set per topic. Bringing every DILR topic up to SPEC.md §16's bar of 15
questions needs ~50 sets, and copying that boilerplate 50 times would mean 50 chances to
mistype an elo, forget a `licence`, or let an MCQ ship with a distractor equal to the key.

So the boilerplate lives here once, and the per-topic scripts contain only the thing that
actually differs: the data and the questions asked of it.

## The safety rules this module enforces

Construction-time, so a violation is a crash during generation rather than a bad question
in front of the learner:

- an MCQ's key must appear exactly once among its options (no duplicate-answer sets),
- an MCQ needs at least 4 options,
- a TITA answer must be finite,
- every question carries a non-empty solution,
- set ids and question ids are content-hashed, so re-running is idempotent and a set whose
  data has not changed keeps the ids any composed mock already references.

## Verification stance

`verify_dilr_batch5.py` re-derives every answer from the *shipped JSON* — the chart spec as
the learner's browser will receive it — using separately written arithmetic. That is a
weaker guarantee than the sympy-against-closed-form independence the QA templates get, and
it is recorded honestly: these items carry `method="self_consistency"` unless a genuinely
independent route (brute-force search over the whole solution space) was used, which is the
case for every LR puzzle, where the answer comes from an exhaustive enumeration that never
consults the intended reasoning chain.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from schemas import PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
VERIFIED_AT = "2026-08-13T00:00:00Z"

# Seeded from the difficulty label per SPEC.md §6.4, matching the earlier DILR generators.
ELO_BY_DIFFICULTY = {"easy": 1050.0, "medium": 1200.0, "hard": 1350.0, "very_hard": 1500.0}


_PIPE_TABLE = re.compile(r"^\s*\|", re.MULTILINE)
_LONE_ITALIC = re.compile(r"(?<!\*)\*(?!\*)[^*\n]+(?<!\*)\*(?!\*)")


def _check_markdown(field: str, text: str, stem: str) -> None:
    """Rejects markdown the app cannot render.

    `markdownSegments.ts` implements a deliberately minimal tokenizer — inline and block math,
    `**bold**`, headings, lists and images, and nothing else. Anything outside that set does not
    fail loudly in the browser; it renders as literal source text in front of the learner, which
    is why this has to be caught at build time. Single-asterisk italics are the easy mistake,
    since every other markdown tool in the world supports them.
    """
    if _PIPE_TABLE.search(text):
        raise ValueError(f"{field} uses a pipe table, which the tokenizer cannot render: {stem!r}")
    match = _LONE_ITALIC.search(text)
    if match:
        raise ValueError(
            f"{field} uses single-asterisk italics {match.group()!r}, which render literally — "
            f"use **bold**: {stem!r}"
        )
    if text.count("$") % 2 != 0:
        raise ValueError(f"{field} has an unbalanced $ delimiter: {stem!r}")


@dataclass
class QSpec:
    """One question. Either `value` (TITA) or `options` + `correct` (MCQ) must be set."""

    stem: str
    solution: str
    difficulty: str
    target_seconds: int
    value: float | None = None
    tolerance: float = 0.0
    options: list[str] | None = None
    correct: str | None = None
    """The option *text* that is correct — not its letter. Letters are assigned on emit, so
    reordering options can never silently detach the key from the intended answer."""

    def __post_init__(self) -> None:
        if self.difficulty not in ELO_BY_DIFFICULTY:
            raise ValueError(f"unknown difficulty {self.difficulty!r}")
        if not self.solution.strip():
            raise ValueError(f"empty solution for {self.stem!r}")
        for field, text in (("stem", self.stem), ("solution", self.solution)):
            _check_markdown(field, text, self.stem)
        if self.options is None:
            if self.value is None:
                raise ValueError(f"TITA question needs a value: {self.stem!r}")
            if not math.isfinite(self.value):
                raise ValueError(f"non-finite TITA value for {self.stem!r}")
        else:
            if self.correct is None:
                raise ValueError(f"MCQ needs `correct`: {self.stem!r}")
            if len(self.options) < 4:
                raise ValueError(f"MCQ needs >= 4 options: {self.stem!r}")
            if len(set(self.options)) != len(self.options):
                raise ValueError(f"MCQ has duplicate options: {self.stem!r}")
            if self.options.count(self.correct) != 1:
                raise ValueError(f"MCQ key {self.correct!r} not uniquely among options: {self.stem!r}")


@dataclass
class SetPlan:
    micro_topic: str
    slug: str
    """Distinguishes sets within a topic. Feeds the content hash, so it must be stable."""
    body: str
    questions: list[QSpec]
    assets: list[dict] = field(default_factory=list)
    kind: str = "di_set"
    target_minutes: float = 8.0
    extra_topics: list[str] = field(default_factory=list)
    """Secondary micro-topics this set also drills, e.g. a growth set that is also a bar chart."""
    verification_method: str = "self_consistency"


def set_id_for(micro_topic: str, slug: str) -> str:
    digest = hashlib.sha1(f"{micro_topic}|{slug}".encode()).hexdigest()[:8]
    return f"{micro_topic}.set-{digest}"


def _to_question(plan: SetPlan, set_id: str, index: int, q: QSpec) -> Question:
    topic_ids = [plan.micro_topic, *plan.extra_topics]
    tag = plan.micro_topic.split(".")[-1]
    common = {
        "id": f"{set_id}.q{index}",
        "microTopicIds": topic_ids,
        "section": "DILR",
        "stemMarkdown": q.stem,
        "difficulty": q.difficulty,
        "eloRating": ELO_BY_DIFFICULTY[q.difficulty],
        "solutionMarkdown": q.solution,
        "targetSeconds": q.target_seconds,
        "source": "generated",
        "verification": VerificationRecord(method=plan.verification_method, verifiedAt=VERIFIED_AT),
        "tags": [f"dilr:{tag}"],
    }
    if q.options is None:
        return Question(format="tita", correctValue=q.value, titaTolerance=q.tolerance, **common)
    keys = [chr(65 + i) for i in range(len(q.options))]
    return Question(
        format="mcq",
        options=[QuestionOption(key=k, markdown=text) for k, text in zip(keys, q.options)],
        correctKey=keys[q.options.index(q.correct)],
        **common,
    )


def emit(plan: SetPlan) -> str:
    """Writes one passage set and its questions. Returns the set id."""
    set_id = set_id_for(plan.micro_topic, plan.slug)
    questions = [_to_question(plan, set_id, i + 1, q) for i, q in enumerate(plan.questions)]

    passage_set = PassageSet(
        id=set_id,
        section="DILR",
        kind=plan.kind,
        bodyMarkdown=plan.body,
        assets=plan.assets or None,
        questionIds=[q.id for q in questions],
        genre=None,
        wordCount=None,
        targetMinutes=plan.target_minutes,
        licence="CC0-1.0",  # Original synthetic data — nothing third-party to attribute.
        sourceUrl=None,
    )

    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    PASSAGE_SETS_DIR.mkdir(parents=True, exist_ok=True)
    for q in questions:
        (QUESTIONS_DIR / f"{q.id}.json").write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
    (PASSAGE_SETS_DIR / f"{set_id}.json").write_text(
        json.dumps(json.loads(passage_set.model_dump_json()), indent=2) + "\n"
    )
    return set_id


def emit_all(plans: list[SetPlan]) -> None:
    by_topic: dict[str, int] = {}
    for plan in plans:
        emit(plan)
        by_topic[plan.micro_topic] = by_topic.get(plan.micro_topic, 0) + len(plan.questions)
    for topic, count in sorted(by_topic.items()):
        print(f"  {topic}: +{count} questions")
    print(f"Wrote {len(plans)} sets, {sum(by_topic.values())} questions")


# ---------------------------------------------------------------------------
# Formatting helpers shared by the solution text
# ---------------------------------------------------------------------------


def fmt(x: float) -> str:
    """Trims a float to its shortest exact-looking form, so solutions read `12` not `12.0`."""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))
    return f"{round(x, 2):g}"


def pct_change(old: float, new: float) -> float:
    return (new - old) / old * 100


def series_table(categories: list[str], rows: dict[str, list[float]]) -> str:
    """Renders data as a markdown-free list, because the app's markdown tokenizer has no pipe
    tables (see markdownSegments.ts) and `check_markdown` rejects them outright."""
    lines = []
    for name, values in rows.items():
        pairs = ", ".join(f"{c} {fmt(v)}" for c, v in zip(categories, values))
        lines.append(f"- {name}: {pairs}")
    return "\n".join(lines)


def numeric_distractors(answer: float, deltas: list[float], count: int = 4) -> list[str]:
    """Builds MCQ options around a numeric answer, keeping them distinct and ordered.

    Distractors come from `deltas` — each should correspond to a *specific* plausible mistake
    (dropping a term, using the wrong base for a percentage), not a random nudge, per SPEC.md
    §6.3's distractor audit."""
    values = [answer]
    for d in deltas:
        candidate = answer + d
        if all(abs(candidate - v) > 1e-9 for v in values):
            values.append(candidate)
        if len(values) == count:
            break
    if len(values) < count:
        raise ValueError(f"could not build {count} distinct options around {answer}")
    return [fmt(v) for v in sorted(values)]
