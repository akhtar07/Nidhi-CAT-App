"""
Lesson authoring framework — one lesson per micro-topic, teaching before practice.

## Why a framework instead of 86 hand-typed JSON files

SPEC.md §16 wants every micro-topic to have a lesson, and the app now routes every
topic through `/lesson/:id` before `/drill/:id`, so a missing lesson is a visible dead
end. Hand-writing 86 JSON documents invites two failure modes this repo has already hit
once each: arithmetic in a worked example that nobody re-checked, and markdown the
app's hand-rolled tokenizer cannot render.

So: lessons are declared as Python data, worked-example arithmetic is **computed and
interpolated** rather than typed (correct by construction), and `check_markdown` rejects
syntax the renderer does not support before anything reaches /content.

## House style — "explain it like she's new to this"

`intuition` is not optional decoration; it is the point. It must open with a concrete,
everyday analogy — something physical a person can picture — before any symbol appears.
`core` then says what is actually going on, still in plain words. Formulas come last,
in `formulas`, once the idea is already in place.

## Renderer constraints (app/src/components/question-player/markdownSegments.ts)

Supported: paragraphs, `## `/`### ` headings, `**bold**`, `$inline$`, `$$block$$`, images.
NOT supported, and actively checked against below:
  - pipe tables (`| a | b |`) — render as literal pipes
  - single-asterisk `*italic*` — renders as literal asterisks
  - `\\%`, `\\times` etc. outside a math span — render as literal backslashes
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from schemas import FormulaCard, Lesson, WorkedExample

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LESSONS_DIR = REPO_ROOT / "content" / "lessons"


@dataclass
class EX:
    """A worked example. Put computed values in via f-strings — never type arithmetic by hand."""
    stem: str
    solution: str
    alt: str | None = None


@dataclass
class FC:
    """A formula card. `title` is what the SRS deck shows on the front."""
    title: str
    body: str
    example: str | None = None


@dataclass
class LessonSpec:
    mt: str
    intuition: str
    core: str
    examples: list[EX] = field(default_factory=list)
    formulas: list[FC] = field(default_factory=list)
    traps: list[str] = field(default_factory=list)
    minutes: int = 5
    extra_sections: list[tuple[str, str]] = field(default_factory=list)


# LaTeX commands are fine inside $...$; loose backslashes outside one are not.
_MATH_SPAN = re.compile(r"\$\$.+?\$\$|\$[^$]+\$", re.S)
_PIPE_TABLE = re.compile(r"^\s*\|.*\|\s*$", re.M)
# A single '*' used as emphasis: not part of '**', not a literal escaped asterisk.
_LONE_ITALIC = re.compile(r"(?<!\*)\*(?!\*)[^*\n]+(?<!\*)\*(?!\*)")


def check_markdown(where: str, text: str) -> list[str]:
    """Returns human-readable problems with `text` for the app's tokenizer."""
    problems = []
    if _PIPE_TABLE.search(text):
        problems.append(f"{where}: contains a pipe table; the renderer has no table support")
    if _LONE_ITALIC.search(text):
        sample = _LONE_ITALIC.search(text).group(0)[:40]
        problems.append(f"{where}: single-asterisk italic {sample!r}; use **bold** instead")
    outside_math = _MATH_SPAN.sub(" ", text)
    stray = re.search(r"\\[a-zA-Z%]+", outside_math)
    if stray:
        problems.append(f"{where}: LaTeX {stray.group(0)!r} outside a $...$ span renders literally")
    return problems


def build_body(spec: LessonSpec) -> str:
    parts = [
        "## The idea in plain language",
        spec.intuition,
        "## What is actually going on",
        spec.core,
    ]
    for heading, body in spec.extra_sections:
        parts.append(f"## {heading}")
        parts.append(body)
    return "\n\n".join(parts)


def to_lesson(spec: LessonSpec) -> Lesson:
    body = build_body(spec)

    problems = check_markdown(f"{spec.mt} body", body)
    for i, ex in enumerate(spec.examples, 1):
        problems += check_markdown(f"{spec.mt} example {i} stem", ex.stem)
        problems += check_markdown(f"{spec.mt} example {i} solution", ex.solution)
        if ex.alt:
            problems += check_markdown(f"{spec.mt} example {i} alt", ex.alt)
    for i, fc in enumerate(spec.formulas, 1):
        problems += check_markdown(f"{spec.mt} formula {i}", fc.body)
        if fc.example:
            problems += check_markdown(f"{spec.mt} formula {i} example", fc.example)
    for i, trap in enumerate(spec.traps, 1):
        problems += check_markdown(f"{spec.mt} trap {i}", trap)
    if problems:
        raise ValueError("unrenderable markdown:\n  " + "\n  ".join(problems))

    return Lesson(
        id=spec.mt,
        microTopicId=spec.mt,
        bodyMarkdown=body,
        workedExamples=[
            WorkedExample(
                id=f"{spec.mt}.ex{i}",
                stemMarkdown=ex.stem,
                solutionMarkdown=ex.solution,
                altSolutionMarkdown=ex.alt,
            )
            for i, ex in enumerate(spec.examples, 1)
        ],
        formulaCards=[
            FormulaCard(
                id=f"{spec.mt}.fc{i}",
                microTopicId=spec.mt,
                title=fc.title,
                bodyMarkdown=fc.body,
                exampleMarkdown=fc.example,
            )
            for i, fc in enumerate(spec.formulas, 1)
        ],
        commonTraps=spec.traps,
        estReadMinutes=spec.minutes,
    )


def write_lessons(specs: list[LessonSpec]) -> int:
    LESSONS_DIR.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        lesson = to_lesson(spec)
        path = LESSONS_DIR / f"{spec.mt}.json"
        path.write_text(json.dumps(json.loads(lesson.model_dump_json()), indent=2) + "\n")
    return len(specs)
