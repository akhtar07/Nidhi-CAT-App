"""
Reusable DI question archetypes over a `{categories, series}` dataset.

## Why archetypes rather than more scenarios

`qagen/templates/__init__.py` records the failure this guards against: the shipped QA bank
once had 398 questions built from 57 distinct skeletons, and all 12 `qa.arith.percentages`
items asked the same thing with different numbers. A learner who does all 12 has practised
one trick twelve times.

The same trap is even easier to fall into with DI, because inventing a fresh scenario feels
like inventing a fresh question. It is not: "read the March bar" and "read the September bar"
are one question. So the varying part here is the *operation demanded* — read, total,
compare, rank by percentage change, weight by base — and each set draws four different ones.

Every archetype returns a `QSpec` whose answer is computed from the data, never typed in, so
the numbers in the stem, the answer and the solution text cannot drift apart. The caller
asserts the expected value at the call site: that double entry is what catches a
transposed digit in the source data itself, which no amount of internal consistency would.

`noun` lets one archetype read naturally across chart types — "bar", "point on the line",
"segment", "vertex" — without duplicating the code.
"""

from __future__ import annotations

from dilr_common import QSpec, fmt

Series = dict[str, list[float]]


def _labelled(categories: list[str], values: list[float], unit: str = "") -> str:
    suffix = f" {unit}" if unit else ""
    return ", ".join(f"{c} {fmt(v)}{suffix}" for c, v in zip(categories, values))


def read_value(
    categories: list[str], data: Series, name: str, category: str, unit: str, noun: str = "bar"
) -> QSpec:
    """Straight lookup. Every set needs one — it is how a learner confirms they have read the
    axes the right way round before committing time to the harder questions."""
    idx = categories.index(category)
    value = data[name][idx]
    return QSpec(
        stem=f"What was {name}'s figure for {category}?",
        value=value,
        difficulty="easy",
        target_seconds=40,
        solution=f"Read the {name} {noun} for {category}: **{fmt(value)} {unit}**.",
    )


def series_total(categories: list[str], data: Series, name: str, unit: str) -> QSpec:
    values = data[name]
    total = sum(values)
    return QSpec(
        stem=f"What was {name}'s total across all {len(categories)} {_period(categories)}?",
        value=total,
        difficulty="medium",
        target_seconds=80,
        solution=(
            f"Add the {len(categories)} {name} figures:\n\n"
            f"${' + '.join(fmt(v) for v in values)} = {fmt(total)}$\n\n"
            f"Total **{fmt(total)} {unit}**."
        ),
    )


def series_average(categories: list[str], data: Series, name: str, unit: str) -> QSpec:
    values = data[name]
    total = sum(values)
    avg = total / len(values)
    return QSpec(
        stem=f"What was {name}'s average per {_period(categories, singular=True)}?",
        value=avg,
        tolerance=0.01,
        difficulty="medium",
        target_seconds=80,
        solution=(
            f"$\\dfrac{{{' + '.join(fmt(v) for v in values)}}}{{{len(values)}}} = "
            f"\\dfrac{{{fmt(total)}}}{{{len(values)}}} = {fmt(round(avg, 2))}$\n\n"
            f"Average **{fmt(round(avg, 2))} {unit}**."
        ),
    )


def count_exceeds(categories: list[str], data: Series, a: str, b: str) -> QSpec:
    """How often does one series beat another. Tests reading across, not reading off."""
    wins = [c for c, x, y in zip(categories, data[a], data[b]) if x > y]
    return QSpec(
        stem=f"In how many {_period(categories)} was {a} higher than {b}?",
        value=len(wins),
        difficulty="medium",
        target_seconds=70,
        solution=(
            f"Compare the two figures {_period(categories, singular=True)} by "
            f"{_period(categories, singular=True)}. {a} is ahead in "
            + (", ".join(wins) if wins else "none of them")
            + f" — **{len(wins)}**."
        ),
    )


