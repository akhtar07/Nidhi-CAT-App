from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SYLLABUS = json.loads((REPO_ROOT / "content" / "syllabus.json").read_text())
_BY_ID = {m["id"]: m for m in _SYLLABUS}

# Items-per-micro-topic, weighted by roiScore — matches the triage
# philosophy in SPEC.md §10.2: spend more generation effort on higher-ROI
# topics rather than flat coverage everywhere. Floor raised to 15 across the
# board (was {5: 12, 4: 9, 3: 6, 2: 5, 1: 3}) because SPEC.md §16's
# acceptance bar is literally "≥15 questions per micro-topic" — the old
# table capped out at 12 even for roiScore 5, so no topic could ever clear
# the bar no matter how many generation passes ran. Every roiScore band
# still gets a floor of 15/questions minimum for the "or coverage: partial"
# clause; higher ROI topics get proportionally more on top of that floor.
COUNT_BY_ROI = {5: 24, 4: 20, 3: 17, 2: 15, 1: 15}


def target_seconds(microtopic_id: str) -> int:
    return _BY_ID[microtopic_id]["targetSecPerQuestion"]


def item_count(microtopic_id: str) -> int:
    return COUNT_BY_ROI[_BY_ID[microtopic_id]["roiScore"]]


def topic_name(microtopic_id: str) -> str:
    return _BY_ID[microtopic_id]["name"]


def topic_ids(section: str | None = None) -> list[str]:
    if section is None:
        return list(_BY_ID.keys())
    return [mt_id for mt_id, mt in _BY_ID.items() if mt["section"] == section]
