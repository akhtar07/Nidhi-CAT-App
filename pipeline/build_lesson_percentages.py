"""
Milestone 6: the first real Lesson, for qa.arith.percentages — needed for
"one micro-topic fully playable end to end" (SPEC.md §15's Milestone 6 row).

Originally authored (not sourced), per SPEC.md §6's rule that raw
third-party material is never committed and the "no fake/placeholder
content" rule in CLAUDE.md: every worked example's arithmetic below was
independently checked by hand before writing this (see comments), not
generated and trusted blind.

Run (from /pipeline, cat-pipeline conda env): python build_lesson_percentages.py
"""

from __future__ import annotations

import json
from pathlib import Path

from schemas import FormulaCard, Lesson, WorkedExample

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "content" / "lessons"

MICRO_TOPIC_ID = "qa.arith.percentages"

BODY_MARKDOWN = r"""
## Percentages

A percentage is just a fraction out of 100. $x\%$ of $N$ means $\dfrac{x}{100} \times N$.

### Percentage change

$$\text{\% change} = \frac{\text{New} - \text{Old}}{\text{Old}} \times 100$$

Always divide by the **original (old)** value, never the new one — this is the single most
common source of errors in CAT percentage questions.

### Increasing/decreasing by a percentage

"Increase $N$ by $x\%$" means multiply by $\left(1 + \dfrac{x}{100}\right)$, not add $x$ to $N$.
"Decrease $N$ by $x\%$" means multiply by $\left(1 - \dfrac{x}{100}\right)$.

### Successive percentage changes

If a quantity changes by $a\%$ and then by $b\%$ (in that order), the **net** change is:

$$a + b + \frac{ab}{100}\ \%$$

Use the actual signed values of $a$ and $b$ (a decrease is negative). This formula is why a
20% increase followed by a 20% decrease does **not** cancel out — see the first worked example.

### Reverse percentage

If a value $V$ remains after a $r\%$ decrease from the original $O$, then
$O = \dfrac{V}{1 - r/100}$. Don't just add $r\%$ of $V$ back — that's the same "wrong base"
mistake as percentage change.
""".strip()

WORKED_EXAMPLES = [
    WorkedExample(
        id=f"{MICRO_TOPIC_ID}.we-01",
        stemMarkdown="A number is increased by 20%, then the result is decreased by 20%. What is the net percentage change from the original number?",
        # Verified directly: 100 -> (x1.20) -> 120 -> (x0.80) -> 96. Net = (96-100)/100 = -4%.
        # Cross-checked via the successive-change formula: a=20, b=-20, net = 20 + (-20) + (20*-20)/100 = -4.
        solutionMarkdown=(
            "Take the original number as 100. After a 20% increase: $100 \\times 1.20 = 120$. "
            "After a 20% decrease on the new value: $120 \\times 0.80 = 96$. "
            "Net change $= \\dfrac{96 - 100}{100} \\times 100 = -4\\%$ — a **4% decrease**, not 0%."
        ),
        altSolutionMarkdown=(
            "Successive-change formula with $a = 20$, $b = -20$: "
            "$\\text{net} = a + b + \\dfrac{ab}{100} = 20 - 20 + \\dfrac{20 \\times (-20)}{100} = -4\\%$."
        ),
    ),
    WorkedExample(
        id=f"{MICRO_TOPIC_ID}.we-02",
        stemMarkdown="The price of an item is reduced by 25%. By what percentage must the new price be increased to restore the original price?",
        # Verified: original 100 -> reduced 25% -> 75. To go 75 -> 100: increase = (100-75)/75*100 = 33.33%.
        solutionMarkdown=(
            "Take the original price as 100. After a 25% reduction: $100 \\times 0.75 = 75$. "
            "To get back to 100 from 75, the required increase is measured on the **new** base (75): "
            "$\\dfrac{100 - 75}{75} \\times 100 = \\dfrac{25}{75} \\times 100 = 33.33\\%$."
        ),
        altSolutionMarkdown=(
            "Shortcut: if a value is reduced by $r\\%$, the increase needed to restore it is "
            "$\\dfrac{r}{100-r} \\times 100\\%$. Here $r=25$: $\\dfrac{25}{75}\\times 100 = 33.33\\%$."
        ),
    ),
    WorkedExample(
        id=f"{MICRO_TOPIC_ID}.we-03",
        stemMarkdown="Aisha scored 30% marks in an exam and failed by 25 marks. Riya scored 60% marks and got 20 marks more than the passing marks. Find the maximum marks and the passing marks.",
        # Verified: let M=max marks, P=passing marks. 0.3M = P-25, 0.6M = P+20.
        # Subtracting: 0.3M = 45 => M = 150. P = 0.3*150 + 25 = 70. Check: 0.6*150 = 90 = 70+20 = 90. Correct.
        solutionMarkdown=(
            "Let $M$ = maximum marks, $P$ = passing marks.\n\n"
            "Aisha: $0.30M = P - 25$\n\n"
            "Riya: $0.60M = P + 20$\n\n"
            "Subtracting the first equation from the second: $0.30M = 45 \\implies M = 150$.\n\n"
            "Then $P = 0.30 \\times 150 + 25 = 70$. Check: $0.60 \\times 150 = 90 = 70 + 20$. ✓\n\n"
            "**Maximum marks = 150, passing marks = 70.**"
        ),
    ),
]

FORMULA_CARDS = [
    FormulaCard(
        id=f"{MICRO_TOPIC_ID}.fc-percent-change",
        microTopicId=MICRO_TOPIC_ID,
        title="Percentage change",
        bodyMarkdown=r"$$\text{\% change} = \frac{\text{New} - \text{Old}}{\text{Old}} \times 100$$ Always divide by the *original* value.",
        exampleMarkdown="Old = 80, New = 100 → % change = $(100-80)/80 \\times 100 = 25\\%$.",
    ),
    FormulaCard(
        id=f"{MICRO_TOPIC_ID}.fc-successive-change",
        microTopicId=MICRO_TOPIC_ID,
        title="Successive percentage change",
        bodyMarkdown=r"$$\text{net \%} = a + b + \frac{ab}{100}$$ where $a, b$ are the two successive signed % changes.",
        exampleMarkdown="10% increase then 10% decrease: $10 - 10 + \\dfrac{10 \\times (-10)}{100} = -1\\%$ net, not 0%.",
    ),
]

COMMON_TRAPS = [
    "Successive percentage changes don't simply add — you must include the ab/100 cross term.",
    "A percentage decrease followed by an equal percentage increase does NOT return you to the original value (the net effect is always negative, by ab/100).",
    "Percentage change is always calculated on the original (base) value, not the new value — reversing this is a common trap.",
    "\"Increased by 20%\" means multiply by 1.20, not add 20 to the number.",
    "Reversing a percentage decrease: don't add r% of the reduced value back — divide by (1 - r/100) instead.",
]


def build() -> Lesson:
    return Lesson(
        id=f"lesson.{MICRO_TOPIC_ID}",
        microTopicId=MICRO_TOPIC_ID,
        bodyMarkdown=BODY_MARKDOWN,
        workedExamples=WORKED_EXAMPLES,
        formulaCards=FORMULA_CARDS,
        commonTraps=COMMON_TRAPS,
        estReadMinutes=6,
    )


def main() -> None:
    lesson = build()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"{MICRO_TOPIC_ID}.json"
    out_path.write_text(json.dumps(json.loads(lesson.model_dump_json()), indent=2) + "\n")
    print(f"Wrote {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
