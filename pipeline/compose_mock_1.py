"""
Milestone 10: composes the first mock from the existing, already-verified
QA bank and flags the chosen items mockReserved (SPEC.md §9.1: "maintain a
mock_reserved flag on items so the drill engine can never serve them").

Real CAT QA is 22 questions. VARC (24Q) and DILR (20Q, as sets) have no
content yet — Milestone 13 ("Content pipeline v3") is where that gets
built — so this mock's VARC/DILR sections are genuinely empty rather than
padded with anything invented. The mock *engine* (Milestone 10) is built to
handle N sections generically; this is a content gap, not an engine one,
and composedNote says so explicitly rather than silently.

Never invents a question — only selects ids that already exist and already
passed verification, per CLAUDE.md's "no placeholder or fake content" rule.

Run (from /pipeline, cat-pipeline conda env): python compose_mock_1.py
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

QA_TARGET_COUNT = 22
MOCK_ID = "mock-1"


def load_qa_questions() -> list[Question]:
    out = []
    for path in sorted(QUESTIONS_DIR.glob("*.json")):
        data = json.loads(path.read_text())
        if data.get("section") == "QA" and not data.get("mockReserved"):
            out.append(Question(**data))
    return out


def select_spread(questions: list[Question], count: int) -> list[Question]:
    """Picks `count` items spread across as many distinct micro-topics and
    difficulties as possible, rather than clustering — a real mock section
    shouldn't be 22 percentage questions."""
    by_topic: dict[str, list[Question]] = defaultdict(list)
    for q in questions:
        by_topic[q.microTopicIds[0]].append(q)

    rng = random.Random(MOCK_ID)
    for bucket in by_topic.values():
        rng.shuffle(bucket)

    topics = list(by_topic.keys())
    rng.shuffle(topics)

    selected: list[Question] = []
    ti = 0
    while len(selected) < count and any(by_topic[t] for t in topics):
        topic = topics[ti % len(topics)]
        ti += 1
        if by_topic[topic]:
            selected.append(by_topic[topic].pop())

    return selected[:count]


def main() -> None:
    qa_pool = load_qa_questions()
    if len(qa_pool) < QA_TARGET_COUNT:
        raise SystemExit(f"Only {len(qa_pool)} unreserved QA questions available, need {QA_TARGET_COUNT}")

    chosen = select_spread(qa_pool, QA_TARGET_COUNT)
    chosen_ids = [q.id for q in chosen]

    for q in chosen:
        path = QUESTIONS_DIR / f"{q.id}.json"
        data = json.loads(path.read_text())
        data["mockReserved"] = True
        path.write_text(json.dumps(data, indent=2) + "\n")

    mock = MockDefinition(
        id=MOCK_ID,
        title="Full Mock 1",
        kind="full",
        difficultyTier="easier",
        # VARC and QA sections are omitted entirely rather than included empty: the mock engine's
        # per-section timer runs for the section's full duration regardless of question count, so
        # an empty 40-minute VARC/DILR block would force sitting through dead time before ever
        # reaching real content — worse than just not offering those sections yet. Once real
        # VARC/DILR-set content exists (Milestone 13), this mock gets regenerated with all three.
        sections=[
            MockSectionDef(section="QA", minutes=40, questionIds=chosen_ids),
        ],
        composedNote=(
            "VARC and DILR sections aren't included yet: no VARC content exists, and the one "
            "DILR set that does is already used in the Passage/Set player demo rather than "
            "reserved for a mock. Milestone 13 (Content pipeline v3) is where RC/VA/DILR-set "
            "generation happens — this mock exercises the real section-locked, timed engine on "
            "the one section that has enough verified content, rather than padding the other two "
            "sections with an empty, un-skippable 40-minute block."
        ),
    )

    MOCKS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = MOCKS_DIR / f"{MOCK_ID}.json"
    out_path.write_text(json.dumps(json.loads(mock.model_dump_json()), indent=2) + "\n")
    print(f"Wrote {out_path.relative_to(REPO_ROOT)} with {len(chosen_ids)} QA questions reserved")


if __name__ == "__main__":
    main()
