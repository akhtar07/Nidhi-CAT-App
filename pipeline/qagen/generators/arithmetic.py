from __future__ import annotations

import random
from fractions import Fraction
from math import gcd

from qagen.harness import ItemSpec, mcq_options_from_distractors
from qagen.syllabus_lookup import item_count, target_seconds

DIFF_CYCLE = ["easy", "easy", "medium", "medium", "medium", "hard", "hard", "very_hard"]


def _diffs(n: int) -> list[str]:
    return [DIFF_CYCLE[i % len(DIFF_CYCLE)] for i in range(n)]


def gen_percentages() -> list[ItemSpec]:
    mt = "qa.arith.percentages"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        p1, p2 = rng.randint(5, 50), rng.randint(5, 50)
        ratio = Fraction(100 + p1, 100) * Fraction(100 - p2, 100)
        net = round(float(ratio - 1) * 100, 2)
        stem = (
            f"The price of an article is first increased by {p1}%, and then the new "
            f"price is decreased by {p2}%. What is the net percentage change in price? "
            f"(Enter a negative value if it is a net decrease.)"
        )
        mid = 100 * (1 + p1 / 100)
        end = mid * (1 - p2 / 100)
        solution = (
            f"Take the original price as 100. After a {p1}% increase: "
            f"$100 \\times (1 + {p1}/100) = {mid:.2f}$. "
            f"After a {p2}% decrease on {mid:.2f}: "
            f"${mid:.2f} \\times (1 - {p2}/100) = {end:.2f}$. "
            f"Net change $= {end:.2f} - 100 = {net:.2f}\\%$."
        )
        alt = (
            f"Shortcut formula: net \\% change $= p_1 - p_2 - \\dfrac{{p_1 p_2}}{{100}} "
            f"= {p1} - {p2} - \\dfrac{{{p1 * p2}}}{{100}} = {net:.2f}\\%$."
        )

        def answer_fn(p1=p1, p2=p2):
            # Independent of the closed-form Fraction formula above: simulate
            # the two operations sequentially in floating point.
            price = 100.0
            price *= 1 + p1 / 100
            price *= 1 - p2 / 100
            return round(price - 100, 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            alt_solution=alt, answer_fn=answer_fn, claimed_value=net,
            target_seconds=target_seconds(mt), tags=["arith:percentages", "successive-change"],
            format="tita", tita_tolerance=0.05,
        ))
    return specs


def gen_profit_loss_discount() -> list[ItemSpec]:
    mt = "qa.arith.profit-loss-discount"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        markup = rng.randint(20, 80)
        discount = rng.randint(5, 40)
        ratio = Fraction(100 + markup, 100) * Fraction(100 - discount, 100)
        pct = round(float(ratio - 1) * 100, 2)
        label = "profit" if pct >= 0 else "loss"
        stem = (
            f"A shopkeeper marks up an article by {markup}% above its cost price, then "
            f"sells it at a discount of {discount}% on the marked price. Find his "
            f"profit or loss percent. (Enter a negative number for a loss.)"
        )
        mp = 100 * (1 + markup / 100)
        sp = mp * (1 - discount / 100)
        solution = (
            f"Let cost price $= 100$. Marked price $= 100(1+{markup}/100) = {mp:.2f}$. "
            f"Selling price $= {mp:.2f}(1-{discount}/100) = {sp:.2f}$. "
            f"{label.capitalize()} \\% $= {sp:.2f} - 100 = {pct:.2f}\\%$."
        )

        def answer_fn(markup=markup, discount=discount):
            cp = 100.0
            mp_ = cp * (1 + markup / 100)
            sp_ = mp_ * (1 - discount / 100)
            return round(sp_ - cp, 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=pct, target_seconds=target_seconds(mt),
            tags=["arith:profit-loss-discount"], format="tita", tita_tolerance=0.05,
        ))
    return specs


