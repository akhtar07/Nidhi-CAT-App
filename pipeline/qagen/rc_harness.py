"""
RC (Reading Comprehension) question generation + verification (SPEC.md §6.1
Tier 2 / §6.3). The passage itself is never LLM-generated — real, open-
licence prose only, hand-selected and passed in — only the questions are
synthesised, and each one has to survive a different gate than QA's SymPy
check:

  "a separate 'answerability' pass where the model, given only the passage
  and the question (never the intended answer), must independently select
  the same option in 4 of 5 samples. Also require the model to quote the
  exact sentence span in the passage that justifies the answer, and reject
  if that span doesn't exist verbatim."

Usage: see build_rc_passage_1.py.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass

from qagen import llm_client

DRAFT_SYSTEM_PROMPT = """You write Reading Comprehension questions for the CAT (Common Admission \
Test) exam, based on a real passage you are given. You never invent facts not in the passage.

Respond with a single JSON object, no prose, no markdown fences:
{
  "question_type": "main_idea" | "detail" | "inference" | "tone" | "structure" | "vocab_in_context",
  "stem": "the question text",
  "options": [{"key": "A", "markdown": "..."}, {"key": "B", "markdown": "..."}, \
{"key": "C", "markdown": "..."}, {"key": "D", "markdown": "..."}],
  "correct_key": "A",
  "justifying_span": "the exact sentence or clause from the passage, copied VERBATIM \
(same words, same punctuation), that justifies the correct answer",
  "solution": "step-by-step explanation of why the correct option is right and the others are not"
}

The four options must be mutually exclusive and only one may be correct. Distractors should be \
plausible misreadings, not obviously wrong. justifying_span must be copied character-for-character \
from the passage — do not paraphrase it."""

ANSWER_SYSTEM_PROMPT = """You are answering a CAT Reading Comprehension question. You are given \
only the passage and the question — solve it independently. Respond with a single JSON object, \
no prose: {"answer": "A"}"""


@dataclass
class RcRejectReason:
    stage: str
    detail: str


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def span_exists_verbatim(passage: str, span: str) -> bool:
    """SPEC.md §6.3: 'reject if that span doesn't exist verbatim.' Normalises whitespace only
    (line-wrapped source text vs. a one-line LLM quote shouldn't fail on that alone) — no other
    fuzziness, since the whole point is the model can't paraphrase its way past this check."""
    if not span.strip():
        return False
    return _normalize(span) in _normalize(passage)


def answerability_check(passage: str, stem: str, options: list[dict], samples: int = 5) -> tuple[int, str | None]:
    """Returns (agreement_count, majority_answer). Each sample is an independent call — the model
    is never shown the claimed correct answer."""
    user = f"Passage:\n{passage}\n\nQuestion:\n{stem}\n\nOptions:\n" + "\n".join(
        f"{o['key']}. {o['markdown']}" for o in options
    )
    answers: list[str] = []
    for _ in range(samples):
        try:
            reply = llm_client.chat_json(ANSWER_SYSTEM_PROMPT, user, temperature=0.8, max_tokens=300)
            answer = str(reply.get("answer", "")).strip().upper()
            if answer in {o["key"] for o in options}:
                answers.append(answer)
        except llm_client.LLMError:
            continue
    if not answers:
        return 0, None
    counts = Counter(answers)
    majority_answer, majority_count = counts.most_common(1)[0]
    return majority_count, majority_answer


def generate_one_rc_question(
    passage: str, avoid_types: list[str], samples: int = 5
) -> tuple[dict | None, RcRejectReason | None]:
    user = (
        f"Passage:\n{passage}\n\n"
        f"Write one original RC question for this passage. "
        f"{'Avoid question types already used: ' + ', '.join(avoid_types) + '.' if avoid_types else ''}"
    )
    try:
        draft = llm_client.chat_json(DRAFT_SYSTEM_PROMPT, user, temperature=0.9, max_tokens=1200)
    except llm_client.LLMError as e:
        return None, RcRejectReason("draft", str(e))

    stem = draft.get("stem", "")
    options = draft.get("options")
    correct_key = draft.get("correct_key")
    span = draft.get("justifying_span", "")
    if not stem or not options or not correct_key:
        return None, RcRejectReason("draft", "malformed draft")

    if not span_exists_verbatim(passage, span):
        return None, RcRejectReason("span_check", f"justifying span not found verbatim: {span[:200]!r}")

    values = [o.get("markdown") for o in options]
    if len(set(values)) != len(values):
        return None, RcRejectReason("draft", "duplicate option text")

    agreement, majority = answerability_check(passage, stem, options, samples)
    if agreement < 4:
        return None, RcRejectReason("answerability", f"only {agreement}/{samples} independent solves agreed")
    if majority != correct_key:
        return None, RcRejectReason(
            "answerability", f"model majority answer {majority!r} disagrees with claimed correct_key {correct_key!r}"
        )

    return draft, None
