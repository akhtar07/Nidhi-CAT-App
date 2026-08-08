from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SYLLABUS = json.loads((REPO_ROOT / "content" / "syllabus.json").read_text())
_BY_ID = {m["id"]: m for m in _SYLLABUS}

# Items-per-micro-topic, weighted by roiScore — matches the triage
# philosophy in SPEC.md §10.2: spend more generation effort on higher-ROI
# topics rather than flat coverage everywhere.
COUNT_BY_ROI = {5: 8, 4: 6, 3: 4, 2: 3, 1: 2}


def target_seconds(microtopic_id: str) -> int:
    return _BY_ID[microtopic_id]["targetSecPerQuestion"]


def item_count(microtopic_id: str) -> int:
    return COUNT_BY_ROI[_BY_ID[microtopic_id]["roiScore"]]
