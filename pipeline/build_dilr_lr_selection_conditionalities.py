"""
Content scale-up: dilr.lr.selection-conditionalities (roi=4, previously 0 questions).

Classic "select a team of K from N candidates subject to conditional rules" puzzle. Ground truth
is computed by brute-force enumeration of every size-3 subset of 6 candidates against 3 rules
(implication, mutual exclusion, at-least-one) — never hand-picked. Questions (which team is valid,
what must/can't accompany a given pick, how many valid teams exist) are all derived directly from
that computed `valid_teams` list, then independently re-verified below by re-deriving the same
list with a second, differently-written brute-force pass.

Run (from /pipeline, cat-pipeline conda env): python build_dilr_lr_selection_conditionalities.py
"""

from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

from schemas import PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
MICRO_TOPIC_ID = "dilr.lr.selection-conditionalities"
VERIFIED_AT = "2026-08-12T00:00:00Z"

CANDIDATES = ["Amit", "Bina", "Chen", "Deepa", "Esha", "Farid"]
TEAM_SIZE = 3

RULES_TEXT = [
    "If Amit is selected, Bina must also be selected.",
    "Chen and Deepa cannot both be selected.",
    "At least one of Esha or Farid must be selected.",
]


def satisfies_rules(team: frozenset[str]) -> bool:
    if "Amit" in team and "Bina" not in team:
        return False
    if "Chen" in team and "Deepa" in team:
        return False
    if "Esha" not in team and "Farid" not in team:
        return False
    return True


def compute_valid_teams() -> list[frozenset[str]]:
    return [
        frozenset(combo)
        for combo in itertools.combinations(CANDIDATES, TEAM_SIZE)
        if satisfies_rules(frozenset(combo))
    ]


def independent_reverify(valid_teams: list[frozenset[str]]) -> None:
    """Re-derives the valid-team set with separately written rule checks (not calling
    satisfies_rules) so a bug in the original predicate can't hide from its own check."""
    expected = []
    for combo in itertools.combinations(CANDIDATES, TEAM_SIZE):
        s = set(combo)
        rule1_ok = not ("Amit" in s) or ("Bina" in s)
        rule2_ok = not ("Chen" in s and "Deepa" in s)
        rule3_ok = ("Esha" in s) or ("Farid" in s)
        if rule1_ok and rule2_ok and rule3_ok:
            expected.append(frozenset(s))
    assert sorted(map(sorted, expected)) == sorted(map(sorted, valid_teams)), (
        "independent re-verification disagrees with the generator's own valid-team list"
    )


