"""
Build /content/syllabus.json — every micro-topic in SPEC.md §3, as a strict
three-level hierarchy (Section -> Topic -> Micro-topic) with stable slug ids.

`catFrequency` and `roiScore` are pipeline-author judgment calls anchored on
the relative-weight language SPEC.md §3 already uses for each area (e.g. "RC
is 2/3 of VARC", "Arithmetic is ~40-45% of QA", the explicit "drop
Trigonometry heights & distances / Binary logic / Base systems" example in
§10.2). They are not measured frequencies from a paper corpus — SPEC.md §6.4
is explicit that labels like this should "self-correct at runtime" from
learner Elo data once there's attempt history, and the same logic applies
here: treat this as a reasonable starting prior, not ground truth.

Run: python build_syllabus.py
"""

from __future__ import annotations

import json
from pathlib import Path

from schemas import MicroTopic

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = REPO_ROOT / "content" / "syllabus.json"

# Each tuple: (id_suffix, name, prerequisites (full ids), catFrequency,
# roiScore, estLearnMinutes, targetSecPerQuestion)
Row = tuple[str, str, list[str], str, int, int, int]

MICRO_TOPICS: dict[str, list[Row]] = {
    # -------------------------------------------------------------- VARC --
    "varc.rc": [
        ("main-idea", "Main Idea / Central Theme", [], "high", 5, 25, 80),
        ("direct-detail", "Direct / Explicit Detail", [], "high", 5, 20, 70),
        ("vocab-in-context", "Vocabulary-in-Context", [], "medium", 4, 20, 70),
        ("structure-function", "Structure & Function of a Paragraph", ["varc.rc.main-idea"], "medium", 3, 25, 90),
        ("inference", "Inference", ["varc.rc.direct-detail", "varc.rc.main-idea"], "high", 5, 30, 90),
        ("tone-attitude", "Author's Tone & Attitude", ["varc.rc.inference"], "medium", 3, 25, 80),
        ("assumption", "Assumption", ["varc.rc.inference"], "medium", 3, 25, 90),
        ("strengthen-weaken", "Strengthen / Weaken", ["varc.rc.assumption"], "low", 2, 25, 100),
        ("except-least-likely", "Except / Least-likely (Negative Questions)", ["varc.rc.inference"], "medium", 3, 20, 100),
        ("analogy-application", "Analogy / Application", ["varc.rc.inference"], "low", 2, 20, 90),
    ],
    "varc.va": [
        ("para-jumbles", "Para-jumbles", [], "high", 5, 30, 120),
        ("para-summary", "Para-summary", ["varc.rc.main-idea"], "high", 4, 20, 75),
        ("odd-sentence-out", "Odd-sentence-out / Odd-one-out", ["varc.va.para-jumbles"], "medium", 3, 25, 110),
        ("para-completion", "Para-completion / Sentence Insertion", ["varc.va.para-jumbles"], "medium", 3, 25, 100),
        ("critical-reasoning", "Critical Reasoning", ["varc.rc.assumption"], "low", 2, 25, 90),
        ("sentence-correction", "Sentence Correction", [], "rare", 1, 20, 70),
        ("fill-in-blanks", "Fill in the Blanks", [], "rare", 1, 15, 60),
    ],
    # -------------------------------------------------------------- DILR --
    "dilr.di": [
        ("tables", "Tables", [], "high", 5, 30, 90),
        ("bar-column", "Bar / Column Charts", ["dilr.di.tables"], "high", 5, 25, 90),
        ("line-charts", "Line Charts", ["dilr.di.tables"], "medium", 4, 20, 90),
        ("pie-charts", "Pie Charts", ["dilr.di.tables"], "medium", 4, 20, 90),
        ("stacked-charts", "Stacked Charts", ["dilr.di.bar-column"], "medium", 3, 25, 100),
        ("radar-spider", "Radar / Spider Charts", ["dilr.di.bar-column"], "low", 2, 20, 100),
        ("bubble-charts", "Bubble Charts", ["dilr.di.bar-column"], "low", 2, 20, 100),
        ("combination-charts", "Combination Charts", ["dilr.di.bar-column", "dilr.di.line-charts"], "medium", 3, 30, 120),
        ("caselets", "Caselets", ["dilr.di.tables"], "high", 5, 30, 130),
        ("missing-data", "Missing / Incomplete Data Tables", ["dilr.di.tables"], "high", 5, 30, 150),
        ("data-sufficiency", "Data Sufficiency", ["dilr.di.tables"], "medium", 3, 25, 100),
        ("growth-cagr", "Growth Rates, CAGR, Indices & Market Share", ["dilr.di.tables", "qa.arith.percentages"], "high", 5, 35, 120),
    ],
    "dilr.lr": [
        ("arrangements", "Linear & Circular Arrangements", [], "high", 5, 35, 120),
        ("distribution-grouping", "Distribution / Matching / Grouping (2D and 3D)", ["dilr.lr.arrangements"], "high", 5, 40, 150),
        ("selection-conditionalities", "Selection & Conditionalities", ["dilr.lr.arrangements"], "medium", 4, 30, 120),
        ("ordering-ranking", "Ordering & Ranking, Comparisons", ["dilr.lr.arrangements"], "medium", 3, 25, 100),
        ("games-tournaments", "Games & Tournaments", ["dilr.lr.ordering-ranking"], "high", 5, 35, 140),
        ("scheduling", "Scheduling & Timetables", ["dilr.lr.arrangements"], "medium", 3, 30, 130),
        ("venn-set", "Venn Diagrams / Set-based LR", ["qa.modern.set-theory-venn"], "medium", 3, 25, 100),
        ("network-routes", "Network & Routes, Maxima-Minima Flow", ["dilr.lr.arrangements"], "medium", 3, 30, 130),
        ("binary-logic", "Binary Logic (Truth-teller / Liar)", [], "low", 2, 20, 100),
        ("cubes-dice", "Cubes, Dice, Matrices", [], "low", 2, 25, 110),
        ("quant-embedded", "Quant-embedded LR", ["dilr.lr.arrangements"], "medium", 3, 30, 130),
        ("number-placement", "Puzzles: Number Placement, Magic Squares, Sudoku-like Grids", ["dilr.lr.arrangements"], "low", 2, 25, 120),
    ],
    # ---------------------------------------------------------------- QA --
    "qa.arith": [
        ("percentages", "Percentages", [], "high", 5, 30, 75),
        ("profit-loss-discount", "Profit, Loss & Discount", ["qa.arith.percentages"], "high", 5, 30, 90),
        ("si-ci-instalments", "Simple & Compound Interest, Instalments", ["qa.arith.percentages"], "medium", 4, 30, 100),
        ("ratio-proportion-variation", "Ratio, Proportion & Variation", [], "high", 5, 25, 90),
        ("mixtures-alligation", "Mixtures & Alligation", ["qa.arith.ratio-proportion-variation"], "medium", 4, 25, 110),
        ("averages-weighted-averages", "Averages & Weighted Averages", ["qa.arith.ratio-proportion-variation"], "high", 5, 20, 90),
        ("tsd-relative-speed", "Time, Speed & Distance: Relative Speed", ["qa.arith.ratio-proportion-variation"], "high", 4, 30, 110),
        ("tsd-trains", "TSD: Trains", ["qa.arith.tsd-relative-speed"], "medium", 3, 20, 110),
        ("tsd-boats-streams", "TSD: Boats & Streams", ["qa.arith.tsd-relative-speed"], "medium", 3, 20, 100),
        ("tsd-races", "TSD: Races", ["qa.arith.tsd-relative-speed"], "low", 2, 20, 120),
        ("tsd-circular-tracks", "TSD: Circular Tracks", ["qa.arith.tsd-relative-speed"], "medium", 3, 25, 120),
        ("time-work-pipes-cisterns", "Time & Work: Pipes & Cisterns", ["qa.arith.ratio-proportion-variation"], "high", 5, 25, 100),
        ("time-work-efficiency-wages", "Time & Work: Efficiency, Work-wages", ["qa.arith.time-work-pipes-cisterns"], "medium", 4, 20, 100),
        ("time-work-chain-rule", "Time & Work: Chain Rule", ["qa.arith.time-work-pipes-cisterns"], "low", 2, 15, 90),
    ],
    "qa.algebra": [
        ("linear-equations", "Linear Equations, Systems, Integer Solutions", [], "high", 5, 30, 90),
        ("integer-solutions", "Integer Solutions (Diophantine-style)", ["qa.algebra.linear-equations"], "medium", 3, 25, 110),
        ("quadratic-equations", "Quadratic Equations: Roots, Discriminant, Sign Analysis", ["qa.algebra.linear-equations"], "high", 5, 30, 90),
        ("polynomials-remainder-factor", "Higher-degree Polynomials, Remainder & Factor Theorem", ["qa.algebra.quadratic-equations"], "medium", 3, 30, 120),
        ("inequalities-modulus", "Inequalities & Modulus", ["qa.algebra.quadratic-equations"], "medium", 3, 25, 110),
        ("logarithms", "Logarithms", ["qa.algebra.linear-equations"], "medium", 4, 25, 90),
        ("surds-indices", "Surds, Indices, Simplification", ["qa.algebra.linear-equations"], "medium", 4, 20, 90),
        ("functions", "Functions: Composite, Inverse, Graphs, Transformations", ["qa.algebra.quadratic-equations"], "medium", 3, 35, 120),
        ("maxima-minima", "Maxima & Minima (AM-GM, Quadratic Vertex)", ["qa.algebra.quadratic-equations", "qa.algebra.inequalities-modulus"], "low", 2, 30, 130),
        ("progressions", "Progressions: AP, GP, HP, AGP, Special Series", ["qa.algebra.linear-equations"], "high", 5, 35, 100),
    ],
    "qa.geometry": [
        ("lines-angles", "Lines, Angles, Parallel Lines", [], "medium", 3, 20, 90),
        ("triangles", "Triangles: Congruence, Similarity, Centres, Pythagorean Triples", ["qa.geometry.lines-angles"], "high", 5, 35, 110),
        ("quadrilaterals-polygons", "Quadrilaterals & Polygons", ["qa.geometry.triangles"], "medium", 4, 25, 100),
        ("circles", "Circles: Tangents, Chords, Cyclic Quadrilaterals, Sectors", ["qa.geometry.triangles"], "medium", 4, 30, 120),
        ("coordinate-geometry", "Coordinate Geometry: Lines, Distance, Section Formula, Circles, Loci", ["qa.geometry.lines-angles"], "medium", 3, 30, 110),
        ("trigonometry", "Trigonometry: Ratios, Identities, Heights & Distances", ["qa.geometry.triangles"], "low", 2, 25, 120),
        ("mensuration-2d", "Mensuration 2D", ["qa.geometry.quadrilaterals-polygons", "qa.geometry.circles"], "high", 5, 25, 100),
        ("mensuration-3d", "Mensuration 3D", ["qa.geometry.mensuration-2d"], "medium", 3, 30, 130),
    ],
    "qa.numsys": [
        ("divisibility-factors", "Divisibility Rules, Factors & Multiples", [], "high", 5, 20, 80),
        ("hcf-lcm", "HCF & LCM", ["qa.numsys.divisibility-factors"], "high", 5, 20, 80),
        ("remainders", "Remainders: Cyclicity, Fermat, Euler, Wilson, CRT", ["qa.numsys.divisibility-factors"], "medium", 4, 30, 110),
        ("factors-count-sum-product", "Number of Factors, Sum of Factors, Product of Factors", ["qa.numsys.divisibility-factors"], "medium", 4, 25, 100),
        ("base-systems", "Base Systems / Number Bases", ["qa.numsys.divisibility-factors"], "rare", 1, 25, 100),
        ("last-digit-trailing-zeroes", "Last Digit, Last Two Digits, Trailing Zeroes", ["qa.numsys.divisibility-factors"], "medium", 4, 20, 90),
        ("factorials-prime-power", "Factorials, Highest Power of a Prime in n!", ["qa.numsys.divisibility-factors"], "medium", 3, 20, 100),
        ("rational-irrational", "Rational / Irrational, Properties of Integers", [], "low", 2, 15, 80),
    ],
    "qa.modern": [
        ("permutations-combinations", "Permutations & Combinations", [], "high", 5, 35, 110),
        ("probability", "Probability: Basic, Conditional, Independent Events", ["qa.modern.permutations-combinations"], "medium", 4, 30, 110),
        ("set-theory-venn", "Set Theory & Venn Diagrams", [], "medium", 4, 20, 90),
        ("binomial-theorem", "Binomial Theorem (Light)", ["qa.modern.permutations-combinations"], "low", 2, 20, 100),
        ("series-sequences-hybrids", "Logical/Quant Hybrids, Series & Sequences", ["qa.algebra.progressions"], "low", 2, 25, 100),
    ],
}

