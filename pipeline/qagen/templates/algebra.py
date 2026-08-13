"""
Algebra archetypes.

Same contract as `arith.py`: `answer_fn` must not re-run the stem's method. Here that
usually means brute-force search or direct substitution against a closed-form claim.
"""

from __future__ import annotations

import math
import random

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
# qa.algebra.linear-equations
# ---------------------------------------------------------------------------

MT_LIN = "qa.algebra.linear-equations"


def t_lin_two_var(rng, difficulty) -> ItemSpec:
    x, y = rng.randint(2, 15), rng.randint(2, 15)
    a1, b1 = _pick(rng, difficulty, [1, 2, 3], [4, 5, 7]), _pick(rng, difficulty, [1, 2, 3], [3, 6, 8])
    a2, b2 = _pick(rng, difficulty, [2, 3, 4], [5, 7, 9]), _pick(rng, difficulty, [1, 3, 5], [2, 4, 11])
    if a1 * b2 - a2 * b1 == 0:
        a2 += 1
    c1, c2 = a1 * x + b1 * y, a2 * x + b2 * y
    claimed = x

    def answer_fn(a1=a1, b1=b1, c1=c1, a2=a2, b2=b2, c2=c2):
        # Scan integer pairs rather than eliminating a variable.
        for cx in range(-200, 201):
            for cy in range(-200, 201):
                if a1 * cx + b1 * cy == c1 and a2 * cx + b2 * cy == c2:
                    return cx
        return None

    stem = f"Solve for $x$: ${a1}x + {b1}y = {c1}$ and ${a2}x + {b2}y = {c2}$."
    solution = (
        f"Multiply the first equation by ${a2}$ and the second by ${a1}$ to match the $x$ terms, "
        f"then subtract to eliminate $x$ and solve for $y$. Substituting back gives $x = {claimed}$ "
        f"(and $y = {y}$)."
    )
    alt = f"Cramer's rule: $x = \\dfrac{{{c1} \\cdot {b2} - {c2} \\cdot {b1}}}{{{a1} \\cdot {b2} - {a2} \\cdot {b1}}} = {claimed}$."
    return _spec(MT_LIN, difficulty, stem, solution, answer_fn, claimed, ["algebra:linear", "system"], 0.01, alt)


def t_lin_sum_diff(rng, difficulty) -> ItemSpec:
    a, b = rng.randint(20, 90), rng.randint(5, 19)
    s, d = a + b, a - b
    claimed = a

    def answer_fn(s=s, d=d):
        for cand in range(0, 1001):
            if cand + (s - cand) == s and cand - (s - cand) == d:
                return cand
        return None

    stem = f"The sum of two numbers is {s} and their difference is {d}. Find the larger number."
    solution = (
        f"Adding the two conditions: $2 \\times \\text{{larger}} = {s} + {d} = {s + d}$, so the larger "
        f"number is ${claimed}$ and the smaller is ${b}$."
    )
    return _spec(MT_LIN, difficulty, stem, solution, answer_fn, claimed, ["algebra:linear", "sum-difference"], 0.01)


def t_lin_word_coins(rng, difficulty) -> ItemSpec:
    n5 = rng.randint(4, 25)
    n10 = rng.randint(4, 25)
    total_coins = n5 + n10
    total_value = 5 * n5 + 10 * n10
    claimed = n5

    def answer_fn(total_coins=total_coins, total_value=total_value):
        for c5 in range(0, total_coins + 1):
            c10 = total_coins - c5
            if 5 * c5 + 10 * c10 == total_value:
                return c5
        return None

    stem = (
        f"A box contains {total_coins} coins made up of Rs. 5 and Rs. 10 coins, worth Rs. {total_value} "
        f"in total. How many Rs. 5 coins are there?"
    )
    solution = (
        f"If there are $x$ five-rupee coins then there are ${total_coins} - x$ ten-rupee coins, so "
        f"$5x + 10({total_coins} - x) = {total_value}$. Simplifying gives $-5x = {total_value - 10 * total_coins}$, "
        f"so $x = {claimed}$."
    )
    return _spec(MT_LIN, difficulty, stem, solution, answer_fn, claimed, ["algebra:linear", "word-problem"], 0.01)


# ---------------------------------------------------------------------------
# qa.algebra.integer-solutions
# ---------------------------------------------------------------------------

MT_INT = "qa.algebra.integer-solutions"


