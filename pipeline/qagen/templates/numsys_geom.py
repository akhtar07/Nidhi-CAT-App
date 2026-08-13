"""
Number-systems, geometry and modern-maths archetypes.

Same contract as `arith.py`. Number theory is especially prone to self-confirming
verification (both routes reducing to the same modular shortcut), so the `answer_fn`s
here lean on brute counting and repeated multiplication, which is the slowest but most
independent way to be sure.
"""

from __future__ import annotations

import math
import random
from itertools import combinations

from qagen.harness import ItemSpec
from qagen.syllabus_lookup import target_seconds

_HARDER = ("hard", "very_hard")


def _pick(rng, difficulty, easy, hard):
    return rng.choice(hard if difficulty in _HARDER else easy)


def _spec(mt, difficulty, stem, solution, answer_fn, claimed, tags, tol, alt=None) -> ItemSpec:
    return ItemSpec(
        microtopic_id=mt, difficulty=difficulty, stem=stem, solution=solution,
        alt_solution=alt, answer_fn=answer_fn, claimed_value=claimed,
        target_seconds=target_seconds(mt), tags=tags, format="tita", tita_tolerance=tol,
    )


# ---------------------------------------------------------------------------
# qa.numsys.remainders
# ---------------------------------------------------------------------------

MT_REM = "qa.numsys.remainders"


def t_rem_power(rng, difficulty) -> ItemSpec:
    base = _pick(rng, difficulty, [2, 3, 7], [11, 13, 17])
    exp = _pick(rng, difficulty, [10, 15, 20], [37, 53, 71])
    mod = _pick(rng, difficulty, [5, 7, 9], [11, 13, 23])
    claimed = pow(base, exp, mod)

    def answer_fn(base=base, exp=exp, mod=mod):
        # Multiply out one factor at a time, reducing as we go — no fast exponentiation,
        # no cyclicity shortcut, so it cannot echo the method the solution teaches.
        acc = 1
        for _ in range(exp):
            acc = (acc * base) % mod
        return acc

    stem = f"Find the remainder when ${base}^{{{exp}}}$ is divided by ${mod}$."
    cycle = []
    seen = {}
    value = 1
    for i in range(1, mod + 2):
        value = (value * base) % mod
        if value in seen:
            break
        seen[value] = i
        cycle.append(value)
    solution = (
        f"Powers of ${base}$ modulo ${mod}$ repeat in a cycle: the first few remainders are "
        f"{', '.join(str(c) for c in cycle[:6])}, and the pattern has length ${len(cycle)}$. "
        f"Since ${exp} \\bmod {len(cycle)} = {exp % len(cycle)}$, the remainder is ${claimed}$."
    )
    alt = "Find the cycle length first — after that the exponent only matters modulo that length."
    return _spec(MT_REM, difficulty, stem, solution, answer_fn, claimed, ["numsys:remainders", "cyclicity"], 0.01, alt)


def t_rem_product(rng, difficulty) -> ItemSpec:
    a = rng.randint(50, 999)
    b = rng.randint(50, 999)
    mod = _pick(rng, difficulty, [7, 9, 11], [13, 17, 19])
    claimed = (a * b) % mod

    def answer_fn(a=a, b=b, mod=mod):
        # Full product then a single division — never reduces the factors first.
        return (a * b) % mod

    stem = f"Find the remainder when ${a} \\times {b}$ is divided by ${mod}$."
    solution = (
        f"Reduce each factor first: ${a} \\equiv {a % mod}$ and ${b} \\equiv {b % mod} \\pmod{{{mod}}}$. "
        f"So the product is $\\equiv {a % mod} \\times {b % mod} = {(a % mod) * (b % mod)} \\equiv {claimed} \\pmod{{{mod}}}$."
    )
    alt = "Reducing before multiplying keeps the numbers small — the remainder is unaffected."
    return _spec(MT_REM, difficulty, stem, solution, answer_fn, claimed, ["numsys:remainders", "product"], 0.01, alt)


# ---------------------------------------------------------------------------
# qa.numsys.factors-count-sum-product
# ---------------------------------------------------------------------------

MT_FACT = "qa.numsys.factors-count-sum-product"


def _factorise(n: int) -> dict[int, int]:
    factors: dict[int, int] = {}
    d, remaining = 2, n
    while d * d <= remaining:
        while remaining % d == 0:
            factors[d] = factors.get(d, 0) + 1
            remaining //= d
        d += 1
    if remaining > 1:
        factors[remaining] = factors.get(remaining, 0) + 1
    return factors


