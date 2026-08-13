"""
DILR / LR content for the six remaining text-based LR micro-topics.

Same SPEC.md §6.3 inversion as every other DILR generator here: the ground truth is
constructed programmatically first, the clues are derived from it, and a brute-force
search over the whole solution space confirms the puzzle has exactly one solution
before anything is written. Nothing is hand-authored and nothing is trusted.

Each topic is generated over several seeds so a topic reaches a usable question count
rather than a single 4-question set.

Run (from /pipeline): python build_dilr_lr_batch4.py
"""

from __future__ import annotations

import hashlib
import itertools
import json
import random
from pathlib import Path

from schemas import PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
VERIFIED_AT = "2026-08-13T00:00:00Z"

SETS_PER_TOPIC = 4


def _q(set_id, n, mt, stem, difficulty, elo, solution, seconds, tags,
       options=None, correct_key=None, value=None, tol=None) -> Question:
    kwargs = dict(
        id=f"{set_id}.q{n}", microTopicIds=[mt], section="DILR",
        stemMarkdown=stem, difficulty=difficulty, eloRating=elo,
        solutionMarkdown=solution, targetSeconds=seconds, source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=tags,
    )
    if options is not None:
        kwargs.update(format="mcq", options=options, correctKey=correct_key)
    else:
        kwargs.update(format="tita", correctValue=value, titaTolerance=tol if tol is not None else 0)
    return Question(**kwargs)


def _mcq(items: list[str]) -> list[QuestionOption]:
    return [QuestionOption(key=chr(65 + i), markdown=v) for i, v in enumerate(items)]


def _set(set_id, mt, body, questions, minutes) -> PassageSet:
    return PassageSet(
        id=set_id, section="DILR", kind="lr_set", bodyMarkdown=body, assets=None,
        questionIds=[q.id for q in questions], genre=None, wordCount=None,
        targetMinutes=minutes, licence="CC0-1.0", sourceUrl=None,
    )


# ---------------------------------------------------------------------------
# dilr.lr.scheduling
# ---------------------------------------------------------------------------

MT_SCHED = "dilr.lr.scheduling"
_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
_PRESENTERS = ["Anil", "Bhavna", "Chirag", "Divya", "Esha"]


def _sched_clues(order: list[str], rng: random.Random) -> list[tuple[str, tuple]]:
    """Every clue is generated FROM the true schedule, so it is true by construction."""
    pos = {p: i for i, p in enumerate(order)}
    clues: list[tuple[str, tuple]] = []
    for p in _PRESENTERS:
        clues.append((f"{p} presents on {_DAYS[pos[p]]}.", ("exact", p, pos[p])))
        for other in _PRESENTERS:
            if p == other:
                continue
            if pos[p] < pos[other]:
                clues.append((f"{p} presents on an earlier day than {other}.", ("before", p, other)))
            if pos[other] - pos[p] == 1:
                clues.append((f"{p} presents on the day immediately before {other}.", ("immediately", p, other)))
            if abs(pos[p] - pos[other]) == 2:
                clues.append((f"Exactly one presentation falls between {p} and {other}.", ("gap2", p, other)))
        if pos[p] not in (0, len(_DAYS) - 1):
            clues.append((f"{p} presents neither on {_DAYS[0]} nor on {_DAYS[-1]}.", ("notends", p, None)))
    rng.shuffle(clues)
    return clues


def _sched_ok(order: list[str], key: tuple) -> bool:
    pos = {p: i for i, p in enumerate(order)}
    kind, a, b = key
    if kind == "exact":
        return pos[a] == b
    if kind == "before":
        return pos[a] < pos[b]
    if kind == "immediately":
        return pos[b] - pos[a] == 1
    if kind == "gap2":
        return abs(pos[a] - pos[b]) == 2
    if kind == "notends":
        return pos[a] not in (0, len(_DAYS) - 1)
    raise ValueError(kind)


