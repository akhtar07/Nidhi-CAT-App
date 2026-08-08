"""
Single source of truth for Ascent's shipped content types (SPEC.md §5.1).

These pydantic v2 models are never hand-duplicated elsewhere. JSON Schemas
are generated from them into /content/schemas/*.json, and TypeScript types
are generated from those JSON Schemas into /app/src/types/content.ts (see
generate_json_schemas.py and app/scripts/generate-types.mjs). See
PROGRESS.md for the full generation/drift-check flow.

Learner-state types (SPEC.md §5.2 — Attempt, MasteryState, PlanDay,
MockResult, Settings) are intentionally NOT modelled here: they never need
to be produced or validated by this offline pipeline, and are TypeScript-
native from Milestone 2 onward.

Two deviations from SPEC.md §5.1, recorded here and in PROGRESS.md:
- `MicroTopic.formulaCardId` (present in §3's prose, absent from §5.1's
  canonical TS interface) is omitted; `FormulaCard.microTopicId` covers the
  same relationship in the other direction.
- `WorkedExample`, `FormulaCard`, and `VerificationRecord` are referenced by
  §5.1 but never defined anywhere in SPEC.md. Their shapes below were
  proposed and confirmed with the project owner before implementation.
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Section = Literal["VARC", "DILR", "QA"]
Difficulty = Literal["easy", "medium", "hard", "very_hard"]


class ContentModel(BaseModel):
    """Base for all shipped-content types: unknown fields are a hard error."""

    model_config = ConfigDict(extra="forbid")


# ---------------------------------------------------------------------------
# Syllabus
# ---------------------------------------------------------------------------


class MicroTopic(ContentModel):
    id: str = Field(
        min_length=1,
        description="Stable slug id, e.g. 'qa.arith.tsd.boats-streams'. Never an array index.",
    )
    name: str = Field(min_length=1)
    section: Section
    topicId: str = Field(min_length=1)
    prerequisites: list[str] = Field(default_factory=list)
    catFrequency: Literal["high", "medium", "low", "rare"]
    roiScore: Literal[1, 2, 3, 4, 5]
    estLearnMinutes: Annotated[int, Field(gt=0)]
    targetSecPerQuestion: Annotated[int, Field(gt=0)]


# ---------------------------------------------------------------------------
# Lessons
# ---------------------------------------------------------------------------


class WorkedExample(ContentModel):
    id: str = Field(min_length=1)
    stemMarkdown: str = Field(min_length=1)
    solutionMarkdown: str = Field(min_length=1, description="Step-by-step. Mandatory, never empty.")
    altSolutionMarkdown: str | None = Field(default=None, description="The 'smart approach', per SPEC.md §13.")


class FormulaCard(ContentModel):
    id: str = Field(min_length=1, description="Stable id — the SRS deck (§8.4) keys off this.")
    microTopicId: str = Field(min_length=1)
    title: str = Field(min_length=1)
    bodyMarkdown: str = Field(min_length=1, description="The formula/rule itself, KaTeX-enabled.")
    exampleMarkdown: str | None = None


class Lesson(ContentModel):
    id: str = Field(min_length=1)
    microTopicId: str = Field(min_length=1)
    bodyMarkdown: str = Field(min_length=1)
    workedExamples: list[WorkedExample] = Field(default_factory=list)
    formulaCards: list[FormulaCard] = Field(default_factory=list)
    commonTraps: list[str] = Field(default_factory=list)
    estReadMinutes: Annotated[int, Field(gt=0)]


# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------


class QuestionOption(ContentModel):
    key: str = Field(min_length=1)
    markdown: str = Field(min_length=1)


class VerificationRecord(ContentModel):
    """Captures which checks in SPEC.md §6.3/§6.4 an item passed."""

    method: Literal[
        "sympy_verified",
        "self_consistency",
        "human_reviewed",
        "answerability_pass",
        "pyq_official",
    ]
    verifiedAt: str = Field(description="ISO 8601 timestamp.")
    selfConsistencyAgreement: Annotated[int, Field(ge=0, le=5)] | None = Field(
        default=None, description="e.g. 4 of 5 sampled solutions agreed, per §6.3."
    )
    distractorAuditPassed: bool | None = Field(default=None, description="§6.3 distractor audit.")
    dedupChecked: bool | None = Field(default=None, description="§6.3 embedding-similarity dedup.")
    reviewerNote: str | None = Field(default=None, description="Human review notes, §6.2 step 6.")


class Question(ContentModel):
    id: str = Field(min_length=1, description="Stable, content-hash based.")
    microTopicIds: list[str] = Field(min_length=1)
    section: Section
    format: Literal["mcq", "tita"]
    stemMarkdown: str = Field(min_length=1)
    options: list[QuestionOption] | None = None
    correctKey: str | None = None
    correctValue: str | float | None = None
    titaTolerance: float | None = None
    difficulty: Difficulty
    eloRating: float = Field(description="Item difficulty, seeded from the difficulty label (§6.4).")
    solutionMarkdown: str = Field(min_length=1, description="Step-by-step. MANDATORY, never empty.")
    altSolutionMarkdown: str | None = None
    targetSeconds: Annotated[int, Field(gt=0)]
    source: Literal["official_pyq", "generated", "authored"]
    sourceRef: str | None = Field(default=None, description="e.g. 'CAT 2023 Slot 2 Q14'.")
    verification: VerificationRecord
    tags: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _check_format_specific_fields(self) -> "Question":
        if self.format == "mcq":
            if not self.options:
                raise ValueError("mcq questions must have at least one option")
            if not self.correctKey:
                raise ValueError("mcq questions must have correctKey")
            if self.correctKey not in {opt.key for opt in self.options}:
                raise ValueError("correctKey must match one of options[].key")
            if self.correctValue is not None:
                raise ValueError("mcq questions must not set correctValue (tita-only field)")
        elif self.format == "tita":
            if self.correctValue is None:
                raise ValueError("tita questions must have correctValue")
            if self.options is not None or self.correctKey is not None:
                raise ValueError("tita questions must not set options/correctKey (mcq-only fields)")
        return self


# ---------------------------------------------------------------------------
# Passage / set (RC and DILR)
# ---------------------------------------------------------------------------


class PassageAsset(ContentModel):
    type: Literal["table", "chart"]
    spec: dict = Field(description="Render charts from data, not images, per SPEC.md §5.1.")


class PassageSet(ContentModel):
    id: str = Field(min_length=1)
    section: Literal["VARC", "DILR"]
    kind: Literal["rc_passage", "di_set", "lr_set"]
    bodyMarkdown: str = Field(min_length=1)
    assets: list[PassageAsset] | None = None
    questionIds: list[str] = Field(default_factory=list)
    genre: str | None = None
    wordCount: int | None = Field(default=None, gt=0)
    targetMinutes: float = Field(gt=0)
    licence: str = Field(min_length=1, description="MANDATORY. See SPEC.md §6. Blank fails CI.")
    sourceUrl: str | None = None


# Root content types, keyed by the schema filename generate_json_schemas.py
# writes them under (/content/schemas/<key>.schema.json).
CONTENT_MODELS: dict[str, type[ContentModel]] = {
    "micro-topic": MicroTopic,
    "lesson": Lesson,
    "question": Question,
    "passage-set": PassageSet,
}
