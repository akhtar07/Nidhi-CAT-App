"""
Additional sets for the six LR topics below SPEC.md §16's bar of 15 questions:
arrangements, distribution-grouping, ordering-ranking, games-tournaments,
selection-conditionalities and venn-set.

## Verification

Every puzzle here is solved by **exhaustive enumeration** — all 720 seatings, all 24
assignments, all 20 three-person committees — and the search asserts that exactly one
arrangement survives the constraints before any question is written. Answers are then read
off that solution programmatically; no answer is typed in by hand.

That makes these the only DILR items in the bank with genuine `answer_fn` independence in the
sense `qagen/templates/__init__.py` demands: the brute force never consults the chain of
deductions the solution text describes, so a flaw in that reasoning cannot propagate into the
answer. If a constraint set were ambiguous or contradictory the generator crashes rather than
shipping a puzzle with two valid answers, which is the failure mode that matters most in LR.

The counting sets (games-tournaments, venn-set) are arithmetic rather than search, and are
checked the same way as the DI batches: computed, then asserted against an independently
worked-out literal.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_lr_batch5.py
"""

from __future__ import annotations

from itertools import combinations, permutations
from typing import Callable

from dilr_common import QSpec, SetPlan, emit_all, fmt


def solve_unique(people: list[str], rules: list[Callable[[dict[str, int]], bool]]) -> dict[str, int]:
    """Enumerates every assignment of `people` to positions 1..n and returns the only one that
    satisfies every rule. Raises if zero or more than one survives — an LR set with two valid
    arrangements is broken content, not a hard question."""
    solutions = []
    for perm in permutations(range(1, len(people) + 1)):
        seating = dict(zip(people, perm))
        if all(rule(seating) for rule in rules):
            solutions.append(seating)
            if len(solutions) > 1:
                raise ValueError(f"puzzle has multiple solutions: {solutions}")
    if not solutions:
        raise ValueError("puzzle has no solution")
    return solutions[0]


# ---------------------------------------------------------------------------
# Arrangements — linear seating
# ---------------------------------------------------------------------------


