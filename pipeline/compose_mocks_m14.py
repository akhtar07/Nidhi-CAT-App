"""
Milestone 14: 5 full + 5 sectional mocks (SPEC.md §9.1/§9.2).

mock-1 (Milestone 10) is already "Full Mock 1" / difficultyTier=easier / 22
QA questions reserved — it already satisfies §9.1's "Mock 1 slightly easier
than CAT" exactly, so this script builds what's missing on top of it:
mock-2..mock-5 (full) and 5 QA sectional mocks, escalating the same way
§9.1 specifies for full mocks ("Mock 1 slightly easier... Mocks 2-4 at CAT
level... Mock 5 harder") applied consistently across both full and
sectional sets.

Content reality (unchanged since Milestone 10, still true after Milestone
13): VARC has 7 questions total (need 24/mock) and DILR has 2 sets / 8
questions (need ~4-5 sets/mock) — nowhere near §9.1/§9.2's real target
volume. QA has 390 unreserved questions. So, like mock-1, every mock this
script produces is QA-only, with an explicit composedNote — never padded
with invented VARC/DILR content, never a silent short-cut. §9.2's own
wording anticipates exactly this case: "5 total if not [the bank allows
15]" — so 5 QA sectionals is the correct target, not a shortfall.

Difficulty escalation is implemented via a fixed {easy,medium,hard,very_hard}
count mix per tier (not just filtering itemElo, which would make a
"harder" mock topic-thin) — each mix always sums to 22 and stays well
within the pool's available counts per difficulty (checked below, and
verified again at runtime by the "not enough" guard).

Run (from /pipeline, cat-pipeline conda env): python compose_mocks_m14.py
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from pathlib import Path

from schemas import MockDefinition, MockSectionDef, Question

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
MOCKS_DIR = REPO_ROOT / "content" / "mocks"

SECTION_MINUTES = 40
QUESTIONS_PER_SECTION = 22

# {difficulty: count}, always summing to QUESTIONS_PER_SECTION. Tuned against
# the actual unreserved pool (easy 142, medium 149, hard 69, very_hard 30 as
# of this writing) so 10 mocks' worth (2 easier + 6 standard + 2 harder) never
# exceeds any bucket: very_hard 0*2+2*6+4*2=20/30, hard 3*2+5*6+8*2=52/69,
# medium 9*2+9*6+7*2=86/149, easy 10*2+6*6+3*2=62/142.
DIFFICULTY_MIX = {
    "easier": {"easy": 10, "medium": 9, "hard": 3, "very_hard": 0},
    "standard": {"easy": 6, "medium": 9, "hard": 5, "very_hard": 2},
    "harder": {"easy": 3, "medium": 7, "hard": 8, "very_hard": 4},
}
assert all(sum(mix.values()) == QUESTIONS_PER_SECTION for mix in DIFFICULTY_MIX.values())

COMPOSED_NOTE = (
    "QA section only: VARC has 7 questions total and DILR has 2 sets (8 questions) — far short "
    "of the 24Q/~5-set-per-mock SPEC.md §9.1/§9.2 targets, so including them would mean either "
    "inventing content (against CLAUDE.md's 'no placeholder or fake content' rule) or shipping a "
    "dead, un-skippable 40-minute empty section. Milestone 13's RC/DILR/VA pipelines need further "
    "scale-up (tracked in PROGRESS.md) before VARC/DILR sections can be added here."
)

# (mock number, difficultyTier) for the 5 full mocks. mock-1 already exists (easier) — this
# script only produces 2 through 5.
FULL_MOCK_TIERS = [
    (2, "standard"),
    (3, "standard"),
    (4, "standard"),
    (5, "harder"),
]

# 5 sectional mocks, same escalation pattern applied independently (SPEC.md doesn't mandate
# grading sectionals, but there's no reason not to given the content is there).
SECTIONAL_TIERS = [
    (1, "easier"),
    (2, "standard"),
    (3, "standard"),
    (4, "standard"),
    (5, "harder"),
]


def load_unreserved_qa() -> list[Question]:
    out = []
    for path in sorted(QUESTIONS_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        if data.get("section") == "QA" and not data.get("mockReserved"):
            out.append(Question(**data))
    return out


def select_by_difficulty_mix(pool_by_difficulty: dict[str, list[Question]], mix: dict[str, int], seed: str) -> list[Question]:
    """For each difficulty bucket, spread the pick across distinct micro-topics (same
    reasoning as compose_mock_1.py's select_spread — a mock section shouldn't cluster on one
    topic), then pop the chosen items out of the shared pool so later mocks can't reuse them."""
    rng = random.Random(seed)
    selected: list[Question] = []
    for difficulty, count in mix.items():
        if count == 0:
            continue
        bucket = pool_by_difficulty[difficulty]
        if len(bucket) < count:
            raise SystemExit(f"seed={seed}: need {count} {difficulty} QA items, only {len(bucket)} left")

        by_topic: dict[str, list[Question]] = defaultdict(list)
        for q in bucket:
            by_topic[q.microTopicIds[0]].append(q)
        for topic_bucket in by_topic.values():
            rng.shuffle(topic_bucket)
        topics = list(by_topic.keys())
        rng.shuffle(topics)

        chosen: list[Question] = []
        ti = 0
        while len(chosen) < count and any(by_topic[t] for t in topics):
            topic = topics[ti % len(topics)]
            ti += 1
            if by_topic[topic]:
                chosen.append(by_topic[topic].pop())

        for q in chosen:
            bucket.remove(q)
        selected.extend(chosen)
    return selected


