"""
Multi-template question generation (content pipeline v4).

## Why this exists

The Milestone-3 generators in `qagen/generators/*.py` produce one item *shape* per
micro-topic and vary only the numbers. Auditing the shipped bank showed the cost of
that: 398 deterministic questions but only 57 genuinely distinct question skeletons —
**1.27 templates per micro-topic**. Every one of the 12 shipped `qa.arith.percentages`
items was "price rises p1%, then falls p2%, find the net change." A learner who does
all 12 has practised one trick twelve times, not learned percentages. Raising
`item_count` against that structure manufactures volume without adding a single new
idea, which is exactly the kind of fake progress SPEC.md §6 exists to prevent.

This package inverts the ratio: each micro-topic gets many *archetypes* (the distinct
question forms CAT actually asks for that topic), and each archetype is instantiated
several times with different numbers and at different difficulty levels.

## Contract for a template function

    def t_something(rng: random.Random, difficulty: str) -> ItemSpec

- It must be pure with respect to `rng` — all randomness drawn from that generator, so
  a seeded run is reproducible and question ids (content-hashed in `harness.py`) stay
  stable across runs.
- `difficulty` is one of easy/medium/hard/very_hard and must genuinely change the item
  (uglier numbers, an extra step, a less-standard framing) — not just relabel it.
- **`answer_fn` must reach the answer by a different route than the stem's stated
  method** (simulation, exhaustive search, or sympy against the closed form). PROGRESS.md
  records the failure mode this guards against: an `answer_fn` that re-runs the same
  formula as the claim is a self-consistency check, not verification, and will happily
  confirm a wrong answer. `harness.verify_and_build` discards any item whose `answer_fn`
  disagrees with `claimed_value`.

Adding items is additive and safe: ids are `sha1(microtopic|stem|value)`, so previously
shipped questions keep their ids (nothing already referenced by a composed mock breaks)
and only genuinely new stems become new files.
"""

from __future__ import annotations

import random
from collections.abc import Callable

from qagen.harness import ItemSpec

from . import algebra, arith, numsys_geom, tsd_work

TemplateFn = Callable[[random.Random, str], ItemSpec]

# micro-topic id -> the archetypes CAT asks for that topic.
TEMPLATES: dict[str, list[TemplateFn]] = {}
TEMPLATES.update(arith.TEMPLATES)
TEMPLATES.update(tsd_work.TEMPLATES)
TEMPLATES.update(algebra.TEMPLATES)
TEMPLATES.update(numsys_geom.TEMPLATES)

# Difficulty ladder walked in parallel with the template cycle, so a topic's items
# spread across both axes instead of all its "hard" items landing on one archetype.
DIFF_CYCLE = ["easy", "easy", "medium", "medium", "medium", "hard", "hard", "very_hard"]

# A template can legitimately redraw the same numbers twice; retry before giving up so
# one unlucky collision doesn't silently shrink a topic's count.
_MAX_ATTEMPTS_PER_ITEM = 40


def generate_topic(microtopic_id: str, n: int) -> list[ItemSpec]:
    """Round-robins the topic's templates across the difficulty ladder until `n`
    distinct stems exist (or the retry budget is exhausted)."""
    templates = TEMPLATES.get(microtopic_id)
    if not templates:
        return []

    rng = random.Random(f"tmpl-v4-{microtopic_id}")
    specs: list[ItemSpec] = []
    seen_stems: set[str] = set()

    for i in range(n):
        template = templates[i % len(templates)]
        difficulty = DIFF_CYCLE[i % len(DIFF_CYCLE)]
        for _ in range(_MAX_ATTEMPTS_PER_ITEM):
            spec = template(rng, difficulty)
            if spec.stem not in seen_stems:
                seen_stems.add(spec.stem)
                specs.append(spec)
                break

    return specs


def covered_topics() -> list[str]:
    return sorted(TEMPLATES)


def template_count(microtopic_id: str) -> int:
    return len(TEMPLATES.get(microtopic_id, []))
