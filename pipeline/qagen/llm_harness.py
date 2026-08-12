"""
LLM generation + verification harness for QA items (SPEC.md §6.3, Tier 3).
Extends the deterministic-generator harness (qagen/harness.py) with an
actual local-LLM path for item variety the hand-written parametrized
generators can't produce, while keeping the same non-negotiable rule:
every claimed answer is independently recomputed by code and must match,
or the item is discarded — never repaired.

Pipeline per candidate item:
  1. Draft: one LLM call emits stem + options/value + solution + a
     self-contained verifier program (sandbox.py).
  2. SymPy/arithmetic verification: run the program, require its output to
     equal the claimed value.
  3. Self-consistency: 5 independent "solve this" calls at temperature 0.8
     (given only the stem/options, never the claimed answer); require >=4
     to agree with the verified value.
  4. Distractor audit (mcq only): a separate call checks no distractor is
     also correct, options are mutually exclusive, and the answer isn't
     guessable from option structure alone.
  5. Dedup: embedding cosine similarity against the whole existing bank
     (>0.92 = duplicate) plus a normalised-numbers hash for trivial
     re-skins (same structure, different numbers swapped in).

Usage: see run_llm.py.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from qagen import llm_client
from qagen.harness import DIFFICULTY_ELO, QUESTIONS_DIR, VERIFIED_AT
from qagen.sandbox import run_verifier
from schemas import Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

DRAFT_SYSTEM_PROMPT = """You write original CAT (Common Admission Test) Quantitative Aptitude \
practice questions. You never copy or paraphrase questions from coaching materials \
or textbooks — every item must be your own original composition.

Respond with a single JSON object, no prose, no markdown fences, matching exactly:
{
  "format": "mcq" or "tita",
  "stem": "the question text, KaTeX math using $...$ for inline and $$...$$ for block",
  "options": [{"key": "A", "markdown": "..."}, ...] (4 options, mcq only, omit for tita),
  "correct_key": "A" (mcq only, omit for tita),
  "correct_value": "the exact numeric or short string answer" (tita only, omit for mcq),
  "verification_target": "the same value as correct_value/the correct option's value, \
as a plain number or short string with NO formatting (no %, no commas, no units) \
so it can be parsed and compared programmatically",
  "solution": "step-by-step solution in markdown, KaTeX for math",
  "alt_solution": "a faster/smarter approach, or null",
  "verifier_code": "a self-contained Python function `def compute():` that independently \
recomputes the answer from the stem's given values using only math/sympy/fractions/\
itertools/decimal/statistics — must return a value equal to verification_target",
  "tags": ["short-tag-1", "short-tag-2"]
}

The verifier_code must derive the answer through actual computation, not just \
`return <the answer>` — it must reflect independent arithmetic from the stem's given \
numbers, using a method that could catch a mistake in your own claimed answer."""

SOLVE_SYSTEM_PROMPT = """You are solving a CAT Quantitative Aptitude question. \
Work through it and respond with a single JSON object, no prose:
{"final_answer": "just the final numeric/short answer, no units or formatting"}"""

DISTRACTOR_AUDIT_SYSTEM_PROMPT = """You are auditing a multiple-choice question for \
quality issues. Respond with a single JSON object, no prose:
{
  "ok": true or false,
  "issues": ["list of any problems found — empty if ok"]
}
Flag: any distractor that could also be considered correct, options that aren't \
mutually exclusive, inconsistent units across options, or an answer that's guessable \
purely from option structure (e.g. it's the only option with a different order of \
magnitude, or the only one that's a round number)."""


@dataclass
class RejectReason:
    stage: str
    detail: str


def _draft_user_prompt(microtopic_id: str, topic_name: str, difficulty: str, avoid_stems: list[str]) -> str:
    avoid = ""
    if avoid_stems:
        sample = "\n".join(f"- {s}" for s in avoid_stems[:8])
        avoid = f"\n\nDo not repeat these already-used question framings (write something structurally different):\n{sample}"
    return (
        f"Topic: {topic_name} (id: {microtopic_id})\n"
        f"Target difficulty: {difficulty}\n"
        f"Write one original CAT QA practice question for this exact topic at this "
        f"difficulty level.{avoid}"
    )