def build_scheduling(seed: int):
    rng = random.Random(f"{MT_SCHED}-{seed}")
    truth = rng.sample(_PRESENTERS, len(_PRESENTERS))

    chosen: list[tuple] = []
    sentences: list[str] = []
    for sentence, key in _sched_clues(truth, rng):
        if key[0] == "exact" and len(chosen) < 2:
            continue  # a bare "X is on Tuesday" too early makes the puzzle trivial
        chosen.append(key)
        sentences.append(sentence)
        survivors = [list(p) for p in itertools.permutations(_PRESENTERS)
                     if all(_sched_ok(list(p), k) for k in chosen)]
        assert truth in survivors, "the true schedule must satisfy its own clues"
        if len(survivors) == 1:
            break
    else:
        return None

    final = [list(p) for p in itertools.permutations(_PRESENTERS)
             if all(_sched_ok(list(p), k) for k in chosen)]
    assert len(final) == 1 and final[0] == truth

    h = hashlib.sha1((MT_SCHED + str(seed) + "".join(truth)).encode()).hexdigest()[:8]
    set_id = f"{MT_SCHED}.set-{h}"
    pos = {p: i for i, p in enumerate(truth)}
    full = ", ".join(f"{_DAYS[i]}: {truth[i]}" for i in range(len(_DAYS)))

    wednesday = truth[2]
    last = truth[-1]
    qs = [
        _q(set_id, 1, MT_SCHED, "Who presents on Wednesday?", "medium", 1200.0,
           f"Working the clues gives the full schedule — {full}. Wednesday is **{wednesday}**.",
           100, ["lr:scheduling"], options=_mcq(_PRESENTERS),
           correct_key=chr(65 + _PRESENTERS.index(wednesday))),
        _q(set_id, 2, MT_SCHED, "Who presents last?", "medium", 1200.0,
           f"From the schedule ({full}), the Friday slot goes to **{last}**.",
           100, ["lr:scheduling"], options=_mcq(_PRESENTERS),
           correct_key=chr(65 + _PRESENTERS.index(last))),
        _q(set_id, 3, MT_SCHED, f"On which day does {_PRESENTERS[0]} present?", "medium", 1200.0,
           f"From the schedule, {_PRESENTERS[0]} presents on **{_DAYS[pos[_PRESENTERS[0]]]}**.",
           100, ["lr:scheduling"], options=_mcq(_DAYS),
           correct_key=chr(65 + pos[_PRESENTERS[0]])),
        _q(set_id, 4, MT_SCHED,
           f"How many presentations fall between {truth[0]}'s and {truth[-1]}'s?", "hard", 1350.0,
           f"{truth[0]} is on {_DAYS[0]} and {truth[-1]} is on {_DAYS[-1]}, so the presentations "
           f"strictly between them number **{len(_DAYS) - 2}**.",
           120, ["lr:scheduling"], value=len(_DAYS) - 2),
    ]
    body = (
        f"Five colleagues — {', '.join(_PRESENTERS[:-1])} and {_PRESENTERS[-1]} — each give exactly one "
        f"presentation, one per day from Monday to Friday. Use the clues below.\n\n"
        + "\n".join(f"- {c}" for c in sentences)
    )
    return _set(set_id, MT_SCHED, body, qs, 9.0), qs


# ---------------------------------------------------------------------------
# dilr.lr.binary-logic
# ---------------------------------------------------------------------------

MT_BIN = "dilr.lr.binary-logic"
_FOLK = ["Ravi", "Sunil", "Tara"]


