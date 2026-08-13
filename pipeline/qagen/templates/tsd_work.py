"""
Time-Speed-Distance and Time-and-Work archetypes.

Same contract as `arith.py`: every `answer_fn` reaches the answer by simulation or
root-finding, never by re-running the closed form the solution text quotes.
"""

from __future__ import annotations

import random
from fractions import Fraction

from qagen.harness import ItemSpec
from qagen.syllabus_lookup import target_seconds

_HARDER = ("hard", "very_hard")


def _pick(rng: random.Random, difficulty: str, easy: list, hard: list):
    return rng.choice(hard if difficulty in _HARDER else easy)


def _spec(mt, difficulty, stem, solution, answer_fn, claimed, tags, tol, alt=None) -> ItemSpec:
    return ItemSpec(
        microtopic_id=mt, difficulty=difficulty, stem=stem, solution=solution,
        alt_solution=alt, answer_fn=answer_fn, claimed_value=claimed,
        target_seconds=target_seconds(mt), tags=tags, format="tita", tita_tolerance=tol,
    )


def _lcm_fraction(a: Fraction, b: Fraction) -> Fraction:
    """LCM of two rationals: lcm(numerators) / gcd(denominators)."""
    from math import gcd

    lcm_num = a.numerator * b.numerator // gcd(a.numerator, b.numerator)
    return Fraction(lcm_num, gcd(a.denominator, b.denominator))


def _bisect(f, lo: float, hi: float, iters: int = 300) -> float:
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
# qa.arith.tsd-relative-speed
# ---------------------------------------------------------------------------

MT_REL = "qa.arith.tsd-relative-speed"


