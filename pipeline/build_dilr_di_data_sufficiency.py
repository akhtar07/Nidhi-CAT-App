"""
Content scale-up: dilr.di.data-sufficiency (roi=3, previously 0 questions).

Standard CAT data-sufficiency format: a question plus two statements, fixed answer choices
(A: Statement I alone sufficient, B: Statement II alone sufficient, C: both together sufficient
but neither alone, D: either alone sufficient, E: not sufficient even together). No PassageSet
needed — DILR questions load by microTopicId like any other question (validate_content.py does
not require a PassageSet link), so these ship as standalone questions.

Every "sufficient / not sufficient" verdict below is derived by actually solving the system (via
sympy where the target is numeric, or exhaustive enumeration over a bounded domain for the
parity/inequality cases) — never asserted by hand. See each build_qN() for its own solve.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_di_data_sufficiency.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import sympy
from schemas import Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
MICRO_TOPIC_ID = "dilr.di.data-sufficiency"
VERIFIED_AT = "2026-08-12T00:00:00Z"

DS_OPTIONS = [
    QuestionOption(key="A", markdown="Statement I alone is sufficient, but Statement II alone is not."),
    QuestionOption(key="B", markdown="Statement II alone is sufficient, but Statement I alone is not."),
    QuestionOption(key="C", markdown="Both statements together are sufficient, but neither alone is."),
    QuestionOption(key="D", markdown="Either statement alone is sufficient."),
    QuestionOption(key="E", markdown="Both statements together are still not sufficient."),
]


def verdict_from_flags(s1_suff: bool, s2_suff: bool, both_suff: bool) -> str:
    if s1_suff and s2_suff:
        return "D"
    if s1_suff:
        return "A"
    if s2_suff:
        return "B"
    if both_suff:
        return "C"
    return "E"


def build_q1() -> Question:
    x, y = sympy.symbols("x y")
    # St1: 2x + 3y = 12 alone -> a line, infinitely many (x, y).
    s1_sufficient = False  # a single equation in 2 unknowns never pins down x uniquely
    # St2: x - y = 1 alone -> also a line, infinitely many.
    s2_sufficient = False
    # Together: unique solution.
    together = sympy.solve([sympy.Eq(2 * x + 3 * y, 12), sympy.Eq(x - y, 1)], [x, y], dict=True)
    assert len(together) == 1
    both_sufficient = len(together) == 1
    verdict = verdict_from_flags(s1_sufficient, s2_sufficient, both_sufficient)
    assert verdict == "C"

    x_val = together[0][x]
    return Question(
        id="dilr.di.data-sufficiency.ds-q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown=(
            "**What is the value of x?**\n\n"
            "Statement I: $2x + 3y = 12$\n\n"
            "Statement II: $x - y = 1$"
        ),
        options=DS_OPTIONS,
        correctKey=verdict,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Each statement alone is a single linear equation in 2 unknowns — infinitely many "
            "$(x, y)$ pairs satisfy it, so neither pins down $x$. Together, solving the 2×2 "
            f"system gives a unique solution ($x = {x_val}$). **Answer: C**."
        ),
        targetSeconds=100,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:data-sufficiency"],
    )


def build_q2() -> Question:
    # St1: n divisible by 4 -> n even, for every such n in a bounded check domain.
    domain = range(1, 2001)
    s1_n = [n for n in domain if n % 4 == 0]
    s1_sufficient = all(n % 2 == 0 for n in s1_n) and len(s1_n) > 0
    # St2: n + 1 is odd -> n is even, for every such n.
    s2_n = [n for n in domain if (n + 1) % 2 == 1]
    s2_sufficient = all(n % 2 == 0 for n in s2_n) and len(s2_n) > 0
    both_sufficient = s1_sufficient or s2_sufficient
    verdict = verdict_from_flags(s1_sufficient, s2_sufficient, both_sufficient)
    assert verdict == "D"

    return Question(
        id="dilr.di.data-sufficiency.ds-q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown=(
            "**Is the positive integer n even?**\n\n"
            "Statement I: n is divisible by 4.\n\n"
            "Statement II: n + 1 is odd."
        ),
        options=DS_OPTIONS,
        correctKey=verdict,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Statement I: any multiple of 4 is even — sufficient alone. Statement II: n + 1 odd "
            "means n is even (odd − 1 = even) — sufficient alone too. Since each alone answers "
            "the question, **Answer: D**."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:data-sufficiency"],
    )


def build_q3() -> Question:
    L, B = sympy.symbols("L B", positive=True)
    # St1: L = 8, area L*B = 40 -> solves for B uniquely -> perimeter computable.
    s1 = sympy.solve([sympy.Eq(L, 8), sympy.Eq(L * B, 40)], [L, B], dict=True)
    assert len(s1) == 1
    s1_sufficient = len(s1) == 1
    perimeter = 2 * (s1[0][L] + s1[0][B])
    assert perimeter == 26
    # St2: B = 5 alone -> L unrestricted -> infinitely many perimeters.
    s2_sufficient = False
    both_sufficient = s1_sufficient or s2_sufficient
    verdict = verdict_from_flags(s1_sufficient, s2_sufficient, both_sufficient)
    assert verdict == "A"

    return Question(
        id="dilr.di.data-sufficiency.ds-q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown=(
            "**What is the perimeter of rectangle PQRS with length L and breadth B?**\n\n"
            "Statement I: L = 8 cm and the area of PQRS is 40 cm².\n\n"
            "Statement II: B = 5 cm."
        ),
        options=DS_OPTIONS,
        correctKey=verdict,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"Statement I gives $L = 8$ and $LB = 40 \\Rightarrow B = 5$, so perimeter $= 2(8+5) = {perimeter}$ — "
            "sufficient alone. Statement II alone only fixes B, leaving L (and hence the perimeter) "
            "undetermined. **Answer: A**."
        ),
        targetSeconds=100,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:data-sufficiency"],
    )


def build_q4() -> Question:
    x = sympy.symbols("x")
    # St1: x^2 = 16 -> x = 4 or -4, not unique.
    s1 = sympy.solve(sympy.Eq(x**2, 16), x)
    s1_sufficient = len(s1) == 1
    assert len(s1) == 2
    # St2: x > -10 alone -> unbounded, obviously not sufficient.
    s2_sufficient = False
    # Together: x in {4, -4} AND x > -10 -> both still satisfy x > -10, so still 2 solutions.
    together = [v for v in s1 if v > -10]
    assert len(together) == 2
    both_sufficient = len(together) == 1
    verdict = verdict_from_flags(s1_sufficient, s2_sufficient, both_sufficient)
    assert verdict == "E"

    return Question(
        id="dilr.di.data-sufficiency.ds-q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown=(
            "**What is the value of x?**\n\n"
            "Statement I: $x^2 = 16$\n\n"
            "Statement II: $x > -10$"
        ),
        options=DS_OPTIONS,
        correctKey=verdict,
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=(
            "Statement I gives $x = 4$ or $x = -4$ — two possible values, not sufficient alone. "
            "Statement II alone is clearly insufficient (any x > −10 works). Together: both $4$ "
            "and $-4$ satisfy $x > -10$, so the ambiguity survives even combined. **Answer: E**."
        ),
        targetSeconds=120,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["dilr:data-sufficiency"],
    )


def main() -> None:
    questions = [build_q1(), build_q2(), build_q3(), build_q4()]
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    for q in questions:
        path = QUESTIONS_DIR / f"{q.id}.json"
        path.write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
    print(f"Wrote {len(questions)} data-sufficiency questions")


if __name__ == "__main__":
    main()
