"""
The three DILR chart types that had no questions at all: radar/spider, bubble, combination.

They were blocked on rendering, not on content — `PassageSetPlayer.tsx` had no renderer for
any of them, so a set would have displayed "[chart rendering not yet implemented]". The
renderers landed alongside this script; these are the sets that use them.

Four sets per topic, 16 questions each, which clears SPEC.md §16's bar of 15.

## Data design constraint (bubble charts)

A bubble chart has no printed axis values, so every plotted point must sit exactly on a
labelled gridline or the learner is interpolating by eye and the arithmetic answers become
ambiguous. Each bubble set therefore declares `xDivisions`/`yDivisions` chosen so that all
five points land on gridlines. The third dimension is printed inside the bubble, because
bubble *area* can be compared but not read.

All figures are invented. Places and firms are lettered rather than named, so no synthetic
statistic can be mistaken for a real one.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_new_charts.py
"""

from __future__ import annotations

from dilr_common import QSpec, SetPlan, emit_all, fmt

# ---------------------------------------------------------------------------
# Radar / spider
# ---------------------------------------------------------------------------


def radar_asset(axes: list[str], series: dict[str, list[float]], scale_max: float, unit: str) -> dict:
    return {
        "type": "chart",
        "spec": {
            "chartKind": "radar",
            "axes": axes,
            "series": [{"name": n, "values": v} for n, v in series.items()],
            "max": scale_max,
            "unit": unit,
        },
    }


def radar_phones() -> SetPlan:
    axes = ["Battery", "Camera", "Display", "Performance", "Value"]
    data = {"Aurora": [43, 36, 45, 40, 30], "Bolt": [34, 44, 38, 46, 33]}
    aurora, bolt = data["Aurora"], data["Bolt"]

    bolt_total = sum(bolt)
    assert bolt_total == 195
    bolt_ahead = [a for a, x, y in zip(axes, aurora, bolt) if y > x]
    assert bolt_ahead == ["Camera", "Performance", "Value"]
    gaps = [abs(x - y) for x, y in zip(aurora, bolt)]
    assert gaps == [9, 8, 7, 6, 3]
    widest = axes[gaps.index(max(gaps))]
    assert widest == "Battery"

    return SetPlan(
        micro_topic="dilr.di.radar-spider",
        slug="phones",
        body=(
            "The radar chart below shows how a review site scored two smartphones, Aurora and "
            "Bolt, on five attributes. Each attribute is scored out of 50.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[radar_asset(axes, data, 50, "points out of 50")],
        questions=[
            QSpec(
                stem="What score did Aurora receive on Camera?",
                value=36,
                difficulty="easy",
                target_seconds=40,
                solution="Read the Aurora vertex on the Camera spoke: **36**.",
            ),
            QSpec(
                stem="What is Bolt's total score across all five attributes?",
                value=bolt_total,
                difficulty="medium",
                target_seconds=75,
                solution=(
                    "Add Bolt's five vertex values:\n\n"
                    f"$34 + 44 + 38 + 46 + 33 = {bolt_total}$\n\n"
                    f"Bolt totals **{bolt_total} points**."
                ),
            ),
            QSpec(
                stem="On how many of the five attributes does Bolt score higher than Aurora?",
                value=len(bolt_ahead),
                difficulty="medium",
                target_seconds=70,
                solution=(
                    "Compare the two polygons spoke by spoke. Bolt is outside Aurora on "
                    + ", ".join(bolt_ahead)
                    + f" — that is **{len(bolt_ahead)} attributes**. On Battery and Display, Aurora is further out."
                ),
            ),
            QSpec(
                stem="On which attribute is the gap between the two phones the widest?",
                options=axes,
                correct=widest,
                difficulty="hard",
                target_seconds=90,
                solution=(
                    "Gap on each spoke:\n\n"
                    + "\n".join(f"- {a}: $|{x} - {y}| = {g}$" for a, x, y, g in zip(axes, aurora, bolt, gaps))
                    + f"\n\nThe widest is **{widest}**, at {max(gaps)} points. The trap is to eyeball the "
                    "polygon: a gap looks larger near the rim than the same gap near the centre, because "
                    "the spokes fan out."
                ),
            ),
        ],
    )


def radar_candidates() -> SetPlan:
    axes = ["Analytics", "Communication", "Leadership", "Technical", "Domain"]
    data = {
        "Kavya": [18, 14, 12, 17, 15],
        "Rohit": [15, 18, 16, 13, 14],
        "Meera": [16, 13, 18, 15, 16],
    }
    totals = {n: sum(v) for n, v in data.items()}
    assert totals == {"Kavya": 76, "Rohit": 76, "Meera": 78}
    best_total = max(totals.values())

    kavya_best = [
        a for i, a in enumerate(axes) if data["Kavya"][i] > data["Rohit"][i] and data["Kavya"][i] > data["Meera"][i]
    ]
    assert kavya_best == ["Analytics", "Technical"]

    shortlisted = [n for n, v in data.items() if min(v) >= 15]
    assert shortlisted == []

    return SetPlan(
        micro_topic="dilr.di.radar-spider",
        slug="candidates",
        body=(
            "Three candidates for a single role were rated on five competencies, each scored out "
            "of 20. The radar chart below shows their ratings.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[radar_asset(axes, data, 20, "points out of 20")],
        questions=[
            QSpec(
                stem="What is Meera's rating on Leadership?",
                value=18,
                difficulty="easy",
                target_seconds=40,
                solution="Read Meera's vertex on the Leadership spoke: **18**.",
            ),
            QSpec(
                stem="What is the highest total rating scored by any one candidate across the five competencies?",
                value=best_total,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Totals:\n\n"
                    + "\n".join(f"- {n}: {t}" for n, t in totals.items())
                    + f"\n\nThe highest is **{best_total}** (Meera). Note Kavya and Rohit tie on 76 with very "
                    "differently shaped polygons — equal area does not mean equal profile."
                ),
            ),
            QSpec(
                stem="On how many competencies is Kavya rated strictly higher than both of the other two candidates?",
                value=len(kavya_best),
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "Kavya is the outermost point on " + " and ".join(kavya_best) + f" — **{len(kavya_best)}** "
                    "competencies. On Communication and Leadership she is the innermost, and on Domain "
                    "Meera is ahead of her."
                ),
            ),
            QSpec(
                stem=(
                    "The company shortlists a candidate only if that candidate scores at least 15 on "
                    "**every** competency. Who is shortlisted?"
                ),
                options=["Kavya only", "Rohit only", "Meera only", "Kavya and Meera", "None of them"],
                correct="None of them",
                difficulty="hard",
                target_seconds=90,
                solution=(
                    "The rule is about the weakest spoke, not the total, so look for the innermost vertex "
                    "of each polygon:\n\n"
                    "- Kavya's minimum is 12 (Leadership)\n"
                    "- Rohit's minimum is 13 (Technical)\n"
                    "- Meera's minimum is 13 (Communication)\n\n"
                    "Every candidate dips below 15 somewhere, so **none of them** is shortlisted. Meera has "
                    "the highest total and still fails — an \"every category\" condition is decided by the "
                    "worst value, and a radar chart shows that as the vertex closest to the centre."
                ),
            ),
        ],
    )


