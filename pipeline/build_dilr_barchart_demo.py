"""
Milestone 13: second DILR set, this time bar-chart based (dilr.di.bar-column) —
same "generate the data programmatically first, questions derived
deterministically" discipline as build_dilr_table_demo.py (SPEC.md §6.3's
DILR inversion), proving the pattern generalises beyond tables, plus the
new bar-chart PassageAsset renderer in PassageSetPlayer.tsx it depends on.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_barchart_demo.py
"""

from __future__ import annotations

import json
from pathlib import Path

from schemas import PassageAsset, PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"

MICRO_TOPIC_ID = "dilr.di.bar-column"
SET_ID = "dilr.di.bar-column.set-01"
VERIFIED_AT = "2026-08-10T00:00:00Z"

# Original synthetic data: monthly units sold, two product lines, four months.
MONTHS = ["Jan", "Feb", "Mar", "Apr"]
PRODUCT_A = [120, 150, 90, 180]
PRODUCT_B = [80, 100, 140, 110]

BODY_MARKDOWN = """The bar chart below shows the number of units sold each month for two products,
A and B, at a retail store.

Study the chart and answer the questions that follow."""


def _totals() -> dict[str, int]:
    return {"A": sum(PRODUCT_A), "B": sum(PRODUCT_B)}


def _month_with_highest_combined() -> str:
    combined = [a + b for a, b in zip(PRODUCT_A, PRODUCT_B)]
    return MONTHS[combined.index(max(combined))]


def _pct_share_of_a_in_march() -> float:
    idx = MONTHS.index("Mar")
    a, b = PRODUCT_A[idx], PRODUCT_B[idx]
    return round(a / (a + b) * 100, 2)


def _months_b_exceeded_a() -> int:
    return sum(1 for a, b in zip(PRODUCT_A, PRODUCT_B) if b > a)


def build_chart_asset() -> PassageAsset:
    return PassageAsset(
        type="chart",
        spec={
            "chartKind": "bar",
            "categories": MONTHS,
            "series": [
                {"name": "Product A", "values": PRODUCT_A},
                {"name": "Product B", "values": PRODUCT_B},
            ],
            "unit": "units",
        },
    )


def build_questions() -> list[Question]:
    totals = _totals()
    assert totals == {"A": 540, "B": 430}, f"unexpected totals: {totals}"

    peak_month = _month_with_highest_combined()
    assert peak_month == "Apr", f"expected Apr, got {peak_month}"  # 180+110=290, highest

    a_share_mar = _pct_share_of_a_in_march()
    assert a_share_mar == _approx(90 / 230 * 100), f"unexpected share: {a_share_mar}"

    b_exceeded_count = _months_b_exceeded_a()
    assert b_exceeded_count == 1, f"expected 1 (Mar only: 140>90), got {b_exceeded_count}"

    q1 = Question(
        id=f"{SET_ID}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="In which month was the combined (Product A + Product B) units sold the highest?",
        options=[
            QuestionOption(key="A", markdown="Jan"),
            QuestionOption(key="B", markdown="Feb"),
            QuestionOption(key="C", markdown="Mar"),
            QuestionOption(key="D", markdown="Apr"),
        ],
        correctKey="D",
        difficulty="easy",
        eloRating=1000.0,
        solutionMarkdown=(
            "Combined totals: Jan = 120+80 = 200, Feb = 150+100 = 250, Mar = 90+140 = 230, "
            "Apr = 180+110 = 290. April is highest at 290."
        ),
        targetSeconds=60,
        source="generated",
        sourceRef=None,
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:bar-chart", "totals"],
    )

    q2 = Question(
        id=f"{SET_ID}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown=(
            "What percentage of the combined (A + B) units sold in March were Product A? "
            "(Round to 2 decimal places; enter just the number.)"
        ),
        correctValue=a_share_mar,
        titaTolerance=0.1,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"March: A = {PRODUCT_A[MONTHS.index('Mar')]}, B = {PRODUCT_B[MONTHS.index('Mar')]}. "
            f"A's share $= \\dfrac{{90}}{{90+140}} \\times 100 = {a_share_mar}\\%$."
        ),
        targetSeconds=75,
        source="generated",
        sourceRef=None,
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:bar-chart", "percentage-share"],
    )

    q3 = Question(
        id=f"{SET_ID}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What was the total number of Product A units sold across all four months?",
        correctValue=totals["A"],
        titaTolerance=0.0,
        difficulty="easy",
        eloRating=1000.0,
        solutionMarkdown=f"Sum: {' + '.join(str(v) for v in PRODUCT_A)} = {totals['A']}.",
        targetSeconds=45,
        source="generated",
        sourceRef=None,
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:bar-chart", "totals"],
    )

    q4 = Question(
        id=f"{SET_ID}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="In how many of the four months did Product B outsell Product A?",
        options=[
            QuestionOption(key="A", markdown="0"),
            QuestionOption(key="B", markdown="1"),
            QuestionOption(key="C", markdown="2"),
            QuestionOption(key="D", markdown="3"),
        ],
        correctKey="B",
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Compare each month: Jan (120 vs 80, A wins), Feb (150 vs 100, A wins), "
            "Mar (90 vs 140, B wins), Apr (180 vs 110, A wins). B outsold A in only **1** month."
        ),
        targetSeconds=75,
        source="generated",
        sourceRef=None,
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:bar-chart", "comparison"],
    )

    return [q1, q2, q3, q4]


def _approx(x: float) -> float:
    # No pytest dependency in this pipeline env — just round to match the rounding the
    # question/solution itself uses, so the assertion is a real check, not decoration.
    return round(x, 2)


def build_passage_set(questions: list[Question]) -> PassageSet:
    return PassageSet(
        id=SET_ID,
        section="DILR",
        kind="di_set",
        bodyMarkdown=BODY_MARKDOWN,
        assets=[build_chart_asset()],
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
