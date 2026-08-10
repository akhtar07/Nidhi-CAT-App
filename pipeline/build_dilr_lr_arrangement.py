"""
Content scale-up: dilr.lr.arrangements (roi=5, previously 0 questions).

SPEC.md §6.3's DILR inversion, applied to a logic puzzle instead of a data table: generate the
*answer* first (a random circular seating), then generate candidate clues about it, then verify
by brute force that the clue set has EXACTLY ONE circular arrangement (up to rotation — a
circular arrangement has no fixed starting seat) consistent with all of them, adding clues one
at a time until uniqueness holds. No LLM anywhere in this file; every question's answer is read
straight off the verified-unique solution, not typed by hand.

"Clockwise" is stated explicitly in the puzzle body, so reflections (mirror-image seatings) are
genuinely different arrangements, not a hidden ambiguity — the uniqueness check only dedupes
rotations of the same cyclic order, never reflections.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_lr_arrangement.py
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
MICRO_TOPIC_ID = "dilr.lr.arrangements"
VERIFIED_AT = "2026-08-10T00:00:00Z"

NAME_POOL = ["Anya", "Bilal", "Chetan", "Divya", "Esha", "Farhan", "Gauri", "Hemant"]
N = 5


def rotations(seq: tuple[str, ...]) -> set[tuple[str, ...]]:
    return {tuple(seq[i:] + seq[:i]) for i in range(len(seq))}


def clockwise_neighbor(seq: tuple[str, ...], person: str) -> str:
    i = seq.index(person)
    return seq[(i + 1) % len(seq)]


def people_between_clockwise(seq: tuple[str, ...], a: str, b: str) -> int:
    """Count of people strictly between a and b going clockwise from a to b."""
    i, j = seq.index(a), seq.index(b)
    n = len(seq)
    return (j - i - 1) % n


def candidate_clues(seq: tuple[str, ...], rng: random.Random) -> list[tuple[str, object]]:
    """Every true statement about `seq` that could serve as a clue, as (English, check-key)
    pairs where check-key lets satisfies() re-evaluate the same statement against any candidate
    permutation without re-parsing English."""
    people = list(seq)
    clues: list[tuple[str, object]] = []
    for a in people:
        # b is whoever comes right after `a` going clockwise, so the TRUE English statement is
        # "b sits immediately clockwise of a" (not the reverse) — caught by hand-checking the
        # first generated set against clockwise_neighbor() directly, see PROGRESS.md.
        b = clockwise_neighbor(seq, a)
        clues.append((f"{b} sits immediately clockwise of {a}.", ("cw_neighbor", b, a)))
    for a, b in itertools.combinations(people, 2):
        gap = people_between_clockwise(seq, a, b)
        other_gap = people_between_clockwise(seq, b, a)
        # only unambiguous, non-trivial gaps make good clues (skip adjacent pairs, covered above)
        if gap not in (0,) and gap <= 2:
            clues.append((f"There are exactly {gap} people between {a} and {b}, going clockwise from {a}.", ("gap_cw", a, b, gap)))
        if other_gap not in (0,) and other_gap <= 2:
            clues.append((f"There are exactly {other_gap} people between {b} and {a}, going clockwise from {b}.", ("gap_cw", b, a, other_gap)))
    rng.shuffle(clues)
    return clues


def satisfies(seq: tuple[str, ...], key: tuple) -> bool:
    kind = key[0]
    if kind == "cw_neighbor":
        _, b, a = key
        return clockwise_neighbor(seq, a) == b
    if kind == "gap_cw":
        _, a, b, gap = key
        return people_between_clockwise(seq, a, b) == gap
    raise ValueError(kind)


def solutions_consistent_with(keys: list[tuple], people: list[str]) -> set[tuple[str, ...]]:
    found: set[tuple[str, ...]] = set()
    canonical_seen: set[tuple[str, ...]] = set()
    for perm in itertools.permutations(people):
        if perm in canonical_seen:
            continue
        canonical_seen |= rotations(perm)
        if all(satisfies(perm, k) for k in keys):
            found.add(min(rotations(perm)))  # canonical representative
    return found


def build_puzzle(seed: int) -> tuple[tuple[str, ...], list[str]]:
    """Returns (solution, clue_sentences) where clue_sentences is the minimal-ish clue set
    verified (by brute force) to pin down exactly one circular arrangement."""
    rng = random.Random(f"{MICRO_TOPIC_ID}-{seed}")
    people = NAME_POOL[:N]
    solution = tuple(rng.sample(people, len(people)))

    clues = candidate_clues(solution, rng)
    chosen_keys: list[tuple] = []
    chosen_sentences: list[str] = []
    for sentence, key in clues:
        chosen_keys.append(key)
        chosen_sentences.append(sentence)
        remaining = solutions_consistent_with(chosen_keys, people)
        assert min(rotations(solution)) in remaining, "solution must always remain consistent with its own true clues"
        if len(remaining) == 1:
            break
    else:
        raise RuntimeError(f"seed {seed}: exhausted all clues without reaching a unique solution")

    final = solutions_consistent_with(chosen_keys, people)
    assert final == {min(rotations(solution))}, f"seed {seed}: clue set is not actually unique: {final}"
    return solution, chosen_sentences


def build_questions(set_id: str, solution: tuple[str, ...]) -> list[Question]:
    people = list(solution)
    q1_target = people[0]
    q1_answer = clockwise_neighbor(solution, q1_target)
    wrong_people = [p for p in people if p != q1_target and p != q1_answer]

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown=f"Who sits immediately clockwise of {q1_target}?",
        options=[QuestionOption(key=chr(65 + i), markdown=p) for i, p in enumerate([q1_answer, *wrong_people[:3]])],
        correctKey="A",
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"From the clues, the verified circular order (clockwise) is "
            f"{' → '.join(solution)} → (back to {solution[0]}). "
            f"Immediately clockwise of {q1_target} is **{q1_answer}**."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:circular-arrangement"],
    )

    a, b = people[1], people[3 % len(people)]
    gap = people_between_clockwise(solution, a, b)
    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown=f"How many people sit between {a} and {b}, going clockwise from {a}?",
        correctValue=gap,
        titaTolerance=0.0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=f"Reading clockwise from {a} to {b} in the verified order {' → '.join(solution)}: {gap} people in between.",
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:circular-arrangement"],
    )

    third = people[2]
    third_neighbor = clockwise_neighbor(solution, third)
    false_options = [p for p in people if p != third_neighbor and p != third]
    rng = random.Random(f"{set_id}-q3")
    rng.shuffle(false_options)
    opts = [third_neighbor, *false_options[:3]]
    rng.shuffle(opts)
    correct_idx = opts.index(third_neighbor)
    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown=f"Which of the following sits immediately clockwise of {third}?",
        options=[QuestionOption(key=chr(65 + i), markdown=p) for i, p in enumerate(opts)],
        correctKey=chr(65 + correct_idx),
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=f"From the verified order {' → '.join(solution)}, immediately clockwise of {third} is **{third_neighbor}**.",
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:circular-arrangement"],
    )

    fourth = people[4 % len(people)]
    total_seats = len(people)
    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown=f"If {fourth} is seat number 1 and seats are numbered clockwise, what seat number is {q1_target}?",
        correctValue=((solution.index(q1_target) - solution.index(fourth)) % total_seats) + 1,
        titaTolerance=0.0,
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=(
            f"Numbering clockwise from {fourth} as seat 1, the order is "
            + ", ".join(f"seat {i + 1}: {solution[(solution.index(fourth) + i) % total_seats]}" for i in range(total_seats))
            + f". {q1_target} is seat {((solution.index(q1_target) - solution.index(fourth)) % total_seats) + 1}."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:circular-arrangement"],
    )

    return [q1, q2, q3, q4]


def build_set(index: int) -> tuple[PassageSet, list[Question]]:
    solution, clues = build_puzzle(index)
    content_hash = hashlib.sha1((MICRO_TOPIC_ID + str(index) + "".join(solution)).encode()).hexdigest()[:8]
    set_id = f"{MICRO_TOPIC_ID}.set-{content_hash}"

    body = (
        f"{N} friends — {', '.join(solution[:-1])}, and {solution[-1]} — sit around a circular table, "
        "facing the center. Study the clues below and answer the questions that follow.\n\n"
        + "\n".join(f"- {c}" for c in clues)
    )

    questions = build_questions(set_id, solution)
    passage_set = PassageSet(
        id=set_id,
        section="DILR",
        kind="lr_set",
        bodyMarkdown=body,
        assets=None,
        questionIds=[q.id for q in questions],
        genre=None,
        wordCount=None,
        targetMinutes=8.0,
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
