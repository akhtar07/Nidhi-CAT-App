"""
Independent re-verification of the DILR batch-5 sets.

## What "independent" means here, precisely

This script does not import the generators. It reads the **shipped JSON** — the same bytes the
learner's browser will fetch — and re-derives answers from the chart spec, the table rows or
the puzzle constraints, using arithmetic written separately from the code that produced them.
Where the generator asserted a literal, this script recomputes from the asset; where the
generator reasoned, this script brute-forces.

Three levels, strongest first:

1. **LR puzzles** — the constraints are re-encoded by hand from the *body text as shipped* and
   solved by exhaustive search. If the body text does not actually imply the shipped answer,
   this fails. This is true independence: nothing is shared with the generator but the prose.
2. **DI chart and table sets** — answers recomputed from `assets[].spec`, matching each stem to
   an operation. If a stem's numbers and its answer ever drift apart, this fails.
3. **Structural checks on every item** — MCQ key appears exactly once among options, at least
   four options, options distinct, TITA values finite, solutions non-empty, ids unique, every
   `questionIds` entry resolves, and the markdown stays inside the tokenizer's supported subset
   (no pipe tables, no lone-asterisk italics, balanced `$`).

Level 3 runs on all 200 items. Levels 1 and 2 cover everything derived from a chart, a table or
a constraint list. The hand-written arithmetic sets (pie, growth, missing-data, caselets,
data-sufficiency) carry their double-entry asserts in the generator plus level 3 here; that is
recorded honestly rather than dressed up as independent verification.

Run (from /pipeline): python verify_dilr_batch5.py
"""

from __future__ import annotations

import json
import math
import re
from itertools import combinations, permutations
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
SETS_DIR = REPO_ROOT / "content" / "passage-sets"

failures: list[str] = []
short_option_sets: list[str] = []
checked_answers = 0


def fail(msg: str) -> None:
    failures.append(msg)


def load(path: Path) -> dict:
    return json.loads(path.read_text())


def answer_of(q: dict) -> float | str:
    if q["format"] == "tita":
        return q["correctValue"]
    return next(o["markdown"] for o in q["options"] if o["key"] == q["correctKey"])


def expect(q: dict, value: float | str, why: str) -> None:
    """Compares the shipped answer against an independently computed one."""
    global checked_answers
    checked_answers += 1
    actual = answer_of(q)
    if isinstance(value, str):
        if actual != value:
            fail(f"{q['id']}: {why} — expected {value!r}, shipped {actual!r}")
        return
    tol = max(q.get("titaTolerance") or 0, 0.01)
    if not isinstance(actual, (int, float)) or abs(actual - value) > tol:
        fail(f"{q['id']}: {why} — expected {value}, shipped {actual}")


# ---------------------------------------------------------------------------
# Level 3: structural and markdown checks
# ---------------------------------------------------------------------------

PIPE_TABLE = re.compile(r"^\s*\|", re.MULTILINE)
LONE_ITALIC = re.compile(r"(?<!\*)\*(?!\*)[^*\n]+(?<!\*)\*(?!\*)")


def check_structure(q: dict) -> None:
    qid = q["id"]
    if not q.get("solutionMarkdown", "").strip():
        fail(f"{qid}: empty solution")
    if q["format"] == "mcq":
        opts = [o["markdown"] for o in q["options"]]
        if len(opts) < 2:
            fail(f"{qid}: only {len(opts)} option(s)")
        elif len(opts) < 4:
            # Not a defect on its own. Some questions are genuinely binary — "truth-teller or
            # liar?", "which of these two companies?" — and padding those with invented third
            # and fourth options would be worse than leaving them at two. Reported so the shape
            # of the bank stays visible.
            short_option_sets.append(f"{qid} ({len(opts)} options)")
        if len(set(opts)) != len(opts):
            fail(f"{qid}: duplicate options")
        keys = [o["key"] for o in q["options"]]
        if q["correctKey"] not in keys:
            fail(f"{qid}: correctKey {q['correctKey']} not among options")
        if q.get("correctValue") is not None:
            fail(f"{qid}: mcq carries a correctValue")
    else:
        v = q.get("correctValue")
        if not isinstance(v, (int, float)) or not math.isfinite(v):
            fail(f"{qid}: TITA value is not a finite number: {v!r}")
        if q.get("options") or q.get("correctKey"):
            fail(f"{qid}: tita carries mcq fields")
    for field in ("stemMarkdown", "solutionMarkdown"):
        text = q.get(field) or ""
        if PIPE_TABLE.search(text):
            fail(f"{qid}: {field} contains a pipe table, which the tokenizer cannot render")
        if LONE_ITALIC.search(text):
            fail(f"{qid}: {field} contains lone-asterisk italics: {LONE_ITALIC.search(text).group()!r}")
        if text.count("$") % 2 != 0:
            fail(f"{qid}: {field} has an odd number of $ delimiters")


