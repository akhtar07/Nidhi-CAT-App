"""
Content scale-up: dilr.lr.ordering-ranking (roi=3, previously 0 questions).

Linear ranking puzzle: 6 students' ranks (1 = best) in a test, deduced from a clue set. Same
DILR-inversion discipline as build_dilr_lr_arrangement.py / build_dilr_lr_distribution_grouping.py
— pick the ground-truth ranking first, generate candidate clues from it, add clues one at a time
(shuffled) and brute-force every one of the 6! = 720 permutations after each addition until
exactly one survives, so the puzzle is provably solvable and provably unique from its own clues
(not just "the generator's checker says so" — see the independent re-verification in main()).

Run (from /pipeline, cat-pipeline conda env): python build_dilr_lr_ordering_ranking.py
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
MICRO_TOPIC_ID = "dilr.lr.ordering-ranking"
VERIFIED_AT = "2026-08-12T00:00:00Z"

STUDENTS = ["Priya", "Rohan", "Sara", "Tarun", "Uma", "Vikram"]
N = len(STUDENTS)


def candidate_clues(rank_of: dict[str, int], rng: random.Random) -> list[tuple[str, tuple]]:
    clues: list[tuple[str, tuple]] = []
    for a in STUDENTS:
        for b in STUDENTS:
            if a == b:
                continue
            if rank_of[a] == rank_of[b] - 1:
                clues.append((f"{a} is ranked immediately above {b}.", ("immediate_above", a, b)))
            if rank_of[a] < rank_of[b]:
                clues.append((f"{a} scored better than {b}.", ("above", a, b)))
            if abs(rank_of[a] - rank_of[b]) == 2:
                clues.append((f"Exactly one student is ranked between {a} and {b}.", ("between2", a, b)))
    for a in STUDENTS:
        clues.append((f"{a} is ranked {rank_of[a]}.", ("exact", a, rank_of[a])))
    rng.shuffle(clues)
    return clues


def satisfies(rank_of: dict[str, int], key: tuple) -> bool:
    kind = key[0]
    if kind == "immediate_above":
        _, a, b = key
        return rank_of[a] == rank_of[b] - 1
    if kind == "above":
        _, a, b = key
        return rank_of[a] < rank_of[b]
    if kind == "between2":
        _, a, b = key
        return abs(rank_of[a] - rank_of[b]) == 2
    if kind == "exact":
        _, a, r = key
        return rank_of[a] == r
    raise ValueError(kind)


def all_rankings_consistent_with(keys: list[tuple]) -> list[dict[str, int]]:
    found = []
    for perm in itertools.permutations(range(1, N + 1)):
        rank_of = dict(zip(STUDENTS, perm))
        if all(satisfies(rank_of, k) for k in keys):
            found.append(rank_of)
    return found


def build_puzzle(seed: int) -> tuple[dict[str, int], list[str]]:
    rng = random.Random(f"{MICRO_TOPIC_ID}-{seed}")
    true_ranks = dict(zip(STUDENTS, rng.sample(range(1, N + 1), N)))

    clues = candidate_clues(true_ranks, rng)
    chosen_keys: list[tuple] = []
    chosen_sentences: list[str] = []
    for sentence, key in clues:
        # Never offer a bare "exact" clue unless we're truly stuck — it trivially fixes one
        # student and makes for a weak puzzle; only reach for it if nothing else narrows things.
        chosen_keys.append(key)
        chosen_sentences.append(sentence)
        remaining = all_rankings_consistent_with(chosen_keys)
        assert true_ranks in remaining, "the true ranking must always satisfy its own true clues"
        if len(remaining) == 1:
            break
    else:
        raise RuntimeError(f"seed {seed}: exhausted all clues without reaching a unique ranking")

    final = all_rankings_consistent_with(chosen_keys)
    assert len(final) == 1 and final[0] == true_ranks, f"seed {seed}: clue set is not actually unique"
    return true_ranks, chosen_sentences


def independent_reverify(clues_sentences: list[str], true_ranks: dict[str, int]) -> None:
    """Re-parses the plain-English clue sentences with a fresh regex layer (not the generator's
    own `key` tuples) and re-runs a separately-written brute force, so a bug that's consistent
    between candidate_clues()/satisfies() but wrong in the printed English can't hide."""
    import re

    parsed: list[tuple] = []
    for s in clues_sentences:
        m = re.match(r"^(\w+) is ranked immediately above (\w+)\.$", s)
        if m:
            parsed.append(("ia", m.group(1), m.group(2)))
            continue
        m = re.match(r"^(\w+) scored better than (\w+)\.$", s)
        if m:
            parsed.append(("ab", m.group(1), m.group(2)))
            continue
        m = re.match(r"^Exactly one student is ranked between (\w+) and (\w+)\.$", s)
        if m:
            parsed.append(("b2", m.group(1), m.group(2)))
            continue
        m = re.match(r"^(\w+) is ranked (\d+)\.$", s)
        if m:
            parsed.append(("ex", m.group(1), int(m.group(2))))
            continue
        raise AssertionError(f"independent parser could not understand clue: {s!r}")

    def check(rank_of: dict[str, int], p: tuple) -> bool:
        if p[0] == "ia":
            return rank_of[p[1]] == rank_of[p[2]] - 1
        if p[0] == "ab":
            return rank_of[p[1]] < rank_of[p[2]]
        if p[0] == "b2":
            return abs(rank_of[p[1]] - rank_of[p[2]]) == 2
        if p[0] == "ex":
            return rank_of[p[1]] == p[2]
        raise ValueError(p)

    survivors = [
        dict(zip(STUDENTS, perm))
        for perm in itertools.permutations(range(1, N + 1))
        if all(check(dict(zip(STUDENTS, perm)), p) for p in parsed)
    ]
    assert len(survivors) == 1, f"independent re-parse finds {len(survivors)} solutions, expected 1"
    assert survivors[0] == true_ranks, "independent re-parse's unique solution disagrees with ground truth"