def radar_retail() -> SetPlan:
    axes = ["Apparel", "Footwear", "Electronics", "Grocery", "Beauty", "Toys"]
    data = {"2024": [120, 80, 150, 200, 60, 40], "2025": [140, 76, 195, 210, 75, 44]}
    y24, y25 = data["2024"], data["2025"]

    assert sum(y25) == 740
    declines = [a for a, o, n in zip(axes, y24, y25) if n < o]
    assert declines == ["Footwear"]
    growth = [(n - o) / o * 100 for o, n in zip(y24, y25)]
    assert [round(g, 2) for g in growth] == [16.67, -5.0, 30.0, 5.0, 25.0, 10.0]
    fastest = axes[growth.index(max(growth))]
    assert fastest == "Electronics"

    return SetPlan(
        micro_topic="dilr.di.radar-spider",
        slug="retail",
        body=(
            "A retail chain's sales across six categories, in Rs lakh, are plotted for 2024 and "
            "2025 on the radar chart below.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[radar_asset(axes, data, 220, "Rs lakh")],
        questions=[
            QSpec(
                stem="What were the Beauty sales in 2024, in Rs lakh?",
                value=60,
                difficulty="easy",
                target_seconds=40,
                solution="Read the 2024 vertex on the Beauty spoke: **Rs 60 lakh**.",
            ),
            QSpec(
                stem="What were the chain's total sales in 2025 across all six categories, in Rs lakh?",
                value=740,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Add the six 2025 vertices:\n\n"
                    "$140 + 76 + 195 + 210 + 75 + 44 = 740$\n\n"
                    "Total **Rs 740 lakh**."
                ),
            ),
            QSpec(
                stem="In which category did sales fall between 2024 and 2025?",
                options=axes,
                correct="Footwear",
                difficulty="medium",
                target_seconds=60,
                solution=(
                    "Look for the one spoke where the 2025 polygon lies **inside** the 2024 polygon: "
                    "**Footwear**, from 80 down to 76. Everywhere else 2025 is further out."
                ),
            ),
            QSpec(
                stem="Which category recorded the highest percentage growth from 2024 to 2025?",
                options=axes,
                correct=fastest,
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Percentage growth, not absolute growth:\n\n"
                    + "\n".join(f"- {a}: $\\dfrac{{{n} - {o}}}{{{o}}} = {fmt(g)}\\%$" for a, o, n, g in zip(axes, y24, y25, growth))
                    + f"\n\nHighest is **{fastest}** at 30%. Grocery grew by the largest **amount** (10 lakh) "
                    "yet only 5%, because it starts from the biggest base — the classic radar-chart trap, "
                    "since the eye reads the outermost movement as the biggest change."
                ),
            ),
        ],
    )