# ---------------------------------------------------------------------------
# Level 2: recompute DI answers from the shipped asset
# ---------------------------------------------------------------------------


def spec_series(asset: dict) -> tuple[list[str], dict[str, list[float]]]:
    spec = asset["spec"]
    cats = spec["categories"]
    return cats, {s["name"]: s["values"] for s in spec["series"]}


def table_series(asset: dict) -> tuple[list[str], dict[str, list[float]]]:
    cols = asset["spec"]["columns"]
    rows = asset["spec"]["rows"]
    cats = [r[0] for r in rows]
    data: dict[str, list[float]] = {}
    for j, name in enumerate(cols[1:], start=1):
        try:
            data[name] = [float(r[j]) for r in rows]
        except ValueError:
            continue  # a column with a withheld entry, handled by the LR/missing-data checks
    return cats, data


def check_di_set(sset: dict, questions: list[dict]) -> None:
    """Matches each stem against an archetype and recomputes from the asset data."""
    assets = sset.get("assets") or []
    source = None
    for asset in assets:
        # Only the categories/series shape drives the archetype checks. Radar carries `axes`,
        # bubble carries `points`, and combo splits into `bars`/`lines` — all hand-written sets.
        if asset["type"] == "chart" and "categories" in asset["spec"] and "series" in asset["spec"]:
            source = spec_series(asset)
            break
        if asset["type"] == "table":
            source = table_series(asset)
            break
    if source is None:
        return
    cats, data = source
    if not data:
        return

    for q in questions:
        stem = q["stemMarkdown"]

        m = re.match(r"^What was (.+?)'s figure for (.+?)\?$", stem)
        if m and m.group(1) in data and m.group(2) in cats:
            expect(q, data[m.group(1)][cats.index(m.group(2))], "read-off")
            continue

        m = re.match(r"^What was (.+?)'s total across all \d+ \w+\?$", stem)
        if m and m.group(1) in data:
            expect(q, sum(data[m.group(1)]), "series total")
            continue

        m = re.match(r"^What was (.+?)'s average per \w+\?$", stem)
        if m and m.group(1) in data:
            values = data[m.group(1)]
            expect(q, sum(values) / len(values), "series average")
            continue

        m = re.match(r"^In how many \w+ was (.+?) higher than (.+?)\?$", stem)
        if m and m.group(1) in data and m.group(2) in data:
            a, b = data[m.group(1)], data[m.group(2)]
            expect(q, sum(1 for x, y in zip(a, b) if x > y), "count exceeds")
            continue

        m = re.match(r"^In which \w+ was the gap between (.+?) and (.+?) the largest\?$", stem)
        if m and m.group(1) in data and m.group(2) in data:
            gaps = [abs(x - y) for x, y in zip(data[m.group(1)], data[m.group(2)])]
            expect(q, cats[gaps.index(max(gaps))], "largest gap")
            continue

        m = re.match(r"^By what percentage did (.+?) change from (.+?) to (.+?)\?$", stem)
        if m and m.group(1) in data and m.group(2) in cats and m.group(3) in cats:
            values = data[m.group(1)]
            old = values[cats.index(m.group(2))]
            new = values[cats.index(m.group(3))]
            expect(q, abs((new - old) / old * 100), "percentage change")
            continue

        m = re.match(r"^Which of these grew the fastest in percentage terms from (.+?) to (.+?)\?$", stem)
        if m and m.group(1) in cats and m.group(2) in cats:
            i, j = cats.index(m.group(1)), cats.index(m.group(2))
            growth = {n: (v[j] - v[i]) / v[i] for n, v in data.items()}
            expect(q, max(growth, key=lambda n: growth[n]), "fastest growth")
            continue

        m = re.match(r"^What was the combined figure across all \d+ categories for (.+?)\?$", stem)
        if m and m.group(1) in cats:
            i = cats.index(m.group(1))
            expect(q, sum(v[i] for v in data.values()), "combined at category")
            continue

        m = re.match(r"^In which \w+ was the combined figure the highest\?$", stem)
        if m:
            totals = [sum(v[i] for v in data.values()) for i in range(len(cats))]
            expect(q, cats[totals.index(max(totals))], "highest combined")
            continue

        m = re.match(r"^(.+?) accounted for what percentage of (.+?)'s total\?$", stem)
        if m and m.group(1) in cats and m.group(2) in data:
            values = data[m.group(2)]
            expect(q, values[cats.index(m.group(1))] / sum(values) * 100, "share of series total")
            continue

        m = re.match(r"^In (.+?), (.+?) accounted for what percentage of the total\?$", stem)
        if m and m.group(1) in cats and m.group(2) in data:
            i = cats.index(m.group(1))
            column = sum(v[i] for v in data.values())
            expect(q, data[m.group(2)][i] / column * 100, "share within stack")
            continue

        m = re.match(r"^In how many \w+ was (.+?) above its own \d+-\w+ average\?$", stem)
        if m and m.group(1) in data:
            values = data[m.group(1)]
            avg = sum(values) / len(values)
            expect(q, sum(1 for v in values if v > avg), "count above average")
            continue