def t_fact_count(rng, difficulty) -> ItemSpec:
    n = _pick(rng, difficulty, [72, 96, 120, 180], [360, 504, 720, 840])
    factors = _factorise(n)
    claimed = math.prod(e + 1 for e in factors.values())

    def answer_fn(n=n):
        # Trial-divide every candidate — the definition, not the exponent formula.
        return sum(1 for d in range(1, n + 1) if n % d == 0)

    fact_str = " \\times ".join(f"{p}^{{{e}}}" for p, e in sorted(factors.items()))
    calc = " \\times ".join(f"({e} + 1)" for e in factors.values())
    stem = f"How many factors does ${n}$ have?"
    solution = (
        f"Prime factorisation: ${n} = {fact_str}$. The number of factors is the product of "
        f"(each exponent $+ 1$): ${calc} = {claimed}$."
    )
    alt = "Every factor is built by choosing an exponent for each prime, independently — hence the product."
    return _spec(MT_FACT, difficulty, stem, solution, answer_fn, claimed, ["numsys:factors", "count"], 0.01, alt)


def t_fact_sum(rng, difficulty) -> ItemSpec:
    n = _pick(rng, difficulty, [24, 36, 60], [96, 120, 180])
    factors = _factorise(n)
    claimed = math.prod((p ** (e + 1) - 1) // (p - 1) for p, e in factors.items())

    def answer_fn(n=n):
        # Add up every divisor found by trial division.
        return sum(d for d in range(1, n + 1) if n % d == 0)

    fact_str = " \\times ".join(f"{p}^{{{e}}}" for p, e in sorted(factors.items()))
    stem = f"Find the sum of all factors of ${n}$."
    solution = (
        f"With ${n} = {fact_str}$, the sum of factors is the product of the geometric series for "
        f"each prime, $\\dfrac{{p^{{e+1}} - 1}}{{p - 1}}$, which gives ${claimed}$."
    )
    return _spec(MT_FACT, difficulty, stem, solution, answer_fn, claimed, ["numsys:factors", "sum"], 0.01)


def t_fact_even_count(rng, difficulty) -> ItemSpec:
    n = _pick(rng, difficulty, [48, 72, 120], [240, 360, 600])
    factors = _factorise(n)
    power_of_two = factors.get(2, 0)
    odd_part_divisors = math.prod(e + 1 for p, e in factors.items() if p != 2)
    claimed = power_of_two * odd_part_divisors

    def answer_fn(n=n):
        return sum(1 for d in range(1, n + 1) if n % d == 0 and d % 2 == 0)

    stem = f"How many even factors does ${n}$ have?"
    solution = (
        f"${n}$ has $2^{{{power_of_two}}}$ in its factorisation. An even factor must take at least one "
        f"factor of 2, leaving ${power_of_two}$ choices for the power of 2 and ${odd_part_divisors}$ "
        f"ways to build the rest, so ${power_of_two} \\times {odd_part_divisors} = {claimed}$."
    )
    return _spec(MT_FACT, difficulty, stem, solution, answer_fn, claimed, ["numsys:factors", "even-factors"], 0.01)


# ---------------------------------------------------------------------------
# qa.numsys.base-systems
# ---------------------------------------------------------------------------

MT_BASE = "qa.numsys.base-systems"


def t_base_to_decimal(rng, difficulty) -> ItemSpec:
    base = _pick(rng, difficulty, [2, 5, 8], [3, 7, 9])
    digits = [rng.randint(1, base - 1)] + [rng.randint(0, base - 1) for _ in range(_pick(rng, difficulty, [3], [4, 5]))]
    digit_str = "".join(str(d) for d in digits)
    claimed = sum(d * base ** (len(digits) - 1 - i) for i, d in enumerate(digits))

    def answer_fn(digits=digits, base=base):
        # Horner's scheme rather than summing explicit place values.
        acc = 0
        for d in digits:
            acc = acc * base + d
        return acc

    terms = " + ".join(
        f"{d} \\times {base}^{{{len(digits) - 1 - i}}}" for i, d in enumerate(digits) if d
    )
    stem = f"Convert the base-{base} number ${digit_str}_{{{base}}}$ to decimal."
    solution = f"Expand by place value: ${terms} = {claimed}$."
    return _spec(MT_BASE, difficulty, stem, solution, answer_fn, claimed, ["numsys:base", "to-decimal"], 0.01)


def t_base_from_decimal(rng, difficulty) -> ItemSpec:
    base = _pick(rng, difficulty, [2, 5, 8], [3, 7, 9])
    n = _pick(rng, difficulty, [50, 100, 200], [365, 512, 999])
    digits = []
    remaining = n
    while remaining:
        digits.append(remaining % base)
        remaining //= base
    digits.reverse()
    claimed = len(digits)

    def answer_fn(n=n, base=base):
        # Count digits by multiplying up until we exceed n.
        count, power = 0, 1
        while power <= n:
            power *= base
            count += 1
        return count

    stem = f"How many digits does the decimal number ${n}$ have when written in base ${base}$?"
    solution = (
        f"Repeatedly divide ${n}$ by ${base}$, recording remainders: the base-{base} form is "
        f"${''.join(str(d) for d in digits)}_{{{base}}}$, which has ${claimed}$ digits."
    )
    return _spec(MT_BASE, difficulty, stem, solution, answer_fn, claimed, ["numsys:base", "digit-count"], 0.01)


# ---------------------------------------------------------------------------
# qa.numsys.last-digit-trailing-zeroes
# ---------------------------------------------------------------------------

MT_LAST = "qa.numsys.last-digit-trailing-zeroes"


def t_last_digit_power(rng, difficulty) -> ItemSpec:
    base = _pick(rng, difficulty, [2, 3, 7, 8], [13, 17, 24, 39])
    exp = _pick(rng, difficulty, [15, 22, 40], [123, 251, 347])
    claimed = pow(base, exp, 10)

    def answer_fn(base=base, exp=exp):
        # One multiplication at a time, keeping only the units digit.
        digit = 1
        for _ in range(exp):
            digit = (digit * base) % 10
        return digit

    unit = base % 10
    cycle = []
    value = 1
    for _ in range(4):
        value = (value * unit) % 10
        cycle.append(value)
    stem = f"Find the last digit of ${base}^{{{exp}}}$."
    solution = (
        f"Only the units digit of the base matters, which is ${unit}$. Its powers cycle through "
        f"{', '.join(str(c) for c in cycle)} with period ${len(set(cycle))}$. "
        f"Locating ${exp}$ in that cycle gives a last digit of ${claimed}$."
    )
    return _spec(MT_LAST, difficulty, stem, solution, answer_fn, claimed, ["numsys:last-digit", "cyclicity"], 0.01)


def t_trailing_zeroes(rng, difficulty) -> ItemSpec:
    n = _pick(rng, difficulty, [25, 50, 100], [125, 200, 365])
    claimed = 0
    power = 5
    while power <= n:
        claimed += n // power
        power *= 5

    def answer_fn(n=n):
        # Count factors of 5 by walking every integer up to n.
        total = 0
        for i in range(1, n + 1):
            value = i
            while value % 5 == 0:
                total += 1
                value //= 5
        return total

    terms = []
    power = 5
    while power <= n:
        terms.append(f"\\left\\lfloor \\dfrac{{{n}}}{{{power}}} \\right\\rfloor = {n // power}")
        power *= 5
    stem = f"How many trailing zeroes does ${n}!$ have?"
    solution = (
        f"Each trailing zero needs a factor of 10, and 5s are scarcer than 2s, so count the 5s: "
        + " , ".join(terms)
        + f". Adding these gives ${claimed}$."
    )
    alt = "Higher powers of 5 must be counted again — 25 contributes two 5s, 125 contributes three."
    return _spec(MT_LAST, difficulty, stem, solution, answer_fn, claimed, ["numsys:trailing-zeroes"], 0.01, alt)


# ---------------------------------------------------------------------------
# qa.numsys.factorials-prime-power
# ---------------------------------------------------------------------------

MT_FACTORIAL = "qa.numsys.factorials-prime-power"


def t_highest_power_prime(rng, difficulty) -> ItemSpec:
    p = _pick(rng, difficulty, [2, 3, 5], [7, 11, 13])
    n = _pick(rng, difficulty, [20, 30, 50], [100, 150, 200])
    claimed = 0
    power = p
    while power <= n:
        claimed += n // power
        power *= p

    def answer_fn(n=n, p=p):
        # Count occurrences of p across every factor of n! individually.
        total = 0
        for i in range(1, n + 1):
            value = i
            while value % p == 0:
                total += 1
                value //= p
        return total

    terms = []
    power = p
    while power <= n:
        terms.append(f"\\left\\lfloor \\dfrac{{{n}}}{{{power}}} \\right\\rfloor = {n // power}")
        power *= p
    stem = f"Find the highest power of ${p}$ that divides ${n}!$."
    solution = (
        f"By Legendre's formula, add the floors of ${n}$ divided by successive powers of ${p}$: "
        + " , ".join(terms)
        + f". The total is ${claimed}$."
    )
    return _spec(MT_FACTORIAL, difficulty, stem, solution, answer_fn, claimed,
                 ["numsys:factorials", "legendre"], 0.01)


# ---------------------------------------------------------------------------
# qa.numsys.hcf-lcm
# ---------------------------------------------------------------------------

MT_HCF = "qa.numsys.hcf-lcm"


def t_hcf_lcm_pair(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [12, 18, 24, 36], [84, 126, 168, 210])
    b = _pick(rng, difficulty, [16, 30, 48, 60], [96, 144, 180, 252])
    claimed = a * b // math.gcd(a, b)

    def answer_fn(a=a, b=b):
        # Walk multiples of the larger number until one divides evenly by the smaller.
        big, small = max(a, b), min(a, b)
        multiple = big
        while multiple % small != 0:
            multiple += big
        return multiple

    stem = f"Find the LCM of ${a}$ and ${b}$."
    solution = (
        f"$\\text{{HCF}}({a}, {b}) = {math.gcd(a, b)}$, and since "
        f"$\\text{{HCF}} \\times \\text{{LCM}} = {a} \\times {b}$, the LCM is "
        f"$\\dfrac{{{a} \\times {b}}}{{{math.gcd(a, b)}}} = {claimed}$."
    )
    alt = "The product identity only works for two numbers — it does not extend to three."
    return _spec(MT_HCF, difficulty, stem, solution, answer_fn, claimed, ["numsys:hcf-lcm", "lcm"], 0.01, alt)


def t_hcf_bells(rng, difficulty) -> ItemSpec:
    intervals = [_pick(rng, difficulty, [4, 6, 8], [9, 14, 21]) for _ in range(3)]
    lcm = intervals[0]
    for i in intervals[1:]:
        lcm = lcm * i // math.gcd(lcm, i)
    claimed = lcm

    def answer_fn(intervals=intervals):
        # Step forward second by second until every bell coincides.
        t = 1
        while any(t % i for i in intervals):
            t += 1
        return t

    stem = (
        f"Three bells ring at intervals of {intervals[0]}, {intervals[1]} and {intervals[2]} seconds "
        f"respectively. If they ring together now, after how many seconds will they next ring together?"
    )
    solution = (
        f"They coincide at a common multiple of all three intervals, and the first such moment is the "
        f"LCM of ${intervals[0]}$, ${intervals[1]}$ and ${intervals[2]}$, which is ${claimed}$ seconds."
    )
    return _spec(MT_HCF, difficulty, stem, solution, answer_fn, claimed, ["numsys:hcf-lcm", "bells"], 0.01)


# ---------------------------------------------------------------------------
# qa.numsys.rational-irrational
# ---------------------------------------------------------------------------

MT_RAT = "qa.numsys.rational-irrational"


def t_recurring_to_fraction(rng, difficulty) -> ItemSpec:
    from fractions import Fraction

    digits = _pick(rng, difficulty, [2], [3])
    repeat = rng.randint(10 ** (digits - 1), 10 ** digits - 1)
    frac = Fraction(repeat, 10 ** digits - 1)
    claimed = frac.denominator

    def answer_fn(repeat=repeat, digits=digits):
        # Reduce the fraction by cancelling the gcd directly.
        denom = 10 ** digits - 1
        g = math.gcd(repeat, denom)
        return denom // g

    bar = str(repeat).zfill(digits)
    stem = (
        f"The recurring decimal $0.\\overline{{{bar}}}$ (the block ${bar}$ repeating) is written as a "
        f"fraction in lowest terms. What is its denominator?"
    )
    solution = (
        f"A block of ${digits}$ repeating digits sits over ${10 ** digits - 1}$: "
        f"$0.\\overline{{{bar}}} = \\dfrac{{{repeat}}}{{{10 ** digits - 1}}}$. Reducing by the HCF "
        f"${math.gcd(repeat, 10 ** digits - 1)}$ gives $\\dfrac{{{frac.numerator}}}{{{claimed}}}$."
    )
    alt = "One repeating digit sits over 9, two over 99, three over 999 — the pattern continues."
    return _spec(MT_RAT, difficulty, stem, solution, answer_fn, claimed, ["numsys:rational", "recurring"], 0.01, alt)


# ---------------------------------------------------------------------------
# qa.geometry.*
# ---------------------------------------------------------------------------

MT_TRI = "qa.geometry.triangles"
MT_CIRCLE = "qa.geometry.circles"
MT_POLY_G = "qa.geometry.quadrilaterals-polygons"
MT_COORD = "qa.geometry.coordinate-geometry"
MT_M2D = "qa.geometry.mensuration-2d"
MT_M3D = "qa.geometry.mensuration-3d"
MT_LINES = "qa.geometry.lines-angles"
MT_TRIG = "qa.geometry.trigonometry"


def t_tri_pythagoras(rng, difficulty) -> ItemSpec:
    triples = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (7, 24, 25), (9, 40, 41), (20, 21, 29)]
    a, b, c = rng.choice(triples)
    k = _pick(rng, difficulty, [1, 2], [3, 4, 5])
    a, b, c = a * k, b * k, c * k
    claimed = c

    def answer_fn(a=a, b=b):
        # Search the integer hypotenuse satisfying the relation.
        target = a * a + b * b
        for h in range(1, 10000):
            if h * h == target:
                return h
        return None

    stem = f"A right-angled triangle has legs of {a} cm and {b} cm. Find the length (in cm) of its hypotenuse."
    solution = f"$h^2 = {a}^2 + {b}^2 = {a * a} + {b * b} = {a * a + b * b}$, so $h = {claimed}$ cm."
    return _spec(MT_TRI, difficulty, stem, solution, answer_fn, claimed, ["geometry:triangles", "pythagoras"], 0.01)


