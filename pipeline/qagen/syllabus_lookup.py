from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SYLLABUS = json.loads((REPO_ROOT / "content" / "syllabus.json").read_text())
_BY_ID = {m["id"]: m for m in _SYLLABUS}

# Items-per-micro-topic, weighted by roiScore — matches the triage
# philosophy in SPEC.md §10.2: spend more generation effort on higher-ROI
# topics rather than flat coverage everywhere. Bumped ~50% for the bank-wide
# scale-up (was {5: 8, 4: 6, 3: 4, 2: 3, 1: 2}) — the project owner wants
# "a lot of questions, topic-wise" for practice, beyond the original
# ≥200-item Milestone-3 floor.
COUNT_BY_ROI = {5: 12, 4: 9, 3: 6, 2: 5, 1: 3}

# Seven lowest-roiScore topics PROGRESS.md flagged as stuck at 2-3 items
# each (too few for DIFF_CYCLE in generators/*.py to reach hard/very_hard —
# that needs an item count of >= 6/8 respectively). Their roiScore-based
# count would still only be 3 or 5 after the bump above, so they get an
# explicit floor here instead: their generators were widened (see
# generators/{arithmetic,algebra,geometry,modern,numsys}.py) to support it.
MIN_COUNT_OVERRIDE = {
    "qa.arith.tsd-races": 10,
    "qa.arith.time-work-chain-rule": 10,
    "qa.numsys.base-systems": 10,
    "qa.algebra.maxima-minima": 10,
    "qa.geometry.trigonometry": 10,
    "qa.modern.binomial-theorem": 10,
    "qa.modern.series-sequences-hybrids": 10,
}


def target_seconds(microtopic_id: str) -> int:
    return _BY_ID[microtopic_id]["targetSecPerQuestion"]


def item_count(microtopic_id: str) -> int:
    base = COUNT_BY_ROI[_BY_ID[microtopic_id]["roiScore"]]
    return max(base, MIN_COUNT_OVERRIDE.get(microtopic_id, 0))


def topic_name(microtopic_id: str) -> str:
    return _BY_ID[microtopic_id]["name"]


def topic_ids(section: str | None = None) -> list[str]:
    if section is None:
        return list(_BY_ID.keys())
    return [mt_id for mt_id, mt in _BY_ID.items() if mt["section"] == section]
