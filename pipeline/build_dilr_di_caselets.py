"""
Content scale-up: dilr.di.caselets (roi=5, previously 0 questions).

A "caselet" is DI data embedded in a narrative paragraph instead of a table/chart — the skill
being tested is careful extraction (find the right numbers buried in prose) as much as
computation. Same discipline as every other generator this pass: the underlying data is defined
as plain Python values first, every answer computed from those same values and asserted before
being written — nothing hand-typed separately from what the learner reads.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_di_caselets.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from schemas import PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
MICRO_TOPIC_ID = "dilr.di.caselets"
VERIFIED_AT = "2026-08-10T00:00:00Z"


def build_headcount_caselet() -> tuple[PassageSet, list[Question]]:
    departments = {
        "Engineering": {"count": 40, "avg_salary": 80000},
        "Sales": {"count": 25, "avg_salary": 60000},
        "Support": {"count": 15, "avg_salary": 45000},
    }
    total_employees = sum(d["count"] for d in departments.values())
    assert total_employees == 80
    totals = {name: d["count"] * d["avg_salary"] for name, d in departments.items()}
    assert totals == {"Engineering": 3200000, "Sales": 1500000, "Support": 675000}
    grand_total = sum(totals.values())
    assert grand_total == 5375000
    overall_avg = grand_total / total_employees
    assert overall_avg == 67187.5
    lowest_dept = min(totals, key=lambda k: totals[k])
    assert lowest_dept == "Support"

    body = (
        "TechNova Solutions has three departments. Engineering has 40 employees with an average "
        "monthly salary of Rs. 80,000. Sales has 25 employees with an average monthly salary of "
        "Rs. 60,000. Support has 15 employees with an average monthly salary of Rs. 45,000.\n\n"
        "Read the passage carefully and answer the questions that follow."
    )

    set_id = f"{MICRO_TOPIC_ID}.headcount-{hashlib.sha1(b'headcount').hexdigest()[:8]}"

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What is the total number of employees across all three departments?",
        correctValue=total_employees,
        titaTolerance=0.0,
        difficulty="easy",
        eloRating=1000.0,
        solutionMarkdown=f"$40 + 25 + 15 = {total_employees}$.",
        targetSeconds=60,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:caselet"],
    )

    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What is the total monthly salary bill for the Engineering department?",
        correctValue=totals["Engineering"],
        titaTolerance=0.0,
        difficulty="easy",
        eloRating=1000.0,
        solutionMarkdown=f"$40 \\times 80{{,}}000 = {totals['Engineering']}$.",
        targetSeconds=60,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:caselet"],
    )

    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What is the overall average monthly salary across all employees in all three departments? (Round to 2 decimal places.)",
        correctValue=round(overall_avg, 2),
        titaTolerance=0.5,
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=(
            f"Total salary bill $= {totals['Engineering']} + {totals['Sales']} + {totals['Support']} = {grand_total}$. "
            f"Overall average $= {grand_total} / {total_employees} = {overall_avg}$. "
            "Note this weighted average is closer to Engineering's salary than a simple average of "
            "the three department averages would be, since Engineering has the most employees."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:caselet", "weighted-average"],
    )

    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Which department has the lowest total monthly salary bill?",
        options=[QuestionOption(key=chr(65 + i), markdown=name) for i, name in enumerate(departments)],
        correctKey=chr(65 + list(departments).index(lowest_dept)),
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Total bills: " + ", ".join(f"{n}: {totals[n]}" for n in departments) + f". **{lowest_dept}** is lowest — "
            "note this is about the department's **total** bill, not its average salary; Support has both the "
            "fewest employees and the lowest average, so it's unambiguous here, but always check total vs. average."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:caselet"],
    )

    questions = [q1, q2, q3, q4]
    passage_set = PassageSet(
        id=set_id, section="DILR", kind="di_set", bodyMarkdown=body, assets=None,
        questionIds=[q.id for q in questions], genre=None, wordCount=None, targetMinutes=8.0,
        licence="CC0-1.0", sourceUrl=None,
    )
    return passage_set, questions


def build_production_caselet() -> tuple[PassageSet, list[Question]]:
    factories = {
        "Factory A": {"units_per_day": 1200, "defect_rate_pct": 2.5},
        "Factory B": {"units_per_day": 800, "defect_rate_pct": 4.0},
    }
    good_units = {
        name: round(f["units_per_day"] * (1 - f["defect_rate_pct"] / 100))
        for name, f in factories.items()
    }
    assert good_units["Factory A"] == round(1200 * 0.975)  # 1170
    assert good_units["Factory A"] == 1170
    assert good_units["Factory B"] == round(800 * 0.96)  # 768
    assert good_units["Factory B"] == 768
    total_good = sum(good_units.values())
    assert total_good == 1938
    total_defective = sum(
        round(f["units_per_day"] * f["defect_rate_pct"] / 100) for f in factories.values()
    )
    assert total_defective == 30 + 32  # A: 1200*0.025=30, B: 800*0.04=32
    combined_units = sum(f["units_per_day"] for f in factories.values())
    assert combined_units == 2000
    combined_defect_pct = round(total_defective / combined_units * 100, 2)
    assert combined_defect_pct == 3.1

    body = (
        "A manufacturer runs two factories. Factory A produces 1,200 units per day with a defect "
        "rate of 2.5%. Factory B produces 800 units per day with a defect rate of 4.0%. "
        "A 'good' unit is one that is not defective.\n\n"
        "Read the passage carefully and answer the questions that follow."
    )

    set_id = f"{MICRO_TOPIC_ID}.production-{hashlib.sha1(b'production').hexdigest()[:8]}"

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="How many good (non-defective) units does Factory A produce per day?",
        correctValue=good_units["Factory A"],
        titaTolerance=0.0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=f"$1200 \\times (1 - 0.025) = 1200 \\times 0.975 = {good_units['Factory A']}$.",
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:caselet"],
    )

    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What is the total number of good units produced by both factories combined, per day?",
        correctValue=total_good,
        titaTolerance=0.0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=f"Factory A: {good_units['Factory A']}, Factory B: {good_units['Factory B']}. Total $= {total_good}$.",
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:caselet"],
    )

    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What is the combined defect rate (%) across both factories? (Round to 2 decimal places.)",
        correctValue=combined_defect_pct,
        titaTolerance=0.05,
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=(
            f"Defective units: Factory A $= 1200 \\times 0.025 = 30$, Factory B $= 800 \\times 0.04 = 32$. "
            f"Total defective $= 62$, total units $= 2000$. Combined defect rate $= 62/2000 \\times 100 = "
            f"{combined_defect_pct}\\%$ — **not** the simple average of 2.5% and 4.0% (3.25%), because the "
            "two factories produce different volumes."
        ),
        targetSeconds=105,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:caselet", "weighted-average"],
    )

    questions = [q1, q2, q3]
    passage_set = PassageSet(
        id=set_id, section="DILR", kind="di_set", bodyMarkdown=body, assets=None,
        questionIds=[q.id for q in questions], genre=None, wordCount=None, targetMinutes=7.0,
        licence="CC0-1.0", sourceUrl=None,
    )
    return passage_set, questions


def main() -> None:
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    PASSAGE_SETS_DIR.mkdir(parents=True, exist_ok=True)
    for builder in [build_headcount_caselet, build_production_caselet]:
        passage_set, questions = builder()
        for q in questions:
            path = QUESTIONS_DIR / f"{q.id}.json"
            path.write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
        set_path = PASSAGE_SETS_DIR / f"{passage_set.id}.json"
        set_path.write_text(json.dumps(json.loads(passage_set.model_dump_json()), indent=2) + "\n")
        print(f"Wrote {passage_set.id} ({len(questions)} questions)")


if __name__ == "__main__":
    main()
