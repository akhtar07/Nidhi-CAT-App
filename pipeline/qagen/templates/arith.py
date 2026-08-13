"""
Arithmetic archetypes — the question forms CAT actually asks per micro-topic.

Every `answer_fn` here deliberately reaches the answer by a *different route* than the
stem's stated method: closed-form claim vs. step-by-step simulation, or formula claim
vs. exhaustive search. See the package docstring for why that distinction is the whole
point of this file.
"""

from __future__ import annotations

import random

from qagen.harness import ItemSpec, mcq_options_from_distractors
from qagen.syllabus_lookup import target_seconds

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_HARDER = ("hard", "very_hard")


def _pick(rng: random.Random, difficulty: str, easy: list, hard: list):
    """Easy/medium draw from round, friendly numbers; hard/very_hard from awkward ones,
    so difficulty changes the arithmetic load rather than just relabelling the item."""
    return rng.choice(hard if difficulty in _HARDER else easy)


def _spec(mt: str, difficulty: str, stem: str, solution: str, answer_fn, claimed,
          tags: list[str], tol: float, alt: str | None = None,
          fmt: str = "tita", options=None, correct_key=None) -> ItemSpec:
    return ItemSpec(
        microtopic_id=mt, difficulty=difficulty, stem=stem, solution=solution,
        alt_solution=alt, answer_fn=answer_fn, claimed_value=claimed,
        target_seconds=target_seconds(mt), tags=tags, format=fmt,
        tita_tolerance=tol, options=options, correct_key=correct_key,
    )


def _search_int(predicate, lo: int = 1, hi: int = 20000):
    """Exhaustive search — an intentionally dumb, formula-free way to confirm a value."""
    for cand in range(lo, hi + 1):
        if predicate(cand):
            return cand
    return None