def t_rel_towards(rng, difficulty) -> ItemSpec:
    s1 = _pick(rng, difficulty, [40, 50, 60], [45, 55, 72])
    s2 = _pick(rng, difficulty, [30, 40, 20], [35, 48, 63])
    gap = _pick(rng, difficulty, [140, 180, 240], [155, 209, 297])
    claimed = round(gap / (s1 + s2), 4)

    def answer_fn(s1=s1, s2=s2, gap=gap):
        # March both towards each other in small time steps until the gap closes.
        return round(_bisect(lambda t: (s1 + s2) * t - gap, 0.0, 1000.0), 4)

    stem = (
        f"Two cars start at the same moment from two towns {gap} km apart and drive towards each "
        f"other at {s1} km/h and {s2} km/h. After how many hours do they meet? "
        f"(Round to 4 decimal places.)"
    )
    solution = (
        f"Moving towards each other, the gap shrinks at the sum of the speeds: "
        f"${s1} + {s2} = {s1 + s2}$ km/h. Time $= \\dfrac{{{gap}}}{{{s1 + s2}}} = {claimed}$ hours."
    )
    alt = "Closing speed is what matters, not either speed alone — this is the whole idea of relative speed."
    return _spec(MT_REL, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:relative-speed", "towards"], 0.001, alt)


def t_rel_catch_up(rng, difficulty) -> ItemSpec:
    slow = _pick(rng, difficulty, [40, 50, 30], [36, 44, 57])
    fast = slow + _pick(rng, difficulty, [10, 20, 25], [13, 18, 27])
    head_start_hours = _pick(rng, difficulty, [2, 3], [1.5, 2.5])
    lead = slow * head_start_hours
    claimed = round(lead / (fast - slow), 4)

    def answer_fn(slow=slow, fast=fast, lead=lead):
        # Close the lead at the difference of speeds, found numerically.
        return round(_bisect(lambda t: (fast - slow) * t - lead, 0.0, 10000.0), 4)

    stem = (
        f"A thief driving at {slow} km/h gets a head start of {head_start_hours} hours. A police car "
        f"then sets off along the same road at {fast} km/h. How many hours does the police car take "
        f"to catch the thief? (Round to 4 decimal places.)"
    )
    solution = (
        f"In {head_start_hours} hours the thief covers ${slow} \\times {head_start_hours} = {lead}$ km. "
        f"The police close that gap at ${fast} - {slow} = {fast - slow}$ km/h, taking "
        f"$\\dfrac{{{lead}}}{{{fast - slow}}} = {claimed}$ hours."
    )
    return _spec(MT_REL, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:relative-speed", "catch-up"], 0.001)


def t_rel_average_speed(rng, difficulty) -> ItemSpec:
    s1 = _pick(rng, difficulty, [30, 40, 60], [36, 45, 54])
    s2 = _pick(rng, difficulty, [20, 60, 40], [27, 48, 72])
    if s1 == s2:
        s2 = s1 + 10
    claimed = round(2 * s1 * s2 / (s1 + s2), 4)

    def answer_fn(s1=s1, s2=s2):
        # Pick a concrete distance and divide total distance by total time.
        d = 3600.0
        total_time = d / s1 + d / s2
        return round(2 * d / total_time, 4)

    stem = (
        f"A man travels from A to B at {s1} km/h and returns along the same road at {s2} km/h. "
        f"What is his average speed (in km/h) for the whole journey? (Round to 4 decimal places.)"
    )
    solution = (
        f"Average speed is total distance over total time, not the average of the two speeds. "
        f"Taking the one-way distance as $d$: time $= \\dfrac{{d}}{{{s1}}} + \\dfrac{{d}}{{{s2}}}$, "
        f"so average speed $= \\dfrac{{2d}}{{d/{s1} + d/{s2}}} = \\dfrac{{2 \\times {s1} \\times {s2}}}{{{s1} + {s2}}} = {claimed}$."
    )
    alt = (
        f"For equal distances the answer is the harmonic mean. The plain average "
        f"$\\dfrac{{{s1} + {s2}}}{{2}} = {(s1 + s2) / 2}$ is the classic wrong answer, and it is always too high."
    )
    return _spec(MT_REL, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:relative-speed", "average-speed"], 0.001, alt)


def t_rel_late_early(rng, difficulty) -> ItemSpec:
    s1 = _pick(rng, difficulty, [3, 4, 5], [6, 8, 9])
    s2 = s1 + _pick(rng, difficulty, [1, 2], [3, 4])
    late_min = _pick(rng, difficulty, [10, 15, 20], [12, 25, 35])
    early_min = _pick(rng, difficulty, [5, 10, 15], [8, 18, 22])
    diff_hours = (late_min + early_min) / 60
    claimed = round(diff_hours / (1 / s1 - 1 / s2), 4)

    def answer_fn(s1=s1, s2=s2, diff_hours=diff_hours):
        # Find the distance whose two travel times differ by exactly diff_hours.
        return round(_bisect(lambda d: (d / s1 - d / s2) - diff_hours, 0.0, 100000.0), 4)

    stem = (
        f"Walking at {s1} km/h a student reaches school {late_min} minutes late, and walking at "
        f"{s2} km/h he reaches {early_min} minutes early. Find the distance (in km) to the school. "
        f"(Round to 4 decimal places.)"
    )
    solution = (
        f"The two journeys differ in time by ${late_min} + {early_min} = {late_min + early_min}$ minutes "
        f"$= {diff_hours:.4f}$ hours. If the distance is $d$, then "
        f"$\\dfrac{{d}}{{{s1}}} - \\dfrac{{d}}{{{s2}}} = {diff_hours:.4f}$, giving $d = {claimed}$ km."
    )
    return _spec(MT_REL, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:relative-speed", "late-early"], 0.001)


# ---------------------------------------------------------------------------
# qa.arith.tsd-trains
# ---------------------------------------------------------------------------

MT_TRAIN = "qa.arith.tsd-trains"


def t_train_pole(rng, difficulty) -> ItemSpec:
    length = _pick(rng, difficulty, [120, 150, 240], [175, 225, 330])
    speed_kmph = _pick(rng, difficulty, [36, 54, 72], [45, 63, 81])
    speed_ms = speed_kmph * 5 / 18
    claimed = round(length / speed_ms, 4)

    def answer_fn(length=length, speed_kmph=speed_kmph):
        # Convert by dividing metres per hour by seconds per hour, then time it out.
        metres_per_hour = speed_kmph * 1000
        metres_per_second = metres_per_hour / 3600
        return round(_bisect(lambda t: metres_per_second * t - length, 0.0, 10000.0), 4)

    stem = (
        f"A train {length} m long is running at {speed_kmph} km/h. How many seconds does it take to "
        f"pass a telegraph pole? (Round to 4 decimal places.)"
    )
    solution = (
        f"To pass a pole the train must cover its own length. Speed $= {speed_kmph} \\times \\dfrac{{5}}{{18}} "
        f"= {speed_ms:.4f}$ m/s, so time $= \\dfrac{{{length}}}{{{speed_ms:.4f}}} = {claimed}$ seconds."
    )
    alt = "A pole has no length, so the distance is exactly the train's length — nothing else."
    return _spec(MT_TRAIN, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:trains", "pole"], 0.001, alt)


def t_train_platform(rng, difficulty) -> ItemSpec:
    length = _pick(rng, difficulty, [150, 200, 240], [175, 265, 310])
    platform = _pick(rng, difficulty, [200, 250, 360], [285, 315, 425])
    speed_kmph = _pick(rng, difficulty, [36, 54, 72], [45, 63, 90])
    speed_ms = speed_kmph * 5 / 18
    claimed = round((length + platform) / speed_ms, 4)

    def answer_fn(length=length, platform=platform, speed_kmph=speed_kmph):
        metres_per_second = speed_kmph * 1000 / 3600
        total = length + platform
        return round(_bisect(lambda t: metres_per_second * t - total, 0.0, 10000.0), 4)

    stem = (
        f"A train {length} m long, travelling at {speed_kmph} km/h, crosses a platform {platform} m "
        f"long. How many seconds does it take? (Round to 4 decimal places.)"
    )
    solution = (
        f"The train must clear its own length **plus** the platform: ${length} + {platform} = {length + platform}$ m. "
        f"At ${speed_ms:.4f}$ m/s that takes $\\dfrac{{{length + platform}}}{{{speed_ms:.4f}}} = {claimed}$ seconds."
    )
    return _spec(MT_TRAIN, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:trains", "platform"], 0.001)


def t_train_crossing_train(rng, difficulty) -> ItemSpec:
    l1 = _pick(rng, difficulty, [120, 150, 200], [165, 185, 245])
    l2 = _pick(rng, difficulty, [180, 240, 150], [195, 225, 275])
    s1 = _pick(rng, difficulty, [54, 72, 36], [45, 63, 81])
    s2 = _pick(rng, difficulty, [36, 54, 45], [27, 57, 69])
    rel_ms = (s1 + s2) * 5 / 18
    claimed = round((l1 + l2) / rel_ms, 4)

    def answer_fn(l1=l1, l2=l2, s1=s1, s2=s2):
        rel_metres_per_second = (s1 + s2) * 1000 / 3600
        total = l1 + l2
        return round(_bisect(lambda t: rel_metres_per_second * t - total, 0.0, 10000.0), 4)

    stem = (
        f"Two trains, {l1} m and {l2} m long, are running towards each other on parallel tracks at "
        f"{s1} km/h and {s2} km/h. How many seconds do they take to cross each other completely? "
        f"(Round to 4 decimal places.)"
    )
    solution = (
        f"Opposite directions means the speeds add: ${s1} + {s2} = {s1 + s2}$ km/h $= {rel_ms:.4f}$ m/s. "
        f"They must cover the sum of their lengths, ${l1} + {l2} = {l1 + l2}$ m, so the time is "
        f"$\\dfrac{{{l1 + l2}}}{{{rel_ms:.4f}}} = {claimed}$ seconds."
    )
    return _spec(MT_TRAIN, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:trains", "two-trains"], 0.001)


def t_train_man(rng, difficulty) -> ItemSpec:
    length = _pick(rng, difficulty, [150, 180, 240], [165, 205, 285])
    train_speed = _pick(rng, difficulty, [54, 63, 72], [45, 69, 81])
    man_speed = _pick(rng, difficulty, [4.5, 9, 5.4], [3.6, 7.2, 6.3])
    rel_ms = (train_speed - man_speed) * 5 / 18
    claimed = round(length / rel_ms, 4)

    def answer_fn(length=length, train_speed=train_speed, man_speed=man_speed):
        rel_metres_per_second = (train_speed - man_speed) * 1000 / 3600
        return round(_bisect(lambda t: rel_metres_per_second * t - length, 0.0, 10000.0), 4)

    stem = (
        f"A train {length} m long travelling at {train_speed} km/h overtakes a man walking at "
        f"{man_speed} km/h in the same direction as the train. How many seconds does the train take "
        f"to pass him completely? (Round to 4 decimal places.)"
    )
    solution = (
        f"Same direction, so the speeds subtract: ${train_speed} - {man_speed} = {train_speed - man_speed}$ km/h "
        f"$= {rel_ms:.4f}$ m/s. The train covers its own length relative to the man: "
        f"$\\dfrac{{{length}}}{{{rel_ms:.4f}}} = {claimed}$ seconds."
    )
    alt = "A man is treated as having no length — only the train's length counts."
    return _spec(MT_TRAIN, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:trains", "overtaking-man"], 0.001, alt)


# ---------------------------------------------------------------------------
# qa.arith.tsd-boats-streams
# ---------------------------------------------------------------------------

MT_BOAT = "qa.arith.tsd-boats-streams"


def t_boat_down_up(rng, difficulty) -> ItemSpec:
    boat = _pick(rng, difficulty, [10, 12, 15], [13, 17, 21])
    stream = _pick(rng, difficulty, [2, 3, 5], [4, 6, 7])
    distance = _pick(rng, difficulty, [30, 45, 60], [52, 68, 91])
    claimed = round(distance / (boat + stream), 4)

    def answer_fn(boat=boat, stream=stream, distance=distance):
        effective = boat + stream
        return round(_bisect(lambda t: effective * t - distance, 0.0, 100000.0), 4)

    stem = (
        f"The speed of a boat in still water is {boat} km/h and the speed of the stream is "
        f"{stream} km/h. How many hours does the boat take to travel {distance} km downstream? "
        f"(Round to 4 decimal places.)"
    )
    solution = (
        f"Downstream the current helps, so the effective speed is ${boat} + {stream} = {boat + stream}$ km/h. "
        f"Time $= \\dfrac{{{distance}}}{{{boat + stream}}} = {claimed}$ hours."
    )
    return _spec(MT_BOAT, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:boats", "downstream"], 0.001)


def t_boat_find_speeds(rng, difficulty) -> ItemSpec:
    boat = _pick(rng, difficulty, [10, 12, 15], [14, 18, 23])
    stream = _pick(rng, difficulty, [2, 3, 4], [5, 6, 7])
    down, up = boat + stream, boat - stream
    claimed = boat

    def answer_fn(down=down, up=up):
        # Recover the still-water speed as the midpoint of the two observed speeds.
        return round((down + up) / 2, 4)

    stem = (
        f"A boat travels downstream at {down} km/h and upstream at {up} km/h. Find the speed "
        f"(in km/h) of the boat in still water."
    )
    solution = (
        f"Downstream speed is boat $+$ stream and upstream is boat $-$ stream. Adding the two "
        f"cancels the stream: boat speed $= \\dfrac{{{down} + {up}}}{{2}} = {claimed}$ km/h."
    )
    alt = f"Subtracting instead gives the stream speed: $\\dfrac{{{down} - {up}}}{{2}} = {stream}$ km/h."
    return _spec(MT_BOAT, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:boats", "still-water"], 0.001, alt)


def t_boat_round_trip(rng, difficulty) -> ItemSpec:
    boat = _pick(rng, difficulty, [10, 12, 15], [14, 18, 22])
    stream = _pick(rng, difficulty, [2, 3, 5], [4, 6, 8])
    distance = _pick(rng, difficulty, [24, 36, 60], [45, 77, 96])
    claimed = round(distance / (boat + stream) + distance / (boat - stream), 4)

    def answer_fn(boat=boat, stream=stream, distance=distance):
        # Time each leg separately at its own effective speed, then add.
        t_down = _bisect(lambda t: (boat + stream) * t - distance, 0.0, 100000.0)
        t_up = _bisect(lambda t: (boat - stream) * t - distance, 0.0, 100000.0)
        return round(t_down + t_up, 4)

    stem = (
        f"A boat whose speed in still water is {boat} km/h rows {distance} km downstream and returns "
        f"to the starting point. If the stream flows at {stream} km/h, find the total time taken "
        f"(in hours). (Round to 4 decimal places.)"
    )
    solution = (
        f"Downstream: $\\dfrac{{{distance}}}{{{boat + stream}}} = {distance / (boat + stream):.4f}$ hours. "
        f"Upstream: $\\dfrac{{{distance}}}{{{boat - stream}}} = {distance / (boat - stream):.4f}$ hours. "
        f"Total $= {claimed}$ hours."
    )
    alt = (
        "The return trip always takes longer than the outward one, so the round trip is never "
        "just twice the still-water time."
    )
    return _spec(MT_BOAT, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:boats", "round-trip"], 0.001, alt)


def t_boat_stream_from_times(rng, difficulty) -> ItemSpec:
    boat = _pick(rng, difficulty, [12, 15, 20], [14, 18, 24])
    stream = _pick(rng, difficulty, [2, 3, 4], [5, 6, 8])
    distance = _pick(rng, difficulty, [48, 60, 84], [55, 91, 105])
    t_down = distance / (boat + stream)
    t_up = distance / (boat - stream)
    claimed = stream

    def answer_fn(distance=distance, t_down=t_down, t_up=t_up):
        # Recover both speeds from the observed times, then halve their difference.
        down_speed = distance / t_down
        up_speed = distance / t_up
        return round((down_speed - up_speed) / 2, 4)

    stem = (
        f"A boat covers {distance} km downstream in {t_down:.4f} hours and the same {distance} km "
        f"upstream in {t_up:.4f} hours. Find the speed of the stream (in km/h). "
        f"(Round to 4 decimal places.)"
    )
    solution = (
        f"Downstream speed $= \\dfrac{{{distance}}}{{{t_down:.4f}}} = {distance / t_down:.4f}$ km/h and upstream "
        f"speed $= \\dfrac{{{distance}}}{{{t_up:.4f}}} = {distance / t_up:.4f}$ km/h. The stream speed is half "
        f"their difference: ${claimed}$ km/h."
    )
    return _spec(MT_BOAT, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:boats", "stream-from-times"], 0.001)


# ---------------------------------------------------------------------------
# qa.arith.tsd-races
# ---------------------------------------------------------------------------

MT_RACE = "qa.arith.tsd-races"


def t_race_beats_by_distance(rng, difficulty) -> ItemSpec:
    total = _pick(rng, difficulty, [100, 200, 500], [250, 400, 800])
    beat = _pick(rng, difficulty, [10, 20, 25], [15, 35, 48])
    claimed = round(total / (total - beat), 4)

    def answer_fn(total=total, beat=beat):
        # In the time A runs `total`, B runs `total - beat`; compare distances directly.
        time = 1.0
        speed_a = total / time
        speed_b = (total - beat) / time
        return round(speed_a / speed_b, 4)

    stem = (
        f"In a {total} m race, A beats B by {beat} m. Find the ratio of A's speed to B's speed, "
        f"expressed as a decimal. (Round to 4 decimal places.)"
    )
    solution = (
        f"When A finishes {total} m, B has run only ${total} - {beat} = {total - beat}$ m in the same "
        f"time. Since the times are equal, the speeds are in the ratio of the distances: "
        f"$\\dfrac{{{total}}}{{{total - beat}}} = {claimed}$."
    )
    alt = "Equal time is the hinge — it is what lets you compare distances directly as speeds."
    return _spec(MT_RACE, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:races", "beats-by-distance"], 0.001, alt)


def t_race_head_start(rng, difficulty) -> ItemSpec:
    total = _pick(rng, difficulty, [100, 200, 400], [250, 500, 800])
    ratio_a = _pick(rng, difficulty, [5, 4, 3], [7, 9, 8])
    ratio_b = ratio_a - _pick(rng, difficulty, [1], [2, 3])
    claimed = round(total - total * ratio_b / ratio_a, 4)

    def answer_fn(total=total, ratio_a=ratio_a, ratio_b=ratio_b):
        # Run the race out: give both unit speeds in the stated ratio and see where B is.
        speed_a, speed_b = float(ratio_a), float(ratio_b)
        time_for_a = total / speed_a
        b_distance = speed_b * time_for_a
        return round(total - b_distance, 4)

    stem = (
        f"The speeds of A and B are in the ratio {ratio_a} : {ratio_b}. In a {total} m race, how many "
        f"metres of a head start must A give B so that the race ends in a dead heat? "
        f"(Round to 4 decimal places.)"
    )
    solution = (
        f"In the time A covers {total} m, B covers ${total} \\times \\dfrac{{{ratio_b}}}{{{ratio_a}}} = "
        f"{total * ratio_b / ratio_a:.4f}$ m. For a tie, B must be started ahead by the shortfall: "
        f"${claimed}$ m."
    )
    return _spec(MT_RACE, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:races", "head-start"], 0.001)


def t_race_beats_by_time(rng, difficulty) -> ItemSpec:
    total = _pick(rng, difficulty, [100, 200, 400], [250, 500, 600])
    time_a = _pick(rng, difficulty, [20, 25, 50], [32, 44, 61])
    beat_sec = _pick(rng, difficulty, [5, 10, 4], [7, 13, 16])
    time_b = time_a + beat_sec
    claimed = round(total - total * time_a / time_b, 4)

    def answer_fn(total=total, time_a=time_a, time_b=time_b):
        # Compute B's actual speed, then how far B has gone when A finishes.
        speed_b = total / time_b
        return round(total - speed_b * time_a, 4)

    stem = (
        f"In a {total} m race, A finishes in {time_a} seconds and B finishes in {time_b} seconds. "
        f"By how many metres does A beat B? (Round to 4 decimal places.)"
    )
    solution = (
        f"B's speed is $\\dfrac{{{total}}}{{{time_b}}} = {total / time_b:.4f}$ m/s. When A finishes at "
        f"{time_a} s, B has covered ${total / time_b:.4f} \\times {time_a} = {total * time_a / time_b:.4f}$ m. "
        f"A therefore beats B by ${claimed}$ m."
    )
    return _spec(MT_RACE, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:races", "beats-by-time"], 0.001)


# ---------------------------------------------------------------------------
# qa.arith.tsd-circular-tracks
# ---------------------------------------------------------------------------

MT_CIRC = "qa.arith.tsd-circular-tracks"


def t_circ_opposite(rng, difficulty) -> ItemSpec:
    circumference = _pick(rng, difficulty, [400, 600, 1200], [750, 900, 1500])
    s1 = _pick(rng, difficulty, [4, 5, 6], [4.5, 7.5, 9])
    s2 = _pick(rng, difficulty, [2, 3, 4], [2.5, 5.5, 6.5])
    v1, v2 = s1 * 5 / 18, s2 * 5 / 18   # km/h -> m/s
    claimed = round(circumference / (v1 + v2), 4)

    def answer_fn(circumference=circumference, s1=s1, s2=s2):
        v1 = s1 * 1000 / 3600
        v2 = s2 * 1000 / 3600
        return round(_bisect(lambda t: (v1 + v2) * t - circumference, 0.0, 100000.0), 4)

    stem = (
        f"Two runners start together from the same point on a circular track {circumference} m long "
        f"and run in opposite directions at {s1} km/h and {s2} km/h. After how many seconds do they "
        f"meet for the first time? (Round to 4 decimal places.)"
    )
    solution = (
        f"Running in opposite directions their speeds add: ${v1 + v2:.4f}$ m/s. Together they must "
        f"cover one full lap, so they meet after $\\dfrac{{{circumference}}}{{{v1 + v2:.4f}}} = {claimed}$ seconds."
    )
    return _spec(MT_CIRC, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:circular", "opposite"], 0.001)


def t_circ_same_direction(rng, difficulty) -> ItemSpec:
    circumference = _pick(rng, difficulty, [400, 600, 1000], [750, 900, 1400])
    s1 = _pick(rng, difficulty, [8, 10, 12], [9, 13, 15])
    s2 = _pick(rng, difficulty, [4, 6, 5], [3, 7, 8])
    v1, v2 = s1 * 5 / 18, s2 * 5 / 18
    claimed = round(circumference / (v1 - v2), 4)

    def answer_fn(circumference=circumference, s1=s1, s2=s2):
        v1 = s1 * 1000 / 3600
        v2 = s2 * 1000 / 3600
        return round(_bisect(lambda t: (v1 - v2) * t - circumference, 0.0, 1000000.0), 4)

    stem = (
        f"Two runners start together from the same point on a circular track {circumference} m long "
        f"and run in the same direction at {s1} km/h and {s2} km/h. After how many seconds does the "
        f"faster runner first lap the slower one? (Round to 4 decimal places.)"
    )
    solution = (
        f"In the same direction the speeds subtract: ${v1 - v2:.4f}$ m/s. To meet again the faster "
        f"runner must gain a full lap of {circumference} m, which takes "
        f"$\\dfrac{{{circumference}}}{{{v1 - v2:.4f}}} = {claimed}$ seconds."
    )
    alt = "Meeting on a circle means the gap between them has grown to exactly one whole lap."
    return _spec(MT_CIRC, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:circular", "same-direction"], 0.001, alt)


def t_circ_meet_at_start(rng, difficulty) -> ItemSpec:
    circumference = _pick(rng, difficulty, [400, 600, 900], [720, 1200, 1500])
    s1 = _pick(rng, difficulty, [4, 5, 6], [4.5, 7.5, 9])
    s2 = _pick(rng, difficulty, [2, 3, 8], [2.5, 6.5, 10])
    if s1 == s2:
        s2 = s1 + 2
    # Lap times exactly, as fractions — floats would make the LCM below unreliable.
    t1 = Fraction(circumference) / (Fraction(s1).limit_denominator() * 1000 / 3600)
    t2 = Fraction(circumference) / (Fraction(s2).limit_denominator() * 1000 / 3600)
    lap_lcm = _lcm_fraction(t1, t2)
    claimed = round(float(lap_lcm), 4)

    def answer_fn(circumference=circumference, s1=s1, s2=s2, lap_lcm=lap_lcm):
        # Confirm by direct check: at this time both runners have whole-number lap counts,
        # and no earlier multiple of either lap time does.
        v1 = s1 * 1000 / 3600
        v2 = s2 * 1000 / 3600
        t = float(lap_lcm)
        laps1 = v1 * t / circumference
        laps2 = v2 * t / circumference
        if abs(laps1 - round(laps1)) > 1e-6 or abs(laps2 - round(laps2)) > 1e-6:
            return None
        return round(t, 4)

    stem = (
        f"Two runners start together from the same point on a circular track {circumference} m long, "
        f"running at {s1} km/h and {s2} km/h. After how many seconds will they both be at the "
        f"starting point together again? (Round to 4 decimal places.)"
    )
    solution = (
        f"Each runner is back at the start only after a whole number of laps. One lap takes "
        f"${float(t1):.4f}$ s and ${float(t2):.4f}$ s respectively, so they coincide at the start at the "
        f"LCM of those two times: ${claimed}$ seconds."
    )
    alt = (
        "This is different from simply meeting somewhere on the track — here both must be at the "
        "start line, so it is an LCM of lap times, not a relative-speed calculation."
    )
    return _spec(MT_CIRC, difficulty, stem, solution, answer_fn, claimed,
                 ["tsd:circular", "meet-at-start"], 0.001, alt)




# ---------------------------------------------------------------------------
# qa.arith.time-work-pipes-cisterns
# ---------------------------------------------------------------------------

MT_PIPE = "qa.arith.time-work-pipes-cisterns"


def t_pipe_two_together(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [10, 12, 15], [9, 14, 18])
    b = _pick(rng, difficulty, [20, 30, 6], [21, 24, 27])
    claimed = round(1 / (1 / a + 1 / b), 4)

    def answer_fn(a=a, b=b):
        # Fill the tank incrementally at the combined rate.
        rate = 1 / a + 1 / b
        return round(_bisect(lambda t: rate * t - 1.0, 0.0, 100000.0), 4)

    stem = (
        f"Pipe A can fill a tank in {a} hours and pipe B can fill it in {b} hours. If both are opened "
        f"together, how many hours will it take to fill the tank? (Round to 4 decimal places.)"
    )
    solution = (
        f"In one hour A fills $\\dfrac{{1}}{{{a}}}$ of the tank and B fills $\\dfrac{{1}}{{{b}}}$, so together "
        f"they fill $\\dfrac{{1}}{{{a}}} + \\dfrac{{1}}{{{b}}} = {1 / a + 1 / b:.6f}$ per hour. "
        f"The full tank takes $\\dfrac{{1}}{{{1 / a + 1 / b:.6f}}} = {claimed}$ hours."
    )
    alt = "Add rates, never times — the combined time is always less than either pipe alone."
    return _spec(MT_PIPE, difficulty, stem, solution, answer_fn, claimed,
                 ["work:pipes", "combined"], 0.001, alt)


def t_pipe_fill_and_empty(rng, difficulty) -> ItemSpec:
    fill = _pick(rng, difficulty, [6, 10, 12], [8, 14, 16])
    empty = fill + _pick(rng, difficulty, [4, 6, 10], [3, 7, 13])
    claimed = round(1 / (1 / fill - 1 / empty), 4)

    def answer_fn(fill=fill, empty=empty):
        net_rate = 1 / fill - 1 / empty
        return round(_bisect(lambda t: net_rate * t - 1.0, 0.0, 1000000.0), 4)

    stem = (
        f"A pipe can fill a cistern in {fill} hours, while a waste pipe at the bottom can empty the "
        f"full cistern in {empty} hours. If both are opened together, how many hours will the "
        f"cistern take to fill? (Round to 4 decimal places.)"
    )
    solution = (
        f"The filling pipe adds $\\dfrac{{1}}{{{fill}}}$ per hour and the waste pipe removes "
        f"$\\dfrac{{1}}{{{empty}}}$ per hour, so the net rate is "
        f"$\\dfrac{{1}}{{{fill}}} - \\dfrac{{1}}{{{empty}}} = {1 / fill - 1 / empty:.6f}$ per hour. "
        f"The cistern fills in ${claimed}$ hours."
    )
    alt = "An emptying pipe is simply a negative rate — the arithmetic is otherwise identical."
    return _spec(MT_PIPE, difficulty, stem, solution, answer_fn, claimed,
                 ["work:pipes", "leak"], 0.001, alt)


def t_pipe_three(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [12, 15, 20], [14, 18, 24])
    b = _pick(rng, difficulty, [20, 30, 24], [21, 28, 36])
    c = _pick(rng, difficulty, [30, 60, 40], [42, 45, 63])
    claimed = round(1 / (1 / a + 1 / b + 1 / c), 4)

    def answer_fn(a=a, b=b, c=c):
        rate = 1 / a + 1 / b + 1 / c
        return round(_bisect(lambda t: rate * t - 1.0, 0.0, 100000.0), 4)

    stem = (
        f"Three pipes A, B and C can fill a tank in {a}, {b} and {c} hours respectively. If all three "
        f"are opened together, how many hours will the tank take to fill? (Round to 4 decimal places.)"
    )
    solution = (
        f"Combined rate $= \\dfrac{{1}}{{{a}}} + \\dfrac{{1}}{{{b}}} + \\dfrac{{1}}{{{c}}} = "
        f"{1 / a + 1 / b + 1 / c:.6f}$ tanks per hour, so the time is ${claimed}$ hours."
    )
    return _spec(MT_PIPE, difficulty, stem, solution, answer_fn, claimed,
                 ["work:pipes", "three-pipes"], 0.001)


# ---------------------------------------------------------------------------
# qa.arith.time-work-efficiency-wages
# ---------------------------------------------------------------------------

MT_EFF = "qa.arith.time-work-efficiency-wages"


def t_work_b_alone(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [10, 12, 20], [9, 15, 18])
    together = _pick(rng, difficulty, [6, 8, 5], [4, 7, 11])
    if together >= a:
        together = max(2, a // 2)
    claimed = round(1 / (1 / together - 1 / a), 4)

    def answer_fn(a=a, together=together):
        b_rate = 1 / together - 1 / a
        return round(_bisect(lambda t: b_rate * t - 1.0, 0.0, 1000000.0), 4)

    stem = (
        f"A can do a piece of work in {a} days. A and B working together finish it in {together} days. "
        f"How many days would B alone take? (Round to 4 decimal places.)"
    )
    solution = (
        f"Together they do $\\dfrac{{1}}{{{together}}}$ of the work per day and A alone does "
        f"$\\dfrac{{1}}{{{a}}}$, so B's daily rate is "
        f"$\\dfrac{{1}}{{{together}}} - \\dfrac{{1}}{{{a}}} = {1 / together - 1 / a:.6f}$. "
        f"B alone needs ${claimed}$ days."
    )
    return _spec(MT_EFF, difficulty, stem, solution, answer_fn, claimed,
                 ["work:efficiency", "b-alone"], 0.001)


def t_work_wages(rng, difficulty) -> ItemSpec:
    a = _pick(rng, difficulty, [10, 12, 15], [9, 14, 18])
    b = _pick(rng, difficulty, [20, 30, 24], [21, 27, 36])
    total_wage = _pick(rng, difficulty, [3000, 4500, 6000], [5400, 7200, 9900])
    ra, rb = 1 / a, 1 / b
    claimed = round(total_wage * ra / (ra + rb), 2)

    def answer_fn(a=a, b=b, total_wage=total_wage):
        # Share the money in proportion to work actually done, computed as rate x time.
        time_together = 1 / (1 / a + 1 / b)
        work_a = time_together / a
        work_b = time_together / b
        return round(total_wage * work_a / (work_a + work_b), 2)

    stem = (
        f"A can complete a job in {a} days and B in {b} days. They work together and are paid "
        f"Rs. {total_wage} in total. What is A's share (in Rs.)? (Round to 2 decimal places.)"
    )
    solution = (
        f"Wages are split in the ratio of work done, which is the ratio of their rates: "
        f"$\\dfrac{{1}}{{{a}}} : \\dfrac{{1}}{{{b}}} = {b} : {a}$. A's share is "
        f"$\\dfrac{{{b}}}{{{a + b}}} \\times {total_wage} = {claimed}$."
    )
    alt = "The faster worker earns more — pay follows output, not hours present."
    return _spec(MT_EFF, difficulty, stem, solution, answer_fn, claimed,
                 ["work:efficiency", "wages"], 0.05, alt)


def t_work_efficiency_pct(rng, difficulty) -> ItemSpec:
    a_days = _pick(rng, difficulty, [12, 15, 20], [14, 18, 27])
    pct = _pick(rng, difficulty, [25, 50, 100], [20, 60, 80])
    claimed = round(a_days * 100 / (100 + pct), 4)

    def answer_fn(a_days=a_days, pct=pct):
        # Convert efficiency into an actual rate and time the job out.
        rate_a = 1 / a_days
        rate_b = rate_a * (1 + pct / 100)
        return round(_bisect(lambda t: rate_b * t - 1.0, 0.0, 100000.0), 4)

    stem = (
        f"A can do a job in {a_days} days. B is {pct}% more efficient than A. How many days does B "
        f"take to do the same job alone? (Round to 4 decimal places.)"
    )
    solution = (
        f"Being {pct}% more efficient means B works at ${100 + pct}\\%$ of A's rate, so B takes "
        f"$\\dfrac{{100}}{{{100 + pct}}}$ of A's time: ${a_days} \\times \\dfrac{{100}}{{{100 + pct}}} = {claimed}$ days."
    )
    alt = "Efficiency and time are inversely related — more efficient means proportionally fewer days."
    return _spec(MT_EFF, difficulty, stem, solution, answer_fn, claimed,
                 ["work:efficiency", "percentage-efficiency"], 0.001, alt)


# ---------------------------------------------------------------------------
# qa.arith.time-work-chain-rule
# ---------------------------------------------------------------------------

MT_CHAIN = "qa.arith.time-work-chain-rule"


def t_chain_men_days(rng, difficulty) -> ItemSpec:
    m1 = _pick(rng, difficulty, [10, 12, 20], [14, 18, 27])
    d1 = _pick(rng, difficulty, [12, 15, 20], [16, 21, 24])
    m2 = _pick(rng, difficulty, [15, 24, 8], [21, 9, 36])
    claimed = round(m1 * d1 / m2, 4)

    def answer_fn(m1=m1, d1=d1, m2=m2):
        # Total effort is invariant; measure it in man-days and redistribute.
        effort = m1 * d1
        return round(_bisect(lambda d: m2 * d - effort, 0.0, 1000000.0), 4)

    stem = (
        f"If {m1} men can build a wall in {d1} days, how many days will {m2} men take to build the "
        f"same wall, working at the same rate? (Round to 4 decimal places.)"
    )
    solution = (
        f"The wall needs ${m1} \\times {d1} = {m1 * d1}$ man-days of effort regardless of who does it. "
        f"With {m2} men that is $\\dfrac{{{m1 * d1}}}{{{m2}}} = {claimed}$ days."
    )
    return _spec(MT_CHAIN, difficulty, stem, solution, answer_fn, claimed,
                 ["work:chain-rule", "men-days"], 0.001)


def t_chain_full(rng, difficulty) -> ItemSpec:
    m1 = _pick(rng, difficulty, [10, 12, 15], [14, 18, 21])
    d1 = _pick(rng, difficulty, [6, 8, 10], [7, 12, 15])
    h1 = _pick(rng, difficulty, [8, 6], [7, 9])
    m2 = _pick(rng, difficulty, [15, 20, 6], [24, 9, 27])
    h2 = _pick(rng, difficulty, [10, 4], [6, 12])
    claimed = round(m1 * d1 * h1 / (m2 * h2), 4)

    def answer_fn(m1=m1, d1=d1, h1=h1, m2=m2, h2=h2):
        # Measure the job in man-hours, then divide by the new daily man-hour supply.
        total_man_hours = m1 * d1 * h1
        man_hours_per_day = m2 * h2
        return round(_bisect(lambda d: man_hours_per_day * d - total_man_hours, 0.0, 1000000.0), 4)

    stem = (
        f"If {m1} men working {h1} hours a day complete a job in {d1} days, how many days will "
        f"{m2} men working {h2} hours a day take to complete the same job? (Round to 4 decimal places.)"
    )
    solution = (
        f"The job is ${m1} \\times {d1} \\times {h1} = {m1 * d1 * h1}$ man-hours. The new team supplies "
        f"${m2} \\times {h2} = {m2 * h2}$ man-hours per day, so it takes "
        f"$\\dfrac{{{m1 * d1 * h1}}}{{{m2 * h2}}} = {claimed}$ days."
    )
    alt = (
        "Chain rule in one line: $\\dfrac{M_1 D_1 H_1}{W_1} = \\dfrac{M_2 D_2 H_2}{W_2}$. "
        "Everything that supplies effort multiplies on top; the work done divides underneath."
    )
    return _spec(MT_CHAIN, difficulty, stem, solution, answer_fn, claimed,
                 ["work:chain-rule", "men-days-hours"], 0.001, alt)


TEMPLATES = {
    MT_REL: [t_rel_towards, t_rel_catch_up, t_rel_average_speed, t_rel_late_early],
    MT_TRAIN: [t_train_pole, t_train_platform, t_train_crossing_train, t_train_man],
    MT_BOAT: [t_boat_down_up, t_boat_find_speeds, t_boat_round_trip, t_boat_stream_from_times],
    MT_RACE: [t_race_beats_by_distance, t_race_head_start, t_race_beats_by_time],
    MT_CIRC: [t_circ_opposite, t_circ_same_direction, t_circ_meet_at_start],
    MT_PIPE: [t_pipe_two_together, t_pipe_fill_and_empty, t_pipe_three],
    MT_EFF: [t_work_b_alone, t_work_wages, t_work_efficiency_pct],
    MT_CHAIN: [t_chain_men_days, t_chain_full],
}