def _normalized_number_hash(stem: str) -> str:
    """Replaces every number in the stem with a placeholder before hashing,
    so a trivial re-skin (same structure, different numbers) collides with
    the original — catches what embedding similarity alone might miss for
    very short stems."""
    normalized = re.sub(r"-?\d+(\.\d+)?", "#", stem.lower())
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return hashlib.sha1(normalized.encode()).hexdigest()


def _values_agree(a: object, b: object, tol: float = 0.05) -> bool:
    try:
        fa, fb = float(a), float(b)  # type: ignore[arg-type]
        if fb == 0:
            return abs(fa - fb) <= tol
        return abs(fa - fb) / max(abs(fb), 1e-9) <= tol
    except (TypeError, ValueError):
        return str(a).strip().lower() == str(b).strip().lower()


def self_consistency_check(
    stem: str, options: list[dict] | None, verified_value: object, samples: int = 5, label: str = ""
) -> int:
    """Independently asks the model to solve the item `samples` times
    (given only stem/options, never the claimed answer) and counts how many
    agree with the already-sympy-verified value. Returns the agreement
    count.

    Prints one line per sample: a single self-consistency call can legitimately
    take minutes under a loaded local model, and a batch run's only per-item
    log line used to come after all 5 samples (plus draft + audit) finished —
    so a slow-but-alive attempt was indistinguishable from a hung one for up
    to ~35 minutes. See PROGRESS.md's QA-batch-hang writeup."""
    user = f"Question:\n{stem}"
    if options:
        user += "\n\nOptions:\n" + "\n".join(f"{o['key']}. {o['markdown']}" for o in options)
    agree = 0
    for i in range(samples):
        try:
            reply = llm_client.chat_json(SOLVE_SYSTEM_PROMPT, user, temperature=0.8, max_tokens=1024)
            ok = _values_agree(reply.get("final_answer"), verified_value)
            if ok:
                agree += 1
            print(f"    {label}self-consistency sample {i + 1}/{samples}: {'agree' if ok else 'disagree'}", flush=True)
        except llm_client.LLMError as e:
            print(f"    {label}self-consistency sample {i + 1}/{samples}: call failed ({e})", flush=True)
            continue
    return agree


def distractor_audit(stem: str, options: list[dict], correct_key: str) -> tuple[bool, list[str]]:
    user = (
        f"Question:\n{stem}\n\nOptions:\n"
        + "\n".join(f"{o['key']}. {o['markdown']}" for o in options)
        + f"\n\nClaimed correct answer: {correct_key}"
    )
    try:
        reply = llm_client.chat_json(DISTRACTOR_AUDIT_SYSTEM_PROMPT, user, temperature=0.2, max_tokens=512)
    except llm_client.LLMError as e:
        return False, [f"audit call failed: {e}"]
    return bool(reply.get("ok")), reply.get("issues", [])


class DedupIndex:
    """Embedding + normalised-hash dedup against the existing bank (SPEC.md
    §6.3 step 6). Loads the whole committed question bank once, embeds all
    stems, and checks new candidates against it (plus items accepted so far
    in this run, so a batch can't duplicate itself)."""

    def __init__(self, threshold: float = 0.92):
        from sentence_transformers import SentenceTransformer

        self.threshold = threshold
        self.model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")
        self.stems: list[str] = []
        self.hashes: set[str] = set()
        self.embeddings = None

        existing_stems = []
        for path in QUESTIONS_DIR.glob("*.json"):
            data = json.loads(path.read_text())
            stem = data.get("stemMarkdown", "")
            existing_stems.append(stem)
            self.hashes.add(_normalized_number_hash(stem))

        if existing_stems:
            import numpy as np

            self.stems = existing_stems
            self.embeddings = self.model.encode(existing_stems, convert_to_numpy=True, normalize_embeddings=True)
        else:
            import numpy as np

            self.embeddings = np.zeros((0, 384), dtype="float32")

    def is_duplicate(self, stem: str) -> bool:
        import numpy as np

        if _normalized_number_hash(stem) in self.hashes:
            return True
        if len(self.stems) == 0:
            return False
        vec = self.model.encode([stem], convert_to_numpy=True, normalize_embeddings=True)
        sims = self.embeddings @ vec[0]
        return bool(np.max(sims) >= self.threshold)

    def add(self, stem: str) -> None:
        import numpy as np

        self.hashes.add(_normalized_number_hash(stem))
        vec = self.model.encode([stem], convert_to_numpy=True, normalize_embeddings=True)
        self.embeddings = np.vstack([self.embeddings, vec]) if len(self.stems) else vec
        self.stems.append(stem)