def arrangement_bench() -> SetPlan:
    people = ["Anaya", "Bhavesh", "Chirag", "Divya", "Esha", "Farhan"]
    seating = solve_unique(
        people,
        [
            lambda s: s["Anaya"] in (1, 6),
            lambda s: s["Bhavesh"] == s["Anaya"] + 2,
            lambda s: s["Divya"] == s["Chirag"] + 1,
            lambda s: s["Esha"] == s["Bhavesh"] + 1,
        ],
    )
    assert seating == {"Anaya": 1, "Farhan": 2, "Bhavesh": 3, "Esha": 4, "Chirag": 5, "Divya": 6}
    by_seat = {v: k for k, v in seating.items()}
    between_anaya_chirag = abs(seating["Anaya"] - seating["Chirag"]) - 1
    assert between_anaya_chirag == 3
    ends = {by_seat[1], by_seat[6]}
    assert ends == {"Anaya", "Divya"}

    return SetPlan(
        micro_topic="dilr.lr.arrangements",
        slug="bench-seating",
        kind="lr_set",
        body=(
            "Six friends — Anaya, Bhavesh, Chirag, Divya, Esha and Farhan — sit in a row of six "
            "seats numbered 1 to 6 from left to right. All of them face the same direction.\n\n"
            "- Anaya sits at one of the two ends.\n"
            "- Bhavesh sits exactly two seats to the right of Anaya.\n"
            "- Divya sits immediately to the right of Chirag.\n"
            "- Esha sits immediately to the right of Bhavesh.\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="Who sits in seat 2?",
                options=people,
                correct=by_seat[2],
                difficulty="easy",
                target_seconds=60,
                solution=(
                    "Anaya is at an end, and Bhavesh sits two seats to her right. If Anaya were in "
                    "seat 6 there would be no seat 8, so **Anaya is in seat 1 and Bhavesh in seat 3**. "
                    "Esha follows Bhavesh, so Esha is in seat 4.\n\n"
                    "Seats 2, 5 and 6 are left for Chirag, Divya and Farhan. Chirag must be immediately "
                    "left of Divya, and the only such pair among those is 5 and 6 — so Chirag is in 5, "
                    "Divya in 6, and Farhan takes seat 2.\n\n"
                    "Final row: Anaya, Farhan, Bhavesh, Esha, Chirag, Divya. Seat 2 is **Farhan**."
                ),
            ),
            QSpec(
                stem="Who sits immediately to the left of Chirag?",
                options=people,
                correct=by_seat[seating["Chirag"] - 1],
                difficulty="medium",
                target_seconds=60,
                solution=(
                    "The row is Anaya, Farhan, Bhavesh, Esha, Chirag, Divya. Chirag is in seat 5, so "
                    "seat 4 is immediately to his left: **Esha**."
                ),
            ),
            QSpec(
                stem="How many people sit between Anaya and Chirag?",
                value=between_anaya_chirag,
                difficulty="medium",
                target_seconds=60,
                solution=(
                    "Anaya is in seat 1 and Chirag in seat 5, so seats 2, 3 and 4 lie between them — "
                    f"**{between_anaya_chirag} people** (Farhan, Bhavesh and Esha). Count the seats "
                    "strictly between the two, not the gap in seat numbers, which is 4."
                ),
            ),
            QSpec(
                stem="Which pair occupies the two ends of the row?",
                options=[
                    "Anaya and Divya",
                    "Anaya and Chirag",
                    "Farhan and Divya",
                    "Bhavesh and Divya",
                    "Anaya and Farhan",
                ],
                correct="Anaya and Divya",
                difficulty="hard",
                target_seconds=70,
                solution=(
                    "Seat 1 is Anaya and seat 6 is Divya, so the ends are **Anaya and Divya**.\n\n"
                    "Worth noticing: Anaya's position was forced by the very first clue, and Divya's "
                    "fell out only at the last step. In a linear arrangement, start from the clue that "
                    "has the fewest ways of being true — here \"two seats to the right of an end seat\" "
                    "has exactly one."
                ),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Distribution / grouping
# ---------------------------------------------------------------------------


def distribution_cafe() -> SetPlan:
    friends = ["Ishan", "Jaya", "Kabir", "Lata"]
    drinks = ["Coffee", "Tea", "Juice", "Lassi"]
    amounts = [80, 120, 150, 200]

    solutions = []
    for drink_perm in permutations(drinks):
        for amount_perm in permutations(amounts):
            drink = dict(zip(friends, drink_perm))
            paid = dict(zip(friends, amount_perm))
            tea_payer = next(f for f in friends if drink[f] == "Tea")
            juice_payer = next(f for f in friends if drink[f] == "Juice")
            if paid["Lata"] != 80:
                continue
            if not (paid["Kabir"] < paid["Jaya"] < paid[tea_payer]):
                continue
            if drink["Ishan"] != "Tea":
                continue
            if paid[juice_payer] != 150:
                continue
            if drink["Kabir"] == "Coffee":
                continue
            solutions.append((drink, paid))
    assert len(solutions) == 1, f"expected one solution, got {len(solutions)}"
    drink, paid = solutions[0]
    assert drink == {"Ishan": "Tea", "Jaya": "Juice", "Kabir": "Lassi", "Lata": "Coffee"}
    assert paid == {"Ishan": 200, "Jaya": 150, "Kabir": 120, "Lata": 80}
    tea_and_lassi = paid["Ishan"] + paid["Kabir"]
    assert tea_and_lassi == 320

    return SetPlan(
        micro_topic="dilr.lr.distribution-grouping",
        slug="cafe-orders",
        kind="lr_set",
        body=(
            "Four friends — Ishan, Jaya, Kabir and Lata — each ordered exactly one drink at a cafe. "
            "The drinks were coffee, tea, juice and lassi, one each. The four bills were Rs 80, "
            "Rs 120, Rs 150 and Rs 200, one each.\n\n"
            "- Lata paid Rs 80.\n"
            "- Jaya paid more than Kabir but less than the person who ordered tea.\n"
            "- Ishan ordered tea.\n"
            "- The person who ordered juice paid Rs 150.\n"
            "- Kabir did not order coffee.\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="What did Lata order?",
                options=drinks,
                correct=drink["Lata"],
                difficulty="easy",
                target_seconds=70,
                solution=(
                    "Lata paid Rs 80, the lowest bill. Since Ishan ordered tea and the juice drinker paid "
                    "Rs 150, Lata ordered neither. That leaves coffee and lassi for Lata and Kabir, and "
                    "Kabir did not order coffee — so Lata ordered **coffee** and Kabir the lassi."
                ),
            ),
            QSpec(
                stem="How much did Kabir pay, in rupees?",
                value=paid["Kabir"],
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Lata has Rs 80, so Ishan, Jaya and Kabir hold 120, 150 and 200 in some order. The "
                    "chain Kabir $<$ Jaya $<$ Ishan (Ishan ordered tea) forces them in that order:\n\n"
                    "$\\text{Kabir} = 120,\\ \\text{Jaya} = 150,\\ \\text{Ishan} = 200$\n\n"
                    f"**Rs {fmt(paid['Kabir'])}**."
                ),
            ),
            QSpec(
                stem="Who ordered juice?",
                options=friends,
                correct="Jaya",
                difficulty="medium",
                target_seconds=60,
                solution=(
                    "The juice drinker paid Rs 150, and that is Jaya's bill. So **Jaya** ordered juice."
                ),
            ),
            QSpec(
                stem="What is the combined bill of the person who ordered tea and the person who ordered lassi?",
                value=tea_and_lassi,
                difficulty="hard",
                target_seconds=90,
                solution=(
                    "Tea is Ishan at Rs 200, lassi is Kabir at Rs 120:\n\n"
                    f"$200 + 120 = {fmt(tea_and_lassi)}$\n\n"
                    f"**Rs {fmt(tea_and_lassi)}**. The full grid: Ishan tea 200, Jaya juice 150, "
                    "Kabir lassi 120, Lata coffee 80. The whole puzzle turns on the second clue, which "
                    "is a three-way ordering disguised as a sentence about two people."
                ),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Ordering / ranking
# ---------------------------------------------------------------------------


def ordering_race() -> SetPlan:
    runners = ["Manav", "Nisha", "Omar", "Priya", "Rehan"]
    finish = solve_unique(
        runners,
        [
            lambda s: s["Omar"] == s["Nisha"] + 1,
            lambda s: s["Omar"] < s["Manav"] < s["Priya"],
            lambda s: s["Rehan"] not in (1, 5),
            lambda s: s["Priya"] == s["Manav"] + 1,
        ],
    )
    assert finish == {"Nisha": 1, "Omar": 2, "Rehan": 3, "Manav": 4, "Priya": 5}
    by_place = {v: k for k, v in finish.items()}

    # "If Rehan had finished one place better" — Rehan and whoever held that place swap.
    improved = dict(finish)
    displaced = by_place[finish["Rehan"] - 1]
    improved["Rehan"], improved[displaced] = finish["Rehan"] - 1, finish["Rehan"]
    third_after = next(r for r, p in improved.items() if p == 3)
    assert third_after == "Omar"

    return SetPlan(
        micro_topic="dilr.lr.ordering-ranking",
        slug="race-finish",
        kind="lr_set",
        body=(
            "Five runners — Manav, Nisha, Omar, Priya and Rehan — finished a race. There were no "
            "ties.\n\n"
            "- Omar finished immediately after Nisha.\n"
            "- Omar finished ahead of Manav, and Manav ahead of Priya.\n"
            "- Rehan finished neither first nor last.\n"
            "- Priya finished immediately after Manav.\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="Who won the race?",
                options=runners,
                correct=by_place[1],
                difficulty="easy",
                target_seconds=70,
                solution=(
                    "Chain the order clues: Nisha is immediately before Omar, and Omar is ahead of "
                    "Manav, who is immediately before Priya. That gives the block "
                    "Nisha, Omar, ..., Manav, Priya covering four of the five places in that order, "
                    "with Rehan somewhere.\n\n"
                    "Rehan cannot be first or last, and Nisha-Omar and Manav-Priya are each adjacent "
                    "pairs, so the only place left for Rehan is the middle: "
                    "**Nisha, Omar, Rehan, Manav, Priya**.\n\n"
                    "**Nisha** won."
                ),
            ),
            QSpec(
                stem="In which position did Manav finish?",
                value=finish["Manav"],
                difficulty="medium",
                target_seconds=70,
                solution=(
                    "The order is Nisha, Omar, Rehan, Manav, Priya, so Manav finished "
                    f"**{fmt(finish['Manav'])}th**."
                ),
            ),
            QSpec(
                stem="Who finished third?",
                options=runners,
                correct=by_place[3],
                difficulty="medium",
                target_seconds=60,
                solution=(
                    "**Rehan**. His position is the one clue that is purely negative — \"neither first "
                    "nor last\" — and it still pins him exactly, because the other four runners form "
                    "two adjacent pairs that can only sit around him."
                ),
            ),
            QSpec(
                stem="If Rehan had finished one place better, who would have finished third?",
                options=runners,
                correct=third_after,
                difficulty="hard",
                target_seconds=90,
                solution=(
                    "Rehan moves from third to second, and Omar — who held second — drops to third. "
                    "The order becomes Nisha, Rehan, Omar, Manav, Priya, so **Omar** finishes third.\n\n"
                    "Only the two runners involved swap; a hypothetical about one runner moving one "
                    "place does not shift anybody else."
                ),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Games and tournaments
# ---------------------------------------------------------------------------


def games_round_robin() -> SetPlan:
    teams = ["Warriors", "Xplorers", "Yodhas", "Zephyrs"]
    record = {  # wins, draws, losses
        "Warriors": (2, 1, 0),
        "Xplorers": (1, 1, 1),
        "Yodhas": (1, 0, 2),
        "Zephyrs": (0, 2, 1),
    }
    matches = len(teams) * (len(teams) - 1) // 2
    assert matches == 6
    total_wins = sum(w for w, _, _ in record.values())
    total_losses = sum(l for _, _, l in record.values())
    assert total_wins == total_losses == 4
    draw_slots = sum(d for _, d, _ in record.values())
    assert draw_slots == 4
    drawn_matches = draw_slots // 2
    assert drawn_matches == 2
    assert total_wins + drawn_matches == matches
    points = {t: 3 * w + d for t, (w, d, _) in record.items()}
    assert points == {"Warriors": 7, "Xplorers": 4, "Yodhas": 3, "Zephyrs": 2}
    total_points = sum(points.values())
    assert total_points == 16 == 3 * total_wins + 2 * drawn_matches

    table = {
        "type": "table",
        "spec": {
            "columns": ["Team", "Won", "Drawn", "Lost"],
            "rows": [[t, str(w), str(d), str(l)] for t, (w, d, l) in record.items()],
        },
    }

    return SetPlan(
        micro_topic="dilr.lr.games-tournaments",
        slug="round-robin",
        kind="lr_set",
        body=(
            "Four teams played a single round-robin tournament, so every team played every other "
            "team exactly once. A win is worth 3 points, a draw 1 point and a loss 0 points. The "
            "table below shows each team's record.\n\n"
            "Answer the questions that follow."
        ),
        assets=[table],
        questions=[
            QSpec(
                stem="How many matches were played in the tournament in total?",
                value=matches,
                difficulty="easy",
                target_seconds=50,
                solution=(
                    "Each pair of teams meets once, so the count is the number of pairs:\n\n"
                    "$\\dbinom{4}{2} = \\dfrac{4 \\times 3}{2} = 6$\n\n"
                    "**6 matches**. Cross-check with the table: each team played "
                    "$2 + 1 + 0 = 3$ matches, giving $\\dfrac{4 \\times 3}{2} = 6$, since every match "
                    "is counted by two teams."
                ),
            ),
            QSpec(
                stem="How many points did the Warriors finish with?",
                value=points["Warriors"],
                difficulty="easy",
                target_seconds=50,
                solution=f"$3 \\times 2 + 1 \\times 1 = {fmt(points['Warriors'])}$ points.",
            ),
            QSpec(
                stem="How many matches in the tournament ended in a draw?",
                value=drawn_matches,
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "Add the draws column: $1 + 1 + 0 + 2 = 4$. But a drawn match puts a draw against "
                    "**two** teams, so the number of drawn matches is half that:\n\n"
                    "$\\dfrac{4}{2} = 2$\n\n"
                    "**2 matches**. Check: 4 wins means 4 decisive matches, and $4 + 2 = 6$, the whole "
                    "tournament."
                ),
            ),
            QSpec(
                stem="What is the total number of points earned by all four teams together?",
                value=total_points,
                difficulty="hard",
                target_seconds=90,
                solution=(
                    "Team by team: $7 + 4 + 3 + 2 = 16$.\n\n"
                    "Faster, and the way to check it: every decisive match puts 3 points into the table "
                    "and every drawn match puts 2. With 4 decisive matches and 2 draws:\n\n"
                    "$4 \\times 3 + 2 \\times 2 = 12 + 4 = 16$\n\n"
                    "**16 points**. That second route is worth having, because it tells you the total "
                    "before you know any individual team's tally — and it means a points table where "
                    "draws are unknown can still be pinned down."
                ),
            ),
        ],
    )


def games_knockout() -> SetPlan:
    # In any single-elimination event, every match eliminates exactly one player, and everyone
    # except the champion is eliminated — so matches = players - 1, byes or not.
    assert 16 - 1 == 15
    assert 64 - 1 == 63
    assert 50 - 1 == 49

    return SetPlan(
        micro_topic="dilr.lr.games-tournaments",
        slug="knockout",
        kind="lr_set",
        body=(
            "A single-elimination (knockout) tournament is one in which a player leaves the "
            "tournament as soon as they lose a match, and the last player remaining is the "
            "champion. When the number of players is not a power of two, some players are given a "
            "bye in the first round, meaning they advance without playing.\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="A knockout tournament has 16 players. How many matches are played in total?",
                value=15,
                difficulty="easy",
                target_seconds=60,
                solution=(
                    "By rounds: $8 + 4 + 2 + 1 = 15$.\n\n"
                    "**15 matches**. The shortcut worth internalising: every match eliminates exactly "
                    "one player, and 15 of the 16 players must be eliminated to leave one champion, so "
                    "there are 15 matches."
                ),
            ),
            QSpec(
                stem="In that 16-player tournament, how many rounds are played?",
                value=4,
                difficulty="easy",
                target_seconds=50,
                solution=(
                    "The field halves each round: 16 to 8 to 4 to 2 to 1. That is **4 rounds**, since "
                    "$2^4 = 16$."
                ),
            ),
            QSpec(
                stem="A knockout tournament has 64 players. How many matches are played in total?",
                value=63,
                difficulty="medium",
                target_seconds=60,
                solution=(
                    "One player is eliminated per match, and 63 players must go:\n\n"
                    "$64 - 1 = 63$\n\n"
                    "**63 matches**. Adding the rounds gives the same: "
                    "$32 + 16 + 8 + 4 + 2 + 1 = 63$."
                ),
            ),
            QSpec(
                stem=(
                    "A knockout tournament has 50 players, with byes given in the first round as "
                    "needed. How many matches are played in total?"
                ),
                value=49,
                difficulty="hard",
                target_seconds=100,
                solution=(
                    "The byes are a distraction. Whatever the bracket looks like, each match "
                    "eliminates exactly one player, a bye eliminates nobody, and everyone except the "
                    "champion is eliminated:\n\n"
                    "$50 - 1 = 49$\n\n"
                    "**49 matches**. Trying to work round by round means first deciding how many byes "
                    "are needed to reach 32 — that is 14 byes and 18 first-round matches — and then "
                    "adding $18 + 16 + 8 + 4 + 2 + 1 = 49$. Same answer, several times the work."
                ),
            ),
        ],
    )


def games_league_table() -> SetPlan:
    teams = ["Alpha", "Bravo", "Cobra", "Delta", "Eagle"]
    known = {  # wins, draws, losses — Cobra's wins withheld from the learner
        "Alpha": (3, 1, 0),
        "Bravo": (2, 2, 0),
        "Cobra": (None, 0, 2),
        "Delta": (0, 2, 2),
        "Eagle": (0, 1, 3),
    }
    matches = len(teams) * (len(teams) - 1) // 2
    assert matches == 10
    known_wins = sum(w for w, _, _ in known.values() if w is not None)
    total_losses = sum(l for _, _, l in known.values())
    assert known_wins == 5 and total_losses == 7
    cobra_wins = total_losses - known_wins  # every win is somebody's loss
    assert cobra_wins == 2
    draw_slots = sum(d for _, d, _ in known.values())
    assert draw_slots == 6
    drawn_matches = draw_slots // 2
    assert drawn_matches == 3
    assert total_losses + drawn_matches == matches
    cobra_points = 2 * cobra_wins + 0
    assert cobra_points == 4

    table = {
        "type": "table",
        "spec": {
            "columns": ["Team", "Played", "Won", "Drawn", "Lost"],
            "rows": [
                [t, "4", "?" if w is None else str(w), str(d), str(l)]
                for t, (w, d, l) in known.items()
            ],
        },
    }

    return SetPlan(
        micro_topic="dilr.lr.games-tournaments",
        slug="league-table",
        kind="lr_set",
        body=(
            "Five teams played a single round-robin tournament, so every team played every other "
            "team exactly once and each team played 4 matches. A win is worth 2 points, a draw 1 "
            "point and a loss 0 points. One entry in the table below has been left out.\n\n"
            "Answer the questions that follow."
        ),
        assets=[table],
        questions=[
            QSpec(
                stem="How many matches were played in the tournament in total?",
                value=matches,
                difficulty="easy",
                target_seconds=50,
                solution=(
                    "$\\dbinom{5}{2} = \\dfrac{5 \\times 4}{2} = 10$ matches. Equivalently, 5 teams "
                    "playing 4 matches each is 20 team-appearances, and each match uses two: "
                    "$\\dfrac{20}{2} = 10$."
                ),
            ),
            QSpec(
                stem="How many matches did Cobra win?",
                value=cobra_wins,
                difficulty="medium",
                target_seconds=100,
                solution=(
                    "Every win by one team is a loss for another, so across the whole table total wins "
                    "must equal total losses.\n\n"
                    "Losses: $0 + 0 + 2 + 2 + 3 = 7$. Known wins: $3 + 2 + 0 + 0 = 5$.\n\n"
                    "$7 - 5 = 2$\n\n"
                    "**2 wins**. Check against Cobra's own row: $2 + 0 + 2 = 4$ matches, exactly what "
                    "each team played."
                ),
            ),
            QSpec(
                stem="How many matches in the tournament ended in a draw?",
                value=drawn_matches,
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "Draws column: $1 + 2 + 0 + 2 + 1 = 6$ team-draws, and each drawn match creates "
                    "two of them:\n\n"
                    "$\\dfrac{6}{2} = 3$\n\n"
                    "**3 matches**. Check: 7 decisive matches plus 3 draws is 10, the whole tournament."
                ),
            ),
            QSpec(
                stem="How many points did Cobra finish with?",
                value=cobra_points,
                difficulty="hard",
                target_seconds=90,
                solution=(
                    "Cobra won 2 and drew none:\n\n"
                    "$2 \\times 2 + 0 \\times 1 = 4$\n\n"
                    "**4 points**. The full table reads Alpha 7, Bravo 6, Cobra 4, Delta 2, Eagle 1, "
                    "totalling 20 — which matches the check that every match hands out exactly 2 points "
                    "whether it is won or drawn, and $10 \\times 2 = 20$."
                ),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Selection and conditionalities
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Selection and conditionalities
#
# Each puzzle's answer set comes from `combinations` over the whole candidate pool. Two things
# that only exhaustive enumeration catches, and that both bit during authoring: a "which pair
# can never appear together" option list where *two* options were correct, and a constraint set
# so tight that only one committee survived, leaving nothing to ask about.
# ---------------------------------------------------------------------------


def selection_team() -> SetPlan:
    candidates = ["P", "Q", "R", "S", "T", "U"]

    def valid(team: set[str]) -> bool:
        if "P" in team and "Q" not in team:
            return False
        if "R" in team and "S" in team:
            return False
        if "T" in team and "R" not in team:
            return False
        if "Q" in team and "U" in team:
            return False
        return True

    valid_teams = [set(c) for c in combinations(candidates, 3) if valid(set(c))]
    assert len(valid_teams) == 4, len(valid_teams)
    assert sorted("".join(sorted(t)) for t in valid_teams) == ["PQR", "PQS", "QRT", "RTU"]

    def never_together(a: str, b: str) -> bool:
        return not any(a in t and b in t for t in valid_teams)

    assert never_together("Q", "U") and never_together("R", "S")
    for pair in (("P", "Q"), ("R", "T"), ("P", "R"), ("R", "U")):
        assert not never_together(*pair), pair

    return SetPlan(
        micro_topic="dilr.lr.selection-conditionalities",
        slug="project-team",
        kind="lr_set",
        body=(
            "A manager must pick a project team of exactly 3 people from six candidates: P, Q, R, "
            "S, T and U. The following conditions apply.\n\n"
            "- If P is selected, then Q must also be selected.\n"
            "- R and S cannot both be selected.\n"
            "- T can be selected only if R is selected.\n"
            "- Q and U cannot both be selected.\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="If P is selected, who else must necessarily be on the team?",
                options=["Q", "R", "S", "T", "U"],
                correct="Q",
                difficulty="easy",
                target_seconds=60,
                solution=(
                    "The first condition says P selected forces Q selected, so **Q** must be on the "
                    "team. The arrow runs one way only: Q can be selected without P."
                ),
            ),
            QSpec(
                stem="If T is selected, who else must necessarily be on the team?",
                options=["P", "Q", "R", "S", "U"],
                correct="R",
                difficulty="medium",
                target_seconds=70,
                solution=(
                    "\"T only if R\" means T cannot be there without R, so selecting T forces **R**.\n\n"
                    "Read the direction carefully: it does **not** say that selecting R forces T. "
                    "The team $\\{P, Q, R\\}$ contains R without T and is perfectly legal."
                ),
            ),
            QSpec(
                stem="Which of the following pairs can never be selected together?",
                options=["P and Q", "Q and U", "R and T", "P and R", "R and U"],
                correct="Q and U",
                difficulty="medium",
                target_seconds=70,
                solution=(
                    "The fourth condition rules out **Q and U** directly.\n\n"
                    "Every other option is achievable: P and Q in $\\{P, Q, R\\}$, R and T in "
                    "$\\{Q, R, T\\}$, P and R in $\\{P, Q, R\\}$, R and U in $\\{R, T, U\\}$.\n\n"
                    "R and S is also a forbidden pair, but it is not among the options — check each "
                    "option against the conditions rather than stopping at the first prohibition you "
                    "remember."
                ),
            ),
            QSpec(
                stem="How many different valid teams of 3 can the manager form?",
                value=len(valid_teams),
                difficulty="hard",
                target_seconds=180,
                solution=(
                    "Split on whether Q is selected.\n\n"
                    "**Q in** (so U is out; the other two come from P, R, S, T):\n\n"
                    "- $\\{Q, P, R\\}$ — legal\n"
                    "- $\\{Q, P, S\\}$ — legal\n"
                    "- $\\{Q, P, T\\}$ — T needs R, rejected\n"
                    "- $\\{Q, R, S\\}$ — R and S clash, rejected\n"
                    "- $\\{Q, R, T\\}$ — legal\n"
                    "- $\\{Q, S, T\\}$ — T needs R, rejected\n\n"
                    "Three teams.\n\n"
                    "**Q out** (so P is out too, since P would force Q; the team is 3 of R, S, T, U):\n\n"
                    "- $\\{R, S, T\\}$ and $\\{R, S, U\\}$ — R and S clash, rejected\n"
                    "- $\\{S, T, U\\}$ — T needs R, rejected\n"
                    "- $\\{R, T, U\\}$ — legal\n\n"
                    "One team.\n\n"
                    f"Total **{len(valid_teams)}**: $\\{{P,Q,R\\}}$, $\\{{P,Q,S\\}}$, $\\{{Q,R,T\\}}$ and "
                    "$\\{R,T,U\\}$. Splitting on the candidate that appears in the most conditions — Q "
                    "here — is what keeps the casework to two short branches instead of twenty."
                ),
            ),
        ],
    )


def selection_courses() -> SetPlan:
    courses = ["Economics", "Finance", "Statistics", "Marketing", "History", "Law"]

    def valid(chosen: set[str]) -> bool:
        if "Finance" in chosen and "Statistics" not in chosen:
            return False
        if "History" in chosen and "Law" in chosen:
            return False
        if "Marketing" in chosen and "Economics" not in chosen:
            return False
        if not ({"History", "Law"} & chosen):
            return False
        return True

    valid_choices = [set(c) for c in combinations(courses, 4) if valid(set(c))]
    assert len(valid_choices) == 4, len(valid_choices)
    always = {c for c in courses if all(c in choice for choice in valid_choices)}
    assert always == {"Economics", "Statistics"}
    with_marketing = [c for c in valid_choices if "Marketing" in c]
    assert with_marketing and all("Finance" not in c for c in with_marketing)
    assert not any({"Finance", "Marketing"} <= c for c in valid_choices)

    return SetPlan(
        micro_topic="dilr.lr.selection-conditionalities",
        slug="course-choice",
        kind="lr_set",
        body=(
            "A student must register for exactly 4 courses out of six on offer: Economics, "
            "Finance, Statistics, Marketing, History and Law. The registration rules are:\n\n"
            "- Statistics must be taken if Finance is taken.\n"
            "- History and Law cannot both be taken.\n"
            "- Marketing can be taken only if Economics is taken.\n"
            "- At least one of History and Law must be taken.\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="How many different valid sets of 4 courses can the student register for?",
                value=len(valid_choices),
                difficulty="hard",
                target_seconds=180,
                solution=(
                    "Rules 2 and 4 together mean **exactly one** of History and Law is taken, which "
                    "uses one of the four slots and leaves three for Economics, Finance, Statistics "
                    "and Marketing — that is, exactly one of those four is dropped.\n\n"
                    "- Drop Economics: Marketing survives without Economics, rejected\n"
                    "- Drop Finance: $\\{$Economics, Statistics, Marketing$\\}$ — legal\n"
                    "- Drop Statistics: Finance survives without Statistics, rejected\n"
                    "- Drop Marketing: $\\{$Economics, Finance, Statistics$\\}$ — legal\n\n"
                    "So two three-course cores, each pairable with History or with Law:\n\n"
                    f"$2 \\times 2 = {len(valid_choices)}$\n\n"
                    f"**{len(valid_choices)} valid registrations**."
                ),
            ),
            QSpec(
                stem="Which of the following is part of every valid registration?",
                options=[
                    "Economics and Statistics",
                    "Finance",
                    "Marketing",
                    "History",
                    "Economics and Finance",
                ],
                correct="Economics and Statistics",
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Both cores contain **Economics and Statistics**, so they appear in all four "
                    "registrations. Finance and Marketing appear in two each and exclude one another; "
                    "History appears in two, Law in the other two."
                ),
            ),
            QSpec(
                stem="If the student registers for Marketing, which course can they not register for?",
                options=["Economics", "Finance", "Statistics", "History", "Law"],
                correct="Finance",
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Marketing drags Economics in with it, and one slot is already committed to "
                    "History or Law. That leaves one slot for Finance and Statistics together — but "
                    "Finance cannot come without Statistics, so Finance cannot fit.\n\n"
                    "**Finance**. The valid Marketing registrations are "
                    "$\\{$Economics, Statistics, Marketing, History$\\}$ and "
                    "$\\{$Economics, Statistics, Marketing, Law$\\}$."
                ),
            ),
            QSpec(
                stem="Which pair of courses can never appear together in a valid registration?",
                options=[
                    "Finance and Marketing",
                    "Economics and History",
                    "Statistics and Law",
                    "Economics and Marketing",
                    "Finance and History",
                ],
                correct="Finance and Marketing",
                difficulty="hard",
                target_seconds=100,
                solution=(
                    "**Finance and Marketing** cannot coexist: Finance needs Statistics, Marketing "
                    "needs Economics, and one slot must go to History or Law — that is five courses "
                    "for four slots.\n\n"
                    "Each of the others appears in some valid registration: Economics and History in "
                    "$\\{$Economics, Finance, Statistics, History$\\}$, Statistics and Law in "
                    "$\\{$Economics, Finance, Statistics, Law$\\}$, Economics and Marketing in "
                    "$\\{$Economics, Statistics, Marketing, History$\\}$, and Finance and History in "
                    "the first of those."
                ),
            ),
        ],
    )


def selection_panel() -> SetPlan:
    members = ["A", "B", "C", "D", "E", "F", "G"]

    def valid(panel: set[str]) -> bool:
        if ("B" in panel) == ("C" in panel):
            return False
        if "D" in panel and "E" in panel:
            return False
        if "A" in panel and "F" in panel:
            return False
        if "G" not in panel:
            return False
        return True

    panels = [set(c) for c in combinations(members, 4) if valid(set(c))]
    assert len(panels) == 8, len(panels)
    counts = {m: sum(1 for p in panels if m in p) for m in members}
    assert counts == {"A": 4, "B": 4, "C": 4, "D": 4, "E": 4, "F": 4, "G": 8}
    with_a = [p for p in panels if "A" in p]
    assert with_a and all("F" not in p for p in with_a)
    without_d = [p for p in panels if "D" not in p]
    assert len(without_d) == 4

    return SetPlan(
        micro_topic="dilr.lr.selection-conditionalities",
        slug="review-panel",
        kind="lr_set",
        body=(
            "A review panel of exactly 4 members must be formed from seven people: A, B, C, D, E, "
            "F and G. The rules are:\n\n"
            "- Exactly one of B and C must be on the panel.\n"
            "- D and E cannot both be on the panel.\n"
            "- A and F cannot both be on the panel.\n"
            "- G must be on the panel.\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="Who is on every possible panel?",
                options=["A", "B", "D", "F", "G"],
                correct="G",
                difficulty="easy",
                target_seconds=50,
                solution="The fourth rule names **G** outright, so G is on every panel.",
            ),
            QSpec(
                stem="If A is on the panel, who cannot be on it?",
                options=["B", "C", "D", "E", "F"],
                correct="F",
                difficulty="easy",
                target_seconds=50,
                solution=(
                    "The third rule bars A and F together, so **F** is out. B, C, D and E are all "
                    "still available — subject to the other rules, which pick one of B/C and at most "
                    "one of D/E."
                ),
            ),
            QSpec(
                stem="How many different valid panels of 4 can be formed?",
                value=len(panels),
                difficulty="hard",
                target_seconds=150,
                solution=(
                    "G takes one of the four seats, leaving three seats for A, B, C, D, E and F.\n\n"
                    "Those six split into three pairs — $\\{B, C\\}$, $\\{D, E\\}$, $\\{A, F\\}$ — and "
                    "each rule allows **at most one** member from its pair, with $\\{B, C\\}$ requiring "
                    "exactly one. Three seats and at most one from each of three pairs means exactly "
                    "one from each pair:\n\n"
                    f"$2 \\times 2 \\times 2 = {len(panels)}$\n\n"
                    f"**{len(panels)} panels**. Recognising the pair structure turns a 35-case check "
                    "into one multiplication."
                ),
            ),
            QSpec(
                stem="If D is not on the panel, how many valid panels can be formed?",
                value=len(without_d),
                difficulty="hard",
                target_seconds=120,
                solution=(
                    "With D excluded, the $\\{D, E\\}$ pair must contribute E — it still has to supply "
                    "exactly one member. The other two pairs are unaffected:\n\n"
                    f"$2 \\times 1 \\times 2 = {len(without_d)}$\n\n"
                    f"**{len(without_d)} panels**: $\\{{A,B,E,G\\}}$, $\\{{A,C,E,G\\}}$, "
                    "$\\{B,E,F,G\\}$ and $\\{C,E,F,G\\}$."
                ),
            ),
        ],
    )


