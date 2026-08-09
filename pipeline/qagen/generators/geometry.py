from __future__ import annotations

import math
import random

import sympy as sp

from qagen.harness import ItemSpec
from qagen.syllabus_lookup import item_count, target_seconds

DIFF_CYCLE = ["easy", "easy", "medium", "medium", "medium", "hard", "hard", "very_hard"]


def _diffs(n: int) -> list[str]:
    return [DIFF_CYCLE[i % len(DIFF_CYCLE)] for i in range(n)]


def gen_lines_angles() -> list[ItemSpec]:
    mt = "qa.geometry.lines-angles"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        theta = rng.randint(20, 160)
        claimed = 180 - theta
        stem = (
            f"Two parallel lines are cut by a transversal. One of the angles formed "
            f"is {theta}\u00b0. Find the co-interior (same-side interior) angle to it, "
            f"in degrees."
        )
        solution = (
            f"Co-interior angles are supplementary (they sum to 180\u00b0). "
            f"So the required angle $= 180 - {theta} = {claimed}$\u00b0."
        )

        def answer_fn(theta=theta):
            return 180 - theta

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["geometry:lines-angles"], format="tita", tita_tolerance=0,
        ))
    return specs


PYTHAGOREAN_TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (20, 21, 29), (9, 40, 41)]


def gen_triangles() -> list[ItemSpec]:
    mt = "qa.geometry.triangles"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        a0, b0, c0 = rng.choice(PYTHAGOREAN_TRIPLES)
        k = rng.randint(1, 4)
        a, b, c = a0 * k, b0 * k, c0 * k
        claimed = round(0.5 * a * b, 2)
        stem = (
            f"A right-angled triangle has legs of length {a} cm and {b} cm. "
            f"Find its area in cm\u00b2."
        )
        solution = (
            f"For a right triangle, the two legs act as base and height: "
            f"Area $= \\dfrac{{1}}{{2}} \\times {a} \\times {b} = {claimed:.2f}$ cm\u00b2. "
            f"(The hypotenuse works out to ${c}$ cm, a Pythagorean triple.)"
        )

        def answer_fn(a=a, b=b, c=c):
            # Independent check via Heron's formula on all three sides.
            s = (a + b + c) / 2
            return round(math.sqrt(s * (s - a) * (s - b) * (s - c)), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["geometry:triangles", "right-triangle"], format="tita", tita_tolerance=0.05,
        ))
    return specs


def gen_quadrilaterals_polygons() -> list[ItemSpec]:
    mt = "qa.geometry.quadrilaterals-polygons"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        sides = rng.randint(5, 15)
        claimed = (sides - 2) * 180
        stem = (
            f"Find the sum of the interior angles of a convex polygon with "
            f"{sides} sides, in degrees."
        )
        solution = (
            f"Sum of interior angles $= (n-2) \\times 180 = "
            f"({sides}-2) \\times 180 = {claimed}$\u00b0."
        )

        def answer_fn(sides=sides):
            # Independent derivation: exterior angles always sum to 360.
            return sides * 180 - 360

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["geometry:polygons"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_circles() -> list[ItemSpec]:
    mt = "qa.geometry.circles"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        r = rng.randint(3, 15)
        extra = rng.randint(2, 10)
        d = r + extra  # distance from external point to centre, > r
        tangent_len_sq = d ** 2 - r ** 2
        claimed = round(math.sqrt(tangent_len_sq), 2)
        stem = (
            f"A point P is {d} cm from the centre of a circle of radius {r} cm. "
            f"Find the length of the tangent from P to the circle (2 decimal places)."
        )
        solution = (
            f"The tangent, radius, and line from P to the centre form a right "
            f"triangle (tangent \u22a5 radius at the point of contact). "
            f"Tangent length $= \\sqrt{{d^2 - r^2}} = \\sqrt{{{d}^2 - {r}^2}} = "
            f"\\sqrt{{{tangent_len_sq}}} = {claimed:.2f}$ cm."
        )

        def answer_fn(d=d, r=r):
            x = sp.sqrt(d ** 2 - r ** 2)
            return round(float(x), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["geometry:circles", "tangent"], format="tita", tita_tolerance=0.02,
        ))
    return specs


def gen_coordinate_geometry() -> list[ItemSpec]:
    mt = "qa.geometry.coordinate-geometry"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        a0, b0, c0 = rng.choice(PYTHAGOREAN_TRIPLES)
        x1, y1 = rng.randint(-10, 10), rng.randint(-10, 10)
        sign_x, sign_y = rng.choice([1, -1]), rng.choice([1, -1])
        x2, y2 = x1 + sign_x * a0, y1 + sign_y * b0
        claimed = c0
        stem = (
            f"Find the distance between the points $({x1}, {y1})$ and "
            f"$({x2}, {y2})$."
        )
        solution = (
            f"Distance $= \\sqrt{{(x_2-x_1)^2 + (y_2-y_1)^2}} = "
            f"\\sqrt{{({x2 - x1})^2 + ({y2 - y1})^2}} = \\sqrt{{{(x2 - x1) ** 2 + (y2 - y1) ** 2}}} "
            f"= {claimed}$."
        )

        def answer_fn(x1=x1, y1=y1, x2=x2, y2=y2):
            p1, p2 = sp.Point(x1, y1), sp.Point(x2, y2)
            return round(float(p1.distance(p2)), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=float(claimed), target_seconds=target_seconds(mt),
            tags=["geometry:coordinate", "distance"], format="tita", tita_tolerance=0.02,
        ))
    return specs