def t_tri_area_heron(rng, difficulty) -> ItemSpec:
    triples = [(13, 14, 15), (6, 8, 10), (9, 12, 15), (5, 12, 13), (10, 17, 21)]
    a, b, c = rng.choice(triples)
    s = (a + b + c) / 2
    claimed = round(math.sqrt(s * (s - a) * (s - b) * (s - c)), 4)

    def answer_fn(a=a, b=b, c=c):
        # Place the triangle on coordinates and use the shoelace formula.
        x = (a * a + b * b - c * c) / (2 * a)
        y = math.sqrt(max(b * b - x * x, 0.0))
        # vertices (0,0), (a,0), (x,y)
        return round(abs(a * y) / 2, 4)

    stem = f"Find the area (in square cm) of a triangle whose sides are {a} cm, {b} cm and {c} cm. (Round to 4 decimal places.)"
    solution = (
        f"Semi-perimeter $s = \\dfrac{{{a} + {b} + {c}}}{{2}} = {s}$. By Heron's formula, area "
        f"$= \\sqrt{{s(s-a)(s-b)(s-c)}} = \\sqrt{{{s} \\times {s - a} \\times {s - b} \\times {s - c}}} = {claimed}$."
    )
    return _spec(MT_TRI, difficulty, stem, solution, answer_fn, claimed, ["geometry:triangles", "heron"], 0.001)