def gen_si_ci_instalments() -> list[ItemSpec]:
    mt = "qa.arith.si-ci-instalments"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        p = rng.choice([1000, 2000, 4000, 5000, 8000, 10000])
        r = rng.choice([5, 8, 10, 12, 15, 20])
        si = Fraction(p * r * 2, 100)
        ci = p * (Fraction(100 + r, 100) ** 2 - 1)
        diff = ci - si
        diff_val = round(float(diff), 2)
        stem = (
            f"Find the difference between the compound interest and the simple "
            f"interest on ₹{p} for 2 years at {r}% per annum (interest compounded "
            f"annually)."
        )
        solution = (
            f"SI for 2 years $= \\dfrac{{P \\times r \\times t}}{{100}} = "
            f"\\dfrac{{{p} \\times {r} \\times 2}}{{100}} = {float(si):.2f}$. "
            f"CI for 2 years $= P\\left[(1+r/100)^2 - 1\\right] = "
            f"{p}\\left[(1+{r}/100)^2 - 1\\right] = {float(ci):.2f}$. "
            f"Difference $= {float(ci):.2f} - {float(si):.2f} = {diff_val:.2f}$."
        )
        alt = f"Shortcut: for 2 years, CI $-$ SI $= P(r/100)^2 = {p}({r}/100)^2 = {diff_val:.2f}$."

        def answer_fn(p=p, r=r):
            si_ = Fraction(p * r * 2, 100)
            ci_ = p * (Fraction(100 + r, 100) ** 2 - 1)
            return round(float(ci_ - si_), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            alt_solution=alt, answer_fn=answer_fn, claimed_value=diff_val,
            target_seconds=target_seconds(mt), tags=["arith:ci-si"], format="tita",
            tita_tolerance=0.5,
        ))
    return specs


def gen_ratio_proportion_variation() -> list[ItemSpec]:
    mt = "qa.arith.ratio-proportion-variation"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        a, b = rng.randint(2, 9), rng.randint(2, 9)
        while gcd(a, b) != 1:
            a, b = rng.randint(2, 9), rng.randint(2, 9)
        k = rng.randint(3, 20)
        total = (a + b) * k
        larger = max(a, b) * k
        smaller = min(a, b) * k
        stem = (
            f"Two numbers are in the ratio {a}:{b}. If their sum is {total}, find the "
            f"larger of the two numbers."
        )
        solution = (
            f"Let the numbers be ${a}x$ and ${b}x$. Then ${a}x + {b}x = {total} "
            f"\\Rightarrow x = {k}$. The larger number is "
            f"${max(a, b)} \\times {k} = {larger}$."
        )
        distractors = sorted({smaller, total, larger + k, max(1, larger - k)} - {larger})[:3]
        while len(distractors) < 3:
            distractors.append(larger + len(distractors) + 1)

        def answer_fn(a=a, b=b, total=total):
            x = Fraction(total, a + b)
            return int(max(a, b) * x)

        options, correct_key = mcq_options_from_distractors(
            str(larger), [str(d) for d in distractors], rng
        )
        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=larger, target_seconds=target_seconds(mt),
            tags=["arith:ratio-proportion"], format="mcq", options=options,
            correct_key=correct_key,
        ))
    return specs