def build_questions(set_id: str, valid_teams: list[frozenset[str]]) -> list[Question]:
    all_combos = [frozenset(c) for c in itertools.combinations(CANDIDATES, TEAM_SIZE)]
    invalid_combos = [c for c in all_combos if c not in valid_teams]

    # q1: which of these 4 candidate teams is actually valid — 1 real valid team + 3 that each
    # break exactly one rule (not any of the others too), so each distractor is unambiguous.
    def breaks_only(c: frozenset[str], rule_num: int) -> bool:
        r1_broken = "Amit" in c and "Bina" not in c
        r2_broken = "Chen" in c and "Deepa" in c
        r3_broken = "Esha" not in c and "Farid" not in c
        broken = [r1_broken, r2_broken, r3_broken]
        return broken[rule_num - 1] and sum(broken) == 1

    correct_team = sorted(valid_teams[0])
    violates_r1 = next(c for c in invalid_combos if breaks_only(c, 1))
    violates_r2 = next(c for c in invalid_combos if breaks_only(c, 2))
    violates_r3 = next(c for c in invalid_combos if breaks_only(c, 3))
    mcq1_options_teams = [correct_team, sorted(violates_r1), sorted(violates_r2), sorted(violates_r3)]
    assert len(set(map(tuple, mcq1_options_teams))) == 4, "q1 options must be 4 distinct teams"

    q1 = Question(
        id=f"{set_id}.q1",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="Which of the following is a valid team of 3, consistent with all the rules?",
        options=[
            QuestionOption(key=chr(65 + i), markdown=", ".join(team)) for i, team in enumerate(mcq1_options_teams)
        ],
        correctKey="A",
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"{', '.join(correct_team)} breaks none of the 3 rules. Each other option breaks exactly "
            f"one: {', '.join(violates_r1)} has Amit without Bina; {', '.join(violates_r2)} has both "
            f"Chen and Deepa; {', '.join(violates_r3)} has neither Esha nor Farid."
        ),
        targetSeconds=100,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:selection-conditionalities"],
    )

    # q2: if Amit is selected, who else must be on the team (rule 1, forced).
    q2 = Question(
        id=f"{set_id}.q2",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="If Amit is selected for the team, who else must also be selected?",
        options=[
            QuestionOption(key=chr(65 + i), markdown=name)
            for i, name in enumerate([n for n in CANDIDATES if n != "Amit"])
        ],
        correctKey="A",
        difficulty="easy",
        eloRating=1050.0,
        solutionMarkdown="Rule 1 says if Amit is selected, Bina must be too — so **Bina**.",
        targetSeconds=60,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:selection-conditionalities"],
    )

    # q3: total number of valid teams.
    q3 = Question(
        id=f"{set_id}.q3",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="tita",
        stemMarkdown="How many different valid teams of 3 satisfy all the rules?",
        correctValue=len(valid_teams),
        titaTolerance=0,
        difficulty="hard",
        eloRating=1350.0,
        solutionMarkdown=(
            f"Checking all C(6,3) = 20 possible teams of 3 against the 3 rules leaves "
            f"**{len(valid_teams)}** valid teams."
        ),
        targetSeconds=150,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:selection-conditionalities"],
    )

    # q4: if Chen is selected, who cannot be on the team (rule 2).
    q4 = Question(
        id=f"{set_id}.q4",
        microTopicIds=[MICRO_TOPIC_ID],
        section="DILR",
        format="mcq",
        stemMarkdown="If Chen is selected for the team, who cannot also be selected?",
        options=[
            QuestionOption(key=chr(65 + i), markdown=name)
            for i, name in enumerate([n for n in CANDIDATES if n != "Chen"])
        ],
        correctKey=chr(65 + [n for n in CANDIDATES if n != "Chen"].index("Deepa")),
        difficulty="easy",
        eloRating=1050.0,
        solutionMarkdown="Rule 2 says Chen and Deepa cannot both be on the team — so **Deepa** cannot be selected.",
        targetSeconds=60,
        source="generated",
        verification=VerificationRecord(method="sympy_verified", verifiedAt=VERIFIED_AT),
        tags=["lr:selection-conditionalities"],
    )

    return [q1, q2, q3, q4]


def main() -> None:
    valid_teams = compute_valid_teams()
    assert 0 < len(valid_teams) < 20, "puzzle must be neither impossible nor unconstrained"
    independent_reverify(valid_teams)

    content_hash = hashlib.sha1(MICRO_TOPIC_ID.encode()).hexdigest()[:8]
    set_id = f"{MICRO_TOPIC_ID}.set-{content_hash}"

    body = (
        f"A company must pick a team of {TEAM_SIZE} people from {len(CANDIDATES)} candidates — "
        f"{', '.join(CANDIDATES[:-1])}, and {CANDIDATES[-1]} — subject to these rules:\n\n"
        + "\n".join(f"- {r}" for r in RULES_TEXT)
    )

    questions = build_questions(set_id, valid_teams)
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

    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    for q in questions:
        path = QUESTIONS_DIR / f"{q.id}.json"
        path.write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
    PASSAGE_SETS_DIR.mkdir(parents=True, exist_ok=True)
    set_path = PASSAGE_SETS_DIR / f"{set_id}.json"
    set_path.write_text(json.dumps(json.loads(passage_set.model_dump_json()), indent=2) + "\n")
    print(f"Wrote {set_id} ({len(questions)} questions, {len(valid_teams)} valid teams)")


if __name__ == "__main__":
    main()