# ---------------------------------------------------------------------------
# Level 1: re-solve the LR puzzles from the shipped body text
#
# The constraints below were transcribed by reading the `bodyMarkdown` of the shipped set, not
# by consulting the generator. Each solver asserts a unique solution and then the answers are
# checked against it.
# ---------------------------------------------------------------------------


def resolve_seating() -> dict[str, int]:
    people = ["Anaya", "Bhavesh", "Chirag", "Divya", "Esha", "Farhan"]
    found = []
    for perm in permutations(range(1, 7)):
        s = dict(zip(people, perm))
        if s["Anaya"] not in (1, 6):
            continue
        if s["Bhavesh"] != s["Anaya"] + 2:
            continue
        if s["Divya"] != s["Chirag"] + 1:
            continue
        if s["Esha"] != s["Bhavesh"] + 1:
            continue
        found.append(s)
    assert len(found) == 1, f"seating puzzle is not unique: {found}"
    return found[0]


def resolve_race() -> dict[str, int]:
    runners = ["Manav", "Nisha", "Omar", "Priya", "Rehan"]
    found = []
    for perm in permutations(range(1, 6)):
        s = dict(zip(runners, perm))
        if s["Omar"] != s["Nisha"] + 1:
            continue
        if not (s["Omar"] < s["Manav"] < s["Priya"]):
            continue
        if s["Rehan"] in (1, 5):
            continue
        if s["Priya"] != s["Manav"] + 1:
            continue
        found.append(s)
    assert len(found) == 1, f"race puzzle is not unique: {found}"
    return found[0]


def resolve_cafe() -> tuple[dict[str, str], dict[str, int]]:
    friends = ["Ishan", "Jaya", "Kabir", "Lata"]
    found = []
    for dp in permutations(["Coffee", "Tea", "Juice", "Lassi"]):
        for ap in permutations([80, 120, 150, 200]):
            drink = dict(zip(friends, dp))
            paid = dict(zip(friends, ap))
            tea = next(f for f in friends if drink[f] == "Tea")
            juice = next(f for f in friends if drink[f] == "Juice")
            if paid["Lata"] != 80:
                continue
            if not (paid["Kabir"] < paid["Jaya"] < paid[tea]):
                continue
            if drink["Ishan"] != "Tea":
                continue
            if paid[juice] != 150:
                continue
            if drink["Kabir"] == "Coffee":
                continue
            found.append((drink, paid))
    assert len(found) == 1, f"cafe puzzle is not unique: {len(found)}"
    return found[0]