def reserve(questions: list[Question]) -> None:
    for q in questions:
        path = QUESTIONS_DIR / f"{q.id}.json"
        data = json.loads(path.read_text())
        data["mockReserved"] = True
        path.write_text(json.dumps(data, indent=2) + "\n")


def write_mock(mock: MockDefinition) -> None:
    out_path = MOCKS_DIR / f"{mock.id}.json"
    out_path.write_text(json.dumps(json.loads(mock.model_dump_json()), indent=2) + "\n")
    n = sum(len(s.questionIds) for s in mock.sections)
    print(f"Wrote {out_path.relative_to(REPO_ROOT)} ({mock.kind}, {mock.difficultyTier}, {n} questions)")


def main() -> None:
    pool = load_unreserved_qa()
    pool_by_difficulty: dict[str, list[Question]] = defaultdict(list)
    for q in pool:
        pool_by_difficulty[q.difficulty].append(q)

    MOCKS_DIR.mkdir(parents=True, exist_ok=True)

    for number, tier in FULL_MOCK_TIERS:
        mock_id = f"mock-{number}"
        chosen = select_by_difficulty_mix(pool_by_difficulty, DIFFICULTY_MIX[tier], seed=mock_id)
        reserve(chosen)
        mock = MockDefinition(
            id=mock_id,
            title=f"Full Mock {number}",
            kind="full",
            difficultyTier=tier,
            sections=[MockSectionDef(section="QA", minutes=SECTION_MINUTES, questionIds=[q.id for q in chosen])],
            composedNote=COMPOSED_NOTE,
        )
        write_mock(mock)

    for number, tier in SECTIONAL_TIERS:
        mock_id = f"sectional-qa-{number}"
        chosen = select_by_difficulty_mix(pool_by_difficulty, DIFFICULTY_MIX[tier], seed=mock_id)
        reserve(chosen)
        mock = MockDefinition(
            id=mock_id,
            title=f"QA Sectional {number}",
            kind="sectional",
            difficultyTier=tier,
            sections=[MockSectionDef(section="QA", minutes=SECTION_MINUTES, questionIds=[q.id for q in chosen])],
            composedNote=(
                "VARC/DILR sectional mocks aren't shippable yet (7 VARC questions, 2 DILR sets — "
                "need ~24Q / ~5 sets respectively). SPEC.md §9.2 anticipates this: 'ship 5 total if "
                "not [the bank allows 15]' — this is that fallback, QA only."
            ),
        )
        write_mock(mock)


if __name__ == "__main__":
    main()
