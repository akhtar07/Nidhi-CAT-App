"""
SPEC.md §2: hard facts about CAT 2026, stored in one place so they can be
corrected without hunting through components. Hand-authored from SPEC.md's
own text, not scraped or inferred.

Run (from /pipeline, cat-pipeline conda env): python build_exam_meta.py
"""

from __future__ import annotations

import json
from pathlib import Path

from schemas import ExamMeta

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "content" / "exam-meta.json"


def build() -> ExamMeta:
    return ExamMeta(
        examDate="2026-11-29",
        registrationOpensDate="2026-08-03",
        registrationClosesDate="2026-09-15",
        slots=["08:30-10:30", "12:30-14:30", "16:30-18:30"],
        sectionOrder=["VARC", "DILR", "QA"],
        totalMinutes=120,
        minutesPerSection=40,
        questionCount={"VARC": 24, "DILR": 20, "QA": 22},
        maxScore=204,
    )


def main() -> None:
    meta = build()
    OUT_PATH.write_text(json.dumps(json.loads(meta.model_dump_json()), indent=2) + "\n")
    print(f"Wrote {OUT_PATH.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