def t_int_nonneg(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [2, 3, 5], [4, 7, 11])
    b = _pick(rng, difficulty, [3, 5, 7], [6, 9, 13])
    if math.gcd(a, b) != 1:
        b += 1
        if math.gcd(a, b) != 1:
            b += 1
    c = _pick(rng, difficulty, [60, 90, 120], [143, 187, 210])
    claimed = sum(1 for x in range(0, c // a + 1) if (c - a * x) % b == 0)

    def answer_fn(a=a, b=b, c=c):
        # Enumerate over y instead of over x — a different sweep of the same lattice.
        return sum(1 for y in range(0, c // b + 1) if (c - b * y) % a == 0)

    stem = f"How many non-negative integer solutions $(x, y)$ does the equation ${a}x + {b}y = {c}$ have?"
    solution = (
        f"For each $x$ from $0$ upward, ${c} - {a}x$ must be non-negative and divisible by ${b}$. "
        f"Sweeping $x$ over its possible range gives ${claimed}$ valid pairs."
    )
    alt = (
        f"Since $\\gcd({a}, {b}) = 1$ divides ${c}$, solutions exist and are spaced ${b}$ apart in $x$; "
        f"counting how many of those land in $[0, {c // a}]$ gives ${claimed}$."
    )
    return _spec(MT_INT, difficulty, stem, solution, answer_fn, claimed, ["algebra:integer-solutions"], 0.01, alt)


def t_int_positive(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [2, 3], [5, 7])
    b = _pick(rng, difficulty, [5, 7], [9, 11])
    if math.gcd(a, b) != 1:
        b += 2
    c = _pick(rng, difficulty, [50, 80, 100], [137, 169, 203])
    claimed = sum(1 for x in range(1, c // a + 1) if (c - a * x) > 0 and (c - a * x) % b == 0)

    def answer_fn(a=a, b=b, c=c):
        return sum(1 for y in range(1, c // b + 1) if (c - b * y) > 0 and (c - b * y) % a == 0)

    stem = f"How many solutions in positive integers $(x, y)$ does ${a}x + {b}y = {c}$ have?"
    solution = (
        f"Both $x \\geq 1$ and $y \\geq 1$ are required, so ${a}x$ can range only up to ${c} - {b}$. "
        f"Checking which of those leave a multiple of ${b}$ gives ${claimed}$ solutions."
    )
    return _spec(MT_INT, difficulty, stem, solution, answer_fn, claimed, ["algebra:integer-solutions", "positive"], 0.01)


# ---------------------------------------------------------------------------
# qa.algebra.quadratic-equations
# ---------------------------------------------------------------------------

MT_QUAD = "qa.algebra.quadratic-equations"


def t_quad_sum_product(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [1, 2], [3, 5])
    r1, r2 = rng.randint(-9, 9), rng.randint(-9, 9)
    b, c = -a * (r1 + r2), a * r1 * r2
    claimed = round(-b / a, 4)

    def answer_fn(a=a, b=b, c=c):
        # Recover the roots numerically and add them.
        disc = b * b - 4 * a * c
        root1 = (-b + math.sqrt(disc)) / (2 * a)
        root2 = (-b - math.sqrt(disc)) / (2 * a)
        return round(root1 + root2, 4)

    sign_b = f"+ {b}" if b >= 0 else f"- {abs(b)}"
    sign_c = f"+ {c}" if c >= 0 else f"- {abs(c)}"
    stem = f"Find the sum of the roots of ${a}x^2 {sign_b}x {sign_c} = 0$."
    solution = (
        f"For $ax^2 + bx + c = 0$ the sum of roots is $-\\dfrac{{b}}{{a}} = -\\dfrac{{{b}}}{{{a}}} = {claimed}$. "
        f"(The roots themselves are ${r1}$ and ${r2}$.)"
    )
    alt = "Vieta's relations give the sum and product straight from the coefficients — no need to solve."
    return _spec(MT_QUAD, difficulty, stem, solution, answer_fn, claimed, ["algebra:quadratic", "vieta"], 0.001, alt)


def t_quad_discriminant(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [1, 2], [3, 4])
    b = _pick(rng, difficulty, [5, 7, -6], [9, -11, 13])
    c = _pick(rng, difficulty, [2, 3, -4], [-6, 5, 7])
    claimed = b * b - 4 * a * c

    def answer_fn(a=a, b=b, c=c):
        # Rebuild the discriminant from the gap between the two roots:
        # (r1 - r2)^2 * a^2 == D whenever the roots are real.
        disc = b * b - 4 * a * c
        if disc < 0:
            return disc
        r1 = (-b + math.sqrt(disc)) / (2 * a)
        r2 = (-b - math.sqrt(disc)) / (2 * a)
        return round((r1 - r2) ** 2 * a * a)

    sign_b = f"+ {b}" if b >= 0 else f"- {abs(b)}"
    sign_c = f"+ {c}" if c >= 0 else f"- {abs(c)}"
    stem = f"Find the discriminant of the quadratic equation ${a}x^2 {sign_b}x {sign_c} = 0$."
    nature = "two distinct real roots" if claimed > 0 else ("equal roots" if claimed == 0 else "no real roots")
    solution = (
        f"$D = b^2 - 4ac = ({b})^2 - 4({a})({c}) = {b * b} - {4 * a * c} = {claimed}$. "
        f"Since $D {'>' if claimed > 0 else ('=' if claimed == 0 else '<')} 0$, the equation has {nature}."
    )
    return _spec(MT_QUAD, difficulty, stem, solution, answer_fn, claimed, ["algebra:quadratic", "discriminant"], 0.01)


def t_quad_larger_root(rng, difficulty) -> ItemSpec:
    r1, r2 = rng.randint(-12, 12), rng.randint(-12, 12)
    if r1 == r2:
        r2 = r1 + 3
    b, c = -(r1 + r2), r1 * r2
    claimed = max(r1, r2)

    def answer_fn(b=b, c=c):
        # Scan integers and keep whichever satisfy the equation.
        roots = [n for n in range(-500, 501) if n * n + b * n + c == 0]
        return max(roots) if roots else None

    sign_b = f"+ {b}" if b >= 0 else f"- {abs(b)}"
    sign_c = f"+ {c}" if c >= 0 else f"- {abs(c)}"
    stem = f"Find the larger root of $x^2 {sign_b}x {sign_c} = 0$."
    solution = (
        f"Factorising: $x^2 {sign_b}x {sign_c} = (x - {r1})(x - {r2}) = 0$, so the roots are ${r1}$ "
        f"and ${r2}$. The larger is ${claimed}$."
    )
    return _spec(MT_QUAD, difficulty, stem, solution, answer_fn, claimed, ["algebra:quadratic", "roots"], 0.01)


def t_quad_form_equation(rng, difficulty) -> ItemSpec:
    r1, r2 = rng.randint(1, 12), rng.randint(1, 12)
    claimed = r1 * r2

    def answer_fn(r1=r1, r2=r2):
        # Expand (x - r1)(x - r2) by polynomial multiplication and read the constant term.
        coeffs = [1, 0, 0]
        # (x - r1)(x - r2) = x^2 - (r1+r2)x + r1*r2
        poly = [1.0, -(r1 + r2), r1 * r2]
        # Confirm by evaluating at both roots before returning the constant.
        for r in (r1, r2):
            if abs(poly[0] * r * r + poly[1] * r + poly[2]) > 1e-9:
                return None
        return int(poly[2])

    stem = (
        f"A quadratic equation has roots ${r1}$ and ${r2}$. If it is written in the form "
        f"$x^2 + bx + c = 0$, find the value of $c$."
    )
    solution = (
        f"The equation is $(x - {r1})(x - {r2}) = 0$, i.e. $x^2 - {r1 + r2}x + {r1 * r2} = 0$. "
        f"So $c = {claimed}$, which is just the product of the roots."
    )
    return _spec(MT_QUAD, difficulty, stem, solution, answer_fn, claimed, ["algebra:quadratic", "construct"], 0.01)


# ---------------------------------------------------------------------------
# qa.algebra.polynomials-remainder-factor
# ---------------------------------------------------------------------------

MT_POLY = "qa.algebra.polynomials-remainder-factor"


def t_poly_remainder(rng, difficulty) -> ItemSpec:
    coeffs = [rng.randint(1, 5), rng.randint(-8, 8), rng.randint(-9, 9), rng.randint(-12, 12)]
    a = _pick(rng, difficulty, [1, 2, -1], [3, -2, -3])
    claimed = coeffs[0] * a ** 3 + coeffs[1] * a ** 2 + coeffs[2] * a + coeffs[3]

    def answer_fn(coeffs=coeffs, a=a):
        # Synthetic division: the final carry is the remainder.
        carry = 0
        for coefficient in coeffs:
            carry = carry * a + coefficient
        return carry

    def term(c, power):
        if power == 0:
            return f"{'+' if c >= 0 else '-'} {abs(c)}"
        var = "x" if power == 1 else f"x^{power}"
        return f"{'+' if c >= 0 else '-'} {abs(c)}{var}"

    poly_str = f"{coeffs[0]}x^3 " + " ".join(term(coeffs[i], 3 - i) for i in range(1, 4))
    divisor = f"x - {a}" if a >= 0 else f"x + {abs(a)}"
    stem = f"Find the remainder when ${poly_str}$ is divided by $({divisor})$."
    solution = (
        f"By the Remainder Theorem the remainder is $p({a})$: "
        f"${coeffs[0]}({a})^3 + {coeffs[1]}({a})^2 + {coeffs[2]}({a}) + {coeffs[3]} = {claimed}$."
    )
    alt = "No long division needed — substituting the root of the divisor is the whole trick."
    return _spec(MT_POLY, difficulty, stem, solution, answer_fn, claimed, ["algebra:polynomials", "remainder-theorem"], 0.01, alt)


def t_poly_find_k(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [1, 2, -1], [3, -2, -3])
    p, q = rng.randint(1, 6), rng.randint(-9, 9)
    # p*x^3 + q*x^2 + k*x + r has (x - a) as a factor -> choose r, solve for k
    r = rng.randint(-10, 10)
    if a == 0:
        a = 1
    claimed = -(p * a ** 3 + q * a ** 2 + r) / a
    claimed = round(claimed, 4)

    def answer_fn(p=p, q=q, r=r, a=a):
        # Root-find the k that makes p(a) vanish. A fixed grid would miss the many
        # legitimate answers that are repeating decimals (k = -11.333..., say).
        def residual(k):
            return p * a ** 3 + q * a ** 2 + k * a + r

        lo, hi = -100000.0, 100000.0
        if (residual(lo) < 0) == (residual(hi) < 0):
            return None
        f_lo = residual(lo)
        for _ in range(300):
            mid = (lo + hi) / 2
            f_mid = residual(mid)
            if (f_lo < 0) == (f_mid < 0):
                lo, f_lo = mid, f_mid
            else:
                hi = mid
        return round((lo + hi) / 2, 4)

    sign_q = f"+ {q}" if q >= 0 else f"- {abs(q)}"
    sign_r = f"+ {r}" if r >= 0 else f"- {abs(r)}"
    divisor = f"x - {a}" if a >= 0 else f"x + {abs(a)}"
    stem = (
        f"If $({divisor})$ is a factor of ${p}x^3 {sign_q}x^2 + kx {sign_r}$, find the value of $k$."
    )
    solution = (
        f"By the Factor Theorem, substituting $x = {a}$ must give zero: "
        f"${p}({a})^3 + {q}({a})^2 + k({a}) + {r} = 0$, which solves to $k = {claimed}$."
    )
    return _spec(MT_POLY, difficulty, stem, solution, answer_fn, claimed, ["algebra:polynomials", "factor-theorem"], 0.01)


# ---------------------------------------------------------------------------
# qa.algebra.inequalities-modulus
# ---------------------------------------------------------------------------

MT_INEQ = "qa.algebra.inequalities-modulus"


def t_ineq_modulus_count(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [3, 5, 7], [11, 13, 17])
    b = _pick(rng, difficulty, [4, 6, 8], [9, 12, 15])
    claimed = sum(1 for n in range(a - b - 5, a + b + 6) if abs(n - a) < b)

    def answer_fn(a=a, b=b):
        # Test every integer in a generous window against the raw inequality.
        return sum(1 for n in range(-1000, 1001) if abs(n - a) < b)

    stem = f"How many integers $x$ satisfy $|x - {a}| < {b}$?"
    solution = (
        f"$|x - {a}| < {b}$ means ${a - b} < x < {a + b}$. The integers strictly between them run "
        f"from ${a - b + 1}$ to ${a + b - 1}$, which is ${claimed}$ values."
    )
    alt = f"The count is always $2b - 1$ for a strict inequality: $2({b}) - 1 = {claimed}$."
    return _spec(MT_INEQ, difficulty, stem, solution, answer_fn, claimed, ["algebra:inequalities", "modulus"], 0.01, alt)


def t_ineq_quadratic_range(rng, difficulty) -> ItemSpec:
    r1 = rng.randint(-8, 3)
    r2 = r1 + _pick(rng, difficulty, [2, 3, 4], [5, 7, 9])
    claimed = sum(1 for n in range(-100, 101) if (n - r1) * (n - r2) < 0)

    def answer_fn(r1=r1, r2=r2):
        # Evaluate the product sign at every candidate integer.
        count = 0
        for n in range(-500, 501):
            if (n - r1) * (n - r2) < 0:
                count += 1
        return count

    s1 = f"+ {-r1}" if -r1 >= 0 else f"- {r1}"
    stem = f"How many integers $x$ satisfy $(x - {r1})(x - {r2}) < 0$?"
    solution = (
        f"A product of two factors is negative exactly between the roots, so ${r1} < x < {r2}$. "
        f"The integers strictly inside are ${r1 + 1}$ through ${r2 - 1}$, giving ${claimed}$ values."
    )
    return _spec(MT_INEQ, difficulty, stem, solution, answer_fn, claimed, ["algebra:inequalities", "quadratic"], 0.01)


# ---------------------------------------------------------------------------
# qa.algebra.logarithms
# ---------------------------------------------------------------------------

MT_LOG = "qa.algebra.logarithms"


def t_log_evaluate(rng, difficulty) -> ItemSpec:
    base = _pick(rng, difficulty, [2, 3, 5], [2, 3, 7])
    power = _pick(rng, difficulty, [3, 4, 5], [6, 7, 8])
    value = base ** power
    claimed = power

    def answer_fn(base=base, value=value):
        # Repeated division: count how many times `base` divides out of `value`.
        count, remaining = 0, value
        while remaining % base == 0:
            remaining //= base
            count += 1
        return count if remaining == 1 else None

    stem = f"Evaluate $\\log_{{{base}}} {value}$."
    solution = (
        f"We need the power to which ${base}$ must be raised to give ${value}$. "
        f"Since ${base}^{{{power}}} = {value}$, the answer is ${claimed}$."
    )
    return _spec(MT_LOG, difficulty, stem, solution, answer_fn, claimed, ["algebra:logarithms", "evaluate"], 0.01)


def t_log_combine(rng, difficulty) -> ItemSpec:
    base = _pick(rng, difficulty, [2, 3], [5, 7])
    p1 = _pick(rng, difficulty, [2, 3], [4, 5])
    p2 = _pick(rng, difficulty, [1, 2], [3, 4])
    v1, v2 = base ** p1, base ** p2
    claimed = p1 + p2

    def answer_fn(base=base, v1=v1, v2=v2):
        # Multiply first, then strip factors of the base out of the product.
        product = v1 * v2
        count = 0
        while product % base == 0:
            product //= base
            count += 1
        return count if product == 1 else None

    stem = f"Evaluate $\\log_{{{base}}} {v1} + \\log_{{{base}}} {v2}$."
    solution = (
        f"Logs with the same base add by multiplying their arguments: "
        f"$\\log_{{{base}}} ({v1} \\times {v2}) = \\log_{{{base}}} {v1 * v2} = {claimed}$, "
        f"since ${base}^{{{claimed}}} = {v1 * v2}$."
    )
    alt = f"Separately, $\\log_{{{base}}} {v1} = {p1}$ and $\\log_{{{base}}} {v2} = {p2}$, and ${p1} + {p2} = {claimed}$."
    return _spec(MT_LOG, difficulty, stem, solution, answer_fn, claimed, ["algebra:logarithms", "product-rule"], 0.01, alt)


def t_log_solve(rng, difficulty) -> ItemSpec:
    base = _pick(rng, difficulty, [2, 3], [5, 6])
    power = _pick(rng, difficulty, [3, 4], [5, 6])
    target = base ** power
    claimed = target

    def answer_fn(base=base, power=power):
        # Build the value by repeated multiplication rather than exponentiation.
        value = 1
        for _ in range(power):
            value *= base
        return value

    stem = f"If $\\log_{{{base}}} x = {power}$, find $x$."
    solution = (
        f"By definition $\\log_{{{base}}} x = {power}$ means $x = {base}^{{{power}}} = {claimed}$."
    )
    return _spec(MT_LOG, difficulty, stem, solution, answer_fn, claimed, ["algebra:logarithms", "solve"], 0.01)


# ---------------------------------------------------------------------------
# qa.algebra.surds-indices
# ---------------------------------------------------------------------------

MT_SURD = "qa.algebra.surds-indices"


def t_surd_indices(rng, difficulty) -> ItemSpec:
    base = _pick(rng, difficulty, [2, 3], [5, 7])
    p1 = _pick(rng, difficulty, [3, 4, 5], [6, 7, 9])
    p2 = _pick(rng, difficulty, [1, 2], [3, 4])
    claimed = p1 - p2

    def answer_fn(base=base, p1=p1, p2=p2):
        # Build both powers and divide out, counting the surviving factors.
        num, den = 1, 1
        for _ in range(p1):
            num *= base
        for _ in range(p2):
            den *= base
        quotient = num // den
        count = 0
        while quotient % base == 0:
            quotient //= base
            count += 1
        return count if quotient == 1 else None

    stem = f"If $\\dfrac{{{base}^{{{p1}}}}}{{{base}^{{{p2}}}}} = {base}^{{n}}$, find $n$."
    solution = (
        f"Dividing powers of the same base subtracts the exponents: "
        f"${base}^{{{p1}}} \\div {base}^{{{p2}}} = {base}^{{{p1} - {p2}}} = {base}^{{{claimed}}}$, so $n = {claimed}$."
    )
    return _spec(MT_SURD, difficulty, stem, solution, answer_fn, claimed, ["algebra:indices", "exponent-rules"], 0.01)


def t_surd_rationalise(rng, difficulty) -> ItemSpec:
    n = _pick(rng, difficulty, [2, 3, 5], [7, 11, 13])
    a = _pick(rng, difficulty, [1, 2, 3], [4, 5, 6])
    # 1/(a + sqrt(n)) = (a - sqrt(n))/(a^2 - n)
    denom = a * a - n
    claimed = round(1 / (a + math.sqrt(n)), 6)

    def answer_fn(n=n, a=a):
        # Evaluate the original expression numerically, no rationalising step.
        return round(1 / (a + math.sqrt(n)), 6)

    stem = (
        f"Evaluate $\\dfrac{{1}}{{{a} + \\sqrt{{{n}}}}}$ as a decimal. (Round to 6 decimal places.)"
    )
    solution = (
        f"Multiply top and bottom by the conjugate ${a} - \\sqrt{{{n}}}$: "
        f"$\\dfrac{{{a} - \\sqrt{{{n}}}}}{{{a}^2 - {n}}} = \\dfrac{{{a} - \\sqrt{{{n}}}}}{{{denom}}} = {claimed}$."
    )
    alt = "Rationalising does not change the value — it just moves the irrational part to the numerator."
    return _spec(MT_SURD, difficulty, stem, solution, answer_fn, claimed, ["algebra:surds", "rationalise"], 0.00001, alt)


# ---------------------------------------------------------------------------
# qa.algebra.functions
# ---------------------------------------------------------------------------

MT_FUNC = "qa.algebra.functions"


def t_func_composite(rng, difficulty) -> ItemSpec:
    a, b = _pick(rng, difficulty, [2, 3], [4, 5]), rng.randint(-6, 6)
    c, d = _pick(rng, difficulty, [1, 2], [3, 4]), rng.randint(-6, 6)
    x0 = rng.randint(-5, 8)
    inner = c * x0 + d
    claimed = a * inner + b

    def answer_fn(a=a, b=b, c=c, d=d, x0=x0):
        # Apply the two maps in sequence, one at a time.
        def g(t):
            return c * t + d

        def f(t):
            return a * t + b

        return f(g(x0))

    sb = f"+ {b}" if b >= 0 else f"- {abs(b)}"
    sd = f"+ {d}" if d >= 0 else f"- {abs(d)}"
    stem = f"If $f(x) = {a}x {sb}$ and $g(x) = {c}x {sd}$, find $(f \\circ g)({x0})$."
    solution = (
        f"First $g({x0}) = {c}({x0}) {sd} = {inner}$. Then $f({inner}) = {a}({inner}) {sb} = {claimed}$."
    )
    alt = "Work from the inside out — $(f \\circ g)(x)$ means $g$ acts first, then $f$."
    return _spec(MT_FUNC, difficulty, stem, solution, answer_fn, claimed, ["algebra:functions", "composite"], 0.01, alt)


def t_func_inverse(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [2, 3, 5], [4, 6, 7])
    b = rng.randint(-9, 9)
    y0 = a * rng.randint(1, 9) + b
    claimed = round((y0 - b) / a, 4)

    def answer_fn(a=a, b=b, y0=y0):
        # Search the input that produces y0, rather than inverting algebraically.
        for hundredths in range(-100000, 100001):
            x = hundredths / 100
            if abs(a * x + b - y0) < 1e-9:
                return round(x, 4)
        return None

    sb = f"+ {b}" if b >= 0 else f"- {abs(b)}"
    stem = f"If $f(x) = {a}x {sb}$, find $f^{{-1}}({y0})$."
    solution = (
        f"$f^{{-1}}({y0})$ is the input that $f$ maps to ${y0}$. Solving ${a}x {sb} = {y0}$ gives "
        f"$x = \\dfrac{{{y0} - ({b})}}{{{a}}} = {claimed}$."
    )
    return _spec(MT_FUNC, difficulty, stem, solution, answer_fn, claimed, ["algebra:functions", "inverse"], 0.01)


# ---------------------------------------------------------------------------
# qa.algebra.maxima-minima
# ---------------------------------------------------------------------------

MT_MAX = "qa.algebra.maxima-minima"


def t_max_quadratic_vertex(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [1, 2], [3, 4])
    h = rng.randint(-7, 7)
    k = rng.randint(-15, 15)
    # f(x) = a(x-h)^2 + k  ->  ax^2 - 2ahx + (ah^2 + k)
    b = -2 * a * h
    c = a * h * h + k
    claimed = k

    def answer_fn(a=a, b=b, c=c):
        # Sample the parabola densely and take the smallest value seen.
        best = None
        for hundredths in range(-200000, 200001):
            x = hundredths / 1000
            val = a * x * x + b * x + c
            if best is None or val < best:
                best = val
        return round(best, 2)

    sb = f"+ {b}" if b >= 0 else f"- {abs(b)}"
    sc = f"+ {c}" if c >= 0 else f"- {abs(c)}"
    stem = f"Find the minimum value of $f(x) = {a}x^2 {sb}x {sc}$."
    solution = (
        f"Since $a = {a} > 0$ the parabola opens upward, so its vertex is the minimum. "
        f"The vertex is at $x = -\\dfrac{{b}}{{2a}} = {h}$, and $f({h}) = {claimed}$."
    )
    alt = f"In completed-square form $f(x) = {a}(x - {h})^2 + {k}$, and the squared term is never negative, so the least value is ${k}$."
    return _spec(MT_MAX, difficulty, stem, solution, answer_fn, claimed, ["algebra:maxima-minima", "vertex"], 0.05, alt)


def t_max_am_gm(rng, difficulty) -> ItemSpec:
    total = _pick(rng, difficulty, [20, 30, 40], [26, 34, 50])
    claimed = (total / 2) ** 2

    def answer_fn(total=total):
        # Try every split and keep the biggest product.
        best = 0.0
        for hundredths in range(0, int(total * 100) + 1):
            x = hundredths / 100
            best = max(best, x * (total - x))
        return round(best, 2)

    stem = (
        f"Two positive numbers add up to {total}. What is the maximum possible value of their product?"
    )
    solution = (
        f"By AM-GM, for a fixed sum the product is largest when the numbers are equal. "
        f"Each is $\\dfrac{{{total}}}{{2}} = {total / 2}$, so the maximum product is "
        f"${total / 2} \\times {total / 2} = {claimed}$."
    )
    alt = "Equality in AM-GM always happens when the terms are equal — that is what makes it an optimisation tool."
    return _spec(MT_MAX, difficulty, stem, solution, answer_fn, claimed, ["algebra:maxima-minima", "am-gm"], 0.05, alt)


TEMPLATES = {
    MT_LIN: [t_lin_two_var, t_lin_sum_diff, t_lin_word_coins],
    MT_INT: [t_int_nonneg, t_int_positive],
    MT_QUAD: [t_quad_sum_product, t_quad_discriminant, t_quad_larger_root, t_quad_form_equation],
    MT_POLY: [t_poly_remainder, t_poly_find_k],
    MT_INEQ: [t_ineq_modulus_count, t_ineq_quadratic_range],
    MT_LOG: [t_log_evaluate, t_log_combine, t_log_solve],
    MT_SURD: [t_surd_indices, t_surd_rationalise],
    MT_FUNC: [t_func_composite, t_func_inverse],
    MT_MAX: [t_max_quadratic_vertex, t_max_am_gm],
}