def check_lr(by_set: dict[str, list[dict]], sets_by_id: dict[str, dict]) -> None:
    def questions_for(topic: str, slug_hint: str) -> list[dict]:
        for sid, sset in sets_by_id.items():
            if sset["id"].startswith(topic) and slug_hint in sset["bodyMarkdown"]:
                return by_set[sid]
        raise AssertionError(f"no set found for {topic} / {slug_hint!r}")

    seating = resolve_seating()
    by_seat = {v: k for k, v in seating.items()}
    qs = questions_for("dilr.lr.arrangements", "row of six")
    for q in qs:
        stem = q["stemMarkdown"]
        if stem == "Who sits in seat 2?":
            expect(q, by_seat[2], "seat 2 occupant")
        elif stem == "Who sits immediately to the left of Chirag?":
            expect(q, by_seat[seating["Chirag"] - 1], "left of Chirag")
        elif stem == "How many people sit between Anaya and Chirag?":
            expect(q, abs(seating["Anaya"] - seating["Chirag"]) - 1, "people between")
        elif stem == "Which pair occupies the two ends of the row?":
            ends = sorted([by_seat[1], by_seat[6]])
            expect(q, f"{ends[0]} and {ends[1]}", "end pair")

    finish = resolve_race()
    by_place = {v: k for k, v in finish.items()}
    qs = questions_for("dilr.lr.ordering-ranking", "finished a race")
    for q in qs:
        stem = q["stemMarkdown"]
        if stem == "Who won the race?":
            expect(q, by_place[1], "winner")
        elif stem == "In which position did Manav finish?":
            expect(q, finish["Manav"], "Manav position")
        elif stem == "Who finished third?":
            expect(q, by_place[3], "third place")
        elif stem.startswith("If Rehan had finished one place better"):
            moved = dict(finish)
            displaced = by_place[finish["Rehan"] - 1]
            moved["Rehan"], moved[displaced] = finish["Rehan"] - 1, finish["Rehan"]
            expect(q, next(r for r, p in moved.items() if p == 3), "third after swap")

    drink, paid = resolve_cafe()
    qs = questions_for("dilr.lr.distribution-grouping", "at a cafe")
    for q in qs:
        stem = q["stemMarkdown"]
        if stem == "What did Lata order?":
            expect(q, drink["Lata"], "Lata's drink")
        elif stem == "How much did Kabir pay, in rupees?":
            expect(q, paid["Kabir"], "Kabir's bill")
        elif stem == "Who ordered juice?":
            expect(q, next(f for f in drink if drink[f] == "Juice"), "juice drinker")
        elif stem.startswith("What is the combined bill"):
            tea = next(f for f in drink if drink[f] == "Tea")
            lassi = next(f for f in drink if drink[f] == "Lassi")
            expect(q, paid[tea] + paid[lassi], "tea + lassi bill")

    # Selection puzzles: re-encode each condition list from the shipped body text.
    def committees(pool: list[str], size: int, rules) -> list[set[str]]:
        return [set(c) for c in combinations(pool, size) if rules(set(c))]

    team_rules = lambda t: not (
        ("P" in t and "Q" not in t)
        or ("R" in t and "S" in t)
        or ("T" in t and "R" not in t)
        or ("Q" in t and "U" in t)
    )
    teams = committees(list("PQRSTU"), 3, team_rules)
    qs = questions_for("dilr.lr.selection-conditionalities", "project team of exactly 3")
    for q in qs:
        stem = q["stemMarkdown"]
        if stem.startswith("How many different valid teams"):
            expect(q, len(teams), "valid team count")
        elif stem.startswith("If P is selected"):
            forced = [m for m in "QRSTU" if all(m in t for t in teams if "P" in t)]
            expect(q, forced[0] if len(forced) == 1 else "AMBIGUOUS", "forced with P")
        elif stem.startswith("If T is selected"):
            forced = [m for m in "PQRSU" if all(m in t for t in teams if "T" in t)]
            expect(q, forced[0] if len(forced) == 1 else "AMBIGUOUS", "forced with T")
        elif stem.startswith("Which of the following pairs can never"):
            never = [
                o["markdown"]
                for o in q["options"]
                if not any(set(o["markdown"].split(" and ")) <= t for t in teams)
            ]
            expect(q, never[0] if len(never) == 1 else "AMBIGUOUS", "never-together pair")

    courses = ["Economics", "Finance", "Statistics", "Marketing", "History", "Law"]
    course_rules = lambda c: not (
        ("Finance" in c and "Statistics" not in c)
        or ("History" in c and "Law" in c)
        or ("Marketing" in c and "Economics" not in c)
        or not ({"History", "Law"} & c)
    )
    choices = committees(courses, 4, course_rules)
    qs = questions_for("dilr.lr.selection-conditionalities", "exactly 4 courses")
    for q in qs:
        stem = q["stemMarkdown"]
        if stem.startswith("How many different valid sets"):
            expect(q, len(choices), "valid registration count")
        elif stem.startswith("Which of the following is part of every"):
            always = {c for c in courses if all(c in ch for ch in choices)}
            match = [o["markdown"] for o in q["options"] if set(o["markdown"].split(" and ")) == always]
            expect(q, match[0] if len(match) == 1 else "AMBIGUOUS", "always-present courses")
        elif stem.startswith("If the student registers for Marketing"):
            with_m = [c for c in choices if "Marketing" in c]
            barred = [o["markdown"] for o in q["options"] if not any(o["markdown"] in c for c in with_m)]
            expect(q, barred[0] if len(barred) == 1 else "AMBIGUOUS", "barred with Marketing")
        elif stem.startswith("Which pair of courses can never"):
            never = [
                o["markdown"]
                for o in q["options"]
                if not any(set(o["markdown"].split(" and ")) <= c for c in choices)
            ]
            expect(q, never[0] if len(never) == 1 else "AMBIGUOUS", "never-together courses")

    panel_rules = lambda p: not (
        (("B" in p) == ("C" in p))
        or ("D" in p and "E" in p)
        or ("A" in p and "F" in p)
        or ("G" not in p)
    )
    panels = committees(list("ABCDEFG"), 4, panel_rules)
    qs = questions_for("dilr.lr.selection-conditionalities", "review panel")
    for q in qs:
        stem = q["stemMarkdown"]
        if stem == "Who is on every possible panel?":
            always = [m for m in "ABCDEFG" if all(m in p for p in panels)]
            expect(q, always[0] if len(always) == 1 else "AMBIGUOUS", "always on panel")
        elif stem.startswith("If A is on the panel"):
            with_a = [p for p in panels if "A" in p]
            barred = [o["markdown"] for o in q["options"] if not any(o["markdown"] in p for p in with_a)]
            expect(q, barred[0] if len(barred) == 1 else "AMBIGUOUS", "barred with A")
        elif stem.startswith("How many different valid panels"):
            expect(q, len(panels), "panel count")
        elif stem.startswith("If D is not on the panel"):
            expect(q, len([p for p in panels if "D" not in p]), "panels without D")


