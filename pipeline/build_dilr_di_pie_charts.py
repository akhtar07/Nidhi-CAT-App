"""
Content scale-up: dilr.di.pie-charts (roi=4, previously 0 questions).

Same "generate the data programmatically, derive questions deterministically" discipline as the
other DI generators. A company's Rs. 60 lakh annual budget broken into 5 expense categories
(percentages summing to exactly 100), rendered as a pie chart (PassageSetPlayer's new
PieChartAsset). Deliberately uses whole-number percentages and a total divisible by 100 so every
derived rupee amount is an exact integer, not a rounded one.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_di_pie_charts.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from schemas import PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
MICRO_TOPIC_ID = "dilr.di.pie-charts"
VERIFIED_AT = "2026-08-12T00:00:00Z"

TOTAL_BUDGET_LAKH = 60
# Percentages sum to exactly 100 — original synthetic figures, nothing to attribute.
BUDGET_PCT = {
    "Salaries": 40,
    "Marketing": 20,
    "Rent": 15,
    "R&D": 15,
    "Utilities": 10,
}


def build_chart_asset() -> dict:
    assert sum(BUDGET_PCT.values()) == 100
    return {
        "type": "chart",
        "spec": {
            "chartKind": "pie",
            "slices": [{"name": name, "value": pct} for name, pct in BUDGET_PCT.items()],
            "unit": "%",
        },
    }


def amount_lakh(pct: int) -> float:
    return round(TOTAL_BUDGET_LAKH * pct / 100, 2)


def build_questions(set_id: str) -> list[Question]:
    salaries_amt = amount_lakh(BUDGET_PCT["Salaries"])
    assert salaries_amt == 24.0

    largest_cat = max(BUDGET_PCT, key=lambda k: BUDGET_PCT[k])
    smallest_cat = min(BUDGET_PCT, key=lambda k: BUDGET_PCT[k])
    assert largest_cat == "Salaries" and smallest_cat == "Utilities"

    rd_rent_ratio_num, rd_rent_ratio_den = BUDGET_PCT["R&D"], BUDGET_PCT["Rent"]
    assert rd_rent_ratio_num == rd_rent_ratio_den  # 15:15 = 1:1
    from math import gcd

    g = gcd(rd_rent_ratio_num, rd_rent_ratio_den)
    ratio_str = f"{rd_rent_ratio_num // g}:{rd_rent_ratio_den // g}"
    assert ratio_str == "1:1"

    marketing_utilities_combined_amt = amount_lakh(BUDGET_PCT["Marketing"] + BUDGET_PCT["Utilities"])
    assert marketing_utilities_combined_amt == 18.0

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown=(
            f"The company's total annual budget is Rs. {TOTAL_BUDGET_LAKH} lakh. "
            "Based on the pie chart, how much (in Rs. lakh) is allocated to Salaries?"
        ),
        correctValue=salaries_amt,
        titaTolerance=0.01,
        difficulty="easy",
        eloRating=1050.0,
        solutionMarkdown=(
            f"Salaries is {BUDGET_PCT['Salaries']}% of the budget: "
            f"$\\dfrac{{{BUDGET_PCT['Salaries']}}}{{100}} \\times {TOTAL_BUDGET_LAKH} = {salaries_amt}$ lakh."
        ),
        targetSeconds=60,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:pie-charts"],
    )

    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Which category has the smallest share of the budget?",
        options=[QuestionOption(key=chr(65 + i), markdown=name) for i, name in enumerate(BUDGET_PCT.keys())],
        correctKey=chr(65 + list(BUDGET_PCT.keys()).index(smallest_cat)),
        difficulty="easy",
        eloRating=1050.0,
        solutionMarkdown=f"Shares are {', '.join(f'{k}: {v}%' for k, v in BUDGET_PCT.items())}. Smallest is **{smallest_cat}** ({BUDGET_PCT[smallest_cat]}%).",
        targetSeconds=45,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:pie-charts"],
    )

    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What is the ratio of the R&D allocation to the Rent allocation?",
        correctValue=1.0,
        titaTolerance=0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"R&D is {BUDGET_PCT['R&D']}% and Rent is {BUDGET_PCT['Rent']}% of the same total, "
            f"so the ratio is {ratio_str} $= 1$."
        ),
        targetSeconds=60,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:pie-charts"],
    )

    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown=(
            f"How much (in Rs. lakh) is spent on Marketing and Utilities combined, "
            f"out of the total Rs. {TOTAL_BUDGET_LAKH} lakh budget?"
        ),
        correctValue=marketing_utilities_combined_amt,
        titaTolerance=0.01,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"Marketing ({BUDGET_PCT['Marketing']}%) + Utilities ({BUDGET_PCT['Utilities']}%) = "
            f"{BUDGET_PCT['Marketing'] + BUDGET_PCT['Utilities']}% of {TOTAL_BUDGET_LAKH} lakh "
            f"$= {marketing_utilities_combined_amt}$ lakh."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:pie-charts"],
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
            f"The pie chart below shows how a company's Rs. {TOTAL_BUDGET_LAKH} lakh annual budget is split "
            "across 5 expense categories.\n\nStudy the chart and answer the questions that follow."
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