def radar_students() -> SetPlan:
    axes = ["Arithmetic", "Algebra", "Geometry", "Number System", "Modern Math", "Data Interpretation"]
    data = {"Student P": [72, 65, 58, 80, 54, 68], "Student Q": [66, 71, 62, 74, 60, 63]}
    p, q = data["Student P"], data["Student Q"]

    assert sum(p) == 397 and sum(q) == 396
    p_ahead = [a for a, x, y in zip(axes, p, q) if x > y]
    assert p_ahead == ["Arithmetic", "Number System", "Data Interpretation"]
    q_avg = sum(q) / len(q)
    assert q_avg == 66

    # Raising the average to 70 needs 70*6 - 397 = 23 more marks in one area; the smallest
    # figure that area must reach is therefore (lowest current score) + 23.
    deficit = 70 * 6 - sum(p)
    assert deficit == 23
    needed = min(p) + deficit
    assert needed == 77

    return SetPlan(
        micro_topic="dilr.di.radar-spider",
        slug="students",
        body=(
            "Two students' accuracy, as a percentage, across six Quant areas is shown on the radar "
            "chart below.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[radar_asset(axes, data, 100, "percent accuracy")],
        questions=[
            QSpec(
                stem="What is Student P's accuracy in Number System?",
                value=80,
                difficulty="easy",
                target_seconds=40,
                solution="Read P's vertex on the Number System spoke: **80%**.",
            ),
            QSpec(
                stem="In how many of the six areas is Student P's accuracy higher than Student Q's?",
                value=len(p_ahead),
                difficulty="medium",
                target_seconds=75,
                solution=(
                    "P's polygon lies outside Q's on " + ", ".join(p_ahead) + f" — **{len(p_ahead)} areas**. "
                    "Q leads on Algebra, Geometry and Modern Math."
                ),
            ),
            QSpec(
                stem="What is Student Q's average accuracy across the six areas?",
                value=q_avg,
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "$\\dfrac{66 + 71 + 62 + 74 + 60 + 63}{6} = \\dfrac{396}{6} = 66$\n\n"
                    "Average accuracy **66%**."
                ),
            ),
            QSpec(
                stem=(
                    "Student P wants to raise their average accuracy across the six areas to 70%, and "
                    "will do it by improving exactly one area. What is the lowest accuracy figure that "
                    "area must reach?"
                ),
                options=["70", "74", "77", "80", "83"],
                correct="77",
                difficulty="hard",
                target_seconds=120,
                solution=(
                    "P currently totals $72 + 65 + 58 + 80 + 54 + 68 = 397$. An average of 70% over six "
                    "areas needs $70 \\times 6 = 420$, so P must gain $420 - 397 = 23$ percentage points, "
                    "all in one area.\n\n"
                    "That area must end at (its current score) $+ 23$. To make that ending figure as low "
                    "as possible, improve the **weakest** area — Modern Math at 54:\n\n"
                    "$54 + 23 = 77$\n\n"
                    "So the answer is **77**. Improving Geometry instead would need 81, and Number System "
                    "would need 103, which is impossible. The counter-intuitive part: the number you are "
                    "minimising is the **final** score, and the weakest spoke is the cheapest place to put "
                    "a fixed number of extra marks."
                ),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Bubble
# ---------------------------------------------------------------------------


def bubble_asset(
    points: list[dict],
    x_label: str,
    y_label: str,
    size_label: str,
    x_max: float,
    y_max: float,
    x_div: int,
    y_div: int,
) -> dict:
    # Every point must land on a gridline, or its coordinates cannot be read exactly.
    for p in points:
        assert abs((p["x"] / x_max ** x_div) - round(p["x"] / x_max ** x_div)) < 1e-9, p
        assert abs((p["y"] / y_max ** y_div) - round(p["y"] / y_max ** y_div)) < 1e-9, p
    return {
        "type": "chart",
        "spec": {
            "chartKind": "bubble",
            "points": points,
            "xLabel": x_label,
            "yLabel": y_label,
            "sizeLabel": size_label,
            "xMax": x_max,
            "yMax": y_max,
            "xDivisions": x_div,
            "yDivisions": y_div,
        },
    }


def bubble_startups() -> SetPlan:
    points = [
        {"name": "Alpha", "x": 150, "y": 20, "size": 600},
        {"name": "Beta", "x": 75, "y": 30, "size": 250},
        {"name": "Gamma", "x": 200, "y": 10, "size": 900},
        {"name": "Delta", "x": 100, "y": 35, "size": 300},
        {"name": "Epsilon", "x": 50, "y": 25, "size": 150},
    ]
    profit = {p["name"]: p["x"] * p["y"] / 100 for p in points}
    assert profit == {"Alpha": 30, "Beta": 22.5, "Gamma": 20, "Delta": 35, "Epsilon": 12.5}
    # Revenue per employee in Rs lakh: revenue is in crore, and 1 crore = 100 lakh.
    per_head = {p["name"]: p["x"] * 100 / p["size"] for p in points}
    assert [round(per_head[p["name"]], 2) for p in points] == [25.0, 30.0, 22.22, 33.33, 33.33]
    above_25 = [n for n, v in per_head.items() if v > 25]
    assert above_25 == ["Beta", "Delta", "Epsilon"]

    return SetPlan(
        micro_topic="dilr.di.bubble-charts",
        slug="startups",
        body=(
            "Five startups are plotted below. The horizontal axis is annual revenue in Rs crore, "
            "the vertical axis is profit margin as a percentage of revenue, and the area of each "
            "bubble is proportional to headcount (printed inside the bubble).\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[
            bubble_asset(
                points,
                "Annual revenue (Rs crore)",
                "Profit margin (%)",
                "headcount",
                x_max=200,
                y_max=40,
                x_div=8,
                y_div=8,
            )
        ],
        questions=[
            QSpec(
                stem="Which startup has the highest annual revenue?",
                options=["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
                correct="Gamma",
                difficulty="easy",
                target_seconds=40,
                solution="Furthest right on the revenue axis is **Gamma**, at Rs 200 crore.",
            ),
            QSpec(
                stem="What is Delta's annual profit, in Rs crore?",
                value=35,
                difficulty="medium",
                target_seconds=70,
                solution=(
                    "Delta sits at revenue Rs 100 crore with a 35% margin:\n\n"
                    "$100 \\times \\dfrac{35}{100} = 35$\n\n"
                    "Profit **Rs 35 crore**."
                ),
            ),
            QSpec(
                stem="Which startup earns the highest absolute profit?",
                options=["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
                correct="Delta",
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Profit is revenue times margin, so neither axis alone decides it:\n\n"
                    + "\n".join(f"- {n}: {fmt(v)}" for n, v in profit.items())
                    + "\n\n**Delta** leads with Rs 35 crore. Gamma has twice Delta's revenue and still "
                    "earns less, because a bubble far to the right but low down is a high-revenue, "
                    "thin-margin business."
                ),
            ),
            QSpec(
                stem="For how many of the five startups does revenue per employee exceed Rs 25 lakh?",
                value=len(above_25),
                difficulty="hard",
                target_seconds=120,
                solution=(
                    "Revenue per employee uses the bubble's horizontal position and its area. "
                    "Revenue is in crore, and 1 crore = 100 lakh, so revenue per employee in lakh is "
                    "$\\dfrac{100 \\times \\text{revenue}}{\\text{headcount}}$:\n\n"
                    + "\n".join(f"- {n}: {fmt(round(v, 2))} lakh" for n, v in per_head.items())
                    + f"\n\n**{len(above_25)}** clear the bar. Alpha lands on exactly 25, and the question "
                    "says **exceed**, so Alpha is excluded — read the inequality carefully."
                ),
            ),
        ],
    )


def bubble_cities() -> SetPlan:
    points = [
        {"name": "City P", "x": 60, "y": 25, "size": 30},
        {"name": "City Q", "x": 80, "y": 20, "size": 12},
        {"name": "City R", "x": 50, "y": 15, "size": 60},
        {"name": "City S", "x": 70, "y": 30, "size": 20},
        {"name": "City T", "x": 40, "y": 10, "size": 45},
    ]
    literate_60_plus = [p for p in points if p["x"] >= 60]
    pop_60_plus = sum(p["size"] for p in literate_60_plus)
    assert pop_60_plus == 62
    pool = {p["name"]: p["size"] * p["y"] for p in points}
    assert pool == {"City P": 750, "City Q": 240, "City R": 900, "City S": 600, "City T": 450}
    bigger_than_p = [n for n, v in pool.items() if v > pool["City P"]]
    assert bigger_than_p == ["City R"]

    return SetPlan(
        micro_topic="dilr.di.bubble-charts",
        slug="cities",
        body=(
            "Five cities are plotted below. The horizontal axis is the literacy rate as a "
            "percentage, the vertical axis is average monthly household income in Rs thousand, "
            "and bubble area is proportional to population in lakh (printed inside the bubble).\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[
            bubble_asset(
                points,
                "Literacy rate (%)",
                "Average monthly income (Rs thousand)",
                "population in lakh",
                x_max=80,
                y_max=40,
                x_div=8,
                y_div=8,
            )
        ],
        questions=[
            QSpec(
                stem="Which city has the highest literacy rate?",
                options=["City P", "City Q", "City R", "City S", "City T"],
                correct="City Q",
                difficulty="easy",
                target_seconds=40,
                solution="Furthest right is **City Q**, at 80%.",
            ),
            QSpec(
                stem="Which city has the highest average monthly household income?",
                options=["City P", "City Q", "City R", "City S", "City T"],
                correct="City S",
                difficulty="easy",
                target_seconds=45,
                solution=(
                    "Highest on the vertical axis is **City S**, at Rs 30 thousand. City Q is furthest "
                    "right but not highest — the two axes are independent."
                ),
            ),
            QSpec(
                stem="What is the combined population, in lakh, of the cities with a literacy rate of 60% or more?",
                value=pop_60_plus,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Cities at or right of the 60% gridline are P (60), S (70) and Q (80). Their bubble "
                    "figures are the populations:\n\n"
                    "$30 + 20 + 12 = 62$\n\n"
                    "**62 lakh**. City P sits exactly on 60 and the condition is \"60% or more\", so it counts."
                ),
            ),
            QSpec(
                stem=(
                    "A city's total household income pool is its population times its average monthly "
                    "income. For how many cities is this pool larger than City P's?"
                ),
                value=len(bigger_than_p),
                difficulty="hard",
                target_seconds=120,
                solution=(
                    "The pool combines bubble area with vertical position, in units of "
                    "lakh $\\times$ Rs thousand:\n\n"
                    + "\n".join(f"- {n}: {fmt(v)}" for n, v in pool.items())
                    + f"\n\nCity P's pool is 750, and only **{len(bigger_than_p)}** city beats it — City R, "
                    "on 900. R has the lowest income of the three largest cities but by far the biggest "
                    "population, and the product is what the question asks about."
                ),
            ),
        ],
    )


def bubble_products() -> SetPlan:
    points = [
        {"name": "Product A", "x": 200, "y": 70, "size": 10},
        {"name": "Product B", "x": 300, "y": 60, "size": 25},
        {"name": "Product C", "x": 500, "y": 40, "size": 40},
        {"name": "Product D", "x": 600, "y": 30, "size": 15},
        {"name": "Product E", "x": 700, "y": 20, "size": 30},
    ]
    # Revenue in Rs lakh: price (Rs) x units (thousand) = Rs thousand x 1000, i.e. price*units/100 lakh.
    revenue = {p["name"]: p["x"] * p["y"] / 100 for p in points}
    assert revenue == {"Product A": 140, "Product B": 180, "Product C": 200, "Product D": 180, "Product E": 140}
    ratio = {p["name"]: revenue[p["name"]] / p["size"] for p in points}
    assert [round(ratio[p["name"]], 2) for p in points] == [14.0, 7.2, 5.0, 12.0, 4.67]
    efficient = [n for n, v in ratio.items() if v > 8]
    assert efficient == ["Product A", "Product D"]

    return SetPlan(
        micro_topic="dilr.di.bubble-charts",
        slug="products",
        body=(
            "Five products of a company are plotted below. The horizontal axis is unit price in "
            "rupees, the vertical axis is annual units sold in thousands, and bubble area is "
            "proportional to the advertising spend on that product in Rs lakh (printed inside the "
            "bubble).\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[
            bubble_asset(
                points,
                "Unit price (Rs)",
                "Units sold (thousand)",
                "advertising spend in Rs lakh",
                x_max=800,
                y_max=80,
                x_div=8,
                y_div=8,
            )
        ],
        questions=[
            QSpec(
                stem="How many units, in thousands, does Product C sell in a year?",
                value=40,
                difficulty="easy",
                target_seconds=40,
                solution="Product C sits on the 40 gridline of the units axis: **40 thousand units**.",
            ),
            QSpec(
                stem="What is Product B's annual revenue, in Rs lakh?",
                value=180,
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "Revenue is price times units. Product B: Rs 300 a unit, 60 thousand units.\n\n"
                    "$300 \\times 60{,}000 = 1{,}80{,}00{,}000$ rupees $=$ **Rs 180 lakh**."
                ),
            ),
            QSpec(
                stem="Which product earns the highest annual revenue?",
                options=["Product A", "Product B", "Product C", "Product D", "Product E"],
                correct="Product C",
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Revenue is the product of the two coordinates, so it is neither the cheapest nor "
                    "the best-selling product that wins:\n\n"
                    + "\n".join(f"- {n}: Rs {fmt(v)} lakh" for n, v in revenue.items())
                    + "\n\n**Product C** leads at Rs 200 lakh. Notice A and E tie on 140, and B and D tie "
                    "on 180 — pairs at opposite corners of the chart can generate identical revenue."
                ),
            ),
            QSpec(
                stem=(
                    "For how many products is annual revenue more than 8 times the advertising spend on "
                    "that product?"
                ),
                value=len(efficient),
                difficulty="hard",
                target_seconds=120,
                solution=(
                    "Both quantities are already in Rs lakh, so divide revenue by the figure inside "
                    "the bubble:\n\n"
                    + "\n".join(f"- {n}: $\\dfrac{{{fmt(revenue[n])}}}{{{p['size']}}} = {fmt(round(ratio[n], 2))}$" for n, p in zip(ratio, points))
                    + f"\n\n**{len(efficient)}** products clear 8 — A and D. Product C earns the most revenue "
                    "of any product and is the **least** efficient advertiser here, which is exactly why the "
                    "third dimension is on the chart."
                ),
            ),
        ],
    )


def bubble_schools() -> SetPlan:
    points = [
        {"name": "School V", "x": 15, "y": 80, "size": 450},
        {"name": "School W", "x": 20, "y": 90, "size": 900},
        {"name": "School X", "x": 25, "y": 60, "size": 1200},
        {"name": "School Y", "x": 30, "y": 70, "size": 1500},
        {"name": "School Z", "x": 35, "y": 50, "size": 700},
    ]
    teachers = {p["name"]: p["size"] / p["x"] for p in points}
    assert teachers == {"School V": 30, "School W": 45, "School X": 48, "School Y": 50, "School Z": 20}
    passed = {p["name"]: p["size"] * p["y"] / 100 for p in points}
    assert passed == {"School V": 360, "School W": 810, "School X": 720, "School Y": 1050, "School Z": 350}
    total_passed = sum(passed.values())
    assert total_passed == 3290

    return SetPlan(
        micro_topic="dilr.di.bubble-charts",
        slug="schools",
        body=(
            "Five schools are plotted below. The horizontal axis is the student-teacher ratio, the "
            "vertical axis is the board-exam pass percentage, and bubble area is proportional to "
            "total enrolment (printed inside the bubble).\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[
            bubble_asset(
                points,
                "Student-teacher ratio",
                "Pass percentage",
                "total enrolment",
                x_max=40,
                y_max=100,
                x_div=8,
                y_div=10,
            )
        ],
        questions=[
            QSpec(
                stem="Which school has the highest pass percentage?",
                options=["School V", "School W", "School X", "School Y", "School Z"],
                correct="School W",
                difficulty="easy",
                target_seconds=40,
                solution="Highest on the vertical axis is **School W**, at 90%.",
            ),
            QSpec(
                stem="How many teachers does School Y have?",
                value=50,
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "School Y enrols 1500 students at a student-teacher ratio of 30:\n\n"
                    "$\\dfrac{1500}{30} = 50$\n\n"
                    "**50 teachers**."
                ),
            ),
            QSpec(
                stem="How many students passed the board exam at School X?",
                value=720,
                difficulty="hard",
                target_seconds=90,
                solution=(
                    "School X enrols 1200 with a 60% pass rate:\n\n"
                    "$1200 \\times 0.60 = 720$\n\n"
                    "**720 students**."
                ),
            ),
            QSpec(
                stem="Across all five schools, how many students passed the board exam?",
                value=total_passed,
                difficulty="hard",
                target_seconds=140,
                solution=(
                    "Multiply each school's enrolment by its own pass rate — you cannot apply an average "
                    "rate to the combined enrolment, because the big schools have the lower rates:\n\n"
                    + "\n".join(f"- {n}: {fmt(v)}" for n, v in passed.items())
                    + f"\n\n$360 + 810 + 720 + 1050 + 350 = {fmt(total_passed)}$\n\n"
                    f"**{fmt(total_passed)} students**. Total enrolment is 4750, so the overall pass rate is "
                    "about 69.3% — below the simple average of the five percentages (70%), because "
                    "enrolment is weighted towards the weaker schools."
                ),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Combination (bars on the left axis, line on the right axis)
# ---------------------------------------------------------------------------


def combo_asset(
    categories: list[str],
    bars: dict[str, list[float]],
    lines: dict[str, list[float]],
    left_unit: str,
    right_unit: str,
) -> dict:
    return {
        "type": "chart",
        "spec": {
            "chartKind": "combo",
            "categories": categories,
            "bars": [{"name": n, "values": v} for n, v in bars.items()],
            "lines": [{"name": n, "values": v} for n, v in lines.items()],
            "leftUnit": left_unit,
            "rightUnit": right_unit,
        },
    }


def combo_revenue() -> SetPlan:
    years = ["2020", "2021", "2022", "2023", "2024"]
    revenue = [400, 520, 480, 650, 800]
    margin = [10, 12, 15, 12, 14]
    profit = [r * m / 100 for r, m in zip(revenue, margin)]
    assert profit == [40, 62.4, 72, 78, 112]
    best_year = years[profit.index(max(profit))]
    assert best_year == "2024"

    rose_and_fell = [
        years[i]
        for i in range(1, len(years))
        if revenue[i] > revenue[i - 1] and margin[i] < margin[i - 1]
    ]
    assert rose_and_fell == ["2023"]

    return SetPlan(
        micro_topic="dilr.di.combination-charts",
        slug="revenue-margin",
        body=(
            "The chart below shows a company's annual revenue as bars, read against the left axis "
            "in Rs crore, and its profit margin as a line, read against the right axis in "
            "percent.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[combo_asset(years, {"Revenue": revenue}, {"Profit margin": margin}, "Rs crore", "%")],
        questions=[
            QSpec(
                stem="What was the company's revenue in 2022, in Rs crore?",
                value=480,
                difficulty="easy",
                target_seconds=40,
                solution="Read the 2022 bar against the **left** axis: **Rs 480 crore**.",
            ),
            QSpec(
                stem="What was the company's profit in 2021, in Rs crore?",
                value=62.4,
                tolerance=0.01,
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "Profit needs both axes: the 2021 bar is Rs 520 crore and the 2021 point on the line "
                    "is 12%.\n\n"
                    "$520 \\times \\dfrac{12}{100} = 62.4$\n\n"
                    "Profit **Rs 62.4 crore**."
                ),
            ),
            QSpec(
                stem="In which year was the company's profit the highest?",
                options=years,
                correct=best_year,
                difficulty="medium",
                target_seconds=100,
                solution=(
                    "Profit is bar times line, year by year:\n\n"
                    + "\n".join(f"- {y}: $ {r} \\times {m}\\% = {fmt(p)}$" for y, r, m, p in zip(years, revenue, margin, profit))
                    + f"\n\nHighest in **{best_year}**. 2022 has the tallest point on the line and the "
                    "third-lowest profit — the line alone tells you nothing about profit."
                ),
            ),
            QSpec(
                stem=(
                    "In how many of the years shown did revenue rise over the previous year while the "
                    "profit margin fell?"
                ),
                options=["0", "1", "2", "3"],
                correct="1",
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Check each year-on-year move for the two conditions together:\n\n"
                    "- 2021: revenue up 400 to 520, margin up 10 to 12 — no\n"
                    "- 2022: revenue down 520 to 480 — no\n"
                    "- 2023: revenue up 480 to 650, margin down 15 to 12 — **yes**\n"
                    "- 2024: revenue up 650 to 800, margin up 12 to 14 — no\n\n"
                    "Exactly **1** year. 2023 is also the year with the second-highest profit, so "
                    "\"margin fell\" and \"the business did worse\" are not the same statement."
                ),
            ),
        ],
    )


def combo_airline() -> SetPlan:
    months = ["Jan", "Feb", "Mar", "Apr", "May"]
    passengers = [12, 15, 18, 14, 20]
    otp = [82, 78, 70, 85, 74]
    on_time = [p * o / 100 for p, o in zip(passengers, otp)]
    assert [round(v, 2) for v in on_time] == [9.84, 11.7, 12.6, 11.9, 14.8]
    best_month = months[on_time.index(max(on_time))]
    assert best_month == "May"
    delayed_total = sum(passengers) - sum(on_time)
    assert round(delayed_total, 2) == 18.16

    return SetPlan(
        micro_topic="dilr.di.combination-charts",
        slug="airline",
        body=(
            "The chart below shows an airline's monthly passengers carried as bars, read against "
            "the left axis in lakh, and its on-time performance as a line, read against the right "
            "axis in percent.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[
            combo_asset(months, {"Passengers": passengers}, {"On-time performance": otp}, "lakh", "%")
        ],
        questions=[
            QSpec(
                stem="How many passengers, in lakh, did the airline carry in March?",
                value=18,
                difficulty="easy",
                target_seconds=40,
                solution="Read the March bar against the **left** axis: **18 lakh passengers**.",
            ),
            QSpec(
                stem="How many passengers, in lakh, arrived on time in April?",
                value=11.9,
                tolerance=0.01,
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "April carried 14 lakh passengers with 85% on-time performance.\n\n"
                    "$14 \\times 0.85 = 11.9$\n\n"
                    "**11.9 lakh passengers**."
                ),
            ),
            QSpec(
                stem="In which month did the largest number of passengers arrive on time?",
                options=months,
                correct=best_month,
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Multiply each bar by its own point on the line:\n\n"
                    + "\n".join(f"- {m}: $ {p} \\times {o}\\% = {fmt(round(v, 2))}$ lakh" for m, p, o, v in zip(months, passengers, otp, on_time))
                    + f"\n\n**{best_month}**, at 14.8 lakh. April has the best on-time percentage and ranks "
                    "third on this measure, because the percentage is applied to a smaller base."
                ),
            ),
            QSpec(
                stem="Across the five months, how many passengers in total, in lakh, were delayed?",
                value=18.16,
                tolerance=0.01,
                difficulty="hard",
                target_seconds=140,
                solution=(
                    "Delayed share is $100\\% -$ on-time percentage, applied month by month:\n\n"
                    + "\n".join(f"- {m}: $ {p} \\times {fmt(100 - o)}\\% = {fmt(round(p * (100 - o) / 100, 2))}$" for m, p, o in zip(months, passengers, otp))
                    + "\n\n$2.16 + 3.3 + 5.4 + 2.1 + 5.2 = 18.16$\n\n"
                    "**18.16 lakh**. Faster route: total passengers 79 lakh minus total on-time 60.84 lakh "
                    "gives the same 18.16. Averaging the five percentages and applying that to 79 gives "
                    "18.09, which is wrong — the months carry different numbers of passengers."
                ),
            ),
        ],
    )


