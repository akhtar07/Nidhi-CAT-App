"""
Content scale-up (round 2 of lessons): 7 more, deliberately spread across all three sections —
QA (permutations-combinations, progressions, divisibility-factors), DILR (arrangements, tables),
VARC (para-jumbles, main-idea) — since the previous 6 lessons were all QA and both DILR and VARC
still had zero lessons at all. Written in a warmer, more conversational, "explain it simply
before the formula" tone, per direct instruction: teach like she's meeting the idea for the
first time, then let her practise.

Same non-negotiable discipline as every lesson before it: every worked example's arithmetic
independently checked (see the comment above each one), nothing generated and trusted blind.

Run (from /pipeline, cat-pipeline conda env): python build_lessons_batch3.py
"""

from __future__ import annotations

import json
from pathlib import Path

from schemas import FormulaCard, Lesson, WorkedExample

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "content" / "lessons"


def permutations_combinations() -> Lesson:
    mt = "qa.modern.permutations-combinations"
    body = r"""
## Permutations & Combinations

Here's the one question that tells them apart: **does the order matter?**

- **Permutation** = arranging things where **who goes where** matters. Picking a President, a
  Vice-President, and a Secretary from a group of friends is a permutation — swapping who gets
  which job gives you a genuinely different outcome.
- **Combination** = just picking a group, where order doesn't matter. Picking 3 friends to be on
  a committee is a combination — it doesn't matter who you "picked first."

$$nPr = \frac{n!}{(n-r)!} \qquad nCr = \frac{n!}{r! \, (n-r)!}$$

Notice $nCr$ is just $nPr$ divided by $r!$ — because for every group you pick, there are $r!$
ways to arrange that same group in order, and combinations don't care about those arrangements.

### The two questions to ask yourself

1. Am I **selecting** a group, or **arranging** things in specific positions/roles? (selecting →
   combination; arranging/assigning roles → permutation)
2. Can something repeat, or is each item used at most once? (Most CAT questions: no repetition —
   read carefully when they do allow it.)
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown="In how many ways can 3 people be selected from a group of 6 to serve as President, Vice-President, and Secretary (three different roles)?",
            # Verified: 6P3 = 6*5*4 = 120.
            solutionMarkdown=(
                "The roles are different, so **order/role matters** — this is a permutation. "
                "$^6P_3 = \\dfrac{6!}{3!} = 6 \\times 5 \\times 4 = 120$."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-02",
            stemMarkdown="In how many ways can a committee of 3 be selected from the same group of 6 people?",
            # Verified: 6C3 = 20.
            solutionMarkdown=(
                "A committee has no roles — just a group. This is a combination. "
                "$^6C_3 = \\dfrac{6!}{3! \\, 3!} = \\dfrac{720}{6 \\times 6} = 20$. "
                "Notice this is exactly the permutation answer (120) divided by $3! = 6$ — the number of ways to "
                "reorder any one group of 3."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-03",
            stemMarkdown="How many 4-letter arrangements (not necessarily meaningful words) can be formed using the letters of 'LOGIC', with no letter repeated?",
            # Verified: LOGIC has 5 distinct letters. 5P4 = 5*4*3*2 = 120.
            solutionMarkdown=(
                "'LOGIC' has 5 distinct letters, and we're arranging 4 of them in order (position matters — "
                "'LOGI' and 'GILO' are different arrangements). $^5P_4 = 5 \\times 4 \\times 3 \\times 2 = 120$."
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-npr-ncr",
            microTopicId=mt,
            title="nPr vs nCr",
            bodyMarkdown=r"$$nPr = \frac{n!}{(n-r)!}, \qquad nCr = \frac{n!}{r!(n-r)!} = \frac{nPr}{r!}$$",
            exampleMarkdown="5P2 = 20 (order matters), 5C2 = 10 (order doesn't).",
        ),
    ]

    common_traps = [
        "Assigning distinct roles/positions is a permutation, even if the question doesn't use the word 'arrange.'",
        "nCr is nPr divided by r! — forgetting this division is the most common slip when a problem actually needs a combination.",
        "Read for repetition allowed vs not allowed — it changes the formula entirely (this lesson covers the no-repetition case, the default on CAT).",
    ]

    return Lesson(
        id=f"lesson.{mt}", microTopicId=mt, bodyMarkdown=body,
        workedExamples=worked_examples, formulaCards=formula_cards, commonTraps=common_traps,
        estReadMinutes=6,
    )


def progressions() -> Lesson:
    mt = "qa.algebra.progressions"
    body = r"""
