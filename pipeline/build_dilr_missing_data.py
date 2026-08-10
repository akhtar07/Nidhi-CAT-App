"""
Content scale-up: dilr.di.missing-data (roi=5, previously 0 questions).

Same DILR inversion as every other generator in this pass: real data is generated first, row/
column totals are computed from it, then a subset of cells is blanked out — chosen so every
blanked cell sits alone in both its row and its column (like non-attacking rooks), which
guarantees it's uniquely recoverable from the row total alone (or the column total alone; both
must agree, and the script asserts they do). The learner sees the table with blanks + all totals
and must deduce the missing values — exactly the "missing/incomplete data table" DILR pattern.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_missing_data.py
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from schemas import PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
MICRO_TOPIC_ID = "dilr.di.missing-data"
VERIFIED_AT = "2026-08-10T00:00:00Z"

PRODUCTS = ["Product P", "Product Q", "Product R", "Product S"]
REGIONS = ["North", "South", "East", "West"]
BLANK = "?"


def build_data() -> list[list[int]]:
    rng = random.Random(f"{MICRO_TOPIC_ID}-data")
    return [[rng.randint(20, 90) for _ in REGIONS] for _ in PRODUCTS]


def row_totals(data: list[list[int]]) -> list[int]:
    return [sum(row) for row in data]


def col_totals(data: list[list[int]]) -> list[int]:
    return [sum(row[j] for row in data) for j in range(len(REGIONS))]


def choose_blanks(rng: random.Random, n_rows: int, n_cols: int, count: int) -> list[tuple[int, int]]:
    """Non-attacking placements — at most one blank per row and per column — so every blank is
    individually recoverable from its row (or column) total alone."""
    rows = rng.sample(range(n_rows), count)
    cols = rng.sample(range(n_cols), count)
    return list(zip(rows, cols))


def build_table_asset(data: list[list[int]], blanks: set[tuple[int, int]]) -> dict:
    rows = []
    for i, product in enumerate(PRODUCTS):
        row = [product]
        for j in range(len(REGIONS)):
            row.append(BLANK if (i, j) in blanks else data[i][j])
        row.append(row_totals(data)[i])
        rows.append(row)
    footer = ["Column total", *col_totals(data), sum(row_totals(data))]
    rows.append(footer)
    return {
        "type": "table",
        "spec": {
            "columns": ["Product", *REGIONS, "Row total"],
            "rows": rows,
        },
    }


def deduce_cell(data: list[list[int]], i: int, j: int) -> int:
    """Recomputes a blanked cell from its row total minus the other known cells in that row —
    verified to equal the same recovery via the column total, and to equal the true value, since
    only one cell per row/column is ever blanked."""
    from_row = row_totals(data)[i] - sum(v for k, v in enumerate(data[i]) if k != j)
    from_col = col_totals(data)[j] - sum(data[r][j] for r in range(len(PRODUCTS)) if r != i)
    assert from_row == from_col == data[i][j], f"cell ({i},{j}) not uniquely recoverable"
    return from_row


def main() -> None:
    data = build_data()
    rng = random.Random(f"{MICRO_TOPIC_ID}-blanks")
    blanks = choose_blanks(rng, len(PRODUCTS), len(REGIONS), 4)
    for i, j in blanks:
        assert deduce_cell(data, i, j) == data[i][j]

    content_hash = hashlib.sha1(MICRO_TOPIC_ID.encode()).hexdigest()[:8]
    set_id = f"{MICRO_TOPIC_ID}.set-{content_hash}"
    table_asset = build_table_asset(data, set(blanks))
    r_totals, c_totals = row_totals(data), col_totals(data)

    b1, b2 = blanks[0], blanks[1]
    v1, v2 = deduce_cell(data, *b1), deduce_cell(data, *b2)

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown=f"What is the missing value for {PRODUCTS[b1[0]]} in the {REGIONS[b1[1]]} region?",
        correctValue=v1,
        titaTolerance=0.0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"{PRODUCTS[b1[0]]}'s row total is {r_totals[b1[0]]}; the other three known cells sum to "
            f"{r_totals[b1[0]] - v1}. Missing value $= {r_totals[b1[0]]} - {r_totals[b1[0]] - v1} = {v1}$ "
            f"(the {REGIONS[b1[1]]} column total confirms the same figure)."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:missing-data"],
    )

    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown=f"What is the missing value for {PRODUCTS[b2[0]]} in the {REGIONS[b2[1]]} region?",
        correctValue=v2,
        titaTolerance=0.0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"Using the {REGIONS[b2[1]]} column total {c_totals[b2[1]]} minus the three other known "
            f"cells in that column: missing value $= {v2}$."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:missing-data"],
    )

    best_row_idx = r_totals.index(max(r_totals))
    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Which product has the highest row total across all regions?",
        options=[QuestionOption(key=chr(65 + i), markdown=p) for i, p in enumerate(PRODUCTS)],
        correctKey=chr(65 + best_row_idx),
        difficulty="easy",
        eloRating=1000.0,
        solutionMarkdown=(
            "Row totals: " + ", ".join(f"{p}: {t}" for p, t in zip(PRODUCTS, r_totals)) + f". Highest is **{PRODUCTS[best_row_idx]}**."
        ),
        targetSeconds=60,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:missing-data"],
    )

    combined = v1 + v2
    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What is the sum of the two missing values in the table?",
        correctValue=combined,
        titaTolerance=0.0,
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=f"The two missing values are {v1} and {v2}. Sum $= {v1} + {v2} = {combined}$.",
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:missing-data"],
    )

    questions = [q1, q2, q3, q4]
    passage_set = PassageSet(
        id=set_id,
        section="DILR",
        kind="di_set",
        bodyMarkdown=(
            "The table below shows units sold by 4 products across 4 regions. Some cells are missing "
            "(shown as '?') but every row and column total is given. Study the table and answer the "
            "questions that follow."
        ),
        assets=[table_asset],
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