def gen_mixtures_alligation() -> list[ItemSpec]:
    mt = "qa.arith.mixtures-alligation"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        x = rng.randint(10, 40)  # cheaper concentration %
        y = rng.randint(x + 15, 95)  # dearer concentration %
        z = rng.randint(x + 5, y - 5)  # mixture concentration %
        r1, r2 = y - z, z - x
        g = gcd(r1, r2)
        r1s, r2s = r1 // g, r2 // g
        stem = (
            f"In what ratio must a solution containing {x}% acid be mixed with a "
            f"solution containing {y}% acid to obtain a mixture that is {z}% acid? "
            f"Give the ratio (cheaper : dearer) in simplest form, e.g. '3:2'."
        )
        solution = (
            f"By alligation: $\\dfrac{{\\text{{cheaper}}}}{{\\text{{dearer}}}} = "
            f"\\dfrac{{y - z}}{{z - x}} = \\dfrac{{{y} - {z}}}{{{z} - {x}}} = "
            f"\\dfrac{{{r1}}}{{{r2}}} = {r1s}:{r2s}$ (after simplifying by "
            f"dividing both terms by {g})."
        )
        claimed = f"{r1s}:{r2s}"

        def answer_fn(x=x, y=y, z=z):
            r1_, r2_ = y - z, z - x
            g_ = gcd(r1_, r2_)
            return f"{r1_ // g_}:{r2_ // g_}"

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=claimed, target_seconds=target_seconds(mt),
            tags=["arith:alligation"], format="tita", tita_tolerance=0,
        ))
    return specs


def gen_averages_weighted_averages() -> list[ItemSpec]:
    mt = "qa.arith.averages-weighted-averages"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        num = rng.randint(5, 20)
        avg = rng.randint(20, 80)
        new_val = rng.randint(1, 150)
        new_avg = Fraction(num * avg + new_val, num + 1)
        new_avg_f = round(float(new_avg), 2)
        stem = (
            f"The average of {num} numbers is {avg}. When one more number is "
            f"included, the average becomes the sum of all {num + 1} numbers divided "
            f"by {num + 1}. If the new number added is {new_val}, find the new "
            f"average (rounded to 2 decimal places)."
        )
        solution = (
            f"Sum of original {num} numbers $= {num} \\times {avg} = {num * avg}$. "
            f"New sum $= {num * avg} + {new_val} = {num * avg + new_val}$. "
            f"New average $= \\dfrac{{{num * avg + new_val}}}{{{num + 1}}} = "
            f"{new_avg_f:.2f}$."
        )

        def answer_fn(num=num, avg=avg, new_val=new_val):
            return round(float(Fraction(num * avg + new_val, num + 1)), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=new_avg_f, target_seconds=target_seconds(mt),
            tags=["arith:averages"], format="tita", tita_tolerance=0.02,
        ))
    return specs


def gen_tsd_relative_speed() -> list[ItemSpec]:
    mt = "qa.arith.tsd-relative-speed"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        dist = rng.randint(60, 400)
        s1, s2 = rng.randint(20, 60), rng.randint(20, 60)
        t = round(dist / (s1 + s2), 2)
        stem = (
            f"Two cars start at the same time from two points {dist} km apart and "
            f"travel towards each other at {s1} km/h and {s2} km/h respectively. "
            f"After how many hours will they meet? (2 decimal places.)"
        )
        solution = (
            f"Relative speed (approaching) $= {s1} + {s2} = {s1 + s2}$ km/h. "
            f"Time to meet $= \\dfrac{{\\text{{distance}}}}{{\\text{{relative speed}}}} "
            f"= \\dfrac{{{dist}}}{{{s1 + s2}}} = {t:.2f}$ hours."
        )

        def answer_fn(dist=dist, s1=s1, s2=s2):
            return round(dist / (s1 + s2), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=t, target_seconds=target_seconds(mt),
            tags=["arith:tsd", "relative-speed"], format="tita", tita_tolerance=0.02,
        ))
    return specs