## Progressions: AP & GP

A **progression** is just a list of numbers that follows a rule. Two kinds show up constantly:

- **Arithmetic Progression (AP)**: you get the next number by **adding** a fixed amount every
  time. $3, 7, 11, 15, \ldots$ — always add 4.
- **Geometric Progression (GP)**: you get the next number by **multiplying** by a fixed amount
  every time. $3, 6, 12, 24, \ldots$ — always multiply by 2.

$$\text{AP: } T_n = a + (n-1)d \qquad S_n = \frac{n}{2}\big(2a + (n-1)d\big)$$

$$\text{GP: } T_n = a \cdot r^{n-1} \qquad S_n = \frac{a(r^n - 1)}{r - 1} \ (r \neq 1)$$

where $a$ is the first term, $d$ is the common **difference** (AP), $r$ is the common **ratio** (GP).

### The trick for "find two unknowns" GP/AP questions

If you're given two terms of a GP (say $T_3$ and $T_6$), **divide** them — the $a$ cancels and
you're left with a power of $r$ you can solve directly. The worked example below does exactly this.
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown="Find the 15th term of the AP: 3, 7, 11, 15, ...",
            # Verified: a=3, d=4, T15 = 3+14*4 = 59.
            solutionMarkdown="$a=3$, $d=4$. $T_{15} = a + 14d = 3 + 14 \\times 4 = 59$.",
        ),
        WorkedExample(
            id=f"{mt}.we-02",
            stemMarkdown="Find the sum of the first 20 terms of the AP: 5, 8, 11, ...",
            # Verified: a=5, d=3, n=20. Sum = 10*(10+57) = 670.
            solutionMarkdown=(
                "$a=5$, $d=3$, $n=20$. $S_{20} = \\dfrac{20}{2}\\big(2(5) + 19(3)\\big) = 10 \\times (10+57) = 670$."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-03",
            stemMarkdown="The 3rd term of a GP is 12 and the 6th term is 96. Find the first term and the common ratio.",
            # Verified: T3=a r^2=12, T6=a r^5=96. r^3=8, r=2, a=3. Check T6=3*32=96.
            solutionMarkdown=(
                "$T_3 = ar^2 = 12$, $T_6 = ar^5 = 96$. Dividing: $\\dfrac{T_6}{T_3} = r^3 = \\dfrac{96}{12} = 8 "
                "\\implies r = 2$. Then $a = \\dfrac{12}{r^2} = \\dfrac{12}{4} = 3$. "
                "Check: $T_6 = 3 \\times 2^5 = 3 \\times 32 = 96$. ✓"
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-ap-gp",
            microTopicId=mt,
            title="AP and GP nth-term formulas",
            bodyMarkdown=r"AP: $T_n = a+(n-1)d$. GP: $T_n = ar^{n-1}$.",
            exampleMarkdown="AP 2,5,8,...: T10 = 2+9×3 = 29. GP 2,6,18,...: T5 = 2×3⁴ = 162.",
        ),
        FormulaCard(
            id=f"{mt}.fc-divide-trick",
            microTopicId=mt,
            title="Two-unknowns GP trick",
            bodyMarkdown="Given two terms of a GP, divide them to cancel $a$ and isolate a power of $r$.",
            exampleMarkdown="T2=6, T5=48 → r³=8 → r=2.",
        ),
    ]

    common_traps = [
        "Mixing up AP (add each time) and GP (multiply each time) — check the pattern of the given terms before picking a formula.",
        "In S_n, it's (n-1)d or r^(n-1), not nd or r^n — an off-by-one that's easy to make under time pressure.",
        "When given two GP terms, divide (don't subtract) to solve for r.",
    ]

    return Lesson(
        id=f"lesson.{mt}", microTopicId=mt, bodyMarkdown=body,
        workedExamples=worked_examples, formulaCards=formula_cards, commonTraps=common_traps,
        estReadMinutes=6,
    )


def divisibility_factors() -> Lesson:
    mt = "qa.numsys.divisibility-factors"
    body = r"""
## Divisibility Rules, Factors & Multiples

You almost never need to actually divide to check divisibility — there's a quick check for
each small number, and CAT rewards knowing them cold.

- **2**: last digit is even
- **3**: digit sum is divisible by 3
- **4**: last **two** digits form a number divisible by 4
- **5**: last digit is 0 or 5
- **6**: divisible by **both** 2 and 3
- **8**: last **three** digits divisible by 8
- **9**: digit sum divisible by 9
- **11**: (sum of digits at odd positions) − (sum at even positions, counting from the right) is divisible by 11

### Counting factors, the fast way

Break the number into primes. If $N = p_1^{a} \times p_2^{b} \times p_3^{c}$, the number of
factors is $(a+1)(b+1)(c+1)$ — one more than each exponent, multiplied together. This works
because each factor is built by independently choosing how many of each prime to include.
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown="Is 4578 divisible by 6?",
            # Verified: last digit 8 (even, /2 ok). digit sum 4+5+7+8=24, /3 ok (24/3=8). So yes.
            solutionMarkdown=(
                "Divisible by 6 means divisible by both 2 and 3. Last digit is 8 (even) → passes the 2-check. "
                "Digit sum $= 4+5+7+8=24$, and $24 \\div 3 = 8$ → passes the 3-check. **Yes**, 4578 is divisible by 6."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-02",
            stemMarkdown="Find the number of factors of 360.",
            # Verified: 360 = 2^3 * 3^2 * 5^1. (3+1)(2+1)(1+1) = 4*3*2 = 24.
            solutionMarkdown=(
                "$360 = 2^3 \\times 3^2 \\times 5^1$. Number of factors $= (3+1)(2+1)(1+1) = 4 \\times 3 \\times 2 = 24$."
            ),
        ),
        WorkedExample(
            id=f"{mt}.we-03",
            stemMarkdown="Is 9152 divisible by 11?",
            # Verified: digits right-to-left: 2,5,1,9. odd positions(1,3)=2+1=3. even(2,4)=5+9=14. diff=-11, /11 yes.
            solutionMarkdown=(
                "Reading digits from the right: 2 (position 1), 5 (position 2), 1 (position 3), 9 (position 4). "
                "Odd-position sum $= 2+1=3$. Even-position sum $= 5+9=14$. Difference $= 3-14=-11$, and $-11$ is "
                "divisible by 11. **Yes**, 9152 is divisible by 11."
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-factor-count",
            microTopicId=mt,
            title="Counting factors from prime powers",
            bodyMarkdown=r"$N = p_1^a p_2^b p_3^c \implies$ number of factors $= (a{+}1)(b{+}1)(c{+}1)$.",
            exampleMarkdown="72 = 2³×3² → factors = 4×3 = 12.",
        ),
        FormulaCard(
            id=f"{mt}.fc-div-6",
            microTopicId=mt,
            title="Combined divisibility (6, 12, 15...)",
            bodyMarkdown="To check divisibility by a composite number, break it into coprime factors and check each separately — divisible by 6 = divisible by 2 AND 3.",
            exampleMarkdown="Divisible by 12 → check divisible by both 4 and 3.",
        ),
    ]

    common_traps = [
        "Divisibility by a composite number (6, 12, 15...) means checking ALL its coprime prime-power factors, not just one.",
        "The factor-count formula adds 1 to each exponent before multiplying — forgetting the +1 is the most common slip.",
        "The rule for 11 alternates by position from the right — mixing up which positions are 'odd' is an easy error under time pressure.",
    ]

    return Lesson(
        id=f"lesson.{mt}", microTopicId=mt, bodyMarkdown=body,
        workedExamples=worked_examples, formulaCards=formula_cards, commonTraps=common_traps,
        estReadMinutes=6,
    )


def dilr_arrangements() -> Lesson:
    mt = "dilr.lr.arrangements"
    body = r"""
## Circular & Linear Arrangements

Think of this like a seating chart puzzle. You're given a handful of clues about where people
sit, and you need to figure out the **one** arrangement that makes every clue true at once.

### How to actually solve one (step by step)

1. **Draw the shape** — a circle for circular arrangements, a line of boxes for linear ones.
   Don't try to do it in your head.
2. **Start with the most specific clue** — one that pins someone down relative to a fixed point,
   or links two people directly ("X sits immediately clockwise of Y").
3. **Fill in what each clue forces**, one at a time. After each clue, ask: does this create a
   contradiction with what I've already placed? If yes, you misread something — recheck.
4. **The last person left goes in the last empty seat** — often the easiest "clue" is simply
   "there's nowhere else for them to go."
5. **Re-read every clue against your finished diagram** before answering — a puzzle isn't solved
   until every single clue checks out, not just the ones you used to build it.

### "Clockwise" matters

In a circular arrangement, clockwise and counter-clockwise are genuinely different arrangements
— don't assume symmetry. If a clue says "clockwise," it means going around the circle in one
specific direction, and mixing it up flips your whole answer.
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown="4 friends P, Q, R, S sit around a circular table. Clue 1: Q sits immediately clockwise of P. Clue 2: R sits immediately clockwise of Q. Where does S sit, relative to P, going clockwise?",
            # Verified by direct construction: order P,Q,R,(only seat left)=S. Clockwise from P: P->Q->R->S,
            # so S is 3 steps clockwise from P (2 people, Q and R, sit between them going that way).
            solutionMarkdown=(
                "Clue 1 fixes Q right after P (clockwise). Clue 2 fixes R right after Q. That places three of "
                "the four seats: $P \\to Q \\to R \\to \\_$. Only one seat is left, and only S is left to fill it — "
                "so S must be immediately clockwise of R (and, since it's a circle, immediately **before** P). "
                "Going clockwise from P, the order is P, Q, R, S — so **2 people (Q and R) sit between P and S** "
                "going clockwise from P."
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-method",
            microTopicId=mt,
            title="Solving method",
            bodyMarkdown="Draw it → place the most specific clue first → fill in what each clue forces → the last person takes the last seat → re-check every clue against the finished diagram.",
        ),
    ]

    common_traps = [
        "Clockwise and counter-clockwise are different arrangements — don't assume the puzzle is symmetric.",
        "Don't stop as soon as your diagram satisfies the clues you USED to build it — re-check every clue, including ones you placed early and might have drifted from.",
        "\"Immediately clockwise of X\" and \"immediately clockwise of the person clockwise of X\" are different distances — read the exact wording, not the gist.",
    ]

    return Lesson(
        id=f"lesson.{mt}", microTopicId=mt, bodyMarkdown=body,
        workedExamples=worked_examples, formulaCards=formula_cards, commonTraps=common_traps,
        estReadMinutes=5,
    )


