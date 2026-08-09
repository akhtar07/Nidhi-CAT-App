from __future__ import annotations

import itertools
import math
import random
from fractions import Fraction

import sympy as sp

from qagen.harness import ItemSpec
from qagen.syllabus_lookup import item_count, target_seconds

DIFF_CYCLE = ["easy", "easy", "medium", "medium", "medium", "hard", "hard", "very_hard"]


def _diffs(n: int) -> list[str]:
    return [DIFF_CYCLE[i % len(DIFF_CYCLE)] for i in range(n)]


def gen_permutations_combinations() -> list[ItemSpec]:
    mt = "qa.modern.permutations-combinations"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        total = rng.randint(6, 15)
        r = rng.randint(2, total - 2)
        claimed = math.comb(total, r)
        stem = (
            f"In how many ways can a committee of {r} people be chosen from a "
            f"group of {total} people?"
        )
        solution = (
            f"This is a selection (order doesn't matter): "
            f"$\\binom{{{total}}}{{{r}}} = \\dfrac{{{total}!}}{{{r}!({total}-{r})!}} = {claimed}$."
        )

        def answer_fn(total=total, r=r):
            # Independent of math.comb(): manual factorial-ratio computation.
            return math.factorial(total) // (math.factorial(r) * math.factorial(total - r))

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["modern:combinations"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_probability() -> list[ItemSpec]:
    mt = "qa.modern.probability"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        red = rng.randint(3, 6)
        blue = rng.randint(3, 6)
        k = rng.randint(2, 3)
        total = red + blue
        favourable = math.comb(red, k)
        possible = math.comb(total, k)
        g = math.gcd(favourable, possible)
        num, den = favourable // g, possible // g
        claimed = f"{num}/{den}"
        stem = (
            f"A bag contains {red} red balls and {blue} blue balls. If {k} balls "
            f"are drawn at random without replacement, find the probability that "
            f"all {k} are red. Give the answer as a reduced fraction, e.g. '3/10'."
        )
        solution = (
            f"P(all red) $= \\dfrac{{\\binom{{{red}}}{{{k}}}}}{{\\binom{{{total}}}{{{k}}}}} "
            f"= \\dfrac{{{favourable}}}{{{possible}}} = \\dfrac{{{num}}}{{{den}}}$."
        )

        def answer_fn(red=red, blue=blue, total=total, k=k):
            # Independent: brute-force enumerate every k-subset of the bag.
            balls = ["R"] * red + ["B"] * blue
            all_combos = list(itertools.combinations(range(total), k))
            fav = sum(1 for combo in all_combos if all(balls[idx] == "R" for idx in combo))
            frac = Fraction(fav, len(all_combos))
            return f"{frac.numerator}/{frac.denominator}"

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["modern:probability"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_set_theory_venn() -> list[ItemSpec]:
    mt = "qa.modern.set-theory-venn"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        both = rng.randint(5, 20)
        a_only = rng.randint(10, 40)
        b_only = rng.randint(10, 40)
        size_a, size_b = a_only + both, b_only + both
        claimed = a_only + b_only + both
        stem = (
            f"In a class, {size_a} students like Maths and {size_b} students like "
            f"Science. If {both} students like both subjects, how many students "
            f"like at least one of the two subjects?"
        )
        solution = (
            f"$|A \\cup B| = |A| + |B| - |A \\cap B| = {size_a} + {size_b} - {both} "
            f"= {claimed}$."
        )

        def answer_fn(size_a=size_a, size_b=size_b, both=both):
            # Independent decomposition: A-only + B-only + both.
            return (size_a - both) + (size_b - both) + both

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["modern:set-theory", "venn"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_binomial_theorem() -> list[ItemSpec]:
    mt = "qa.modern.binomial-theorem"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    x = sp.symbols("x")
    # Widened power/a/b ranges for more combinatorial variety (was power in
    # [5,9], a/b in [1,3] — ~225 combos, workable but thin at the high end).
    for i in range(n):
        power = rng.randint(5, 12)
        a, b = rng.randint(1, 4), rng.randint(1, 4)
        k = rng.randint(1, power - 1)
        claimed = math.comb(power, k) * a ** (power - k) * b ** k
        stem = (
            f"Find the coefficient of $x^{{{k}}}$ in the expansion of "
            f"$({a} + {b}x)^{{{power}}}$."
        )
        solution = (
            f"General term: $\\binom{{{power}}}{{{k}}} {a}^{{{power}-{k}}} "
            f"({b}x)^{{{k}}}$. Coefficient of $x^{{{k}}}$ "
            f"$= \\binom{{{power}}}{{{k}}} {a}^{{{power - k}}} {b}^{{{k}}} = {claimed}$."
        )

        def answer_fn(power=power, a=a, b=b, k=k):
            # Independent: fully expand the polynomial with sympy and read
            # off the coefficient, rather than reusing the closed-form.
            expr = sp.expand((a + b * x) ** power)
            return int(expr.coeff(x, k))

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["modern:binomial-theorem"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_series_sequences_hybrids() -> list[ItemSpec]:
    mt = "qa.modern.series-sequences-hybrids"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    # Original version only ever produced "sum of squares" items — a single
    # num parameter in [8,30] (23 possible values) is too thin a pool to
    # safely draw 10 unique instances, and gives no real mathematical
    # variety for a topic named "hybrids". Added a genuinely distinct
    # sum-of-cubes variant (different closed form, different independent
    # check) and widened the num range, so both the item count and the
    # underlying maths vary.
    num_choices = list(range(6, 60))
    for i in range(n):
        series_type = rng.choice(["squares", "cubes"])
        num = rng.choice(num_choices)
        if series_type == "squares":
            claimed = num * (num + 1) * (2 * num + 1) // 6
            stem = f"Find the sum $1^2 + 2^2 + 3^2 + \\dots + {num}^2$."
            solution = (
                f"$\\sum_{{i=1}}^{{n}} i^2 = \\dfrac{{n(n+1)(2n+1)}}{{6}} = "
                f"\\dfrac{{{num}\\times{num + 1}\\times{2 * num + 1}}}{{6}} = {claimed}$."
            )
            tag = "sum-of-squares"

            def answer_fn(num=num):
                return sum(k * k for k in range(1, num + 1))
        else:
            claimed = (num * (num + 1) // 2) ** 2
            stem = f"Find the sum $1^3 + 2^3 + 3^3 + \\dots + {num}^3$."
            solution = (
                f"$\\sum_{{i=1}}^{{n}} i^3 = \\left[\\dfrac{{n(n+1)}}{{2}}\\right]^2 = "
                f"\\left[\\dfrac{{{num}\\times{num + 1}}}{{2}}\\right]^2 = {claimed}$."
            )
            tag = "sum-of-cubes"

            def answer_fn(num=num):
                # Independent of the [n(n+1)/2]^2 closed form: direct
                # cube-by-cube summation.
                return sum(k ** 3 for k in range(1, num + 1))

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["modern:series", tag], format="tita", tita_tolerance=0,
        ))
    return specs


GENERATORS = [
    gen_permutations_combinations,
    gen_probability,
    gen_set_theory_venn,
    gen_binomial_theorem,
    gen_series_sequences_hybrids,
]
