"""
Generation + verification harness for original QA items (SPEC.md §6.3,
Tier 3). Used because Tier 1 (official PYQ PDFs) turned out to require
per-candidate authenticated access, not a freely downloadable public PDF —
see PROGRESS.md for the full account. Coaching-site scraping remains
off-limits per SPEC.md §6.1, so every item here is original and independently
verified, never sourced from a third party.

The core discipline (SPEC.md §6.3): every item's claimed answer must be
independently computed by code and checked to match before the item is kept.
A generator function returns an ItemSpec whose `answer_fn` recomputes the
answer via a path independent of however the stem's displayed numbers were
chosen. Mismatch -> the item is discarded, never "repaired" by adjusting the
claimed answer to fit.
"""

from __future__ import annotations

import hashlib
import json
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from schemas import Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
VERIFIED_AT = "2026-08-09T00:00:00Z"

DIFFICULTY_ELO = {"easy": 1000, "medium": 1200, "hard": 1400, "very_hard": 1600}


@dataclass
class ItemSpec:
    microtopic_id: str
    difficulty: str
    stem: str
    solution: str
    answer_fn: Callable[[], float | int | str]
    claimed_value: float | int | str
    target_seconds: int
    tags: list[str] = field(default_factory=list)
    alt_solution: str | None = None
    format: str = "tita"  # 'tita' or 'mcq'
    options: list[tuple[str, str]] | None = None  # (key, markdown) — mcq only
    correct_key: str | None = None  # mcq only
    tita_tolerance: float | None = None
    extra_microtopic_ids: list[str] = field(default_factory=list)


class VerificationError(Exception):
    pass


def _numbers_close(a: float | int | str, b: float | int | str, tol: float) -> bool:
    try:
        return abs(float(a) - float(b)) <= tol
    except (TypeError, ValueError):
        return str(a).strip() == str(b).strip()


def verify_and_build(spec: ItemSpec, section: str = "QA", source: str = "generated") -> Question:
    """Runs spec.answer_fn() and only builds a Question if it matches the
    claimed value. Raises VerificationError otherwise — callers must not
    catch-and-ship; a failed item is discarded, per SPEC.md §6.3."""

    computed = spec.answer_fn()
    tol = spec.tita_tolerance if spec.tita_tolerance is not None else 1e-6
    if not _numbers_close(computed, spec.claimed_value, tol):
        raise VerificationError(
            f"[{spec.microtopic_id}] answer_fn()={computed!r} != claimed={spec.claimed_value!r}\n"
            f"stem: {spec.stem}"
        )

    if spec.format == "mcq":
        if not spec.options or not spec.correct_key:
            raise VerificationError(f"[{spec.microtopic_id}] mcq item missing options/correct_key")
        values = [v for _, v in spec.options]
        if len(set(values)) != len(values):
            raise VerificationError(
                f"[{spec.microtopic_id}] distractor audit failed: duplicate option values {values}"
            )
        keys = [k for k, _ in spec.options]
        if spec.correct_key not in keys:
            raise VerificationError(f"[{spec.microtopic_id}] correct_key not among options")

    content_hash = hashlib.sha1(
        (spec.microtopic_id + "|" + spec.stem + "|" + str(spec.claimed_value)).encode()
    ).hexdigest()[:10]
    qid = f"{spec.microtopic_id}.gen-{content_hash}"

    micro_topic_ids = [spec.microtopic_id, *spec.extra_microtopic_ids]

    verification = VerificationRecord(
        method="sympy_verified",
        verifiedAt=VERIFIED_AT,
        distractorAuditPassed=True if spec.format == "mcq" else None,
        dedupChecked=None,
        reviewerNote=None,
    )

    kwargs = dict(
        id=qid,
        microTopicIds=micro_topic_ids,
        section=section,
        format=spec.format,
        stemMarkdown=spec.stem,
        difficulty=spec.difficulty,
        eloRating=float(DIFFICULTY_ELO[spec.difficulty]),
        solutionMarkdown=spec.solution,
        altSolutionMarkdown=spec.alt_solution,
        targetSeconds=spec.target_seconds,
        source=source,
        sourceRef=None,
        verification=verification,
        tags=spec.tags,
    )

    if spec.format == "mcq":
        kwargs["options"] = [QuestionOption(key=k, markdown=v) for k, v in spec.options]
        kwargs["correctKey"] = spec.correct_key
    else:
        kwargs["correctValue"] = spec.claimed_value
        kwargs["titaTolerance"] = tol

    return Question(**kwargs)


def mcq_options_from_distractors(
    correct_markdown: str, distractor_markdowns: list[str], rng: random.Random
) -> tuple[list[tuple[str, str]], str]:
    """Shuffles [correct, *distractors] into A/B/C/D and returns
    (options, correct_key). Caller guarantees distractors are distinct from
    correct and from each other."""
    all_vals = [correct_markdown, *distractor_markdowns]
    keys = ["A", "B", "C", "D"][: len(all_vals)]
    order = list(range(len(all_vals)))
    rng.shuffle(order)
    options = [(keys[i], all_vals[order[i]]) for i in range(len(all_vals))]
    correct_key = next(k for k, i in zip(keys, order) if all_vals[i] == correct_markdown)
    return options, correct_key


def write_items(items: list[Question]) -> None:
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    for q in items:
        path = QUESTIONS_DIR / f"{q.id}.json"
        path.write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")


def run_generators(generators: list[Callable[[], list[ItemSpec]]]) -> list[Question]:
    """Runs every generator, verifies every returned spec, and returns the
    Questions that passed. Failures are printed (with the discarded stem)
    and skipped — never silently patched.

    Also dedupes on (microtopic_id, stem): a small random-parameter space
    can produce the same question twice (same stem, same answer). Rather
    than let the second draw silently overwrite the first item's file on
    disk (same content-hash id), it's dropped here and counted separately —
    fewer unique items for that micro-topic is fine; shipping the same
    question under a second id is not."""
    built: list[Question] = []
    failed = 0
    duplicates = 0
    seen: set[tuple[str, str]] = set()
    for gen in generators:
        specs = gen()
        for spec in specs:
            key = (spec.microtopic_id, spec.stem)
            if key in seen:
                duplicates += 1
                continue
            seen.add(key)
            try:
                built.append(verify_and_build(spec))
            except VerificationError as e:
                failed += 1
                print(f"DISCARDED: {e}")
    print(f"\n{len(built)} items verified and built, {failed} discarded, {duplicates} duplicate draws skipped.")
    return built