def dilr_tables() -> Lesson:
    mt = "dilr.di.tables"
    body = r"""
## Reading Data Tables

A DI table question is rarely about hard maths — it's about reading carefully and not rushing.
Before you touch a single question, spend 20-30 seconds just **understanding the table**:

1. What does each **row** represent? What does each **column** represent?
2. What are the **units** (Rs., kg, %, thousands...)? Mixing these up is the #1 source of wrong
   answers in DI.
3. Are there **totals** given (row totals, column totals)? If so, they're a free way to check
   your own arithmetic — the row totals should always add up to the same grand total as the
   column totals.

### The "totals cross-check" trick

If a table gives you both row totals and column totals, they must agree:
$$\sum (\text{row totals}) = \sum (\text{column totals}) = \text{grand total}$$

If your calculated answer doesn't respect this, you've made an arithmetic slip somewhere — this
is a genuinely useful sanity check, not just a curiosity.
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown="A table shows sales (units) for two products across two months: Product A sold 40 in Jan and 60 in Feb. Product B sold 30 in Jan and 50 in Feb. What is the row total for Product A, and does it match the sum of column totals?",
            # Verified: row A=40+60=100. Column Jan=40+30=70, Feb=60+50=110. Sum cols=70+110=180.
            # Grand total = 100(A)+80(B)=180. Matches.
            solutionMarkdown=(
                "Product A's row total $= 40+60=100$. Product B's row total $= 30+50=80$. Grand total (both rows) "
                "$= 180$. Column totals: Jan $=40+30=70$, Feb $=60+50=110$; sum $=70+110=180$. "
                "Both ways give **180** — the cross-check passes."
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-cross-check",
            microTopicId=mt,
            title="Row/column totals cross-check",
            bodyMarkdown="Sum of row totals = sum of column totals = grand total. Use this to catch arithmetic slips.",
        ),
    ]

    common_traps = [
        "Mixing up which axis is rows vs columns when the question names a category — always re-check the header before reading a value.",
        "Ignoring stated units (thousands, %, Rs. crore) — a right number in the wrong unit is a wrong answer.",
        "Not using the totals cross-check when it's available — it's free error-detection.",
    ]

    return Lesson(
        id=f"lesson.{mt}", microTopicId=mt, bodyMarkdown=body,
        workedExamples=worked_examples, formulaCards=formula_cards, commonTraps=common_traps,
        estReadMinutes=4,
    )


def varc_para_jumbles() -> Lesson:
    mt = "varc.va.para-jumbles"
    body = r"""
