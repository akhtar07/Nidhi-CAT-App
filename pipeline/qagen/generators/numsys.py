from __future__ import annotations

import math
import random

import sympy as sp

from qagen.harness import ItemSpec
from qagen.syllabus_lookup import item_count, target_seconds

DIFF_CYCLE = ["easy", "easy", "medium", "medium", "medium", "hard", "hard", "very_hard"]


def _diffs(n: int) -> list[str]:
    return [DIFF_CYCLE[i % len(DIFF_CYCLE)] for i in range(n)]


def _brute_factor_count(num: int) -> int:
    return sum(1 for d in range(1, num + 1) if num % d == 0)


def gen_divisibility_factors() -> list[ItemSpec]:
    mt = "qa.numsys.divisibility-factors"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    primes = [2, 3, 5, 7, 11]
    for i in range(n):
        p1, p2 = rng.sample(primes, 2)
        e1, e2 = rng.randint(1, 4), rng.randint(1, 3)
        num = p1 ** e1 * p2 ** e2
        claimed = (e1 + 1) * (e2 + 1)
        stem = f"Find the number of factors (divisors) of {num}."
        solution = (
            f"${num} = {p1}^{{{e1}}} \\times {p2}^{{{e2}}}$. "
            f"Number of factors $= ({e1}+1)({e2}+1) = {claimed}$."
        )

        def answer_fn(num=num):
            return _brute_factor_count(num)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["numsys:factors"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_hcf_lcm() -> list[ItemSpec]:
    mt = "qa.numsys.hcf-lcm"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        g = rng.randint(2, 15)
        m1, m2 = rng.randint(2, 12), rng.randint(2, 12)
        while m1 == m2:
            m2 = rng.randint(2, 12)
        while math.gcd(m1, m2) != 1:
            m1, m2 = rng.randint(2, 12), rng.randint(2, 12)
        a, b = g * m1, g * m2
        claimed = a * b // g
        stem = f"Find the LCM of {a} and {b}."
        solution = (
            f"HCF$({a}, {b}) = {g}$. LCM $= \\dfrac{{{a} \\times {b}}}{{{g}}} = {claimed}$."
        )

        def answer_fn(a=a, b=b):
            return math.lcm(a, b)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["numsys:hcf-lcm"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_remainders() -> list[ItemSpec]:
    mt = "qa.numsys.remainders"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        a = rng.randint(2, 30)
        b = rng.randint(5, 12)
        m = rng.randint(3, 20)
        claimed = pow(a, b, m)
        stem = f"Find the remainder when ${a}^{{{b}}}$ is divided by {m}."
        solution = (
            f"Using modular exponentiation (repeated squaring), "
            f"${a}^{{{b}}} \\bmod {m} = {claimed}$."
        )

        def answer_fn(a=a, b=b, m=m):
            # Independent of pow()'s fast modexp: naive iterative multiply-mod.
            r = 1
            for _ in range(b):
                r = (r * a) % m
            return r

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["numsys:remainders", "modular-exponentiation"], format="tita",
            tita_tolerance=0,
        ))
    return specs