def build_questions(set_id: str, rank_of: dict[str, int]) -> list[Question]:
    ranked_order = sorted(STUDENTS, key=lambda s: rank_of[s])

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Who scored the highest (rank 1)?",
        options=[QuestionOption(key=chr(65 + i), markdown=s) for i, s in enumerate(STUDENTS)],
        correctKey=chr(65 + STUDENTS.index(ranked_order[0])),
        difficulty="easy",
        eloRating=1050.0,
        solutionMarkdown=(
            "Full ranking (best to worst): " + " > ".join(ranked_order) + f". Rank 1 is **{ranked_order[0]}**."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:ordering-ranking"],
    )

    third = ranked_order[2]
    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Who is ranked 3rd?",
        options=[QuestionOption(key=chr(65 + i), markdown=s) for i, s in enumerate(STUDENTS)],
        correctKey=chr(65 + STUDENTS.index(third)),
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=f"From the full ranking, **{third}** is 3rd.",
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:ordering-ranking"],
    )

    last = ranked_order[-1]
    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Who scored the lowest (rank 6)?",
        options=[QuestionOption(key=chr(65 + i), markdown=s) for i, s in enumerate(STUDENTS)],
        correctKey=chr(65 + STUDENTS.index(last)),
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=f"From the full ranking, **{last}** is last (rank 6).",
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:ordering-ranking"],
    )

    a, b = ranked_order[1], ranked_order[4]
    between_count = abs(rank_of[a] - rank_of[b]) - 1
    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown=f"How many students are ranked between {a} and {b}?",
        correctValue=between_count,
        titaTolerance=0,
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=(
            f"{a} is rank {rank_of[a]}, {b} is rank {rank_of[b]}. Students strictly between them: "
            f"**{between_count}**."
        ),
        targetSeconds=120,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:ordering-ranking"],
    )

    return [q1, q2, q3, q4]


def build_set(index: int) -> tuple[PassageSet, list[Question]]:
    true_ranks, clues = build_puzzle(index)
    independent_reverify(clues, true_ranks)

    content_hash = hashlib.sha1((MICRO_TOPIC_ID + str(index) + "".join(str(true_ranks[s]) for s in STUDENTS)).encode()).hexdigest()[:8]
    set_id = f"{MICRO_TOPIC_ID}.set-{content_hash}"

    body = (
        f"{N} students — {', '.join(STUDENTS[:-1])}, and {STUDENTS[-1]} — took a test and each "
        "got a distinct rank from 1 (highest score) to 6 (lowest score). Study the clues below "
        "and answer the questions that follow.\n\n"
        + "\n".join(f"- {c}" for c in clues)
    )

    questions = build_questions(set_id, true_ranks)
    passage_set = PassageSet(
        id=set_id,
        section="DILR",
        kind="lr_set",
        bodyMarkdown=body,
        assets=None,
        questionIds=[q.id for q in questions],
        genre=None,
        wordCount=None,
        targetMinutes=9.0,
        licence="CC0-1.0",
        sourceUrl=None,
    )
    return passage_set, questions


def main() -> None:
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    PASSAGE_SETS_DIR.mkdir(parents=True, exist_ok=True)
    for index in range(3):
        passage_set, questions = build_set(index)
        for q in questions:
            path = QUESTIONS_DIR / f"{q.id}.json"
            path.write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
        set_path = PASSAGE_SETS_DIR / f"{passage_set.id}.json"
        set_path.write_text(json.dumps(json.loads(passage_set.model_dump_json()), indent=2) + "\n")
        print(f"Wrote {passage_set.id} ({len(questions)} questions)")


if __name__ == "__main__":
    main()