def combo_school() -> SetPlan:
    years = ["2021", "2022", "2023", "2024"]
    boys = [120, 140, 130, 160]
    girls = [100, 130, 150, 180]
    pass_pct = [75, 80, 75, 85]
    totals = [b + g for b, g in zip(boys, girls)]
    assert totals == [220, 270, 280, 340]
    passed = [t * p / 100 for t, p in zip(totals, pass_pct)]
    assert passed == [165, 216, 210, 289]

    up_but_worse = [
        years[i]
        for i in range(1, len(years))
        if totals[i] > totals[i - 1] and pass_pct[i] < pass_pct[i - 1]
    ]
    assert up_but_worse == ["2023"]

    return SetPlan(
        micro_topic="dilr.di.combination-charts",
        slug="school-results",
        body=(
            "The chart below shows the number of boys and girls appearing for a school's board "
            "exam as bars, read against the left axis, and the school's overall pass percentage as "
            "a line, read against the right axis.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[
            combo_asset(years, {"Boys": boys, "Girls": girls}, {"Pass percentage": pass_pct}, "students", "%")
        ],
        questions=[
            QSpec(
                stem="How many girls appeared for the exam in 2022?",
                value=130,
                difficulty="easy",
                target_seconds=40,
                solution="Read the Girls bar for 2022 against the **left** axis: **130**.",
            ),
            QSpec(
                stem="How many students in total appeared for the exam in 2023?",
                value=280,
                difficulty="medium",
                target_seconds=60,
                solution="$130 \\text{ boys} + 150 \\text{ girls} = 280$ students.",
            ),
            QSpec(
                stem="How many students passed the exam in 2024?",
                value=289,
                difficulty="hard",
                target_seconds=100,
                solution=(
                    "Total appearing in 2024 is $160 + 180 = 340$, and the line reads 85%.\n\n"
                    "$340 \\times 0.85 = 289$\n\n"
                    "**289 students**. The percentage is of the **combined** bar, not of either bar alone."
                ),
            ),
            QSpec(
                stem=(
                    "In which year did the total number of students appearing rise over the previous "
                    "year while the pass percentage fell?"
                ),
                options=years,
                correct="2023",
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Totals by year: "
                    + ", ".join(f"{y} {t}" for y, t in zip(years, totals))
                    + ". Pass percentages: "
                    + ", ".join(f"{y} {p}%" for y, p in zip(years, pass_pct))
                    + ".\n\n"
                    "- 2022: total up 220 to 270, but pass rate up 75 to 80 — no\n"
                    "- 2023: total up 270 to 280, pass rate down 80 to 75 — **yes**\n"
                    "- 2024: total up 280 to 340, pass rate up 75 to 85 — no\n\n"
                    "The answer is **2023**. In absolute terms 210 students passed in 2023 against 216 in "
                    "2022, so more people sat the exam and fewer passed it."
                ),
            ),
        ],
    )


