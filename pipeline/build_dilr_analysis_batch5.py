"""
Additional sets for the four DI topics that are about reasoning over data rather than reading
a chart: growth-cagr, missing-data, data-sufficiency and caselets.

Three new sets each for the first three, two for caselets (which already had seven questions),
bringing all four to at least 15 per SPEC.md §16.

These are hand-written rather than archetype-driven. The archetype library in
`dilr_di_archetypes.py` varies the *operation* over a fixed categories/series shape, and none
of these four topics has that shape: a data-sufficiency item is a pair of statements plus a
fixed five-option ladder, a missing-data item is a table with a hole and enough constraints to
fill it, and a caselet has no chart at all.

Every numeric claim is computed and then asserted against an independently worked-out literal.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_analysis_batch5.py
"""

from __future__ import annotations

from dilr_common import QSpec, SetPlan, emit_all, fmt

# The five-way ladder every data-sufficiency question in this batch uses. Kept identical across
# questions on purpose: in the real exam the options never move, and part of what is being
# trained is picking the right rung fast rather than re-reading five long sentences.
DS_OPTIONS = [
    "Statement I alone is sufficient, but statement II alone is not.",
    "Statement II alone is sufficient, but statement I alone is not.",
    "Both statements together are sufficient, but neither alone is.",
    "Each statement alone is sufficient.",
    "Statements I and II together are not sufficient.",
]
DS_I_ONLY, DS_II_ONLY, DS_BOTH, DS_EITHER, DS_NEITHER = DS_OPTIONS


def ds_question(stem: str, one: str, two: str, answer: str, solution: str, difficulty: str, seconds: int) -> QSpec:
    return QSpec(
        stem=f"{stem}\n\n**I.** {one}\n\n**II.** {two}",
        options=list(DS_OPTIONS),
        correct=answer,
        difficulty=difficulty,
        target_seconds=seconds,
        solution=solution,
    )


# ---------------------------------------------------------------------------
# Growth and CAGR
# ---------------------------------------------------------------------------


def growth_revenue() -> SetPlan:
    years = ["2021", "2022", "2023", "2024"]
    revenue = [128, 192, 288, 432]
    assert [round(revenue[i] / revenue[i - 1], 4) for i in range(1, 4)] == [1.5, 1.5, 1.5]
    total = sum(revenue)
    assert total == 1040
    cagr = (revenue[-1] / revenue[0]) ** (1 / 3) - 1
    assert round(cagr * 100, 6) == 50
    projected = revenue[-1] * 1.5**2
    assert projected == 972

    return SetPlan(
        micro_topic="dilr.di.growth-cagr",
        slug="steady-revenue",
        body=(
            "A company's annual revenue, in Rs crore, was:\n\n"
            "- 2021: 128\n- 2022: 192\n- 2023: 288\n- 2024: 432\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="By what percentage did revenue grow from 2021 to 2022?",
                value=50,
                tolerance=0.05,
                difficulty="easy",
                target_seconds=50,
                solution="$\\dfrac{192 - 128}{128} \\times 100 = 50\\%$.",
            ),
            QSpec(
                stem="What was the company's total revenue over the four years, in Rs crore?",
                value=total,
                difficulty="easy",
                target_seconds=50,
                solution=f"$128 + 192 + 288 + 432 = {fmt(total)}$, so **Rs {fmt(total)} crore**.",
            ),
            QSpec(
                stem="What was the compound annual growth rate of revenue from 2021 to 2024, as a percentage?",
                value=50,
                tolerance=0.05,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "From 2021 to 2024 is **3** growth periods, not 4 — count the gaps between the "
                    "years, not the years themselves.\n\n"
                    "$\\text{CAGR} = \\left(\\dfrac{432}{128}\\right)^{1/3} - 1 = (3.375)^{1/3} - 1 = 1.5 - 1 = 0.5$\n\n"
                    "**50%**. Here every year-on-year growth rate is already 50%, so the CAGR must equal "
                    "it — a constant growth rate is its own compound rate. Using 4 periods instead of 3 "
                    "would give about 35.7%, and that off-by-one is the most common CAGR error."
                ),
            ),
            QSpec(
                stem=(
                    "If revenue continues to grow at the same annual rate, what will it be in 2026, in "
                    "Rs crore?"
                ),
                value=projected,
                difficulty="hard",
                target_seconds=100,
                solution=(
                    "2026 is two years past 2024, so apply the 50% growth factor twice:\n\n"
                    "$432 \\times 1.5 \\times 1.5 = 648 \\times 1.5 = 972$\n\n"
                    f"**Rs {fmt(projected)} crore**. Adding $2 \\times 50\\% = 100\\%$ to get 864 is the trap: "
                    "growth compounds, so two years of 50% is a factor of 2.25, not 2."
                ),
            ),
        ],
    )