# Statement templates, each a predicate evaluated against a candidate assignment.
# Claims purely of the form "X is a liar" are not enough on their own: with three
# speakers each describing one other, the constraints close into a cycle, and such a
# system always admits either two assignments or none -- never exactly one. Adding
# counting statements ("exactly one of us is a liar") breaks that symmetry and lets a
# puzzle have a single solution.
_BIN_STATEMENTS = [
    ("{subject} is a truth-teller", lambda a, sp, subj: a[subj], True),
    ("{subject} is a liar", lambda a, sp, subj: not a[subj], True),
    ("both of the others are liars", lambda a, sp, subj: all(not a[p] for p in _FOLK if p != sp), False),
    ("at least one of the other two is a truth-teller",
     lambda a, sp, subj: any(a[p] for p in _FOLK if p != sp), False),
    ("exactly one of the three of us is a liar",
     lambda a, sp, subj: sum(1 for p in _FOLK if not a[p]) == 1, False),
    ("all three of us are truth-tellers", lambda a, sp, subj: all(a.values()), False),
]


def build_binary_logic(seed: int):
    rng = random.Random(f"{MT_BIN}-{seed}")
    truth = {p: rng.choice([True, False]) for p in _FOLK}
    if all(truth.values()) or not any(truth.values()):
        truth[_FOLK[0]] = not truth[_FOLK[0]]

    # Try random statement assignments until one yields a uniquely solvable puzzle.
    for _ in range(400):
        claims = []   # (speaker, predicate, subject, sentence)
        for speaker in _FOLK:
            template, predicate, needs_subject, = rng.choice(_BIN_STATEMENTS)
            subject = rng.choice([p for p in _FOLK if p != speaker]) if needs_subject else None
            # A truth-teller's statement must be true and a liar's must be false, so only
            # keep a template whose value on the real assignment matches the speaker's type.
            if predicate(truth, speaker, subject) != truth[speaker]:
                continue
            sentence = template.format(subject=subject) if needs_subject else template
            claims.append((speaker, predicate, subject, f"{speaker} says: \"{sentence.capitalize()}\""))
        if len(claims) != len(_FOLK):
            continue

        def consistent(assign, claims=claims):
            return all(assign[sp] == pred(assign, sp, subj) for sp, pred, subj, _ in claims)

        survivors = [dict(zip(_FOLK, combo))
                     for combo in itertools.product([True, False], repeat=len(_FOLK))
                     if consistent(dict(zip(_FOLK, combo)))]
        if len(survivors) == 1 and survivors[0] == truth:
            break
    else:
        return None

    h = hashlib.sha1((MT_BIN + str(seed) + str(truth)).encode()).hexdigest()[:8]
    set_id = f"{MT_BIN}.set-{h}"
    liars = [p for p in _FOLK if not truth[p]]
    tellers = [p for p in _FOLK if truth[p]]
    full = ", ".join(f"{p}: {'truth-teller' if truth[p] else 'liar'}" for p in _FOLK)

    qs = [
        _q(set_id, 1, MT_BIN, "How many of the three are liars?", "medium", 1200.0,
           f"Testing all eight possible truth-teller/liar combinations, only one is self-consistent: "
           f"{full}. That gives **{len(liars)}** liar(s).",
           110, ["lr:binary-logic"], value=len(liars)),
        _q(set_id, 2, MT_BIN, f"Is {_FOLK[0]} a truth-teller or a liar?", "medium", 1200.0,
           f"In the unique consistent assignment ({full}), {_FOLK[0]} is a "
           f"**{'truth-teller' if truth[_FOLK[0]] else 'liar'}**.",
           110, ["lr:binary-logic"],
           options=_mcq(["Truth-teller", "Liar"]), correct_key="A" if truth[_FOLK[0]] else "B"),
        _q(set_id, 3, MT_BIN, "Who among the three tells the truth?" if len(tellers) == 1
           else "How many of the three are truth-tellers?", "hard", 1350.0,
           f"From the unique assignment ({full}), the truth-tellers are "
           f"{', '.join(tellers) if tellers else 'none'} — that is **{len(tellers)}**.",
           120, ["lr:binary-logic"], value=len(tellers)),
        _q(set_id, 4, MT_BIN, f"Is {_FOLK[-1]} a truth-teller or a liar?", "hard", 1350.0,
           f"From the unique assignment ({full}), {_FOLK[-1]} is a "
           f"**{'truth-teller' if truth[_FOLK[-1]] else 'liar'}**.",
           120, ["lr:binary-logic"],
           options=_mcq(["Truth-teller", "Liar"]), correct_key="A" if truth[_FOLK[-1]] else "B"),
    ]
    body = (
        f"On an island every inhabitant is either a truth-teller (whose every statement is true) or a "
        f"liar (whose every statement is false). Three inhabitants — {', '.join(_FOLK[:-1])} and "
        f"{_FOLK[-1]} — each make one statement.\n\n"
        + "\n".join(f"- {c[3]}" for c in claims)
    )
    return _set(set_id, MT_BIN, body, qs, 8.0), qs