TOPIC_NAMES = {
    "varc.rc": "Reading Comprehension",
    "varc.va": "Verbal Ability",
    "dilr.di": "Data Interpretation",
    "dilr.lr": "Logical Reasoning",
    "qa.arith": "Arithmetic",
    "qa.algebra": "Algebra",
    "qa.geometry": "Geometry & Mensuration",
    "qa.numsys": "Number System",
    "qa.modern": "Modern Mathematics",
}

SECTION_OF_TOPIC = {
    "varc.rc": "VARC",
    "varc.va": "VARC",
    "dilr.di": "DILR",
    "dilr.lr": "DILR",
    "qa.arith": "QA",
    "qa.algebra": "QA",
    "qa.geometry": "QA",
    "qa.numsys": "QA",
    "qa.modern": "QA",
}


def build() -> list[MicroTopic]:
    topics: list[MicroTopic] = []
    all_ids: set[str] = set()

    for topic_id, rows in MICRO_TOPICS.items():
        for suffix, *_ in rows:
            all_ids.add(f"{topic_id}.{suffix}")

    for topic_id, rows in MICRO_TOPICS.items():
        section = SECTION_OF_TOPIC[topic_id]
        for suffix, name, prereqs, cat_freq, roi, learn_min, target_sec in rows:
            mt_id = f"{topic_id}.{suffix}"
            for p in prereqs:
                if p not in all_ids:
                    raise ValueError(f"{mt_id}: unknown prerequisite {p!r}")
            topics.append(
                MicroTopic(
                    id=mt_id,
                    name=name,
                    section=section,
                    topicId=topic_id,
                    prerequisites=prereqs,
                    catFrequency=cat_freq,
                    roiScore=roi,
                    estLearnMinutes=learn_min,
                    targetSecPerQuestion=target_sec,
                )
            )

    ids = [t.id for t in topics]
    dupes = {i for i in ids if ids.count(i) > 1}
    if dupes:
        raise ValueError(f"Duplicate micro-topic ids: {dupes}")

    return topics


def main() -> None:
    topics = build()
    data = [json.loads(t.model_dump_json()) for t in topics]
    OUT_PATH.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Wrote {len(data)} micro-topics to {OUT_PATH.relative_to(REPO_ROOT)}")

    by_section: dict[str, int] = {}
    for t in topics:
        by_section[t.section] = by_section.get(t.section, 0) + 1
    for section, count in sorted(by_section.items()):
        print(f"  {section}: {count}")


if __name__ == "__main__":
    main()
