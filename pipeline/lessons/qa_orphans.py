"""
The last six lessons that had JSON on disk but no declaration anywhere in this package.

Same problem as the five in qa_arith_core.py: they could not be rebuilt, could not be checked
by `check_markdown`, and would have silently drifted from every other lesson's house style.
Declaring them here closes that gap — after this, `build_lessons` writes all 86, and there is
no lesson in /content that this package cannot reproduce.

Two of them are VARC, which is why the module is not named for a QA area.
"""

from __future__ import annotations

from . import EX, FC, LessonSpec, Method

SPECS = [
    LessonSpec(
        mt="qa.algebra.progressions",
        prereq="Nothing beyond arithmetic. If you can continue the pattern 3, 7, 11, 15 you already have the idea.",
        intuition=(
            "Two ways of walking up a staircase.\n\n"
            "In an **arithmetic progression** every step is the same height. You add a fixed "
            "amount each time: 5, 8, 11, 14, adding 3 over and over. Plot it and you get a "
            "straight line, because the rise never changes.\n\n"
            "In a **geometric progression** every step multiplies. You double, or halve, or "
            "triple: 3, 6, 12, 24. Plot it and the line bends upwards sharply, because each step "
            "is bigger than the last — this is the same shape as compound interest, and for the "
            "same reason.\n\n"
            "So the first question to ask of any sequence is: to get from one term to the next, "
            "am I **adding** something or **multiplying** by something? Everything else follows "
            "from the answer."
        ),
        core=(
            "An AP is fixed by two numbers: the first term $a$ and the common difference $d$. "
            "The $n$th term is $a + (n-1)d$ — note the $n - 1$, because you take the step "
            "**between** terms, and there are one fewer gaps than terms. Off-by-one errors here "
            "are the most common mistake in the topic.\n\n"
            "For the sum of an AP there is a lovely argument. Write the series forwards, write it "
            "again backwards underneath, and add the two columns: every column gives the same "
            "total, first plus last. There are $n$ columns and you counted everything twice, so\n\n"
            "$$S_n = \\frac{n}{2}(\\text{first} + \\text{last})$$\n\n"
            "A GP is fixed by the first term $a$ and the common ratio $r$, with $n$th term "
            "$ar^{n-1}$. Its sum is $\\dfrac{a(r^n - 1)}{r - 1}$.\n\n"
            "When $|r| < 1$ the terms shrink towards nothing fast enough that an infinite GP has "
            "a finite total, $\\dfrac{a}{1 - r}$. This is genuinely surprising the first time — "
            "adding infinitely many positive numbers and getting a finite answer — but "
            "$\\tfrac12 + \\tfrac14 + \\tfrac18 + \\cdots = 1$ makes it concrete: each step "
            "covers half the remaining distance to 1, so you approach 1 without ever passing it."
        ),
        methods=[
            Method(
                name="The nth term of an AP",
                recognise="a sequence with a constant difference, asking for a particular term.",
                steps=[
                    "Find $a$ and $d$ by subtracting consecutive terms.",
                    "Apply $t_n = a + (n-1)d$.",
                    "Count the gaps, not the terms — that is where the $n-1$ comes from.",
                ],
                worked="For 5, 8, 11, ... the 20th term is $5 + 19 \\times 3 = 62$.",
            ),
            Method(
                name="The sum of an AP",
                recognise="'find the sum of the first n terms', or a total of evenly spaced values.",
                steps=[
                    "Find the last term first, if it is not given.",
                    "Apply $S_n = \\dfrac{n}{2}(\\text{first} + \\text{last})$.",
                    "Equivalently $\\dfrac{n}{2}[2a + (n-1)d]$, which avoids computing the last term separately.",
                ],
                worked="The first 20 terms of 5, 8, 11, ... sum to $\\dfrac{20}{2}(5 + 62) = 670$.",
            ),
            Method(
                name="The nth term and sum of a GP",
                recognise="a constant ratio between consecutive terms.",
                steps=[
                    "Find $r$ by dividing any term by the one before it.",
                    "Use $t_n = ar^{n-1}$, and $S_n = \\dfrac{a(r^n - 1)}{r - 1}$.",
                    "For $r < 1$ it is tidier to write $\\dfrac{a(1 - r^n)}{1 - r}$ so both parts stay positive.",
                ],
                worked="For 3, 6, 12, ... the 8th term is $3 \\times 2^7 = 384$ and the sum of eight terms is $3(2^8 - 1) = 765$.",
            ),
            Method(
                name="Sum of an infinite GP",
                recognise="'sum to infinity', or a series that clearly shrinks towards zero.",
                steps=[
                    "Check that $|r| < 1$. If not, the series has no finite sum and that is the answer.",
                    "Apply $S_\\infty = \\dfrac{a}{1 - r}$.",
                ],
                worked="$8 + 4 + 2 + \\cdots$ has $a = 8$ and $r = \\dfrac{1}{2}$, so the sum is $\\dfrac{8}{0.5} = 16$.",
            ),
            Method(
                name="Finding a missing term or the number of terms",
                recognise="the sum or a particular term is given and $n$, $a$ or $d$ is wanted.",
                steps=[
                    "Write the relevant formula with the unknown left as a letter.",
                    "Substitute everything you know and solve.",
                    "If solving gives a non-integer $n$, you have made an arithmetic slip — the number of terms must be a whole number.",
                ],
                worked="If $a = 4$, $d = 5$ and $t_n = 79$, then $4 + 5(n-1) = 79$ gives $n = 16$.",
            ),
        ],
        examples=[
            EX(
                stem="Find the sum of all the multiples of 7 between 100 and 300.",
                solution=(
                    "First find where the sequence starts and stops.\n\n"
                    "The first multiple of 7 above 100 is $105 = 7 \\times 15$, and the last below "
                    "300 is $294 = 7 \\times 42$.\n\n"
                    "So the terms run from $7 \\times 15$ to $7 \\times 42$, which is "
                    "$42 - 15 + 1 = 28$ terms.\n\n"
                    "$S = \\dfrac{28}{2}(105 + 294) = 14 \\times 399 = 5586$."
                ),
                alt=(
                    "Factor the 7 out instead: the sum is $7(15 + 16 + \\cdots + 42)$, and the "
                    "bracket is $\\dfrac{28}{2}(15 + 42) = 798$, giving "
                    "$7 \\times 798 = 5586$. Smaller numbers, same answer."
                ),
            ),
            EX(
                stem="The third term of an AP is 14 and the seventh is 30. Find the first term and the sum of the first ten terms.",
                solution=(
                    "The gap from the third term to the seventh is four steps of $d$:\n\n"
                    "$30 - 14 = 4d$, so $d = 4$.\n\n"
                    "Work back from the third term by two steps: "
                    "$a = 14 - 2 \\times 4 = 6$.\n\n"
                    "The tenth term is $6 + 9 \\times 4 = 42$, so\n\n"
                    "$S_{10} = \\dfrac{10}{2}(6 + 42) = 5 \\times 48 = 240$."
                ),
                alt=(
                    "Counting the gaps is what makes this quick: from the 3rd to the 7th term is "
                    "$7 - 3 = 4$ gaps, not 5 terms. Any two terms of an AP give $d$ immediately "
                    "this way, without setting up simultaneous equations."
                ),
            ),
            EX(
                stem="A ball is dropped from 16 metres and rebounds to half its previous height each bounce. Find the total vertical distance it travels before coming to rest.",
                solution=(
                    "The first drop is 16 m. After that, every bounce is travelled twice — up and "
                    "then down again.\n\n"
                    "The upward distances form an infinite GP: $8, 4, 2, \\ldots$ with $a = 8$ and "
                    "$r = \\dfrac{1}{2}$.\n\n"
                    "That sums to $\\dfrac{8}{1 - 0.5} = 16$ metres, and the same 16 metres is "
                    "travelled coming back down.\n\n"
                    "Total $= 16 + 16 + 16 = 48$ metres."
                ),
                alt=(
                    "The trap is counting the first drop twice, or forgetting that every rebound "
                    "contributes its height twice. Draw the first three bounces and label each "
                    "arrow before summing anything."
                ),
            ),
        ],
        formulas=[
            FC(
                title="AP: nth term",
                body="$t_n = a + (n-1)d$",
                example="$a = 5$, $d = 3$ gives $t_{10} = 5 + 27 = 32$.",
            ),
            FC(
                title="AP: sum",
                body="$S_n = \\dfrac{n}{2}(\\text{first} + \\text{last}) = \\dfrac{n}{2}[2a + (n-1)d]$",
                example="Ten terms from 5 with $d = 3$ sum to $\\dfrac{10}{2}(5 + 32) = 185$.",
            ),
            FC(
                title="GP: nth term and sum",
                body="$t_n = ar^{n-1}$ and $S_n = \\dfrac{a(r^n - 1)}{r - 1}$",
                example="$a = 3$, $r = 2$, $n = 5$ gives $S_5 = 3 \\times 31 = 93$.",
            ),
            FC(
                title="Infinite GP",
                body="$S_\\infty = \\dfrac{a}{1 - r}$, valid only when $|r| < 1$.",
                example="$9 + 3 + 1 + \\cdots$ sums to $\\dfrac{9}{1 - 1/3} = 13.5$.",
            ),
            FC(
                title="Arithmetic mean of an AP",
                body="For evenly spaced terms the average is the midpoint of the first and last.",
                example="The terms from 5 to 32 average $\\dfrac{5 + 32}{2} = 18.5$.",
            ),
        ],
        traps=[
            "Using $n$ instead of $n - 1$ in the nth-term formula. Count gaps, not terms.",
            "Assuming a sequence is an AP because the first two gaps happen to match. Check a third.",
            "Applying the infinite-sum formula when the ratio is 1 or more — there is no finite sum then.",
            "Forgetting that a bouncing-ball distance counts each rebound twice.",
            "Getting a fractional number of terms and not treating it as a signal that something is wrong.",
        ],
        checklist=[
            "Decide whether a sequence is arithmetic, geometric, or neither.",
            "Find any term and any sum for both kinds.",
            "Get $d$ from any two terms by counting the gaps between them.",
            "Recognise when an infinite GP converges, and when it does not.",
        ],
        minutes=11,
    ),
    LessonSpec(
        mt="qa.modern.permutations-combinations",
        prereq="Multiplication, and factorial notation — $5!$ just means $5 \\times 4 \\times 3 \\times 2 \\times 1$.",
        intuition=(
            "One question separates every problem in this topic: **does the order matter?**\n\n"
            "Picture picking three people from a group of ten. If you are choosing a president, a "
            "secretary and a treasurer, then Asha-Ben-Chandra is a different outcome from "
            "Ben-Asha-Chandra — the same three people, different jobs. Order matters, and that is "
            "a **permutation**.\n\n"
            "If instead you are choosing three people to form a committee with no titles, then "
            "those two outcomes are the same committee. Order does not matter, and that is a "
            "**combination**.\n\n"
            "There are always more permutations than combinations, because each combination can "
            "be shuffled into several orders. Precisely: each group of $r$ people can be arranged "
            "in $r!$ ways, which is exactly the factor between the two formulas."
        ),
        core=(
            "The whole topic rests on one principle: if a first choice can be made in $m$ ways "
            "and a second in $n$ ways, the pair can be made in $m \\times n$ ways. Multiply "
            "independent choices; add mutually exclusive cases.\n\n"
            "From that, arranging $r$ objects out of $n$ distinct ones: the first slot has $n$ "
            "candidates, the next $n-1$, and so on for $r$ slots. That product is "
            "$^nP_r = \\dfrac{n!}{(n-r)!}$.\n\n"
            "For a selection where order is irrelevant, take the permutations and divide out the "
            "$r!$ orderings you have counted more than once:\n\n"
            "$$^nC_r = \\frac{n!}{r!\\,(n-r)!}$$\n\n"
            "Two facts worth having in your fingers. First, $^nC_r = {}^nC_{n-r}$ — choosing 8 of "
            "10 to take is the same as choosing 2 to leave behind, and the second sum is much "
            "less work. Second, when items repeat, divide by the factorial of each repeat count: "
            "the letters of LEVEL arrange in $\\dfrac{5!}{2!\\,2!}$ ways, because swapping the "
            "two Ls, or the two Es, does not make a new word."
        ),
        methods=[
            Method(
                name="Choosing a committee",
                recognise="a group selected with no roles or ordering.",
                steps=[
                    "Use $^nC_r$.",
                    "If the group must contain specified numbers from different pools, multiply the choices for each pool.",
                    "Use the symmetry $^nC_r = {}^nC_{n-r}$ to keep the arithmetic small.",
                ],
                worked="Choosing 3 from 5 men and 2 from 4 women gives $\\binom{5}{3}\\binom{4}{2} = 10 \\times 6 = 60$.",
            ),
            Method(
                name="Arranging distinct objects",
                recognise="a queue, a photograph, a seating row, or a set of ranked positions.",
                steps=[
                    "All $n$ objects in a row: $n!$.",
                    "Only $r$ of them: $^nP_r$.",
                    "If some objects must sit together, glue them into one block, arrange the blocks, then arrange within the block.",
                ],
                worked="Five people in a row with two insisting on adjacency: $4! \\times 2! = 48$.",
            ),
            Method(
                name="Arrangements with repeated items",
                recognise="a word with repeated letters, or identical objects among distinct ones.",
                steps=[
                    "Start with $n!$ for all positions.",
                    "Divide by $k!$ for each group of $k$ identical items.",
                ],
                worked="BANANA has 6 letters with three As and two Ns: $\\dfrac{6!}{3!\\,2!} = 60$.",
            ),
            Method(
                name="At least / at most conditions",
                recognise="'at least one', 'at most two', or a condition that splits into cases.",
                steps=[
                    "For 'at least one', it is usually far quicker to count the total and subtract the 'none' case.",
                    "Otherwise split into disjoint cases and add them.",
                    "Check the cases do not overlap and do not leave a gap.",
                ],
                worked="At least one woman on a committee of 3 from 5 men and 4 women: $\\binom{9}{3} - \\binom{5}{3} = 84 - 10 = 74$.",
            ),
            Method(
                name="Circular arrangements",
                recognise="people around a round table, or beads in a ring.",
                steps=[
                    "Fix one person to kill the rotational symmetry, leaving $(n-1)!$ arrangements.",
                    "If the arrangement can also be flipped over — a necklace rather than a table — halve it again.",
                ],
                worked="Six people round a table: $5! = 120$ ways.",
            ),
        ],
        examples=[
            EX(
                stem="In how many ways can a committee of 4 be formed from 7 men and 5 women, if it must contain at least 3 women?",
                solution=(
                    "'At least 3 women' from a committee of 4 splits into exactly two disjoint "
                    "cases: 3 women, or 4 women.\n\n"
                    "**Three women and one man:** "
                    "$\\binom{5}{3} \\times \\binom{7}{1} = 10 \\times 7 = 70$.\n\n"
                    "**Four women and no man:** "
                    "$\\binom{5}{4} \\times \\binom{7}{0} = 5 \\times 1 = 5$.\n\n"
                    "The cases cannot both happen, so add them: $70 + 5 = 75$ ways."
                ),
                alt=(
                    "Adding rather than multiplying here is the point. Multiply when choices "
                    "happen together (women **and** men in one committee); add when they are "
                    "alternatives (3 women **or** 4 women)."
                ),
            ),
            EX(
                stem="How many different words can be formed using all the letters of the word MISSISSIPPI?",
                solution=(
                    "Count the letters first: 11 in total, made of one M, four Is, four Ss and "
                    "two Ps.\n\n"
                    "If every letter were distinct there would be $11!$ arrangements. But swapping "
                    "the four Is changes nothing, and likewise for the Ss and the Ps, so divide "
                    "by each repeat count's factorial:\n\n"
                    "$\\dfrac{11!}{4!\\,4!\\,2!} = \\dfrac{39916800}{24 \\times 24 \\times 2} = 34650$\n\n"
                    "So there are **34650** distinct arrangements."
                ),
                alt=(
                    "Sanity check the letter count before anything else — miscounting the Is or "
                    "Ss is far more common than getting the formula wrong, and it is silent."
                ),
            ),
            EX(
                stem="In how many ways can 5 boys and 3 girls sit in a row so that no two girls sit together?",
                solution=(
                    "Seat the boys first, then slot the girls into the gaps between them.\n\n"
                    "The 5 boys can be arranged in $5! = 120$ ways.\n\n"
                    "That creates 6 gaps — one before each boy and one at the end. Choose 3 of "
                    "those gaps for the girls and arrange them: "
                    "$\\binom{6}{3} \\times 3! = 20 \\times 6 = 120$.\n\n"
                    "Total $= 120 \\times 120 = 14400$ ways."
                ),
                alt=(
                    "The gap method is the standard tool for every 'no two together' question. "
                    "Place the unrestricted items first, count the gaps they create — always one "
                    "more than the number of items — then choose gaps for the restricted ones."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Permutations",
                body="$^nP_r = \\dfrac{n!}{(n-r)!}$ — order matters.",
                example="$^5P_2 = \\dfrac{120}{6} = 20$.",
            ),
            FC(
                title="Combinations",
                body="$^nC_r = \\dfrac{n!}{r!\\,(n-r)!}$ — order does not matter.",
                example="$\\binom{5}{2} = 10$.",
            ),
            FC(
                title="Symmetry",
                body="$^nC_r = {}^nC_{n-r}$",
                example="$\\binom{10}{8} = \\binom{10}{2} = 45$, and the second is much less work.",
            ),
            FC(
                title="Repeated items",
                body="$\\dfrac{n!}{p!\\,q!\\,r!}$, dividing by the factorial of each repeat count.",
                example="LEVEL gives $\\dfrac{5!}{2!\\,2!} = 30$.",
            ),
            FC(
                title="Circular arrangements",
                body="$(n-1)!$ round a table; halve it if reflections are also identical.",
                example="Five people round a table: $4! = 24$.",
            ),
            FC(
                title="The gap method",
                body="Arrange the unrestricted items, then choose from the $n + 1$ gaps for the ones that must not be adjacent.",
                example="4 boys make 5 gaps for the girls to go into.",
            ),
        ],
        traps=[
            "Using a permutation where the question does not care about order. Ask 'would swapping two of these give a different outcome?'",
            "Adding when you should multiply. Multiply for 'and', add for 'or'.",
            "Forgetting to divide by the repeats when letters or objects are identical.",
            "In circular arrangements, using $n!$ instead of $(n-1)!$ — a rotation is not a new arrangement.",
            "Counting overlapping cases twice in an 'at least' question. Subtract from the total instead when you can.",
        ],
        checklist=[
            "Decide, for any question, whether order matters.",
            "Multiply independent choices and add exclusive cases, correctly.",
            "Handle repeated items and circular seating.",
            "Use the gap method for 'no two together'.",
            "Choose between direct casework and total-minus-complement.",
        ],
        minutes=12,
    ),
    LessonSpec(
        mt="qa.numsys.divisibility-factors",
        prereq="Multiplication tables, and the idea of a prime number.",
        intuition=(
            "Every whole number has a fingerprint: the primes it is built from, and how many of "
            "each. $60$ is $2 \\times 2 \\times 3 \\times 5$, and no other number has that exact "
            "recipe. This is the fundamental theorem of arithmetic, and it is the reason nearly "
            "every number-systems question begins with 'factorise it'.\n\n"
            "Divisibility tests are shortcuts for reading part of that fingerprint without doing "
            "the division. They are not magic: the test for 9, for instance, works because every "
            "power of 10 leaves a remainder of 1 when divided by 9, so a number and its digit sum "
            "always leave the same remainder."
        ),
        core=(
            "The tests worth knowing cold:\n\n"
            "**2** — last digit even. **4** — last two digits divisible by 4. **8** — last three. "
            "This works because 100 is divisible by 4 and 1000 by 8, so everything above those "
            "places contributes nothing.\n\n"
            "**3** — digit sum divisible by 3. **9** — digit sum divisible by 9.\n\n"
            "**5** — ends in 0 or 5. **10** — ends in 0.\n\n"
            "**11** — the alternating digit sum, adding and subtracting digits in turn, is "
            "divisible by 11.\n\n"
            "**6, 12, 15** and other composites — test each of their coprime parts. For 12, check "
            "3 and 4, not 2 and 6, because 2 and 6 share a factor and would not pin the number "
            "down.\n\n"
            "That last point catches people out regularly: a number divisible by both 2 and 6 need "
            "not be divisible by 12. You need factors with no common divisor."
        ),
        methods=[
            Method(
                name="Testing divisibility",
                recognise="'is N divisible by k?', or a missing digit that makes it so.",
                steps=[
                    "For a composite divisor, split it into coprime factors and test each.",
                    "Apply the digit tests rather than dividing.",
                    "For a missing digit, write the test as an equation and solve for the digit.",
                ],
                worked="For $3\\_4$ divisible by 9, the digit sum $3 + d + 4$ must be a multiple of 9, so $d = 2$.",
            ),
            Method(
                name="Finding common factors and multiples",
                recognise="'the largest number that divides both', or 'the smallest number divisible by both'.",
                steps=[
                    "Prime factorise each number.",
                    "For the HCF take the lowest power of each shared prime; for the LCM take the highest power of every prime that appears.",
                    "Check with $\\text{HCF} \\times \\text{LCM} = $ product of the two numbers.",
                ],
                worked="$12 = 2^2 \\times 3$ and $18 = 2 \\times 3^2$ give HCF 6 and LCM 36, and $6 \\times 36 = 216 = 12 \\times 18$.",
            ),
            Method(
                name="Counting multiples in a range",
                recognise="'how many numbers between 1 and 500 are divisible by 7?'",
                steps=[
                    "Divide the upper limit by the divisor and take the floor.",
                    "Subtract the same count for anything below the lower limit.",
                    "For 'divisible by 3 or 5', add both counts and subtract those divisible by 15, or you will double-count.",
                ],
                worked="Multiples of 7 up to 500: $\\left\\lfloor \\dfrac{500}{7} \\right\\rfloor = 71$.",
            ),
        ],
        examples=[
            EX(
                stem="How many numbers from 1 to 300 are divisible by 3 or by 5?",
                solution=(
                    "Count each separately, then remove the overlap.\n\n"
                    "Divisible by 3: $\\left\\lfloor \\dfrac{300}{3} \\right\\rfloor = 100$.\n\n"
                    "Divisible by 5: $\\left\\lfloor \\dfrac{300}{5} \\right\\rfloor = 60$.\n\n"
                    "Divisible by both means divisible by 15: "
                    "$\\left\\lfloor \\dfrac{300}{15} \\right\\rfloor = 20$. Those have been "
                    "counted twice, so subtract them once.\n\n"
                    "$100 + 60 - 20 = 140$ numbers."
                ),
                alt=(
                    "This is inclusion-exclusion, the same principle as two overlapping circles in "
                    "a Venn diagram. Note the overlap is multiples of 15, the **LCM** of 3 and 5 — "
                    "not their product in general, though here the two coincide because 3 and 5 "
                    "are coprime."
                ),
            ),
            EX(
                stem="Find the smallest number that must be added to 2497 to make it divisible by 11.",
                solution=(
                    "Apply the alternating-sum test to 2497, adding and subtracting digits in "
                    "turn from the right:\n\n"
                    "$7 - 9 + 4 - 2 = 0$\n\n"
                    "Zero is divisible by 11, so 2497 is **already** divisible by 11 — the answer "
                    "is 0.\n\n"
                    "Confirming directly: $2497 = 11 \\times 227$."
                ),
                alt=(
                    "Always finish by checking the direct division when a test gives a surprising "
                    "answer. The alternating sum is easy to get wrong by starting from the wrong "
                    "end, and a 30-second check costs less than a wrong mark."
                ),
            ),
            EX(
                stem="What is the largest three-digit number divisible by both 8 and 12?",
                solution=(
                    "A number divisible by both is divisible by their LCM.\n\n"
                    "$8 = 2^3$ and $12 = 2^2 \\times 3$, so the LCM is $2^3 \\times 3 = 24$.\n\n"
                    "The largest three-digit number is 999, and "
                    "$\\left\\lfloor \\dfrac{999}{24} \\right\\rfloor = 41$.\n\n"
                    "So the answer is $41 \\times 24 = 984$."
                ),
                alt=(
                    "Using the product $8 \\times 12 = 96$ instead of the LCM would give 960, "
                    "which is divisible by both but is not the largest such number. Always take "
                    "the LCM, not the product, unless the two are coprime."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Digit-sum tests",
                body="Divisible by 3 or 9 exactly when the digit sum is.",
                example="$4716$ has digit sum 18, so it is divisible by both 3 and 9.",
            ),
            FC(
                title="Last-digits tests",
                body="4 checks the last two digits, 8 the last three, because 100 and 1000 carry those factors.",
                example="$71316$ ends in 16, which is divisible by 4.",
            ),
            FC(
                title="The 11 test",
                body="Alternately add and subtract the digits; divisible by 11 exactly when that total is.",
                example="$2497$ gives $7 - 9 + 4 - 2 = 0$, so it is divisible by 11.",
            ),
            FC(
                title="Composite divisors",
                body="Split into **coprime** factors and test each. For 12 use 3 and 4, never 2 and 6.",
                example="$36$ passes both the 3 test and the 4 test, so it is divisible by 12.",
            ),
        ],
        traps=[
            "Testing 12 with 2 and 6. They share a factor, so passing both proves nothing.",
            "Multiplying two numbers instead of taking their LCM when a common multiple is wanted.",
            "In an 'A or B' count, forgetting to subtract the overlap.",
            "Running the 11 test from the wrong end, or losing a sign partway through.",
        ],
        checklist=[
            "Apply every standard divisibility test from memory.",
            "Split a composite divisor into coprime parts correctly.",
            "Count multiples in a range, including 'or' cases with inclusion-exclusion.",
            "Explain why the digit-sum test for 9 actually works.",
        ],
        minutes=10,
    ),
    LessonSpec(
        mt="qa.numsys.hcf-lcm",
        prereq="Prime factorisation.",
        intuition=(
            "Two ways of thinking about two numbers.\n\n"
            "The **HCF** is the largest tile that paves both. If you have a floor 12 m by 18 m and "
            "want to cover it in identical square tiles with none cut, the biggest square you can "
            "use is 6 m — the highest common factor. HCF questions are the ones about cutting "
            "things into equal largest pieces.\n\n"
            "The **LCM** is when two repeating cycles line up again. Two bells, one ringing every "
            "12 minutes and one every 18, both rang together at the start; they next coincide "
            "after 36 minutes — the lowest common multiple. LCM questions are the ones about "
            "things meeting, coinciding, or coming round together.\n\n"
            "So the giveaway in a stem: **cutting or distributing** points to HCF, **repeating or "
            "coinciding** points to LCM."
        ),
        core=(
            "Prime factorise both numbers and the two quantities read straight off.\n\n"
            "For the **HCF**, take every prime the numbers share, each to the **lowest** power "
            "that appears. Anything not in both cannot divide both.\n\n"
            "For the **LCM**, take every prime that appears in either, each to the **highest** "
            "power. Anything less would fail to be a multiple of one of them.\n\n"
            "For two numbers there is a relationship worth keeping as a check:\n\n"
            "$$\\text{HCF} \\times \\text{LCM} = a \\times b$$\n\n"
            "It holds for two numbers only — it is **not** true for three, and assuming otherwise "
            "is a classic error.\n\n"
            "For fractions the rules invert in a way that is easy to remember once you see why: "
            "the HCF of fractions is $\\dfrac{\\text{HCF of numerators}}{\\text{LCM of "
            "denominators}}$, and the LCM is $\\dfrac{\\text{LCM of numerators}}{\\text{HCF of "
            "denominators}}$. A larger denominator makes a smaller fraction, so the roles swap."
        ),
        methods=[
            Method(
                name="Finding HCF and LCM from factorisation",
                recognise="two or more numbers, asking for a greatest common divisor or least common multiple.",
                steps=[
                    "Prime factorise each number.",
                    "HCF: lowest power of each shared prime. LCM: highest power of every prime present.",
                    "For two numbers, check with $\\text{HCF} \\times \\text{LCM} = a \\times b$.",
                ],
                worked="$24 = 2^3 \\times 3$ and $36 = 2^2 \\times 3^2$ give HCF $2^2 \\times 3 = 12$ and LCM $2^3 \\times 3^2 = 72$.",
            ),
            Method(
                name="Bells, lights and coinciding cycles",
                recognise="things repeating at fixed intervals, asking when they next coincide.",
                steps=[
                    "Take the LCM of the intervals.",
                    "For 'how many times in an hour', divide the total time by that LCM.",
                    "Decide whether the moment at the very start counts — questions differ, and the wording decides it.",
                ],
                worked="Bells at 6, 8 and 12 minutes have LCM 24, so they ring together every 24 minutes.",
            ),
            Method(
                name="Largest equal pieces, or largest common measure",
                recognise="cutting rope, tiling a floor, or distributing items into equal groups with nothing left over.",
                steps=[
                    "Take the HCF of the quantities.",
                    "For 'how many pieces', divide each quantity by the HCF and add.",
                ],
                worked="Ropes of 36 and 48 m cut into equal longest pieces use 12 m lengths: $3 + 4 = 7$ pieces.",
            ),
            Method(
                name="Numbers leaving the same remainder",
                recognise="'the least number that leaves remainder r when divided by a, b and c'.",
                steps=[
                    "If the remainder is the same each time, the answer is $\\text{LCM} + r$.",
                    "If instead each divisor leaves a remainder that falls short by the same amount, the answer is $\\text{LCM} - \\text{that shortfall}$.",
                    "Read carefully which of the two situations you are in.",
                ],
                worked="The least number leaving remainder 3 with 4, 6 and 8 is $24 + 3 = 27$.",
            ),
        ],
        examples=[
            EX(
                stem="Find the HCF and LCM of 48 and 180, and verify the relationship between them.",
                solution=(
                    "Factorise both.\n\n"
                    "$48 = 2^4 \\times 3$ and $180 = 2^2 \\times 3^2 \\times 5$.\n\n"
                    "**HCF** — shared primes at their lowest powers: "
                    "$2^2 \\times 3 = 12$.\n\n"
                    "**LCM** — every prime at its highest power: "
                    "$2^4 \\times 3^2 \\times 5 = 720$.\n\n"
                    "Check: $12 \\times 720 = 8640$, and $48 \\times 180 = 8640$. They agree."
                ),
                alt=(
                    "That check is cheap and catches most slips. Note it only works for two "
                    "numbers — with three, HCF times LCM has no such tidy relationship to the "
                    "product."
                ),
            ),
            EX(
                stem="Three bells ring at intervals of 9, 12 and 15 minutes. If they ring together at 10 am, when do they next ring together?",
                solution=(
                    "They coincide at multiples of every interval, so take the LCM.\n\n"
                    "$9 = 3^2$, $12 = 2^2 \\times 3$, $15 = 3 \\times 5$.\n\n"
                    "Highest power of each prime: $2^2 \\times 3^2 \\times 5 = 180$.\n\n"
                    "So they next ring together after 180 minutes, which is 3 hours: at "
                    "**1 pm**."
                ),
                alt=(
                    "Sanity check by dividing: $180$ is $20$ nines, $15$ twelves and $12$ "
                    "fifteens — all whole, as they must be. If any division leaves a remainder, "
                    "the LCM is wrong."
                ),
            ),
            EX(
                stem="Find the greatest number that divides 261, 933 and 1381 leaving the same remainder in each case.",
                solution=(
                    "If a number $d$ leaves the same remainder with all three, then it divides "
                    "their **differences** exactly — the remainder cancels out on subtraction.\n\n"
                    "$933 - 261 = 672$, $1381 - 933 = 448$, and $1381 - 261 = 1120$.\n\n"
                    "So $d$ is the HCF of 672, 448 and 1120.\n\n"
                    "$672 = 2^5 \\times 3 \\times 7$, $448 = 2^6 \\times 7$, "
                    "$1120 = 2^5 \\times 5 \\times 7$.\n\n"
                    "Shared at lowest powers: $2^5 \\times 7 = 224$.\n\n"
                    "The greatest such number is **224**."
                ),
                alt=(
                    "The differences trick is the key move, and it is worth remembering as a "
                    "sentence: **equal remainders means take differences**. Checking, "
                    "$261 = 224 + 37$ and $933 = 4 \\times 224 + 37$ — remainder 37 both times."
                ),
            ),
        ],
        formulas=[
            FC(
                title="From prime factorisation",
                body="HCF takes the lowest power of each shared prime; LCM takes the highest power of every prime present.",
                example="$2^3 3$ and $2^2 3^2$ give HCF $2^2 3 = 12$ and LCM $2^3 3^2 = 72$.",
            ),
            FC(
                title="The two-number identity",
                body="$\\text{HCF} \\times \\text{LCM} = a \\times b$. True for two numbers only.",
                example="$12 \\times 72 = 864 = 24 \\times 36$.",
            ),
            FC(
                title="Fractions",
                body=(
                    "$\\text{HCF} = \\dfrac{\\text{HCF of numerators}}{\\text{LCM of denominators}}$ and "
                    "$\\text{LCM} = \\dfrac{\\text{LCM of numerators}}{\\text{HCF of denominators}}$"
                ),
                example="For $\\dfrac{2}{3}$ and $\\dfrac{4}{9}$ the HCF is $\\dfrac{2}{9}$.",
            ),
            FC(
                title="Equal remainders",
                body="A divisor leaving the same remainder with several numbers is a factor of their pairwise differences.",
                example="Same remainder with 261 and 933 means it divides 672.",
            ),
        ],
        traps=[
            "Applying $\\text{HCF} \\times \\text{LCM} = $ product to three numbers. It only holds for two.",
            "Reaching for the LCM on a cutting-into-pieces question, or the HCF on a coinciding question. Read what is being asked for.",
            "Including a prime in the HCF that is missing from one of the numbers.",
            "Forgetting that the moment at the start may or may not count as a coincidence, depending on the wording.",
            "Inverting the fraction rules, using LCM of denominators where HCF belongs.",
        ],
        checklist=[
            "Compute HCF and LCM from prime factorisations without hesitating.",
            "Tell an HCF question from an LCM question by the wording alone.",
            "Use the differences trick for equal-remainder problems.",
            "Handle HCF and LCM of fractions.",
        ],
        minutes=11,
    ),
]