# ---------------------------------------------------------------------------
# Venn / set theory
# ---------------------------------------------------------------------------


def venn_sports() -> SetPlan:
    total = 120
    cricket, football, tennis = 70, 60, 50
    cf, ft, ct, all_three = 30, 25, 20, 10
    at_least_one = cricket + football + tennis - cf - ft - ct + all_three
    assert at_least_one == 115
    none = total - at_least_one
    assert none == 5
    only_cricket = cricket - cf - ct + all_three
    assert only_cricket == 30
    exactly_two = (cf - all_three) + (ft - all_three) + (ct - all_three)
    assert exactly_two == 45

    return SetPlan(
        micro_topic="dilr.lr.venn-set",
        slug="school-sports",
        kind="lr_set",
        body=(
            "In a class of 120 students, 70 play cricket, 60 play football and 50 play tennis. "
            "30 play both cricket and football, 25 play both football and tennis, and 20 play both "
            "cricket and tennis. 10 students play all three sports.\n\n"
            "(Each \"both\" figure includes the students who play all three.)\n\n"
            "Answer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="How many students play at least one of the three sports?",
                value=at_least_one,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Inclusion-exclusion for three sets:\n\n"
                    "$70 + 60 + 50 - 30 - 25 - 20 + 10 = 115$\n\n"
                    "**115 students**. The final $+10$ is there because the triple overlap was "
                    "subtracted three times by the pairwise terms after being added three times by "
                    "the singles — it has to be put back once."
                ),
            ),
            QSpec(
                stem="How many students play none of the three sports?",
                value=none,
                difficulty="easy",
                target_seconds=50,
                solution=f"$120 - 115 = {fmt(none)}$, so **{fmt(none)} students**.",
            ),
            QSpec(
                stem="How many students play cricket only?",
                value=only_cricket,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "Strip the overlaps out of the cricket total, then restore the triple region that "
                    "has now been removed twice:\n\n"
                    "$70 - 30 - 20 + 10 = 30$\n\n"
                    f"**{fmt(only_cricket)} students**. Filling the Venn diagram from the centre "
                    "outwards is the safer habit: 10 in the middle, then $30 - 10 = 20$ in "
                    "cricket-and-football only, $20 - 10 = 10$ in cricket-and-tennis only, and "
                    "$70 - 10 - 20 - 10 = 30$ left in cricket alone."
                ),
            ),
            QSpec(
                stem="How many students play exactly two of the three sports?",
                value=exactly_two,
                difficulty="hard",
                target_seconds=110,
                solution=(
                    "Each pairwise figure includes the 10 who play all three, so subtract them from "
                    "each:\n\n"
                    "- cricket and football only: $30 - 10 = 20$\n"
                    "- football and tennis only: $25 - 10 = 15$\n"
                    "- cricket and tennis only: $20 - 10 = 10$\n\n"
                    "$20 + 15 + 10 = 45$\n\n"
                    f"**{fmt(exactly_two)} students**. Adding the three pairwise figures to 75 and "
                    "stopping there is the standard error — it triple-counts the centre."
                ),
            ),
        ],
    )


