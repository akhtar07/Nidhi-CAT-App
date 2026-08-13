"""DILR lessons. These teach a reading and reasoning routine rather than formulas."""

from __future__ import annotations

from . import EX, FC, LessonSpec

_SET_SELECTION = (
    "Before solving anything, spend 30 seconds deciding whether to attempt the set at all. "
    "Count how many questions it carries, look at whether the data is fully given or has to be "
    "deduced, and check whether the first question is answerable from a single row or needs the "
    "whole grid solved. A set that takes 12 minutes for 4 marks is worse than two sets that take "
    "5 minutes each. Walking away from a bad set is a skill, not a failure."
)

SPECS = [
    LessonSpec(
        mt="dilr.di.bar-column",
        intuition=(
            "A bar chart is a set of numbers wearing a costume. Each bar's height is just a value, drawn so "
            "your eye can compare quickly.\n\n"
            "So the first thing to do is undress it: read the axis, note the units, and treat the picture as "
            "a small table of numbers. Once it is numbers, it is ordinary arithmetic."
        ),
        core=(
            "Read three things before any question: what the axis units are (thousands? crores?), what each "
            "bar represents, and what the legend says if there are grouped bars.\n\n"
            "Most bar-chart questions are one of four kinds: read a value, compare two values, compute a "
            "total or average across bars, or find a percentage change between two bars. None are hard "
            "individually; errors come from misreading the scale or the legend."
        ),
        examples=[
            EX(
                stem="A chart shows sales of 45, 52, 48 and 60 units across Q1 to Q4. By what percent did sales grow from Q1 to Q4?",
                solution=(
                    "Growth $= \\dfrac{60 - 45}{45} \\times 100 = \\dfrac{15}{45} \\times 100 = 33.33$ percent.\n\n"
                    "Always divide by the **starting** value, not the ending one."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Percentage change",
                body="$\\dfrac{\\text{new} - \\text{old}}{\\text{old}} \\times 100$. The denominator is always the earlier value.",
                example="From 80 to 100 is a 25 percent rise; from 100 to 80 is a 20 percent fall.",
            ),
        ],
        traps=[
            "Misreading the axis scale, especially when it starts somewhere other than zero.",
            "Ignoring the legend on grouped bars and reading the wrong series.",
            "Dividing by the new value when computing percentage change.",
        ],
        minutes=5,
    ),
    LessonSpec(
        mt="dilr.di.line-charts",
        intuition=(
            "A line chart is a bar chart that has been joined up, and that changes what your eye notices. "
            "Bars invite you to compare heights; lines invite you to notice **direction** — rising, falling, "
            "flattening, crossing.\n\n"
            "So line-chart questions lean towards trends and turning points rather than single readings."
        ),
        core=(
            "The steepness of a segment is the rate of change, not the value. A line can be high but falling, "
            "or low but climbing fast — and questions deliberately exploit that difference.\n\n"
            "When two lines cross, the quantities are equal at that moment; before and after, one leads. "
            "Questions about 'in how many years did A exceed B' are answered by reading which line sits on "
            "top, interval by interval."
        ),
        examples=[
            EX(
                stem="Two colleges' enrolments over 2019-2023 are 820, 865, 790, 910, 960 and 700, 745, 810, 845, 880. In how many years did the second exceed the first?",
                solution=(
                    "Compare year by year:\n\n"
                    "2019: 700 against 820, no. 2020: 745 against 865, no. 2021: 810 against 790, **yes**. "
                    "2022: 845 against 910, no. 2023: 880 against 960, no.\n\n"
                    "So in exactly 1 year."
                ),
                alt="On the chart this is simply the interval where the second line pokes above the first.",
            ),
        ],
        formulas=[
            FC(
                title="Reading a line chart",
                body="Height is the value; steepness is the rate of change; a crossing point means the two values are equal.",
                example="A steeply falling line from 900 to 700 still sits above a flat line at 400.",
            ),
        ],
        traps=[
            "Confusing the steepest rise with the highest value.",
            "Assuming values between marked points are meaningful. Only the plotted points are data.",
            "Missing a crossing that happens between two labelled years.",
        ],
        minutes=5,
    ),
    LessonSpec(
        mt="dilr.di.pie-charts",
        intuition=(
            "A pie chart shows how one whole thing is sliced up. Every slice is a **share**, not an amount — "
            "which is why two pie charts can look identical while describing totally different totals.\n\n"
            "A 40 percent slice of a small pie can be less food than a 20 percent slice of a huge one."
        ),
        core=(
            "All slices sum to 100 percent, or equivalently 360 degrees. So one degree is $\\frac{1}{3.6}$ of "
            "a percent, and a slice's angle converts straight to its share.\n\n"
            "To turn a share into an actual quantity you need the total, and the question must give it. If two "
            "pie charts are shown with different totals, you can only compare absolute amounts after "
            "multiplying each share by its own total — comparing percentages directly is meaningless."
        ),
        examples=[
            EX(
                stem="A company's Rs. 60 lakh budget is split: Salaries 40 percent, Marketing 20, Rent 15, R&D 15, Utilities 10. How much goes to Marketing and Utilities together?",
                solution=(
                    "Combined share $= 20 + 10 = 30$ percent.\n\n"
                    "Amount $= \\dfrac{30}{100} \\times 60 = 18$ lakh."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Share to angle and back",
                body="Percentage $= \\dfrac{\\text{angle}}{360} \\times 100$, and angle $= \\dfrac{\\text{percentage}}{100} \\times 360$.",
                example="A 90-degree slice is 25 percent; a 20 percent slice is 72 degrees.",
            ),
            FC(
                title="Share to amount",
                body="Amount $=$ share $\\times$ total. Without the total, a pie chart gives you no absolute values at all.",
                example="15 percent of Rs. 80 lakh is Rs. 12 lakh.",
            ),
        ],
        traps=[
            "Comparing percentages across two pie charts with different totals as though they were amounts.",
            "Forgetting that the slices must sum to exactly 100 percent — useful for finding a missing slice.",
            "Treating a bigger angle as a bigger quantity when the two pies have different totals.",
        ],
        minutes=5,
    ),
    LessonSpec(
        mt="dilr.di.stacked-charts",
        intuition=(
            "A stacked bar is several bar charts balanced on top of each other. The whole column tells you the "
            "total; each coloured band tells you one component's contribution.\n\n"
            "The catch is that only the bottom band starts at zero. Every band above it has to be read as a "
            "**difference** between two boundary lines, which is where careless reading costs marks."
        ),
        core=(
            "Two questions get asked. Absolute questions ask for one band's size — read the gap between its "
            "top and bottom edges. Proportional questions ask for a component's share of its column — divide "
            "the band by the column total.\n\n"
            "Watch for the difference between a component **growing** and its **share** growing. A component "
            "can increase in absolute terms while its share falls, if the total grew faster."
        ),
        examples=[
            EX(
                stem="Quarterly sales stack as Electronics 45, Apparel 30, Groceries 25 in Q1. What share of Q1 came from Electronics?",
                solution=(
                    "Q1 total $= 45 + 30 + 25 = 100$.\n\n"
                    "Electronics share $= \\dfrac{45}{100} \\times 100 = 45$ percent."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Reading a band",
                body="A band's value is (its top edge) minus (its bottom edge), not its top edge alone.",
                example="A band running from 45 to 75 on the axis represents 30, not 75.",
            ),
            FC(
                title="Share within a column",
                body="Component share $= \\dfrac{\\text{band}}{\\text{column total}} \\times 100$.",
                example="A band of 30 in a column totalling 120 is a 25 percent share.",
            ),
        ],
        traps=[
            "Reading a band's top edge as its value instead of subtracting the bottom edge.",
            "Confusing growth in absolute size with growth in share.",
            "Comparing bands across columns of different heights without converting to shares.",
        ],
        minutes=5,
    ),
    LessonSpec(
        mt="dilr.di.radar-spider",
        intuition=(
            "A radar chart is a set of measuring sticks fanning out from a centre, one per category, with the "
            "values joined into a web. The further from the centre a point sits, the bigger the value.\n\n"
            "It is designed for comparing **profiles** — is this student strong across the board, or spiky?"
        ),
        core=(
            "Each spoke is its own axis, and every spoke usually shares the same scale. Read a value by seeing "
            "how far along its spoke the point lies.\n\n"
            "The enclosed area is visually striking but rarely the answer to anything — it depends on the "
            "arbitrary order of the spokes. Trust the individual readings, not the shape.\n\n"
            "Typical questions: which category scores highest, which entity is most balanced, or on how many "
            "categories does one entity beat another."
        ),
        examples=[
            EX(
                stem="Two products are rated out of 10 on five features. A scores 8, 6, 9, 5, 7 and B scores 7, 8, 6, 9, 5. On how many features does A beat B?",
                solution=(
                    "Compare feature by feature:\n\n"
                    "8 vs 7: A. 6 vs 8: B. 9 vs 6: A. 5 vs 9: B. 7 vs 5: A.\n\n"
                    "A wins on 3 of the 5 features."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Reading a radar chart",
                body="Distance from centre along a spoke is the value on that category. Compare spoke by spoke, never by overall shape.",
                example="A point halfway along a spoke scaled 0-10 represents about 5.",
            ),
        ],
        traps=[
            "Judging 'bigger overall' from the enclosed area, which changes if the spokes are reordered.",
            "Assuming all spokes share a scale when the chart labels them differently.",
            "Reading towards the centre as larger. The centre is the minimum.",
        ],
        minutes=5,
    ),
    LessonSpec(
        mt="dilr.di.bubble-charts",
        intuition=(
            "A bubble chart squeezes three numbers into one picture. Left-to-right is one variable, up-and-down "
            "is a second, and the **size** of the bubble is a third.\n\n"
            "So a bubble far right, high up and large is scoring well on all three — and a question asking "
            "'which is best' usually needs you to say which of the three you are judging on."
        ),
        core=(
            "Read the two axes first, then check what the legend says bubble size encodes. Size is the "
            "dimension people forget.\n\n"
            "Be careful comparing bubble sizes by eye: a bubble that looks twice as wide has four times the "
            "area, so visual comparison badly exaggerates differences. Where exact values matter, the question "
            "will normally give them in a table alongside."
        ),
        examples=[
            EX(
                stem="Bubbles plot revenue on the x-axis, profit margin on the y-axis, and headcount as size. A firm is far right but low down with a small bubble. Describe it.",
                solution=(
                    "Far right means high revenue.\n\n"
                    "Low down means a low profit margin.\n\n"
                    "A small bubble means few employees.\n\n"
                    "So it is a high-revenue, low-margin business run by a small team."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Three variables at once",
                body="x-position, y-position, and bubble size are three separate readings. Always check the legend for what size means.",
                example="Two bubbles at the same height differ only in the x-variable and in size.",
            ),
        ],
        traps=[
            "Comparing bubble sizes by width when area is what encodes the value.",
            "Ignoring the size dimension entirely and treating the chart as a scatter plot.",
            "Assuming position implies causation between the two axis variables.",
        ],
        minutes=5,
    ),
    LessonSpec(
        mt="dilr.di.combination-charts",
        intuition=(
            "Sometimes one picture carries two different kinds of number — say, bars for total sales in crores "
            "and a line for profit margin in percent. They cannot share one axis, so the chart grows a second "
            "one on the right.\n\n"
            "The single most important habit here: check which axis each series belongs to before reading any "
            "value."
        ),
        core=(
            "A combination chart mixes chart types precisely because the quantities are of different kinds — "
            "usually an absolute amount and a rate or percentage.\n\n"
            "The left axis serves one series, the right axis the other. Reading a line against the bar axis "
            "produces confidently wrong answers, and the chart is often designed so that mistake yields one "
            "of the offered options.\n\n"
            "The interesting questions ask you to combine the two: revenue from the bars times margin from "
            "the line gives profit, which appears nowhere on the chart directly."
        ),
        examples=[
            EX(
                stem="Bars show revenue of Rs. 200 crore and a line shows a profit margin of 15 percent for the same year. Find the profit.",
                solution=(
                    "Profit $=$ revenue $\\times$ margin $= 200 \\times \\dfrac{15}{100} = 30$ crore.\n\n"
                    "Neither axis showed profit directly — it had to be built from both series."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Two axes, two scales",
                body="Identify which axis each series uses before reading anything. Bars and lines normally use opposite axes.",
                example="A line at '15' may mean 15 percent on the right axis, not 15 crore on the left.",
            ),
            FC(
                title="Combining the series",
                body="Absolute $\\times$ rate gives a new absolute. This is usually what the hard question wants.",
                example="Revenue 400 with margin 12 percent gives profit 48.",
            ),
        ],
        traps=[
            "Reading a percentage line against the absolute axis.",
            "Assuming both axes start at zero or share a scale.",
            "Adding a percentage to an absolute value. They are different kinds of quantity.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="dilr.di.caselets",
        intuition=(
            "A caselet hides the data inside a paragraph of prose instead of a neat table. Nothing about the "
            "arithmetic is harder — the difficulty is purely in **extraction**.\n\n"
            "So the first move is always the same: stop reading for meaning and start reading for numbers. "
            "Build the table the examiner declined to give you."
        ),
        core=(
            "Read once with a pen. Every time a number appears, write it down with its label. Every time a "
            "relationship appears ('twice as many', 'Rs. 200 more than'), write that as a small equation.\n\n"
            "You will usually find you have enough to fill a table completely, or enough equations to solve "
            "for the unknowns. Only then look at the questions.\n\n"
            "Resist the urge to start answering during the first read. Half-extracted data leads to rework."
        ),
        examples=[
            EX(
                stem="A firm has 3 departments. Sales has 40 staff, Engineering has twice as many as Sales, and Support has 10 fewer than Engineering. Find the total headcount.",
                solution=(
                    "Extract in order:\n\n"
                    "Sales $= 40$.\n"
                    "Engineering $= 2 \\times 40 = 80$.\n"
                    "Support $= 80 - 10 = 70$.\n\n"
                    "Total $= 40 + 80 + 70 = 190$."
                ),
                alt="Written as a three-row table this takes seconds; read as prose it invites arithmetic slips.",
            ),
        ],
        formulas=[
            FC(
                title="Extraction routine",
                body="Read once, tabulating every number with its label and every relationship as an equation. Only then read the questions.",
                example="'Twice as many as Sales' becomes $E = 2S$, written down immediately.",
            ),
        ],
        traps=[
            "Answering while still reading, then discovering a later sentence changes an earlier value.",
            "Missing a relationship buried mid-sentence, especially comparatives like 'fewer than' or 'more than'.",
            "Assuming the paragraph gives values in the order the questions need them.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="dilr.di.missing-data",
        intuition=(
            "Some tables arrive with holes in them. This looks unfair until you notice the totals: if a row "
            "must add to 100 and three of its four entries are given, the fourth is forced.\n\n"
            "The blanks are not missing information. They are a puzzle whose answer is already determined by "
            "the constraints around them."
        ),
        core=(
            "Work the constraints, not the blanks. Row totals, column totals, grand totals and stated "
            "percentages each pin down values.\n\n"
            "Fill in whatever is immediately forced by a single constraint. That usually unlocks another cell, "
            "which unlocks another. Proceed until the table is complete or you have exhausted the constraints.\n\n"
            "If several blanks remain and no constraint forces them individually, check whether the question "
            "actually needs them — often it only asks about a total, which may already be determined."
        ),
        examples=[
            EX(
                stem="A row must total 200. Three of its four entries are 45, 60 and 30. Find the fourth.",
                solution=(
                    "Sum of the known entries $= 45 + 60 + 30 = 135$.\n\n"
                    "The missing entry $= 200 - 135 = 65$."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Filling by constraint",
                body="A blank is determined when its row total, column total, or a stated percentage leaves only one possible value.",
                example="A column summing to 500 with entries 120, 180 and one blank forces 200.",
            ),
            FC(
                title="Cascade",
                body="Fill every forced cell first; each one may force another. Repeat until nothing new is forced.",
                example="Completing a row often completes a column that crosses it.",
            ),
        ],
        traps=[
            "Guessing a blank rather than deriving it from a constraint.",
            "Missing the grand total, which often constrains the table when no single row or column does.",
            "Spending time filling cells the questions never reference.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="dilr.di.data-sufficiency",
        intuition=(
            "Data sufficiency does not ask you to solve anything. It asks: **do I have enough to solve it?**\n\n"
            "That is a genuinely different question, and the discipline is to stop as soon as you know the "
            "answer is determined, without actually computing it. Solving wastes time you do not have."
        ),
        core=(
            "The answer options are fixed:\n\n"
            "A: Statement I alone is enough, II alone is not.\n"
            "B: Statement II alone is enough, I alone is not.\n"
            "C: Both together are enough, neither alone is.\n"
            "D: Either alone is enough.\n"
            "E: Even together they are not enough.\n\n"
            "Test statement I **completely on its own**, forgetting II entirely. Then test II alone, forgetting "
            "I. Only if both fail individually do you combine them.\n\n"
            "'Sufficient' means it pins down exactly one answer. Two possible values is not sufficient, even if "
            "both look plausible."
        ),
        examples=[
            EX(
                stem="What is the value of x? Statement I: $x^2 = 16$. Statement II: $x > -10$.",
                solution=(
                    "Statement I alone gives $x = 4$ or $x = -4$ — two values, so not sufficient.\n\n"
                    "Statement II alone allows endless values, so not sufficient.\n\n"
                    "Together: both 4 and $-4$ satisfy $x > -10$, so the ambiguity survives.\n\n"
                    "The answer is **E** — not sufficient even together."
                ),
                alt="The trap is assuming a square root has one value. $x^2 = 16$ has two solutions.",
            ),
        ],
        formulas=[
            FC(
                title="The five options",
                body="A: I alone. B: II alone. C: both needed. D: either alone. E: insufficient even together.",
                example="If each statement independently pins the answer down, the answer is D, not C.",
            ),
            FC(
                title="What counts as sufficient",
                body="A statement is sufficient only if it leaves exactly one possible answer. Two candidates means insufficient.",
                example="'x is a positive even number less than 5' gives only 2 or 4 — still insufficient.",
            ),
        ],
        traps=[
            "Letting information from statement I leak into your evaluation of statement II.",
            "Actually computing the answer instead of just establishing that it is determined.",
            "Choosing C when each statement alone would have sufficed, which is D.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.di.growth-cagr",
        intuition=(
            "If a business grows from 100 to 200 over four years, it did not grow 25 percent a year. Growth "
            "compounds, so each year's rise builds on a bigger base.\n\n"
            "CAGR answers: what **steady** yearly rate would have produced this same journey? It is the "
            "smoothed-out rate, ignoring the bumps along the way."
        ),
        core=(
            "Year-on-year growth compares consecutive periods and always divides by the earlier value.\n\n"
            "CAGR looks only at the start and end, and asks what constant multiplier repeated over the period "
            "would connect them. Crucially, the exponent uses the number of **intervals**, not the number of "
            "data points: 2019 to 2023 is 4 years of growth, not 5.\n\n"
            "Market share is a share of a total, so a company's share can fall while its absolute sales rise, "
            "if the market grew faster. Questions exploit exactly that."
        ),
        examples=[
            EX(
                stem="Revenue rises from 120 to 210 between 2019 and 2023. Find the CAGR.",
                solution=(
                    "From 2019 to 2023 is 4 intervals, not 5.\n\n"
                    "$\\text{CAGR} = \\left(\\dfrac{210}{120}\\right)^{1/4} - 1$\n\n"
                    "$= (1.75)^{0.25} - 1 \\approx 0.1503$, so about 15.03 percent per year."
                ),
                alt="Sanity check: 15 percent compounded 4 times multiplies by roughly 1.75, matching 120 to 210.",
            ),
        ],
        formulas=[
            FC(
                title="Year-on-year growth",
                body="$\\dfrac{\\text{this year} - \\text{last year}}{\\text{last year}} \\times 100$",
                example="From 175 to 210 is a 20 percent rise.",
            ),
            FC(
                title="CAGR",
                body="$\\left(\\dfrac{\\text{End}}{\\text{Start}}\\right)^{1/n} - 1$, where $n$ is the number of intervals.",
                example="Doubling over 3 years gives $2^{1/3} - 1 \\approx 25.99$ percent.",
            ),
            FC(
                title="Market share",
                body="$\\dfrac{\\text{company sales}}{\\text{total market sales}} \\times 100$. Share can fall while sales rise.",
                example="Sales up from 50 to 60 while the market doubles from 200 to 500 means share fell from 25 to 12 percent.",
            ),
        ],
        traps=[
            "Counting years instead of intervals. 2019 to 2023 is 4, not 5.",
            "Averaging the yearly growth rates and calling it CAGR. Compounding is not additive.",
            "Reading a falling market share as falling sales.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.distribution-grouping",
        intuition=(
            "Four friends, four different pets, four different jobs, and a handful of clues. This is the "
            "logic puzzle you may have done in a puzzle book — and the method is exactly the same: draw a "
            "grid and start crossing things out.\n\n"
            "What you can rule **out** is as valuable as what you can confirm. A cell you have eliminated "
            "narrows every row and column it touches."
        ),
        core=(
            "Draw a grid with people down the side and each attribute across the top. Work through the clues "
            "in order, marking a tick for anything confirmed and a cross for anything ruled out.\n\n"
            "After each pass, look for **forced** cells: a row where only one option remains, or a column where "
            "only one person can take a value. These cascade — one confirmation usually creates another.\n\n"
            "Negative clues ('Ben does not own the cat') are often more useful than positive ones, because "
            "they eliminate across a whole row or column at once. Re-read clues after each pass; a clue that "
            "told you nothing early can become decisive later."
        ),
        examples=[
            EX(
                stem="Aria, Ben and Cora own a cat, dog and fish in some order. Aria does not own the fish. Ben owns the dog. Who owns the fish?",
                solution=(
                    "Ben owns the dog, so Ben is settled and neither Aria nor Cora owns it.\n\n"
                    "Aria does not own the fish, so Aria must own the cat.\n\n"
                    "That leaves the fish for Cora."
                ),
                alt="Notice the negative clue about Aria did the real work — it forced her onto the cat by elimination.",
            ),
        ],
        formulas=[
            FC(
                title="Grid method",
                body="One row per person, one column per attribute value. Tick confirmations, cross eliminations, and re-scan for forced cells after every clue.",
                example="If a row has crosses in all but one cell, that cell is confirmed.",
            ),
            FC(
                title="Uniqueness constraint",
                body="Each attribute value is used exactly once, so confirming a cell crosses out the rest of its row and its column.",
                example="Confirming Ben owns the dog rules out the dog for everyone else.",
            ),
        ],
        traps=[
            "Using a clue once and never revisiting it. Clues often become useful only after other deductions.",
            "Forgetting to propagate a confirmation across both the row and the column.",
            "Guessing a placement to 'see what happens' without tracking that it was an assumption.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.selection-conditionalities",
        intuition=(
            "You are picking a team, and there are rules: if Amit comes then Bina must come too; Chen and "
            "Deepa refuse to be in the same room. These are the constraints, and every valid team must "
            "satisfy all of them.\n\n"
            "The safest approach is often just to list every possible team and strike out the ones that break "
            "a rule. With small numbers that is faster than clever reasoning, and far less error-prone."
        ),
        core=(
            "Translate each rule into precise logic before doing anything else.\n\n"
            "'If A then B' means A cannot appear without B — but B **can** appear without A. That asymmetry is "
            "the single most misread rule type.\n\n"
            "'A and B cannot both be selected' allows either alone, or neither.\n\n"
            "'At least one of A or B' forbids only the case where both are absent.\n\n"
            "For counting questions, enumerate systematically. Choosing 3 from 6 is only 20 possibilities, "
            "and checking all 20 against three rules is quick and certain."
        ),
        examples=[
            EX(
                stem="Rule: if Amit is selected, Bina must be selected. Is a team of Bina and Chen, without Amit, valid?",
                solution=(
                    "The rule only restricts what happens **when Amit is in**. Amit is not selected here, so the "
                    "rule imposes nothing at all.\n\n"
                    "The team is valid. Bina may be selected with or without Amit."
                ),
                alt="The common error is reading 'if A then B' as 'A and B always travel together'. It is a one-way street.",
            ),
        ],
        formulas=[
            FC(
                title="Conditional",
                body="'If A then B' forbids exactly one case: A present and B absent. B alone is fine, and neither is fine.",
                example="With this rule, valid teams include {B}, {B, C} and {A, B} but never {A, C}.",
            ),
            FC(
                title="Mutual exclusion and at-least-one",
                body="'Not both A and B' forbids only {A, B} together. 'At least one of A or B' forbids only the case with neither.",
                example="Under both rules, a team must contain exactly one of A and B if only those two are involved.",
            ),
        ],
        traps=[
            "Reading a conditional as working in both directions.",
            "Treating 'at least one' as 'exactly one'. Both being present is usually allowed.",
            "Missing that 'neither' can be a valid option for an exclusion rule.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.ordering-ranking",
        intuition=(
            "Six students finished a test in some order and you are given hints: 'Priya scored better than "
            "Rohan', 'exactly one person came between Sara and Tarun'.\n\n"
            "Draw six blank slots on paper. Each clue either fixes someone, or fixes a **relationship** "
            "between two people that you can slide along the line until other clues lock it down."
        ),
        core=(
            "Separate the clues into two kinds. **Absolute** clues fix a position outright ('Uma was third'). "
            "**Relative** clues fix an order or a gap without saying where ('A is immediately above B').\n\n"
            "Start with the absolutes — they anchor the line. Then take the relative clues with the largest "
            "blocks, since a rigid pair or triple has few places it can fit.\n\n"
            "Be precise about language. 'Better than' allows any gap; 'immediately above' allows none. "
            "'Exactly one between' means a gap of two positions."
        ),
        examples=[
            EX(
                stem="Five runners finish a race. C is immediately ahead of D. A finished first. B finished last. Where can C and D be?",
                solution=(
                    "A is 1st and B is 5th, so positions 2, 3 and 4 remain for C, D and E.\n\n"
                    "C and D must be adjacent with C first, so the possible pairs are (2,3) or (3,4).\n\n"
                    "If C and D take 2 and 3, E is 4th. If they take 3 and 4, E is 2nd. Both remain possible "
                    "without a further clue."
                ),
                alt="Recognising that a question can still have two valid arrangements matters — do not force a unique answer that the clues do not support.",
            ),
        ],
        formulas=[
            FC(
                title="Anchor then slide",
                body="Place absolute clues first, then fit rigid relative blocks into the remaining gaps.",
                example="A fixed 1st place plus an adjacent pair leaves very few arrangements to test.",
            ),
            FC(
                title="Reading the gap language",
                body="'Immediately' means adjacent. 'Exactly one between' means two positions apart. 'Above' or 'before' alone means any gap.",
                example="'Exactly two between X and Y' means their positions differ by 3.",
            ),
        ],
        traps=[
            "Reading 'better than' as 'immediately better than'.",
            "Fixing a direction for a relative clue that does not state one, such as 'X and Y are two apart'.",
            "Assuming the answer must be unique when the clues genuinely allow several orders.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.games-tournaments",
        intuition=(
            "A league table is just bookkeeping. Every match hands out a fixed number of points, and the table "
            "is the running total.\n\n"
            "The useful consequence: the **total** points awarded across the whole tournament is fixed before "
            "a single game is played. That total is often the key that unlocks an incomplete table."
        ),
        core=(
            "First establish the format. In a round robin with $n$ teams, each pair meets once, giving "
            "$\\binom{n}{2}$ matches. If a win is 2 points and there are no draws, the total handed out is "
            "$2 \\times \\binom{n}{2}$.\n\n"
            "That total lets you find a missing team's points by subtraction, and caps how high any team can "
            "finish.\n\n"
            "For 'maximum possible' questions, imagine the most favourable remaining results for the team in "
            "question — but check the arrangement is actually consistent, since one team winning means another "
            "must lose."
        ),
        examples=[
            EX(
                stem="Four teams play a round robin, each pair once. How many matches are played?",
                solution=(
                    "Every pair of teams meets exactly once, so count the pairs:\n\n"
                    "$\\binom42 = \\dfrac{4 \\times 3}{2} = 6$ matches."
                ),
                alt="Listing them confirms it: AB, AC, AD, BC, BD, CD.",
            ),
        ],
        formulas=[
            FC(
                title="Round robin size",
                body="$n$ teams playing each other once gives $\\binom{n}{2} = \\dfrac{n(n-1)}{2}$ matches. Twice each doubles it.",
                example="6 teams play 15 matches in a single round robin.",
            ),
            FC(
                title="Total points",
                body="With a fixed award per match, total points $=$ matches $\\times$ points per match. Use it to find a missing entry.",
                example="6 matches at 2 points each distributes 12 points in total.",
            ),
        ],
        traps=[
            "Forgetting whether teams meet once or twice. It doubles everything.",
            "Ignoring draws when the format allows them, which changes the points-per-match total.",
            "Computing a 'maximum possible' score without checking the results are mutually consistent.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.scheduling",
        intuition=(
            "Scheduling puzzles are timetables with gaps. Five people, five days, some rules about who cannot "
            "go on which day.\n\n"
            "It is the same grid technique as any matching puzzle, with one extra feature: time has an order. "
            "'Before' and 'after' constrain things that 'different from' does not."
        ),
        core=(
            "Build a grid of slots against entities. Mark the impossible cells from the negative clues first — "
            "these are usually generous and cut the space down fast.\n\n"
            "Then apply the ordering clues. 'A is scheduled before B' means A cannot take the last slot and B "
            "cannot take the first, which is often an immediate elimination people miss.\n\n"
            "Watch for clues about gaps ('three days after') versus mere order ('some day after'). And check "
            "whether every slot must be filled, or whether some can be empty — that changes the counting."
        ),
        examples=[
            EX(
                stem="Four presentations run Monday to Thursday, one per day. P is before Q. R is on Wednesday. P is not on Monday. When is P?",
                solution=(
                    "R takes Wednesday, leaving Monday, Tuesday and Thursday for P, Q and S.\n\n"
                    "P is not on Monday, so P is Tuesday or Thursday.\n\n"
                    "P must be before Q, so P cannot be Thursday — nothing would be left after it.\n\n"
                    "So P is on Tuesday."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Ordering eliminations",
                body="'A before B' immediately rules A out of the last slot and B out of the first.",
                example="With four slots and A before B, A can only be in slots 1 to 3.",
            ),
            FC(
                title="Grid first, order second",
                body="Apply negative and fixed clues to the grid first, then layer the ordering constraints onto what remains.",
                example="Fixing one entity to Wednesday shrinks the problem before any ordering logic is needed.",
            ),
        ],
        traps=[
            "Missing the automatic first-and-last eliminations that any ordering clue produces.",
            "Reading 'after' as 'immediately after'.",
            "Assuming every slot is filled when the puzzle allows empty ones.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.venn-set",
        intuition=(
            "Draw overlapping circles for the groups. Every person in the survey lands in exactly one region "
            "of the picture — plays only cricket, plays cricket and football but not tennis, plays nothing at "
            "all, and so on.\n\n"
            "Once you see it that way, the entire problem is filling in each region's headcount without "
            "counting anyone twice."
        ),
        core=(
            "Always fill the diagram from the **middle outwards**. Start with the all-three overlap, then the "
            "pairwise regions (subtracting the middle from each), then the only-one regions.\n\n"
            "The reason is that a stated figure like 'cricket and football' almost always includes the people "
            "who also play tennis. Only by subtracting the centre do you get the genuinely-only-two region.\n\n"
            "Watch the wording closely: 'both A and B' usually means at least both, while 'only A and B' "
            "explicitly excludes the third."
        ),
        examples=[
            EX(
                stem="Of 100 people, 60 like tea, 50 like coffee, and 10 like neither. How many like both?",
                solution=(
                    "People liking at least one $= 100 - 10 = 90$.\n\n"
                    "$|T \\cup C| = |T| + |C| - |T \\cap C|$\n\n"
                    "$90 = 60 + 50 - |T \\cap C|$, so $|T \\cap C| = 20$."
                ),
                alt="Check the regions: only tea 40, only coffee 30, both 20, neither 10 — totalling 100.",
            ),
        ],
        formulas=[
            FC(
                title="Two-set inclusion-exclusion",
                body="$|A \\cup B| = |A| + |B| - |A \\cap B|$",
                example="Sets of 30 and 25 with a union of 45 must overlap in 10.",
            ),
            FC(
                title="Three-set inclusion-exclusion",
                body="$|A \\cup B \\cup C| = \\sum|A| - \\sum|A \\cap B| + |A \\cap B \\cap C|$",
                example="Singles 20 each, pairs 8 each, triple 3: union is $60 - 24 + 3 = 39$.",
            ),
            FC(
                title="Fill order",
                body="Centre first, then pairwise-only (pair minus centre), then only-one regions.",
                example="If 'A and B' is 12 and the centre is 5, then A-and-B-only is 7.",
            ),
        ],
        traps=[
            "Treating a stated pairwise figure as the only-two region without subtracting the centre.",
            "Forgetting the 'neither' group when the grand total is given.",
            "Filling the diagram outside-in, which double counts almost every time.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.network-routes",
        intuition=(
            "Picture a map of towns joined by roads, each road with a distance or a capacity. Questions ask "
            "for the shortest route, or how much traffic can flow from one end to the other.\n\n"
            "These look intimidating but reward patience: with a small network, listing the possible routes "
            "and totalling each is completely reliable."
        ),
        core=(
            "For **shortest path** in a small network, enumerate the distinct routes and add up each one. Do "
            "not try to eyeball it — the shortest-looking route on the diagram is often not the shortest by "
            "the numbers.\n\n"
            "For **maximum flow**, the total that can pass along a route is limited by its narrowest link, "
            "just as a chain is only as strong as its weakest link. Add up the capacities of independent "
            "routes, being careful not to reuse an edge's capacity twice.\n\n"
            "Redraw the network neatly before starting. Crossed lines cause more errors than the logic does."
        ),
        examples=[
            EX(
                stem="Routes from A to D: via B costs 4 + 5, via C costs 3 + 7, direct costs 11. Which is shortest?",
                solution=(
                    "Via B: $4 + 5 = 9$.\n"
                    "Via C: $3 + 7 = 10$.\n"
                    "Direct: $11$.\n\n"
                    "The shortest is via B, at 9."
                ),
                alt="Note the direct route is the longest here — a deliberate trap in many such questions.",
            ),
        ],
        formulas=[
            FC(
                title="Shortest path",
                body="Enumerate every distinct route and total its edge weights. Choose the smallest total.",
                example="Three routes costing 9, 10 and 11 give a shortest path of 9.",
            ),
            FC(
                title="Bottleneck capacity",
                body="A route's capacity is its smallest edge. Total flow adds independent routes without reusing edges.",
                example="A route with capacities 8, 5 and 6 carries only 5.",
            ),
        ],
        traps=[
            "Assuming the direct link is the shortest. It frequently is not.",
            "Counting an edge's capacity in two different routes.",
            "Missing a valid route because the diagram is drawn awkwardly. Redraw it.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.binary-logic",
        intuition=(
            "Some people in the puzzle always tell the truth, and others always lie. Someone says 'I am a "
            "liar' — which cannot be true, because a liar would not admit it, and a truth-teller would not "
            "say it.\n\n"
            "That contradiction is the engine of the whole topic. You assume something, follow it through, and "
            "see whether the world it creates makes sense."
        ),
        core=(
            "The reliable method is **assume and test**. Suppose person A is a truth-teller. Work out what "
            "every statement then implies. If you reach a contradiction, A must be a liar; if everything holds "
            "together, that scenario is possible.\n\n"
            "Do this systematically rather than jumping between assumptions. Two people gives four cases; "
            "three gives eight — still perfectly countable.\n\n"
            "Remember the asymmetry: a liar's statement is **false**, which tells you the opposite is true. A "
            "false statement is information, not an absence of it."
        ),
        examples=[
            EX(
                stem="A says 'B is a liar'. B says 'A and I are both truth-tellers'. Who is what?",
                solution=(
                    "Assume A tells the truth. Then B is a liar, so B's claim must be false. B claimed both are "
                    "truth-tellers — false, since B is a liar. Consistent so far, with no contradiction.\n\n"
                    "Now assume A lies. Then B is a truth-teller, so B's claim is true, meaning A is a "
                    "truth-teller too. That contradicts our assumption that A lies.\n\n"
                    "So A is a truth-teller and B is a liar."
                ),
                alt="Only one of the two assumptions survives — which is exactly how these puzzles are built.",
            ),
        ],
        formulas=[
            FC(
                title="Assume and test",
                body="Assume one person's type, follow every consequence, and reject the assumption if a contradiction appears.",
                example="If assuming A is truthful forces A to be lying, then A is a liar.",
            ),
            FC(
                title="A lie is information",
                body="If a liar says X, then X is false, so the negation of X is true.",
                example="A liar saying 'C is guilty' establishes that C is not guilty.",
            ),
        ],
        traps=[
            "Treating a liar's statement as merely unreliable. It is reliably false.",
            "Stopping at the first consistent scenario without checking whether others also work.",
            "Forgetting that 'not a truth-teller' means liar only when the puzzle offers exactly two types.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.cubes-dice",
        intuition=(
            "Take a wooden cube, paint it all over, and saw it into 27 small cubes. The 8 corner pieces have "
            "paint on 3 faces. The middle-of-an-edge pieces have 2. The face-centre pieces have 1. And the "
            "single cube buried in the middle has none at all.\n\n"
            "Every painted-cube question is that picture, with a different number of cuts."
        ),
        core=(
            "Cut a cube into $n \\times n \\times n$ smaller cubes and the counts follow fixed patterns:\n\n"
            "3 painted faces: always 8, the corners.\n"
            "2 painted faces: $12(n-2)$, along the twelve edges.\n"
            "1 painted face: $6(n-2)^2$, on the six faces.\n"
            "0 painted faces: $(n-2)^3$, the hidden core.\n\n"
            "For **dice**, the key fact is that opposite faces sum to 7 in a standard die. Two faces that "
            "appear adjacent in any view cannot be opposite each other — that one observation resolves most "
            "dice questions."
        ),
        examples=[
            EX(
                stem="A painted cube is cut into 64 smaller cubes. How many have exactly two painted faces?",
                solution=(
                    "$64 = 4^3$, so $n = 4$.\n\n"
                    "Two-face cubes lie along the edges, excluding the corners: $12(n-2) = 12 \\times 2 = 24$.\n\n"
                    "So 24 small cubes have exactly two painted faces."
                ),
                alt="Check the total: $8 + 24 + 6(4) + 8 = 8 + 24 + 24 + 8 = 64$. It balances.",
            ),
        ],
        formulas=[
            FC(
                title="Painted cube counts",
                body="For an $n \\times n \\times n$ cut: 3 faces $= 8$, 2 faces $= 12(n-2)$, 1 face $= 6(n-2)^2$, 0 faces $= (n-2)^3$.",
                example="$n = 5$: 8, 36, 54 and 27, totalling 125.",
            ),
            FC(
                title="Standard dice",
                body="Opposite faces sum to 7. Any two faces visible together in one view are adjacent, never opposite.",
                example="If 2 and 5 are both visible, neither is opposite the other, so 2 faces 5's opposite side.",
            ),
        ],
        traps=[
            "Using $n$ where $n-2$ is needed. The corners are always excluded from edge and face counts.",
            "Forgetting that the corner count is always 8, regardless of how many cuts are made.",
            "Assuming two faces seen in the same view could be opposite.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.quant-embedded",
        intuition=(
            "Some LR sets hide ordinary arithmetic inside a logic puzzle. You might have to work out who sat "
            "where **and** compute how much each person paid.\n\n"
            "The trap is treating it as two separate problems. Usually the arithmetic constrains the logic: a "
            "total that must come out right eliminates most arrangements immediately."
        ),
        core=(
            "Read the set twice — once for the logical structure (who, what, where) and once for the numeric "
            "constraints (totals, averages, differences).\n\n"
            "Then use the numbers as filters. If the four values must sum to 100 and three arrangements are "
            "logically possible, computing the sums usually kills two of them at once.\n\n"
            "Set up the logic grid as usual, but add a column for the numeric attribute so the two kinds of "
            "constraint can talk to each other."
        ),
        examples=[
            EX(
                stem="Three people scored distinct whole numbers summing to 30, each between 8 and 12. A scored more than B, who scored more than C. Find the scores.",
                solution=(
                    "Distinct values from 8 to 12 summing to 30. The possible triples are {8, 10, 12} and "
                    "{9, 10, 11}.\n\n"
                    "Both sum to 30, so the numeric constraint alone does not decide it — but both are "
                    "consistent with $A > B > C$.\n\n"
                    "So the data is insufficient without a further clue, and recognising that is the correct answer."
                ),
                alt="Noticing when a set is under-determined saves more time than grinding for a unique answer that is not there.",
            ),
        ],
        formulas=[
            FC(
                title="Numbers as filters",
                body="Enumerate the logically possible arrangements, then discard those whose totals or averages do not fit.",
                example="Three arrangements reduced to one by a required total is the usual shape.",
            ),
        ],
        traps=[
            "Solving the logic fully before looking at the numbers, when the numbers would have pruned the work.",
            "Assuming values are whole numbers when the set never said so.",
            "Missing that the set is genuinely under-determined and forcing an answer.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="dilr.lr.number-placement",
        intuition=(
            "This is Sudoku's family. You have a grid, some numbers already placed, and rules about what can "
            "go where — each row sums to a value, or no digit repeats in a line.\n\n"
            "The method is always the same: find the most constrained cell, not the first empty one. A row "
            "with five of six entries filled tells you the sixth immediately."
        ),
        core=(
            "Scan for the cell with the fewest possibilities and fill that. It will usually force a neighbour, "
            "which forces another. Working the most-constrained cell first turns a large search into a chain "
            "of forced moves.\n\n"
            "For magic squares, the row, column and diagonal sums are all equal, and for a $3 \\times 3$ square "
            "using 1 to 9 that common sum is 15, with 5 always in the centre.\n\n"
            "If you must guess, note where you guessed so you can unwind cleanly on a contradiction."
        ),
        examples=[
            EX(
                stem="A row of a magic square using 1-9 contains 8 and 3. What is the third entry?",
                solution=(
                    "Every line of a $3 \\times 3$ magic square using 1 to 9 sums to 15.\n\n"
                    "$15 - 8 - 3 = 4$.\n\nThe third entry is 4."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Most-constrained first",
                body="Always fill the cell with the fewest remaining options. It converts searching into forced deduction.",
                example="A row missing one entry is fully determined by the row's sum.",
            ),
            FC(
                title="3 by 3 magic square",
                body="Using 1 to 9, every row, column and diagonal sums to 15, and the centre is always 5.",
                example="A corner of 8 forces the opposite corner to 2, since $8 + 5 + 2 = 15$.",
            ),
        ],
        traps=[
            "Filling cells in reading order instead of by how constrained they are.",
            "Forgetting the diagonals when checking a magic square.",
            "Guessing without recording it, so a contradiction cannot be traced back.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="dilr.di.tables",
        intuition=(
            "A table is data with nowhere to hide — no scale to misread, no legend to confuse. Which means "
            "the difficulty is never in reading it, only in deciding **what to compute** and how much of the "
            "table you actually need.\n\n"
            "Most tables are far bigger than the question requires. Finding the two relevant cells fast is "
            "the real skill."
        ),
        core=(
            "Read the row and column headers and the units before anything else. Then read the question and "
            "identify exactly which cells it touches. Resist computing row totals you were never asked for.\n\n"
            "Common asks: a single lookup, a ratio between two cells, a row or column total, a percentage "
            "change across two periods, or a rank ('which region grew fastest'). Ranking questions need every "
            "row computed, so check whether the question really needs all of them before starting."
        ),
        examples=[
            EX(
                stem="A table shows a product's sales as 240 in 2022 and 300 in 2023. Find the percentage growth.",
                solution=(
                    "Growth $= \\dfrac{300 - 240}{240} \\times 100 = \\dfrac{60}{240} \\times 100 = 25$ percent."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Ratio and share",
                body="Share of a total $= \\dfrac{\\text{cell}}{\\text{row or column total}} \\times 100$.",
                example="A cell of 30 in a row totalling 120 is a 25 percent share.",
            ),
        ],
        traps=[
            "Computing totals the question never asked for.",
            "Reading across the wrong row, especially in a wide table. Track with a finger or cursor.",
            "Missing a units note such as 'figures in thousands'.",
        ],
        minutes=5,
        extra_sections=[("Choosing whether to attempt a set", _SET_SELECTION)],
    ),
    LessonSpec(
        mt="dilr.lr.arrangements",
        intuition=(
            "Six people around a circular table, and clues about who sits next to whom. The thing that makes "
            "circular arrangements different from a straight line is that there is no first or last seat — "
            "only neighbours.\n\n"
            "So fix somebody's position arbitrarily and arrange everyone else relative to them. Rotating the "
            "whole table does not create a new arrangement."
        ),
        core=(
            "Draw the actual shape — a circle with the right number of seats, or a row of boxes. Do not try "
            "to hold it in your head.\n\n"
            "Fix one person to break the rotational symmetry. Then place the most rigid clue next: 'X sits "
            "immediately left of Y' is far more restrictive than 'X sits somewhere opposite Y'.\n\n"
            "Direction matters enormously in circular puzzles. Decide once whether people face the centre or "
            "outwards, since that flips what 'left' means, and write it at the top of your diagram."
        ),
        examples=[
            EX(
                stem="Five people sit in a circle. B is immediately clockwise of A. C is directly opposite... with 5 seats, why is that impossible?",
                solution=(
                    "With an odd number of seats, no seat has a true opposite — the position directly across "
                    "falls between two seats.\n\n"
                    "'Directly opposite' clues only make sense when the number of seats is even.\n\n"
                    "Spotting that immediately tells you the clue must mean something else, or the set has a "
                    "different seat count than assumed."
                ),
                alt="Checking whether opposites can even exist takes two seconds and prevents a lot of wasted effort.",
            ),
        ],
        formulas=[
            FC(
                title="Fix one, arrange the rest",
                body="In a circle, fix one person to remove rotational duplicates. $n$ people in a circle have $(n-1)!$ distinct arrangements.",
                example="5 people around a table have $4! = 24$ arrangements, not 120.",
            ),
            FC(
                title="Opposites need even seats",
                body="A seat has a directly opposite seat only when the total number of seats is even.",
                example="In 8 seats, seat 1 faces seat 5. In 7 seats, nothing faces seat 1 exactly.",
            ),
        ],
        traps=[
            "Forgetting to state whether people face inward or outward, which reverses left and right.",
            "Treating rotations of the same arrangement as different answers.",
            "Applying 'directly opposite' logic to an odd number of seats.",
        ],
        minutes=7,
        extra_sections=[("Choosing whether to attempt a set", _SET_SELECTION)],
    ),
]
