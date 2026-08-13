"""
Runs the multi-template question generators (qagen/templates/) and writes the
survivors to content/questions/.

Unlike `qagen.run` (the Milestone-3 single-shape generators), this walks each
micro-topic's *archetype list*, so a topic's items differ in kind and not only in
their numbers. See qagen/templates/__init__.py for the reasoning.

Every item still goes through `harness.verify_and_build`, which discards anything whose
independent `answer_fn` disagrees with the claimed answer — a template that produces a
wrong item is dropped, never repaired (SPEC.md §6.3).

Usage (from /pipeline):
    python -m qagen.run_templates [--topics id1,id2] [--per-topic N] [--dry-run]
"""

from __future__ import annotations

import argparse
from collections import Counter

from qagen import templates
from qagen.harness import VerificationError, verify_and_build, write_items
from qagen.syllabus_lookup import item_count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics", type=str, default=None, help="comma-separated micro-topic ids")
    parser.add_argument("--per-topic", type=int, default=None, help="override the target count per topic")
    parser.add_argument("--dry-run", action="store_true", help="verify everything but write nothing")
    args = parser.parse_args()

    topic_ids = args.topics.split(",") if args.topics else templates.covered_topics()

    accepted = []
    rejected: list[str] = []
    per_topic: Counter[str] = Counter()
    diff_mix: Counter[str] = Counter()

    for mt in topic_ids:
        if templates.template_count(mt) == 0:
            print(f"skip {mt}: no templates registered")
            continue
        target = args.per_topic if args.per_topic is not None else item_count(mt)
        specs = templates.generate_topic(mt, target)
        for spec in specs:
            try:
                question = verify_and_build(spec)
            except VerificationError as e:
                rejected.append(str(e))
                continue
            accepted.append(question)
            per_topic[mt] += 1
            diff_mix[spec.difficulty] += 1
        print(
            f"{mt}: {per_topic[mt]}/{target} verified "
            f"from {templates.template_count(mt)} templates"
        )

    if rejected:
        print(f"\n{len(rejected)} item(s) FAILED verification and were discarded:")
        for line in rejected:
            print(f"  {line}")

    print(f"\ndifficulty mix: {dict(sorted(diff_mix.items()))}")

    if args.dry_run:
        print(f"\n[dry run] {len(accepted)} items verified, nothing written.")
        return

    write_items(accepted)
    print(f"\nWrote {len(accepted)} verified questions to content/questions/")


if __name__ == "__main__":
    main()