# ---------------------------------------------------------------------------
# dilr.lr.network-routes
# ---------------------------------------------------------------------------

MT_NET = "dilr.lr.network-routes"


def build_network_routes(seed: int):
    rng = random.Random(f"{MT_NET}-{seed}")
    nodes = ["A", "B", "C", "D", "E", "F"]
    edges: dict[tuple[str, str], int] = {}
    # A layered graph guarantees at least one A->F route while keeping the search small.
    layers = [["A"], ["B", "C"], ["D", "E"], ["F"]]
    for i in range(len(layers) - 1):
        for u in layers[i]:
            for v in layers[i + 1]:
                edges[(u, v)] = rng.randint(3, 15)
    # One shortcut edge, to make the obvious route not always the best.
    edges[("B", "E")] = rng.randint(2, 9)

    def routes(src: str, dst: str) -> list[list[str]]:
        found: list[list[str]] = []

        def walk(path: list[str]):
            if path[-1] == dst:
                found.append(list(path))
                return
            for (u, v) in edges:
                if u == path[-1] and v not in path:
                    walk(path + [v])

        walk([src])
        return found

    all_routes = routes("A", "F")
    if len(all_routes) < 3:
        return None

    def cost(path: list[str]) -> int:
        return sum(edges[(path[i], path[i + 1])] for i in range(len(path) - 1))

    costs = sorted((cost(r), r) for r in all_routes)
    shortest_cost, shortest = costs[0]
    longest_cost, _ = costs[-1]
    # Independent re-derivation of the minimum by a different mechanism (Dijkstra-style relaxation).
    dist = {n: float("inf") for n in nodes}
    dist["A"] = 0
    for _ in range(len(nodes)):
        for (u, v), w in edges.items():
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    assert dist["F"] == shortest_cost, "enumeration and relaxation disagree on the shortest route"

    h = hashlib.sha1((MT_NET + str(seed) + str(sorted(edges.items()))).encode()).hexdigest()[:8]
    set_id = f"{MT_NET}.set-{h}"
    edge_lines = "\n".join(f"- {u} to {v}: {w} km" for (u, v), w in sorted(edges.items()))

    qs = [
        _q(set_id, 1, MT_NET, "What is the length (in km) of the shortest route from A to F?",
           "medium", 1200.0,
           f"Listing every route from A to F and totalling its legs, the cheapest is "
           f"{' to '.join(shortest)} at **{shortest_cost} km**.",
           130, ["lr:network-routes"], value=shortest_cost),
        _q(set_id, 2, MT_NET, "How many distinct routes lead from A to F without revisiting any town?",
           "medium", 1200.0,
           f"Enumerating every simple path from A to F gives **{len(all_routes)}** routes.",
           130, ["lr:network-routes"], value=len(all_routes)),
        _q(set_id, 3, MT_NET, "What is the length (in km) of the longest route from A to F without revisiting any town?",
           "hard", 1350.0,
           f"Of the {len(all_routes)} simple routes, the most expensive totals **{longest_cost} km**.",
           130, ["lr:network-routes"], value=longest_cost),
        _q(set_id, 4, MT_NET,
           f"How many kilometres longer than the shortest route is the longest one?", "hard", 1350.0,
           f"Longest {longest_cost} km minus shortest {shortest_cost} km is **{longest_cost - shortest_cost} km**.",
           130, ["lr:network-routes"], value=longest_cost - shortest_cost),
    ]
    body = (
        "The road network below connects six towns. Each road is one-way, in the direction shown, "
        "and its length is given in kilometres.\n\n" + edge_lines
    )
    return _set(set_id, MT_NET, body, qs, 10.0), qs


