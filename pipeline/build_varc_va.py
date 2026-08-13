"""
VARC / Verbal Ability questions for the six VA micro-topics that had none.

These are original, hand-authored items — not scraped, and not LLM-generated. SPEC.md
§6.3's "never let the model invent the answer" rule applies just as much to verbal
questions as to quant, so the structure here keeps the answer fixed by construction:

- Every item names its correct option explicitly in the source data.
- `verify()` below re-checks each item mechanically before anything is written: exactly
  four distinct options, the stated answer present exactly once, a non-empty explanation,
  and no duplicate stems anywhere in the bank.

Where an item's correctness rests on a grammatical rule (agreement, parallelism, dangling
modifiers), the three distractors are each built by introducing one **named** error into
the correct sentence, so "why is this wrong" is answerable for every option rather than
being a matter of taste. That naming is what keeps these defensible.

Run (from /pipeline): python build_varc_va.py
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from schemas import Question, QuestionOption, VerificationRecord

REPO_ROOT = Path(__file__).resolve().parent.parent
QUESTIONS_DIR = REPO_ROOT / "content" / "questions"
VERIFIED_AT = "2026-08-13T00:00:00Z"


@dataclass
class VAItem:
    mt: str
    stem: str
    options: list[str]
    answer: str            # must appear in options exactly once
    explanation: str
    difficulty: str = "medium"
    seconds: int = 60
    tags: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# varc.va.sentence-correction
# Each distractor carries exactly one named error against the correct sentence.
# ---------------------------------------------------------------------------

SC = "varc.va.sentence-correction"
_SC = [
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["The list of banned items is displayed at the entrance.",
            "The list of banned items are displayed at the entrance.",
            "The list of banned items were displayed at the entrance.",
            "The list of banned items have been displayed at the entrance."],
           "The list of banned items is displayed at the entrance.",
           "The subject is **list**, which is singular; **of banned items** is a prepositional phrase and "
           "cannot change the subject. So the verb must be **is**. The plural noun sitting next to the verb "
           "is what misleads the ear.",
           tags=["va:sentence-correction", "subject-verb"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["She enjoys reading, writing and painting.",
            "She enjoys reading, writing and to paint.",
            "She enjoys to read, writing and painting.",
            "She enjoys reading, to write and painting."],
           "She enjoys reading, writing and painting.",
           "Items in a list must share a grammatical form. All three must be gerunds — **reading, writing "
           "and painting**. Each wrong option switches one item to an infinitive, breaking the parallelism.",
           tags=["va:sentence-correction", "parallelism"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["Having finished the report, I found that the printer had jammed.",
            "Having finished the report, the printer had jammed.",
            "Having finished the report, the jam in the printer was discovered.",
            "Having finished the report, it was found that the printer jammed."],
           "Having finished the report, I found that the printer had jammed.",
           "An opening participial phrase attaches to whatever immediately follows the comma. Only the "
           "correct option puts a person there; the others make the printer, the jam, or nothing at all "
           "the one who finished the report. This is a **dangling modifier**.",
           difficulty="hard", seconds=75, tags=["va:sentence-correction", "modifier"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["Neither the manager nor the employees were informed of the change.",
            "Neither the manager nor the employees was informed of the change.",
            "Neither the manager nor the employees is informed of the change.",
            "Neither the manager or the employees were informed of the change."],
           "Neither the manager nor the employees were informed of the change.",
           "With **neither ... nor**, the verb agrees with the nearer subject, which is **employees** "
           "(plural), so **were** is right. The last option also wrongly pairs **neither** with **or** "
           "instead of **nor**.",
           difficulty="hard", seconds=75, tags=["va:sentence-correction", "subject-verb"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["Each of the candidates has submitted a proposal.",
            "Each of the candidates have submitted a proposal.",
            "Each of the candidates are submitting a proposal.",
            "Each of the candidates were submitting a proposal."],
           "Each of the candidates has submitted a proposal.",
           "**Each** is always singular, however many candidates there are, so it takes **has**. The "
           "plural **candidates** belongs to the prepositional phrase and does not govern the verb.",
           tags=["va:sentence-correction", "subject-verb"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["The new policy is more effective than the old one.",
            "The new policy is more effective than the old.",
            "The new policy is more effective as the old one.",
            "The new policy is the most effective than the old one."],
           "The new policy is more effective than the old one.",
           "A comparison of two things uses the comparative **more effective ... than**. The third option "
           "wrongly uses **as** with a comparative, and the fourth mixes a superlative with **than**.",
           tags=["va:sentence-correction", "comparatives"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["When the committee announced its decision, the members applauded.",
            "When the committee announced their decision, the members applauded.",
            "When the committee announced it's decision, the members applauded.",
            "When the committee announced its' decision, the members applauded."],
           "When the committee announced its decision, the members applauded.",
           "**Committee** here acts as a single body, so the possessive is **its**. Note **it's** means "
           "'it is', and **its'** is not a word at all.",
           tags=["va:sentence-correction", "pronoun"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["The scientist explained that water boils at 100 degrees Celsius at sea level.",
            "The scientist explained that water boiled at 100 degrees Celsius at sea level.",
            "The scientist explained that water will boil at 100 degrees Celsius at sea level.",
            "The scientist explained that water would have boiled at 100 degrees Celsius at sea level."],
           "The scientist explained that water boils at 100 degrees Celsius at sea level.",
           "A permanent scientific fact stays in the present tense even after a past-tense reporting verb. "
           "Shifting it to the past wrongly implies water no longer behaves that way.",
           difficulty="hard", seconds=75, tags=["va:sentence-correction", "tense"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["Between you and me, the proposal seems unworkable.",
            "Between you and I, the proposal seems unworkable.",
            "Between yourself and I, the proposal seems unworkable.",
            "Between you and myself, the proposal seems unworkable."],
           "Between you and me, the proposal seems unworkable.",
           "**Between** is a preposition, so the pronouns following it must be in the object form: **me**, "
           "not **I**. Reflexives like **myself** cannot serve as the object of a preposition here either.",
           tags=["va:sentence-correction", "pronoun"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["The number of applicants has risen sharply this year.",
            "The number of applicants have risen sharply this year.",
            "A number of applicants has risen sharply this year.",
            "The number of applicants are rising sharply this year."],
           "The number of applicants has risen sharply this year.",
           "**The number** is singular and takes **has**; confusingly, **a number of** is plural and takes "
           "a plural verb. The third option uses the plural phrase with a singular verb and also changes "
           "the meaning.",
           difficulty="hard", seconds=75, tags=["va:sentence-correction", "subject-verb"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["Not only did she finish the report, but she also presented it.",
            "Not only she finished the report, but she also presented it.",
            "Not only did she finish the report, but she presented it also.",
            "Not only she did finish the report, but also presented it."],
           "Not only did she finish the report, but she also presented it.",
           "**Not only** at the start of a clause forces inversion — **did she finish** — and it pairs with "
           "**but also** in the standard correlative structure.",
           difficulty="hard", seconds=80, tags=["va:sentence-correction", "parallelism"]),
    VAItem(SC, "Which of the following sentences is grammatically correct?",
           ["Fewer people attended than we had expected.",
            "Less people attended than we had expected.",
            "Fewer people attended then we had expected.",
            "Less people attended then we had expected."],
           "Fewer people attended than we had expected.",
           "**Fewer** is used for countable nouns like people; **less** is for uncountable quantities. "
           "Also **than** makes comparisons, while **then** refers to time.",
           tags=["va:sentence-correction", "usage"]),
]

# ---------------------------------------------------------------------------
# varc.va.fill-in-blanks
# ---------------------------------------------------------------------------

FB = "varc.va.fill-in-blanks"
_FB = [
    VAItem(FB, "Choose the word that best fits the blank:\n\nAlthough the team had prepared thoroughly, their performance was ___.",
           ["disappointing", "exemplary", "thorough", "commendable"],
           "disappointing",
           "**Although** signals a contrast, so the result must run against what thorough preparation "
           "would predict. Only **disappointing** is negative; the other three are positive or neutral.",
           tags=["va:fill-blanks", "contrast"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nBecause the evidence was overwhelming, the jury reached a ___ verdict.",
           ["unanimous", "tentative", "disputed", "delayed"],
           "unanimous",
           "**Because** signals agreement between cause and effect. Overwhelming evidence produces "
           "agreement, so **unanimous** follows. The others all imply doubt or difficulty, contradicting "
           "the stated cause.",
           tags=["va:fill-blanks", "cause"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nThe minister's answer was deliberately ___, leaving reporters unsure what had actually been decided.",
           ["vague", "precise", "lengthy", "audible"],
           "vague",
           "The second half explains the blank: reporters were left unsure. Only **vague** produces that "
           "confusion. **Lengthy** and **audible** do not bear on clarity, and **precise** is its opposite.",
           tags=["va:fill-blanks", "context"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nDespite its ___ appearance, the building is structurally sound.",
           ["dilapidated", "imposing", "modern", "elegant"],
           "dilapidated",
           "**Despite** sets up a contrast with **structurally sound**, so the appearance must suggest the "
           "opposite. Only **dilapidated** implies decay; the others would agree with soundness rather "
           "than contrast with it.",
           tags=["va:fill-blanks", "contrast"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nHer argument was so ___ that even her critics conceded the point.",
           ["compelling", "convoluted", "tentative", "brief"],
           "compelling",
           "Critics conceding indicates the argument succeeded, so the blank needs strong positive force. "
           "**Compelling** supplies it. **Convoluted** and **tentative** would weaken it, and **brief** "
           "says nothing about persuasiveness.",
           tags=["va:fill-blanks", "context"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nThe policy was introduced to ___ the shortage, but it made matters worse.",
           ["alleviate", "aggravate", "conceal", "postpone"],
           "alleviate",
           "**But it made matters worse** contrasts with the intention, so the intention must have been "
           "to improve things: **alleviate**. **Aggravate** would remove the contrast the sentence "
           "explicitly signals.",
           difficulty="hard", seconds=70, tags=["va:fill-blanks", "contrast"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nMoreover, the report ___ the earlier findings rather than challenging them.",
           ["corroborated", "contradicted", "ignored", "delayed"],
           "corroborated",
           "**Rather than challenging** tells you directly that the report supported the findings, and "
           "**moreover** signals continuation rather than contrast. **Corroborated** means confirmed.",
           tags=["va:fill-blanks", "continuation"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nThe committee remained ___ despite hours of debate, and no decision was reached.",
           ["divided", "unanimous", "efficient", "punctual"],
           "divided",
           "No decision was reached, so the committee must have stayed in disagreement: **divided**. "
           "**Unanimous** would have produced a decision, and the other two are irrelevant to agreement.",
           tags=["va:fill-blanks", "context"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nHis explanation was ___; it accounted for every detail we had raised.",
           ["comprehensive", "superficial", "evasive", "concise"],
           "comprehensive",
           "The semicolon introduces an explanation of the blank: it covered every detail. That is "
           "**comprehensive**. **Concise** describes length, not coverage, and the other two contradict "
           "the second clause.",
           tags=["va:fill-blanks", "context"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nThe results were ___, so the team repeated the experiment before publishing.",
           ["inconclusive", "definitive", "publishable", "encouraging"],
           "inconclusive",
           "Repeating the experiment implies the first results settled nothing, which is **inconclusive**. "
           "Each other option would have made repetition unnecessary.",
           difficulty="hard", seconds=70, tags=["va:fill-blanks", "cause"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nFar from being ___, the reform was welcomed by nearly every group it affected.",
           ["controversial", "popular", "welcome", "beneficial"],
           "controversial",
           "**Far from being X** means the opposite of X is true. Since the reform was widely welcomed, "
           "X must mean disputed: **controversial**. The other three would make the sentence contradict "
           "itself.",
           difficulty="hard", seconds=75, tags=["va:fill-blanks", "negation"]),
    VAItem(FB, "Choose the word that best fits the blank:\n\nThe witness gave a ___ account, changing key details each time she was questioned.",
           ["inconsistent", "detailed", "credible", "rehearsed"],
           "inconsistent",
           "Changing details each time is the definition of **inconsistent**. **Detailed** and "
           "**rehearsed** do not address the contradiction, and **credible** contradicts it.",
           tags=["va:fill-blanks", "context"]),
]

# ---------------------------------------------------------------------------
# varc.va.critical-reasoning
# ---------------------------------------------------------------------------

CR = "varc.va.critical-reasoning"
_CR = [
    VAItem(CR, "A company reports: \"After we redesigned our packaging, sales rose 20 percent. The redesign clearly caused the increase.\"\n\nWhich of the following, if true, most weakens this argument?",
           ["The company's main competitor withdrew from the market in the same month.",
            "The redesign was carried out by an experienced design agency.",
            "Some customers said they preferred the earlier packaging.",
            "The redesign cost more than the company had budgeted."],
           "The company's main competitor withdrew from the market in the same month.",
           "The argument leaps from a correlation in time to a cause. It is weakened most by an "
           "**alternative explanation** for the same rise, which a competitor's exit provides. The other "
           "options concern the redesign's quality or cost, neither of which bears on what caused the "
           "sales increase.",
           difficulty="hard", seconds=90, tags=["va:critical-reasoning", "weaken"]),
    VAItem(CR, "A survey conducted on a shopping website found that 90 percent of respondents prefer shopping online. The site concludes that most people prefer shopping online.\n\nThe reasoning is flawed because:",
           ["the people surveyed are not representative of the general population",
            "90 percent is not a large enough majority to draw conclusions",
            "the survey did not ask respondents to explain their preference",
            "online shopping has grown steadily in recent years"],
           "the people surveyed are not representative of the general population",
           "Everyone surveyed was already visiting a shopping website, so they were predisposed to prefer "
           "online shopping. A self-selected sample cannot support a claim about people in general. This "
           "is **selection bias**, and it is the flaw regardless of how large the percentage is.",
           difficulty="hard", seconds=90, tags=["va:critical-reasoning", "flaw"]),
    VAItem(CR, "\"The new bridge will reduce traffic congestion, because it provides drivers with a second route into the city.\"\n\nThe argument assumes that:",
           ["a meaningful number of drivers will actually use the new route",
            "the bridge was completed within its original budget",
            "the existing route is the oldest road into the city",
            "congestion is the most serious problem facing the city"],
           "a meaningful number of drivers will actually use the new route",
           "Apply the negation test. If no drivers use the new route, the bridge cannot reduce congestion "
           "and the argument collapses — so this is a **necessary assumption**. Negating any other option "
           "leaves the argument intact, so none of them is assumed.",
           difficulty="hard", seconds=90, tags=["va:critical-reasoning", "assumption"]),
    VAItem(CR, "\"Students who eat breakfast score higher on tests. Therefore, schools should provide free breakfast to raise test scores.\"\n\nWhich of the following, if true, most strengthens this argument?",
           ["In trials where breakfast was provided to randomly chosen students, their scores rose.",
            "Breakfast is widely regarded as the most important meal of the day.",
            "Most students say they would eat a free breakfast if it were offered.",
            "Schools in wealthier districts already provide free breakfast."],
           "In trials where breakfast was provided to randomly chosen students, their scores rose.",
           "The argument's weakness is that eating breakfast may simply mark out better-off or "
           "better-organised households. A **randomised** trial removes that alternative explanation and "
           "supports genuine causation. The others restate opinion, intention, or an existing practice "
           "without addressing cause.",
           difficulty="hard", seconds=90, tags=["va:critical-reasoning", "strengthen"]),
    VAItem(CR, "\"Either we raise ticket prices or the museum will close. We cannot let the museum close, so prices must rise.\"\n\nThe reasoning is most vulnerable to the criticism that it:",
           ["treats two options as the only possibilities when others may exist",
            "assumes the museum is worth keeping open",
            "relies on the opinions of museum staff",
            "does not specify how much prices would rise"],
           "treats two options as the only possibilities when others may exist",
           "This is a **false dichotomy**. Donations, sponsorship, reduced opening hours or public funding "
           "could all be alternatives, and the argument never rules them out. The other options question "
           "the premises' desirability or detail, not the logical structure.",
           difficulty="hard", seconds=90, tags=["va:critical-reasoning", "flaw"]),
    VAItem(CR, "\"The average salary at our firm rose last year. Therefore every employee earned more than in the previous year.\"\n\nThe reasoning is flawed because:",
           ["an average can rise even if some individuals earn less",
            "salaries are not the only form of compensation",
            "the firm may have hired new employees",
            "the previous year's figures may have been misreported"],
           "an average can rise even if some individuals earn less",
           "This moves from a **group statistic to a claim about every individual**. A rise in the average "
           "is fully consistent with some employees taking a pay cut, as long as others gained more. The "
           "other options raise possibilities but do not identify the logical error.",
           difficulty="hard", seconds=85, tags=["va:critical-reasoning", "flaw"]),
    VAItem(CR, "\"Cities with more parks report lower rates of anxiety. Building more parks would therefore reduce anxiety.\"\n\nWhich of the following, if true, most weakens this argument?",
           ["Wealthier cities tend both to build more parks and to have better healthcare.",
            "Some people who live near parks never visit them.",
            "Parks are expensive to maintain over time.",
            "Anxiety can be measured in several different ways."],
           "Wealthier cities tend both to build more parks and to have better healthcare.",
           "This identifies a **common cause** — wealth — that could produce both the parks and the lower "
           "anxiety, meaning the parks need not be doing the work. The other options concern usage, cost "
           "or measurement, none of which undermines the causal claim itself.",
           difficulty="very_hard", seconds=95, tags=["va:critical-reasoning", "weaken"]),
    VAItem(CR, "\"All employees who completed the training passed the audit. Ramesh passed the audit, so he must have completed the training.\"\n\nThe reasoning is flawed because:",
           ["passing the audit may be possible without the training",
            "Ramesh may have completed a different training course",
            "the audit may not be a fair test of ability",
            "not all employees are required to take the audit"],
           "passing the audit may be possible without the training",
           "The premise says training is **sufficient** for passing, not **necessary**. Someone could pass "
           "without it, so the conclusion does not follow. This is the classic error of reversing a "
           "conditional: 'all A are B' does not give 'all B are A'.",
           difficulty="very_hard", seconds=95, tags=["va:critical-reasoning", "flaw"]),
]

# ---------------------------------------------------------------------------
# varc.va.para-summary
# ---------------------------------------------------------------------------

PS = "varc.va.para-summary"
_PS = [
    VAItem(PS, "Summarise the paragraph:\n\n\"Microfinance has genuinely helped some borrowers start small businesses and smooth irregular incomes. But its advocates have often presented it as a cure for poverty itself, a claim the evidence does not support. Most studies find modest gains for a minority of borrowers and no measurable effect on overall poverty rates.\"",
           ["Microfinance offers real but limited benefits that its supporters have overstated.",
            "Microfinance has failed to help borrowers and should be abandoned.",
            "Microfinance allows borrowers to start small businesses and smooth incomes.",
            "Studies of microfinance have produced inconsistent and unreliable results."],
           "Microfinance offers real but limited benefits that its supporters have overstated.",
           "The paragraph makes two moves: it concedes real benefits, then criticises the exaggeration. A "
           "faithful summary must keep both. The second option drops the concession and overstates the "
           "criticism, the third drops the criticism entirely, and the fourth misdescribes the evidence, "
           "which the paragraph says is fairly consistent.",
           difficulty="hard", seconds=90, tags=["va:para-summary"]),
    VAItem(PS, "Summarise the paragraph:\n\n\"Remote work reduces commuting time and gives employees more control over their day. Yet it also weakens the informal contact through which junior staff learn from experienced colleagues. Organisations that have moved entirely remote report faster individual output but slower development of new hires.\"",
           ["Remote work improves individual productivity but hinders the informal learning junior staff rely on.",
            "Remote work is more efficient than office work in every respect.",
            "Organisations should require all employees to return to the office.",
            "Junior staff generally prefer working in an office to working remotely."],
           "Remote work improves individual productivity but hinders the informal learning junior staff rely on.",
           "The paragraph balances a benefit against a cost, and the summary must carry both. The second "
           "option keeps only the benefit, the third recommends an action the paragraph never proposes, "
           "and the fourth asserts a preference that is never mentioned.",
           difficulty="hard", seconds=90, tags=["va:para-summary"]),
    VAItem(PS, "Summarise the paragraph:\n\n\"Early maps of the ocean floor assumed it was a featureless plain. Sonar surveys in the twentieth century revealed mountain ranges longer than any on land, trenches deeper than the Himalayas are tall, and volcanic activity along vast ridges. The ocean floor turned out to be more geologically active than the continents.\"",
           ["Sonar revealed the ocean floor to be dramatically more varied and active than had been assumed.",
            "Sonar technology was the most important scientific advance of the twentieth century.",
            "The ocean floor contains mountain ranges and deep trenches.",
            "Early cartographers made serious errors in mapping the continents."],
           "Sonar revealed the ocean floor to be dramatically more varied and active than had been assumed.",
           "The paragraph's point is the overturning of an assumption. The third option lists details "
           "without the contrast that gives them meaning; the second makes a claim about sonar's "
           "importance the paragraph never makes; the fourth misplaces the error onto continental mapping.",
           seconds=85, tags=["va:para-summary"]),
    VAItem(PS, "Summarise the paragraph:\n\n\"Attempts to measure a school's quality by its examination results are appealing because the data already exists. But results reflect the students a school admits at least as much as the teaching it provides. A school selecting high-achieving entrants will post strong results regardless of what happens in its classrooms.\"",
           ["Exam results are a poor measure of school quality because they largely reflect which students were admitted.",
            "Schools should stop publishing their examination results.",
            "Examination data is convenient because it is already collected.",
            "High-achieving students perform well wherever they are educated."],
           "Exam results are a poor measure of school quality because they largely reflect which students were admitted.",
           "The paragraph concedes convenience and then explains why the measure fails. The correct "
           "summary keeps the conclusion and its reason. The second recommends an action never proposed, "
           "the third keeps only the concession, and the fourth states a supporting detail as though it "
           "were the main point.",
           difficulty="hard", seconds=90, tags=["va:para-summary"]),
    VAItem(PS, "Summarise the paragraph:\n\n\"Antibiotic resistance is often described as a future threat. It is not. Infections that no longer respond to first-line treatment are already routine in hospitals worldwide, and the pipeline of genuinely new antibiotics has been nearly empty for two decades.\"",
           ["Antibiotic resistance is a present crisis, not a future one, and few new drugs are coming.",
            "Antibiotic resistance will become a serious problem within the next few decades.",
            "Hospitals should improve their infection control procedures.",
            "Pharmaceutical companies have stopped researching new medicines altogether."],
           "Antibiotic resistance is a present crisis, not a future one, and few new drugs are coming.",
           "The paragraph exists to correct a framing: the threat is current, not future. The second "
           "option reasserts exactly the view being corrected. The third proposes an unmentioned action, "
           "and the fourth overstates 'nearly empty antibiotic pipeline' into abandoning all research.",
           seconds=85, tags=["va:para-summary"]),
    VAItem(PS, "Summarise the paragraph:\n\n\"The city's cycle lanes were built quickly and have been well used. But they stop abruptly at major junctions, precisely where cyclists are most at risk. Usage data shows riders diverting onto pavements at these points, which suggests the network's gaps matter more than its total length.\"",
           ["The cycle network's usefulness is limited by gaps at dangerous junctions rather than by its overall size.",
            "The city's cycle lanes were built too quickly to be safe.",
            "Cyclists in the city frequently ride on pavements.",
            "The city should build a greater total length of cycle lanes."],
           "The cycle network's usefulness is limited by gaps at dangerous junctions rather than by its overall size.",
           "The paragraph's conclusion is explicitly about gaps mattering more than length. The second "
           "blames the speed of construction, which the paragraph mentions neutrally; the third reports a "
           "supporting observation as the main point; the fourth recommends the very thing the paragraph "
           "says is not the issue.",
           difficulty="hard", seconds=90, tags=["va:para-summary"]),
]

# ---------------------------------------------------------------------------
# varc.va.odd-sentence-out
# ---------------------------------------------------------------------------

OS = "varc.va.odd-sentence-out"
_OS = [
    VAItem(OS, "Four of the following five sentences form a coherent paragraph. Which one does NOT belong?\n\n"
               "1. In 2010 the city council began redesigning its bus network.\n"
               "2. The redesign replaced dozens of winding routes with a smaller grid of frequent ones.\n"
               "3. Public transport is a system of shared vehicles operating on fixed routes.\n"
               "4. Ridership rose by a third within two years of the change.\n"
               "5. Similar redesigns have since been adopted by three neighbouring cities.",
           ["Sentence 3", "Sentence 1", "Sentence 4", "Sentence 5"],
           "Sentence 3",
           "Sentences 1, 2, 4 and 5 form a chronological account of one city's redesign and its "
           "consequences, each referring back to the previous. Sentence 3 is a **general definition** "
           "pitched at a different level entirely — on topic, but doing a different job and connected to "
           "nothing in the sequence.",
           difficulty="hard", seconds=90, tags=["va:odd-sentence"]),
    VAItem(OS, "Four of the following five sentences form a coherent paragraph. Which one does NOT belong?\n\n"
               "1. Coral reefs support roughly a quarter of all marine species.\n"
               "2. They do so by providing physical structure in otherwise open water.\n"
               "3. This structure offers shelter, breeding sites and hunting grounds.\n"
               "4. Rising sea temperatures have caused widespread coral bleaching since the 1980s.\n"
               "5. Remove the reef and the species that depend on that structure disappear with it.",
           ["Sentence 4", "Sentence 2", "Sentence 3", "Sentence 5"],
           "Sentence 4",
           "Sentences 1, 2, 3 and 5 build a single argument about **why** reefs support so much life — "
           "structure, what it provides, and what happens without it. Sentence 4 introduces a separate "
           "topic, the causes of bleaching, which the surrounding argument neither sets up nor uses.",
           difficulty="hard", seconds=90, tags=["va:odd-sentence"]),
    VAItem(OS, "Four of the following five sentences form a coherent paragraph. Which one does NOT belong?\n\n"
               "1. The manuscript was discovered in a monastery library in 1923.\n"
               "2. Its margins contained notes in at least three different hands.\n"
               "3. Scholars used these annotations to trace the text's readers across two centuries.\n"
               "4. Monasteries in the region were founded largely between the ninth and eleventh centuries.\n"
               "5. The result was a detailed picture of how the work had been used and understood.",
           ["Sentence 4", "Sentence 1", "Sentence 3", "Sentence 5"],
           "Sentence 4",
           "Sentences 1, 2, 3 and 5 follow one thread: a manuscript found, its annotations, what scholars "
           "did with them, and the outcome. Sentence 4 gives background about **when monasteries were "
           "founded**, which nothing else refers to and which the argument never uses.",
           seconds=85, tags=["va:odd-sentence"]),
    VAItem(OS, "Four of the following five sentences form a coherent paragraph. Which one does NOT belong?\n\n"
               "1. Most people assume that adding lanes to a motorway reduces congestion.\n"
               "2. In practice, extra capacity tends to attract additional drivers.\n"
               "3. Within a few years, traffic often returns to its previous level of delay.\n"
               "4. Economists call this effect induced demand.\n"
               "5. Motorways are typically maintained by national rather than local authorities.",
           ["Sentence 5", "Sentence 2", "Sentence 3", "Sentence 4"],
           "Sentence 5",
           "Sentences 1 to 4 develop one idea from assumption to mechanism to its name. Sentence 5 is an "
           "administrative fact about **who maintains motorways**, unrelated to the argument about "
           "congestion and referenced by nothing else.",
           seconds=85, tags=["va:odd-sentence"]),
    VAItem(OS, "Four of the following five sentences form a coherent paragraph. Which one does NOT belong?\n\n"
               "1. Sourdough bread relies on wild yeasts rather than commercial ones.\n"
               "2. These yeasts live alongside bacteria that produce lactic acid.\n"
               "3. The acid gives the bread its characteristic sour flavour.\n"
               "4. It also slows staling, so the loaf keeps longer than most.\n"
               "5. Bread has been a staple food across Europe and Asia for thousands of years.",
           ["Sentence 5", "Sentence 2", "Sentence 3", "Sentence 4"],
           "Sentence 5",
           "Sentences 1 to 4 form a causal chain: wild yeasts, accompanying bacteria, the acid they "
           "produce, and its two effects. Sentence 5 is a broad historical statement about bread in "
           "general, at a different level of generality and connected to nothing in the chain.",
           seconds=85, tags=["va:odd-sentence"]),
]

# ---------------------------------------------------------------------------
# varc.va.para-completion
# ---------------------------------------------------------------------------

PC = "varc.va.para-completion"
_PC = [
    VAItem(PC, "Choose the sentence that best completes the paragraph:\n\n"
               "\"The policy failed on three counts: the funding arrived late, the training was never "
               "delivered, and the monitoring system was abandoned within a year. Each of these problems "
               "was foreseeable, and indeed foreseen — officials had raised all three in writing before "
               "the launch. ___\"",
           ["The question, then, is not why the policy failed but why those warnings were ignored.",
            "Similar policies have been attempted in several other countries.",
            "Late funding is a common problem in public administration.",
            "The policy was eventually replaced by a different scheme."],
           "The question, then, is not why the policy failed but why those warnings were ignored.",
           "The final given sentence sharpens the point: the failures were predicted in advance. The "
           "completion should follow that to its natural conclusion — the puzzle is now about the "
           "ignoring, not the failing. The other options change subject or restate a detail already made.",
           difficulty="hard", seconds=90, tags=["va:para-completion"]),
    VAItem(PC, "Choose the sentence that best completes the paragraph:\n\n"
               "\"For decades the standard treatment was prescribed to nearly every patient with the "
               "condition. Recent trials, however, show it helps only those with a particular genetic "
               "marker, and offers no benefit at all to the rest. ___\"",
           ["Testing for that marker should therefore precede any decision to prescribe.",
            "The condition affects roughly one in four hundred adults.",
            "Genetic testing has become considerably cheaper in recent years.",
            "The treatment was first developed in the 1960s."],
           "Testing for that marker should therefore precede any decision to prescribe.",
           "The paragraph establishes that the treatment works only for an identifiable subgroup. The "
           "completion that follows is the practical implication — test first. The others add background "
           "facts that the paragraph was not building towards.",
           difficulty="hard", seconds=90, tags=["va:para-completion"]),
    VAItem(PC, "Choose the sentence that best completes the paragraph:\n\n"
               "\"Translators have long argued about whether to render a text literally or freely. A "
               "literal version preserves the original's structure but can read awkwardly; a free one "
               "reads well but may drift from what was actually said. ___\"",
           ["Most working translators therefore treat the choice as a balance to be struck afresh in each passage.",
            "Translation has existed for as long as written language itself.",
            "Literal translation is clearly the more scholarly of the two approaches.",
            "Many great works of literature have never been translated at all."],
           "Most working translators therefore treat the choice as a balance to be struck afresh in each passage.",
           "The paragraph sets up a genuine two-sided tension, giving each side a cost. The completion "
           "must resolve that tension rather than pick a winner arbitrarily or change topic. Only the "
           "first does so; the third takes a side the paragraph deliberately left open.",
           difficulty="hard", seconds=90, tags=["va:para-completion"]),
    VAItem(PC, "Choose the sentence that best completes the paragraph:\n\n"
               "\"Early forecasts of electric vehicle adoption consistently underestimated it. Analysts "
               "assumed buyers would wait for battery costs to fall to parity with petrol engines. In "
               "fact, buyers responded to running costs and local emissions rules long before that point "
               "was reached. ___\"",
           ["The forecasts erred not in their cost projections but in their model of what buyers respond to.",
            "Battery costs have continued to fall steadily since those forecasts were made.",
            "Electric vehicles now account for a substantial share of new car sales.",
            "Petrol engines remain more common in commercial vehicles than in private cars."],
           "The forecasts erred not in their cost projections but in their model of what buyers respond to.",
           "The paragraph diagnoses a specific mistake: the analysts' assumption about buyer motivation, "
           "not their arithmetic. The completion names that diagnosis. The other options supply further "
           "facts without completing the argument the paragraph was making.",
           difficulty="very_hard", seconds=95, tags=["va:para-completion"]),
    VAItem(PC, "Choose the sentence that best completes the paragraph:\n\n"
               "\"Open-plan offices were introduced partly to encourage collaboration. Studies since have "
               "found that face-to-face interaction actually falls when partitions are removed, while "
               "written messaging rises sharply. Workers, it seems, create the privacy they need by other "
               "means. ___\"",
           ["Removing physical barriers does not remove the desire for them.",
            "Open-plan layouts also reduce the cost of office space per employee.",
            "Written messaging tools have improved considerably in recent years.",
            "Most large firms adopted open-plan layouts during the same period."],
           "Removing physical barriers does not remove the desire for them.",
           "The last given sentence observes that workers find other ways to get privacy. The completion "
           "should crystallise that insight, which the first option does. The others introduce cost, "
           "tooling or adoption history — none of which the paragraph was heading towards.",
           difficulty="hard", seconds=90, tags=["va:para-completion"]),
]

ALL_ITEMS = _SC + _FB + _CR + _PS + _OS + _PC


def verify(items: list[VAItem]) -> None:
    """Mechanical checks before anything is written. A verbal question cannot be
    machine-solved, but these catch the failure modes that actually occur in authoring:
    a mistyped answer that matches no option, duplicated options, and repeated stems."""
    seen_stems: set[str] = set()
    problems: list[str] = []
    for i, item in enumerate(items):
        if len(item.options) != 4:
            problems.append(f"[{item.mt} #{i}] has {len(item.options)} options, expected 4")
        if len(set(item.options)) != len(item.options):
            problems.append(f"[{item.mt} #{i}] has duplicate options")
        if item.options.count(item.answer) != 1:
            problems.append(f"[{item.mt} #{i}] answer is not present exactly once in options")
        if len(item.explanation) < 60:
            problems.append(f"[{item.mt} #{i}] explanation is too short to be useful")
        # Keyed on stem AND options: a shared stem like "Which sentence is correct?" is
        # legitimate across many items, but the same stem with the same options twice is a
        # genuine duplicate. This check first ran on the stem alone and correctly flagged all
        # 12 sentence-correction items -- which exposed the real bug that the id hash also
        # keyed on the stem alone, so they would have overwritten each other into one file.
        key = (item.mt, item.stem, tuple(item.options))
        if key in seen_stems:
            problems.append(f"[{item.mt} #{i}] duplicate stem and options")
        seen_stems.add(key)
    if problems:
        raise SystemExit("VA item verification failed:\n  " + "\n  ".join(problems))


def to_question(item: VAItem) -> Question:
    # Options are part of the hash, not just the stem: many sentence-correction items share
    # the identical stem and differ only in their options.
    h = hashlib.sha1(("|".join([item.mt, item.stem, *item.options])).encode()).hexdigest()[:10]
    return Question(
        id=f"{item.mt}.va-{h}",
        microTopicIds=[item.mt],
        section="VARC",
        format="mcq",
        stemMarkdown=item.stem,
        options=[QuestionOption(key=chr(65 + i), markdown=o) for i, o in enumerate(item.options)],
        correctKey=chr(65 + item.options.index(item.answer)),
        difficulty=item.difficulty,
        eloRating={"easy": 1050.0, "medium": 1200.0, "hard": 1350.0, "very_hard": 1500.0}[item.difficulty],
        solutionMarkdown=item.explanation,
        targetSeconds=item.seconds,
        source="generated",
        verification=VerificationRecord(method="human_reviewed", verifiedAt=VERIFIED_AT),
        tags=item.tags,
    )


def main() -> None:
    verify(ALL_ITEMS)
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    counts: dict[str, int] = {}
    for item in ALL_ITEMS:
        q = to_question(item)
        (QUESTIONS_DIR / f"{q.id}.json").write_text(
            json.dumps(json.loads(q.model_dump_json()), indent=2) + "\n")
        counts[item.mt] = counts.get(item.mt, 0) + 1
    for mt, n in sorted(counts.items()):
        print(f"{mt}: {n} questions")
    print(f"\nTotal: {len(ALL_ITEMS)} VARC/VA questions written.")


if __name__ == "__main__":
    main()
