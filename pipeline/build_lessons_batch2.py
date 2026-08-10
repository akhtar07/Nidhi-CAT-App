"""
Content scale-up: 5 more Lessons (only qa.arith.percentages had one, from Milestone 6's "one
micro-topic end to end" scope). Picked the next 5 highest-ROI QA topics that already have a
healthy question bank (roi=5, 7-12 questions each) so the Learn -> Drill loop is meaningful
immediately. Same discipline as build_lesson_percentages.py: originally authored, every worked
example's arithmetic independently checked by hand (see the comment above each one) before being
written, not generated and trusted blind.

Run (from /pipeline, cat-pipeline conda env): python build_lessons_batch2.py
"""

from __future__ import annotations

import json
from pathlib import Path

from schemas import FormulaCard, Lesson, WorkedExample

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "content" / "lessons"


def profit_loss_discount() -> Lesson:
    mt = "qa.arith.profit-loss-discount"
    body = r"""
## Profit, Loss & Discount

$$\text{Profit\%} = \frac{SP - CP}{CP} \times 100 \qquad \text{Loss\%} = \frac{CP - SP}{CP} \times 100$$

Profit/loss percentage is **always** calculated on the cost price (CP), never on the selling
price (SP), unless a question explicitly says "profit on SP."

### Marked price and discount

$$SP = MP \times \left(1 - \frac{d}{100}\right)$$

Discount is applied to the **marked price**, profit/loss is measured against the **cost price**
— these are two different bases, and mixing them up is the single most common error here.

### Successive discounts

Successive discounts combine exactly like successive percentage changes (see the Percentages
lesson): a 20% discount followed by a 10% discount is **not** a 30% discount.

$$\text{single equivalent discount} = 1 - (1 - d_1)(1 - d_2)$$
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown="A shopkeeper marks an item 40% above cost price and then gives a discount of 15%. What is his profit percentage?",
            # Verified: CP=100, MP=140, SP=140*0.85=119, profit=19%.
            solutionMarkdown=(
                "Take CP $= 100$. Marked price $= 100 \\times 1.40 = 140$. "
                "After a 15% discount on MP: $SP = 140 \\times 0.85 = 119$. "
                "$\\text{Profit\\%} = \\dfrac{119 - 100}{100} \\times 100 = 19\\%$."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-02",
            stemMarkdown="A trader sells two items at Rs. 1200 each. On one he gains 20% and on the other he loses 20%. What is his overall profit or loss percentage?",
            # Verified: CP1=1200/1.2=1000, CP2=1200/0.8=1500, total CP=2500, total SP=2400, loss=100/2500=4%.
            solutionMarkdown=(
                "$CP_1 = \\dfrac{1200}{1.20} = 1000$ (20% gain). $CP_2 = \\dfrac{1200}{0.80} = 1500$ (20% loss). "
                "Total CP $= 2500$, total SP $= 2400$. Loss $= 100$, $\\text{loss\\%} = \\dfrac{100}{2500} \\times 100 = 4\\%$. "
                "It is **not** breakeven — equal SP with equal +x%/-x% always nets a loss."
            ),
            altSolutionMarkdown=(
                "Shortcut: when two items are sold at the **same** SP, one at $x\\%$ gain and the other at $x\\%$ loss, "
                "the overall result is always a loss of $\\dfrac{x^2}{100}\\%$, regardless of the SP value. "
                "Here $x = 20$: loss $= \\dfrac{20^2}{100} = 4\\%$."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-03",
            stemMarkdown="Successive discounts of 20% and 10% are equivalent to a single discount of what percentage?",
            # Verified: 0.8*0.9=0.72, single discount = 28%.
            solutionMarkdown=(
                "Combined multiplier $= 0.80 \\times 0.90 = 0.72$, i.e. the buyer pays 72% of MP. "
                "Single equivalent discount $= 100 - 72 = 28\\%$ (not $20+10=30\\%$)."
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-profit-loss",
            microTopicId=mt,
            title="Profit / Loss %",
            bodyMarkdown=r"$$\text{Profit\%} = \frac{SP-CP}{CP}\times 100$$ Always on CP, never on SP.",
            exampleMarkdown="CP=80, SP=100 → profit% = $(100-80)/80 \\times 100 = 25\\%$.",
        ),
        FormulaCard(
            id=f"{mt}.fc-equal-sp-trick",
            microTopicId=mt,
            title="Equal-SP, equal-%, opposite-sign trick",
            bodyMarkdown=r"Two items sold at the **same** SP, one at $+x\%$ and one at $-x\%$: overall result is always a **loss** of $\dfrac{x^2}{100}\%$.",
            exampleMarkdown="x=10 → always a 1% net loss, never breakeven.",
        ),
    ]

    common_traps = [
        "Profit/loss % is calculated on CP, not SP — mixing the base is the #1 error here.",
        "Discount is applied to the marked price (MP), not the cost price — MP and CP are different bases entirely.",
        "Successive discounts don't add: 20% + 10% is a 28% single discount, not 30%.",
        "Equal SP with +x% gain on one item and -x% loss on another is always a net LOSS of x²/100%, never breakeven.",
    ]

    return Lesson(
        id=f"lesson.{mt}",
        microTopicId=mt,
        bodyMarkdown=body,
        workedExamples=worked_examples,
        formulaCards=formula_cards,
        commonTraps=common_traps,
        estReadMinutes=6,
    )


def averages() -> Lesson:
    mt = "qa.arith.averages-weighted-averages"
    body = r"""