def gen_factors_count_sum_product() -> list[ItemSpec]:
    mt = "qa.numsys.factors-count-sum-product"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        p1, p2 = rng.sample([2, 3, 5, 7], 2)
        e1, e2 = rng.randint(1, 3), rng.randint(1, 2)
        num = p1 ** e1 * p2 ** e2
        claimed = int(sp.divisor_sigma(num))
        stem = f"Find the sum of all factors (divisors) of {num}."
        p1_series = " + ".join(f"{p1}^{{{k}}}" for k in range(e1 + 1))
        p2_series = " + ".join(f"{p2}^{{{k}}}" for k in range(e2 + 1))
        solution = (
            f"${num} = {p1}^{{{e1}}} \\times {p2}^{{{e2}}}$. "
            f"Sum of factors $= ({p1_series})({p2_series}) = {claimed}$."
        )

        def answer_fn(num=num):
            return sum(d for d in range(1, num + 1) if num % d == 0)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["numsys:sum-of-factors"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_base_systems() -> list[ItemSpec]:
    mt = "qa.numsys.base-systems"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    digits = "0123456789ABCDEF"
    for i in range(n):
        num = rng.randint(50, 500)
        base = rng.choice([2, 5, 7, 8, 16])

        def to_base(x: int, b: int) -> str:
            if x == 0:
                return "0"
            out = []
            while x:
                out.append(digits[x % b])
                x //= b
            return "".join(reversed(out))

        claimed = to_base(num, base)
        stem = f"Convert {num} (base 10) to base {base}."
        solution = (
            f"Repeatedly divide {num} by {base} and read the remainders "
            f"bottom-to-top: $({num})_{{10}} = ({claimed})_{{{base}}}$."
        )

        def answer_fn(claimed=claimed, base=base, num=num):
            # Independent: parse the produced digit string with Python's own
            # base-N int parser and confirm it round-trips to num, rather
            # than re-running the same to_base() division loop.
            return claimed if int(claimed, base) == num else "MISMATCH"

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["numsys:base-conversion"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_last_digit_trailing_zeroes() -> list[ItemSpec]:
    mt = "qa.numsys.last-digit-trailing-zeroes"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        num = rng.randint(20, 90)
        stem = f"Find the number of trailing zeroes in {num}!"

        def legendre_zeroes(x: int) -> int:
            count, p = 0, 5
            while p <= x:
                count += x // p
                p *= 5
            return count

        claimed = legendre_zeroes(num)
        solution = (
            f"Trailing zeroes in $n!$ come from factors of 5 (since factors of 2 "
            f"are more abundant). Count $= \\lfloor n/5 \\rfloor + \\lfloor n/25 "
            f"\\rfloor + \\dots = "
            + " + ".join(
                f"\\lfloor {num}/{5 ** k} \\rfloor"
                for k in range(1, 10) if 5 ** k <= num
            )
            + f" = {claimed}$."
        )

        def answer_fn(num=num):
            # Independent: compute n! directly and count trailing zeroes.
            fact = math.factorial(num)
            s = str(fact)
            return len(s) - len(s.rstrip("0"))

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["numsys:trailing-zeroes", "legendre"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_factorials_prime_power() -> list[ItemSpec]:
    mt = "qa.numsys.factorials-prime-power"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        num = rng.randint(20, 80)
        p = rng.choice([2, 3, 5, 7])

        def legendre(x: int, prime: int) -> int:
            count, pw = 0, prime
            while pw <= x:
                count += x // pw
                pw *= prime
            return count

        claimed = legendre(num, p)
        stem = f"Find the highest power of {p} that divides {num}!"
        solution = (
            f"By Legendre's formula, the highest power of {p} dividing $n!$ is "
            f"$\\sum \\lfloor n/{p}^k \\rfloor = {claimed}$."
        )

        def answer_fn(num=num, p=p):
            # Independent: repeatedly divide out p from n! computed directly.
            fact = math.factorial(num)
            count = 0
            while fact % p == 0:
                fact //= p
                count += 1
            return count

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["numsys:legendre", "prime-power"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_rational_irrational() -> list[ItemSpec]:
    mt = "qa.numsys.rational-irrational"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    non_squares = [2, 3, 5, 6, 7]
    for i in range(n):
        a = rng.choice(non_squares)
        m = rng.randint(2, 5)
        b = a * m * m
        claimed = (1 + m) ** 2 * a
        stem = (
            f"Simplify $(\\sqrt{{{a}}} + \\sqrt{{{b}}})^2$ and give its exact "
            f"(integer) value."
        )
        solution = (
            f"$\\sqrt{{{b}}} = \\sqrt{{{a} \\times {m}^2}} = {m}\\sqrt{{{a}}}$, so "
            f"$\\sqrt{{{a}}}+\\sqrt{{{b}}} = (1+{m})\\sqrt{{{a}}}$. "
            f"Squaring: $(1+{m})^2 \\times {a} = {claimed}$."
        )

        def answer_fn(a=a, b=b):
            expr = (sp.sqrt(a) + sp.sqrt(b)) ** 2
            return int(sp.nsimplify(sp.expand(expr)))

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["numsys:surds", "rational-irrational"], format="tita", tita_tolerance=0,
        ))
    return specs


GENERATORS = [
    gen_divisibility_factors,
    gen_hcf_lcm,
    gen_remainders,
    gen_factors_count_sum_product,
    gen_base_systems,
    gen_last_digit_trailing_zeroes,
    gen_factorials_prime_power,
    gen_rational_irrational,
]