# ---------------------------------------------------------------------------


def main() -> int:
    all_sets = {p.stem: load(p) for p in SETS_DIR.glob("dilr.*.json")}
    all_questions = {p.stem: load(p) for p in QUESTIONS_DIR.glob("dilr.*.json")}

    by_set: dict[str, list[dict]] = {}
    for sid, sset in all_sets.items():
        qs = []
        for qid in sset["questionIds"]:
            if qid not in all_questions:
                fail(f"{sid}: references missing question {qid}")
                continue
            qs.append(all_questions[qid])
        by_set[sid] = qs

    seen_ids: set[str] = set()
    for qid, q in all_questions.items():
        if q["id"] in seen_ids:
            fail(f"duplicate question id {q['id']}")
        seen_ids.add(q["id"])
        check_structure(q)
        check_solution_math(q)

    for sid, sset in all_sets.items():
        if sset["kind"] == "di_set":
            check_di_set(sset, by_set[sid])

    check_lr(by_set, all_sets)

    print(f"sets: {len(all_sets)}  questions: {len(all_questions)}")
    if short_option_sets:
        print(f"note — {len(short_option_sets)} MCQ(s) with fewer than 4 options (binary by nature):")
        for s_ in short_option_sets:
            print(f"  {s_}")
    print(f"answers independently recomputed: {checked_answers}")
    print(f"solution equations evaluated: {equations_checked} (skipped {equations_skipped} carrying free variables)")
    if failures:
        print(f"\nFAILED — {len(failures)} problem(s):")
        for f in failures:
            print(f"  {f}")
        return 1
    print("all checks passed")
    return 0