def t_circle_area_circumference(rng, difficulty) -> ItemSpec:
    r = _pick(rng, difficulty, [7, 14, 21], [10.5, 17.5, 12])
    claimed = round(math.pi * r * r, 4)

    def answer_fn(r=r):
        # Numerically integrate the disc in thin rings instead of using pi r^2.
        steps = 200000
        total = 0.0
        dr = r / steps
        for i in range(steps):
            radius = (i + 0.5) * dr
            total += 2 * math.pi * radius * dr
        return round(total, 4)

    stem = f"Find the area (in square cm) of a circle of radius {r} cm. Use $\\pi = 3.14159265$. (Round to 4 decimal places.)"
    solution = f"Area $= \\pi r^2 = \\pi \\times {r}^2 = {claimed}$ square cm."
    return _spec(MT_CIRCLE, difficulty, stem, solution, answer_fn, claimed, ["geometry:circles", "area"], 0.05)


def t_circle_sector(rng, difficulty) -> ItemSpec:
    r = _pick(rng, difficulty, [7, 14, 21], [10, 12, 18])
    angle = _pick(rng, difficulty, [60, 90, 120], [45, 135, 210])
    claimed = round(math.pi * r * r * angle / 360, 4)

    def answer_fn(r=r, angle=angle):
        # Build the sector as a fraction of a full disc measured in radians.
        radians = angle * math.pi / 180
        return round(0.5 * radians * r * r, 4)

    stem = (
        f"Find the area (in square cm) of a sector of a circle of radius {r} cm subtending an angle "
        f"of ${angle}$ degrees at the centre. Use $\\pi = 3.14159265$. (Round to 4 decimal places.)"
    )
    solution = (
        f"A sector is the fraction $\\dfrac{{{angle}}}{{360}}$ of the whole circle: "
        f"$\\dfrac{{{angle}}}{{360}} \\times \\pi \\times {r}^2 = {claimed}$ square cm."
    )
    return _spec(MT_CIRCLE, difficulty, stem, solution, answer_fn, claimed, ["geometry:circles", "sector"], 0.05)