## Para-jumbles

You're given a set of sentences in the wrong order, and you need to figure out the order they
were originally written in — one that reads as a single, coherent argument or story.

### How to find the starting sentence

The opening sentence usually:
- Introduces a topic or person **without** referring back to something ("This," "However," "The
  same...") — if a sentence starts with a pronoun pointing at something not yet introduced, it
  can't be first.
- Doesn't start with a conjunction like "But," "And," "So" — those connect to something before them.

### How to find links between sentences

Look for **explicit connectors**: pronouns ("it," "this," "they") that must refer to a specific
noun in an earlier sentence, transition words ("however," "therefore," "in contrast") that imply
a specific kind of sentence came before, and repeated or related nouns that thread two sentences
together.

### Build from both ends

Find the sentence that's obviously first, and (often easier) the sentence that's obviously
**last** — one that concludes or summarizes. Then work inward, linking pairs you're confident
about, rather than trying to solve the whole order in one pass.
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown=(
                "Arrange into a coherent paragraph:\n\n"
                "A. However, this convenience comes at a real cost to attention spans.\n"
                "B. Smartphones have made information instantly accessible.\n"
                "C. Indeed, studies increasingly link heavy phone use to shorter attention spans.\n"
                "D. As a result, anyone can look up any fact within seconds."
            ),
            # Verified by construction, each link forced by an explicit connector (not just topical
            # similarity, to avoid a genuinely ambiguous order): B names the subject (smartphones) with no
            # backward reference -> must open. D's "As a result" requires an immediately preceding cause,
            # which only B provides -> D follows B. A's "However...this convenience" requires a stated
            # convenience just before it, which B+D provide, and pivots to a NEW claim (cost) -> A follows D.
            # C's "Indeed" signals confirmation of the claim just made, which only A provides -> C is last.
            # Order: B, D, A, C.
            solutionMarkdown=(
                "**B** names the subject (smartphones) with nothing referring backward — a clean opening. "
                "**D** opens with 'As a result,' which demands an immediately preceding cause — only B "
                "provides one, so D follows B. **A** opens with 'However, this convenience,' which needs a "
                "stated convenience just before it (B+D) and then pivots to a new claim (a cost) — so A "
                "comes next. **C** opens with 'Indeed,' which confirms/elaborates the claim just made — only "
                "A's claim (a cost to attention spans) fits, so C is last. Order: **B, D, A, C**."
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-method",
            microTopicId=mt,
            title="Method",
            bodyMarkdown="Find the sentence with no backward reference (likely first) and the one that concludes (likely last). Link the rest via pronouns, connectors, and repeated nouns.",
        ),
    ]

    common_traps = [
        "A sentence starting with a pronoun ('This,' 'They,' 'It') almost never opens the paragraph — it needs an antecedent.",
        "Don't just look for topical similarity between two sentences — look for an actual grammatical link (a pronoun, a connector word).",
        "Solve from BOTH ends (first and last) rather than only trying to find the opening sentence.",
    ]

    return Lesson(
        id=f"lesson.{mt}", microTopicId=mt, bodyMarkdown=body,
        workedExamples=worked_examples, formulaCards=formula_cards, commonTraps=common_traps,
        estReadMinutes=5,
    )