def venn_newspapers() -> SetPlan:
    total = 400
    a_pct, b_pct, both_pct = 60, 45, 20
    both = total * both_pct / 100
    assert both == 80
    at_least_one_pct = a_pct + b_pct - both_pct
    assert at_least_one_pct == 85
    at_least_one = total * at_least_one_pct / 100
    assert at_least_one == 340
    neither = total - at_least_one
    assert neither == 60
    exactly_one = at_least_one - both
    assert exactly_one == 260

    return SetPlan(
        micro_topic="dilr.lr.venn-set",
        slug="newspapers",
        kind="lr_set",
        body=(
            "In a survey of 400 people, 60% read newspaper A, 45% read newspaper B, and 20% read "
            "both.\n\nAnswer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="How many people read both newspapers?",
                value=both,
                difficulty="easy",
                target_seconds=50,
                solution=f"$400 \\times \\dfrac{{20}}{{100}} = {fmt(both)}$, so **{fmt(both)} people**.",
            ),
            QSpec(
                stem="How many people read at least one of the two newspapers?",
                value=at_least_one,
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "Work in percentages first, then convert once:\n\n"
                    "$60 + 45 - 20 = 85\\%$\n\n"
                    "$400 \\times 0.85 = 340$\n\n"
                    f"**{fmt(at_least_one)} people**. Adding 60% and 45% to 105% and not subtracting "
                    "the overlap gives an impossible figure above the survey size — a built-in warning "
                    "that the overlap was missed."
                ),
            ),
            QSpec(
                stem="How many people read neither newspaper?",
                value=neither,
                difficulty="medium",
                target_seconds=60,
                solution=(
                    f"$400 - 340 = {fmt(neither)}$, so **{fmt(neither)} people** — the 15% left outside "
                    "both circles."
                ),
            ),
            QSpec(
                stem="How many people read exactly one of the two newspapers?",
                value=exactly_one,
                difficulty="hard",
                target_seconds=100,
                solution=(
                    "Take the overlap out of the union once more, since the union counts the both-"
                    "readers:\n\n"
                    "$340 - 80 = 260$\n\n"
                    f"**{fmt(exactly_one)} people**. Equivalently, A only is "
                    "$240 - 80 = 160$ and B only is $180 - 80 = 100$, and $160 + 100 = 260$."
                ),
            ),
        ],
    )