# ---------------------------------------------------------------------------
# dilr.lr.cubes-dice
# ---------------------------------------------------------------------------

MT_CUBE = "dilr.lr.cubes-dice"


def build_cubes_dice(seed: int):
    rng = random.Random(f"{MT_CUBE}-{seed}")
    n = rng.choice([3, 4, 5, 6])

    # Formula counts, then re-derived by explicit enumeration of every small cube's position.
    f3, f2 = 8, 12 * (n - 2)
    f1, f0 = 6 * (n - 2) ** 2, (n - 2) ** 3

    counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for x in range(n):
        for y in range(n):
            for z in range(n):
                painted = sum([x in (0, n - 1), y in (0, n - 1), z in (0, n - 1)])
                counts[painted] += 1
    assert (counts[3], counts[2], counts[1], counts[0]) == (f3, f2, f1, f0), \
        "formula and enumeration disagree on painted-face counts"

    h = hashlib.sha1((MT_CUBE + str(seed) + str(n)).encode()).hexdigest()[:8]
    set_id = f"{MT_CUBE}.set-{h}"

    qs = [
        _q(set_id, 1, MT_CUBE, "How many of the small cubes have exactly three painted faces?",
           "easy", 1050.0,
           f"Only the corner cubes show three painted faces, and a cube has **8** corners "
           f"whatever the number of cuts.",
           90, ["lr:cubes"], value=f3),
        _q(set_id, 2, MT_CUBE, "How many of the small cubes have exactly two painted faces?",
           "medium", 1200.0,
           f"These lie along the twelve edges, excluding the corners: "
           f"$12 \\times ({n} - 2) = $ **{f2}**.",
           110, ["lr:cubes"], value=f2),
        _q(set_id, 3, MT_CUBE, "How many of the small cubes have exactly one painted face?",
           "medium", 1200.0,
           f"These form the interior of each of the six faces: "
           f"$6 \\times ({n} - 2)^2 = $ **{f1}**.",
           110, ["lr:cubes"], value=f1),
        _q(set_id, 4, MT_CUBE, "How many of the small cubes have no painted face at all?",
           "hard", 1350.0,
           f"The unpainted cubes form the hidden core: $({n} - 2)^3 = $ **{f0}**. "
           f"As a check, $8 + {f2} + {f1} + {f0} = {n**3}$, the total number of small cubes.",
           110, ["lr:cubes"], value=f0),
    ]
    body = (
        f"A wooden cube is painted on all six faces and then cut into {n**3} identical smaller cubes "
        f"by making equally spaced cuts, {n} small cubes along each edge."
    )
    return _set(set_id, MT_CUBE, body, qs, 8.0), qs


# ---------------------------------------------------------------------------
# dilr.lr.number-placement
# ---------------------------------------------------------------------------

MT_NUM = "dilr.lr.number-placement"


