"""VARC lessons. Reading and elimination technique rather than rules to memorise."""

from __future__ import annotations

from . import EX, FC, LessonSpec

_ELIMINATION = (
    "In VARC you almost never prove an option right. You prove three of them wrong. Options fail for "
    "recognisable reasons: they go further than the passage does, they are true in the world but not "
    "stated here, they get the right idea but the wrong scope, or they distort a small detail. Naming "
    "**why** an option is wrong is what separates a reliable eliminator from a guesser."
)

SPECS = [
    LessonSpec(
        mt="varc.rc.direct-detail",
        intuition=(
            "This is the closest VARC gets to a lookup. The answer is written in the passage, somewhere, and "
            "your job is to find the sentence and match it to an option.\n\n"
            "It sounds easy, which is exactly why people lose marks: they answer from memory of the passage "
            "instead of going back and reading the actual line."
        ),
        core=(
            "Locate first, then answer. Find the specific sentence that addresses the question and read it "
            "fully, including whatever comes just before and after — qualifications often sit in the "
            "neighbouring clause.\n\n"
            "The correct option is a **paraphrase** of that sentence, not a copy of it. Options that reuse the "
            "passage's exact words are often the trap, with one word quietly changed.\n\n"
            "Wrong options here typically overstate ('always' where the passage said 'often'), or attach the "
            "right fact to the wrong subject."
        ),
        examples=[
            EX(
                stem="A passage says: 'Coastal cities in the region have, in most years since 2010, recorded higher rainfall than inland ones.' Which option is supported?",
                solution=(
                    "The passage supports: 'Coastal cities usually received more rain than inland cities after 2010.'\n\n"
                    "It does **not** support 'Coastal cities always received more rain' — the passage said 'in "
                    "most years', not every year.\n\n"
                    "Nor does it support any claim about why, since the passage gives no cause."
                ),
                alt="The single word 'most' is what decides between the right and wrong options. Detail questions usually turn on one such word.",
            ),
        ],
        formulas=[
            FC(
                title="Locate before you answer",
                body="Find the exact sentence, read it with its neighbours, then match to an option. Never answer from memory of the passage.",
                example="A question about a date sends you back to the sentence with that date in it.",
            ),
            FC(
                title="Watch the quantifiers",
                body="'Most', 'some', 'often' and 'always' are not interchangeable. An option that upgrades the strength is wrong.",
                example="Passage 'many economists' does not support option 'economists agree'.",
            ),
        ],
        traps=[
            "Answering from memory rather than returning to the line.",
            "Choosing the option that repeats the passage's wording most closely, which is often the distortion.",
            "Missing a qualifier such as 'in most years' that limits the claim.",
        ],
        minutes=6,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.rc.vocab-in-context",
        intuition=(
            "The word 'bright' means one thing about a lamp and another about a student. Nobody needs a "
            "dictionary to tell them apart — the sentence around it does the work.\n\n"
            "Vocabulary-in-context questions test exactly that. They rarely use obscure words; they use "
            "ordinary words in a particular sense and check whether you read the sentence."
        ),
        core=(
            "Cover the word and read the sentence with a blank. Decide what would fit, in your own words, "
            "before looking at the options. This stops the options from steering you.\n\n"
            "Then find the option closest to your own guess. The correct answer must fit the sentence "
            "grammatically and carry the right tone — positive, negative or neutral — as well as the right "
            "meaning.\n\n"
            "The most common trap is an option that is a perfectly good dictionary synonym but wrong for "
            "**this** sentence."
        ),
        examples=[
            EX(
                stem="'The committee's decision was arresting, and delegates spoke of little else for days.' What does 'arresting' mean here?",
                solution=(
                    "Cover the word: 'The decision was ___, and delegates spoke of little else.'\n\n"
                    "Something that makes people talk for days is **striking** or attention-grabbing.\n\n"
                    "'Arresting' here means striking, not 'stopping' or 'detaining' — even though those are "
                    "its more common senses elsewhere."
                ),
                alt="The clue is entirely in the second half of the sentence. The literal police sense is the deliberate trap.",
            ),
        ],
        formulas=[
            FC(
                title="Blank-it-out method",
                body="Cover the word, predict a replacement from context, then match to the closest option.",
                example="Predicting 'striking' makes the right option obvious and the trap visible.",
            ),
            FC(
                title="Match the tone",
                body="The replacement must carry the same positive, negative or neutral charge as the original sentence implies.",
                example="A word describing criticism cannot be replaced with a complimentary synonym.",
            ),
        ],
        traps=[
            "Choosing the word's most common meaning rather than its meaning here.",
            "Picking a synonym that does not fit the sentence grammatically.",
            "Ignoring whether the sentence is approving or disapproving.",
        ],
        minutes=5,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.rc.structure-function",
        intuition=(
            "Ask not what a paragraph **says** but what it **does**. Is it introducing an idea, giving an "
            "example, raising an objection, or answering one?\n\n"
            "Think of a paragraph as a person in a conversation. Some people set the topic, some disagree, "
            "some give evidence, some summarise. The question is asking which role this one plays."
        ),
        core=(
            "Read the paragraph and describe its job in a short verb phrase: 'gives a counterexample', "
            "'explains the mechanism', 'concedes a limitation'.\n\n"
            "Connectives are the strongest clue. 'However' signals a turn against what came before; 'for "
            "instance' signals illustration; 'therefore' signals a conclusion drawn from earlier material.\n\n"
            "Note that a paragraph's function is about its **relationship to the passage**, not its content. "
            "Options describing what the paragraph says, accurately, can still be the wrong answer to a "
            "function question."
        ),
        examples=[
            EX(
                stem="A paragraph opens 'However, this account overlooks the role of migration...' What is its function?",
                solution=(
                    "'However' signals a turn against the preceding argument.\n\n"
                    "The paragraph's function is to **raise an objection** to the account just described, by "
                    "pointing to a factor it ignores.\n\n"
                    "An option saying it 'describes patterns of migration' might be factually accurate about "
                    "the content, but it misses the paragraph's role in the argument."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Describe the job, not the content",
                body="Summarise the paragraph as a verb phrase: introduces, illustrates, qualifies, refutes, concludes.",
                example="'Presents a counterexample' is a function; 'discusses rainfall in Kerala' is content.",
            ),
            FC(
                title="Connectives carry the signal",
                body="'However' and 'yet' turn; 'for example' illustrates; 'therefore' and 'thus' conclude; 'moreover' extends.",
                example="A paragraph starting 'Moreover' is adding support, not objecting.",
            ),
        ],
        traps=[
            "Choosing an accurate description of content when the question asked about function.",
            "Ignoring the opening connective, which usually gives the answer away.",
            "Judging the paragraph in isolation rather than by its relationship to what surrounds it.",
        ],
        minutes=6,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.rc.inference",
        intuition=(
            "If the passage says the streets are wet and people are shaking out umbrellas, you may infer it "
            "rained. You may **not** infer that it rained for three hours, or that a storm is coming.\n\n"
            "An inference is what must follow from what is written — one small step beyond the text, never a "
            "leap."
        ),
        core=(
            "The correct inference is the option that **must** be true given the passage, not the one that is "
            "most likely or most interesting.\n\n"
            "Test each option by asking: could the passage be entirely true while this option is false? If "
            "yes, it is not an inference.\n\n"
            "Correct answers to inference questions are usually cautiously worded — 'may', 'suggests', 'at "
            "least some'. Options with sweeping language are usually going a step too far, because a strong "
            "claim needs stronger support than most passages give."
        ),
        examples=[
            EX(
                stem="Passage: 'Every student who passed the exam had attended the revision class.' What can be inferred?",
                solution=(
                    "It follows that **a student who did not attend the revision class did not pass**. That is "
                    "just the original statement read backwards, and it must be true.\n\n"
                    "It does **not** follow that everyone who attended the class passed. Attending was "
                    "necessary, but the passage never says it was sufficient.\n\n"
                    "That distinction between necessary and sufficient is the heart of most inference questions."
                ),
                alt="'All P are Q' guarantees 'not Q means not P', but never 'all Q are P'.",
            ),
        ],
        formulas=[
            FC(
                title="Must be true, not could be",
                body="An inference is only correct if the passage cannot be true while the option is false.",
                example="'Sales rose' does not let you infer 'profits rose'.",
            ),
            FC(
                title="Necessary is not sufficient",
                body="'All P are Q' implies 'not Q means not P'. It does not imply 'all Q are P'.",
                example="All doctors studied medicine; that does not make every medicine student a doctor.",
            ),
        ],
        traps=[
            "Picking the most plausible real-world statement rather than what the passage forces.",
            "Reversing a conditional. 'All A are B' does not give 'all B are A'.",
            "Choosing a strongly worded option when the passage supports only a cautious one.",
        ],
        minutes=7,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.rc.tone-attitude",
        intuition=(
            "Two people can describe the same event and you can hear, from word choice alone, that one "
            "approves and the other does not. 'Frugal' and 'stingy' describe identical behaviour with "
            "opposite attitudes.\n\n"
            "Tone questions ask you to hear that. The information is carried by adjectives, verbs and the "
            "occasional aside, not by the facts themselves."
        ),
        core=(
            "First decide the simplest thing: is the author positive, negative, or neutral? That alone "
            "usually eliminates half the options.\n\n"
            "Then calibrate the strength. Most academic and editorial writing is measured — 'critical' or "
            "'sceptical' rather than 'furious' or 'contemptuous'. Extreme tone words are rarely correct "
            "because passages are rarely extreme.\n\n"
            "Watch for authors who present a view at length and then reject it. The tone belongs to the "
            "**author**, not to the view being reported."
        ),
        examples=[
            EX(
                stem="An author writes: 'The proposal is well intentioned, though its authors appear not to have consulted anyone who would live with its consequences.' What is the tone?",
                solution=(
                    "'Well intentioned' is mild praise, but the second clause is a pointed criticism.\n\n"
                    "The tone is **critical but measured** — something like 'qualified disapproval'.\n\n"
                    "It is not 'enthusiastic', and it is not 'scathing' either. The concession in the first "
                    "half rules out anything harsh."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Sign first, strength second",
                body="Decide positive, negative or neutral, then judge how strong. Most passages are moderate.",
                example="Between 'sceptical' and 'derisive', a measured passage takes 'sceptical'.",
            ),
            FC(
                title="The author is not the view",
                body="When a passage reports others' opinions, the tone is the author's attitude to them, not the opinions themselves.",
                example="An author explaining a theory at length may still be arguing against it.",
            ),
        ],
        traps=[
            "Choosing an extreme tone word for a moderately worded passage.",
            "Mistaking a reported opinion for the author's own.",
            "Reading a single strong word as the tone of the whole passage.",
        ],
        minutes=6,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.rc.assumption",
        intuition=(
            "'She must be at home, her car is in the driveway.' The unstated assumption is that she does not "
            "go anywhere without her car.\n\n"
            "An assumption is the missing plank the argument is standing on. The author never says it, but "
            "the argument collapses without it."
        ),
        core=(
            "Identify the conclusion, then the stated evidence, then ask what gap sits between them. The "
            "assumption is whatever bridges that gap.\n\n"
            "The **negation test** is the reliable check: negate the option and see whether the argument "
            "falls apart. If it does, that option was a necessary assumption. If the argument survives, it "
            "was not.\n\n"
            "Assumptions are usually modest, not grand. The correct answer often sounds obvious or barely "
            "worth saying, which is exactly what makes it an assumption rather than a claim."
        ),
        examples=[
            EX(
                stem="'The new bridge will reduce congestion, since it gives drivers a second route into the city.' What is assumed?",
                solution=(
                    "The argument assumes that **drivers will actually use the new route**.\n\n"
                    "Apply the negation test: if drivers do not use it, the bridge cannot reduce congestion "
                    "and the argument fails completely. So this is a necessary assumption.\n\n"
                    "By contrast, 'the bridge was expensive' can be negated without touching the argument, so "
                    "it is not an assumption."
                ),
                alt="A good assumption often feels too obvious to state. That is the point — it goes unsaid.",
            ),
        ],
        formulas=[
            FC(
                title="Find the gap",
                body="Separate the conclusion from the evidence. The assumption is whatever must be true to get from one to the other.",
                example="Evidence about a route plus a conclusion about congestion needs an assumption about usage.",
            ),
            FC(
                title="Negation test",
                body="Negate the option. If the argument collapses, it is a necessary assumption; if it survives, it is not.",
                example="Negating 'drivers will use it' destroys the conclusion, confirming it as the assumption.",
            ),
        ],
        traps=[
            "Choosing something that would strengthen the argument rather than something it requires.",
            "Picking a sweeping statement when the argument only needs a narrow one.",
            "Selecting a restatement of the conclusion instead of the gap beneath it.",
        ],
        minutes=7,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.rc.strengthen-weaken",
        intuition=(
            "An argument is a bridge from evidence to conclusion. To **strengthen** it, add support under the "
            "bridge. To **weaken** it, knock out a support or show the bridge leads somewhere else.\n\n"
            "Notice that weakening does not mean disproving. Making the conclusion less likely is enough."
        ),
        core=(
            "Find the conclusion first, precisely. Everything depends on knowing exactly what is being "
            "claimed.\n\n"
            "To weaken, look for an alternative explanation of the evidence, a case the argument did not "
            "consider, or a reason the evidence does not transfer to the conclusion's situation.\n\n"
            "To strengthen, rule out an alternative explanation, or supply the missing link.\n\n"
            "The most common wrong answer is relevant to the **topic** but not to the **argument**. Ask "
            "whether the option changes how likely the conclusion is; if not, it is out however interesting "
            "it sounds."
        ),
        examples=[
            EX(
                stem="'Sales rose after we changed the packaging, so the new packaging caused the increase.' What most weakens this?",
                solution=(
                    "The argument moves from a correlation in time to a cause. It is weakened most by an "
                    "**alternative explanation** for the rise.\n\n"
                    "For instance: 'A competitor withdrew from the market in the same month.'\n\n"
                    "That leaves the sales rise fully explained without the packaging, so the causal claim "
                    "loses its support — without anyone having to prove the packaging did nothing."
                ),
                alt="Most causal arguments in CAT are weakened the same way: something else could have caused the effect.",
            ),
        ],
        formulas=[
            FC(
                title="Weaken a causal claim",
                body="Offer another cause, show the effect happened without the cause, or show the cause happened without the effect.",
                example="A competitor leaving the market explains the sales rise without the packaging.",
            ),
            FC(
                title="Strengthen",
                body="Eliminate an alternative explanation, or supply the missing link between evidence and conclusion.",
                example="'No other market conditions changed that month' strengthens the packaging claim.",
            ),
        ],
        traps=[
            "Choosing an option on the right topic that does not affect the conclusion's likelihood.",
            "Expecting a weakener to disprove the conclusion. It only has to make it less likely.",
            "Losing track of the precise conclusion and attacking a different claim.",
        ],
        minutes=7,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.rc.except-least-likely",
        intuition=(
            "'All of the following are true EXCEPT' flips the whole exercise. Now three options are correct "
            "and you are hunting for the odd one out.\n\n"
            "The error people make is not misunderstanding the passage — it is forgetting halfway through "
            "that they are looking for the wrong one."
        ),
        core=(
            "Write a small 'NOT' on your page, or say it aloud. Some visible reminder that the polarity is "
            "reversed.\n\n"
            "Then work option by option, marking each as supported or not supported by the passage. Do not "
            "try to spot the answer directly — check all four and the odd one reveals itself.\n\n"
            "The answer is the option that is either contradicted by the passage or simply absent from it. "
            "Both count as 'except'; it does not have to be contradicted."
        ),
        examples=[
            EX(
                stem="'The passage supports all of the following EXCEPT:' — how should you work through it?",
                solution=(
                    "Mark each option individually:\n\n"
                    "Option A: find the supporting line. Supported.\n"
                    "Option B: find the supporting line. Supported.\n"
                    "Option C: no supporting line anywhere. **Not supported**.\n"
                    "Option D: find the supporting line. Supported.\n\n"
                    "C is the answer, because it is the one the passage does not support — even though "
                    "nothing in the passage contradicts it either."
                ),
                alt="Checking all four is slower but far safer than trying to spot the odd one at a glance.",
            ),
        ],
        formulas=[
            FC(
                title="Flag the reversal",
                body="Physically mark that the question is negative before reading the options.",
                example="Writing 'NOT' beside the question prevents the commonest error in this type.",
            ),
            FC(
                title="Check all four",
                body="Label each option supported or not. The answer is the one that stands alone.",
                example="Three ticks and one blank identifies the answer without guesswork.",
            ),
        ],
        traps=[
            "Forgetting the 'except' partway through and picking a supported option.",
            "Expecting the answer to be contradicted, when merely being unmentioned is enough.",
            "Stopping at the first option that looks odd instead of checking all four.",
        ],
        minutes=6,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.rc.analogy-application",
        intuition=(
            "The passage explains how a coral reef supports many species by providing structure. Now the "
            "question asks which of four unrelated situations is most similar.\n\n"
            "You are not matching the topic — reefs to reefs. You are matching the **shape** of the "
            "relationship: something providing structure that others depend on."
        ),
        core=(
            "Strip the passage's idea down to an abstract pattern, ignoring its subject matter entirely. "
            "'X enables Y by providing Z' or 'a small change produces a disproportionate effect'.\n\n"
            "Then test each option against that pattern, again ignoring subject matter. The correct option "
            "usually comes from a completely different domain, because superficial topic similarity is the "
            "trap.\n\n"
            "If two options seem to fit, the pattern was described too loosely. Sharpen it and test again."
        ),
        examples=[
            EX(
                stem="A passage describes how a keystone species keeps an ecosystem stable despite being small in number. Which is analogous?",
                solution=(
                    "The abstract pattern is: **a small component whose removal destabilises a much larger "
                    "system**.\n\n"
                    "An option about a small supplier whose failure halts an entire manufacturing chain fits "
                    "that pattern exactly, despite having nothing to do with ecology.\n\n"
                    "An option about a different animal species would look related but need not share the "
                    "pattern at all."
                ),
                alt="Same-topic options are usually decoys in analogy questions. Match structure, not subject.",
            ),
        ],
        formulas=[
            FC(
                title="Abstract the pattern",
                body="Restate the relationship without any subject-specific nouns, then test the options against that skeleton.",
                example="'Small part, disproportionate effect on the whole' is a testable skeleton.",
            ),
        ],
        traps=[
            "Matching the topic instead of the relationship.",
            "Describing the pattern too vaguely, so several options appear to fit.",
            "Ignoring the direction of the relationship, such as cause versus effect.",
        ],
        minutes=6,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.va.para-summary",
        intuition=(
            "Imagine a friend asks what a paragraph said and you have one sentence to tell them. You would "
            "give the main point — not the examples, not the aside in the middle.\n\n"
            "That is a summary. The commonest mistake is picking an option that repeats a striking detail "
            "instead of capturing the whole."
        ),
        core=(
            "Find the paragraph's central claim, then check that your chosen option covers **all** of it and "
            "nothing beyond it.\n\n"
            "Options fail in four recognisable ways. Too narrow: captures only one part. Too broad: says "
            "something more general than the paragraph supports. Distorted: changes an emphasis or a "
            "qualifier. Outside: introduces material the paragraph never mentioned.\n\n"
            "A summary must also preserve the paragraph's **relationships** — if the paragraph argued A "
            "despite B, a summary mentioning only A has lost the argument."
        ),
        examples=[
            EX(
                stem="A paragraph argues that microfinance helps some borrowers but that its benefits have been overstated by advocates. Which summary is best?",
                solution=(
                    "The best summary keeps **both** halves: microfinance has real but limited benefits that "
                    "have been exaggerated.\n\n"
                    "'Microfinance helps borrowers escape poverty' is too narrow and drops the criticism.\n\n"
                    "'Microfinance does not work' is a distortion — the paragraph said some borrowers do benefit.\n\n"
                    "Keeping the concession **and** the criticism is what makes a summary faithful."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Four ways an option fails",
                body="Too narrow, too broad, distorted, or introducing outside material. Name the failure for each rejected option.",
                example="An option covering only the first half of a two-part argument is too narrow.",
            ),
            FC(
                title="Preserve the relationship",
                body="If the paragraph concedes something and then objects, the summary must keep both parts.",
                example="'A, although B' cannot be summarised as just 'A'.",
            ),
        ],
        traps=[
            "Choosing an option built around the paragraph's most memorable example.",
            "Dropping a concession or qualifier that changes the paragraph's stance.",
            "Picking an option that is true but broader than what the paragraph argued.",
        ],
        minutes=6,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.va.odd-sentence-out",
        intuition=(
            "Four sentences belong to one paragraph and one has wandered in from somewhere else. It is "
            "usually on the same broad topic — otherwise it would be too easy — but it is doing a different "
            "job.\n\n"
            "The reliable move is to build the paragraph from the sentences that clearly link, and see which "
            "one is left holding nothing."
        ),
        core=(
            "First find the pairs. Pronouns, repeated nouns and connectives link sentences to each other: "
            "'this shift', 'such policies', 'however' all point back at something specific.\n\n"
            "Assemble the sentences that chain together into a coherent paragraph. The odd one is the "
            "sentence that no other sentence refers to and that refers to nothing itself.\n\n"
            "Being on the same topic is not enough to belong. The odd sentence often makes a general or "
            "definitional statement while the others are pursuing a specific argument."
        ),
        examples=[
            EX(
                stem="Three sentences trace how a city's transport policy changed after 2010. A fourth defines what public transport is. Which is the odd one?",
                solution=(
                    "The definitional sentence is the odd one.\n\n"
                    "The other three form a narrative chain about a specific city and a specific period, each "
                    "referring back to the previous one.\n\n"
                    "The definition is on the same topic but sits at a different level of generality and "
                    "connects to nothing in the sequence."
                ),
                alt="Same subject matter, different job — that mismatch is what marks the intruder.",
            ),
        ],
        formulas=[
            FC(
                title="Chain by reference",
                body="Track pronouns, repeated nouns and connectives. The odd sentence neither refers back nor is referred to.",
                example="'Such measures' must point at measures named in another sentence.",
            ),
            FC(
                title="Level of generality",
                body="A general or definitional sentence among specific, argumentative ones is usually the intruder.",
                example="A textbook definition among three sentences about one city's history does not belong.",
            ),
        ],
        traps=[
            "Removing a sentence just because it is the hardest to read.",
            "Assuming shared topic means it belongs.",
            "Failing to actually build the remaining paragraph and check it reads coherently.",
        ],
        minutes=6,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.va.para-completion",
        intuition=(
            "A paragraph has been cut off mid-thought and you must supply the ending. The right sentence "
            "finishes the journey the paragraph was already on — it does not start a new one.\n\n"
            "Read the paragraph and ask: where was this heading? The answer is usually visible in the last "
            "sentence before the gap."
        ),
        core=(
            "Pay closest attention to the final sentence given. It sets the direction, and the completion must "
            "continue it — resolving a tension, drawing the conclusion, or delivering the point the paragraph "
            "was building to.\n\n"
            "If the paragraph has been building a contrast, the ending usually lands on the second side of it. "
            "If it has been listing evidence, the ending usually states what the evidence shows.\n\n"
            "Reject options that introduce a genuinely new topic, that repeat something already said, or that "
            "contradict the paragraph's direction."
        ),
        examples=[
            EX(
                stem="A paragraph lists three failures of a policy and ends 'Each of these problems was foreseeable, and indeed foreseen.' What kind of completion fits?",
                solution=(
                    "The last sentence sharpens the criticism: the failures were predictable and predicted.\n\n"
                    "The completion should follow that to its conclusion — something about responsibility, or "
                    "why the warnings went unheeded.\n\n"
                    "An option introducing a new policy area would abandon the paragraph's direction, and an "
                    "option restating that the policy failed would add nothing."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Follow the last sentence",
                body="The sentence just before the gap sets the direction. The completion continues it rather than changing course.",
                example="A paragraph ending on an unanswered question should be completed with an answer.",
            ),
            FC(
                title="Reject new topics",
                body="A completion cannot introduce material the paragraph was not already heading towards.",
                example="Switching from transport policy to housing policy is a change of subject, not a completion.",
            ),
        ],
        traps=[
            "Choosing a broadly true statement that does not follow from this paragraph.",
            "Picking an option that restates a point already made.",
            "Ignoring the direction set by the final given sentence.",
        ],
        minutes=6,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.va.critical-reasoning",
        intuition=(
            "Someone says: 'Ice cream sales and drowning deaths both rise in July, so ice cream causes "
            "drowning.' The flaw is obvious once stated — hot weather drives both.\n\n"
            "Critical reasoning is the practice of spotting that kind of flaw when it is less obvious. Most "
            "flaws come from a small number of recurring patterns."
        ),
        core=(
            "Always separate **conclusion** from **evidence** first. Almost every question becomes easier once "
            "you can say precisely what is being claimed and what is offered in support.\n\n"
            "Then look for the standard flaws. Correlation treated as causation. A sample that does not "
            "represent the group. A conclusion about individuals drawn from a group average, or the reverse. "
            "An either-or framing that ignores other options. A term used in two different senses.\n\n"
            "Naming the flaw explicitly, in your own words, makes the right option much easier to recognise."
        ),
        examples=[
            EX(
                stem="'A survey of our website visitors found 90 percent prefer online shopping, so most people prefer online shopping.' What is the flaw?",
                solution=(
                    "Conclusion: most people prefer online shopping.\n"
                    "Evidence: 90 percent of **website visitors** said so.\n\n"
                    "The flaw is an unrepresentative sample. People who visit a shopping website are already "
                    "predisposed to shop online, so they cannot stand in for the general population.\n\n"
                    "This is selection bias, and it is one of the most frequently tested flaws."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Split conclusion from evidence",
                body="Identify what is claimed and what supports it before evaluating anything.",
                example="Marking the conclusion sentence makes the gap visible.",
            ),
            FC(
                title="Common flaws",
                body="Correlation as causation, unrepresentative sample, group-to-individual leaps, false dichotomy, shifting definitions.",
                example="A survey of a self-selected group cannot support a claim about everyone.",
            ),
        ],
        traps=[
            "Attacking the conclusion because you disagree with it, rather than assessing the reasoning.",
            "Choosing an option that is true but does not describe this argument's flaw.",
            "Missing that the evidence and the conclusion refer to different populations.",
        ],
        minutes=7,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.va.sentence-correction",
        intuition=(
            "'The list of items are on the table.' It sounds acceptable spoken aloud, but the subject is "
            "'list', which is singular, so it should be 'is'. The plural 'items' sitting next to the verb is "
            "what misleads the ear.\n\n"
            "Sentence correction rewards checking structure rather than trusting how a sentence sounds."
        ),
        core=(
            "Check a small number of things in order.\n\n"
            "**Subject-verb agreement**: find the true subject, ignoring any phrase sitting between it and "
            "the verb.\n"
            "**Pronoun reference**: every pronoun needs exactly one clear noun it refers to.\n"
            "**Modifier placement**: a describing phrase attaches to whatever it sits next to, which can "
            "produce nonsense.\n"
            "**Parallel structure**: items in a list must share a grammatical form.\n"
            "**Tense consistency**: shifts must be justified by the meaning.\n\n"
            "Where two options are both grammatical, prefer the clearer and shorter one."
        ),
        examples=[
            EX(
                stem="'Walking through the park, the flowers seemed especially bright.' What is wrong?",
                solution=(
                    "The opening phrase 'Walking through the park' attaches to whatever follows it — which "
                    "here is 'the flowers'. So the sentence literally says the flowers were walking.\n\n"
                    "This is a dangling modifier. It is fixed by naming the real walker:\n\n"
                    "'Walking through the park, I thought the flowers seemed especially bright.'"
                ),
                alt="Any sentence opening with an '-ing' phrase should be checked: whoever follows the comma must be the one doing it.",
            ),
        ],
        formulas=[
            FC(
                title="Find the real subject",
                body="Ignore phrases between the subject and verb. 'The list of items **is**', not 'are'.",
                example="'A box of chocolates was delivered' — the subject is 'box', not 'chocolates'.",
            ),
            FC(
                title="Parallel structure",
                body="Items in a list must take the same grammatical form.",
                example="'She likes reading, writing and to paint' should be 'reading, writing and painting'.",
            ),
            FC(
                title="Dangling modifiers",
                body="An opening descriptive phrase must describe the subject that immediately follows the comma.",
                example="'Having finished the report, the printer jammed' wrongly credits the printer.",
            ),
        ],
        traps=[
            "Trusting how a sentence sounds. Spoken English tolerates errors that written English does not.",
            "Being distracted by a plural noun sitting next to a singular subject.",
            "Choosing a wordier option when a shorter grammatical one is available.",
        ],
        minutes=7,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
    LessonSpec(
        mt="varc.va.fill-in-blanks",
        intuition=(
            "A sentence with a gap is a puzzle with a shape. The words around the gap tell you what kind of "
            "word belongs there — positive or negative, strong or mild, and what part of speech.\n\n"
            "As with vocabulary questions, guess before you look. Predicting your own word first makes the "
            "options much easier to judge."
        ),
        core=(
            "Read the whole sentence, not just the words touching the gap. The decisive clue is often at the "
            "far end.\n\n"
            "Watch the connectives closely. 'Although' and 'despite' signal contrast, so the blank opposes "
            "what came before. 'Because' and 'therefore' signal agreement, so it continues.\n\n"
            "With two blanks, solve the easier one first and use it to eliminate. Any option whose first word "
            "fails is out regardless of how well the second word fits — you do not need to evaluate both."
        ),
        examples=[
            EX(
                stem="'Although the team had prepared thoroughly, their performance was ___.' What kind of word fits?",
                solution=(
                    "'Although' sets up a contrast, so the second half must go against what thorough "
                    "preparation would predict.\n\n"
                    "Thorough preparation predicts a good performance, so the blank needs something negative: "
                    "'disappointing', 'lacklustre', 'poor'.\n\n"
                    "Anything positive would break the contrast the sentence explicitly announced."
                ),
                alt="The single word 'Although' determines the sign of the answer before any option is read.",
            ),
        ],
        formulas=[
            FC(
                title="Predict before you look",
                body="Decide what the blank needs in your own words, then find the closest option.",
                example="Predicting 'disappointing' makes the correct option obvious.",
            ),
            FC(
                title="Connectives set the direction",
                body="'Although', 'despite', 'yet' reverse direction. 'Because', 'therefore', 'moreover' continue it.",
                example="'Because he had prepared, his performance was ___' needs a positive word.",
            ),
            FC(
                title="Two blanks: eliminate on the easier one",
                body="Solve whichever blank is more constrained and discard every option that fails it.",
                example="If only two options have a workable first word, only those two need checking.",
            ),
        ],
        traps=[
            "Reading only the words immediately around the gap.",
            "Missing a contrast connective and choosing a word with the wrong sign.",
            "Evaluating both blanks in every option instead of eliminating on one.",
        ],
        minutes=6,
        extra_sections=[("How elimination works in VARC", _ELIMINATION)],
    ),
]
