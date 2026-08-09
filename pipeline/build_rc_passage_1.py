"""
Milestone 13: the first real RC passage (SPEC.md §6.1 Tier 2 + §6.3).

The passage is real, hand-selected, open-licence text — never LLM-generated
(SPEC.md §6.1: "Do not generate RC passages with an LLM ... LLM prose is
too clean, too structured, and trains the wrong reading reflexes"):

  Source: "On Liberty" (Walter Scott Publishing Co., 1901 edition),
  introduction by W. L. Courtney, discussing John Stuart Mill's
  intellectual relationship with Harriet Taylor Mill.
  Project Gutenberg ebook #34901: https://www.gutenberg.org/ebooks/34901
  Licence: Public domain (Courtney's introduction, published 1901; both he
  and Mill died more than 70 years ago). Project Gutenberg's own licence
  terms additionally apply to this specific digitised text.

Only the *questions* are generated (qagen/rc_harness.py), each required to
pass SPEC.md §6.3's answerability check (5 independent solves given only
the passage, >=4 must agree with the claimed answer) and to cite a
justifying span that exists verbatim in the passage — never invents facts
not in the text.

Run (from /pipeline, cat-pipeline conda env, with Ollama serving):
    python build_rc_passage_1.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from qagen import llm_client
from qagen.rc_harness import generate_one_rc_question
from schemas import PassageSet, Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
PASSAGE_SETS_DIR = REPO_ROOT / "content" / "passage-sets"
VERIFIED_AT = "2026-08-10T00:00:00Z"

SET_ID = "varc.rc.on-liberty-intro.set-01"
SOURCE_URL = "https://www.gutenberg.org/ebooks/34901"
LICENCE = "Public domain (Project Gutenberg #34901)"

PASSAGE_TEXT = (
    'It is easy for the ordinary worldly cynicism to curl a sceptical lip over sentences like '
    'these. There may be exaggeration of sentiment, the necessary and inevitable reaction of a '
    'man who was trained according to the "dry light" of so unimpressionable a man as James Mill, '
    'the father; but the passage quoted is not the only one in which John Stuart Mill proclaims '
    'his unhesitating belief in the intellectual influence of his wife. The treatise on Liberty '
    'was written especially under her authority and encouragement, but there are many earlier '
    'references to the power which she exercised over his mind. Mill was introduced to her as '
    "early as 1831, at a dinner-party at Mr. Taylor's house, where were present, amongst others, "
    "Roebuck, W. J. Fox, and Miss Harriet Martineau. The acquaintance rapidly ripened into "
    "intimacy and the intimacy into friendship, and Mill was never weary of expatiating on all "
    "the advantages of so singular a relationship. In some of the presentation copies of his work "
    'on Political Economy, he wrote the following dedication:--"To Mrs. John Taylor, who, of all '
    "persons known to the author, is the most highly qualified either to originate or to "
    'appreciate speculation on social advancement, this work is with the highest respect and '
    'esteem dedicated." An article on the enfranchisement of women was made the occasion for '
    "another encomium. We shall hardly be wrong in attributing a much later book, The Subjection "
    "of Women, published in 1869, to the influence wielded by Mrs. Taylor. Finally, the pages of "
    'the Autobiography ring with the dithyrambic praise of his "almost infallible counsellor."\n\n'
    "The facts of this remarkable intimacy can easily be stated. The deductions are more "
    "difficult. There is no question that Mill's infatuation was the cause of considerable "
    "trouble to his acquaintances and friends. His father openly taxed him with being in love "
    "with another man's wife. Roebuck, Mrs. Grote, Mrs. Austin, Miss Harriet Martineau were "
    "amongst those who suffered because they made some allusion to a forbidden subject. Mrs. "
    "Taylor lived with her daughter in a lodging in the country; but in 1851 her husband died, "
    "and then Mill made her his wife. Opinions were widely divergent as to her merits; but every "
    "one agreed that up to the time of her death, in 1858, Mill was wholly lost to his friends. "
    "George Mill, one of Mill's younger brothers, gave it as his opinion that she was a clever "
    'and remarkable woman, but "nothing like what John took her to be." Carlyle, in his '
    'reminiscences, described her with ambiguous epithets. She was "vivid," "iridescent," "pale '
    'and passionate and sad-looking, a living-romance heroine of the royalist volition and '
    'questionable destiny." It is not possible to make much of a judgment like this, but we get '
    'on more certain ground when we discover that Mrs. Carlyle said on one occasion that "she is '
    'thought to be dangerous," and that Carlyle added that she was worse than dangerous, she was '
    "patronising. The occasion when Mill and his wife were brought into close contact with the "
    "Carlyles is well known."
)

TARGET_QUESTION_COUNT = 4

QUESTION_TYPE_TO_MICROTOPIC = {
    "main_idea": "varc.rc.main-idea",
    "detail": "varc.rc.direct-detail",
    "inference": "varc.rc.inference",
    "tone": "varc.rc.tone-attitude",
    "structure": "varc.rc.structure-function",
    "vocab_in_context": "varc.rc.vocab-in-context",
}


def build_questions() -> list[Question]:
    if not llm_client.server_is_up():
        raise SystemExit(f"No LLM server reachable at {llm_client.VLLM_BASE_URL}. Start Ollama first.")

    accepted: list[Question] = []
    used_types: list[str] = []
    attempts = 0
    max_attempts = TARGET_QUESTION_COUNT * 4

    while len(accepted) < TARGET_QUESTION_COUNT and attempts < max_attempts:
        attempts += 1
        draft, reason = generate_one_rc_question(PASSAGE_TEXT, used_types)
        if draft is None:
            print(f"  attempt {attempts}: REJECTED - {reason.stage}: {reason.detail}")  # type: ignore[union-attr]
            continue

        q_type = draft.get("question_type", "detail")
        micro_topic_id = QUESTION_TYPE_TO_MICROTOPIC.get(q_type, "varc.rc.direct-detail")
        options = draft["options"]
        content_hash_src = micro_topic_id + "|" + draft["stem"]
        qid = f"{SET_ID}.q{len(accepted) + 1}-{hashlib.sha1(content_hash_src.encode()).hexdigest()[:8]}"

        question = Question(
            id=qid,
            microTopicIds=[micro_topic_id],
            section="VARC",
            format="mcq",
            stemMarkdown=draft["stem"],
            options=[QuestionOption(key=o["key"], markdown=o["markdown"]) for o in options],
            correctKey=draft["correct_key"],
            difficulty="medium",
            eloRating=1200.0,
            solutionMarkdown=draft.get("solution", "") or "See the passage for the justifying detail.",
            targetSeconds=90,
            source="generated",
            sourceRef=None,
            verification=VerificationRecord(
                method="answerability_pass",
                verifiedAt=VERIFIED_AT,
                selfConsistencyAgreement=None,
                distractorAuditPassed=None,
                dedupChecked=None,
                reviewerNote=f"justifying span: {draft.get('justifying_span', '')[:200]}",
            ),
            tags=[f"rc:{q_type}"],
        )
        accepted.append(question)
        used_types.append(q_type)
        print(f"  attempt {attempts}: accepted ({q_type} -> {micro_topic_id})")

    if len(accepted) < TARGET_QUESTION_COUNT:
        print(f"WARNING: only {len(accepted)}/{TARGET_QUESTION_COUNT} questions verified after {attempts} attempts")

    return accepted


def build_passage_set(questions: list[Question]) -> PassageSet:
    word_count = len(PASSAGE_TEXT.split())
    return PassageSet(
        id=SET_ID,
        section="VARC",
        kind="rc_passage",
        bodyMarkdown=PASSAGE_TEXT,
        assets=None,
        questionIds=[q.id for q in questions],
        genre="Humanities/Biography",
        wordCount=word_count,
        targetMinutes=round(word_count / 100 + len(questions) * 1.2, 1),
        licence=LICENCE,
        sourceUrl=SOURCE_URL,
    )


def main() -> None:
    questions = build_questions()
    if not questions:
        raise SystemExit("No questions survived verification — nothing written.")

    passage_set = build_passage_set(questions)

    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    for q in questions:
        path = QUESTIONS_DIR / f"{q.id}.json"
        path.write_text(json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
        print(f"Wrote {path.relative_to(REPO_ROOT)}")

    PASSAGE_SETS_DIR.mkdir(parents=True, exist_ok=True)
    set_path = PASSAGE_SETS_DIR / f"{SET_ID}.json"
    set_path.write_text(json.dumps(json.loads(passage_set.model_dump_json()), indent=2) + "\n")
    print(f"Wrote {set_path.relative_to(REPO_ROOT)} with {len(questions)} questions")


if __name__ == "__main__":
    main()
