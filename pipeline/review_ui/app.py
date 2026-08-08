"""
Human review UI for generated content (SPEC.md §6.2 step 6): "shows the
rendered question... with Approve / Fix / Reject." There's no original PDF
crop to show alongside it here — every item in content/questions/ is
originally authored (source='generated'), not PDF-extracted — so this shows
the rendered question and its SymPy-verified status instead.

Review decisions are logged to pipeline/review_log.json, keyed by question
id, and never mutate content/questions/*.json directly — a rejected item
stays in the bank with a logged 'rejected' status until someone removes it;
this script never silently deletes shipped content.

Run (from /pipeline): streamlit run review_ui/app.py
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
REVIEW_LOG_PATH = REPO_ROOT / "pipeline" / "review_log.json"


@st.cache_data
def load_questions() -> list[dict]:
    items = []
    for path in sorted(QUESTIONS_DIR.glob("*.json")):
        items.append(json.loads(path.read_text()))
    return items


def load_review_log() -> dict[str, dict]:
    if REVIEW_LOG_PATH.exists():
        return json.loads(REVIEW_LOG_PATH.read_text())
    return {}


def save_review_log(log: dict[str, dict]) -> None:
    REVIEW_LOG_PATH.write_text(json.dumps(log, indent=2, sort_keys=True) + "\n")


def record_decision(qid: str, decision: str, note: str) -> None:
    log = load_review_log()
    log[qid] = {
        "decision": decision,
        "note": note,
        "reviewedAt": datetime.now(timezone.utc).isoformat(),
    }
    save_review_log(log)


st.set_page_config(page_title="Ascent — content review", layout="wide")
st.title("Ascent — question review")
st.caption(
    "Every item here was originally authored and SymPy-verified (source='generated'), "
    "not extracted from a PDF — see PROGRESS.md for why. This is the human review pass "
    "SPEC.md §6.2 step 6 calls for before content is considered trustworthy."
)

questions = load_questions()
log = load_review_log()

topics = sorted({q["microTopicIds"][0] for q in questions})
difficulties = ["easy", "medium", "hard", "very_hard"]
statuses = ["unreviewed", "approved", "needs_fix", "rejected"]

with st.sidebar:
    st.header("Filters")
    topic_filter = st.selectbox("Micro-topic", ["(all)"] + topics)
    difficulty_filter = st.selectbox("Difficulty", ["(all)"] + difficulties)
    status_filter = st.selectbox("Review status", ["(all)"] + statuses)

    st.header("Progress")
    counts = {s: 0 for s in statuses}
    for q in questions:
        entry = log.get(q["id"])
        counts[entry["decision"] if entry else "unreviewed"] += 1
    st.metric("Total items", len(questions))
    for s in statuses:
        st.write(f"{s}: {counts[s]}")


def status_of(q: dict) -> str:
    entry = log.get(q["id"])
    return entry["decision"] if entry else "unreviewed"


filtered = [
    q for q in questions
    if (topic_filter == "(all)" or q["microTopicIds"][0] == topic_filter)
    and (difficulty_filter == "(all)" or q["difficulty"] == difficulty_filter)
    and (status_filter == "(all)" or status_of(q) == status_filter)
]

st.write(f"**{len(filtered)}** items match the current filters.")

for q in filtered:
    status = status_of(q)
    badge = {"unreviewed": "⚪", "approved": "✅", "needs_fix": "🟡", "rejected": "🔴"}[status]
    with st.expander(f"{badge} {q['id']}  —  {q['microTopicIds'][0]}  ·  {q['difficulty']}  ·  {q['format']}"):
        st.markdown(f"**Stem:** {q['stemMarkdown']}")

        if q["format"] == "mcq":
            for opt in q["options"]:
                marker = "✔" if opt["key"] == q["correctKey"] else " "
                st.markdown(f"- [{marker}] **{opt['key']}.** {opt['markdown']}")
        else:
            st.markdown(f"**Correct value (TITA):** `{q['correctValue']}`"
                        + (f" (± {q['titaTolerance']})" if q.get("titaTolerance") else ""))

        st.markdown("**Solution:**")
        st.markdown(q["solutionMarkdown"])
        if q.get("altSolutionMarkdown"):
            st.markdown("**Alt (smart) approach:**")
            st.markdown(q["altSolutionMarkdown"])

        st.caption(
            f"verification: {q['verification']['method']} · "
            f"elo {q['eloRating']:.0f} · target {q['targetSeconds']}s · "
            f"tags: {', '.join(q['tags']) or '—'}"
        )

        prior_note = log.get(q["id"], {}).get("note", "")
        note = st.text_input("Note (optional)", value=prior_note, key=f"note-{q['id']}")

        c1, c2, c3 = st.columns(3)
        if c1.button("Approve", key=f"approve-{q['id']}"):
            record_decision(q["id"], "approved", note)
            st.rerun()
        if c2.button("Needs fix", key=f"fix-{q['id']}"):
            record_decision(q["id"], "needs_fix", note)
            st.rerun()
        if c3.button("Reject", key=f"reject-{q['id']}"):
            record_decision(q["id"], "rejected", note)
            st.rerun()