def t_poly_interior_angle(rng, difficulty) -> ItemSpec:
    n = _pick(rng, difficulty, [5, 6, 8, 10], [9, 12, 15, 18])
    claimed = round((n - 2) * 180 / n, 4)

    def answer_fn(n=n):
        # Interior angle as the supplement of the exterior angle, which must total 360.
        exterior = 360 / n
        return round(180 - exterior, 4)

    stem = f"Find each interior angle (in degrees) of a regular polygon with {n} sides. (Round to 4 decimal places.)"
    solution = (
        f"The interior angles of an $n$-sided polygon sum to $(n-2) \\times 180 = {(n - 2) * 180}$ degrees. "
        f"Divided equally among ${n}$ angles that is ${claimed}$ degrees each."
    )
    alt = f"Or: each exterior angle is $\\dfrac{{360}}{{{n}}} = {360 / n}$ degrees, and the interior angle is its supplement."
    return _spec(MT_POLY_G, difficulty, stem, solution, answer_fn, claimed, ["geometry:polygons", "interior-angle"], 0.05, alt)


def t_poly_diagonals(rng, difficulty) -> ItemSpec:
    n = _pick(rng, difficulty, [6, 8, 10], [12, 15, 20])
    claimed = n * (n - 3) // 2

    def answer_fn(n=n):
        # Count vertex pairs and subtract the ones that are sides.
        pairs = len(list(combinations(range(n), 2)))
        return pairs - n

    stem = f"How many diagonals does a polygon with {n} sides have?"
    solution = (
        f"Each vertex joins to ${n - 3}$ non-adjacent vertices, and each diagonal gets counted twice: "
        f"$\\dfrac{{{n} \\times {n - 3}}}{{2}} = {claimed}$."
    )
    return _spec(MT_POLY_G, difficulty, stem, solution, answer_fn, claimed, ["geometry:polygons", "diagonals"], 0.01)