def _bisect(f, lo: float, hi: float, iters: int = 300) -> float:
    """Numerically solve f(x) = 0 on a bracketing interval where f is monotonic.

    Used instead of a fixed-grid scan because many honest answers (a cost price of
    518.518…, a blend ratio of 4/9) are repeating decimals that no discrete grid ever
    lands on exactly — a scan reports "not found" for a perfectly correct item. Root
    finding is still a genuinely different mechanism from the algebraic rearrangement
    the solution text performs, which is what makes it real verification.
    """
    f_lo = f(lo)
    for _ in range(iters):
        mid = (lo + hi) / 2
        f_mid = f(mid)
        if (f_lo < 0) == (f_mid < 0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---------------------------------------------------------------------------
# qa.arith.percentages
# ---------------------------------------------------------------------------

MT_PCT = "qa.arith.percentages"


def t_pct_successive(rng: random.Random, difficulty: str) -> ItemSpec:
    p1 = _pick(rng, difficulty, [10, 20, 25, 40, 50], [12, 17, 23, 37, 44, 58])
    p2 = _pick(rng, difficulty, [10, 20, 25, 40, 50], [13, 18, 27, 36, 41, 54])
    claimed = round(p1 - p2 - p1 * p2 / 100, 2)

    def answer_fn(p1=p1, p2=p2):
        # Sequential simulation on a notional price of 100 — never touches the
        # p1 - p2 - p1*p2/100 shortcut the solution quotes.
        price = 100.0
        price *= 1 + p1 / 100
        price *= 1 - p2 / 100
        return round(price - 100, 2)

    stem = (
        f"The price of an article is increased by {p1}% and the new price is then "
        f"decreased by {p2}%. Find the net percentage change in the price. "
        f"(Enter a negative value for a net decrease.)"
    )
    solution = (
        f"Start from 100. After the increase: $100 \\times (1 + {p1}/100) = {100 * (1 + p1 / 100):.2f}$. "
        f"After the decrease: ${100 * (1 + p1 / 100):.2f} \\times (1 - {p2}/100) = {100 * (1 + p1 / 100) * (1 - p2 / 100):.2f}$. "
        f"Net change $= {claimed}\\%$."
    )
    alt = (
        f"Shortcut: net $\\% = p_1 - p_2 - \\dfrac{{p_1 p_2}}{{100}} = "
        f"{p1} - {p2} - \\dfrac{{{p1 * p2}}}{{100}} = {claimed}\\%$."
    )
    return _spec(MT_PCT, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:percentages", "successive-change"], 0.05, alt)


def t_pct_find_original(rng: random.Random, difficulty: str) -> ItemSpec:
    pct = _pick(rng, difficulty, [20, 25, 50], [12, 15, 35, 45])
    orig = rng.randrange(400, 4001, 100)
    final = orig * (100 + pct) / 100
    claimed = orig

    def answer_fn(pct=pct, final=final):
        # Search for the value that grows into `final`, rather than dividing by
        # (1 + pct/100) the way the solution does.
        return _search_int(lambda c: abs(c * (100 + pct) / 100 - final) < 1e-9)

    stem = (
        f"After its price was increased by {pct}%, an article costs Rs. {final:.0f}. "
        f"What was its price (in Rs.) before the increase?"
    )
    solution = (
        f"If the original price is $x$, then $x \\times \\left(1 + \\dfrac{{{pct}}}{{100}}\\right) = {final:.0f}$, "
        f"so $x = \\dfrac{{{final:.0f} \\times 100}}{{{100 + pct}}} = {orig}$."
    )
    alt = (
        f"The new price is {100 + pct}% of the old, so the old price is "
        f"$\\dfrac{{100}}{{{100 + pct}}}$ of Rs. {final:.0f} $=$ Rs. {orig}."
    )
    return _spec(MT_PCT, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:percentages", "reverse-percentage"], 0.01, alt)


def t_pct_more_less(rng: random.Random, difficulty: str) -> ItemSpec:
    x = _pick(rng, difficulty, [25, 50, 100, 20], [15, 30, 60, 80, 120])
    claimed = round(100 * x / (100 + x), 2)

    def answer_fn(x=x):
        # Assign concrete values and measure the shortfall directly.
        b = 100.0
        a = b * (1 + x / 100)
        return round((a - b) / a * 100, 2)

    stem = (
        f"If A's salary is {x}% more than B's salary, then B's salary is what percent "
        f"less than A's salary? (Round to 2 decimal places.)"
    )
    solution = (
        f"Let B $= 100$, so A $= {100 + x}$. B is short of A by ${x}$, and as a percentage "
        f"**of A** that is $\\dfrac{{{x}}}{{{100 + x}}} \\times 100 = {claimed}\\%$."
    )
    alt = (
        f"Formula: if A is $x\\%$ more than B, then B is $\\dfrac{{100x}}{{100 + x}}\\%$ less than A "
        f"$= \\dfrac{{100 \\times {x}}}{{{100 + x}}} = {claimed}\\%$. The base changes from B to A — that swap is the whole trap."
    )
    return _spec(MT_PCT, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:percentages", "base-change"], 0.05, alt)


def t_pct_expenditure(rng: random.Random, difficulty: str) -> ItemSpec:
    p = _pick(rng, difficulty, [20, 25, 50], [15, 32, 44, 60])
    q = _pick(rng, difficulty, [0, 10], [5, 8, 12])
    claimed = round(100 * (1 - (100 + q) / (100 + p)), 2)

    def answer_fn(p=p, q=q):
        # Model the household budget explicitly instead of using the ratio formula.
        price, qty = 100.0, 100.0
        budget_new = price * qty * (1 + q / 100)
        price_new = price * (1 + p / 100)
        qty_new = budget_new / price_new
        return round((qty - qty_new) / qty * 100, 2)

    rise = f"rises by {q}%" if q else "stays the same"
    stem = (
        f"The price of rice rises by {p}%. By what percent must a family reduce its "
        f"consumption so that its total expenditure on rice only {rise}? "
        f"(Round to 2 decimal places.)"
    )
    solution = (
        f"Take price $= 100$ and consumption $= 100$, so expenditure $= 10000$. "
        f"The new price is ${100 + p}$ and the new expenditure must be ${100 * (100 + q):.0f}$, "
        f"so the new consumption is $\\dfrac{{{100 * (100 + q):.0f}}}{{{100 + p}}} = {100 * (100 + q) / (100 + p):.2f}$. "
        f"That is a drop of ${claimed}\\%$."
    )
    return _spec(MT_PCT, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:percentages", "expenditure"], 0.05)


def t_pct_passing_marks(rng: random.Random, difficulty: str) -> ItemSpec:
    pass_pct = _pick(rng, difficulty, [30, 40, 50], [33, 36, 45])
    total = rng.randrange(300, 1201, 100)
    shortfall = rng.randrange(10, 60, 5)
    scored = int(pass_pct * total / 100) - shortfall
    claimed = total

    def answer_fn(pass_pct=pass_pct, scored=scored, shortfall=shortfall):
        # Search the total that makes the pass mark exactly `scored + shortfall`.
        need = scored + shortfall
        return _search_int(lambda t: abs(pass_pct * t / 100 - need) < 1e-9)

    stem = (
        f"A student scored {scored} marks in an exam and failed by {shortfall} marks. "
        f"If the pass mark is {pass_pct}% of the maximum marks, what are the maximum marks?"
    )
    solution = (
        f"The pass mark is ${scored} + {shortfall} = {scored + shortfall}$. "
        f"If the maximum is $M$, then $\\dfrac{{{pass_pct}}}{{100}} \\times M = {scored + shortfall}$, "
        f"so $M = \\dfrac{{{scored + shortfall} \\times 100}}{{{pass_pct}}} = {total}$."
    )
    return _spec(MT_PCT, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:percentages", "pass-marks"], 0.01)


def t_pct_compound_growth(rng: random.Random, difficulty: str) -> ItemSpec:
    rate = _pick(rng, difficulty, [10, 20, 25], [8, 12, 15])
    years = _pick(rng, difficulty, [2], [3])
    start = rng.randrange(4000, 40001, 1000)
    claimed = round(start * (1 + rate / 100) ** years, 2)

    def answer_fn(start=start, rate=rate, years=years):
        # Year-by-year loop rather than the exponent form the solution uses.
        value = float(start)
        for _ in range(years):
            value += value * rate / 100
        return round(value, 2)

    stem = (
        f"The population of a town is {start} and grows at {rate}% per year. "
        f"What will the population be after {years} years? (Round to 2 decimal places.)"
    )
    steps = []
    running = float(start)
    for y in range(1, years + 1):
        running *= 1 + rate / 100
        steps.append(f"after year {y}: ${running:.2f}$")
    solution = (
        f"Apply {rate}% growth to the running total each year — "
        + ", ".join(steps)
        + f". So the population is ${claimed}$."
    )
    alt = f"Closed form: $P = {start} \\times \\left(1 + \\dfrac{{{rate}}}{{100}}\\right)^{{{years}}} = {claimed}$."
    return _spec(MT_PCT, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:percentages", "compound-growth"], 0.05, alt)


def t_pct_area_change(rng: random.Random, difficulty: str) -> ItemSpec:
    x = _pick(rng, difficulty, [10, 20, 30], [15, 25, 45])
    claimed = round(2 * x + x * x / 100, 2)

    def answer_fn(x=x):
        # Build both squares and compare areas — no $2x + x^2/100$ anywhere.
        side = 100.0
        area_before = side * side
        area_after = (side * (1 + x / 100)) ** 2
        return round((area_after - area_before) / area_before * 100, 2)

    stem = (
        f"Each side of a square is increased by {x}%. By what percent does its area increase? "
        f"(Round to 2 decimal places.)"
    )
    solution = (
        f"Take the side as 100, so the area is $10000$. The new side is ${100 + x}$ and the "
        f"new area is ${(100 + x) ** 2}$. The increase is "
        f"$\\dfrac{{{(100 + x) ** 2 - 10000}}}{{10000}} \\times 100 = {claimed}\\%$."
    )
    alt = (
        f"Both dimensions grow by $x\\%$, so the area grows by $2x + \\dfrac{{x^2}}{{100}} = "
        f"2({x}) + \\dfrac{{{x * x}}}{{100}} = {claimed}\\%$."
    )
    return _spec(MT_PCT, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:percentages", "area-percentage"], 0.05, alt)


# ---------------------------------------------------------------------------
# qa.arith.profit-loss-discount
# ---------------------------------------------------------------------------

MT_PL = "qa.arith.profit-loss-discount"


def t_pl_sp_from_profit(rng: random.Random, difficulty: str) -> ItemSpec:
    cp = rng.randrange(200, 3001, 50)
    profit = _pick(rng, difficulty, [10, 20, 25], [14, 18, 32, 45])
    claimed = round(cp * (1 + profit / 100), 2)

    def answer_fn(cp=cp, profit=profit):
        # Recover SP from the definition of profit percent, not by scaling CP.
        gain = cp * profit / 100
        total = cp
        total += gain
        return round(total, 2)

    stem = (
        f"An article is bought for Rs. {cp} and sold at a profit of {profit}%. "
        f"Find its selling price (in Rs.)."
    )
    solution = (
        f"Profit $= {profit}\\%$ of Rs. {cp} $=$ Rs. ${cp * profit / 100:.2f}$. "
        f"So SP $=$ CP $+$ profit $= {cp} + {cp * profit / 100:.2f} = {claimed}$."
    )
    return _spec(MT_PL, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:profit-loss", "sp-from-cp"], 0.05)


def t_pl_successive_discount(rng: random.Random, difficulty: str) -> ItemSpec:
    d1 = _pick(rng, difficulty, [10, 20, 25], [12, 15, 35])
    d2 = _pick(rng, difficulty, [10, 20, 5], [8, 18, 22])
    claimed = round(100 - (100 - d1) * (100 - d2) / 100, 2)

    def answer_fn(d1=d1, d2=d2):
        # Apply the two discounts to a concrete marked price in sequence.
        mp = 10000.0
        price = mp * (1 - d1 / 100)
        price *= 1 - d2 / 100
        return round((mp - price) / mp * 100, 2)

    stem = (
        f"A shop offers two successive discounts of {d1}% and {d2}% on an item. "
        f"What single discount percentage is equivalent to these two? (Round to 2 decimal places.)"
    )
    solution = (
        f"Take MP $= 100$. After {d1}%: ${100 - d1}$. After a further {d2}%: "
        f"${(100 - d1) * (100 - d2) / 100:.2f}$. The total discount is "
        f"$100 - {(100 - d1) * (100 - d2) / 100:.2f} = {claimed}\\%$."
    )
    alt = (
        f"Equivalent discount $= d_1 + d_2 - \\dfrac{{d_1 d_2}}{{100}} = "
        f"{d1} + {d2} - \\dfrac{{{d1 * d2}}}{{100}} = {claimed}\\%$. Note it is **not** ${d1 + d2}\\%$."
    )
    return _spec(MT_PL, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:profit-loss", "successive-discount"], 0.05, alt)


def t_pl_cp_from_mp_discount(rng: random.Random, difficulty: str) -> ItemSpec:
    mp = rng.randrange(600, 5001, 100)
    disc = _pick(rng, difficulty, [10, 20, 25], [15, 28, 36])
    profit = _pick(rng, difficulty, [8, 20, 25], [12, 17, 32])
    sp = mp * (100 - disc) / 100
    claimed = round(sp * 100 / (100 + profit), 2)

    def answer_fn(mp=mp, disc=disc, profit=profit):
        # Root-find the cost price whose profit percent equals the stated one, instead
        # of algebraically dividing SP by (100 + profit)/100 as the solution does.
        sp = mp * (100 - disc) / 100
        return round(_bisect(lambda c: (sp - c) / c * 100 - profit, 0.01, sp), 2)

    stem = (
        f"An article marked at Rs. {mp} is sold at a discount of {disc}%, still yielding a "
        f"profit of {profit}%. Find its cost price (in Rs., rounded to 2 decimal places)."
    )
    solution = (
        f"SP $= {mp} \\times \\dfrac{{{100 - disc}}}{{100}} = {sp:.2f}$. "
        f"Since SP is ${100 + profit}\\%$ of CP, CP $= {sp:.2f} \\times \\dfrac{{100}}{{{100 + profit}}} = {claimed}$."
    )
    return _spec(MT_PL, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:profit-loss", "mp-discount-cp"], 0.05)


def t_pl_same_sp_gain_loss(rng: random.Random, difficulty: str) -> ItemSpec:
    x = _pick(rng, difficulty, [10, 20], [15, 25, 30])
    claimed = round(-(x * x) / 100, 2)

    def answer_fn(x=x):
        # Reconstruct both cost prices from a common SP and compare totals.
        sp = 10000.0
        cp_gain = sp / (1 + x / 100)
        cp_loss = sp / (1 - x / 100)
        total_cp = cp_gain + cp_loss
        total_sp = 2 * sp
        return round((total_sp - total_cp) / total_cp * 100, 2)

    stem = (
        f"A man sells two articles at the same price. On one he gains {x}% and on the other "
        f"he loses {x}%. What is his overall percentage profit or loss on the whole transaction? "
        f"(Enter a negative value for a loss, rounded to 2 decimal places.)"
    )
    solution = (
        f"Let each SP be 10000. Then CP of the first is $\\dfrac{{10000}}{{1 + {x}/100}} = {10000 / (1 + x / 100):.2f}$ "
        f"and CP of the second is $\\dfrac{{10000}}{{1 - {x}/100}} = {10000 / (1 - x / 100):.2f}$. "
        f"Total CP $= {10000 / (1 + x / 100) + 10000 / (1 - x / 100):.2f}$ against a total SP of 20000, "
        f"a net **loss** of ${abs(claimed)}\\%$."
    )
    alt = (
        f"Whenever two items sell at the same price with equal gain and loss percentages, the result "
        f"is always a loss of $\\dfrac{{x^2}}{{100}} = \\dfrac{{{x * x}}}{{100}} = {abs(claimed)}\\%$ — never a break-even."
    )
    return _spec(MT_PL, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:profit-loss", "equal-gain-loss"], 0.05, alt)


def t_pl_target_sp(rng: random.Random, difficulty: str) -> ItemSpec:
    cp = rng.randrange(300, 4001, 100)
    loss = _pick(rng, difficulty, [10, 20, 25], [12, 18, 32])
    target = _pick(rng, difficulty, [10, 20, 25], [15, 28, 35])
    sp_loss = cp * (100 - loss) / 100
    claimed = round(cp * (100 + target) / 100, 2)

    def answer_fn(cp=cp, target=target):
        # Step up from CP in paise until the profit percent matches the target.
        for cand in range(1, 2000001):
            sp = cand / 100
            if abs((sp - cp) / cp * 100 - target) < 1e-6:
                return round(sp, 2)
        return None

    stem = (
        f"By selling an article for Rs. {sp_loss:.2f}, a shopkeeper incurs a loss of {loss}%. "
        f"At what price (in Rs.) should he sell it to make a profit of {target}%?"
    )
    solution = (
        f"A {loss}% loss means SP is ${100 - loss}\\%$ of CP, so CP $= {sp_loss:.2f} \\times "
        f"\\dfrac{{100}}{{{100 - loss}}} = {cp}$. For a {target}% profit, SP $= {cp} \\times "
        f"\\dfrac{{{100 + target}}}{{100}} = {claimed}$."
    )
    return _spec(MT_PL, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:profit-loss", "target-price"], 0.05)


def t_pl_false_weight(rng: random.Random, difficulty: str) -> ItemSpec:
    short = _pick(rng, difficulty, [100, 200, 250], [80, 120, 160])
    weight = 1000 - short
    claimed = round(short / weight * 100, 2)

    def answer_fn(weight=weight):
        # Price him out in rupees-per-gram rather than using the shortfall ratio.
        cost_per_gram = 1.0
        revenue = 1000 * cost_per_gram   # he charges for a full kilogram
        cost = weight * cost_per_gram    # but only hands over `weight` grams
        return round((revenue - cost) / cost * 100, 2)

    stem = (
        f"A dishonest shopkeeper claims to sell his goods at cost price, but uses a weight of "
        f"{weight} g in place of 1 kg. Find his percentage gain. (Round to 2 decimal places.)"
    )
    solution = (
        f"He charges for 1000 g but delivers {weight} g, so on goods costing him Rs. {weight} "
        f"(at Rs. 1 per gram) he collects Rs. 1000. His gain is Rs. {short} on a cost of Rs. {weight}, "
        f"i.e. $\\dfrac{{{short}}}{{{weight}}} \\times 100 = {claimed}\\%$."
    )
    alt = (
        f"Formula: gain $\\% = \\dfrac{{\\text{{error}}}}{{\\text{{true weight}} - \\text{{error}}}} \\times 100 = "
        f"\\dfrac{{{short}}}{{{weight}}} \\times 100 = {claimed}\\%$. The denominator is what he actually gives, not 1000."
    )
    return _spec(MT_PL, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:profit-loss", "false-weight"], 0.05, alt)


# ---------------------------------------------------------------------------
# qa.arith.si-ci-instalments
# ---------------------------------------------------------------------------

MT_SICI = "qa.arith.si-ci-instalments"


def t_si_basic(rng: random.Random, difficulty: str) -> ItemSpec:
    p = rng.randrange(2000, 30001, 500)
    r = _pick(rng, difficulty, [5, 8, 10, 12], [6.5, 7.5, 9.5, 11.25])
    t = _pick(rng, difficulty, [2, 3, 4], [5, 6, 7])
    claimed = round(p * r * t / 100, 2)

    def answer_fn(p=p, r=r, t=t):
        # Accrue one year at a time instead of using PRT/100.
        interest = 0.0
        for _ in range(t):
            interest += p * r / 100
        return round(interest, 2)

    stem = (
        f"Find the simple interest (in Rs.) on a principal of Rs. {p} at {r}% per annum "
        f"for {t} years."
    )
    solution = (
        f"$SI = \\dfrac{{P \\times R \\times T}}{{100}} = \\dfrac{{{p} \\times {r} \\times {t}}}{{100}} = {claimed}$."
    )
    return _spec(MT_SICI, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:si-ci", "simple-interest"], 0.05)


def t_ci_amount(rng: random.Random, difficulty: str) -> ItemSpec:
    p = rng.randrange(2000, 25001, 1000)
    r = _pick(rng, difficulty, [10, 20, 5], [8, 12, 15])
    t = _pick(rng, difficulty, [2], [3])
    claimed = round(p * (1 + r / 100) ** t, 2)

    def answer_fn(p=p, r=r, t=t):
        # Compound year by year — the exponent never appears.
        amount = float(p)
        for _ in range(t):
            amount += amount * r / 100
        return round(amount, 2)

    stem = (
        f"Find the amount (in Rs.) when Rs. {p} is invested at {r}% per annum compound interest, "
        f"compounded annually, for {t} years. (Round to 2 decimal places.)"
    )
    rows = []
    running = float(p)
    for y in range(1, t + 1):
        running *= 1 + r / 100
        rows.append(f"end of year {y}: ${running:.2f}$")
    solution = "Interest is added to the principal each year — " + ", ".join(rows) + f". Amount $= {claimed}$."
    alt = f"$A = P\\left(1 + \\dfrac{{R}}{{100}}\\right)^T = {p}\\left(1 + \\dfrac{{{r}}}{{100}}\\right)^{{{t}}} = {claimed}$."
    return _spec(MT_SICI, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:si-ci", "compound-interest"], 0.05, alt)


def t_ci_minus_si(rng: random.Random, difficulty: str) -> ItemSpec:
    p = rng.randrange(5000, 40001, 1000)
    r = _pick(rng, difficulty, [10, 20, 5], [8, 12, 15])
    claimed = round(p * (r / 100) ** 2, 2)

    def answer_fn(p=p, r=r):
        # Compute both interests independently and subtract, rather than using P(R/100)^2.
        ci_amount = float(p)
        for _ in range(2):
            ci_amount += ci_amount * r / 100
        ci = ci_amount - p
        si = p * r * 2 / 100
        return round(ci - si, 2)

    stem = (
        f"Find the difference (in Rs.) between the compound interest and the simple interest on "
        f"Rs. {p} at {r}% per annum for 2 years. (Round to 2 decimal places.)"
    )
    ci_amt = p * (1 + r / 100) ** 2
    solution = (
        f"CI: the amount after 2 years is ${ci_amt:.2f}$, so CI $= {ci_amt - p:.2f}$. "
        f"SI $= \\dfrac{{{p} \\times {r} \\times 2}}{{100}} = {p * r * 2 / 100:.2f}$. "
        f"The difference is ${claimed}$."
    )
    alt = (
        f"For 2 years the gap is always the interest earned on the first year's interest: "
        f"$P\\left(\\dfrac{{R}}{{100}}\\right)^2 = {p} \\times \\left(\\dfrac{{{r}}}{{100}}\\right)^2 = {claimed}$."
    )
    return _spec(MT_SICI, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:si-ci", "ci-si-difference"], 0.05, alt)


def t_si_rate_from_multiple(rng: random.Random, difficulty: str) -> ItemSpec:
    multiple = _pick(rng, difficulty, [2, 3], [4, 5])
    years = _pick(rng, difficulty, [5, 10, 20], [8, 16, 12])
    claimed = round((multiple - 1) * 100 / years, 2)

    def answer_fn(multiple=multiple, years=years):
        # Root-find the rate that grows 100 into 100*multiple under simple interest.
        principal = 100.0
        target = principal * multiple
        return round(
            _bisect(lambda r: principal + principal * r * years / 100 - target, 0.0, 1000.0), 2
        )

    stem = (
        f"At what rate percent per annum of simple interest will a sum of money become "
        f"{multiple} times itself in {years} years? (Round to 2 decimal places.)"
    )
    solution = (
        f"To become {multiple} times itself, the interest earned must be ${multiple - 1}$ times the principal. "
        f"So $\\dfrac{{P \\times R \\times {years}}}{{100}} = {multiple - 1}P$, giving "
        f"$R = \\dfrac{{{multiple - 1} \\times 100}}{{{years}}} = {claimed}\\%$."
    )
    return _spec(MT_SICI, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:si-ci", "rate-from-multiple"], 0.05)


def t_ci_half_yearly(rng: random.Random, difficulty: str) -> ItemSpec:
    p = rng.randrange(4000, 30001, 2000)
    r = _pick(rng, difficulty, [10, 20], [8, 12, 15])
    years = 1
    periods = 2 * years
    claimed = round(p * (1 + r / 200) ** periods, 2)

    def answer_fn(p=p, r=r, periods=periods):
        # Step through each half-year explicitly.
        amount = float(p)
        for _ in range(periods):
            amount += amount * (r / 2) / 100
        return round(amount, 2)

    stem = (
        f"Find the amount (in Rs.) when Rs. {p} is invested for {years} year at {r}% per annum "
        f"compound interest, compounded half-yearly. (Round to 2 decimal places.)"
    )
    solution = (
        f"Half-yearly compounding halves the rate and doubles the periods: {r / 2}% for {periods} periods. "
        f"$A = {p}\\left(1 + \\dfrac{{{r / 2}}}{{100}}\\right)^{{{periods}}} = {claimed}$."
    )
    alt = (
        f"Compounding more often beats annual compounding: at {r}% compounded annually the amount "
        f"would only be ${p * (1 + r / 100):.2f}$."
    )
    return _spec(MT_SICI, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:si-ci", "half-yearly"], 0.05, alt)


# ---------------------------------------------------------------------------
# qa.arith.averages-weighted-averages
# ---------------------------------------------------------------------------

MT_AVG = "qa.arith.averages-weighted-averages"


def t_avg_replacement(rng: random.Random, difficulty: str) -> ItemSpec:
    n = _pick(rng, difficulty, [8, 10, 12], [9, 11, 15])
    old_avg = rng.randrange(20, 61)
    change = _pick(rng, difficulty, [2, 3, 5], [1.5, 2.5, 4])
    claimed = round(n * change, 2)

    def answer_fn(n=n, old_avg=old_avg, change=change):
        # Build an explicit list, swap one member, and read off the difference.
        people = [float(old_avg)] * n
        old_total = sum(people)
        new_total = old_total + n * change
        return round(new_total - old_total, 2)

    stem = (
        f"The average weight of {n} students increases by {change} kg when a new student "
        f"replaces one weighing {old_avg} kg. What is the weight (in kg) of the new student?"
    )
    claimed_weight = round(old_avg + n * change, 2)

    def answer_fn2(n=n, old_avg=old_avg, change=change):
        people = [float(old_avg)] * n
        target_avg = sum(people) / n + change
        people[0] = 0.0
        # solve for the replacement that lifts the mean to target_avg
        needed = target_avg * n - sum(people)
        return round(needed, 2)

    solution = (
        f"The total weight rises by ${n} \\times {change} = {n * change}$ kg. That entire increase "
        f"comes from one swap, so the new student is ${n * change}$ kg heavier than the one who left: "
        f"${old_avg} + {n * change} = {claimed_weight}$ kg."
    )
    return _spec(MT_AVG, difficulty, stem, solution, answer_fn2, claimed_weight,
                 ["arith:averages", "replacement"], 0.05)


def t_avg_weighted_two_groups(rng: random.Random, difficulty: str) -> ItemSpec:
    n1 = _pick(rng, difficulty, [20, 25, 30], [18, 22, 27])
    n2 = _pick(rng, difficulty, [10, 15, 20], [13, 17, 23])
    a1 = rng.randrange(50, 81)
    a2 = rng.randrange(30, 50)
    claimed = round((n1 * a1 + n2 * a2) / (n1 + n2), 2)

    def answer_fn(n1=n1, n2=n2, a1=a1, a2=a2):
        # Expand into an explicit population and take the plain mean.
        values = [float(a1)] * n1 + [float(a2)] * n2
        return round(sum(values) / len(values), 2)

    stem = (
        f"In a class, {n1} boys have an average score of {a1} and {n2} girls have an average "
        f"score of {a2}. What is the average score of the whole class? (Round to 2 decimal places.)"
    )
    solution = (
        f"Total score $= {n1} \\times {a1} + {n2} \\times {a2} = {n1 * a1 + n2 * a2}$ across "
        f"${n1 + n2}$ students, so the average is $\\dfrac{{{n1 * a1 + n2 * a2}}}{{{n1 + n2}}} = {claimed}$."
    )
    alt = (
        f"The combined average must lie between {a2} and {a1}, closer to whichever group is larger — "
        f"a useful sanity check before computing."
    )
    return _spec(MT_AVG, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:averages", "weighted"], 0.05, alt)


def t_avg_consecutive(rng: random.Random, difficulty: str) -> ItemSpec:
    count = _pick(rng, difficulty, [5, 7, 9], [6, 8, 12])
    start = rng.randrange(11, 200)
    numbers = list(range(start, start + count))
    claimed = round(sum(numbers) / count, 2)

    def answer_fn(numbers=numbers):
        # Plain mean of the explicit list — no first/last shortcut.
        return round(sum(numbers) / len(numbers), 2)

    stem = (
        f"Find the average of {count} consecutive integers starting from {start}. "
        f"(Round to 2 decimal places.)"
    )
    solution = (
        f"The numbers run from ${start}$ to ${start + count - 1}$. For an evenly spaced list the "
        f"average is the midpoint of the first and last terms: "
        f"$\\dfrac{{{start} + {start + count - 1}}}{{2}} = {claimed}$."
    )
    return _spec(MT_AVG, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:averages", "consecutive"], 0.05)


def t_avg_wrong_reading(rng: random.Random, difficulty: str) -> ItemSpec:
    n = _pick(rng, difficulty, [10, 20, 25], [15, 18, 24])
    wrong_avg = rng.randrange(30, 81)
    misread_as = rng.randrange(20, 61)
    actual = misread_as + _pick(rng, difficulty, [10, 20, 30], [14, 26, 33])
    claimed = round(wrong_avg + (actual - misread_as) / n, 2)

    def answer_fn(n=n, wrong_avg=wrong_avg, misread_as=misread_as, actual=actual):
        # Rebuild the dataset, correct the one bad entry, re-average from scratch.
        values = [float(wrong_avg)] * n
        values[0] = values[0] - misread_as + misread_as  # keep the list explicit
        wrong_total = sum(values)
        corrected_total = wrong_total - misread_as + actual
        return round(corrected_total / n, 2)

    stem = (
        f"The average of {n} observations was calculated as {wrong_avg}, but one observation was "
        f"wrongly read as {misread_as} instead of the correct value {actual}. What is the correct "
        f"average? (Round to 2 decimal places.)"
    )
    solution = (
        f"The recorded total was ${n} \\times {wrong_avg} = {n * wrong_avg}$. Correcting the single "
        f"entry changes it by ${actual} - {misread_as} = {actual - misread_as}$, giving a true total of "
        f"${n * wrong_avg + actual - misread_as}$. The correct average is "
        f"$\\dfrac{{{n * wrong_avg + actual - misread_as}}}{{{n}}} = {claimed}$."
    )
    return _spec(MT_AVG, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:averages", "correction"], 0.05)


def t_avg_excluding_member(rng: random.Random, difficulty: str) -> ItemSpec:
    n = _pick(rng, difficulty, [11, 15, 12], [13, 17, 19])
    team_avg = rng.randrange(20, 41)
    captain_extra = _pick(rng, difficulty, [10, 15, 20], [12, 18, 26])
    captain_age = team_avg + captain_extra
    total = n * team_avg
    rest_avg = (total - captain_age) / (n - 1)
    claimed = round(rest_avg, 2)

    def answer_fn(n=n, team_avg=team_avg, captain_age=captain_age):
        # Remove the captain from an explicit roster and re-average the remainder.
        roster = [float(team_avg)] * n
        total = sum(roster)
        remaining_total = total - captain_age
        return round(remaining_total / (n - 1), 2)

    stem = (
        f"The average age of a team of {n} members is {team_avg} years. If the captain is "
        f"{captain_age} years old, what is the average age (in years) of the remaining members? "
        f"(Round to 2 decimal places.)"
    )
    solution = (
        f"Total age $= {n} \\times {team_avg} = {total}$. Excluding the captain leaves "
        f"${total} - {captain_age} = {total - captain_age}$ years across ${n - 1}$ members, "
        f"so the average is $\\dfrac{{{total - captain_age}}}{{{n - 1}}} = {claimed}$."
    )
    return _spec(MT_AVG, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:averages", "exclusion"], 0.05)


# ---------------------------------------------------------------------------
# qa.arith.ratio-proportion-variation
# ---------------------------------------------------------------------------

MT_RATIO = "qa.arith.ratio-proportion-variation"


def t_ratio_divide_amount(rng: random.Random, difficulty: str) -> ItemSpec:
    a, b, c = (rng.randrange(2, 8), rng.randrange(2, 8), rng.randrange(2, 8))
    unit = rng.randrange(200, 2001, 100)
    total = (a + b + c) * unit
    largest = max(a, b, c)
    claimed = largest * unit

    def answer_fn(a=a, b=b, c=c, total=total):
        # Distribute the money share by share instead of using the parts formula.
        parts = [a, b, c]
        per_part = total / sum(parts)
        shares = [p * per_part for p in parts]
        return round(max(shares), 2)

    stem = (
        f"Rs. {total} is divided among three people in the ratio {a} : {b} : {c}. "
        f"What is the largest share (in Rs.)?"
    )
    solution = (
        f"There are ${a} + {b} + {c} = {a + b + c}$ equal parts, so one part is "
        f"$\\dfrac{{{total}}}{{{a + b + c}}} = {unit}$. The largest share is ${largest}$ parts "
        f"$= {largest} \\times {unit} = {claimed}$."
    )
    return _spec(MT_RATIO, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:ratio", "division"], 0.05)


def t_ratio_ages(rng: random.Random, difficulty: str) -> ItemSpec:
    k = rng.randrange(3, 12)
    a, b = 3, 5
    years = _pick(rng, difficulty, [4, 5, 6], [7, 9, 11])
    age_a, age_b = a * k, b * k
    fut_a, fut_b = age_a + years, age_b + years
    claimed = age_a

    def answer_fn(fut_a=fut_a, fut_b=fut_b, years=years, a=a, b=b):
        # Search present ages consistent with both the current and future ratios.
        for cand in range(1, 2001):
            other = cand * b / a
            if abs((cand + years) * fut_b - (other + years) * fut_a) < 1e-9 and abs(other - round(other)) < 1e-9:
                return cand
        return None

    stem = (
        f"The present ages of A and B are in the ratio {a} : {b}. After {years} years, their ages "
        f"will be in the ratio {fut_a} : {fut_b}. What is A's present age (in years)?"
    )
    solution = (
        f"Let the present ages be ${a}x$ and ${b}x$. Then "
        f"$\\dfrac{{{a}x + {years}}}{{{b}x + {years}}} = \\dfrac{{{fut_a}}}{{{fut_b}}}$. "
        f"Cross-multiplying and solving gives $x = {k}$, so A is ${a} \\times {k} = {claimed}$ years old."
    )
    return _spec(MT_RATIO, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:ratio", "ages"], 0.01)


def t_ratio_compound(rng: random.Random, difficulty: str) -> ItemSpec:
    a, b = rng.randrange(2, 9), rng.randrange(2, 9)
    c, d = rng.randrange(2, 9), rng.randrange(2, 9)
    # a:b and b:c given as a:b = a:b and b:c = c:d -> chain them
    claimed = round((a / b) * (c / d), 4)

    def answer_fn(a=a, b=b, c=c, d=d):
        # Assign a concrete value to the shared middle term and measure the end ratio.
        y = float(b * d)          # divisible by both b and d
        x = y * a / b
        z = y * d / c
        return round(x / z, 4)

    stem = (
        f"If $A : B = {a} : {b}$ and $B : C = {c} : {d}$, find the value of $A : C$ as a decimal. "
        f"(Round to 4 decimal places.)"
    )
    solution = (
        f"Scale $B$ to a common value. $A : C = \\dfrac{{A}}{{B}} \\times \\dfrac{{B}}{{C}} = "
        f"\\dfrac{{{a}}}{{{b}}} \\times \\dfrac{{{c}}}{{{d}}} = {claimed}$."
    )
    return _spec(MT_RATIO, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:ratio", "compound-ratio"], 0.001)


def t_ratio_inverse_variation(rng: random.Random, difficulty: str) -> ItemSpec:
    men1 = _pick(rng, difficulty, [12, 15, 20], [14, 18, 27])
    days1 = _pick(rng, difficulty, [10, 12, 20], [11, 16, 21])
    men2 = _pick(rng, difficulty, [6, 10, 24], [7, 9, 30])
    claimed = round(men1 * days1 / men2, 2)

    def answer_fn(men1=men1, days1=days1, men2=men2):
        # Work in man-days: total effort is fixed, so divide it by the new crew size.
        total_effort = men1 * days1
        return round(total_effort / men2, 2)

    stem = (
        f"If {men1} workers can complete a job in {days1} days, how many days will {men2} workers "
        f"take to complete the same job, working at the same rate? (Round to 2 decimal places.)"
    )
    solution = (
        f"The job needs ${men1} \\times {days1} = {men1 * days1}$ worker-days. With {men2} workers "
        f"that takes $\\dfrac{{{men1 * days1}}}{{{men2}}} = {claimed}$ days. Workers and days vary inversely."
    )
    return _spec(MT_RATIO, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:ratio", "inverse-variation"], 0.05)


def t_ratio_add_constant(rng: random.Random, difficulty: str) -> ItemSpec:
    k = rng.randrange(2, 15)
    a, b = 2, 3
    add = _pick(rng, difficulty, [4, 6, 8], [5, 7, 11])
    x, y = a * k, b * k
    nx, ny = x + add, y + add
    claimed = x

    def answer_fn(a=a, b=b, add=add, nx=nx, ny=ny):
        # Search the multiplier that satisfies the post-addition ratio.
        for cand in range(1, 2001):
            p, q = a * cand, b * cand
            if abs((p + add) * ny - (q + add) * nx) < 1e-9:
                return p
        return None

    stem = (
        f"Two numbers are in the ratio {a} : {b}. When {add} is added to each, the ratio becomes "
        f"{nx} : {ny}. Find the smaller of the two original numbers."
    )
    solution = (
        f"Let the numbers be ${a}x$ and ${b}x$. Then "
        f"$\\dfrac{{{a}x + {add}}}{{{b}x + {add}}} = \\dfrac{{{nx}}}{{{ny}}}$, which solves to $x = {k}$. "
        f"The smaller number is ${a} \\times {k} = {claimed}$."
    )
    return _spec(MT_RATIO, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:ratio", "ratio-shift"], 0.01)


# ---------------------------------------------------------------------------
# qa.arith.mixtures-alligation
# ---------------------------------------------------------------------------

MT_MIX = "qa.arith.mixtures-alligation"


def t_mix_blend_two(rng: random.Random, difficulty: str) -> ItemSpec:
    v1 = _pick(rng, difficulty, [20, 30, 40], [25, 35, 45])
    c1 = _pick(rng, difficulty, [20, 25, 40], [18, 32, 46])
    v2 = _pick(rng, difficulty, [10, 20, 60], [15, 28, 55])
    c2 = _pick(rng, difficulty, [50, 60, 10], [42, 58, 12])
    claimed = round((v1 * c1 + v2 * c2) / (v1 + v2), 2)

    def answer_fn(v1=v1, c1=c1, v2=v2, c2=c2):
        # Track litres of pure acid explicitly, then re-derive the percentage.
        acid = v1 * c1 / 100 + v2 * c2 / 100
        volume = v1 + v2
        return round(acid / volume * 100, 2)

    stem = (
        f"{v1} litres of a {c1}% acid solution is mixed with {v2} litres of a {c2}% acid solution. "
        f"What is the acid concentration (in %) of the resulting mixture? (Round to 2 decimal places.)"
    )
    solution = (
        f"Acid from the first: ${v1 * c1 / 100:.2f}$ L. From the second: ${v2 * c2 / 100:.2f}$ L. "
        f"Total acid $= {v1 * c1 / 100 + v2 * c2 / 100:.2f}$ L in ${v1 + v2}$ L of mixture, so the "
        f"concentration is ${claimed}\\%$."
    )
    return _spec(MT_MIX, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:mixtures", "blending"], 0.05)


def t_mix_replacement(rng: random.Random, difficulty: str) -> ItemSpec:
    total = _pick(rng, difficulty, [40, 50, 80], [45, 60, 75])
    drawn = _pick(rng, difficulty, [8, 10, 20], [9, 12, 15])
    times = _pick(rng, difficulty, [2], [3])
    claimed = round(total * ((total - drawn) / total) ** times, 2)

    def answer_fn(total=total, drawn=drawn, times=times):
        # Simulate each draw-and-replace round on the actual litres of milk.
        milk = float(total)
        for _ in range(times):
            milk -= milk * drawn / total   # the portion removed is milk in proportion
        return round(milk, 2)

    stem = (
        f"A vessel contains {total} litres of pure milk. {drawn} litres are drawn out and replaced "
        f"with water. This operation is repeated {times} times in total. How many litres of milk "
        f"remain in the vessel? (Round to 2 decimal places.)"
    )
    solution = (
        f"Each operation leaves $\\dfrac{{{total - drawn}}}{{{total}}}$ of the milk behind. After "
        f"{times} operations the milk left is "
        f"${total} \\times \\left(\\dfrac{{{total - drawn}}}{{{total}}}\\right)^{{{times}}} = {claimed}$ litres."
    )
    alt = (
        f"General rule: milk remaining $= V\\left(1 - \\dfrac{{x}}{{V}}\\right)^n$. The water added never "
        f"changes the vessel's volume, which is why the same fraction applies every round."
    )
    return _spec(MT_MIX, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:mixtures", "replacement"], 0.05, alt)


def t_mix_alligation_ratio(rng: random.Random, difficulty: str) -> ItemSpec:
    cheap = _pick(rng, difficulty, [20, 30, 40], [24, 34, 46])
    dear = cheap + _pick(rng, difficulty, [20, 30, 40], [26, 36, 44])
    mean = (cheap + dear) // 2 + _pick(rng, difficulty, [0, 2], [3, 5])
    if not (cheap < mean < dear):
        mean = (cheap + dear) // 2
    claimed = round((dear - mean) / (mean - cheap), 4)

    def answer_fn(cheap=cheap, dear=dear, mean=mean):
        # Root-find the blend ratio that lands on the target price, rather than using
        # the alligation cross the solution quotes.
        def cost_gap(r):
            return (r * cheap + dear) / (r + 1) - mean

        return round(_bisect(cost_gap, 0.0, 10000.0), 4)

    stem = (
        f"In what ratio must rice costing Rs. {cheap} per kg be mixed with rice costing Rs. {dear} "
        f"per kg so that the mixture costs Rs. {mean} per kg? Give the answer as the ratio "
        f"(cheaper : dearer) expressed as a decimal, rounded to 4 decimal places."
    )
    solution = (
        f"By alligation, the ratio of quantities is the ratio of the opposite differences: "
        f"$\\dfrac{{\\text{{dear}} - \\text{{mean}}}}{{\\text{{mean}} - \\text{{cheap}}}} = "
        f"\\dfrac{{{dear} - {mean}}}{{{mean} - {cheap}}} = \\dfrac{{{dear - mean}}}{{{mean - cheap}}} = {claimed}$."
    )
    return _spec(MT_MIX, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:mixtures", "alligation"], 0.001)


def t_mix_add_water(rng: random.Random, difficulty: str) -> ItemSpec:
    volume = _pick(rng, difficulty, [40, 60, 80], [45, 55, 75])
    conc = _pick(rng, difficulty, [50, 40, 25], [36, 44, 62])
    target = _pick(rng, difficulty, [20, 25, 10], [15, 22, 30])
    if target >= conc:
        target = max(5, conc // 2)
    acid = volume * conc / 100
    new_volume = acid * 100 / target
    claimed = round(new_volume - volume, 2)

    def answer_fn(volume=volume, conc=conc, target=target):
        # Root-find how much water drives the strength down to target, rather than
        # rearranging for the final volume as the solution does.
        acid = volume * conc / 100
        return round(_bisect(lambda w: acid / (volume + w) * 100 - target, 0.0, 100000.0), 2)

    stem = (
        f"A {volume}-litre solution contains {conc}% acid. How many litres of water must be added "
        f"to dilute it to a {target}% acid solution? (Round to 2 decimal places.)"
    )
    solution = (
        f"The acid stays fixed at ${acid:.2f}$ litres. For that to be ${target}\\%$ of the solution, "
        f"the total volume must become $\\dfrac{{{acid:.2f} \\times 100}}{{{target}}} = {new_volume:.2f}$ litres. "
        f"Water to add $= {new_volume:.2f} - {volume} = {claimed}$ litres."
    )
    alt = "Only the solvent changes — anchoring on the unchanged solute is what makes these quick."
    return _spec(MT_MIX, difficulty, stem, solution, answer_fn, claimed,
                 ["arith:mixtures", "dilution"], 0.05, alt)


# ---------------------------------------------------------------------------
# registry
# ---------------------------------------------------------------------------

TEMPLATES = {
    MT_PCT: [
        t_pct_successive, t_pct_find_original, t_pct_more_less, t_pct_expenditure,
        t_pct_passing_marks, t_pct_compound_growth, t_pct_area_change,
    ],
    MT_PL: [
        t_pl_sp_from_profit, t_pl_successive_discount, t_pl_cp_from_mp_discount,
        t_pl_same_sp_gain_loss, t_pl_target_sp, t_pl_false_weight,
    ],
    MT_SICI: [
        t_si_basic, t_ci_amount, t_ci_minus_si, t_si_rate_from_multiple, t_ci_half_yearly,
    ],
    MT_AVG: [
        t_avg_replacement, t_avg_weighted_two_groups, t_avg_consecutive,
        t_avg_wrong_reading, t_avg_excluding_member,
    ],
    MT_RATIO: [
        t_ratio_divide_amount, t_ratio_ages, t_ratio_compound,
        t_ratio_inverse_variation, t_ratio_add_constant,
    ],
    MT_MIX: [
        t_mix_blend_two, t_mix_replacement, t_mix_alligation_ratio, t_mix_add_water,
    ],
}
