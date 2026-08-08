from __future__ import annotations

import random

import sympy as sp

from qagen.harness import ItemSpec, mcq_options_from_distractors
from qagen.syllabus_lookup import item_count, target_seconds

DIFF_CYCLE = ["easy", "easy", "medium", "medium", "medium", "hard", "hard", "very_hard"]


def _diffs(n: int) -> list[str]:
    return [DIFF_CYCLE[i % len(DIFF_CYCLE)] for i in range(n)]


def gen_linear_equations() -> list[ItemSpec]:
    mt = "qa.algebra.linear-equations"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    x, y = sp.symbols("x y")
    for i in range(n):
        x0, y0 = rng.randint(-10, 15), rng.randint(-10, 15)
        a1, b1 = rng.randint(1, 6), rng.randint(1, 6)
        a2, b2 = rng.randint(1, 6), rng.randint(-6, -1)
        c1, c2 = a1 * x0 + b1 * y0, a2 * x0 + b2 * y0

        def term(coef: int, var: str, lead: bool) -> str:
            sign = "" if lead and coef >= 0 else ("+ " if coef >= 0 else "- ")
            mag = abs(coef)
            mag_str = "" if mag == 1 else str(mag)
            return f"{sign}{mag_str}{var}"

        eq1 = f"{term(a1, 'x', True)} {term(b1, 'y', False)} = {c1}"
        eq2 = f"{term(a2, 'x', True)} {term(b2, 'y', False)} = {c2}"
        stem = f"Solve for $x + y$: $\\;{eq1}$ and $\\;{eq2}$."
        solution = (
            f"Solving the two equations simultaneously (elimination or "
            f"substitution) gives $x = {x0}$ and $y = {y0}$, so "
            f"$x + y = {x0 + y0}$."
        )

        def answer_fn(a1=a1, b1=b1, c1=c1, a2=a2, b2=b2, c2=c2):
            sol = sp.solve([sp.Eq(a1 * x + b1 * y, c1), sp.Eq(a2 * x + b2 * y, c2)], [x, y])
            return int(sol[x] + sol[y])

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=x0 + y0, target_seconds=target_seconds(mt),
            tags=["algebra:linear-equations"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_integer_solutions() -> list[ItemSpec]:
    mt = "qa.algebra.integer-solutions"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        total = rng.randint(8, 25)
        count = (total - 1) * (total - 2) // 2
        stem = (
            f"Find the number of ordered triples of positive integers $(x, y, z)$ "
            f"such that $x + y + z = {total}$."
        )
        solution = (
            f"This is a stars-and-bars count of positive-integer solutions: "
            f"$\\binom{{n-1}}{{k-1}} = \\binom{{{total}-1}}{{3-1}} = "
            f"\\binom{{{total - 1}}}{{2}} = {count}$."
        )

        def answer_fn(total=total):
            # Independent brute-force count.
            c = 0
            for xv in range(1, total - 1):
                for yv in range(1, total - xv):
                    zv = total - xv - yv
                    if zv >= 1:
                        c += 1
            return c

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=count, target_seconds=target_seconds(mt),
            tags=["algebra:integer-solutions"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_quadratic_equations() -> list[ItemSpec]:
    mt = "qa.algebra.quadratic-equations"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    x = sp.symbols("x")
    for i in range(n):
        r1 = rng.choice([v for v in range(-9, 10) if v != 0])
        r2 = rng.choice([v for v in range(-9, 10) if v != 0 and v != r1])
        b, c = -(r1 + r2), r1 * r2
        claimed = r1 ** 2 + r2 ** 2
        stem = (
            f"If the roots of $x^2 {'+' if b >= 0 else '-'} {abs(b)}x "
            f"{'+' if c >= 0 else '-'} {abs(c)} = 0$ are $\\alpha$ and $\\beta$, "
            f"find $\\alpha^2 + \\beta^2$."
        )
        solution = (
            f"$\\alpha + \\beta = {r1 + r2}$ and $\\alpha\\beta = {c}$ (sum/product "
            f"of roots). $\\alpha^2+\\beta^2 = (\\alpha+\\beta)^2 - 2\\alpha\\beta = "
            f"{r1 + r2}^2 - 2({c}) = {claimed}$."
        )

        def answer_fn(b=b, c=c):
            roots = sp.solve(sp.Eq(x ** 2 + b * x + c, 0), x)
            return int(sum(rt ** 2 for rt in roots))

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["algebra:quadratics"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_polynomials_remainder_factor() -> list[ItemSpec]:
    mt = "qa.algebra.polynomials-remainder-factor"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    x = sp.symbols("x")
    for i in range(n):
        a, b, c = rng.randint(1, 5), rng.randint(-8, 8), rng.randint(-10, 10)
        k = rng.choice([v for v in range(-4, 5) if v != 0])
        remainder = a * k ** 3 + b * k ** 2 + c * k + 1
        b_term = f"+ {b}x^2" if b >= 0 else f"- {abs(b)}x^2"
        c_term = f"+ {c}x" if c >= 0 else f"- {abs(c)}x"
        divisor = f"(x - {k})" if k >= 0 else f"(x + {abs(k)})"
        stem = (
            f"Find the remainder when $p(x) = {a}x^3 {b_term} {c_term} + 1$ is "
            f"divided by ${divisor}$."
        )
        solution = (
            f"By the Remainder Theorem, the remainder equals $p({k})$: "
            f"$p({k}) = {a}({k})^3 {b_term.replace('x^2', f'({k})^2')} "
            f"{c_term.replace('x', f'({k})')} + 1 = {remainder}$."
        )

        def answer_fn(a=a, b=b, c=c, k=k):
            poly = sp.Poly(a * x ** 3 + b * x ** 2 + c * x + 1, x)
            _, rem = sp.div(poly, sp.Poly(x - k, x))
            return int(rem.eval(0)) if rem.degree() >= 0 else 0

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=remainder, target_seconds=target_seconds(mt),
            tags=["algebra:remainder-theorem"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_inequalities_modulus() -> list[ItemSpec]:
    mt = "qa.algebra.inequalities-modulus"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        a = rng.randint(-10, 10)
        b = rng.randint(4, 12)
        count = sum(1 for xv in range(a - b - 2, a + b + 2) if abs(xv - a) < b)
        stem = f"How many integers $x$ satisfy $|x - {a}| < {b}$?"
        solution = (
            f"$|x-{a}| < {b}$ means ${a - b} < x < {a + b}$, an open interval of "
            f"length ${2 * b}$. Counting the integers strictly inside gives "
            f"${count}$."
        )

        def answer_fn(a=a, b=b):
            return sum(1 for xv in range(a - b - 2, a + b + 2) if abs(xv - a) < b)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=count, target_seconds=target_seconds(mt),
            tags=["algebra:inequalities-modulus"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_logarithms() -> list[ItemSpec]:
    mt = "qa.algebra.logarithms"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        base = rng.choice([2, 3, 5])
        power = rng.randint(2, 6)
        val = base ** power
        stem = f"Find the value of $\\log_{{{base}}} {val}$."
        solution = (
            f"$\\log_{{{base}}} {val} = \\log_{{{base}}} {base}^{{{power}}} = "
            f"{power}$, since ${base}^{{{power}}} = {val}$."
        )

        def answer_fn(base=base, val=val):
            import math
            return round(math.log(val, base))

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=power, target_seconds=target_seconds(mt),
            tags=["algebra:logarithms"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_surds_indices() -> list[ItemSpec]:
    mt = "qa.algebra.surds-indices"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        base = rng.choice([2, 3, 4, 5])
        e1, e2 = rng.randint(2, 6), rng.randint(2, 6)
        claimed = base ** (e1 + e2)
        stem = f"Simplify: $ {base}^{{{e1}}} \\times {base}^{{{e2}}} $."
        solution = (
            f"Using $a^m \\times a^n = a^{{m+n}}$: "
            f"${base}^{{{e1}}} \\times {base}^{{{e2}}} = {base}^{{{e1 + e2}}} = {claimed}$."
        )

        def answer_fn(base=base, e1=e1, e2=e2):
            return (base ** e1) * (base ** e2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["algebra:surds-indices"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_functions() -> list[ItemSpec]:
    mt = "qa.algebra.functions"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        a, b = rng.randint(2, 6), rng.randint(1, 10)
        k = rng.randint(-5, 5)
        claimed = a * (a * k + b) + b
        stem = (
            f"If $f(x) = {a}x + {b}$, find $f(f({k}))$."
        )
        inner = a * k + b
        solution = (
            f"$f({k}) = {a}({k}) + {b} = {inner}$. "
            f"$f(f({k})) = f({inner}) = {a}({inner}) + {b} = {claimed}$."
        )

        def answer_fn(a=a, b=b, k=k):
            def f(v):
                return a * v + b
            return f(f(k))

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["algebra:functions", "composite"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_maxima_minima() -> list[ItemSpec]:
    mt = "qa.algebra.maxima-minima"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    x = sp.symbols("x")
    for i in range(n):
        a = rng.randint(1, 4)
        b = rng.randint(-12, 12)
        c = rng.randint(-10, 10)
        vertex_x = sp.Rational(-b, 2 * a)
        min_val = a * vertex_x ** 2 + b * vertex_x + c
        min_val_f = round(float(min_val), 2)
        stem = (
            f"Find the minimum value of $f(x) = {a}x^2 {'+' if b >= 0 else '-'} "
            f"{abs(b)}x {'+' if c >= 0 else '-'} {abs(c)}$. (2 decimal places.)"
        )
        solution = (
            f"Since $a={a}>0$, the parabola opens upward and the minimum is at "
            f"$x = -b/2a = {float(vertex_x):.2f}$. Minimum value "
            f"$= c - b^2/(4a) = {min_val_f:.2f}$."
        )

        def answer_fn(a=a, b=b, c=c):
            expr = a * x ** 2 + b * x + c
            crit = sp.solve(sp.diff(expr, x), x)[0]
            return round(float(expr.subs(x, crit)), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=min_val_f, target_seconds=target_seconds(mt),
            tags=["algebra:maxima-minima"], format="tita", tita_tolerance=0.02,
        ))
    return specs


def gen_progressions() -> list[ItemSpec]:
    mt = "qa.algebra.progressions"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        a0 = rng.randint(1, 15)
        d = rng.randint(2, 9)
        terms = rng.randint(10, 30)
        claimed = terms * (2 * a0 + (terms - 1) * d) // 2 if (terms * (2 * a0 + (terms - 1) * d)) % 2 == 0 \
            else terms * (2 * a0 + (terms - 1) * d) / 2
        stem = (
            f"Find the sum of the first {terms} terms of an arithmetic progression "
            f"whose first term is {a0} and common difference is {d}."
        )
        solution = (
            f"$S_n = \\dfrac{{n}}{{2}}\\left[2a + (n-1)d\\right] = "
            f"\\dfrac{{{terms}}}{{2}}\\left[2({a0}) + ({terms}-1)({d})\\right] = {claimed}$."
        )

        def answer_fn(a0=a0, d=d, terms=terms):
            # Independent: sum the sequence directly.
            return sum(a0 + t * d for t in range(terms))

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["algebra:progressions", "ap"], format="tita", tita_tolerance=0,
        ))
    return specs


GENERATORS = [
    gen_linear_equations,
    gen_integer_solutions,
    gen_quadratic_equations,
    gen_polynomials_remainder_factor,
    gen_inequalities_modulus,
    gen_logarithms,
    gen_surds_indices,
    gen_functions,
    gen_maxima_minima,
    gen_progressions,
]