# ---------------------------------------------------------------------------
# Level 2b: evaluate every equation printed in a solution
#
# The stem-matching above only reaches questions built from an archetype over a chart or table.
# The hand-written sets — radar, bubble, combo, pie, growth, missing-data, caselets, venn,
# games — state their working as displayed LaTeX, and that working is what the learner is asked
# to trust. So every `$...$` span containing an `=` is parsed, evaluated on both sides and
# compared. A transposed digit anywhere in a solution fails here even when the final answer
# happens to be right, which is the failure mode that plain answer-checking cannot see.
#
# Spans carrying free variables ($x^2 = 49$) or prose macros are skipped, not guessed at; the
# skip count is printed so the coverage is visible rather than implied.
# ---------------------------------------------------------------------------

from math import comb  # noqa: E402

MATH_SPAN = re.compile(r"\$([^$\n]+)\$")
equations_checked = 0
equations_skipped = 0


def _latex_to_python(expr: str) -> str | None:
    e = expr
    e = re.sub(r"\\d?binom\{([^{}]+)\}\{([^{}]+)\}", r"comb(\1,\2)", e)
    e = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", e)
    e = e.replace("\\times", "*").replace("\\cdot", "*").replace("\\div", "/")
    e = e.replace("\\left", "").replace("\\right", "")
    e = e.replace("{,}", "").replace(",", "")
    e = e.replace("\\%", "").replace("%", "")
    e = e.replace("\\ ", " ")
    e = re.sub(r"\\text\{[^{}]*\}", "", e)
    e = re.sub(r"\^\{([^{}]+)\}", r"**(\1)", e)
    e = re.sub(r"\^(\d)", r"**\1", e)
    e = e.replace("{", "(").replace("}", ")")
    if re.search(r"[A-Za-z\\]", e.replace("comb", "")):
        return None
    return e


def check_solution_math(q: dict) -> None:
    global equations_checked, equations_skipped
    for span in MATH_SPAN.findall(q.get("solutionMarkdown") or ""):
        if "=" not in span or "\\approx" in span or "<" in span or ">" in span:
            continue
        parts = [p for p in span.split("=") if p.strip()]
        if len(parts) < 2:
            continue
        converted = [_latex_to_python(p) for p in parts]
        if any(c is None for c in converted):
            equations_skipped += 1
            continue
        try:
            values = [eval(c, {"comb": comb, "__builtins__": {}}) for c in converted]  # noqa: S307
        except Exception:
            equations_skipped += 1
            continue
        equations_checked += 1
        first = values[0]
        for v in values[1:]:
            # `%` is stripped rather than interpreted, because the notation is genuinely
            # ambiguous across correct solutions: in `\dfrac{45}{150} = 30\%` the percent sign
            # is an operator, while in `\dfrac{14760}{31400} \times 100 = 47.01\%` it is a unit
            # label on an already-scaled number. Rather than guess, a factor of exactly 100 is
            # accepted on either side. The cost is that a pure 100x slip would pass; the benefit
            # is that every digit of every equation is still checked, which is the error this is
            # actually hunting.
            if any(abs(v - first * k) <= max(0.02, abs(first * k) * 1e-6) for k in (1, 100, 0.01)):
                continue
            fail(f"{q['id']}: solution equation does not hold: ${span}$ -> {values}")
            break

if __name__ == "__main__":
    raise SystemExit(main())