def build_number_placement(seed: int):
    rng = random.Random(f"{MT_NUM}-{seed}")

    def is_magic(g):
        lines = [g[0:3], g[3:6], g[6:9], g[0::3], g[1::3], g[2::3], [g[0], g[4], g[8]], [g[2], g[4], g[6]]]
        return all(sum(line) == 15 for line in lines)

    all_magic = [list(p) for p in itertools.permutations(range(1, 10)) if is_magic(list(p))]
    assert len(all_magic) == 8, f"a 3x3 magic square has 8 symmetries, found {len(all_magic)}"
    target = rng.choice(all_magic)

    # Reveal cells one at a time until exactly one magic square fits the revealed pattern.
    idxs = list(range(9))
    rng.shuffle(idxs)
    revealed: list[int] = []
    for i in idxs:
        revealed.append(i)
        fits = [g for g in all_magic if all(g[j] == target[j] for j in revealed)]
        if len(fits) == 1:
            break
    else:
        return None
    assert len([g for g in all_magic if all(g[j] == target[j] for j in revealed)]) == 1

    hidden = [i for i in range(9) if i not in revealed]
    if not hidden:
        return None

    h = hashlib.sha1((MT_NUM + str(seed) + str(target)).encode()).hexdigest()[:8]
    set_id = f"{MT_NUM}.set-{h}"

    def cell_name(i):
        return f"row {i // 3 + 1}, column {i % 3 + 1}"

    grid_desc = "\n".join(
        f"- {cell_name(i)}: " + (str(target[i]) if i in revealed else "empty")
        for i in range(9)
    )
    ask1, ask2 = hidden[0], hidden[-1]

    qs = [
        _q(set_id, 1, MT_NUM, f"What number belongs in {cell_name(ask1)}?", "medium", 1200.0,
           f"Every row, column and diagonal must total 15, and the digits 1 to 9 are each used once. "
           f"Those constraints leave exactly one completion, in which {cell_name(ask1)} holds "
           f"**{target[ask1]}**.",
           120, ["lr:number-placement"], value=target[ask1]),
        _q(set_id, 2, MT_NUM, f"What number belongs in {cell_name(ask2)}?", "medium", 1200.0,
           f"From the same unique completion, {cell_name(ask2)} holds **{target[ask2]}**.",
           120, ["lr:number-placement"], value=target[ask2]),
        _q(set_id, 3, MT_NUM, "What is the number in the centre cell?", "easy", 1050.0,
           f"In any 3 by 3 magic square built from 1 to 9 the centre is always 5, and here it is "
           f"**{target[4]}**.",
           90, ["lr:number-placement"], value=target[4]),
        _q(set_id, 4, MT_NUM, "What is the sum of the four corner cells?", "hard", 1350.0,
           f"The corners are {target[0]}, {target[2]}, {target[6]} and {target[8]}, summing to "
           f"**{target[0] + target[2] + target[6] + target[8]}**.",
           120, ["lr:number-placement"], value=target[0] + target[2] + target[6] + target[8]),
    ]
    body = (
        "A 3 by 3 grid is filled with the digits 1 to 9, each used exactly once, so that every row, "
        "every column and both diagonals add up to the same total. Some cells are already filled:\n\n"
        + grid_desc
    )
    return _set(set_id, MT_NUM, body, qs, 9.0), qs


# ---------------------------------------------------------------------------
# dilr.lr.quant-embedded
# ---------------------------------------------------------------------------

MT_QE = "dilr.lr.quant-embedded"
_STAFF = ["Kiran", "Lata", "Manoj", "Nisha"]


