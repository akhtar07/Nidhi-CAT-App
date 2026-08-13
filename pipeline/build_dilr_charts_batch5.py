"""
Additional sets for the five DI chart topics that shipped with a single set each:
bar-column, line-charts, pie-charts, stacked-charts and tables.

Three new sets per topic (four per topic in total, 16 questions), clearing SPEC.md §16's bar
of 15 questions per micro-topic.

The scenario changes every set, but the thing that actually varies is the *operation* each
question demands — see the module docstring of `dilr_di_archetypes.py` for why that is the
axis that matters. Every set draws four different archetypes, so a learner working through
one topic meets read-off, aggregate, cross-series comparison, percentage-change and
share-of-base questions rather than the same question with new numbers.

Pie sets are hand-written rather than archetype-driven: a pie carries shares of one whole,
so the interesting questions (central angle, applying a share to a changed base, chaining a
second pie off one slice of the first) have no analogue in the categories/series shape.

All figures are invented; entities are lettered or generic so no synthetic statistic can be
mistaken for a real one.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_charts_batch5.py
"""

from __future__ import annotations

from dilr_common import QSpec, SetPlan, emit_all, fmt
from dilr_di_archetypes import (
    Series,
    combined_at,
    count_above_average,
    count_exceeds,
    fastest_growth,
    highest_combined,
    largest_gap,
    percentage_change,
    read_value,
    series_average,
    series_total,
    share_in_stack,
    share_of_total,
)


def chart_asset(kind: str, categories: list[str], data: Series, unit: str) -> dict:
    return {
        "type": "chart",
        "spec": {
            "chartKind": kind,
            "categories": categories,
            "series": [{"name": n, "values": v} for n, v in data.items()],
            "unit": unit,
        },
    }


def table_asset(row_header: str, categories: list[str], data: Series) -> dict:
    return {
        "type": "table",
        "spec": {
            "columns": [row_header, *data.keys()],
            "rows": [[c, *(fmt(v[i]) for v in data.values())] for i, c in enumerate(categories)],
        },
    }


# ---------------------------------------------------------------------------
# Bar / column
# ---------------------------------------------------------------------------


def bar_factory() -> SetPlan:
    cats = ["Jan", "Feb", "Mar", "Apr", "May"]
    data: Series = {"Plant X": [340, 420, 380, 500, 460], "Plant Y": [300, 350, 410, 390, 520]}
    assert sum(data["Plant Y"]) == 1970
    return SetPlan(
        micro_topic="dilr.di.bar-column",
        slug="factory-output",
        body=(
            "The bar chart below shows the monthly output, in units, of two plants of the same "
            "manufacturer.\n\nStudy the chart and answer the questions that follow."
        ),
        assets=[chart_asset("bar", cats, data, "units")],
        questions=[
            read_value(cats, data, "Plant X", "Mar", "units"),
            series_total(cats, data, "Plant Y", "units"),
            count_exceeds(cats, data, "Plant Y", "Plant X"),
            largest_gap(cats, data, "Plant X", "Plant Y", "units"),
        ],
    )


def bar_rainfall() -> SetPlan:
    cats = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
    data: Series = {"District A": [180, 260, 240, 120, 40, 20], "District B": [150, 300, 210, 90, 60, 30]}
    assert sum(data["District A"]) == 860
    return SetPlan(
        micro_topic="dilr.di.bar-column",
        slug="rainfall",
        body=(
            "The bar chart below shows monsoon rainfall, in millimetres, recorded in two districts "
            "over six months.\n\nStudy the chart and answer the questions that follow."
        ),
        assets=[chart_asset("bar", cats, data, "mm")],
        questions=[
            read_value(cats, data, "District A", "Aug", "mm"),
            series_average(cats, data, "District A", "mm"),
            share_of_total(cats, data, "District A", "Jul"),
            count_above_average(cats, data, "District A"),
        ],
    )