def growth_population() -> SetPlan:
    pop = [50000, 60000, 66000, 82500, 79200]
    years = ["2019", "2020", "2021", "2022", "2023"]
    rates = [20, 10, 25, -4]
    for i, r in enumerate(rates):
        assert round(pop[i] * (1 + r / 100), 6) == pop[i + 1], (i, r)
    overall = (pop[-1] - pop[0]) / pop[0] * 100
    assert round(overall, 2) == 58.4
    jumps = [pop[i + 1] - pop[i] for i in range(4)]
    assert jumps == [10000, 6000, 16500, -3300]
    biggest = years[jumps.index(max(jumps)) + 1]
    assert biggest == "2022"
    steady = 50000 * 1.1**4
    assert round(steady, 4) == 73205

    return SetPlan(
        micro_topic="dilr.di.growth-cagr",
        slug="town-population",
        body=(
            "The population of a town was 50,000 at the end of 2019. It then changed as follows:\n\n"
            "- 2020: up 20%\n- 2021: up 10%\n- 2022: up 25%\n- 2023: down 4%\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="What was the town's population at the end of 2021?",
                value=66000,
                difficulty="easy",
                target_seconds=60,
                solution=(
                    "$50{,}000 \\times 1.20 = 60{,}000$ at the end of 2020, then "
                    "$60{,}000 \\times 1.10 = 66{,}000$.\n\n**66,000**."
                ),
            ),
            QSpec(
                stem="By what percentage did the population change over the whole period, end-2019 to end-2023?",
                value=58.4,
                tolerance=0.05,
                difficulty="medium",
                target_seconds=100,
                solution=(
                    "Chain the factors rather than adding the percentages:\n\n"
                    "$1.20 \\times 1.10 \\times 1.25 \\times 0.96 = 1.584$\n\n"
                    "So the population is 1.584 times its starting value, a rise of **58.4%**. Adding the "
                    "four rates gives $20 + 10 + 25 - 4 = 51\\%$, which is wrong — successive percentages "
                    "never add."
                ),
            ),
            QSpec(
                stem="In which year did the population increase by the largest number of people?",
                options=["2020", "2021", "2022", "2023"],
                correct=biggest,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Absolute changes:\n\n"
                    "- 2020: $60{,}000 - 50{,}000 = 10{,}000$\n"
                    "- 2021: $66{,}000 - 60{,}000 = 6{,}000$\n"
                    "- 2022: $82{,}500 - 66{,}000 = 16{,}500$\n"
                    "- 2023: $79{,}200 - 82{,}500 = -3{,}300$\n\n"
                    "**2022**. Note 2020 has the highest **percentage** rise (20%) and only the second-largest "
                    "absolute rise, because it applies to a smaller base."
                ),
            ),
            QSpec(
                stem=(
                    "Suppose the town had instead grown at a constant 10% a year from its end-2019 level. "
                    "What would its population have been at the end of 2023?"
                ),
                value=73205,
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Four years of compounding at 10%:\n\n"
                    "$50{,}000 \\times 1.1^4 = 50{,}000 \\times 1.4641 = 73{,}205$\n\n"
                    "**73,205**. Worth memorising: $1.1^2 = 1.21$, $1.1^3 = 1.331$, $1.1^4 = 1.4641$. The "
                    "simple-interest answer of $50{,}000 \\times 1.4 = 70{,}000$ is 3,205 short — the gap "
                    "between simple and compound growth over just four years."
                ),
            ),
        ],
    )