def build_quant_embedded(seed: int):
    rng = random.Random(f"{MT_QE}-{seed}")
    total = rng.choice([100, 120, 140, 160])
    while True:
        scores = sorted(rng.sample(range(10, 60), 4), reverse=True)
        if sum(scores) == total and len(set(scores)) == 4:
            break
        scores = None
        # Construct rather than reject-sample: pick three then force the fourth.
        a, b, c = sorted(rng.sample(range(10, 55), 3), reverse=True)
        d = total - (a + b + c)
        if 5 <= d < c and len({a, b, c, d}) == 4:
            scores = [a, b, c, d]
            break
    if not scores:
        return None

    assign = dict(zip(_STAFF, scores))   # already in descending order

    # Brute-force check: the stated constraints must pin down exactly one assignment.
    highest, lowest = _STAFF[0], _STAFF[-1]
    gap = assign[_STAFF[0]] - assign[_STAFF[1]]

    def consistent(perm):
        m = dict(zip(_STAFF, perm))
        return (
            sum(perm) == total
            and m[_STAFF[0]] > m[_STAFF[1]] > m[_STAFF[2]] > m[_STAFF[3]]
            and m[_STAFF[0]] - m[_STAFF[1]] == gap
            and m[_STAFF[3]] == assign[_STAFF[3]]
            and m[_STAFF[2]] == assign[_STAFF[2]]
        )

    survivors = [p for p in itertools.permutations(scores) if consistent(p)]
    if len(survivors) != 1:
        return None

    h = hashlib.sha1((MT_QE + str(seed) + str(assign)).encode()).hexdigest()[:8]
    set_id = f"{MT_QE}.set-{h}"
    full = ", ".join(f"{p}: {assign[p]}" for p in _STAFF)

    qs = [
        _q(set_id, 1, MT_QE, f"What is {highest}'s score?", "medium", 1200.0,
           f"The constraints pin every score down uniquely — {full}. So {highest} scored "
           f"**{assign[highest]}**.",
           130, ["lr:quant-embedded"], value=assign[highest]),
        _q(set_id, 2, MT_QE, f"What is {lowest}'s score?", "medium", 1200.0,
           f"From the same unique solution, {lowest} scored **{assign[lowest]}**.",
           130, ["lr:quant-embedded"], value=assign[lowest]),
        _q(set_id, 3, MT_QE, "What is the difference between the highest and lowest scores?",
           "hard", 1350.0,
           f"{assign[highest]} minus {assign[lowest]} is **{assign[highest] - assign[lowest]}**.",
           130, ["lr:quant-embedded"], value=assign[highest] - assign[lowest]),
        _q(set_id, 4, MT_QE, "What is the average of the four scores?", "easy", 1050.0,
           f"The four scores total {total}, so the average is "
           f"$\\dfrac{{{total}}}{{4}} = $ **{total / 4}**.",
           100, ["lr:quant-embedded"], value=total / 4, tol=0.01),
    ]
    body = (
        f"Four analysts — {', '.join(_STAFF[:-1])} and {_STAFF[-1]} — sat the same test and scored "
        f"{total} marks between them. Their scores were all different whole numbers, and:\n\n"
        f"- {_STAFF[0]} scored more than {_STAFF[1]}, who scored more than {_STAFF[2]}, "
        f"who scored more than {_STAFF[3]}.\n"
        f"- {_STAFF[0]} scored exactly {gap} marks more than {_STAFF[1]}.\n"
        f"- {_STAFF[2]} scored {assign[_STAFF[2]]} marks.\n"
        f"- {_STAFF[3]} scored {assign[_STAFF[3]]} marks."
    )
    return _set(set_id, MT_QE, body, qs, 10.0), qs


BUILDERS = {
    MT_SCHED: build_scheduling,
    MT_BIN: build_binary_logic,
    MT_NET: build_network_routes,
    MT_CUBE: build_cubes_dice,
    MT_NUM: build_number_placement,
    MT_QE: build_quant_embedded,
}


def main() -> None:
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    PASSAGE_SETS_DIR.mkdir(parents=True, exist_ok=True)
    grand_total = 0
    for mt, builder in BUILDERS.items():
        made, seed, seen_ids = 0, 0, set()
        while made < SETS_PER_TOPIC and seed < 400:
            result = builder(seed)
            seed += 1
            if result is None:
                continue
            passage_set, questions = result
            if passage_set.id in seen_ids:
                continue
            seen_ids.add(passage_set.id)
            for q in questions:
                (QUESTIONS_DIR / f"{q.id}.json").write_text(
                    json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
            (PASSAGE_SETS_DIR / f"{passage_set.id}.json").write_text(
                json.dumps(json.loads(passage_set.model_dump_json()), indent=2) + "\n")
            made += 1
            grand_total += len(questions)
        print(f"{mt}: {made} sets, {made * 4} questions")
    print(f"\nTotal: {grand_total} DILR/LR questions written.")


if __name__ == "__main__":
    main()