def gen_tsd_trains() -> list[ItemSpec]:
    mt = "qa.arith.tsd-trains"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        train_len = rng.randint(100, 250)
        platform_len = rng.randint(100, 300)
        speed_kmh = rng.randint(36, 108)
        speed_ms = Fraction(speed_kmh * 5, 18)
        t = round(float(Fraction(train_len + platform_len) / speed_ms), 2)
        stem = (
            f"A train {train_len} m long crosses a platform {platform_len} m long "
            f"in how many seconds, if the train runs at {speed_kmh} km/h? "
            f"(2 decimal places.)"
        )
        solution = (
            f"Speed in m/s $= {speed_kmh} \\times \\dfrac{{5}}{{18}} = "
            f"{float(speed_ms):.2f}$ m/s. Total distance to cover "
            f"$= {train_len} + {platform_len} = {train_len + platform_len}$ m. "
            f"Time $= \\dfrac{{{train_len + platform_len}}}{{{float(speed_ms):.2f}}} "
            f"= {t:.2f}$ s."
        )

        def answer_fn(train_len=train_len, platform_len=platform_len, speed_kmh=speed_kmh):
            speed_ms_ = Fraction(speed_kmh * 5, 18)
            return round(float(Fraction(train_len + platform_len) / speed_ms_), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=t, target_seconds=target_seconds(mt),
            tags=["arith:tsd", "trains"], format="tita", tita_tolerance=0.05,
        ))
    return specs


def gen_tsd_boats_streams() -> list[ItemSpec]:
    mt = "qa.arith.tsd-boats-streams"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        boat = rng.randint(10, 25)
        stream = rng.randint(2, boat - 3)
        dist = rng.randint(20, 100)
        downstream_speed = boat + stream
        t = round(dist / downstream_speed, 2)
        stem = (
            f"A boat's speed in still water is {boat} km/h and the speed of the "
            f"stream is {stream} km/h. Find the time (in hours) taken by the boat "
            f"to cover {dist} km downstream. (2 decimal places.)"
        )
        solution = (
            f"Downstream speed $= {boat} + {stream} = {downstream_speed}$ km/h. "
            f"Time $= \\dfrac{{{dist}}}{{{downstream_speed}}} = {t:.2f}$ hours."
        )

        def answer_fn(dist=dist, boat=boat, stream=stream):
            return round(dist / (boat + stream), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=t, target_seconds=target_seconds(mt),
            tags=["arith:tsd", "boats-streams"], format="tita", tita_tolerance=0.02,
        ))
    return specs


def gen_tsd_races() -> list[ItemSpec]:
    mt = "qa.arith.tsd-races"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    # Widened from length in {100,200,400,500,1000} x p in [5,9] x q in {3,4}
    # (~50 combos, too narrow to safely draw 10 unique instances) to a much
    # larger combinatorial space so the difficulty cycle reliably reaches
    # hard/very_hard without duplicate-draw collisions.
    lengths = [100, 150, 200, 250, 300, 400, 500, 600, 800, 1000, 1200, 1500]
    for i in range(n):
        length = rng.choice(lengths)
        speed_ratio_p, speed_ratio_q = rng.randint(5, 15), rng.randint(2, 9)
        while gcd(speed_ratio_p, speed_ratio_q) != 1 or speed_ratio_q >= speed_ratio_p:
            speed_ratio_p, speed_ratio_q = rng.randint(5, 15), rng.randint(2, 9)
        margin = round(float(length * (1 - Fraction(speed_ratio_q, speed_ratio_p))), 2)
        stem = (
            f"In a race of {length} m, the ratio of speeds of A and B is "
            f"{speed_ratio_p}:{speed_ratio_q}. If they start together, by what "
            f"distance (in m) does A win when A finishes the race? (2 decimal places.)"
        )
        solution = (
            f"In the time A covers {length} m, B covers "
            f"$\\dfrac{{{speed_ratio_q}}}{{{speed_ratio_p}}} \\times {length} = "
            f"{float(Fraction(speed_ratio_q, speed_ratio_p) * length):.2f}$ m "
            f"(same time, speeds proportional to distance covered). "
            f"A wins by $= {length} - "
            f"{float(Fraction(speed_ratio_q, speed_ratio_p) * length):.2f} = {margin:.2f}$ m."
        )

        def answer_fn(length=length, p=speed_ratio_p, q=speed_ratio_q):
            # Independent of the Fraction closed-form above: model the race
            # on a real time axis instead of an algebraic ratio. Assign A and
            # B literal speeds (p and q "units"), compute the wall-clock time
            # A takes to finish with plain float division, then compute how
            # far B physically travels in that time. This is a genuinely
            # different computational path (float time-simulation vs exact
            # Fraction algebra) — see PROGRESS.md re: the percentages/
            # profit-loss bug where both paths were secretly the same formula.
            speed_a, speed_b = float(p), float(q)
            time_a_finishes = length / speed_a
            dist_b_travelled = speed_b * time_a_finishes
            return round(length - dist_b_travelled, 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=float(margin), target_seconds=target_seconds(mt),
            tags=["arith:tsd", "races"], format="tita", tita_tolerance=0.05,
        ))
    return specs