def growth_investments() -> SetPlan:
    a_start, a_end, a_years = 8000, 27000, 3
    b_start, b_end, b_years = 6250, 16000, 2
    a_gain = a_end - a_start
    assert a_gain == 19000
    a_cagr = (a_end / a_start) ** (1 / a_years) - 1
    assert round(a_cagr * 100, 6) == 50
    b_cagr = (b_end / b_start) ** (1 / b_years) - 1
    assert round(b_cagr * 100, 6) == 60
    a_total = (a_end - a_start) / a_start * 100
    b_total = (b_end - b_start) / b_start * 100
    assert round(a_total, 2) == 237.5 and round(b_total, 2) == 156.0

    return SetPlan(
        micro_topic="dilr.di.growth-cagr",
        slug="two-investments",
        body=(
            "Two investments were made and later valued:\n\n"
            "- Investment A: Rs 8,000 grew to Rs 27,000 over 3 years\n"
            "- Investment B: Rs 6,250 grew to Rs 16,000 over 2 years\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="What was the absolute gain on Investment A, in rupees?",
                value=a_gain,
                difficulty="easy",
                target_seconds=40,
                solution=f"$27{{,}}000 - 8{{,}}000 = {fmt(a_gain)}$, so **Rs {fmt(a_gain)}**.",
            ),
            QSpec(
                stem="What was the compound annual growth rate of Investment A, as a percentage?",
                value=50,
                tolerance=0.05,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "$\\left(\\dfrac{27000}{8000}\\right)^{1/3} - 1 = "
                    "\\left(\\dfrac{27}{8}\\right)^{1/3} - 1 = \\dfrac{3}{2} - 1 = 0.5$\n\n"
                    "**50%**. Spotting that 27 and 8 are both perfect cubes turns a cube root into "
                    "mental arithmetic — CAT sets these ratios deliberately."
                ),
            ),
            QSpec(
                stem="What was the compound annual growth rate of Investment B, as a percentage?",
                value=60,
                tolerance=0.05,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "$\\left(\\dfrac{16000}{6250}\\right)^{1/2} - 1 = (2.56)^{1/2} - 1 = 1.6 - 1 = 0.6$\n\n"
                    "**60%**, since $1.6^2 = 2.56$."
                ),
            ),
            QSpec(
                stem="Which investment grew more in percentage terms over its own holding period?",
                options=[
                    "Investment A",
                    "Investment B",
                    "Both grew by the same percentage",
                    "Cannot be determined from the data given",
                ],
                correct="Investment A",
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Total growth over the whole holding period:\n\n"
                    "- A: $\\dfrac{27000 - 8000}{8000} \\times 100 = 237.5\\%$\n"
                    "- B: $\\dfrac{16000 - 6250}{6250} \\times 100 = 156\\%$\n\n"
                    "**Investment A**, and this is the point of the set: B has the higher annual rate "
                    "(60% against 50%) and still grew less overall, because it compounded for two years "
                    "instead of three. A CAGR is only comparable across investments held for the **same** "
                    "length of time."
                ),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Missing data
# ---------------------------------------------------------------------------


def missing_sales() -> SetPlan:
    months = ["Jan", "Feb", "Mar", "Apr"]
    rows = {"Anil": [12, 15, None, 18], "Bina": [20, 14, 16, 10], "Chetan": [8, 11, 13, 9]}
    row_totals = {"Anil": 63, "Bina": 60, "Chetan": 41}
    anil_mar = row_totals["Anil"] - sum(v for v in rows["Anil"] if v is not None)
    assert anil_mar == 18
    filled = {"Anil": [12, 15, anil_mar, 18], "Bina": rows["Bina"], "Chetan": rows["Chetan"]}
    for name, values in filled.items():
        assert sum(values) == row_totals[name], name
    col_totals = [sum(v[i] for v in filled.values()) for i in range(4)]
    assert col_totals == [40, 40, 47, 37]
    grand = sum(row_totals.values())
    assert grand == 164 == sum(col_totals)
    anil_share = row_totals["Anil"] / grand * 100
    assert round(anil_share, 2) == 38.41

    table = {
        "type": "table",
        "spec": {
            "columns": ["Salesperson", *months, "Total"],
            "rows": [
                ["Anil", "12", "15", "?", "18", "63"],
                ["Bina", "20", "14", "16", "10", "60"],
                ["Chetan", "8", "11", "13", "9", "41"],
            ],
        },
    }

    return SetPlan(
        micro_topic="dilr.di.missing-data",
        slug="sales-grid",
        body=(
            "The table below shows units sold by three salespeople over four months, with each "
            "person's four-month total in the last column. One entry has been left out.\n\n"
            "Study the table and answer the questions that follow."
        ),
        assets=[table],
        questions=[
            QSpec(
                stem="How many units did Anil sell in March?",
                value=anil_mar,
                difficulty="easy",
                target_seconds=50,
                solution=(
                    "Anil's row must add to his stated total of 63:\n\n"
                    "$63 - (12 + 15 + 18) = 63 - 45 = 18$\n\n"
                    f"**{fmt(anil_mar)} units**."
                ),
            ),
            QSpec(
                stem="What is the grand total of units sold by all three salespeople over the four months?",
                value=grand,
                difficulty="medium",
                target_seconds=60,
                solution=(
                    f"Add the row totals: $63 + 60 + 41 = {fmt(grand)}$.\n\n"
                    "**164 units**. Adding the four monthly columns gives "
                    "$40 + 40 + 47 + 37 = 164$ as well — a free check that the missing entry was "
                    "filled in correctly."
                ),
            ),
            QSpec(
                stem="In which month did the three salespeople together sell the most units?",
                options=months,
                correct="Mar",
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "Column totals, once the gap is filled: "
                    + ", ".join(f"{m} {fmt(t)}" for m, t in zip(months, col_totals))
                    + ".\n\n**March**, at 47 units. March cannot be totalled at all until the missing "
                    "entry is recovered, which is why that question comes first."
                ),
            ),
            QSpec(
                stem="Anil accounted for what percentage of total units sold? Give the answer to two decimal places.",
                value=38.41,
                tolerance=0.05,
                difficulty="hard",
                target_seconds=100,
                solution=(
                    f"$\\dfrac{{63}}{{164}} \\times 100 = {fmt(round(anil_share, 2))}\\%$\n\n"
                    "**38.41%**. A useful sanity check: three people would average 33.3% each, so a "
                    "figure a little above a third is the right neighbourhood."
                ),
            ),
        ],
    )


