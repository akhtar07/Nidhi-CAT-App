"""
Milestone 7 (SPEC.md §15): scale the QA bank via LLM generation +
verification (qagen/llm_harness.py) on top of the deterministic generators
from Milestone 3. Requires a vLLM server already running — see
pipeline/README.md / PROGRESS.md for the launch command.

Usage (from /pipeline, cat-llm conda env):
    python -m qagen.run_llm [--topics id1,id2] [--per-topic N] [--attempts-per-item N]
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from qagen import llm_client
from qagen.harness import QUESTIONS_DIR, write_items
from qagen.llm_harness import DedupIndex, generate_one
from qagen.syllabus_lookup import item_count, target_seconds, topic_ids, topic_name

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

DIFF_CYCLE = ["easy", "easy", "medium", "medium", "hard", "very_hard"]

# LLM generation targets QA micro-topics broadly; DILR/VARC need different
# pipelines per SPEC.md §6.3 (programmatic data-first for DILR, real source
# text for RC) and are out of scope for this pass — see PROGRESS.md.
QA_TOPIC_IDS = topic_ids(section="QA")


def _existing_counts() -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for path in QUESTIONS_DIR.glob("*.json"):
        data = json.loads(path.read_text())
        for mt_id in data.get("microTopicIds", []):
            counts[mt_id] += 1
    return counts


def generate_for_topic(
    microtopic_id: str, n: int, dedup: DedupIndex, attempts_per_item: int
) -> tuple[list, list[str]]:
    name = topic_name(microtopic_id)
    tsec = target_seconds(microtopic_id)
    accepted = []
    reject_log = []
    recent_stems: list[str] = []
    for i in range(n):
        difficulty = DIFF_CYCLE[i % len(DIFF_CYCLE)]
        item = None
        for attempt in range(attempts_per_item):
            # A multi-hour run must not die on one item's unexpected
            # failure — this crashed the whole batch once already on an
            # uncaught network timeout (now fixed in llm_client.py, but
            # this is the backstop for whatever's next). Caught per-item,
            # not per-topic, so everything accepted so far in this topic
            # is still returned to the caller and written to disk.
            try:
                item, reason = generate_one(microtopic_id, name, difficulty, tsec, dedup, recent_stems)
            except Exception as e:
                reject_log.append(f"[{microtopic_id}] attempt {attempt + 1}: unexpected error - {e}")
                item = None
                continue
            if item is not None:
                break
            reject_log.append(f"[{microtopic_id}] attempt {attempt + 1}: {reason.stage} - {reason.detail}")
        if item is not None:
            accepted.append(item)
            recent_stems.append(item.stemMarkdown)
    return accepted, reject_log


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics", type=str, default=None, help="comma-separated micro-topic ids")
    parser.add_argument("--per-topic", type=int, default=None, help="override item count per topic")
    parser.add_argument("--attempts-per-item", type=int, default=3)
    parser.add_argument("--shortfall-only", action="store_true", help="only generate up to syllabus target count")
    args = parser.parse_args()

    if not llm_client.server_is_up():
        print(f"ERROR: no vLLM server reachable at {llm_client.VLLM_BASE_URL}. Start one first.", file=sys.stderr)
        sys.exit(1)

    topics = args.topics.split(",") if args.topics else QA_TOPIC_IDS
    existing = _existing_counts()

    print("Loading dedup index (embedding the existing bank)...")
    dedup = DedupIndex()
    print(f"Dedup index ready: {len(dedup.stems)} existing items loaded.\n")

    total_accepted = 0
    total_rejected = 0
    all_ids = set(topic_ids())
    for mt_id in topics:
        if mt_id not in all_ids:
            print(f"skip: unknown micro-topic id {mt_id}")
            continue
        target = args.per_topic if args.per_topic is not None else item_count(mt_id)
        have = existing.get(mt_id, 0)
        n = max(0, target - have) if args.shortfall_only else target
        if n == 0:
            print(f"{mt_id}: already at target ({have}/{target}), skipping")
            continue
        print(f"{mt_id}: generating {n} items (have {have}, target {target})...")
        # Per-item failures are already caught inside generate_for_topic;
        # this is the last-resort backstop for a failure outside that loop
        # (e.g. in the dedup index itself) so one topic's total loss still
        # can't take down the rest of the run.
        try:
            accepted, rejects = generate_for_topic(mt_id, n, dedup, args.attempts_per_item)
        except Exception as e:
            print(f"  -> ERROR generating for {mt_id}, skipping to next topic: {e}")
            continue
        write_items(accepted)
        total_accepted += len(accepted)
        total_rejected += len(rejects)
        print(f"  -> {len(accepted)}/{n} accepted, {len(rejects)} rejected attempts")
        for line in rejects:
            print(f"     {line}")

    print(f"\nDone. {total_accepted} items written, {total_rejected} rejected attempts total.")


if __name__ == "__main__":
    main()
