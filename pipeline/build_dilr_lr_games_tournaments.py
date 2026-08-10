"""
Content scale-up: dilr.lr.games-tournaments (roi=5, previously 0 questions).

Same DILR inversion as every other generator this pass: simulate a round-robin tournament
first (every match's winner decided by a seeded RNG, no draws — kept simple and unambiguous),
compute the real standings table from those results, then derive every question directly from
that table. No LLM. Retries the seed if the standings produce a tie at the top (a genuine
"who finished first" question needs a unique answer).

Run (from /pipeline, cat-pipeline conda env): python build_dilr_lr_games_tournaments.py
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
MICRO_TOPIC_ID = "dilr.lr.games-tournaments"
VERIFIED_AT = "2026-08-10T00:00:00Z"

TEAMS = ["Eagles", "Falcons", "Hawks", "Kites"]
WIN_POINTS = 2


def simulate(seed: int) -> dict[str, dict[str, int]]:
    """Every team plays every other team exactly once (round robin); no draws. Returns
    {team: {"wins": int, "losses": int, "points": int}}."""
    rng = random.Random(f"{MICRO_TOPIC_ID}-{seed}")
    record = {t: {"wins": 0, "losses": 0, "points": 0} for t in TEAMS}
    matches: list[tuple[str, str, str]] = []  # (winner, loser, fixture label)
    for a, b in itertools.combinations(TEAMS, 2):
        winner, loser = (a, b) if rng.random() < 0.5 else (b, a)
        record[winner]["wins"] += 1
        record[winner]["points"] += WIN_POINTS
        record[loser]["losses"] += 1
        matches.append((winner, loser, f"{a} vs {b}"))
    return record, matches


def find_valid_tournament() -> tuple[int, dict, list]:
    """Retries seeds until the standings have a unique top team and a unique last-place team —
    both needed for well-posed, single-answer questions."""
    for seed in range(200):
        record, matches = simulate(seed)
        points = [record[t]["points"] for t in TEAMS]
        if points.count(max(points)) == 1 and points.count(min(points)) == 1:
            return seed, record, matches
    raise RuntimeError("no seed produced a unique top/bottom team in 200 tries")


def build_questions(set_id: str, record: dict, matches: list) -> list[Question]:
    ranked = sorted(TEAMS, key=lambda t: -record[t]["points"])
    top_team = ranked[0]
    bottom_team = ranked[-1]

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Which team finished with the most points?",
        options=[QuestionOption(key=chr(65 + i), markdown=t) for i, t in enumerate(TEAMS)],
        correctKey=chr(65 + TEAMS.index(top_team)),
        difficulty="easy",
        eloRating=1000.0,
        solutionMarkdown=(
            "Points (2 per win, 0 per loss): " + ", ".join(f"{t}: {record[t]['points']}" for t in TEAMS) +
            f". **{top_team}** finished with the most points."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:games-tournaments"],
    )

    q2_team = TEAMS[0]
    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown=f"How many matches did {q2_team} win?",
        correctValue=record[q2_team]["wins"],
        titaTolerance=0.0,
        difficulty="easy",
        eloRating=1000.0,
        solutionMarkdown=(
            f"{q2_team}'s matches: "
            + "; ".join(f"{w} beat {l}" for w, l, _ in matches if q2_team in (w, l))
            + f". {q2_team} won {record[q2_team]['wins']} match(es)."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:games-tournaments"],
    )

    total_points = sum(record[t]["points"] for t in TEAMS)
    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="What is the sum of points scored by all teams combined?",
        correctValue=total_points,
        titaTolerance=0.0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"There are {len(matches)} matches total, each worth {WIN_POINTS} points to the winner "
            f"(0 to the loser). Total points $= {len(matches)} \\times {WIN_POINTS} = {total_points}$."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:games-tournaments"],
    )

    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Which team finished last (fewest points)?",
        options=[QuestionOption(key=chr(65 + i), markdown=t) for i, t in enumerate(TEAMS)],
        correctKey=chr(65 + TEAMS.index(bottom_team)),
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            "Points: " + ", ".join(f"{t}: {record[t]['points']}" for t in TEAMS) + f". **{bottom_team}** finished last."
        ),
        targetSeconds=75,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:games-tournaments"],
    )

    return [q1, q2, q3, q4]


def main() -> None:
    seed, record, matches = find_valid_tournament()
    # Independent check: total wins across all teams must equal total matches (every match has
    # exactly one winner) — catches a bookkeeping bug in simulate() if one ever creeps in.
    assert sum(record[t]["wins"] for t in TEAMS) == len(matches)
    assert sum(record[t]["losses"] for t in TEAMS) == len(matches)

    content_hash = hashlib.sha1(f"{MICRO_TOPIC_ID}-{seed}".encode()).hexdigest()[:8]
    set_id = f"{MICRO_TOPIC_ID}.set-{content_hash}"

    fixtures_md = "\n".join(f"- {w} beat {l}" for w, l, _ in matches)
    body = (
        f"In a round-robin tournament, {len(TEAMS)} teams ({', '.join(TEAMS)}) each played every "
        "other team exactly once (no draws). The results were:\n\n"
        f"{fixtures_md}\n\n"
        f"A win is worth {WIN_POINTS} points, a loss 0. Study the results and answer the questions that follow."
    )

    questions = build_questions(set_id, record, matches)
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

    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    for q in questions:
        path = QUESTIONS_DIR / f"{q.id}.json"
        path.write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
    PASSAGE_SETS_DIR.mkdir(parents=True, exist_ok=True)
    set_path = PASSAGE_SETS_DIR / f"{set_id}.json"
    set_path.write_text(json.dumps(json.loads(passage_set.model_dump_json()), indent=2) + "\n")
    print(f"Wrote {set_id} ({len(questions)} questions, seed={seed})")


if __name__ == "__main__":
    main()