def missing_marks() -> SetPlan:
    known = {"Prisha": 72, "Qadir": 65, "Sana": 81}
    average = 74
    total = average * 4
    assert total == 296
    rahul = total - sum(known.values())
    assert rahul == 78
    marks = {**known, "Rahul": rahul}
    spread = max(marks.values()) - min(marks.values())
    assert spread == 16
    with_fifth = (total + 89) / 5
    assert with_fifth == 77
    needed_total = 76 * 4
    needed_rahul = needed_total - sum(known.values())
    assert needed_rahul == 86

    return SetPlan(
        micro_topic="dilr.di.missing-data",
        slug="class-marks",
        body=(
            "Four students sat a test marked out of 100. Three of the scores are known:\n\n"
            "- Prisha: 72\n- Qadir: 65\n- Rahul: not recorded\n- Sana: 81\n\n"
            "The average of all four scores is 74.\n\nAnswer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="What did Rahul score?",
                value=rahul,
                difficulty="easy",
                target_seconds=60,
                solution=(
                    "An average of 74 over 4 students means a total of $74 \\times 4 = 296$.\n\n"
                    "$296 - (72 + 65 + 81) = 296 - 218 = 78$\n\n"
                    f"**{fmt(rahul)}**."
                ),
            ),
            QSpec(
                stem="What is the difference between the highest and the lowest of the four scores?",
                value=spread,
                difficulty="medium",
                target_seconds=50,
                solution=f"Highest 81 (Sana), lowest 65 (Qadir): $81 - 65 = {fmt(spread)}$.",
            ),
            QSpec(
                stem="A fifth student then scores 89. What is the average of all five scores?",
                value=with_fifth,
                difficulty="medium",
                target_seconds=70,
                solution=(
                    f"$\\dfrac{{296 + 89}}{{5}} = \\dfrac{{385}}{{5}} = {fmt(with_fifth)}$\n\n"
                    "**77**. Faster: the new score is 15 above the old average of 74, and spreading that "
                    "surplus over 5 students lifts the average by 3."
                ),
            ),
            QSpec(
                stem="What would Rahul have needed to score for the four-student average to be 76?",
                value=needed_rahul,
                difficulty="hard",
                target_seconds=90,
                solution=(
                    "A 76 average over 4 students needs a total of $76 \\times 4 = 304$.\n\n"
                    "$304 - 218 = 86$\n\n"
                    f"**{fmt(needed_rahul)}**. Shortcut: lifting the average by 2 across 4 students needs "
                    "8 extra marks, and $78 + 8 = 86$."
                ),
            ),
        ],
    )