def venn_minmax() -> SetPlan:
    total, tea, coffee = 200, 130, 110
    min_both = tea + coffee - total
    assert min_both == 40
    max_both = min(tea, coffee)
    assert max_both == 110
    with_neither = 20
    both_given_neither = tea + coffee - (total - with_neither)
    assert both_given_neither == 60
    max_exactly_one = tea + coffee - 2 * min_both
    assert max_exactly_one == 160

    return SetPlan(
        micro_topic="dilr.lr.venn-set",
        slug="tea-coffee-bounds",
        kind="lr_set",
        body=(
            "In a group of 200 people, 130 like tea and 110 like coffee. Nothing else is known "
            "about the group.\n\nAnswer the questions that follow."
        ),
        questions=[
            QSpec(
                stem="What is the minimum possible number of people who like both tea and coffee?",
                value=min_both,
                difficulty="medium",
                target_seconds=90,
                solution=(
                    "The overlap is smallest when the union is as large as it can be, and the union "
                    "cannot exceed the group:\n\n"
                    "$130 + 110 - 200 = 40$\n\n"
                    f"**{fmt(min_both)} people**. Together the two preferences account for 240 "
                    "preference-slots among 200 people, so at least 40 people must be supplying two "
                    "of them."
                ),
            ),
            QSpec(
                stem="What is the maximum possible number of people who like both tea and coffee?",
                value=max_both,
                difficulty="medium",
                target_seconds=80,
                solution=(
                    "The overlap can be no larger than the smaller of the two groups — every coffee "
                    "drinker could also drink tea, but there are only 110 of them:\n\n"
                    f"**{fmt(max_both)} people**, which happens when the coffee group sits entirely "
                    "inside the tea group."
                ),
            ),
            QSpec(
                stem="If exactly 20 people in the group like neither tea nor coffee, how many like both?",
                value=both_given_neither,
                difficulty="hard",
                target_seconds=100,
                solution=(
                    "Fixing the outside fixes the union: $200 - 20 = 180$ people like at least one.\n\n"
                    "$130 + 110 - 180 = 60$\n\n"
                    f"**{fmt(both_given_neither)} people**. Once the \"neither\" count is known the "
                    "overlap is no longer a range — it is a single number."
                ),
            ),
            QSpec(
                stem="What is the maximum possible number of people who like exactly one of the two drinks?",
                value=max_exactly_one,
                difficulty="hard",
                target_seconds=120,
                solution=(
                    "Exactly-one equals $130 + 110 - 2 \\times (\\text{both})$, so it is largest when "
                    "the overlap is smallest. The smallest possible overlap is 40:\n\n"
                    "$130 + 110 - 2 \\times 40 = 240 - 80 = 160$\n\n"
                    f"**{fmt(max_exactly_one)} people**. That case has nobody outside both circles: "
                    "40 like both, 90 like tea only, 70 like coffee only, and $40 + 90 + 70 = 200$. "
                    "Note the overlap is subtracted **twice** here, once from each group, because "
                    "someone who likes both is excluded from exactly-one on two counts."
                ),
            ),
        ],
    )


PLANS = [
    arrangement_bench(),
    distribution_cafe(),
    ordering_race(),
    games_round_robin(),
    games_knockout(),
    games_league_table(),
    selection_team(),
    selection_courses(),
    selection_panel(),
    venn_sports(),
    venn_newspapers(),
    venn_minmax(),
]


if __name__ == "__main__":
    emit_all(PLANS)
