"""
Content scale-up: dilr.di.line-charts (roi=4, previously 0 questions).

Same "generate the data programmatically, derive questions deterministically" discipline as
build_dilr_growth_cagr.py / build_dilr_barchart_demo.py. Two colleges' student enrollment across
5 years, rendered as a line chart (app/src/pages/PassageSetPlayer.tsx's LineChartAsset — added
alongside this generator since only bar charts were renderable before).

Run (from /pipeline, cat-pipeline conda env): python build_dilr_di_line_charts.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from schemas import PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
MICRO_TOPIC_ID = "dilr.di.line-charts"
VERIFIED_AT = "2026-08-12T00:00:00Z"

YEARS = ["2019", "2020", "2021", "2022", "2023"]
# Original synthetic figures (student headcount) — nothing to attribute.
ENROLLMENT = {
    "Greenfield College": [820, 865, 790, 910, 960],
    "Riverside College": [700, 745, 810, 845, 880],
}


def build_chart_asset() -> dict:
    return {
        "type": "chart",
        "spec": {
            "chartKind": "line",
            "categories": YEARS,
            "series": [{"name": name, "values": vals} for name, vals in ENROLLMENT.items()],
            "unit": "students",
        },
    }


def build_questions(set_id: str) -> list[Question]:
    green = ENROLLMENT["Greenfield College"]
    river = ENROLLMENT["Riverside College"]

    # q1: read a value directly off the chart.
    green_2021 = green[2]
    assert green_2021 == 790

    # q2: which year had the largest combined enrollment.
    combined = [g + r for g, r in zip(green, river)]
    assert combined == [1520, 1610, 1600, 1755, 1840]
    max_year_idx = combined.index(max(combined))
    max_year = YEARS[max_year_idx]

    # q3: in how many years did Riverside have more students than Greenfield.
    river_ahead_years = [y for y, g, r in zip(YEARS, green, river) if r > g]
    assert river_ahead_years == ["2021"]

    # q4: the year with the smallest absolute gap between the two colleges.
    gaps = [abs(g - r) for g, r in zip(green, river)]
    assert gaps == [120, 120, 20, 65, 80]
    min_gap_idx = gaps.index(min(gaps))
    min_gap_year = YEARS[min_gap_idx]

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What was Greenfield College's enrollment in 2021?",
        correctValue=green_2021,
        titaTolerance=0,
        difficulty="easy",
        eloRating=1050.0,
        solutionMarkdown=f"Read directly off the 2021 point on Greenfield's line: **{green_2021} students**.",
        targetSeconds=45,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:line-charts"],
    )

    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="In which year was the combined enrollment of both colleges the highest?",
        options=[QuestionOption(key=chr(65 + i), markdown=y) for i, y in enumerate(YEARS)],
        correctKey=chr(65 + max_year_idx),
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Combined enrollment by year: " + ", ".join(f"{y}: {c}" for y, c in zip(YEARS, combined))
            + f". Highest is **{max_year}** ({combined[max_year_idx]})."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:line-charts"],
    )

    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="In how many of the 5 years shown did Riverside College have a higher enrollment than Greenfield College?",
        correctValue=len(river_ahead_years),
        titaTolerance=0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Comparing year by year, Riverside exceeds Greenfield only in "
            + ", ".join(river_ahead_years)
            + f" → **{len(river_ahead_years)} year(s)**."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:line-charts"],
    )

    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="In which year was the gap between the two colleges' enrollment the smallest?",
        options=[QuestionOption(key=chr(65 + i), markdown=y) for i, y in enumerate(YEARS)],
        correctKey=chr(65 + min_gap_idx),
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=(
            "Absolute gaps by year: " + ", ".join(f"{y}: {g}" for y, g in zip(YEARS, gaps))
            + f". Smallest is **{min_gap_year}** (gap of {gaps[min_gap_idx]})."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:line-charts"],
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
            "The line chart below shows annual student enrollment at two colleges, 2019-2023.\n\n"
            "Study the chart and answer the questions that follow."
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