## Averages & Weighted Averages

$$\text{Average} = \frac{\text{Sum of values}}{\text{Number of values}} \qquad \Rightarrow \qquad \text{Sum} = \text{Average} \times \text{Count}$$

Almost every average question is really a "sum" question in disguise — convert to sums first,
solve there, and only convert back to an average at the end if the question asks for one.

### Weighted average

$$\bar{x} = \frac{w_1 x_1 + w_2 x_2 + \cdots}{w_1 + w_2 + \cdots}$$

This is **not** the simple average of the group averages when the group sizes (weights) differ.

### When one value joins, leaves, or is replaced

Convert to sums: $\text{new sum} = \text{old sum} \pm \text{value changed}$, remembering that the
**count** ($n$) usually changes too when a member joins or leaves (but not on a simple swap).
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown="The average of 5 numbers is 28. If one number is excluded, the average of the remaining 4 numbers becomes 25. What is the excluded number?",
            # Verified: sum5=140, sum4=100, excluded=40.
            solutionMarkdown=(
                "Sum of 5 numbers $= 28 \\times 5 = 140$. Sum of remaining 4 $= 25 \\times 4 = 100$. "
                "Excluded number $= 140 - 100 = 40$."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-02",
            stemMarkdown="The average weight of 10 students is 42 kg. A new student joins and the average becomes 43 kg. What is the weight of the new student?",
            # Verified: old sum=420, new sum(11)=473, new student=53.
            solutionMarkdown=(
                "Old sum (10 students) $= 42 \\times 10 = 420$. New sum (11 students) $= 43 \\times 11 = 473$. "
                "New student's weight $= 473 - 420 = 53$ kg."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-03",
            stemMarkdown="A shopkeeper mixes 20 kg of rice costing Rs. 30/kg with 30 kg of rice costing Rs. 45/kg. Find the average cost per kg of the mixture.",
            # Verified: (20*30+30*45)/50 = (600+1350)/50 = 1950/50 = 39.
            solutionMarkdown=(
                "Weighted average $= \\dfrac{20 \\times 30 + 30 \\times 45}{20 + 30} = \\dfrac{600 + 1350}{50} = \\dfrac{1950}{50} = 39$ "
                "Rs./kg. Note this is closer to 45 than to 30 — correctly reflecting the larger weight (30 kg) on the higher price."
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-sum-trick",
            microTopicId=mt,
            title="Sum = Average × Count",
            bodyMarkdown="Convert average problems to sum problems first — it's almost always easier from there.",
            exampleMarkdown="Average of 6 numbers is 15 → sum = 90.",
        ),
        FormulaCard(
            id=f"{mt}.fc-weighted-average",
            microTopicId=mt,
            title="Weighted average",
            bodyMarkdown=r"$$\bar{x} = \frac{w_1x_1 + w_2x_2 + \cdots}{w_1 + w_2 + \cdots}$$",
            exampleMarkdown="10 items @ 20 and 5 items @ 50: weighted avg = (10×20+5×50)/15 = 30.",
        ),
    ]

    common_traps = [
        "Weighted average ≠ simple average of the group averages when group sizes differ.",
        "When a member joins or leaves, the count (n) changes too — forgetting this is the most common slip.",
        "Convert to sums before solving; working directly with averages usually leads to fraction errors.",
    ]

    return Lesson(
        id=f"lesson.{mt}",
        microTopicId=mt,
        bodyMarkdown=body,
        workedExamples=worked_examples,
        formulaCards=formula_cards,
        commonTraps=common_traps,
        estReadMinutes=5,
    )


def hcf_lcm() -> Lesson:
    mt = "qa.numsys.hcf-lcm"
    body = r"""
## HCF & LCM

For **exactly two** numbers $a, b$:

$$HCF(a,b) \times LCM(a,b) = a \times b$$

This does **not** extend to three or more numbers — compute HCF/LCM of 3+ numbers directly via
prime factorization instead.

### Via prime factorization

- **LCM** = product of the **highest** power of every prime appearing in any number.
- **HCF** = product of the **lowest** power of every prime common to **all** the numbers.

### "Leaves a remainder" problems

"Find the largest number that divides $X$ and $Y$, leaving remainder $r$ in each case" —
**subtract $r$ first**, then take the HCF of $(X-r)$ and $(Y-r)$.

### Word-problem cue

Dividing things into equal groups / finding the largest common measure → **HCF**. Events that
recur together / finding when things next coincide → **LCM**.
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown="Find the HCF and LCM of 36 and 60.",
            # Verified: 36=2^2*3^2, 60=2^2*3*5. HCF=2^2*3=12. LCM=2^2*3^2*5=180. Check 12*180=2160=36*60.
            solutionMarkdown=(
                "$36 = 2^2 \\times 3^2$, $60 = 2^2 \\times 3 \\times 5$. "
                "HCF $= 2^2 \\times 3 = 12$ (lowest common powers). "
                "LCM $= 2^2 \\times 3^2 \\times 5 = 180$ (highest powers of every prime). "
                "Check: $12 \\times 180 = 2160 = 36 \\times 60$. ✓"
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-02",
            stemMarkdown="Three bells toll at intervals of 12, 18, and 24 minutes. If they toll together at 6:00 AM, when will they next toll together?",
            # Verified: LCM(12,18,24): 12=2^2*3, 18=2*3^2, 24=2^3*3. LCM=2^3*3^2=72. 6:00+72min=7:12.
            solutionMarkdown=(
                "$12 = 2^2 \\times 3$, $18 = 2 \\times 3^2$, $24 = 2^3 \\times 3$. "
                "LCM $= 2^3 \\times 3^2 = 72$ minutes. "
                "Next together at $6{:}00 + 72\\text{ min} = 7{:}12$ AM."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-03",
            stemMarkdown="Find the greatest number that divides 245 and 1029, leaving remainder 5 in each case.",
            # Verified: 245-5=240, 1029-5=1024. gcd(240,1024): 240=2^4*3*5, 1024=2^10. HCF=2^4=16.
            solutionMarkdown=(
                "Subtract the remainder first: $245 - 5 = 240$, $1029 - 5 = 1024$. "
                "$240 = 2^4 \\times 3 \\times 5$, $1024 = 2^{10}$. "
                "HCF $= 2^4 = 16$."
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-product-rule",
            microTopicId=mt,
            title="HCF × LCM = product (two numbers only)",
            bodyMarkdown=r"$$HCF(a,b) \times LCM(a,b) = a \times b$$ Only valid for exactly two numbers.",
            exampleMarkdown="HCF(12,18)=6, LCM(12,18)=36, and 6×36=216=12×18.",
        ),
        FormulaCard(
            id=f"{mt}.fc-remainder-trick",
            microTopicId=mt,
            title="\"Leaves remainder r\" trick",
            bodyMarkdown="Subtract the remainder from each number **before** taking the HCF.",
            exampleMarkdown="Largest number dividing 50 and 80 leaving remainder 2: HCF(48,78)=6.",
        ),
    ]

    common_traps = [
        "HCF × LCM = product only works for exactly two numbers — not three or more.",
        "In \"leaves remainder r\" problems, subtract r from each number before computing the HCF — a very common miss.",
        "Confusing when to use HCF (equal grouping / largest common measure) vs LCM (things recurring together).",
    ]

    return Lesson(
        id=f"lesson.{mt}",
        microTopicId=mt,
        bodyMarkdown=body,
        workedExamples=worked_examples,
        formulaCards=formula_cards,
        commonTraps=common_traps,
        estReadMinutes=6,
    )


def pipes_cisterns() -> Lesson:
    mt = "qa.arith.time-work-pipes-cisterns"
    body = r"""
## Time & Work: Pipes & Cisterns

Treat this exactly like Time & Work, with one twist: an **outlet** pipe (a leak, or a pipe that
empties the tank) has a **negative** rate.

$$\text{Rate} = \frac{1}{\text{time to complete alone}} \qquad \text{Combined rate} = \sum \text{individual rates}$$

$$\text{Time} = \frac{1}{\text{combined rate}}$$

Inlet pipes: positive rate (they fill). Outlet pipes/leaks: negative rate (they empty). Never
average two times directly — always combine through rates.
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown="Pipe A can fill a tank in 6 hours, pipe B in 8 hours. If both pipes are opened together, how long will it take to fill the tank?",
            # Verified: 1/6+1/8 = 4/24+3/24 = 7/24. Time = 24/7 hours.
            solutionMarkdown=(
                "Rate of A $= \\dfrac{1}{6}$, rate of B $= \\dfrac{1}{8}$. Combined rate "
                "$= \\dfrac{1}{6} + \\dfrac{1}{8} = \\dfrac{4}{24} + \\dfrac{3}{24} = \\dfrac{7}{24}$. "
                "Time $= \\dfrac{24}{7} \\approx 3.43$ hours."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-02",
            stemMarkdown="Pipe A fills a tank in 5 hours. Pipe B can empty the full tank in 10 hours. If both are opened together, how long will it take to fill the tank?",
            # Verified: 1/5 - 1/10 = 2/10-1/10=1/10. Time=10 hours.
            solutionMarkdown=(
                "Rate of A (inlet) $= \\dfrac{1}{5}$. Rate of B (outlet) $= -\\dfrac{1}{10}$. "
                "Combined rate $= \\dfrac{1}{5} - \\dfrac{1}{10} = \\dfrac{2}{10} - \\dfrac{1}{10} = \\dfrac{1}{10}$. "
                "Time $= 10$ hours."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-03",
            stemMarkdown="Pipes A and B can fill a tank in 12 and 15 hours respectively. Both are opened together, but after 4 hours pipe A is closed. How much longer will pipe B alone take to fill the remaining tank?",
            # Verified: combined=1/12+1/15=5/60+4/60=9/60=3/20. 4h*3/20=12/20=3/5 done. Remaining=2/5.
            # B alone: (2/5)/(1/15)=(2/5)*15=6 hours.
            solutionMarkdown=(
                "Combined rate $= \\dfrac{1}{12} + \\dfrac{1}{15} = \\dfrac{5}{60} + \\dfrac{4}{60} = \\dfrac{9}{60} = \\dfrac{3}{20}$. "
                "In 4 hours: $4 \\times \\dfrac{3}{20} = \\dfrac{3}{5}$ of the tank is filled, leaving $\\dfrac{2}{5}$. "
                "B alone fills at $\\dfrac{1}{15}$ per hour, so time $= \\dfrac{2/5}{1/15} = \\dfrac{2}{5} \\times 15 = 6$ hours."
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-combined-rate",
            microTopicId=mt,
            title="Combined rate",
            bodyMarkdown=r"$$\text{Combined rate} = \sum \text{individual rates}, \quad \text{Time} = \frac{1}{\text{combined rate}}$$ Outlet/leak rates are negative.",
            exampleMarkdown="Fill in 4h, leak empties in 12h: combined = 1/4 - 1/12 = 1/6 → fills in 6h.",
        ),
    ]

    common_traps = [
        "An outlet pipe's rate is subtracted, never added.",
        "Never average two fill times directly (e.g. (6+8)/2) — you must combine through rates.",
        "When a pipe is closed partway through, compute work done so far, then solve the remaining fraction with only the pipe(s) still open.",
    ]

    return Lesson(
        id=f"lesson.{mt}",
        microTopicId=mt,
        bodyMarkdown=body,
        workedExamples=worked_examples,
        formulaCards=formula_cards,
        commonTraps=common_traps,
        estReadMinutes=6,
    )


def ratio_proportion() -> Lesson:
    mt = "qa.arith.ratio-proportion-variation"
    body = r"""
## Ratio, Proportion & Variation

A ratio $a:b$ is just the fraction $\dfrac{a}{b}$. A proportion $a:b :: c:d$ means
$\dfrac{a}{b} = \dfrac{c}{d}$, i.e. $ad = bc$ (cross-multiplication).

### Dividing a quantity in a given ratio

If a total $T$ is split in the ratio $p:q:r$, each share is
$\dfrac{p}{p+q+r} \times T$, $\dfrac{q}{p+q+r} \times T$, $\dfrac{r}{p+q+r} \times T$ — the total
number of "parts" is the **sum** of the ratio terms, not the number of people/groups.

### Combining two ratios

To combine $a:b$ and $b:c$ into $a:b:c$, scale both so the common term ($b$) matches — usually
via the LCM of the two $b$ values.

### Variation

- **Direct**: $y \propto x \implies y = kx$ (y grows as x grows).
- **Inverse**: $y \propto \dfrac{1}{x} \implies y = \dfrac{k}{x}$ (y shrinks as x grows).
- **Joint**: $y \propto \dfrac{x}{z} \implies y = \dfrac{kx}{z}$.
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown="Divide Rs. 1400 among A, B, and C in the ratio 2:3:5.",
            # Verified: total parts=10. A=280, B=420, C=700. Sum=1400.
            solutionMarkdown=(
                "Total parts $= 2+3+5 = 10$. $A = \\dfrac{2}{10}\\times 1400 = 280$, "
                "$B = \\dfrac{3}{10}\\times 1400 = 420$, $C = \\dfrac{5}{10}\\times 1400 = 700$. "
                "Check: $280+420+700 = 1400$. ✓"
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-02",
            stemMarkdown="If a:b = 2:3 and b:c = 4:5, find a:b:c.",
            # Verified: LCM(3,4)=12. a:b=2:3 -> x4 -> 8:12. b:c=4:5 -> x3 -> 12:15. Combined a:b:c=8:12:15.
            solutionMarkdown=(
                "Make the common term ($b$) equal: LCM(3, 4) = 12. "
                "$a:b = 2:3 = 8:12$ (×4). $b:c = 4:5 = 12:15$ (×3). "
                "Combined: $a:b:c = 8:12:15$."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-03",
            stemMarkdown="y varies directly as x and inversely as z. When x = 6, z = 2, y = 9. Find y when x = 8, z = 4.",
            # Verified: y=kx/z. 9=k*6/2=3k => k=3. y=3*8/4=6.
            solutionMarkdown=(
                "$y = \\dfrac{kx}{z}$. Using $x=6, z=2, y=9$: $9 = \\dfrac{k \\times 6}{2} = 3k \\implies k = 3$. "
                "When $x=8, z=4$: $y = \\dfrac{3 \\times 8}{4} = 6$."
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-dividing-ratio",
            microTopicId=mt,
            title="Dividing a total in a ratio",
            bodyMarkdown=r"Total parts = sum of ratio terms. Each share $= \dfrac{\text{its term}}{\text{total parts}} \times T$.",
            exampleMarkdown="Split 900 in ratio 1:2:6 → parts=9 → shares 100, 200, 600.",
        ),
        FormulaCard(
            id=f"{mt}.fc-variation",
            microTopicId=mt,
            title="Direct / inverse / joint variation",
            bodyMarkdown=r"Direct: $y=kx$. Inverse: $y=k/x$. Joint: $y=kx/z$. Solve for $k$ first from given values.",
            exampleMarkdown="y∝x², y=20 at x=5 → k=0.8 → y=(0.8)(100)=80 at x=10.",
        ),
    ]

    common_traps = [
        "\"Divide in ratio\" — total parts is the sum of the ratio terms, not the number of people.",
        "Combining two ratios requires matching the common term first (via LCM), not just multiplying blindly.",
        "Inverse variation means y goes DOWN as x goes up — easy to accidentally treat it as direct.",
    ]

    return Lesson(
        id=f"lesson.{mt}",
        microTopicId=mt,
        bodyMarkdown=body,
        workedExamples=worked_examples,
        formulaCards=formula_cards,
        commonTraps=common_traps,
        estReadMinutes=6,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for build_fn in [profit_loss_discount, averages, hcf_lcm, pipes_cisterns, ratio_proportion]:
        lesson = build_fn()
        out_path = OUT_DIR / f"{lesson.microTopicId}.json"
        out_path.write_text(json.dumps(json.loads(lesson.model_dump_json()), indent=2) + "\n")
        print(f"Wrote {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