def gen_tsd_circular_tracks() -> list[ItemSpec]:
    mt = "qa.arith.tsd-circular-tracks"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        circumference = rng.choice([300, 400, 500, 600, 800])
        s1, s2 = rng.randint(5, 12), rng.randint(13, 20)
        t_opposite = round(circumference / (s1 + s2), 2)
        stem = (
            f"Two runners start at the same time from the same point on a circular "
            f"track of length {circumference} m and run in opposite directions at "
            f"{s1} m/s and {s2} m/s. After how many seconds will they first meet? "
            f"(2 decimal places.)"
        )
        solution = (
            f"Running in opposite directions, relative speed $= {s1} + {s2} = "
            f"{s1 + s2}$ m/s. They first meet after covering the full circumference "
            f"between them: time $= \\dfrac{{{circumference}}}{{{s1 + s2}}} = "
            f"{t_opposite:.2f}$ s."
        )

        def answer_fn(c=circumference, s1=s1, s2=s2):
            return round(c / (s1 + s2), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=t_opposite, target_seconds=target_seconds(mt),
            tags=["arith:tsd", "circular-tracks"], format="tita", tita_tolerance=0.05,
        ))
    return specs


def gen_time_work_pipes_cisterns() -> list[ItemSpec]:
    mt = "qa.arith.time-work-pipes-cisterns"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        a, b = rng.randint(4, 20), rng.randint(4, 20)
        t = round(float(1 / (Fraction(1, a) + Fraction(1, b))), 2)
        stem = (
            f"Pipe A can fill a cistern in {a} hours and pipe B can fill it in "
            f"{b} hours. If both pipes are opened together, how long will they take "
            f"to fill the cistern? (2 decimal places, in hours.)"
        )
        solution = (
            f"A's rate $= 1/{a}$ of the cistern per hour, B's rate $= 1/{b}$. "
            f"Combined rate $= 1/{a} + 1/{b} = "
            f"{float(Fraction(1, a) + Fraction(1, b)):.4f}$ per hour. "
            f"Time together $= \\dfrac{{1}}{{1/{a}+1/{b}}} = {t:.2f}$ hours."
        )

        def answer_fn(a=a, b=b):
            return round(float(1 / (Fraction(1, a) + Fraction(1, b))), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=t, target_seconds=target_seconds(mt),
            tags=["arith:time-work", "pipes-cisterns"], format="tita", tita_tolerance=0.02,
        ))
    return specs


