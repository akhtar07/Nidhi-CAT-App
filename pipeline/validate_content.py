"""
Validate everything under /content against the schemas in schemas.py.

This is the "schema-validate-content" CI job SPEC.md §7 calls for. It is
separate from generate_json_schemas.py --check (which catches drift between
schemas.py and the committed *.schema.json files) — this script validates
the actual content *data* files.

Checks:
  - content/syllabus.json: every entry validates as a MicroTopic, ids are
    unique, every `prerequisites` entry references a real micro-topic id,
    and the prerequisite graph has no cycles.
  - content/lessons/*.json, content/questions/*.json,
    content/passage-sets/*.json (if present — none exist yet as of
    Milestone 1, and that's fine, missing content is not an error): each
    validates against its schema, and every `microTopicId` /
    `microTopicIds` reference resolves to a real syllabus entry ("orphan
    microTopicId -> red build", SPEC.md §7).

Usage: python validate_content.py
Exits non-zero with all errors printed if anything fails.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from pydantic import ValidationError

from schemas import ExamMeta, Lesson, MicroTopic, PassageSet, Question

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content"


def load_syllabus(errors: list[str]) -> dict[str, MicroTopic]:
    path = CONTENT_DIR / "syllabus.json"
    if not path.exists():
        errors.append(f"missing required file: {path.relative_to(REPO_ROOT)}")
        return {}

    raw = json.loads(path.read_text())
    if not isinstance(raw, list) or not raw:
        errors.append("content/syllabus.json must be a non-empty array")
        return {}

    by_id: dict[str, MicroTopic] = {}
    for i, entry in enumerate(raw):
        try:
            mt = MicroTopic(**entry)
        except ValidationError as e:
            errors.append(f"content/syllabus.json[{i}]: {e}")
            continue
        if mt.id in by_id:
            errors.append(f"content/syllabus.json: duplicate micro-topic id {mt.id!r}")
        by_id[mt.id] = mt

    for mt in by_id.values():
        for p in mt.prerequisites:
            if p not in by_id:
                errors.append(
                    f"content/syllabus.json: {mt.id!r} has unknown prerequisite {p!r}"
                )

    if not _acyclic(by_id):
        errors.append("content/syllabus.json: prerequisite graph has a cycle")

    return by_id


def _acyclic(by_id: dict[str, MicroTopic]) -> bool:
    indeg = {mid: 0 for mid in by_id}
    adj: dict[str, list[str]] = {mid: [] for mid in by_id}
    for mt in by_id.values():
        for p in mt.prerequisites:
            if p in by_id:
                adj[p].append(mt.id)
                indeg[mt.id] += 1
    queue = [mid for mid, d in indeg.items() if d == 0]
    seen = 0
    while queue:
        n = queue.pop()
        seen += 1
        for m in adj[n]:
            indeg[m] -= 1
            if indeg[m] == 0:
                queue.append(m)
    return seen == len(by_id)


def validate_dir(
    dirname: str,
    model: type,
    errors: list[str],
    known_micro_topic_ids: dict[str, MicroTopic],
    microtopic_field: str | None,
) -> int:
    """Validates every *.json file in content/<dirname>/, if it exists.

    microtopic_field: name of the field holding micro-topic id(s) to check
    against known_micro_topic_ids, or None if this model has no such field
    (e.g. PassageSet, which references questions, not micro-topics).
    """
    d = CONTENT_DIR / dirname
    if not d.exists():
        return 0

    count = 0
    for path in sorted(d.glob("*.json")):
        raw = json.loads(path.read_text())
        rel = path.relative_to(REPO_ROOT)
        try:
            item = model(**raw)
        except ValidationError as e:
            errors.append(f"{rel}: {e}")
            continue
        count += 1

        if microtopic_field is None:
            continue

        ids = getattr(item, microtopic_field)
        ids = ids if isinstance(ids, list) else [ids]
        for mtid in ids:
            if mtid not in known_micro_topic_ids:
                errors.append(f"{rel}: orphan microTopicId {mtid!r} (not in syllabus.json)")

    return count


def main() -> int:
    errors: list[str] = []

    by_id = load_syllabus(errors)
    lesson_count = validate_dir("lessons", Lesson, errors, by_id, "microTopicId")
    question_count = validate_dir("questions", Question, errors, by_id, "microTopicIds")
    validate_dir("passage-sets", PassageSet, errors, by_id, None)

    exam_meta_path = CONTENT_DIR / "exam-meta.json"
    if exam_meta_path.exists():
        try:
            ExamMeta(**json.loads(exam_meta_path.read_text()))
        except ValidationError as e:
            errors.append(f"content/exam-meta.json: {e}")

    if errors:
        print(f"content validation FAILED — {len(errors)} error(s):\n")
        for e in errors:
            print(f"  - {e}")
        return 1

    print("content validation OK")
    print(f"  syllabus.json: {len(by_id)} micro-topics")
    print(f"  lessons: {lesson_count}")
    print(f"  questions: {question_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