def gen_trigonometry() -> list[ItemSpec]:
    mt = "qa.geometry.trigonometry"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    angle_tan = {30: sp.Rational(1, 1) / sp.sqrt(3), 45: sp.Integer(1), 60: sp.sqrt(3)}
    # Widened dist choices from {10,20,30,40,50} (only 15 angle x dist combos
    # total, too narrow for 10 unique draws) to a much larger pool. Angle
    # stays restricted to {30,45,60} deliberately — those are the only
    # standard angles with exact, unambiguous tan values; adding others
    # (e.g. 37/53 degree approximations) risks the "degenerate or ambiguous
    # math" the task asked us to avoid forcing. Even at 3 x 19 = 57 combos,
    # independent rng.choice() draws collide often enough (birthday problem,
    # ~55% chance of >=1 collision in 10 draws) to knock out the hard/
    # very_hard tail of DIFF_CYCLE, which is exactly the failure mode we're
    # trying to fix — so sample the (angle, dist) pairs without replacement
    # instead of drawing each field independently.
    all_combos = [(a, d) for a in (30, 45, 60) for d in range(10, 105, 5)]
    rng.shuffle(all_combos)
    combos = all_combos[:n]
    for i in range(n):
        angle, dist = combos[i]
        height = float(dist * angle_tan[angle])
        claimed = round(height, 2)
        stem = (
            f"A pole stands vertically on the ground. From a point {dist} m from "
            f"its base, the angle of elevation of the top of the pole is {angle}\u00b0. "
            f"Find the height of the pole (2 decimal places)."
        )
        solution = (
            f"$\\text{{height}} = \\text{{distance}} \\times \\tan({angle}\u00b0) = "
            f"{dist} \\times \\tan({angle}\u00b0) = {claimed:.2f}$ m."
        )

        def answer_fn(dist=dist, angle=angle):
            # Independent: numeric tan via math, not the exact sympy value used to build claimed_value.
            return round(dist * math.tan(math.radians(angle)), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["geometry:trigonometry", "heights-distances"], format="tita",
            tita_tolerance=0.05,
        ))
    return specs


def gen_mensuration_2d() -> list[ItemSpec]:
    mt = "qa.geometry.mensuration-2d"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        a = rng.randint(6, 20)  # longer parallel side
        b = rng.randint(3, a - 2)  # shorter parallel side
        h = rng.randint(4, 15)
        claimed = round(0.5 * (a + b) * h, 2)
        stem = (
            f"A trapezium has parallel sides of length {a} cm and {b} cm, and the "
            f"perpendicular distance between them is {h} cm. Find its area in cm\u00b2."
        )
        solution = (
            f"Area of trapezium $= \\dfrac{{1}}{{2}}(a+b)h = "
            f"\\dfrac{{1}}{{2}}({a}+{b})({h}) = {claimed:.2f}$ cm\u00b2."
        )

        def answer_fn(a=a, b=b, h=h):
            # Independent: split into a rectangle (width = shorter side) and
            # a triangle (the remaining width), areas summed.
            rect_area = b * h
            tri_area = 0.5 * (a - b) * h
            return round(rect_area + tri_area, 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["geometry:mensuration-2d", "trapezium"], format="tita", tita_tolerance=0.02,
        ))
    return specs


def gen_mensuration_3d() -> list[ItemSpec]:
    mt = "qa.geometry.mensuration-3d"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        r = rng.randint(2, 10)
        h = rng.randint(5, 20)
        claimed = round(math.pi * r ** 2 * h, 2)
        stem = (
            f"Find the volume of a right circular cylinder with radius {r} cm and "
            f"height {h} cm. Use $\\pi = 3.14159$ and round to 2 decimal places."
        )
        solution = (
            f"Volume $= \\pi r^2 h = \\pi \\times {r}^2 \\times {h} = {claimed:.2f}$ cm\u00b3."
        )

        def answer_fn(r=r, h=h):
            # Independent pi source (sympy's exact pi, evaluated numerically).
            return round(float(sp.pi * r ** 2 * h), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["geometry:mensuration-3d", "cylinder"], format="tita", tita_tolerance=0.5,
        ))
    return specs


GENERATORS = [
    gen_lines_angles,
    gen_triangles,
    gen_quadrilaterals_polygons,
    gen_circles,
    gen_coordinate_geometry,
    gen_trigonometry,
    gen_mensuration_2d,
    gen_mensuration_3d,
]
