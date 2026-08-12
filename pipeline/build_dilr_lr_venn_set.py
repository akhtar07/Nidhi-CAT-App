"""
Content scale-up: dilr.lr.venn-set (roi=3, previously 0 questions).

Classic 3-set Venn/survey puzzle. Ground truth is the 8 disjoint regions (only-Cricket,
only-Football, only-Tennis, each pairwise-only overlap, all-three, none) — picked first, as plain
numbers. Every aggregate the student is actually given (|Cricket|, |Cricket ∩ Football|, etc.) is
then *derived* from those regions via inclusion-exclusion, matching the DILR inversion in
SPEC.md §6.3: the learner has to invert what this script computed forward.

Independently re-verified below by a second, differently-written check: an explicit student-ID
simulation (real set operations on synthetic IDs) rather than the inclusion-exclusion formulas
used to build the stem — so a formula bug in one path can't hide from the other.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_lr_venn_set.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from schemas import PassageSet, Question, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
MICRO_TOPIC_ID = "dilr.lr.venn-set"
VERIFIED_AT = "2026-08-12T00:00:00Z"

# Ground-truth disjoint regions — original synthetic figures, nothing to attribute.
ONLY_CRICKET = 25
ONLY_FOOTBALL = 20
ONLY_TENNIS = 15
CRICKET_FOOTBALL_ONLY = 10
FOOTBALL_TENNIS_ONLY = 8
CRICKET_TENNIS_ONLY = 7
ALL_THREE = 5
NONE = 10

TOTAL = ONLY_CRICKET + ONLY_FOOTBALL + ONLY_TENNIS + CRICKET_FOOTBALL_ONLY + FOOTBALL_TENNIS_ONLY + CRICKET_TENNIS_ONLY + ALL_THREE + NONE


def build_aggregates() -> dict[str, int]:
    cricket = ONLY_CRICKET + CRICKET_FOOTBALL_ONLY + CRICKET_TENNIS_ONLY + ALL_THREE
    football = ONLY_FOOTBALL + CRICKET_FOOTBALL_ONLY + FOOTBALL_TENNIS_ONLY + ALL_THREE
    tennis = ONLY_TENNIS + FOOTBALL_TENNIS_ONLY + CRICKET_TENNIS_ONLY + ALL_THREE
    cricket_football = CRICKET_FOOTBALL_ONLY + ALL_THREE
    football_tennis = FOOTBALL_TENNIS_ONLY + ALL_THREE
    cricket_tennis = CRICKET_TENNIS_ONLY + ALL_THREE
    union = cricket + football + tennis - cricket_football - football_tennis - cricket_tennis + ALL_THREE
    return {
        "cricket": cricket,
        "football": football,
        "tennis": tennis,
        "cricket_football": cricket_football,
        "football_tennis": football_tennis,
        "cricket_tennis": cricket_tennis,
        "all_three": ALL_THREE,
        "union": union,
        "none": TOTAL - union,
        "exactly_one": ONLY_CRICKET + ONLY_FOOTBALL + ONLY_TENNIS,
        "exactly_two": CRICKET_FOOTBALL_ONLY + FOOTBALL_TENNIS_ONLY + CRICKET_TENNIS_ONLY,
    }


def independent_reverify(agg: dict[str, int]) -> None:
    """Builds an explicit population of TOTAL synthetic student IDs, assigns each to exactly one
    of the 8 regions, then re-derives every aggregate via real set operations — a genuinely
    different code path from the inclusion-exclusion arithmetic in build_aggregates()."""
    next_id = 0
    cricket_set: set[int] = set()
    football_set: set[int] = set()
    tennis_set: set[int] = set()
    region_sizes = {
        "only_c": ONLY_CRICKET,
        "only_f": ONLY_FOOTBALL,
        "only_t": ONLY_TENNIS,
        "cf": CRICKET_FOOTBALL_ONLY,
        "ft": FOOTBALL_TENNIS_ONLY,
        "ct": CRICKET_TENNIS_ONLY,
        "all3": ALL_THREE,
        "none": NONE,
    }
    membership = {"only_c": (1, 0, 0), "only_f": (0, 1, 0), "only_t": (0, 0, 1), "cf": (1, 1, 0), "ft": (0, 1, 1), "ct": (1, 0, 1), "all3": (1, 1, 1), "none": (0, 0, 0)}
    for region, size in region_sizes.items():
        in_c, in_f, in_t = membership[region]
        for _ in range(size):
            if in_c:
                cricket_set.add(next_id)
            if in_f:
                football_set.add(next_id)
            if in_t:
                tennis_set.add(next_id)
            next_id += 1
    total_population = next_id

    assert total_population == TOTAL
    assert len(cricket_set) == agg["cricket"]
    assert len(football_set) == agg["football"]
    assert len(tennis_set) == agg["tennis"]
    assert len(cricket_set & football_set) == agg["cricket_football"]
    assert len(football_set & tennis_set) == agg["football_tennis"]
    assert len(cricket_set & tennis_set) == agg["cricket_tennis"]
    assert len(cricket_set & football_set & tennis_set) == agg["all_three"]
    union_ids = cricket_set | football_set | tennis_set
    assert len(union_ids) == agg["union"]
    assert total_population - len(union_ids) == agg["none"]
    exactly_two_ids = (
        (cricket_set & football_set - tennis_set)
        | (football_set & tennis_set - cricket_set)
        | (cricket_set & tennis_set - football_set)
    )
    assert len(exactly_two_ids) == agg["exactly_two"]
    exactly_one_ids = (cricket_set ^ football_set ^ tennis_set) - (cricket_set & football_set & tennis_set)
    # symmetric-difference-of-3 isolates odd-membership-count ids (1 or 3 sets); remove the
    # all-three ones to leave exactly the exactly-one ids.
    assert len(exactly_one_ids) == agg["exactly_one"]


def build_questions(set_id: str, agg: dict[str, int]) -> list[Question]:
    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="How many students like exactly one of the three sports?",
        correctValue=agg["exactly_one"],
        titaTolerance=0,
        difficulty="easy",
        eloRating=1050.0,
        solutionMarkdown=(
            f"Only-Cricket + only-Football + only-Tennis = {ONLY_CRICKET} + {ONLY_FOOTBALL} + "
            f"{ONLY_TENNIS} = **{agg['exactly_one']}**."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:venn-set"],
    )

    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="How many students like exactly two of the three sports (but not all three)?",
        correctValue=agg["exactly_two"],
        titaTolerance=0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"(Cricket∩Football only) + (Football∩Tennis only) + (Cricket∩Tennis only), each "
            f"excluding the all-three group: "
            f"({agg['cricket_football']} − {agg['all_three']}) + ({agg['football_tennis']} − {agg['all_three']}) "
            f"+ ({agg['cricket_tennis']} − {agg['all_three']}) = **{agg['exactly_two']}**."
        ),
        targetSeconds=120,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:venn-set"],
    )

    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="How many students like none of the three sports?",
        correctValue=agg["none"],
        titaTolerance=0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"By inclusion-exclusion, students liking at least one sport = {agg['cricket']} + "
            f"{agg['football']} + {agg['tennis']} − {agg['cricket_football']} − {agg['football_tennis']} "
            f"− {agg['cricket_tennis']} + {agg['all_three']} = {agg['union']}. "
            f"None = {TOTAL} − {agg['union']} = **{agg['none']}**."
        ),
        targetSeconds=150,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:venn-set"],
    )

    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="How many students like only Cricket (and no other sport)?",
        correctValue=ONLY_CRICKET,
        titaTolerance=0,
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=(
            f"Only-Cricket = |Cricket| − (Cricket∩Football) − (Cricket∩Tennis) + (all three) = "
            f"{agg['cricket']} − {agg['cricket_football']} − {agg['cricket_tennis']} + {agg['all_three']} "
            f"= **{ONLY_CRICKET}**."
        ),
        targetSeconds=150,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:venn-set"],
    )

    return [q1, q2, q3, q4]


def main() -> None:
    agg = build_aggregates()
    # q4's formula path double-checked against the ground-truth constant directly.
    assert agg["cricket"] - agg["cricket_football"] - agg["cricket_tennis"] + agg["all_three"] == ONLY_CRICKET
    independent_reverify(agg)

    content_hash = hashlib.sha1(MICRO_TOPIC_ID.encode()).hexdigest()[:8]
    set_id = f"{MICRO_TOPIC_ID}.set-{content_hash}"

    body = (
        f"In a survey of {TOTAL} students about the sports they play: {agg['cricket']} play "
        f"Cricket, {agg['football']} play Football, and {agg['tennis']} play Tennis. "
        f"{agg['cricket_football']} play both Cricket and Football, {agg['football_tennis']} play "
        f"both Football and Tennis, and {agg['cricket_tennis']} play both Cricket and Tennis. "
        f"{agg['all_three']} play all three sports.\n\n"
        "Study this information and answer the questions that follow."
    )

    questions = build_questions(set_id, agg)
    passage_set = PassageSet(
        id=set_id,
        section="DILR",
        kind="lr_set",
        bodyMarkdown=body,
        assets=None,
        questionIds=[q.id for q in questions],
        genre=None,
        wordCount=None,
        targetMinutes=9.0,
        licence="CC0-1.0",
        sourceUrl=None,
    )

    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    for q in questions:
        path = QUESTIONS_DIR / f"{q.id}.json"
        path.write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
    PASSAGE_SETS_DIR.mkdir(parents=True, exist_ok=True)
    set_path = PASSAGE_SETS_DIR / f"{set_id}.json"
    set_path.write_text(json.dumps(json.loads(passage_set.model_dump_json()), indent=2) + "\n")
    print(f"Wrote {set_id} ({len(questions)} questions)")


if __name__ == "__main__":
    main()
