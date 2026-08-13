"""Series and sequences archetypes (qa.modern.series-sequences-hybrids)."""

from __future__ import annotations

import random

from qagen.harness import ItemSpec
from qagen.syllabus_lookup import target_seconds

MT = "qa.modern.series-sequences-hybrids"
_HARDER = ("hard", "very_hard")


def _pick(rng, difficulty, easy, hard):
    return rng.choice(hard if difficulty in _HARDER else easy)


def _spec(difficulty, stem, solution, answer_fn, claimed, tags, tol, alt=None) -> ItemSpec:
    return ItemSpec(
        microtopic_id=MT, difficulty=difficulty, stem=stem, solution=solution,
        alt_solution=alt, answer_fn=answer_fn, claimed_value=claimed,
        target_seconds=target_seconds(MT), tags=tags, format="tita", tita_tolerance=tol,
    )


def t_ap_nth_term(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [3, 5, 7, 10], [4, 11, 13, 17])
    d = _pick(rng, difficulty, [2, 3, 4, 5], [6, 7, 9, 11])
    n = _pick(rng, difficulty, [10, 12, 15], [23, 31, 40])
    claimed = a + (n - 1) * d

    def answer_fn(a=a, d=d, n=n):
        # Walk the sequence forward rather than using a + (n-1)d.
        term = a
        for _ in range(n - 1):
            term += d
        return term

    stem = f"Find the {n}th term of the arithmetic progression {a}, {a + d}, {a + 2 * d}, ..."
    solution = (
        f"The first term is ${a}$ and the common difference is ${d}$. "
        f"The $n$th term is $a + (n-1)d = {a} + {n - 1} \\times {d} = {claimed}$."
    )
    return _spec(difficulty, stem, solution, answer_fn, claimed,
                 ["modern:series", "ap-term"], 0.01)


def t_ap_sum(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [2, 5, 8], [6, 9, 13])
    d = _pick(rng, difficulty, [3, 4, 5], [7, 8, 11])
    n = _pick(rng, difficulty, [10, 15, 20], [25, 32, 45])
    last = a + (n - 1) * d
    claimed = n * (a + last) // 2

    def answer_fn(a=a, d=d, n=n):
        # Add the terms one at a time.
        total, term = 0, a
        for _ in range(n):
            total += term
            term += d
        return total

    stem = f"Find the sum of the first {n} terms of the arithmetic progression {a}, {a + d}, {a + 2 * d}, ..."
    solution = (
        f"The {n}th term is ${a} + {n - 1} \\times {d} = {last}$. "
        f"Sum $= \\dfrac{{n}}{{2}}(\\text{{first}} + \\text{{last}}) = \\dfrac{{{n}}}{{2}}({a} + {last}) = {claimed}$."
    )
    alt = (
        f"Pairing works because the terms are evenly spaced: the first pairs with the last, the second "
        f"with the second-last, and every pair totals ${a + last}$."
    )
    return _spec(difficulty, stem, solution, answer_fn, claimed,
                 ["modern:series", "ap-sum"], 0.01, alt)


def t_gp_nth_term(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [2, 3, 5], [4, 6, 7])
    r = _pick(rng, difficulty, [2, 3], [2, 3, 4])
    n = _pick(rng, difficulty, [6, 7, 8], [9, 10, 11])
    claimed = a * r ** (n - 1)

    def answer_fn(a=a, r=r, n=n):
        # Repeated multiplication instead of exponentiation.
        term = a
        for _ in range(n - 1):
            term *= r
        return term

    stem = f"Find the {n}th term of the geometric progression {a}, {a * r}, {a * r * r}, ..."
    solution = (
        f"The first term is ${a}$ and the common ratio is ${r}$. "
        f"The $n$th term is $ar^{{n-1}} = {a} \\times {r}^{{{n - 1}}} = {claimed}$."
    )
    return _spec(difficulty, stem, solution, answer_fn, claimed,
                 ["modern:series", "gp-term"], 0.01)


def t_gp_sum(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [2, 3, 5], [4, 6, 7])
    r = _pick(rng, difficulty, [2, 3], [3, 4])
    n = _pick(rng, difficulty, [5, 6], [7, 8])
    claimed = a * (r ** n - 1) // (r - 1)

    def answer_fn(a=a, r=r, n=n):
        total, term = 0, a
        for _ in range(n):
            total += term
            term *= r
        return total

    stem = f"Find the sum of the first {n} terms of the geometric progression {a}, {a * r}, {a * r * r}, ..."
    solution = (
        f"Sum $= \\dfrac{{a(r^n - 1)}}{{r - 1}} = \\dfrac{{{a}({r}^{{{n}}} - 1)}}{{{r} - 1}} = {claimed}$."
    )
    return _spec(difficulty, stem, solution, answer_fn, claimed,
                 ["modern:series", "gp-sum"], 0.01)