def generate_one(
    microtopic_id: str,
    topic_name: str,
    difficulty: str,
    target_seconds: int,
    dedup: DedupIndex,
    recent_stems: list[str],
) -> tuple[Question | None, RejectReason | None]:
    label = f"[{microtopic_id}/{difficulty}] "
    print(f"  {label}draft...", flush=True)
    try:
        draft = llm_client.chat_json(
            DRAFT_SYSTEM_PROMPT,
            _draft_user_prompt(microtopic_id, topic_name, difficulty, recent_stems),
            temperature=0.9,
            max_tokens=2048,
        )
    except llm_client.LLMError as e:
        print(f"  {label}draft failed: {e}", flush=True)
        return None, RejectReason("draft", str(e))

    fmt = draft.get("format")
    stem = draft.get("stem", "")
    if fmt not in ("mcq", "tita") or not stem:
        return None, RejectReason("draft", "malformed draft (missing format/stem)")
    print(f"  {label}draft ok ({fmt}): {stem[:70]!r}...", flush=True)

    if dedup.is_duplicate(stem):
        return None, RejectReason("dedup", "duplicate of existing bank item")

    print(f"  {label}sympy verify...", flush=True)
    verifier_code = draft.get("verifier_code", "")
    ok, computed, err = run_verifier(verifier_code)
    if not ok:
        return None, RejectReason("sympy_verify", err)

    target = draft.get("verification_target")
    if not _values_agree(computed, target):
        return None, RejectReason("sympy_verify", f"program returned {computed!r}, claimed target {target!r}")
    print(f"  {label}sympy verify ok (target={target!r})", flush=True)

    options = draft.get("options")
    correct_key = draft.get("correct_key")
    if fmt == "mcq":
        if not options or not correct_key:
            return None, RejectReason("draft", "mcq missing options/correct_key")
        values = [o.get("markdown") for o in options]
        if len(set(values)) != len(values):
            return None, RejectReason("distractor_audit", "duplicate option text")
        print(f"  {label}distractor audit...", flush=True)
        audit_ok, issues = distractor_audit(stem, options, correct_key)
        if not audit_ok:
            return None, RejectReason("distractor_audit", "; ".join(issues) or "audit flagged issues")
        print(f"  {label}distractor audit ok", flush=True)

    print(f"  {label}self-consistency (5 samples)...", flush=True)
    agreement = self_consistency_check(stem, options, target, samples=5, label=label)
    if agreement < 4:
        return None, RejectReason("self_consistency", f"only {agreement}/5 independent solves agreed")

    content_hash = hashlib.sha1((microtopic_id + "|" + stem + "|" + str(target)).encode()).hexdigest()[:10]
    qid = f"{microtopic_id}.llm-{content_hash}"

    verification = VerificationRecord(
        method="sympy_verified",
        verifiedAt=VERIFIED_AT,
        selfConsistencyAgreement=agreement,
        distractorAuditPassed=True if fmt == "mcq" else None,
        dedupChecked=True,
        reviewerNote=None,
    )

    kwargs = dict(
        id=qid,
        microTopicIds=[microtopic_id],
        section="QA",
        format=fmt,
        stemMarkdown=stem,
        difficulty=difficulty,
        eloRating=float(DIFFICULTY_ELO[difficulty]),
        solutionMarkdown=draft.get("solution", ""),
        altSolutionMarkdown=draft.get("alt_solution"),
        targetSeconds=target_seconds,
        source="generated",
        sourceRef=None,
        verification=verification,
        tags=draft.get("tags", []),
    )
    if fmt == "mcq":
        kwargs["options"] = [QuestionOption(key=o["key"], markdown=o["markdown"]) for o in options]
        kwargs["correctKey"] = correct_key
    else:
        cv = draft.get("correct_value", target)
        kwargs["correctValue"] = cv
        kwargs["titaTolerance"] = abs(float(target)) * 0.01 if _is_number(target) else 0.0

    try:
        question = Question(**kwargs)
    except Exception as e:  # pydantic ValidationError et al.
        return None, RejectReason("schema", str(e))

    dedup.add(stem)
    return question, None


def _is_number(v: object) -> bool:
    try:
        float(v)  # type: ignore[arg-type]
        return True
    except (TypeError, ValueError):
        return False
