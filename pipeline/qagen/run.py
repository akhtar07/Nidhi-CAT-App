"""
Run every QA generator, verify every item, and write the survivors to
content/questions/<id>.json.

Usage (from /pipeline): python -m qagen.run
"""

from __future__ import annotations

from qagen.generators import algebra, arithmetic, geometry, modern, numsys
from qagen.harness import run_generators, write_items

ALL_GENERATORS = (
    arithmetic.GENERATORS
    + algebra.GENERATORS
    + geometry.GENERATORS
    + numsys.GENERATORS
    + modern.GENERATORS
)


def main() -> None:
    items = run_generators(ALL_GENERATORS)
    write_items(items)
    print(f"Wrote {len(items)} questions to content/questions/")

    by_topic: dict[str, int] = {}
    for q in items:
        by_topic[q.microTopicIds[0]] = by_topic.get(q.microTopicIds[0], 0) + 1
    for topic, count in sorted(by_topic.items()):
        print(f"  {topic}: {count}")


if __name__ == "__main__":
    main()
