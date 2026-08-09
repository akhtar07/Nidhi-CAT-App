"""
Milestone 8: the first real DILR set, for dilr.di.tables — needed for
"one micro-topic fully playable end to end" on the Passage/Set player
(SPEC.md §15's Milestone 8 row), mirroring how Milestone 6 shipped one
real Lesson before building the reader UI around it.

Per SPEC.md §6.3's DILR approach: generate the set's underlying data table
programmatically first, derive the questions from the data deterministically,
and never let an LLM invent the numbers. Every answer below is computed by
`_expected()` from the same DATA table the learner sees — not hand-typed —
so a transcription slip here would fail loudly instead of shipping quietly
wrong.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_table_demo.py
"""

from __future__ import annotations

import json
from pathlib import Path

from schemas import PassageAsset, PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"

MICRO_TOPIC_ID = "dilr.di.tables"
SET_ID = "dilr.di.tables.set-01"
VERIFIED_AT = "2026-08-09T00:00:00Z"

COMPANIES = ["P", "Q", "R", "S", "T"]
QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
# Revenue in Rs. crore. Original synthetic data, not sourced from anywhere.
DATA = {
    "P": [120, 135, 150, 165],
    "Q": [200, 180, 190, 210],
    "R": [90, 95, 100, 98],
    "S": [160, 170, 185, 200],
    "T": [175, 170, 165, 160],
}

BODY_MARKDOWN = """The table below shows the quarterly revenue (in Rs. crore) of five companies,
P, Q, R, S and T, over the four quarters of a fiscal year.

Study the table and answer the questions that follow."""


def _totals() -> dict[str, int]:
    return {c: sum(vals) for c, vals in DATA.items()}


def _highest_total_company() -> str:
    totals = _totals()
    return max(totals, key=lambda c: totals[c])


def _pct_growth(company: str) -> float:
    vals = DATA[company]
    return round((vals[-1] - vals[0]) / vals[0] * 100, 2)


def _average(company: str) -> float:
    vals = DATA[company]
    return round(sum(vals) / len(vals), 2)


def _strictly_increasing_count() -> int:
    return sum(1 for vals in DATA.values() if all(vals[i] < vals[i + 1] for i in range(len(vals) - 1)))


def build_table_asset() -> PassageAsset:
    return PassageAsset(
        type="table",
        spec={
            "columns": ["Company", *QUARTERS],
            "rows": [[c, *DATA[c]] for c in COMPANIES],
        },
    )


def build_questions() -> list[Question]:
    totals = _totals()
    highest = _highest_total_company()
    assert highest == "Q", f"expected Q to have the highest total, got {highest} ({totals})"

    s_growth = _pct_growth("S")
    assert s_growth == 25.0, f"expected S growth 25%, computed {s_growth}"

    r_avg = _average("R")
    assert r_avg == 95.75, f"expected R average 95.75, computed {r_avg}"

    inc_count = _strictly_increasing_count()
    assert inc_count == 2, f"expected 2 strictly-increasing companies, computed {inc_count}"

    q1 = Question(
        id=f"{SET_ID}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Which company had the highest total revenue over the four quarters combined?",
        options=[
            QuestionOption(key="A", markdown="P"),
            QuestionOption(key="B", markdown="Q"),
            QuestionOption(key="C", markdown="S"),
            QuestionOption(key="D", markdown="T"),
        ],
        correctKey="B",
        difficulty="easy",
        eloRating=1000.0,
        solutionMarkdown=(
            "Sum each company's four quarters: "
            f"P = {totals['P']}, Q = {totals['Q']}, R = {totals['R']}, "
            f"S = {totals['S']}, T = {totals['T']}. "
            f"Q has the highest total at {totals['Q']} crore."
        ),
        targetSeconds=60,
        source="generated",
        sourceRef=None,
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:tables", "totals"],
    )

    q2 = Question(
        id=f"{SET_ID}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What is the percentage growth in Company S's revenue from Q1 to Q4? (Enter just the number, e.g. 25 for 25%.)",
        correctValue=s_growth,
        titaTolerance=0.5,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"Company S: Q1 = {DATA['S'][0]}, Q4 = {DATA['S'][-1]}. "
            f"Growth $= \\dfrac{{{DATA['S'][-1]} - {DATA['S'][0]}}}{{{DATA['S'][0]}}} \\times 100 = {s_growth}\\%$."
        ),
        targetSeconds=75,
        source="generated",
        sourceRef=None,
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:tables", "percentage-change"],
    )

    q3 = Question(
        id=f"{SET_ID}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What was Company R's average quarterly revenue over the four quarters, in Rs. crore?",
        correctValue=r_avg,
        titaTolerance=0.1,
        difficulty="easy",
        eloRating=1000.0,
        solutionMarkdown=(
            f"R's quarters: {', '.join(str(v) for v in DATA['R'])}. "
            f"Average $= {totals['R']}/4 = {r_avg}$ crore."
        ),
        targetSeconds=60,
        source="generated",
        sourceRef=None,
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:tables", "average"],
    )

    q4 = Question(
        id=f"{SET_ID}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown=(
            "For how many of the five companies did revenue increase in every successive "
            "quarter (i.e. Q1 < Q2 < Q3 < Q4)?"
        ),
        options=[
            QuestionOption(key="A", markdown="1"),
            QuestionOption(key="B", markdown="2"),
            QuestionOption(key="C", markdown="3"),
            QuestionOption(key="D", markdown="4"),
        ],
        correctKey="B",
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Check each company: P (120<135<150<165) strictly increases. "
            "Q dips from 200 to 180 in Q2 — no. "
            "R dips from 100 to 98 in Q4 — no. "
            "S (160<170<185<200) strictly increases. "
            "T decreases throughout — no. "
            "Only **P and S** — 2 companies."
        ),
        targetSeconds=90,
        source="generated",
        sourceRef=None,
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:tables", "trend-analysis"],
    )

    return [q1, q2, q3, q4]


def build_passage_set(questions: list[Question]) -> PassageSet:
    return PassageSet(
        id=SET_ID,
        section="DILR",
        kind="di_set",
        bodyMarkdown=BODY_MARKDOWN,
        assets=[build_table_asset()],
        questionIds=[q.id for q in questions],
        genre=None,
        wordCount=None,
        targetMinutes=8.0,
        licence="CC0-1.0",
        sourceUrl=None,
    )


def main() -> None:
    questions = build_questions()
    passage_set = build_passage_set(questions)

    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    for q in questions:
        path = QUESTIONS_DIR / f"{q.id}.json"
        path.write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
        print(f"Wrote {path.relative_to(REPO_ROOT)}")

    PASSAGE_SETS_DIR.mkdir(parents=True, exist_ok=True)
    set_path = PASSAGE_SETS_DIR / f"{SET_ID}.json"
    set_path.write_text(json.dumps(json.loads(passage_set.model_dump_json()), indent=2) + "\n")
    print(f"Wrote {set_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