def largest_gap(categories: list[str], data: Series, a: str, b: str, unit: str) -> QSpec:
    gaps = [abs(x - y) for x, y in zip(data[a], data[b])]
    if gaps.count(max(gaps)) != 1:
        raise ValueError("largest_gap needs a unique maximum")
    winner = categories[gaps.index(max(gaps))]
    return QSpec(
        stem=f"In which {_period(categories, singular=True)} was the gap between {a} and {b} the largest?",
        options=list(categories),
        correct=winner,
        difficulty="hard",
        target_seconds=90,
        solution=(
            "Gap in each:\n\n"
            + "\n".join(f"- {c}: $|{fmt(x)} - {fmt(y)}| = {fmt(g)}$" for c, x, y, g in zip(categories, data[a], data[b], gaps))
            + f"\n\nThe largest is **{winner}**, at {fmt(max(gaps))} {unit}."
        ),
    )


def percentage_change(
    categories: list[str], data: Series, name: str, frm: str, to: str
) -> QSpec:
    i, j = categories.index(frm), categories.index(to)
    old, new = data[name][i], data[name][j]
    change = (new - old) / old * 100
    direction = "increase" if change >= 0 else "decrease"
    return QSpec(
        stem=f"By what percentage did {name} change from {frm} to {to}?",
        value=round(abs(change), 2),
        tolerance=0.05,
        difficulty="medium",
        target_seconds=90,
        solution=(
            f"The base is the **earlier** figure, {fmt(old)}:\n\n"
            f"$\\dfrac{{{fmt(new)} - {fmt(old)}}}{{{fmt(old)}}} \\times 100 = {fmt(round(change, 2))}\\%$\n\n"
            f"A **{fmt(round(abs(change), 2))}% {direction}**. Dividing by the later figure instead is the "
            "single most common error in this question type."
        ),
    )


def fastest_growth(categories: list[str], data: Series, frm: str, to: str) -> QSpec:
    """Percentage growth ranks differently from absolute growth. That gap is the question."""
    i, j = categories.index(frm), categories.index(to)
    growth = {n: (v[j] - v[i]) / v[i] * 100 for n, v in data.items()}
    absolute = {n: v[j] - v[i] for n, v in data.items()}
    winner = max(growth, key=lambda n: growth[n])
    if list(growth.values()).count(growth[winner]) != 1:
        raise ValueError("fastest_growth needs a unique maximum")
    biggest_abs = max(absolute, key=lambda n: absolute[n])
    note = (
        f" {biggest_abs} grew by the largest **amount** ({fmt(absolute[biggest_abs])}) and is not the answer, "
        "because it starts from a much larger base."
        if biggest_abs != winner
        else ""
    )
    # With only two or three series the entity names alone would make a 3-option MCQ, which no
    # real paper uses. Padding with these two keeps the option count exam-like, and both are
    # answers a learner might genuinely reach: "same rate" if they compare absolute gains on a
    # chart with similar bases, "cannot be determined" if they think percentage growth needs
    # information the chart withholds.
    options = list(data)
    for filler in ("All of them grew at the same rate", "Cannot be determined from the data given"):
        if len(options) >= 4:
            break
        options.append(filler)

    return QSpec(
        stem=f"Which of these grew the fastest in percentage terms from {frm} to {to}?",
        options=options,
        correct=winner,
        difficulty="hard",
        target_seconds=110,
        solution=(
            "Percentage growth, each against its own starting figure:\n\n"
            + "\n".join(
                f"- {n}: $\\dfrac{{{fmt(v[j])} - {fmt(v[i])}}}{{{fmt(v[i])}}} = {fmt(round(growth[n], 2))}\\%$"
                for n, v in data.items()
            )
            + f"\n\nFastest is **{winner}**.{note}"
        ),
    )


def combined_at(categories: list[str], data: Series, category: str, unit: str) -> QSpec:
    idx = categories.index(category)
    parts = {n: v[idx] for n, v in data.items()}
    total = sum(parts.values())
    return QSpec(
        stem=f"What was the combined figure across all {len(data)} categories for {category}?",
        value=total,
        difficulty="easy",
        target_seconds=50,
        solution=(
            f"${' + '.join(fmt(v) for v in parts.values())} = {fmt(total)}$, so **{fmt(total)} {unit}**."
        ),
    )


def highest_combined(categories: list[str], data: Series) -> QSpec:
    totals = [sum(v[i] for v in data.values()) for i in range(len(categories))]
    if totals.count(max(totals)) != 1:
        raise ValueError("highest_combined needs a unique maximum")
    winner = categories[totals.index(max(totals))]
    return QSpec(
        stem=f"In which {_period(categories, singular=True)} was the combined figure the highest?",
        options=list(categories),
        correct=winner,
        difficulty="medium",
        target_seconds=80,
        solution=(
            "Combined figures: " + _labelled(categories, totals) + f".\n\nHighest is **{winner}**."
        ),
    )


