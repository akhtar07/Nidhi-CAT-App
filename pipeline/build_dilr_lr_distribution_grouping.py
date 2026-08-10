"""
Content scale-up: dilr.lr.distribution-grouping (roi=5, previously 0 questions).

A classic matching-grid puzzle: 4 people, each with a unique pet AND a unique job (two
independent permutations to deduce together). Same DILR inversion as every other generator this
pass: generate the ground-truth mapping first, then add clues one at a time — direct ("X has the
Cat"), cross ("the Doctor has the Dog"), and negative ("Y is not the Artist") — brute-forcing all
4! x 4! = 576 combined possibilities after each addition until exactly one (pet-mapping,
job-mapping) pair survives every clue so far.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_lr_distribution_grouping.py
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
MICRO_TOPIC_ID = "dilr.lr.distribution-grouping"
VERIFIED_AT = "2026-08-10T00:00:00Z"

PEOPLE = ["Aria", "Ben", "Cora", "Dev"]
PETS = ["Cat", "Dog", "Fish", "Bird"]
JOBS = ["Doctor", "Teacher", "Engineer", "Artist"]


def candidate_clues(pet_of: dict[str, str], job_of: dict[str, str], rng: random.Random) -> list[tuple[str, tuple]]:
    clues: list[tuple[str, tuple]] = []
    for p in PEOPLE:
        clues.append((f"{p} has the {pet_of[p]}.", ("pet", p, pet_of[p])))
        clues.append((f"{p} is the {job_of[p]}.", ("job", p, job_of[p])))
    for p in PEOPLE:
        clues.append((f"The {job_of[p]} has the {pet_of[p]}.", ("cross", job_of[p], pet_of[p])))
    for p in PEOPLE:
        for pet in PETS:
            if pet != pet_of[p]:
                clues.append((f"{p} does not have the {pet}.", ("not_pet", p, pet)))
        for job in JOBS:
            if job != job_of[p]:
                clues.append((f"{p} is not the {job}.", ("not_job", p, job)))
    rng.shuffle(clues)
    return clues


def satisfies(pet_of: dict[str, str], job_of: dict[str, str], key: tuple) -> bool:
    kind = key[0]
    if kind == "pet":
        return pet_of[key[1]] == key[2]
    if kind == "job":
        return job_of[key[1]] == key[2]
    if kind == "cross":
        _, job, pet = key
        person = next(p for p in PEOPLE if job_of[p] == job)
        return pet_of[person] == pet
    if kind == "not_pet":
        return pet_of[key[1]] != key[2]
    if kind == "not_job":
        return job_of[key[1]] != key[2]
    raise ValueError(kind)


def all_solutions_consistent_with(keys: list[tuple]) -> list[tuple[dict, dict]]:
    found = []
    for pet_perm in itertools.permutations(PETS):
        pet_of = dict(zip(PEOPLE, pet_perm))
        for job_perm in itertools.permutations(JOBS):
            job_of = dict(zip(PEOPLE, job_perm))
            if all(satisfies(pet_of, job_of, k) for k in keys):
                found.append((pet_of, job_of))
    return found


def build_puzzle(seed: int) -> tuple[dict, dict, list[str]]:
    rng = random.Random(f"{MICRO_TOPIC_ID}-{seed}")
    pet_of = dict(zip(PEOPLE, rng.sample(PETS, len(PETS))))
    job_of = dict(zip(PEOPLE, rng.sample(JOBS, len(JOBS))))

    clues = candidate_clues(pet_of, job_of, rng)
    chosen_keys: list[tuple] = []
    chosen_sentences: list[str] = []
    for sentence, key in clues:
        chosen_keys.append(key)
        chosen_sentences.append(sentence)
        remaining = all_solutions_consistent_with(chosen_keys)
        assert (pet_of, job_of) in remaining, "the true solution must always satisfy its own true clues"
        if len(remaining) == 1:
            break
    else:
        raise RuntimeError(f"seed {seed}: exhausted all clues without reaching a unique solution")

    final = all_solutions_consistent_with(chosen_keys)
    assert len(final) == 1 and final[0] == (pet_of, job_of), f"seed {seed}: clue set is not actually unique"
    return pet_of, job_of, chosen_sentences


def build_questions(set_id: str, pet_of: dict, job_of: dict) -> list[Question]:
    p0 = PEOPLE[0]
    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown=f"What pet does {p0} have?",
        options=[QuestionOption(key=chr(65 + i), markdown=pet) for i, pet in enumerate(PETS)],
        correctKey=chr(65 + PETS.index(pet_of[p0])),
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Full solution (from the clues): "
            + "; ".join(f"{p}: {pet_of[p]}, {job_of[p]}" for p in PEOPLE)
            + f". {p0} has the **{pet_of[p0]}**."
        ),
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:distribution-grouping"],
    )

    pet_person = next(p for p in PEOPLE if pet_of[p] == PETS[1])
    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown=f"Who has the {PETS[1]}?",
        options=[QuestionOption(key=chr(65 + i), markdown=p) for i, p in enumerate(PEOPLE)],
        correctKey=chr(65 + PEOPLE.index(pet_person)),
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=f"From the full solution, **{pet_person}** has the {PETS[1]}.",
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:distribution-grouping"],
    )

    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown=f"What is {p0}'s job?",
        options=[QuestionOption(key=chr(65 + i), markdown=job) for i, job in enumerate(JOBS)],
        correctKey=chr(65 + JOBS.index(job_of[p0])),
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=f"From the full solution, {p0} is the **{job_of[p0]}**.",
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:distribution-grouping"],
    )

    doctor_person = next(p for p in PEOPLE if job_of[p] == "Doctor")
    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="What pet does the Doctor have?",
        options=[QuestionOption(key=chr(65 + i), markdown=pet) for i, pet in enumerate(PETS)],
        correctKey=chr(65 + PETS.index(pet_of[doctor_person])),
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=f"The Doctor is {doctor_person}, who has the **{pet_of[doctor_person]}**.",
        targetSeconds=90,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:distribution-grouping"],
    )

    return [q1, q2, q3, q4]


def build_set(index: int) -> tuple[PassageSet, list[Question]]:
    pet_of, job_of, clues = build_puzzle(index)
    content_hash = hashlib.sha1((MICRO_TOPIC_ID + str(index) + "".join(pet_of.values()) + "".join(job_of.values())).encode()).hexdigest()[:8]
    set_id = f"{MICRO_TOPIC_ID}.set-{content_hash}"

    body = (
        f"{len(PEOPLE)} friends — {', '.join(PEOPLE[:-1])}, and {PEOPLE[-1]} — each have a "
        f"different pet ({', '.join(PETS)}) and a different job ({', '.join(JOBS)}). Study the "
        "clues below and answer the questions that follow.\n\n"
        + "\n".join(f"- {c}" for c in clues)
    )

    questions = build_questions(set_id, pet_of, job_of)
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
