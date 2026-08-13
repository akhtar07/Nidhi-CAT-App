"""
The final two lessons that had JSON on disk but no declaration in this package.

With these, `build_lessons` writes all 86 and there is no lesson in /content that cannot be
reproduced from source.
"""

from __future__ import annotations

from . import EX, FC, LessonSpec, Method

SPECS = [
    LessonSpec(
        mt="varc.rc.main-idea",
        prereq="Nothing technical. The skill is holding a whole passage in view rather than the last thing you read.",
        intuition=(
            "Imagine a friend asks what a book was about and you have thirty seconds. You would not "
            "recite the third chapter, however interesting it was — you would say what the book was "
            "**for**.\n\n"
            "That is a main-idea question. Wrong options are almost never false; they are true "
            "things the passage happens to say. A detail from paragraph two can be perfectly "
            "accurate and still be the wrong answer, because it is not what the passage is about.\n\n"
            "So the test is not 'is this true?' — it will be. The test is 'does the whole passage "
            "exist to say this?'"
        ),
        core=(
            "A CAT passage usually has one central claim, and the paragraphs around it do jobs: "
            "setting up, illustrating, qualifying, countering. If you can say in one sentence what "
            "the author is arguing, and what the paragraphs are doing to support that, you can "
            "answer nearly every main-idea question without re-reading.\n\n"
            "Two structural habits pay for themselves.\n\n"
            "**Watch the turn.** Most argumentative passages pivot somewhere, often on 'however', "
            "'yet' or 'but'. The main idea sits **after** the turn, not before it — the material "
            "before it is usually the position being corrected. Answering from the opening "
            "paragraph is the most common way to get these wrong.\n\n"
            "**Match the scope.** The right answer covers the whole passage and no more. Too "
            "narrow, and it describes one paragraph; too broad, and it claims something the "
            "passage never reaches."
        ),
        methods=[
            Method(
                name="Stating the main idea before reading options",
                recognise="'the primary purpose', 'the passage is mainly concerned with', 'the best title'.",
                steps=[
                    "Say the passage's point in one sentence, in your own words, before looking at the options.",
                    "Find the option closest to your sentence.",
                    "Predicting first stops the options from talking you into a plausible detail.",
                ],
                worked="If your sentence is 'urban planners have overestimated the value of density', the answer will echo that, not the density statistics.",
            ),
            Method(
                name="Locating the turn",
                recognise="a passage that opens by describing a widely-held view.",
                steps=[
                    "Look for 'however', 'yet', 'but', 'in fact' — usually near the start of the second or third paragraph.",
                    "The author's own position is what follows the turn.",
                    "The opening view is what the author is arguing against, so an option restating it is wrong.",
                ],
                worked="A passage opening 'It is widely believed that X' and turning to 'Yet the evidence suggests otherwise' is about the otherwise.",
            ),
            Method(
                name="Testing scope",
                recognise="two options that both sound like reasonable summaries.",
                steps=[
                    "Ask of each: does the passage support this **and** does it support all of it?",
                    "An option is too narrow if a whole paragraph is left unaccounted for.",
                    "It is too broad if you can imagine a passage twice as long being needed to justify it.",
                ],
                worked="For a passage on one city's transport policy, 'transport policy fails in developing economies' is too broad.",
            ),
            Method(
                name="Choosing a title",
                recognise="'the most appropriate title for the passage'.",
                steps=[
                    "A title must cover the passage's whole span, like a main-idea answer.",
                    "Prefer the one naming the passage's tension or argument over the one naming its subject.",
                ],
                worked="'The Hidden Cost of Density' beats 'Urban Density' when the passage argues rather than describes.",
            ),
        ],
        examples=[
            EX(
                stem=(
                    "A passage argues that microfinance was widely praised for reducing poverty, then "
                    "presents studies showing consumption rose but incomes did not, and closes by saying "
                    "the programmes should be judged on what they actually deliver. Which option is the "
                    "main idea?"
                ),
                solution=(
                    "Locate the turn first. The passage opens with the praise — that is the view being "
                    "examined, not the author's position.\n\n"
                    "The evidence paragraph and the closing sentence both push the same way: the "
                    "programmes have been credited with something the evidence does not show.\n\n"
                    "So the main idea is roughly **microfinance's reputation outruns its measured "
                    "effects**.\n\n"
                    "An option about consumption rising is a true detail from the middle of the "
                    "passage, and it is the trap. An option saying microfinance should be abandoned "
                    "goes further than the passage, which asks for honest judgement, not abolition."
                ),
                alt=(
                    "Notice the two failure modes sitting side by side: one option too narrow (a "
                    "detail), one too strong (a recommendation the author never makes). Most "
                    "main-idea questions are built from exactly this pair."
                ),
            ),
        ],
        formulas=[
            FC(
                title="The one-sentence test",
                body="State the passage's point in your own words before reading options, then match.",
                example="Your sentence acts as a filter the plausible details cannot pass.",
            ),
            FC(
                title="After the turn",
                body="The author's position follows 'however', 'yet' or 'but' — the opening view is usually the one being corrected.",
                example="'It is widely assumed... Yet...' means the answer lies after the Yet.",
            ),
            FC(
                title="Scope check",
                body="The right answer covers the whole passage and nothing beyond it.",
                example="A summary that leaves a paragraph unexplained is too narrow.",
            ),
        ],
        traps=[
            "Choosing a true detail. Wrong options in this question type are usually accurate but not central.",
            "Answering from the first paragraph when the passage turns against it later.",
            "Picking the option with the most familiar-sounding vocabulary rather than the right scope.",
            "Choosing a recommendation when the author only diagnoses.",
            "Reading only the first and last sentences. It works often enough to be a dangerous habit and fails on exactly the passages that carry the hardest questions.",
        ],
        checklist=[
            "State a passage's point in one sentence without looking at the options.",
            "Find the turn and know which side of it the author is on.",
            "Reject options for being too narrow or too broad, and say which.",
            "Pick a title that captures the argument rather than the subject.",
        ],
        minutes=9,
    ),
    LessonSpec(
        mt="varc.va.para-jumbles",
        prereq="An ear for how one sentence hands off to the next.",
        intuition=(
            "Sentences leave fingerprints on each other. 'This decision' can only follow a sentence "
            "that mentioned a decision. 'However' can only follow something to push against. 'The "
            "empire' can only follow a sentence that has already told you which empire.\n\n"
            "So a jumble is not a puzzle about meaning — it is a puzzle about **references**. You "
            "are not asked which order reads most pleasantly; you are asked which order is the only "
            "one where every backward-pointing word has something to point at.\n\n"
            "This is why the reliable method never starts with 'which sentence feels like the "
            "beginning?'. It starts with 'which sentences are welded to each other?', because those "
            "welds are facts, and feelings are not."
        ),
        core=(
            "Work in three stages, in this order.\n\n"
            "**Find a valid opener.** The first sentence cannot refer backwards. It introduces its "
            "subject in full — a name rather than a pronoun, a noun phrase rather than 'this' or "
            "'such' — and carries no connective like 'however', 'therefore' or 'moreover'. Often two "
            "sentences pass this test, which is fine; hold both.\n\n"
            "**Build mandatory pairs.** Every pronoun must have an antecedent, and it must come "
            "earlier. Every 'however' needs a claim to contrast with. Every 'for example' needs a "
            "generalisation above it. Each of these fixes an order between two sentences, and those "
            "fixed orders are the only hard information in the question.\n\n"
            "**Assemble and read back.** Place the opener, attach the blocks, and then read the "
            "paragraph straight through. A wrong order almost always sounds wrong at one identifiable "
            "join rather than being vaguely unsatisfying — and if you can name the join, you can fix "
            "it.\n\n"
            "A last check that catches a surprising number of errors: the final sentence should "
            "close something. If your last sentence opens a new idea, the order is wrong."
        ),
        methods=[
            Method(
                name="Identifying the opening sentence",
                recognise="the first move in every jumble.",
                steps=[
                    "Rule out any sentence containing a backward reference: 'this', 'such', 'these', 'it' with no antecedent.",
                    "Rule out any sentence starting with a connective — 'however', 'therefore', 'moreover', 'consequently'.",
                    "What remains introduces its subject in full. If two survive, keep both and let the pairs decide.",
                ],
                worked="'The Mughal empire expanded rapidly' can open; 'This expansion had costs' cannot.",
            ),
            Method(
                name="Fixing mandatory pairs",
                recognise="a pronoun, a repeated noun, or a connective linking two sentences.",
                steps=[
                    "Match each pronoun to the sentence naming what it refers to; that sentence must come first.",
                    "Treat contrast, cause and chronology markers the same way.",
                    "Note that a pair fixes only the order of those two, not their position in the paragraph.",
                ],
                worked="'It' referring to a treaty must follow the sentence naming the treaty.",
            ),
            Method(
                name="Using the definite article as a signal",
                recognise="the same noun appearing with 'a' in one sentence and 'the' in another.",
                steps=[
                    "English introduces a thing with 'a' and refers back to it with 'the'.",
                    "So the sentence with 'a scheme' comes before the sentence with 'the scheme'.",
                    "This is one of the most reliable ordering clues and one of the most often missed.",
                ],
                worked="'A committee was formed' precedes 'The committee reported in March'.",
            ),
            Method(
                name="Assembling and checking the ending",
                recognise="you have blocks and need a single order.",
                steps=[
                    "Place the opener, attach each block by its link, and read the whole paragraph through.",
                    "If a join needs a connective the sentence does not have, the order is wrong there.",
                    "Confirm the last sentence concludes rather than raising something new.",
                ],
                worked="A paragraph ending 'But this raises a further question' is almost certainly mis-ordered.",
            ),
        ],
        examples=[
            EX(
                stem=(
                    "Order these four sentences.\n\n"
                    "(1) The scheme was quietly withdrawn two years later.\n"
                    "(2) A subsidy scheme for rural solar panels was announced in 2019.\n"
                    "(3) However, uptake remained far below the government's projections.\n"
                    "(4) It had been expected to reach two million households."
                ),
                solution=(
                    "Start with the opener test. Sentence 3 begins with 'However' and sentence 1 says "
                    "'The scheme', both backward references. Sentence 4 begins with 'It', which needs "
                    "an antecedent. Only **2** introduces its subject in full — 'A subsidy scheme' — "
                    "so 2 opens.\n\n"
                    "Now the pairs. Sentence 4's 'It' refers to the scheme, so 4 follows 2. The "
                    "indefinite-to-definite signal agrees: 'A subsidy scheme' in 2, 'The scheme' in 1, "
                    "so 2 comes before 1.\n\n"
                    "Sentence 3's 'However' must contrast with an expectation. Sentence 4 states the "
                    "expectation, so 3 follows 4.\n\n"
                    "Sentence 1 reports the outcome, which follows the disappointing uptake.\n\n"
                    "Order: **2, 4, 3, 1**."
                ),
                alt=(
                    "Read it back: a scheme is announced, it was expected to reach two million, "
                    "however uptake was low, so it was withdrawn. Every join carries its own signal, "
                    "and the paragraph ends on a conclusion rather than a new idea — both checks pass."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Valid opener",
                body="No pronoun without an antecedent, no back-referring 'this' or 'such', no opening connective.",
                example="'However, the plan failed' can never be first.",
            ),
            FC(
                title="Mandatory pair",
                body="A pronoun, or a connective needing something to attach to, fixes the order of two sentences.",
                example="'They objected' must follow the sentence naming who they are.",
            ),
            FC(
                title="A before The",
                body="A noun introduced with 'a' precedes the sentence referring to it with 'the'.",
                example="'A report' comes before 'The report'.",
            ),
            FC(
                title="Ending check",
                body="The final sentence should close the paragraph, not open a new line of thought.",
                example="An ending that raises a fresh question usually signals a wrong order.",
            ),
        ],
        traps=[
            "Choosing an order because it reads pleasantly, rather than because the references demand it.",
            "Missing that a sentence beginning with a pronoun cannot be first, however natural it sounds.",
            "Ignoring the 'a' to 'the' shift, which is often the only clue distinguishing two candidate orders.",
            "Fixing a pair correctly and then placing the pair at the wrong point in the paragraph — a pair fixes relative order only.",
            "Not reading the assembled paragraph back. The check takes fifteen seconds and catches most errors.",
        ],
        checklist=[
            "Eliminate impossible openers on sight.",
            "Fix every pair the pronouns and connectives demand.",
            "Use the indefinite-to-definite article shift.",
            "Read the finished paragraph back and check the ending closes it.",
        ],
        minutes=9,
    ),
]
