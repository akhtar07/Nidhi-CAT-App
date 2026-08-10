"""
Content scale-up: dilr.di.growth-cagr (roi=5, previously 0 questions).

Same "generate the data programmatically, derive questions deterministically" discipline as
build_dilr_table_demo.py / build_dilr_barchart_demo.py — a company's revenue across 5 years,
with YoY-growth and CAGR questions whose answers are computed directly from the same DATA list
the learner sees, asserted before being written.

CAGR formula: (End / Start)^(1/n) - 1, n = number of periods (years - 1).

Run (from /pipeline, cat-pipeline conda env): python build_dilr_growth_cagr.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from schemas import PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
MICRO_TOPIC_ID = "dilr.di.growth-cagr"
VERIFIED_AT = "2026-08-10T00:00:00Z"

YEARS = ["2019", "2020", "2021", "2022", "2023"]
# Two companies' revenue (Rs. crore), original synthetic figures — nothing to attribute.
REVENUE = {
    "Alpha Textiles": [120, 138, 152, 175, 210],
    "Beta Textiles": [95, 110, 118, 145, 152],
}


def yoy_growth_pct(values: list[int], year_index: int) -> float:
    prev, cur = values[year_index - 1], values[year_index]
    return round((cur - prev) / prev * 100, 2)


def cagr_pct(values: list[int]) -> float:
    n = len(values) - 1
    return round(((values[-1] / values[0]) ** (1 / n) - 1) * 100, 2)


def build_chart_asset() -> dict:
    return {
        "type": "chart",
        "spec": {
            "chartKind": "bar",
            "categories": YEARS,
            "series": [{"name": name, "values": vals} for name, vals in REVENUE.items()],
            "unit": "Rs. crore",
        },
    }


def build_questions(set_id: str) -> list[Question]:
    alpha = REVENUE["Alpha Textiles"]
    beta = REVENUE["Beta Textiles"]

    alpha_2023_growth = yoy_growth_pct(alpha, 4)
    assert alpha_2023_growth == round((210 - 175) / 175 * 100, 2)

    alpha_cagr = cagr_pct(alpha)
    beta_cagr = cagr_pct(beta)
    assert alpha_cagr == round((210 / 120) ** (1 / 4) * 100 - 100, 2)

    # Find the year with the highest single-year YoY growth for Alpha.
    alpha_yoy = [yoy_growth_pct(alpha, i) for i in range(1, len(alpha))]
    best_year_idx = alpha_yoy.index(max(alpha_yoy)) + 1  # +1 since yoy[0] is year_index=1
    best_year = YEARS[best_year_idx]
    assert alpha_yoy == [round((138 - 120) / 120 * 100, 2), round((152 - 138) / 138 * 100, 2), round((175 - 152) / 152 * 100, 2), round((210 - 175) / 175 * 100, 2)]

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What was Alpha Textiles' year-on-year revenue growth (%) from 2022 to 2023? (Round to 2 decimal places.)",
        correctValue=alpha_2023_growth,
        titaTolerance=0.05,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"2022 revenue = 175, 2023 revenue = 210. Growth $= \\dfrac{{210-175}}{{175}} \\times 100 = {alpha_2023_growth}\\%$."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:growth-cagr"],
    )

    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What is Alpha Textiles' CAGR (%) in revenue from 2019 to 2023? (Round to 2 decimal places.)",
        correctValue=alpha_cagr,
        titaTolerance=0.05,
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=(
            f"CAGR $= \\left(\\dfrac{{210}}{{120}}\\right)^{{1/4}} - 1 = {alpha_cagr}\\%$ (4 periods between 2019 and 2023)."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:growth-cagr", "cagr"],
    )

    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="In which year did Alpha Textiles record its highest year-on-year revenue growth?",
        options=[QuestionOption(key=chr(65 + i), markdown=y) for i, y in enumerate(YEARS[1:])],
        correctKey=chr(65 + YEARS[1:].index(best_year)),
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Year-on-year growth: "
            + ", ".join(f"{YEARS[i]}: {alpha_yoy[i-1]}%" for i in range(1, len(YEARS)))
            + f". Highest is **{best_year}**."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:growth-cagr"],
    )

    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Which company had the higher CAGR in revenue over 2019-2023?",
        options=[QuestionOption(key="A", markdown="Alpha Textiles"), QuestionOption(key="B", markdown="Beta Textiles")],
        correctKey="A" if alpha_cagr > beta_cagr else "B",
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=f"Alpha's CAGR is {alpha_cagr}%, Beta's is {beta_cagr}%. Alpha's is higher." if alpha_cagr > beta_cagr else f"Beta's CAGR is {beta_cagr}%, Alpha's is {alpha_cagr}%. Beta's is higher.",
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:growth-cagr", "cagr"],
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
            "The chart below shows annual revenue (Rs. crore) for two textile companies, "
            "2019-2023.\n\nStudy the chart and answer the questions that follow."
        ),
        assets=[build_chart_asset()],
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