def share_of_total(categories: list[str], data: Series, name: str, category: str) -> QSpec:
    """What fraction of a series' whole sits in one category — the question a pie chart answers
    directly and a bar chart makes you work for."""
    idx = categories.index(category)
    value = data[name][idx]
    total = sum(data[name])
    share = value / total * 100
    return QSpec(
        stem=f"{category} accounted for what percentage of {name}'s total?",
        value=round(share, 2),
        tolerance=0.05,
        difficulty="hard",
        target_seconds=100,
        solution=(
            f"Total {name} is ${' + '.join(fmt(v) for v in data[name])} = {fmt(total)}$.\n\n"
            f"$\\dfrac{{{fmt(value)}}}{{{fmt(total)}}} \\times 100 = {fmt(round(share, 2))}\\%$\n\n"
            f"**{fmt(round(share, 2))}%**."
        ),
    )


def share_in_stack(categories: list[str], data: Series, name: str, category: str) -> QSpec:
    """Share of one segment within a single stacked column.

    Distinct from `share_of_total`, which runs along one series across categories. Confusing the
    two is the characteristic stacked-chart error: the denominator is the height of *this*
    column, not the sum of that segment everywhere."""
    idx = categories.index(category)
    value = data[name][idx]
    column_total = sum(v[idx] for v in data.values())
    share = value / column_total * 100
    return QSpec(
        stem=f"In {category}, {name} accounted for what percentage of the total?",
        value=round(share, 2),
        tolerance=0.05,
        difficulty="hard",
        target_seconds=100,
        solution=(
            f"The whole column for {category} is "
            f"${' + '.join(fmt(v[idx]) for v in data.values())} = {fmt(column_total)}$.\n\n"
            f"$\\dfrac{{{fmt(value)}}}{{{fmt(column_total)}}} \\times 100 = {fmt(round(share, 2))}\\%$\n\n"
            f"**{fmt(round(share, 2))}%**. The denominator is this column's own height, not the total "
            f"of {name} across every column."
        ),
    )


def count_above_average(categories: list[str], data: Series, name: str) -> QSpec:
    values = data[name]
    avg = sum(values) / len(values)
    above = [c for c, v in zip(categories, values) if v > avg]
    return QSpec(
        stem=f"In how many {_period(categories)} was {name} above its own {len(values)}-{_period(categories, singular=True)} average?",
        value=len(above),
        difficulty="hard",
        target_seconds=100,
        solution=(
            f"The average is $\\dfrac{{{fmt(sum(values))}}}{{{len(values)}}} = {fmt(round(avg, 2))}$.\n\n"
            f"Figures above it: " + (", ".join(above) if above else "none")
            + f" — **{len(above)}**. A value cannot be above average in more than half the "
            "periods unless the low ones are very low; checking that sanity is a quick way to "
            "catch an arithmetic slip."
        ),
    )


def ratio_at(categories: list[str], data: Series, a: str, b: str, category: str) -> QSpec:
    idx = categories.index(category)
    x, y = data[a][idx], data[b][idx]
    ratio = x / y
    return QSpec(
        stem=f"In {category}, what was the ratio of {a} to {b}? Give the answer as a decimal.",
        value=round(ratio, 2),
        tolerance=0.02,
        difficulty="medium",
        target_seconds=70,
        solution=f"$\\dfrac{{{fmt(x)}}}{{{fmt(y)}}} = {fmt(round(ratio, 2))}$, so the ratio is **{fmt(round(ratio, 2))} : 1**.",
    )


# ---------------------------------------------------------------------------


_MONTHS = {"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"}


def _period(categories: list[str], singular: bool = False) -> str:
    """Picks the right noun for the category axis so stems read naturally."""
    first = categories[0]
    if first.isdigit() and len(first) == 4:
        return "year" if singular else "years"
    if first in _MONTHS:
        return "month" if singular else "months"
    if first.startswith("Q") and first[1:].isdigit():
        return "quarter" if singular else "quarters"
    return "category" if singular else "categories"
