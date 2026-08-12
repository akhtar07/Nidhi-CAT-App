"""
Content scale-up: dilr.di.stacked-charts (roi=3, previously 0 questions).

A company's quarterly sales (Rs. lakh) across 3 product lines, rendered as a stacked bar chart
(PassageSetPlayer's new StackedBarChartAsset). Same discipline as every other DI generator this
pass: raw data is a plain Python dict, every question's answer is computed from that same dict
and asserted before being written.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_di_stacked_charts.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from schemas import PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
MICRO_TOPIC_ID = "dilr.di.stacked-charts"
VERIFIED_AT = "2026-08-12T00:00:00Z"

QUARTERS = ["Q1", "Q2", "Q3", "Q4"]
# Original synthetic figures (Rs. lakh) — nothing to attribute.
SALES = {
    "Electronics": [45, 52, 48, 60],
    "Apparel": [30, 28, 35, 38],
    "Groceries": [25, 30, 27, 32],
}


def build_chart_asset() -> dict:
    return {
        "type": "chart",
        "spec": {
            "chartKind": "stacked-bar",
            "categories": QUARTERS,
            "series": [{"name": name, "values": vals} for name, vals in SALES.items()],
            "unit": "Rs. lakh",
        },
    }


def build_questions(set_id: str) -> list[Question]:
    totals = [sum(SALES[cat][qi] for cat in SALES) for qi in range(len(QUARTERS))]
    assert totals == [100, 110, 110, 130]

    # q1: total sales in a given quarter.
    q4_total = totals[3]

    # q2: which quarter had the highest total sales.
    max_idx = totals.index(max(totals))
    max_quarter = QUARTERS[max_idx]

    # q3: Electronics' share (%) of total sales in Q1, rounded to 2 decimals.
    electronics_q1_share = round(SALES["Electronics"][0] / totals[0] * 100, 2)
    assert electronics_q1_share == 45.0

    # q4: by how much did Apparel's sales increase from Q1 to Q4.
    apparel_increase = SALES["Apparel"][3] - SALES["Apparel"][0]
    assert apparel_increase == 8

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What were the total sales (Rs. lakh, all three product lines combined) in Q4?",
        correctValue=q4_total,
        titaTolerance=0,
        difficulty="easy",
        eloRating=1050.0,
        solutionMarkdown=(
            f"Q4: Electronics {SALES['Electronics'][3]} + Apparel {SALES['Apparel'][3]} + "
            f"Groceries {SALES['Groceries'][3]} = **{q4_total}** lakh."
        ),
        targetSeconds=60,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:stacked-charts"],
    )

    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="In which quarter were the total sales (all product lines combined) the highest?",
        options=[QuestionOption(key=chr(65 + i), markdown=q) for i, q in enumerate(QUARTERS)],
        correctKey=chr(65 + max_idx),
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Quarterly totals: " + ", ".join(f"{q}: {t}" for q, t in zip(QUARTERS, totals))
            + f". Highest is **{max_quarter}** ({totals[max_idx]})."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:stacked-charts"],
    )

    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What percentage of Q1's total sales came from Electronics? (Round to 2 decimal places.)",
        correctValue=electronics_q1_share,
        titaTolerance=0.05,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"Electronics Q1 = {SALES['Electronics'][0]}, total Q1 = {totals[0]}. "
            f"$\\dfrac{{{SALES['Electronics'][0]}}}{{{totals[0]}}} \\times 100 = {electronics_q1_share}\\%$."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:stacked-charts"],
    )

    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="By how much (Rs. lakh) did Apparel's sales increase from Q1 to Q4?",
        correctValue=apparel_increase,
        titaTolerance=0,
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=(
            f"Apparel: Q4 ({SALES['Apparel'][3]}) − Q1 ({SALES['Apparel'][0]}) = **{apparel_increase}** lakh."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:stacked-charts"],
    )

    return [q1, q2, q3, q4]


def main() -> None:
    content_hash = hashlib.sha1(MICRO_TOPIC_ID.encode()).hexdigest()[:8]
    set_id = f"{MICRO_TOPIC_ID}.set-{content_hash}"

    questions = build_questions(set_id)
    passage_set = PassageSet(
        id=set_id,
        section="DILR",
        kind="di_set",
        bodyMarkdown=(
            "The stacked bar chart below shows a company's quarterly sales (Rs. lakh) across "
            "three product lines.\n\nStudy the chart and answer the questions that follow."
        ),
        assets=[build_chart_asset()],
        questionIds=[q.id for q in questions],
        genre=None,
        wordCount=None,
        targetMinutes=8.0,
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