def bar_placements() -> SetPlan:
    cats = ["2021", "2022", "2023", "2024"]
    data: Series = {"CSE": [120, 150, 180, 240], "ECE": [90, 100, 110, 130], "Mechanical": [60, 66, 72, 90]}
    assert [sum(v[i] for v in data.values()) for i in range(4)] == [270, 316, 362, 460]
    return SetPlan(
        micro_topic="dilr.di.bar-column",
        slug="placements",
        body=(
            "The bar chart below shows the number of students placed from three branches of an "
            "engineering college over four years.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[chart_asset("bar", cats, data, "students")],
        questions=[
            combined_at(cats, data, "2022", "students"),
            highest_combined(cats, data),
            percentage_change(cats, data, "ECE", "2021", "2024"),
            fastest_growth(cats, data, "2021", "2024"),
        ],
    )


# ---------------------------------------------------------------------------
# Line
# ---------------------------------------------------------------------------


def line_traffic() -> SetPlan:
    cats = ["Jan", "Feb", "Mar", "Apr", "May"]
    data: Series = {"Site P": [120, 140, 160, 150, 200], "Site Q": [90, 150, 130, 180, 165]}
    assert sum(data["Site Q"]) == 715
    return SetPlan(
        micro_topic="dilr.di.line-charts",
        slug="web-traffic",
        body=(
            "The line chart below shows monthly visits, in thousands, to two websites.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[chart_asset("line", cats, data, "thousand visits")],
        questions=[
            read_value(cats, data, "Site P", "Mar", "thousand visits", noun="point on the line"),
            series_total(cats, data, "Site Q", "thousand visits"),
            largest_gap(cats, data, "Site P", "Site Q", "thousand visits"),
            fastest_growth(cats, data, "Jan", "May"),
        ],
    )


def line_hospitals() -> SetPlan:
    cats = ["Jun", "Jul", "Aug", "Sep", "Oct", "Nov"]
    data: Series = {
        "Hospital A": [420, 460, 510, 480, 530, 560],
        "Hospital B": [380, 500, 470, 520, 490, 600],
    }
    assert sum(data["Hospital A"]) == 2960 and sum(data["Hospital B"]) == 2960
    return SetPlan(
        micro_topic="dilr.di.line-charts",
        slug="hospitals",
        body=(
            "The line chart below shows the number of outpatients seen each month at two "
            "hospitals.\n\nStudy the chart and answer the questions that follow."
        ),
        assets=[chart_asset("line", cats, data, "patients")],
        questions=[
            read_value(cats, data, "Hospital A", "Sep", "patients", noun="point on the line"),
            series_average(cats, data, "Hospital B", "patients"),
            count_exceeds(cats, data, "Hospital B", "Hospital A"),
            share_of_total(cats, data, "Hospital A", "Nov"),
        ],
    )


def line_apps() -> SetPlan:
    cats = ["2020", "2021", "2022", "2023", "2024"]
    data: Series = {
        "App A": [50, 80, 120, 150, 200],
        "App B": [200, 180, 160, 150, 140],
        "App C": [30, 60, 90, 150, 240],
    }
    assert [sum(v[i] for v in data.values()) for i in range(5)] == [280, 320, 370, 450, 580]
    return SetPlan(
        micro_topic="dilr.di.line-charts",
        slug="app-downloads",
        body=(
            "The line chart below shows annual downloads, in lakh, of three mobile apps.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[chart_asset("line", cats, data, "lakh downloads")],
        questions=[
            combined_at(cats, data, "2022", "lakh downloads"),
            highest_combined(cats, data),
            percentage_change(cats, data, "App B", "2020", "2024"),
            count_above_average(cats, data, "App C"),
        ],
    )


# ---------------------------------------------------------------------------
# Stacked
# ---------------------------------------------------------------------------


def stacked_segments() -> SetPlan:
    cats = ["2021", "2022", "2023", "2024"]
    data: Series = {"Products": [120, 140, 160, 200], "Services": [80, 110, 150, 220], "Licensing": [40, 50, 60, 80]}
    assert [sum(v[i] for v in data.values()) for i in range(4)] == [240, 300, 370, 500]
    return SetPlan(
        micro_topic="dilr.di.stacked-charts",
        slug="revenue-segments",
        body=(
            "The stacked column chart below splits a company's annual revenue, in Rs crore, across "
            "its three business segments.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[chart_asset("stacked-bar", cats, data, "Rs crore")],
        questions=[
            combined_at(cats, data, "2023", "Rs crore"),
            highest_combined(cats, data),
            share_in_stack(cats, data, "Services", "2024"),
            count_exceeds(cats, data, "Services", "Products"),
        ],
    )


def stacked_fees() -> SetPlan:
    cats = ["2021", "2022", "2023", "2024"]
    data: Series = {"Tuition": [60, 66, 72, 80], "Hostel": [30, 33, 36, 40], "Other charges": [10, 11, 12, 15]}
    assert [sum(v[i] for v in data.values()) for i in range(4)] == [100, 110, 120, 135]
    return SetPlan(
        micro_topic="dilr.di.stacked-charts",
        slug="college-fees",
        body=(
            "The stacked column chart below splits a college's annual fee, in Rs thousand, into its "
            "three components.\n\nStudy the chart and answer the questions that follow."
        ),
        assets=[chart_asset("stacked-bar", cats, data, "Rs thousand")],
        questions=[
            read_value(cats, data, "Tuition", "2023", "Rs thousand", noun="segment"),
            combined_at(cats, data, "2024", "Rs thousand"),
            share_in_stack(cats, data, "Other charges", "2024"),
            fastest_growth(cats, data, "2021", "2024"),
        ],
    )


def stacked_commute() -> SetPlan:
    cats = ["2020", "2021", "2022", "2023", "2024"]
    data: Series = {"Bus": [40, 42, 38, 45, 50], "Metro": [10, 15, 22, 30, 42], "Car": [25, 26, 28, 27, 30]}
    assert [sum(v[i] for v in data.values()) for i in range(5)] == [75, 83, 88, 102, 122]
    return SetPlan(
        micro_topic="dilr.di.stacked-charts",
        slug="commuters",
        body=(
            "The stacked column chart below splits a city's daily commuters, in lakh, across three "
            "modes of transport.\n\nStudy the chart and answer the questions that follow."
        ),
        assets=[chart_asset("stacked-bar", cats, data, "lakh commuters")],
        questions=[
            read_value(cats, data, "Metro", "2022", "lakh commuters", noun="segment"),
            highest_combined(cats, data),
            share_in_stack(cats, data, "Metro", "2024"),
            fastest_growth(cats, data, "2020", "2024"),
        ],
    )


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------


def table_crops() -> SetPlan:
    cats = ["State P", "State Q", "State R", "State S", "State T"]
    data: Series = {
        "Rice": [120, 200, 150, 90, 180],
        "Wheat": [80, 60, 220, 140, 100],
        "Maize": [50, 90, 70, 110, 130],
    }
    assert sum(data["Rice"]) == 740
    return SetPlan(
        micro_topic="dilr.di.tables",
        slug="crop-production",
        body=(
            "The table below shows the production of three crops, in thousand tonnes, in five "
            "states in a given year.\n\nStudy the table and answer the questions that follow."
        ),
        assets=[table_asset("State", cats, data)],
        questions=[
            read_value(cats, data, "Wheat", "State R", "thousand tonnes", noun="entry"),
            combined_at(cats, data, "State S", "thousand tonnes"),
            share_of_total(cats, data, "Rice", "State Q"),
            largest_gap(cats, data, "Rice", "Wheat", "thousand tonnes"),
        ],
    )


def table_headcount() -> SetPlan:
    cats = ["2020", "2021", "2022", "2023", "2024"]
    data: Series = {"Engineering": [200, 240, 300, 360, 400], "Sales": [150, 160, 180, 200, 210]}
    assert sum(data["Engineering"]) == 1500 and sum(data["Sales"]) == 900
    return SetPlan(
        micro_topic="dilr.di.tables",
        slug="headcount",
        body=(
            "The table below shows the year-end headcount of two departments at a company.\n\n"
            "Study the table and answer the questions that follow."
        ),
        assets=[table_asset("Year", cats, data)],
        questions=[
            read_value(cats, data, "Engineering", "2022", "employees", noun="entry"),
            series_average(cats, data, "Sales", "employees"),
            percentage_change(cats, data, "Engineering", "2020", "2024"),
            count_above_average(cats, data, "Engineering"),
        ],
    )


def table_malls() -> SetPlan:
    cats = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    data: Series = {
        "Mall A": [45, 52, 48, 60, 55, 70],
        "Mall B": [60, 58, 62, 55, 65, 68],
        "Mall C": [30, 35, 40, 42, 50, 58],
    }
    assert [sum(v[i] for v in data.values()) for i in range(6)] == [135, 145, 150, 157, 170, 196]
    return SetPlan(
        micro_topic="dilr.di.tables",
        slug="mall-footfall",
        body=(
            "The table below shows monthly footfall, in thousands, at three shopping malls.\n\n"
            "Study the table and answer the questions that follow."
        ),
        assets=[table_asset("Month", cats, data)],
        questions=[
            read_value(cats, data, "Mall C", "Apr", "thousand visitors", noun="entry"),
            combined_at(cats, data, "Feb", "thousand visitors"),
            count_exceeds(cats, data, "Mall A", "Mall B"),
            fastest_growth(cats, data, "Jan", "Jun"),
        ],
    )


# ---------------------------------------------------------------------------
# Pie — hand-written, see module docstring
# ---------------------------------------------------------------------------


def pie_asset(slices: dict[str, float], unit: str) -> dict:
    total = sum(slices.values())
    assert abs(total - 100) < 1e-9, f"shares must sum to 100, got {total}"
    return {
        "type": "chart",
        "spec": {
            "chartKind": "pie",
            "slices": [{"name": n, "value": v} for n, v in slices.items()],
            "unit": unit,
        },
    }


def pie_budget() -> SetPlan:
    shares = {"Rent": 30, "Food": 22, "Education": 18, "Transport": 12, "Savings": 10, "Other": 8}
    income = 60000
    rent = income * shares["Rent"] / 100
    assert rent == 18000
    gap = income * (shares["Education"] - shares["Transport"]) / 100
    assert gap == 3600
    savings_angle = shares["Savings"] / 100 * 360
    assert savings_angle == 36
    new_rent = 75000 * 24 / 100
    assert new_rent == 18000

    return SetPlan(
        micro_topic="dilr.di.pie-charts",
        slug="household-budget",
        body=(
            "A household's monthly income of Rs 60,000 is spent as shown in the pie chart below. "
            "Each figure is a percentage of the monthly income.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[pie_asset(shares, "%")],
        questions=[
            QSpec(
                stem="How much does the household spend on rent each month, in rupees?",
                value=rent,
                difficulty="easy",
                target_seconds=50,
                solution=f"$60{{,}}000 \\times \\dfrac{{30}}{{100}} = 18{{,}}000$, so **Rs {fmt(rent)}**.",
            ),
            QSpec(
                stem="By how many rupees does monthly spending on education exceed spending on transport?",
                value=gap,
                difficulty="medium",
                target_seconds=70,
                solution=(
                    "Work with the difference in shares rather than computing both amounts:\n\n"
                    "$(18 - 12)\\% \\text{ of } 60{,}000 = 6\\% \\times 60{,}000 = 3{,}600$\n\n"
                    f"**Rs {fmt(gap)}**."
                ),
            ),
            QSpec(
                stem="What is the central angle, in degrees, of the sector representing savings?",
                value=savings_angle,
                difficulty="medium",
                target_seconds=60,
                solution=(
                    "A full circle is 360 degrees, and savings is 10% of the whole:\n\n"
                    "$\\dfrac{10}{100} \\times 360 = 36$\n\n"
                    f"**{fmt(savings_angle)} degrees**. A useful constant to carry: 1% of a pie is 3.6 degrees."
                ),
            ),
            QSpec(
                stem=(
                    "Next year the household's monthly income rises to Rs 75,000 and rent falls to 24% "
                    "of income. What will the household then spend on rent each month, in rupees?"
                ),
                value=new_rent,
                difficulty="hard",
                target_seconds=100,
                solution=(
                    "$75{,}000 \\times \\dfrac{24}{100} = 18{,}000$\n\n"
                    f"**Rs {fmt(new_rent)}** — exactly what it is today. The rent **share** drops by 6 "
                    "percentage points and the rent **amount** does not move at all, because the base grew "
                    "by 25% at the same time. A pie chart shows shares only, so no change in a slice can "
                    "be read as a change in an amount unless you know what happened to the total."
                ),
            ),
        ],
    )


def pie_college() -> SetPlan:
    streams = {"Science": 35, "Commerce": 30, "Arts": 20, "Law": 15}
    total_students = 1200
    science = total_students * streams["Science"] / 100
    assert science == 420
    commerce = total_students * streams["Commerce"] / 100
    assert commerce == 360
    specialisations = {"Physics": 30, "Chemistry": 25, "Biology": 25, "Mathematics": 20}
    biology = science * specialisations["Biology"] / 100
    assert biology == 105
    maths = science * specialisations["Mathematics"] / 100
    assert maths == 84
    maths_share = round(maths / total_students * 100, 6)  # 84/1200*100 lands on 7.000000000000001
    assert maths_share == 7

    return SetPlan(
        micro_topic="dilr.di.pie-charts",
        slug="college-streams",
        body=(
            "A college has 1,200 students. The first pie chart splits them by stream. The second "
            "pie chart splits the **Science** students alone by specialisation. All figures are "
            "percentages of the relevant whole.\n\n"
            "Study the charts and answer the questions that follow."
        ),
        assets=[pie_asset(streams, "%"), pie_asset(specialisations, "%")],
        questions=[
            QSpec(
                stem="How many students are enrolled in Commerce?",
                value=commerce,
                difficulty="easy",
                target_seconds=50,
                solution=f"$1200 \\times \\dfrac{{30}}{{100}} = 360$, so **{fmt(commerce)} students**.",
            ),
            QSpec(
                stem="How many students are enrolled in Science?",
                value=science,
                difficulty="easy",
                target_seconds=50,
                solution=(
                    f"$1200 \\times \\dfrac{{35}}{{100}} = 420$, so **{fmt(science)} students**. This is the "
                    "figure the second pie chart divides up, so it is worth writing down before going on."
                ),
            ),
            QSpec(
                stem="How many students specialise in Biology?",
                value=biology,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "The second chart's percentages are of the Science students, not of the college:\n\n"
                    "$420 \\times \\dfrac{25}{100} = 105$\n\n"
                    f"**{fmt(biology)} students**. Applying 25% to 1,200 gives 300 and is the trap this "
                    "set is built around."
                ),
            ),
            QSpec(
                stem="Students specialising in Mathematics make up what percentage of the whole college?",
                value=maths_share,
                tolerance=0.05,
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Mathematics is 20% of Science, and Science is 35% of the college, so multiply the "
                    "two shares:\n\n"
                    "$0.20 \\times 0.35 = 0.07 = 7\\%$\n\n"
                    "Checking with headcounts: $420 \\times 0.20 = 84$, and "
                    "$\\dfrac{84}{1200} \\times 100 = 7\\%$.\n\n"
                    f"**{fmt(maths_share)}%**. Nested pies chain by multiplication, never by addition — "
                    "20% and 35% do not combine into 55% or into 20%."
                ),
            ),
        ],
    )


def pie_expenditure() -> SetPlan:
    shares = {"Salaries": 40, "Raw material": 25, "Marketing": 12, "Administration": 9, "R&D": 8, "Misc": 6}
    total = 250.0
    marketing = total * shares["Marketing"] / 100
    assert marketing == 30
    raw_angle = shares["Raw material"] / 100 * 360
    assert raw_angle == 90
    others = shares["Administration"] + shares["R&D"] + shares["Misc"]
    assert others == 23
    excess = total * (shares["Salaries"] - others) / 100
    assert excess == 42.5
    new_salaries = total * 1.2 * 35 / 100
    assert new_salaries == 105

    return SetPlan(
        micro_topic="dilr.di.pie-charts",
        slug="company-expenditure",
        body=(
            "A company's total annual expenditure of Rs 250 lakh is split as shown in the pie chart "
            "below. Each figure is a percentage of total expenditure.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[pie_asset(shares, "%")],
        questions=[
            QSpec(
                stem="How much does the company spend on marketing, in Rs lakh?",
                value=marketing,
                difficulty="easy",
                target_seconds=50,
                solution=f"$250 \\times \\dfrac{{12}}{{100}} = 30$, so **Rs {fmt(marketing)} lakh**.",
            ),
            QSpec(
                stem="What is the central angle, in degrees, of the sector representing raw material?",
                value=raw_angle,
                difficulty="medium",
                target_seconds=60,
                solution=(
                    "$\\dfrac{25}{100} \\times 360 = 90$\n\n"
                    f"**{fmt(raw_angle)} degrees** — a quarter of the pie, which is worth recognising on "
                    "sight rather than computing."
                ),
            ),
            QSpec(
                stem=(
                    "By how much, in Rs lakh, does spending on salaries exceed the combined spending on "
                    "administration, R&D and miscellaneous?"
                ),
                options=["17", "32.5", "42.5", "57.5", "100"],
                correct="42.5",
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Combined share of the three smaller heads: $9 + 8 + 6 = 23\\%$. Salaries are 40%, so "
                    "the difference is $40 - 23 = 17$ percentage points.\n\n"
                    "$250 \\times \\dfrac{17}{100} = 42.5$\n\n"
                    "**Rs 42.5 lakh**. The option 17 is there for anyone who stops at the percentage-point "
                    "gap and forgets to convert it into money."
                ),
            ),
            QSpec(
                stem=(
                    "Next year total expenditure rises by 20% and salaries fall to 35% of the total. "
                    "What will the company then spend on salaries, in Rs lakh?"
                ),
                value=new_salaries,
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "New total: $250 \\times 1.2 = 300$ lakh.\n\n"
                    "$300 \\times \\dfrac{35}{100} = 105$\n\n"
                    f"**Rs {fmt(new_salaries)} lakh**, against Rs 100 lakh this year. Salaries fall by 5 "
                    "percentage points of the pie and still cost 5% more in rupees, because the pie itself "
                    "got bigger."
                ),
            ),
        ],
    )


PLANS = [
    bar_factory(),
    bar_rainfall(),
    bar_placements(),
    line_traffic(),
    line_hospitals(),
    line_apps(),
    stacked_segments(),
    stacked_fees(),
    stacked_commute(),
    table_crops(),
    table_headcount(),
    table_malls(),
    pie_budget(),
    pie_college(),
    pie_expenditure(),
]


if __name__ == "__main__":
    emit_all(PLANS)