def t_coord_distance(rng, difficulty) -> ItemSpec:
    x1, y1 = rng.randint(-9, 9), rng.randint(-9, 9)
    dx, dy = rng.choice([(3, 4), (6, 8), (5, 12), (8, 15), (9, 12)])
    x2, y2 = x1 + dx, y1 + dy
    claimed = round(math.hypot(dx, dy), 4)

    def answer_fn(x1=x1, y1=y1, x2=x2, y2=y2):
        # Sum of squares expanded manually, then square-rooted.
        return round(((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5, 4)

    stem = f"Find the distance between the points $({x1}, {y1})$ and $({x2}, {y2})$. (Round to 4 decimal places.)"
    solution = (
        f"$d = \\sqrt{{({x2} - {x1})^2 + ({y2} - {y1})^2}} = \\sqrt{{{dx}^2 + {dy}^2}} = "
        f"\\sqrt{{{dx * dx + dy * dy}}} = {claimed}$."
    )
    return _spec(MT_COORD, difficulty, stem, solution, answer_fn, claimed, ["geometry:coordinate", "distance"], 0.001)


def t_coord_section(rng, difficulty) -> ItemSpec:
    x1, y1 = rng.randint(-9, 9), rng.randint(-9, 9)
    x2, y2 = rng.randint(-9, 9), rng.randint(-9, 9)
    m, n = _pick(rng, difficulty, [1, 2], [3, 4]), _pick(rng, difficulty, [1, 3], [2, 5])
    claimed = round((m * x2 + n * x1) / (m + n), 4)

    def answer_fn(x1=x1, x2=x2, m=m, n=n):
        # Walk the fraction m/(m+n) along the segment.
        t = m / (m + n)
        return round(x1 + t * (x2 - x1), 4)

    stem = (
        f"Find the $x$-coordinate of the point that divides the line segment joining $({x1}, {y1})$ "
        f"and $({x2}, {y2})$ internally in the ratio ${m} : {n}$. (Round to 4 decimal places.)"
    )
    solution = (
        f"By the section formula, $x = \\dfrac{{m x_2 + n x_1}}{{m + n}} = "
        f"\\dfrac{{{m}({x2}) + {n}({x1})}}{{{m} + {n}}} = {claimed}$."
    )
    return _spec(MT_COORD, difficulty, stem, solution, answer_fn, claimed, ["geometry:coordinate", "section-formula"], 0.001)


def t_m2d_rectangle_path(rng, difficulty) -> ItemSpec:
    length = _pick(rng, difficulty, [20, 30, 40], [35, 45, 55])
    width = _pick(rng, difficulty, [10, 15, 25], [18, 27, 33])
    path = _pick(rng, difficulty, [2, 3], [4, 5])
    outer = (length + 2 * path) * (width + 2 * path)
    claimed = outer - length * width

    def answer_fn(length=length, width=width, path=path):
        # Decompose the border into four rectangles plus four corner squares.
        sides = 2 * (length * path) + 2 * (width * path)
        corners = 4 * path * path
        return sides + corners

    stem = (
        f"A rectangular garden {length} m by {width} m is surrounded by a path {path} m wide running "
        f"all around it on the outside. Find the area (in square m) of the path."
    )
    solution = (
        f"The outer rectangle measures ${length + 2 * path}$ m by ${width + 2 * path}$ m, an area of "
        f"${outer}$ square m. Subtracting the garden's ${length * width}$ square m leaves ${claimed}$."
    )
    alt = "The path widens the plot on both sides, so each dimension grows by twice the width."
    return _spec(MT_M2D, difficulty, stem, solution, answer_fn, claimed, ["geometry:mensuration-2d", "path"], 0.01, alt)


def t_m3d_cylinder_volume(rng, difficulty) -> ItemSpec:
    r = _pick(rng, difficulty, [7, 14, 3.5], [10.5, 12, 21])
    h = _pick(rng, difficulty, [10, 20, 15], [18, 25, 32])
    claimed = round(math.pi * r * r * h, 4)

    def answer_fn(r=r, h=h):
        # Stack thin discs up the height instead of applying the volume formula once.
        steps = 100000
        dh = h / steps
        total = 0.0
        for _ in range(steps):
            total += math.pi * r * r * dh
        return round(total, 4)

    stem = (
        f"Find the volume (in cubic cm) of a cylinder of radius {r} cm and height {h} cm. "
        f"Use $\\pi = 3.14159265$. (Round to 4 decimal places.)"
    )
    solution = f"Volume $= \\pi r^2 h = \\pi \\times {r}^2 \\times {h} = {claimed}$ cubic cm."
    return _spec(MT_M3D, difficulty, stem, solution, answer_fn, claimed, ["geometry:mensuration-3d", "cylinder"], 0.05)


def t_m3d_cube_surface(rng, difficulty) -> ItemSpec:
    side = _pick(rng, difficulty, [4, 6, 10], [7, 9, 13])
    claimed = 6 * side * side

    def answer_fn(side=side):
        # Add the six faces one at a time.
        total = 0
        for _ in range(6):
            total += side * side
        return total

    stem = f"Find the total surface area (in square cm) of a cube of side {side} cm."
    solution = f"A cube has 6 identical square faces: $6 \\times {side}^2 = 6 \\times {side * side} = {claimed}$ square cm."
    return _spec(MT_M3D, difficulty, stem, solution, answer_fn, claimed, ["geometry:mensuration-3d", "cube"], 0.01)


def t_lines_angle_pair(rng, difficulty) -> ItemSpec:
    angle = _pick(rng, difficulty, [35, 50, 65], [43, 57, 72])
    claimed = 180 - angle

    def answer_fn(angle=angle):
        # A straight line is 180 degrees; take the complement of what remains.
        straight = 180
        return straight - angle

    stem = (
        f"Two parallel lines are cut by a transversal. If one of the interior angles on the same side "
        f"of the transversal is ${angle}$ degrees, find the other one (in degrees)."
    )
    solution = (
        f"Co-interior (allied) angles between parallel lines are supplementary, so the other angle is "
        f"$180 - {angle} = {claimed}$ degrees."
    )
    alt = "Corresponding and alternate angles are equal; only co-interior angles add to 180."
    return _spec(MT_LINES, difficulty, stem, solution, answer_fn, claimed, ["geometry:lines-angles", "parallel"], 0.01, alt)


def t_trig_height(rng, difficulty) -> ItemSpec:
    angle = _pick(rng, difficulty, [30, 45, 60], [30, 45, 60])
    distance = _pick(rng, difficulty, [30, 50, 100], [45, 75, 120])
    claimed = round(distance * math.tan(math.radians(angle)), 4)

    def answer_fn(angle=angle, distance=distance):
        # Build the ratio from sine and cosine separately rather than calling tan.
        radians = angle * math.pi / 180
        return round(distance * (math.sin(radians) / math.cos(radians)), 4)

    stem = (
        f"From a point {distance} m away from the foot of a tower, the angle of elevation of its top is "
        f"${angle}$ degrees. Find the height (in m) of the tower. (Round to 4 decimal places.)"
    )
    solution = (
        f"$\\tan({angle}^\\circ) = \\dfrac{{\\text{{height}}}}{{{distance}}}$, so the height is "
        f"${distance} \\times \\tan({angle}^\\circ) = {claimed}$ m."
    )
    return _spec(MT_TRIG, difficulty, stem, solution, answer_fn, claimed, ["geometry:trigonometry", "heights-distances"], 0.05)


# ---------------------------------------------------------------------------
# qa.modern.*
# ---------------------------------------------------------------------------

MT_PROB = "qa.modern.probability"
MT_VENN = "qa.modern.set-theory-venn"
MT_BINOM = "qa.modern.binomial-theorem"


def t_prob_dice_sum(rng, difficulty) -> ItemSpec:
    target = _pick(rng, difficulty, [7, 8, 6], [5, 9, 10])
    favourable = sum(1 for a in range(1, 7) for b in range(1, 7) if a + b == target)
    claimed = round(favourable / 36, 6)

    def answer_fn(target=target):
        # Enumerate the whole sample space and count.
        outcomes = [(a, b) for a in range(1, 7) for b in range(1, 7)]
        hits = [o for o in outcomes if sum(o) == target]
        return round(len(hits) / len(outcomes), 6)

    stem = (
        f"Two fair dice are thrown together. What is the probability that the sum of the numbers "
        f"shown is ${target}$? (Round to 6 decimal places.)"
    )
    solution = (
        f"There are $6 \\times 6 = 36$ equally likely outcomes. The pairs summing to ${target}$ number "
        f"${favourable}$, so the probability is $\\dfrac{{{favourable}}}{{36}} = {claimed}$."
    )
    return _spec(MT_PROB, difficulty, stem, solution, answer_fn, claimed, ["modern:probability", "dice"], 0.00001)


def t_prob_balls(rng, difficulty) -> ItemSpec:
    red = _pick(rng, difficulty, [3, 4, 5], [6, 7, 9])
    blue = _pick(rng, difficulty, [2, 5, 6], [4, 8, 11])
    total = red + blue
    claimed = round(math.comb(red, 2) / math.comb(total, 2), 6)

    def answer_fn(red=red, blue=blue):
        # Enumerate every unordered pair from a labelled bag.
        balls = ["R"] * red + ["B"] * blue
        pairs = list(combinations(range(len(balls)), 2))
        hits = [p for p in pairs if balls[p[0]] == "R" and balls[p[1]] == "R"]
        return round(len(hits) / len(pairs), 6)

    stem = (
        f"A bag contains {red} red balls and {blue} blue balls. Two balls are drawn at random without "
        f"replacement. What is the probability that both are red? (Round to 6 decimal places.)"
    )
    solution = (
        f"Choose 2 from the {red} red balls out of 2 from all {total}: "
        f"$\\dfrac{{\\binom{{{red}}}{{2}}}}{{\\binom{{{total}}}{{2}}}} = "
        f"\\dfrac{{{math.comb(red, 2)}}}{{{math.comb(total, 2)}}} = {claimed}$."
    )
    return _spec(MT_PROB, difficulty, stem, solution, answer_fn, claimed, ["modern:probability", "combinations"], 0.00001)


def t_venn_two_sets(rng, difficulty) -> ItemSpec:
    total = _pick(rng, difficulty, [100, 120, 150], [175, 220, 260])
    a = int(total * _pick(rng, difficulty, [0.6, 0.5], [0.55, 0.65]))
    b = int(total * _pick(rng, difficulty, [0.4, 0.5], [0.45, 0.35]))
    neither = _pick(rng, difficulty, [10, 15, 20], [12, 23, 31])
    both = a + b - (total - neither)
    claimed = both

    def answer_fn(total=total, a=a, b=b, neither=neither):
        # Build the four disjoint regions and solve for the overlap by subtraction.
        at_least_one = total - neither
        only_a_plus_only_b_plus_both = at_least_one
        overlap = a + b - only_a_plus_only_b_plus_both
        return overlap

    stem = (
        f"In a survey of {total} people, {a} like tea and {b} like coffee, while {neither} like neither. "
        f"How many like both tea and coffee?"
    )
    solution = (
        f"People liking at least one drink: ${total} - {neither} = {total - neither}$. By inclusion-exclusion, "
        f"$|A \\cup B| = |A| + |B| - |A \\cap B|$, so $|A \\cap B| = {a} + {b} - {total - neither} = {claimed}$."
    )
    return _spec(MT_VENN, difficulty, stem, solution, answer_fn, claimed, ["modern:venn", "two-sets"], 0.01)


def t_binom_coefficient(rng, difficulty) -> ItemSpec:
    n = _pick(rng, difficulty, [5, 6, 7], [8, 9, 10])
    r = rng.randint(2, n - 2)
    claimed = math.comb(n, r)

    def answer_fn(n=n, r=r):
        # Build Pascal's triangle row by row.
        row = [1]
        for _ in range(n):
            row = [1] + [row[i] + row[i + 1] for i in range(len(row) - 1)] + [1]
        return row[r]

    stem = f"Find the coefficient of $x^{{{r}}}$ in the expansion of $(1 + x)^{{{n}}}$."
    solution = (
        f"The coefficient of $x^r$ in $(1+x)^n$ is $\\binom{{n}}{{r}}$: "
        f"$\\binom{{{n}}}{{{r}}} = \\dfrac{{{n}!}}{{{r}!({n}-{r})!}} = {claimed}$."
    )
    return _spec(MT_BINOM, difficulty, stem, solution, answer_fn, claimed, ["modern:binomial", "coefficient"], 0.01)


TEMPLATES = {
    MT_REM: [t_rem_power, t_rem_product],
    MT_FACT: [t_fact_count, t_fact_sum, t_fact_even_count],
    MT_BASE: [t_base_to_decimal, t_base_from_decimal],
    MT_LAST: [t_last_digit_power, t_trailing_zeroes],
    MT_FACTORIAL: [t_highest_power_prime],
    MT_HCF: [t_hcf_lcm_pair, t_hcf_bells],
    MT_RAT: [t_recurring_to_fraction],
    MT_TRI: [t_tri_pythagoras, t_tri_area_heron],
    MT_CIRCLE: [t_circle_area_circumference, t_circle_sector],
    MT_POLY_G: [t_poly_interior_angle, t_poly_diagonals],
    MT_COORD: [t_coord_distance, t_coord_section],
    MT_M2D: [t_m2d_rectangle_path],
    MT_M3D: [t_m3d_cylinder_volume, t_m3d_cube_surface],
    MT_LINES: [t_lines_angle_pair],
    MT_TRIG: [t_trig_height],
    MT_PROB: [t_prob_dice_sum, t_prob_balls],
    MT_VENN: [t_venn_two_sets],
    MT_BINOM: [t_binom_coefficient],
}