def combo_retail() -> SetPlan:
    quarters = ["Q1", "Q2", "Q3", "Q4"]
    online = [60, 75, 90, 120]
    offline = [140, 130, 110, 100]
    discount = [10, 15, 20, 25]
    totals = [a + b for a, b in zip(online, offline)]
    assert totals == [200, 205, 200, 220]
    share = [o / t * 100 for o, t in zip(online, totals)]
    assert [round(s, 2) for s in share] == [30.0, 36.59, 45.0, 54.55]
    exactly_45 = quarters[[round(s, 6) for s in share].index(45.0)]
    assert exactly_45 == "Q3"

    first_over_half = next(q for q, o, f in zip(quarters, online, offline) if o > f / 2)
    assert first_over_half == "Q2"

    return SetPlan(
        micro_topic="dilr.di.combination-charts",
        slug="retail-channels",
        body=(
            "The chart below shows a retailer's quarterly online and offline sales as bars, read "
            "against the left axis in Rs lakh, and the average discount offered as a line, read "
            "against the right axis in percent.\n\n"
            "Study the chart and answer the questions that follow."
        ),
        assets=[
            combo_asset(
                quarters,
                {"Online": online, "Offline": offline},
                {"Average discount": discount},
                "Rs lakh",
                "%",
            )
        ],
        questions=[
            QSpec(
                stem="What were the offline sales in Q3, in Rs lakh?",
                value=110,
                difficulty="easy",
                target_seconds=40,
                solution="Read the Offline bar for Q3 against the **left** axis: **Rs 110 lakh**.",
            ),
            QSpec(
                stem="What were the retailer's total sales in Q4, in Rs lakh?",
                value=220,
                difficulty="easy",
                target_seconds=50,
                solution="$120 \\text{ online} + 100 \\text{ offline} = 220$, so **Rs 220 lakh**.",
            ),
            QSpec(
                stem="In which quarter did online sales first exceed half of offline sales?",
                options=quarters,
                correct=first_over_half,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Compare online against half of offline each quarter:\n\n"
                    + "\n".join(f"- {q}: online {o}, half of offline {fmt(f / 2)}" for q, o, f in zip(quarters, online, offline))
                    + f"\n\nThe first time online is larger is **{first_over_half}**."
                ),
            ),
            QSpec(
                stem="In which quarter did online sales account for exactly 45% of total sales?",
                options=quarters,
                correct=exactly_45,
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Share of online in the total, quarter by quarter:\n\n"
                    + "\n".join(f"- {q}: $\\dfrac{{{o}}}{{{t}}} = {fmt(round(s, 2))}\\%$" for q, o, t, s in zip(quarters, online, totals, share))
                    + f"\n\n**{exactly_45}**. Total sales barely move across the four quarters, so the whole "
                    "story is the mix shifting from offline to online — a shift the discount line tracks "
                    "but does not measure."
                ),
            ),
        ],
    )


PLANS = [
    radar_phones(),
    radar_candidates(),
    radar_retail(),
    radar_students(),
    bubble_startups(),
    bubble_cities(),
    bubble_products(),
    bubble_schools(),
    combo_revenue(),
    combo_airline(),
    combo_school(),
    combo_retail(),
]


if __name__ == "__main__":
    emit_all(PLANS)
