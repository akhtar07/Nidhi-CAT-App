"""
Builds every declared lesson into content/lessons/.

Reports which micro-topics still have no lesson, so the gap against SPEC.md §16 is a
number on screen rather than something to be discovered later in the app as a dead end.

Usage (from /pipeline): python -m lessons.build_lessons
"""

from __future__ import annotations

import json
from pathlib import Path

from lessons import LESSONS_DIR, write_lessons
from lessons import qa_algebra, qa_arith, qa_geometry, qa_numsys_modern, dilr, varc

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

ALL_SPECS = (
    qa_arith.SPECS
    + qa_algebra.SPECS
    + qa_numsys_modern.SPECS
    + qa_geometry.SPECS
    + dilr.SPECS
    + varc.SPECS
)


def main() -> None:
    ids = [s.mt for s in ALL_SPECS]
    duplicates = {i for i in ids if ids.count(i) > 1}
    if duplicates:
        raise SystemExit(f"duplicate lesson specs for: {sorted(duplicates)}")

    syllabus = json.loads((REPO_ROOT / "content" / "syllabus.json").read_text())
    valid = {t["id"] for t in syllabus}
    unknown = [i for i in ids if i not in valid]
    if unknown:
        raise SystemExit(f"lesson specs reference unknown micro-topics: {unknown}")

    written = write_lessons(ALL_SPECS)
    print(f"Wrote {written} lessons.")

    have = {p.stem for p in LESSONS_DIR.glob("*.json")}
    missing = sorted(t["id"] for t in syllabus if t["id"] not in have)
    print(f"Lessons on disk: {len(have)}/{len(syllabus)} micro-topics")
    if missing:
        print(f"Still missing ({len(missing)}):")
        for m in missing:
            print(f"  {m}")
    else:
        print("Every micro-topic in the syllabus has a lesson.")


if __name__ == "__main__":
    main()