def gen_time_work_efficiency_wages() -> list[ItemSpec]:
    mt = "qa.arith.time-work-efficiency-wages"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    for i in range(n):
        eff_ratio = rng.randint(2, 4)  # A is eff_ratio times as efficient as B
        together_days = rng.randint(4, 12)
        # A's rate = eff_ratio * B's rate; A_rate + B_rate = 1/together_days
        # B_rate * (eff_ratio + 1) = 1/together_days
        b_days = together_days * (eff_ratio + 1)
        a_days = Fraction(b_days, eff_ratio)
        a_days_f = round(float(a_days), 2)
        stem = (
            f"A is {eff_ratio} times as efficient as B. Working together, they "
            f"complete a job in {together_days} days. In how many days can A alone "
            f"complete the job? (2 decimal places.)"
        )
        solution = (
            f"Let B's rate be $r$ per day; A's rate is ${eff_ratio}r$. Combined rate "
            f"$= ({eff_ratio}+1)r = 1/{together_days}$, so "
            f"$r = \\dfrac{{1}}{{{eff_ratio + 1}\\times{together_days}}}$. "
            f"A's rate $= {eff_ratio}r$, so A alone takes "
            f"$\\dfrac{{1}}{{{eff_ratio}r}} = \\dfrac{{{eff_ratio+1}\\times{together_days}}}{{{eff_ratio}}} "
            f"= {a_days_f:.2f}$ days."
        )

        def answer_fn(eff_ratio=eff_ratio, together_days=together_days):
            b_days_ = together_days * (eff_ratio + 1)
            return round(float(Fraction(b_days_, eff_ratio)), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=a_days_f, target_seconds=target_seconds(mt),
            tags=["arith:time-work", "efficiency"], format="tita", tita_tolerance=0.02,
        ))
    return specs


def gen_time_work_chain_rule() -> list[ItemSpec]:
    mt = "qa.arith.time-work-chain-rule"
    rng = random.Random(mt)
    n = item_count(mt)
    specs = []
    # Parameter space (p,d,h,q,h2 all multi-valued ranges) was already large
    # enough for 10 unique draws; widened h/h2 slightly for more variety at
    # the high-difficulty end (more workers/hours combinations to reason about).
    for i in range(n):
        p = rng.randint(4, 30)
        d = rng.randint(4, 25)
        h = rng.randint(3, 12)
        q = rng.randint(4, 30)
        h2 = rng.randint(3, 12)
        d2 = round(float(Fraction(p * d * h, q * h2)), 2)
        stem = (
            f"{p} workers, each working {h} hours a day, can complete a job in "
            f"{d} days. How many days will {q} workers, each working {h2} hours a "
            f"day, take to complete the same job? (2 decimal places.)"
        )
        solution = (
            f"Total work $= {p} \\times {d} \\times {h}$ worker-hours $= {p*d*h}$. "
            f"With {q} workers at {h2} hours/day, days needed "
            f"$= \\dfrac{{{p*d*h}}}{{{q}\\times{h2}}} = {d2:.2f}$."
        )

        def answer_fn(p=p, d=d, h=h, q=q, h2=h2):
            # Independent of the Fraction closed-form above: set up the
            # work-conservation equation p*h*d == q*h2*D (total worker-hours
            # is constant) and solve for D with sympy's equation solver
            # instead of directly evaluating the ratio — a different code
            # path (symbolic solve vs. Fraction division), same discipline
            # used for gen_linear_equations/gen_maxima_minima.
            import sympy as sp
            d_sym = sp.symbols("d_sym", positive=True)
            solved = sp.solve(sp.Eq(p * h * d, q * h2 * d_sym), d_sym)[0]
            return round(float(solved), 2)

        specs.append(ItemSpec(
            microtopic_id=mt, difficulty=_diffs(n)[i], stem=stem, solution=solution,
            answer_fn=answer_fn, claimed_value=d2, target_seconds=target_seconds(mt),
            tags=["arith:time-work", "chain-rule"], format="tita", tita_tolerance=0.02,
        ))
    return specs


GENERATORS = [
    gen_percentages,
    gen_profit_loss_discount,
    gen_si_ci_instalments,
    gen_ratio_proportion_variation,
    gen_mixtures_alligation,
    gen_averages_weighted_averages,
    gen_tsd_relative_speed,
    gen_tsd_trains,
    gen_tsd_boats_streams,
    gen_tsd_races,
    gen_tsd_circular_tracks,
    gen_time_work_pipes_cisterns,
    gen_time_work_efficiency_wages,
    gen_time_work_chain_rule,
]