def missing_shifts() -> SetPlan:
    total = 1200
    shift1 = total * 0.35
    shift3 = total * 2 / 5
    shift2 = total - shift1 - shift3
    assert shift1 == 420 and shift3 == 480 and shift2 == 300
    shift2_share = shift2 / total * 100
    assert shift2_share == 25
    defects = shift1 * 0.02 + shift2 * 0.05 + shift3 * 0.03
    assert round(defects, 4) == 37.8

    return SetPlan(
        micro_topic="dilr.di.missing-data",
        slug="factory-shifts",
        body=(
            "A factory produced 1,200 units in a day across three shifts. Shift 1 produced 35% of "
            "the day's output and Shift 3 produced two-fifths of it. Shift 2's output was not "
            "recorded.\n\nAnswer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="How many units did Shift 1 produce?",
                value=shift1,
                difficulty="easy",
                target_seconds=45,
                solution=f"$1200 \\times 0.35 = {fmt(shift1)}$ units.",
            ),
            QSpec(
                stem="How many units did Shift 2 produce?",
                value=shift2,
                difficulty="medium",
                target_seconds=70,
                solution=(
                    "Shift 3 made $1200 \\times \\dfrac{2}{5} = 480$ units. The three shifts must "
                    "account for the whole day:\n\n"
                    "$1200 - 420 - 480 = 300$\n\n"
                    f"**{fmt(shift2)} units**."
                ),
            ),
            QSpec(
                stem="Shift 2's output was what percentage of the day's total?",
                value=shift2_share,
                tolerance=0.05,
                difficulty="medium",
                target_seconds=60,
                solution=(
                    "$\\dfrac{300}{1200} \\times 100 = 25\\%$.\n\n"
                    "Faster: the other two shifts hold $35\\% + 40\\% = 75\\%$, so Shift 2 holds the "
                    "remaining **25%** — no need to find 300 first."
                ),
            ),
            QSpec(
                stem=(
                    "Defect rates were 2% for Shift 1, 5% for Shift 2 and 3% for Shift 3. How many "
                    "defective units were produced during the day?"
                ),
                value=37.8,
                tolerance=0.05,
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Each rate applies to its own shift's output:\n\n"
                    "- Shift 1: $420 \\times 0.02 = 8.4$\n"
                    "- Shift 2: $300 \\times 0.05 = 15$\n"
                    "- Shift 3: $480 \\times 0.03 = 14.4$\n\n"
                    "$8.4 + 15 + 14.4 = 37.8$\n\n"
                    "**37.8 units**. Averaging the three rates to $\\dfrac{2 + 5 + 3}{3} = 3.33\\%$ and "
                    "applying it to 1,200 gives 40, which is wrong — the shifts are different sizes, so "
                    "the rates must be weighted by output."
                ),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Data sufficiency
# ---------------------------------------------------------------------------


def ds_numbers() -> SetPlan:
    return SetPlan(
        micro_topic="dilr.di.data-sufficiency",
        slug="numbers",
        body=(
            "Each question below is followed by two statements, I and II. Decide whether the "
            "statements are sufficient to answer the question, and choose the matching option.\n\n"
            "A statement is sufficient if it pins the answer down to exactly one value — or, for a "
            "yes/no question, settles it as a definite yes or a definite no. You never need to "
            "actually compute the answer, only to establish that it is determined."
        ),
        questions=[
            ds_question(
                "What is the value of $x$?",
                "$x^2 = 49$",
                "$x > 0$",
                DS_BOTH,
                (
                    "**I alone:** $x = 7$ or $x = -7$. Two values, so not sufficient — forgetting the "
                    "negative root is the single most common error in this question type.\n\n"
                    "**II alone:** $x$ could be any positive number. Not sufficient.\n\n"
                    "**Together:** the two candidates from I, filtered by II, leave $x = 7$. Sufficient.\n\n"
                    "So **both statements together are sufficient, but neither alone is**."
                ),
                "medium",
                80,
            ),
            ds_question(
                "Is the integer $x$ even?",
                "$x$ is a multiple of 3.",
                "$x$ is a multiple of 4.",
                DS_II_ONLY,
                (
                    "**I alone:** multiples of 3 include 6 (even) and 9 (odd). Not sufficient.\n\n"
                    "**II alone:** every multiple of 4 is $4k = 2(2k)$, which is even. That is a definite "
                    "**yes**, and a definite yes is sufficient.\n\n"
                    "So **statement II alone is sufficient, but statement I alone is not**. Note you "
                    "answer the question asked without ever knowing what $x$ is."
                ),
                "medium",
                80,
            ),
            ds_question(
                "What is the average of five numbers?",
                "Their sum is 200.",
                "The largest of them is 60.",
                DS_I_ONLY,
                (
                    "**I alone:** an average is the sum divided by the count, and both are known: "
                    "$\\dfrac{200}{5} = 40$. Sufficient.\n\n"
                    "**II alone:** knowing the largest value says nothing about the other four. Not "
                    "sufficient.\n\n"
                    "So **statement I alone is sufficient, but statement II alone is not**. You do not "
                    "need the individual numbers — averages depend only on the total."
                ),
                "easy",
                70,
            ),
            ds_question(
                "What is the value of the integer $p$?",
                "$p$ is a prime number between 10 and 20.",
                "$p$ is odd.",
                DS_NEITHER,
                (
                    "**I alone:** $p \\in \\{11, 13, 17, 19\\}$. Four candidates, not sufficient.\n\n"
                    "**II alone:** any odd integer. Not sufficient.\n\n"
                    "**Together:** every prime between 10 and 20 is already odd, so II removes nothing "
                    "and all four candidates survive. Still not sufficient.\n\n"
                    "So **statements I and II together are not sufficient**. This is the shape to watch "
                    "for: a second statement that sounds like a constraint but is implied by the first, "
                    "and therefore adds no information at all."
                ),
                "hard",
                100,
            ),
        ],
    )


def ds_geometry() -> SetPlan:
    return SetPlan(
        micro_topic="dilr.di.data-sufficiency",
        slug="geometry-algebra",
        body=(
            "Each question below is followed by two statements, I and II. Decide whether the "
            "statements are sufficient to answer the question, and choose the matching option.\n\n"
            "Judge each statement on its own first, and only then together — deciding they are "
            "needed jointly before testing them separately is what turns an \"each alone\" question "
            "into a wrong answer."
        ),
        questions=[
            ds_question(
                "What is the area of a square?",
                "Its perimeter is 40 cm.",
                "Its diagonal is $10\\sqrt{2}$ cm.",
                DS_EITHER,
                (
                    "**I alone:** side $= \\dfrac{40}{4} = 10$, so area $= 100$ sq cm. Sufficient.\n\n"
                    "**II alone:** a square's diagonal is side $\\times \\sqrt{2}$, so the side is 10 and "
                    "the area is 100 sq cm. Sufficient.\n\n"
                    "So **each statement alone is sufficient**. A square has one degree of freedom — fix "
                    "any one length and everything else follows."
                ),
                "medium",
                80,
            ),
            ds_question(
                "What is the value of $x + y$?",
                "$2x + 2y = 18$",
                "$x - y = 3$",
                DS_I_ONLY,
                (
                    "**I alone:** divide by 2 to get $x + y = 9$. Sufficient — the question asks for the "
                    "**sum**, not for $x$ and $y$ separately.\n\n"
                    "**II alone:** the difference fixes nothing about the sum: $(5, 2)$ gives 7 and "
                    "$(10, 7)$ gives 17. Not sufficient.\n\n"
                    "So **statement I alone is sufficient, but statement II alone is not**. Answer the "
                    "question actually asked: two equations feel necessary only if you insist on solving "
                    "for both variables."
                ),
                "medium",
                80,
            ),
            ds_question(
                "What is the perimeter of a rectangle?",
                "Its length is twice its breadth.",
                "Its area is 72 sq cm.",
                DS_BOTH,
                (
                    "**I alone:** a shape ratio with no size. Not sufficient.\n\n"
                    "**II alone:** area 72 fits $8 \\times 9$ (perimeter 34) and $6 \\times 12$ "
                    "(perimeter 36). Not sufficient.\n\n"
                    "**Together:** $l = 2b$ and $lb = 72$ give $2b^2 = 72$, so $b = 6$, $l = 12$, and the "
                    "perimeter is $2(6 + 12) = 36$ cm. Sufficient.\n\n"
                    "So **both statements together are sufficient, but neither alone is**."
                ),
                "medium",
                90,
            ),
            ds_question(
                "What is the value of the integer $n$?",
                "$n^2 < 20$",
                "$n > 1$",
                DS_NEITHER,
                (
                    "**I alone:** $n \\in \\{-4, -3, -2, -1, 0, 1, 2, 3, 4\\}$, since $4^2 = 16 < 20$ but "
                    "$5^2 = 25 > 20$. Not sufficient.\n\n"
                    "**II alone:** unbounded above. Not sufficient.\n\n"
                    "**Together:** $n \\in \\{2, 3, 4\\}$. Three candidates survive, so still not "
                    "sufficient.\n\n"
                    "So **statements I and II together are not sufficient**. Narrowing a set is not the "
                    "same as determining a value — the test is whether exactly one candidate is left."
                ),
                "hard",
                100,
            ),
        ],
    )


def ds_word_problems() -> SetPlan:
    return SetPlan(
        micro_topic="dilr.di.data-sufficiency",
        slug="word-problems",
        body=(
            "Each question below is followed by two statements, I and II. Decide whether the "
            "statements are sufficient to answer the question, and choose the matching option.\n\n"
            "Watch for statements that restate the question in other words, and for statements that "
            "look like background detail but silently fix a quantity."
        ),
        questions=[
            ds_question(
                "What is the average speed of a train?",
                "It covers 300 km in 4 hours.",
                "It travels faster than a bus on the same route.",
                DS_I_ONLY,
                (
                    "**I alone:** average speed is distance over time, "
                    "$\\dfrac{300}{4} = 75$ km/h. Sufficient.\n\n"
                    "**II alone:** a comparison with an unknown bus speed. Not sufficient.\n\n"
                    "So **statement I alone is sufficient, but statement II alone is not**."
                ),
                "easy",
                60,
            ),
            ds_question(
                "How many students in a class passed an exam?",
                "60% of the class are girls.",
                "40 of the 50 students in the class passed.",
                DS_II_ONLY,
                (
                    "**I alone:** the gender split says nothing about passing. Not sufficient.\n\n"
                    "**II alone:** it states the answer outright — 40. Sufficient.\n\n"
                    "So **statement II alone is sufficient, but statement I alone is not**. Statement I "
                    "is there to invite arithmetic that the question never asked for; note that it also "
                    "quietly implies a class size, which is genuinely irrelevant here."
                ),
                "easy",
                70,
            ),
            ds_question(
                "What is the cost price of an article?",
                "It is sold for Rs 240.",
                "The profit made on it is 20%.",
                DS_BOTH,
                (
                    "**I alone:** selling price without any margin information. Not sufficient.\n\n"
                    "**II alone:** a rate with nothing to apply it to. Not sufficient.\n\n"
                    "**Together:** $240 = 1.2 \\times \\text{CP}$, so CP $= 200$. Sufficient.\n\n"
                    "So **both statements together are sufficient, but neither alone is**. Profit "
                    "percentage is always on cost price unless stated otherwise, which is what makes the "
                    "pair work."
                ),
                "medium",
                90,
            ),
            ds_question(
                "A shopkeeper sells an article at a profit of 25%. What is the selling price?",
                "The cost price is Rs 400.",
                "The profit is Rs 100.",
                DS_EITHER,
                (
                    "**I alone:** $400 \\times 1.25 = 500$. Sufficient.\n\n"
                    "**II alone:** the profit of Rs 100 is the 25% named in the question stem, so cost "
                    "price $= \\dfrac{100}{0.25} = 400$ and the selling price is 500. Sufficient.\n\n"
                    "So **each statement alone is sufficient**. The information in the stem counts as "
                    "given for both statements — a statement that looks thin on its own is often "
                    "sufficient once the stem is used properly."
                ),
                "hard",
                100,
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Caselets
# ---------------------------------------------------------------------------


def caselet_trip() -> SetPlan:
    spends = {"Pranav": 4200, "Quasar": 3600, "Ritu": 2100}
    total = sum(spends.values())
    assert total == 9900
    equal_share = total / 3
    assert equal_share == 3300
    ritu_owes = equal_share - spends["Ritu"]
    assert ritu_owes == 1200
    weights = {"Pranav": 5, "Quasar": 4, "Ritu": 3}
    unit = total / sum(weights.values())
    assert unit == 825
    ritu_weighted_share = unit * weights["Ritu"]
    assert ritu_weighted_share == 2475
    ritu_weighted_owes = ritu_weighted_share - spends["Ritu"]
    assert ritu_weighted_owes == 375

    return SetPlan(
        micro_topic="dilr.di.caselets",
        slug="trip-expenses",
        body=(
            "Pranav, Quasar and Ritu went on a trip together and paid for shared costs out of "
            "pocket as they went. Pranav paid Rs 4,200, Quasar paid Rs 3,600 and Ritu paid "
            "Rs 2,100. They agreed beforehand to divide the total cost equally between the three "
            "of them and settle up at the end.\n\nAnswer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="What was the total shared cost of the trip, in rupees?",
                value=total,
                difficulty="easy",
                target_seconds=40,
                solution=f"$4200 + 3600 + 2100 = {fmt(total)}$, so **Rs {fmt(total)}**.",
            ),
            QSpec(
                stem="What is each person's equal share of the total cost, in rupees?",
                value=equal_share,
                difficulty="easy",
                target_seconds=40,
                solution=f"$\\dfrac{{9900}}{{3}} = {fmt(equal_share)}$, so **Rs {fmt(equal_share)}** each.",
            ),
            QSpec(
                stem="How much must Ritu pay the others when they settle up, in rupees?",
                value=ritu_owes,
                difficulty="medium",
                target_seconds=70,
                solution=(
                    "Ritu owes the gap between her share and what she actually paid:\n\n"
                    "$3300 - 2100 = 1200$\n\n"
                    f"**Rs {fmt(ritu_owes)}**. Check the settlement balances: Pranav is owed "
                    "$4200 - 3300 = 900$ and Quasar is owed $3600 - 3300 = 300$, and "
                    "$900 + 300 = 1200$."
                ),
            ),
            QSpec(
                stem=(
                    "Suppose instead they had agreed to split the total in the ratio of nights stayed — "
                    "Pranav 5, Quasar 4 and Ritu 3. How much would Ritu then have had to pay the others, "
                    "in rupees?"
                ),
                value=ritu_weighted_owes,
                difficulty="hard",
                target_seconds=120,
                solution=(
                    "The ratio has $5 + 4 + 3 = 12$ parts, so one part is "
                    "$\\dfrac{9900}{12} = 825$.\n\n"
                    "Ritu's share is $3 \\times 825 = 2475$, and she already paid 2,100:\n\n"
                    "$2475 - 2100 = 375$\n\n"
                    f"**Rs {fmt(ritu_weighted_owes)}**. Her bill drops from 1,200 to 375 without anyone "
                    "spending a rupee differently — all that changed is the rule for dividing the same "
                    "total."
                ),
            ),
        ],
    )


def caselet_bakery() -> SetPlan:
    items = {
        "Loaves": {"qty": 120, "price": 45, "cost_rate": 0.60},
        "Cakes": {"qty": 80, "price": 250, "cost_rate": 0.55},
        "Pastries": {"qty": 200, "price": 30, "cost_rate": 0.40},
    }
    revenue = {k: v["qty"] * v["price"] for k, v in items.items()}
    assert revenue == {"Loaves": 5400, "Cakes": 20000, "Pastries": 6000}
    total_revenue = sum(revenue.values())
    assert total_revenue == 31400
    profit = {k: revenue[k] * (1 - v["cost_rate"]) for k, v in items.items()}
    assert [round(profit[k], 4) for k in items] == [2160, 9000, 3600]
    total_profit = sum(profit.values())
    assert round(total_profit, 4) == 14760
    margin = total_profit / total_revenue * 100
    assert round(margin, 2) == 47.01

    return SetPlan(
        micro_topic="dilr.di.caselets",
        slug="bakery",
        body=(
            "In one day a bakery sold 120 loaves at Rs 45 each, 80 cakes at Rs 250 each and 200 "
            "pastries at Rs 30 each. Ingredient cost came to 60% of revenue on loaves, 55% on "
            "cakes and 40% on pastries.\n\nAnswer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="What was the day's revenue from cakes, in rupees?",
                value=revenue["Cakes"],
                difficulty="easy",
                target_seconds=40,
                solution=f"$80 \\times 250 = {fmt(revenue['Cakes'])}$, so **Rs {fmt(revenue['Cakes'])}**.",
            ),
            QSpec(
                stem="What was the bakery's total revenue for the day, in rupees?",
                value=total_revenue,
                difficulty="medium",
                target_seconds=70,
                solution=(
                    "- Loaves: $120 \\times 45 = 5400$\n"
                    "- Cakes: $80 \\times 250 = 20000$\n"
                    "- Pastries: $200 \\times 30 = 6000$\n\n"
                    f"$5400 + 20000 + 6000 = {fmt(total_revenue)}$, so **Rs {fmt(total_revenue)}**. "
                    "Pastries are the biggest seller by count and the smallest by revenue."
                ),
            ),
            QSpec(
                stem="What was the day's profit on pastries, in rupees?",
                value=profit["Pastries"],
                difficulty="medium",
                target_seconds=70,
                solution=(
                    "Ingredients take 40% of pastry revenue, leaving 60%:\n\n"
                    "$6000 \\times 0.60 = 3600$\n\n"
                    f"**Rs {fmt(profit['Pastries'])}**."
                ),
            ),
            QSpec(
                stem=(
                    "Taking the day as a whole, profit was what percentage of revenue? Give the answer "
                    "to two decimal places."
                ),
                value=47.01,
                tolerance=0.05,
                difficulty="hard",
                target_seconds=130,
                solution=(
                    "Profit line by line:\n\n"
                    "- Loaves: $5400 \\times 0.40 = 2160$\n"
                    "- Cakes: $20000 \\times 0.45 = 9000$\n"
                    "- Pastries: $6000 \\times 0.60 = 3600$\n\n"
                    "$2160 + 9000 + 3600 = 14760$ on revenue of 31,400:\n\n"
                    f"$\\dfrac{{14760}}{{31400}} \\times 100 = {fmt(round(margin, 2))}\\%$\n\n"
                    "**47.01%**. Averaging the three margins (40%, 45%, 60%) gives 48.33% and is wrong: "
                    "cakes carry nearly two-thirds of the revenue, so the overall margin sits close to "
                    "the cake margin, not to the middle of the three."
                ),
            ),
        ],
    )


PLANS = [
    growth_revenue(),
    growth_population(),
    growth_investments(),
    missing_sales(),
    missing_marks(),
    missing_shifts(),
    ds_numbers(),
    ds_geometry(),
    ds_word_problems(),
    caselet_trip(),
    caselet_bakery(),
]


if __name__ == "__main__":
    emit_all(PLANS)
