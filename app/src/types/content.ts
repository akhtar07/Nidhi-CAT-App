/* eslint-disable */
/**
 * AUTO-GENERATED — do not hand-edit.
 *
 * Source of truth is /pipeline/schemas.py (pydantic v2). Regenerate via:
 *   python pipeline/generate_json_schemas.py
 *   node app/scripts/generate-content-types.mjs
 * CI fails the build if this file drifts from that source. See
 * PROGRESS.md for the full generation flow.
 */

export interface ExamMeta {
  /**
   * ISO 8601 date, e.g. '2026-11-29'.
   */
  examDate: string
  /**
   * ISO 8601 date.
   */
  registrationOpensDate: string
  /**
   * ISO 8601 date.
   */
  registrationClosesDate: string
  /**
   * IST time ranges, e.g. '08:30-10:30'.
   */
  slots: string[]
  sectionOrder: ('VARC' | 'DILR' | 'QA')[]
  totalMinutes: number
  minutesPerSection: number
  /**
   * Approx count per section, e.g. {'VARC': 24}.
   */
  questionCount: {
    [k: string]: number
  }
  maxScore: number
}

export interface Lesson {
  id: string
  microTopicId: string
  bodyMarkdown: string
  workedExamples?: WorkedExample[]
  formulaCards?: FormulaCard[]
  commonTraps?: string[]
  estReadMinutes: number
}
export interface WorkedExample {
  id: string
  stemMarkdown: string
  /**
   * Step-by-step. Mandatory, never empty.
   */
  solutionMarkdown: string
  /**
   * The 'smart approach', per SPEC.md §13.
   */
  altSolutionMarkdown?: string | null
}
export interface FormulaCard {
  /**
   * Stable id — the SRS deck (§8.4) keys off this.
   */
  id: string
  microTopicId: string
  title: string
  /**
   * The formula/rule itself, KaTeX-enabled.
   */
  bodyMarkdown: string
  exampleMarkdown?: string | null
}

export interface MicroTopic {
  /**
   * Stable slug id, e.g. 'qa.arith.tsd.boats-streams'. Never an array index.
   */
  id: string
  name: string
  section: 'VARC' | 'DILR' | 'QA'
  topicId: string
  prerequisites?: string[]
  catFrequency: 'high' | 'medium' | 'low' | 'rare'
  roiScore: 1 | 2 | 3 | 4 | 5
  estLearnMinutes: number
  targetSecPerQuestion: number
}

export interface PassageSet {
  id: string
  section: 'VARC' | 'DILR'
  kind: 'rc_passage' | 'di_set' | 'lr_set'
  bodyMarkdown: string
  assets?: PassageAsset[] | null
  questionIds?: string[]
  genre?: string | null
  wordCount?: number | null
  targetMinutes: number
  /**
   * MANDATORY. See SPEC.md §6. Blank fails CI.
   */
  licence: string
  sourceUrl?: string | null
}
export interface PassageAsset {
  type: 'table' | 'chart'
  /**
   * Render charts from data, not images, per SPEC.md §5.1.
   */
  spec: {
    [k: string]: unknown
  }
}

export interface Question {
  /**
   * Stable, content-hash based.
   */
  id: string
  /**
   * @minItems 1
   */
  microTopicIds: [string, ...string[]]
  section: 'VARC' | 'DILR' | 'QA'
  format: 'mcq' | 'tita'
  stemMarkdown: string
  options?: QuestionOption[] | null
  correctKey?: string | null
  correctValue?: string | number | null
  titaTolerance?: number | null
  difficulty: 'easy' | 'medium' | 'hard' | 'very_hard'
  /**
   * Item difficulty, seeded from the difficulty label (§6.4).
   */
  eloRating: number
  /**
   * Step-by-step. MANDATORY, never empty.
   */
  solutionMarkdown: string
  altSolutionMarkdown?: string | null
  targetSeconds: number
  source: 'official_pyq' | 'generated' | 'authored'
  /**
   * e.g. 'CAT 2023 Slot 2 Q14'.
   */
  sourceRef?: string | null
  verification: VerificationRecord
  tags?: string[]
}
export interface QuestionOption {
  key: string
  markdown: string
}
/**
 * Captures which checks in SPEC.md §6.3/§6.4 an item passed.
 */
export interface VerificationRecord {
  method: 'sympy_verified' | 'self_consistency' | 'human_reviewed' | 'answerability_pass' | 'pyq_official'
  /**
   * ISO 8601 timestamp.
   */
  verifiedAt: string
  /**
   * e.g. 4 of 5 sampled solutions agreed, per §6.3.
   */
  selfConsistencyAgreement?: number | null
  /**
   * §6.3 distractor audit.
   */
  distractorAuditPassed?: boolean | null
  /**
   * §6.3 embedding-similarity dedup.
   */
  dedupChecked?: boolean | null
  /**
   * Human review notes, §6.2 step 6.
   */
  reviewerNote?: string | null
}