def varc_main_idea() -> Lesson:
    mt = "varc.rc.main-idea"
    body = r"""
## Main Idea / Central Theme

A "main idea" question asks: if you had to summarize this entire passage in one sentence, what
would it be? Not a summary of every detail — the single thread the whole passage is actually
arguing or exploring.

### How to find it without re-reading the whole passage

1. The main idea is usually stated (or strongly implied) in the **first paragraph** or the
   **last paragraph** — authors tend to open with their thesis or close by restating it.
2. Ask: what does **every** paragraph have in common? A wrong answer choice often describes just
   ONE paragraph's detail, not the passage as a whole.
3. Beware options that are **too narrow** (true, but only about one part of the passage) or **too
   broad** (technically related, but goes beyond what the passage actually claims).

### The most common wrong-answer traps

- **A true detail, but not the main point.** The passage mentions it, but it's supporting
  evidence, not the thesis.
- **Too extreme.** The passage says something is "one factor," the wrong option says it's "the
  only factor."
- **Off-topic but plausible-sounding.** Related to the general subject, but not what this
  specific passage actually argues.
""".strip()

    worked_examples = [
        WorkedExample(
            id=f"{mt}.we-01",
            stemMarkdown=(
                "A passage opens by describing how early 20th-century economists assumed markets were "
                "always rational, spends two paragraphs on behavioral-economics experiments showing "
                "systematic irrational biases, and closes by arguing modern economic policy must account "
                "for these biases. Which best captures the main idea?\n\n"
                "A) Early economists were wrong about everything.\n"
                "B) Behavioral economics shows that accounting for real human irrationality, not just "
                "assumed rationality, should inform economic policy.\n"
                "C) A specific psychological experiment on loss aversion.\n"
                "D) Rational-market theory is used in most economics textbooks."
            ),
            solutionMarkdown=(
                "**(A)** is too extreme — the passage critiques one assumption, not \"everything.\" "
                "**(C)** is a supporting detail from the middle paragraphs, not the passage's overall point. "
                "**(D)** is true but is background, not the argument being made. "
                "**(B)** ties together the opening (the old assumption), the middle (evidence against it), "
                "and the close (the policy conclusion) — that's the actual thread running through the whole "
                "passage. **Answer: B.**"
            ),
        ),
    ]

    formula_cards = [
        FormulaCard(
            id=f"{mt}.fc-method",
            microTopicId=mt,
            title="Method",
            bodyMarkdown="Check the first and last paragraphs first. Reject options that are too narrow (one paragraph only), too extreme, or off-topic.",
        ),
    ]

    common_traps = [
        "Picking an option that's a true detail from one paragraph, not the passage's overall point.",
        "Picking an option that's more extreme than what the passage actually claims.",
        "Ignoring the concluding paragraph, which often restates the thesis most directly.",
    ]

    return Lesson(
        id=f"lesson.{mt}", microTopicId=mt, bodyMarkdown=body,
        workedExamples=worked_examples, formulaCards=formula_cards, commonTraps=common_traps,
        estReadMinutes=5,
    )


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    builders = [
        permutations_combinations, progressions, divisibility_factors,
        dilr_arrangements, dilr_tables, varc_para_jumbles, varc_main_idea,
    ]
    for build_fn in builders:
        lesson = build_fn()
        out_path = OUT_DIR / f"{lesson.microTopicId}.json"
        out_path.write_text(json.dumps(json.loads(lesson.model_dump_json()), indent=2) + "\n")
        print(f"Wrote {out_path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