def t_gp_infinite(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [4, 6, 8, 12], [5, 9, 15, 21])
    denom = _pick(rng, difficulty, [2, 3, 4], [5, 6, 8])
    claimed = round(a / (1 - 1 / denom), 4)

    def answer_fn(a=a, denom=denom):
        # Add many terms until the tail is negligible, instead of using a/(1-r).
        total, term = 0.0, float(a)
        for _ in range(400):
            total += term
            term /= denom
        return round(total, 4)

    stem = (
        f"Find the sum to infinity of the geometric progression "
        f"${a}, \\dfrac{{{a}}}{{{denom}}}, \\dfrac{{{a}}}{{{denom ** 2}}}, \\ldots$ "
        f"(Round to 4 decimal places.)"
    )
    solution = (
        f"The common ratio is $\\dfrac{{1}}{{{denom}}}$, whose absolute value is below 1, so the series "
        f"converges. Sum $= \\dfrac{{a}}{{1 - r}} = \\dfrac{{{a}}}{{1 - 1/{denom}}} = {claimed}$."
    )
    alt = "The formula only applies when the ratio is strictly between -1 and 1; otherwise the terms never die away."
    return _spec(difficulty, stem, solution, answer_fn, claimed,
                 ["modern:series", "infinite-gp"], 0.001, alt)


def t_pattern_next(rng, difficulty) -> ItemSpec:
    kind = _pick(rng, difficulty, ["oblong", "squares"], ["triangular", "cubes"])
    start = _pick(rng, difficulty, [1, 2], [2, 3])
    formulas = {
        "oblong": lambda k: k * (k + 1),
        "squares": lambda k: k * k,
        "triangular": lambda k: k * (k + 1) // 2,
        "cubes": lambda k: k ** 3,
    }
    names = {
        "oblong": "each term is $n(n+1)$",
        "squares": "each term is $n^2$",
        "triangular": "each term is the sum of the first $n$ whole numbers",
        "cubes": "each term is $n^3$",
    }
    f = formulas[kind]
    shown = [f(start + i) for i in range(5)]
    claimed = f(start + 5)

    def answer_fn(shown=shown, kind=kind, start=start, f=f):
        # Rebuild the sequence from its defining rule and read off the next value,
        # after confirming the rule reproduces every term shown.
        for i, value in enumerate(shown):
            if f(start + i) != value:
                return None
        return f(start + len(shown))

    stem = "Find the next term in the series: " + ", ".join(str(x) for x in shown) + ", ..."
    diffs = [shown[i + 1] - shown[i] for i in range(len(shown) - 1)]
    solution = (
        f"The differences between consecutive terms are {', '.join(str(d) for d in diffs)}, which are "
        f"themselves patterned rather than constant — so this is not an arithmetic progression. "
        f"In fact {names[kind]}, and continuing that rule gives **{claimed}**."
    )
    alt = "When a series is neither arithmetic nor geometric, writing out the differences is the first thing to try."
    return _spec(difficulty, stem, solution, answer_fn, claimed,
                 ["modern:series", "pattern"], 0.01, alt)


def t_ap_missing_term(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [4, 7, 10], [6, 13, 19])
    d = _pick(rng, difficulty, [3, 5, 6], [7, 9, 12])
    n = _pick(rng, difficulty, [8, 10], [12, 15])
    total = n * (2 * a + (n - 1) * d) // 2
    claimed = round(total / n, 4)

    def answer_fn(a=a, d=d, n=n):
        # Build the list, then take its plain mean.
        terms = [a + i * d for i in range(n)]
        return round(sum(terms) / len(terms), 4)

    stem = (
        f"An arithmetic progression has first term {a} and common difference {d}. "
        f"Find the average of its first {n} terms. (Round to 4 decimal places.)"
    )
    solution = (
        f"For evenly spaced terms the average is the midpoint of the first and last. "
        f"The last term is ${a} + {n - 1} \\times {d} = {a + (n - 1) * d}$, so the average is "
        f"$\\dfrac{{{a} + {a + (n - 1) * d}}}{{2}} = {claimed}$."
    )
    return _spec(difficulty, stem, solution, answer_fn, claimed,
                 ["modern:series", "ap-average"], 0.001)


TEMPLATES = {
    MT: [t_ap_nth_term, t_ap_sum, t_gp_nth_term, t_gp_sum,
         t_gp_infinite, t_pattern_next, t_ap_missing_term],
}
