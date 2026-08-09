"""
Milestone 13: VARC-VA para-jumbles (varc.va.para-jumbles), SPEC.md §6.1 Tier 2
discipline extended to a structural question type instead of comprehension:
real, open-licence prose (same source as build_rc_passage_1.py — Project
Gutenberg #34901, "On Liberty," public domain), never LLM-generated. The
correct order is simply the sentences' real original order in the source
text, so — unlike RC's questions — there is nothing to verify by LLM at
all: the answer key is self-evident from how the sentences were extracted,
and the shuffle + label assignment is computed in code, not decided by
hand, so a labelling mistake would show up as a failed assertion instead
of shipping quietly wrong.

Each cluster below is copied verbatim (including the original's own
punctuation, italics-underscores stripped) from a genuinely coherent,
self-contained run of consecutive sentences in the source — never
reordered, trimmed, or reworded before being listed here.

Run (from /pipeline, cat-pipeline conda env): python build_va_parajumbles.py
"""

from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from schemas import Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
VERIFIED_AT = "2026-08-10T00:00:00Z"
MICRO_TOPIC_ID = "varc.va.para-jumbles"
SOURCE_NOTE = 'Sentences excerpted verbatim from "On Liberty" (intro. by W. L. Courtney), Project Gutenberg #34901, public domain.'

# Each cluster's sentences are listed in their real, original order.
CLUSTERS: list[list[str]] = [
    [
        "To any one whose thoughts have been occupied with the sphere of abstract speculation, "
        "the lively and vivid presentment of concrete fact comes as a delightful and agreeable shock.",
        "The instinct of the woman often enables her not only to apprehend but to illustrate a truth "
        "for which she would be totally unable to give the adequate philosophic reasoning.",
        "On the other hand, the man, with the more careful logical methods and the slow processes of "
        "formal reasoning, is apt to suppose that the happy intuition which leaps to the conclusion is "
        "really based on the intellectual processes of which he is conscious in his own case.",
        "Thus both parties to the happy contract are equally pleased.",
        "The abstract truth gets the concrete illustration; the concrete illustration finds its proper "
        "foundation in a series of abstract inquiries.",
    ],
    [
        "Every one will judge for himself of this romantic episode in Mill's career, according to such "
        "experience as he may possess of the philosophic mind and of the value of these curious but not "
        "infrequent relationships.",
        "It may have been a piece of infatuation, or, if we prefer to say so, it may have been the most "
        "gracious and the most human page in Mill's career.",
        "Mrs. Mill may have flattered her husband's vanity by echoing his opinions, or she may have "
        "indeed been an Egeria, full of inspiration and intellectual helpfulness.",
        "What usually happens in these cases,--although the philosopher himself, through his belief in "
        "the equality of the sexes, was debarred from thinking so,--is the extremely valuable action and "
        "reaction of two different classes and orders of mind.",
    ],
    [
        "From this it would appear that she gave Mill that tendency to Socialism which, while it lends a "
        "progressive spirit to his speculations on politics, at the same time does not manifestly accord "
        "with his earlier advocacy of peasant proprietorships.",
        "Nor, again, is it, on the face of it, consistent with those doctrines of individual liberty "
        "which, aided by the intellectual companionship of his wife, he propounded in a later work.",
        "The ideal of individual freedom is not the ideal of Socialism, just as that invocation of "
        "governmental aid to which the Socialist resorts is not consistent with the theory of laisser-faire.",
        "Yet Liberty was planned by Mill and his wife in concert.",
    ],
]

LABELS = ["A", "B", "C", "D", "E"]


def build_one(cluster_index: int, original_order: list[str]) -> Question:
    rng = random.Random(f"{MICRO_TOPIC_ID}-{cluster_index}")
    n = len(original_order)
    labels = LABELS[:n]

    shuffled_indices = list(range(n))
    while True:
        rng.shuffle(shuffled_indices)
        if shuffled_indices != list(range(n)):  # never present them already-in-order
            break

    # label -> original sentence it displays
    label_to_sentence = {labels[i]: original_order[shuffled_indices[i]] for i in range(n)}
    # original sentence -> which label it ended up under
    sentence_to_label = {v: k for k, v in label_to_sentence.items()}
    correct_sequence = "".join(sentence_to_label[s] for s in original_order)

    # Verify: reading the shuffled sentences back in `correct_sequence` order reconstructs the original.
    reconstructed = [label_to_sentence[label] for label in correct_sequence]
    assert reconstructed == original_order, f"cluster {cluster_index}: reconstruction mismatch"

    stem_lines = "\n\n".join(f"{label}. {label_to_sentence[label]}" for label in labels)
    stem = (
        f"The following {n} sentences, when arranged in the correct order, form a coherent paragraph. "
        f"Enter the correct sequence (e.g. {''.join(labels)}).\n\n{stem_lines}"
    )

    content_hash = hashlib.sha1((MICRO_TOPIC_ID + str(cluster_index) + correct_sequence).encode()).hexdigest()[:10]
    return Question(
        id=f"{MICRO_TOPIC_ID}.authored-{content_hash}",
        microTopicIds=[MICRO_TOPIC_ID],
        section="VARC",
        format="tita",
        stemMarkdown=stem,
        correctValue=correct_sequence,
        titaTolerance=0.0,
        difficulty="medium",
        eloRating=1200.0,
        solutionMarkdown=(
            f"Original order: {correct_sequence}. Read in this order, the sentences form one "
            f"continuous argument:\n\n" + "\n\n".join(original_order)
        ),
        targetSeconds=90,
        source="authored",
        sourceRef=SOURCE_NOTE,
        verification=VerificationRecord(
            method="human_reviewed",
            verifiedAt=VERIFIED_AT,
            reviewerNote="Sentence order is the source text's real original order, not an LLM claim.",
        ),
        tags=["va:para-jumble"],
    )


def main() -> None:
    questions = [build_one(i, cluster) for i, cluster in enumerate(CLUSTERS)]
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    for q in questions:
        path = QUESTIONS_DIR / f"{q.id}.json"
        path.write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
        print(f"Wrote {path.relative_to(REPO_ROOT)} (answer: {q.correctValue})")


if __name__ == "__main__":
    main()
