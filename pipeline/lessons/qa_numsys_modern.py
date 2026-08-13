"""Number systems and modern-maths lessons."""

from __future__ import annotations

from . import EX, FC, LessonSpec, Method

SPECS = [
    LessonSpec(
        mt="qa.numsys.remainders",
        prereq="Division with remainder, and index laws.",
        methods=[
            Method(
                name="Remainder of a large power",
                recognise="something like $7^{100}$ divided by a small number.",
                steps=[
                    "Compute the remainders of the first few powers and look for the cycle.",
                    "Divide the exponent by the cycle length and take the remainder.",
                    "Read off the corresponding entry in the cycle — a remainder of 0 means the last entry.",
                ],
                worked="Powers of 3 mod 7 cycle 3, 2, 6, 4, 5, 1 with length 6; $3^{100}$ has $100 \\bmod 6 = 4$, so the answer is 4.",
            ),
            Method(
                name="Remainder of a product",
                recognise="several numbers multiplied, then divided.",
                steps=[
                    "Reduce each factor to its own remainder first.",
                    "Multiply the small remainders together.",
                    "Reduce again at the end.",
                ],
                worked="$53 \\times 47 \\bmod 9$ becomes $8 \\times 2 = 16$, which reduces to 7.",
            ),
        ],
        checklist=[
            "Find the cycle length of a power modulo a small number.",
            "Reduce each factor before multiplying, not after.",
        ],
        intuition=(
            "Look at a clock. It is 10 o'clock and you wait 5 hours — you land on 3, not 15, because the "
            "clock wraps around at 12. Remainders work exactly like that: only the wrap-around position "
            "matters, not how many full loops you made.\n\n"
            "That is why enormous powers like $7^{100}$ have easy remainders. The pattern repeats in a short "
            "cycle, and you just need to know where in the cycle you land."
        ),
        core=(
            "The key habit is to **reduce early**. If you want the remainder of a big product, replace each "
            "factor by its own remainder first — the answer is unchanged and the numbers stay small.\n\n"
            "For powers, compute the first few remainders and watch for the repeat. Once you know the cycle "
            "length $L$, the exponent only matters modulo $L$. Take $7^{100} \\bmod 5$: the remainders of "
            "$7^1, 7^2, 7^3, 7^4$ are 2, 4, 3, 1 and then it repeats, so the cycle length is 4. Since "
            "$100 \\bmod 4 = 0$, we land on the last entry of the cycle, giving 1."
        ),
        examples=[
            EX(
                stem="Find the remainder when $3^{20}$ is divided by 7.",
                solution=(
                    "List the remainders of successive powers of 3 modulo 7:\n\n"
                    "$3^1 = 3$, $3^2 = 9 \\to 2$, $3^3 \\to 6$, $3^4 \\to 4$, $3^5 \\to 5$, $3^6 \\to 1$, and "
                    "then the pattern restarts.\n\n"
                    "The cycle has length 6. Since $20 \\bmod 6 = 2$, we are at the second entry, which is 2.\n\n"
                    "The remainder is 2."
                ),
            ),
            EX(
                stem="Find the remainder when $123 \\times 457$ is divided by 11.",
                solution=(
                    "Reduce each factor first. $123 = 11 \\times 11 + 2$, so $123 \\to 2$. "
                    "$457 = 11 \\times 41 + 6$, so $457 \\to 6$.\n\n"
                    "Now $2 \\times 6 = 12$, and $12 \\bmod 11 = 1$.\n\n"
                    "The remainder is 1 — found without ever multiplying 123 by 457."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Reduce before combining",
                body="$(a \\times b) \\bmod m = ((a \\bmod m) \\times (b \\bmod m)) \\bmod m$. The same holds for addition.",
                example="$98 \\times 97 \\bmod 9$: $98 \\to 8$, $97 \\to 7$, $8 \\times 7 = 56 \\to 2$.",
            ),
            FC(
                title="Cyclicity of powers",
                body="Find the smallest $L$ with $a^L \\equiv 1 \\pmod m$. Then $a^n$ depends only on $n \\bmod L$.",
                example="Powers of 2 mod 7 cycle 2, 4, 1 with $L = 3$, so $2^{30} \\equiv 1$.",
            ),
            FC(
                title="Fermat's little theorem",
                body="If $p$ is prime and $a$ is not a multiple of $p$, then $a^{p-1} \\equiv 1 \\pmod p$.",
                example="$3^{10} \\equiv 1 \\pmod{11}$, so $3^{23} = 3^{20} \\cdot 3^3 \\equiv 27 \\equiv 5$.",
            ),
        ],
        traps=[
            "Computing the giant power first. Reduce as you go or the numbers become unusable.",
            "Getting the cycle length off by one. Write out the first several powers explicitly until you see the repeat.",
            "Applying Fermat's theorem when the base is a multiple of the prime — the theorem does not apply there.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.numsys.factors-count-sum-product",
        prereq="Prime factorisation.",
        methods=[
            Method(
                name="Counting the factors",
                recognise="'how many factors does N have?'",
                steps=[
                    "Write $N$ in prime factorised form, $p^a q^b r^c$.",
                    "Add one to each index and multiply: $(a+1)(b+1)(c+1)$.",
                    "Each factor is built by choosing an index from 0 up to the maximum, which is why the plus one is there.",
                ],
                worked="$72 = 2^3 \\times 3^2$ has $4 \\times 3 = 12$ factors.",
            ),
            Method(
                name="Sum of the factors",
                recognise="'find the sum of all factors of N'.",
                steps=[
                    "For each prime, form the sum $1 + p + p^2 + \\cdots + p^a$.",
                    "Multiply those sums together.",
                ],
                worked="$72$ gives $(1+2+4+8)(1+3+9) = 15 \\times 13 = 195$.",
            ),
            Method(
                name="Counting only even or only odd factors",
                recognise="a restriction on the kind of factor wanted.",
                steps=[
                    "Odd factors: ignore the power of 2 entirely and count from the rest.",
                    "Even factors: total factors minus odd factors.",
                ],
                worked="$72$ has $(2+1) = 3$ odd factors, so $12 - 3 = 9$ even ones.",
            ),
        ],
        checklist=[
            "Prime factorise quickly and reliably.",
            "Count and sum factors from the factorisation alone.",
            "Split a count into odd and even factors.",
        ],
        intuition=(
            "Every whole number is built from prime bricks, and there is only one way to build it. "
            "$12 = 2 \\times 2 \\times 3$, always.\n\n"
            "Now, a factor of 12 is anything you can make using **some** of those bricks. You can take zero, "
            "one or two 2s (3 choices) and zero or one 3 (2 choices). That is $3 \\times 2 = 6$ factors — and "
            "indeed 12 has exactly 6: 1, 2, 3, 4, 6, 12."
        ),
        core=(
            "Write $N = p^a \\times q^b \\times r^c \\ldots$. Building a factor means choosing an exponent for "
            "each prime independently: $a+1$ options for $p$ (from 0 to $a$), $b+1$ for $q$, and so on.\n\n"
            "Multiply those counts and you have the number of factors. That single idea also gives you the "
            "sum of factors, and lets you count only the even ones, or only the odd ones, by restricting the "
            "choices you allow."
        ),
        examples=[
            EX(
                stem="How many factors does 360 have?",
                solution=(
                    "Factorise: $360 = 2^3 \\times 3^2 \\times 5^1$.\n\n"
                    "Choices: the power of 2 can be 0 to 3 (4 ways), the power of 3 can be 0 to 2 (3 ways), "
                    "and the power of 5 can be 0 or 1 (2 ways).\n\n"
                    "Total $= 4 \\times 3 \\times 2 = 24$ factors."
                ),
            ),
            EX(
                stem="How many of 360's factors are even?",
                solution=(
                    "An even factor must include at least one 2, so the power of 2 can be 1, 2 or 3 — that is "
                    "3 choices instead of 4.\n\n"
                    "The other primes are unrestricted: 3 ways for the 3s, 2 ways for the 5.\n\n"
                    "Even factors $= 3 \\times 3 \\times 2 = 18$."
                ),
                alt="Cross-check: odd factors allow only $2^0$, giving $1 \\times 3 \\times 2 = 6$. And $18 + 6 = 24$, the total.",
            ),
        ],
        formulas=[
            FC(
                title="Number of factors",
                body="If $N = p^a q^b r^c$ then the number of factors is $(a+1)(b+1)(c+1)$.",
                example="$72 = 2^3 \\times 3^2$ has $(3+1)(2+1) = 12$ factors.",
            ),
            FC(
                title="Sum of factors",
                body="$\\sigma(N) = \\dfrac{p^{a+1}-1}{p-1} \\times \\dfrac{q^{b+1}-1}{q-1} \\times \\cdots$",
                example="$12 = 2^2 \\times 3$: $\\dfrac{2^3-1}{1} \\times \\dfrac{3^2-1}{2} = 7 \\times 4 = 28$, and indeed $1+2+3+4+6+12 = 28$.",
            ),
            FC(
                title="Product of factors",
                body="The product of all factors of $N$ is $N^{d/2}$, where $d$ is the number of factors.",
                example="12 has 6 factors, so their product is $12^3 = 1728$.",
            ),
        ],
        traps=[
            "Forgetting that the exponent can be zero. A prime with exponent $a$ gives $a+1$ choices, not $a$.",
            "Missing 1 and $N$ themselves — they are both factors.",
            "Rushing the prime factorisation. Every later step depends on getting it exactly right.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.numsys.base-systems",
        prereq="Place value — base 10 is one case of a general idea.",
        methods=[
            Method(
                name="Converting to decimal",
                recognise="a number written with a base subscript.",
                steps=[
                    "Give each digit its place value: powers of the base, rising from the right starting at zero.",
                    "Multiply and add.",
                ],
                worked="$1011_2 = 8 + 0 + 2 + 1 = 11$.",
            ),
            Method(
                name="Converting from decimal",
                recognise="a decimal number to be written in another base.",
                steps=[
                    "Divide repeatedly by the base, recording each remainder.",
                    "Read the remainders **upwards** — bottom to top.",
                ],
                worked="$45$ in base 3: remainders 0, 0, 2, 1 read upwards give $1200_3$.",
            ),
        ],
        checklist=[
            "Convert in both directions without confusing the digit order.",
            "Recognise that a digit must always be smaller than the base.",
        ],
        intuition=(
            "We count in tens because we have ten fingers. The number 342 means three hundreds, four tens and "
            "two ones — each place is worth ten times the one to its right.\n\n"
            "There is nothing sacred about ten. A computer counts in twos. If you had only five fingers per "
            "hand and counted in fives, then '342' would mean three twenty-fives, four fives and two ones, "
            "which is 97 in our notation. Same digits, different place values."
        ),
        core=(
            "In base $b$, the places are worth $1, b, b^2, b^3, \\ldots$ from the right. Converting **to** "
            "decimal means multiplying each digit by its place value and adding.\n\n"
            "Converting **from** decimal goes the other way: divide repeatedly by $b$, collecting remainders, "
            "then read those remainders bottom to top.\n\n"
            "One rule worth remembering: in base $b$ the only digits allowed are $0$ through $b-1$. Seeing a "
            "7 in a base-5 number means something has gone wrong."
        ),
        examples=[
            EX(
                stem="Convert $2143_5$ to decimal.",
                solution=(
                    "Place values from the right are $1, 5, 25, 125$.\n\n"
                    "$2 \\times 125 + 1 \\times 25 + 4 \\times 5 + 3 \\times 1$\n\n"
                    "$= 250 + 25 + 20 + 3 = 298$."
                ),
            ),
            EX(
                stem="Convert 100 to base 7.",
                solution=(
                    "Divide repeatedly by 7 and keep the remainders:\n\n"
                    "$100 \\div 7 = 14$ remainder $2$\n"
                    "$14 \\div 7 = 2$ remainder $0$\n"
                    "$2 \\div 7 = 0$ remainder $2$\n\n"
                    "Reading the remainders bottom to top: $202_7$.\n\n"
                    "Check: $2 \\times 49 + 0 \\times 7 + 2 = 100$."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Base to decimal",
                body="$d_n \\ldots d_1 d_0$ in base $b$ equals $\\sum d_i b^i$, with place values $1, b, b^2, \\ldots$",
                example="$1011_2 = 8 + 0 + 2 + 1 = 11$.",
            ),
            FC(
                title="Decimal to base",
                body="Divide by $b$ repeatedly, collect remainders, and read them in reverse order.",
                example="$30$ in base 4: remainders 2, 3, 1 giving $132_4$.",
            ),
        ],
        traps=[
            "Reading the remainders in the order you found them. They must be reversed.",
            "Using a digit that does not exist in that base, such as an 8 in base 8.",
            "Assuming a bigger base means a bigger number. $100_2$ is 4, far smaller than $100_{10}$.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.numsys.last-digit-trailing-zeroes",
        prereq="Cyclicity of last digits, and prime factorisation.",
        methods=[
            Method(
                name="Last digit of a large power",
                recognise="'the unit digit of $n^k$'.",
                steps=[
                    "Only the last digit of the base matters.",
                    "Last digits repeat with a cycle of length 1, 2 or 4.",
                    "Reduce the exponent modulo the cycle length and read off.",
                ],
                worked="$7^{102}$: the cycle is 7, 9, 3, 1 of length 4, and $102 \\bmod 4 = 2$, so the last digit is 9.",
            ),
            Method(
                name="Trailing zeroes in a factorial",
                recognise="'how many zeroes does $n!$ end in?'",
                steps=[
                    "A zero needs a 2 and a 5; fives are always scarcer, so count fives.",
                    "Add $\\left\\lfloor \\dfrac{n}{5} \\right\\rfloor + \\left\\lfloor \\dfrac{n}{25} \\right\\rfloor + \\left\\lfloor \\dfrac{n}{125} \\right\\rfloor + \\cdots$",
                    "Stop when the divisor exceeds $n$.",
                ],
                worked="$100!$ has $20 + 4 = 24$ trailing zeroes.",
            ),
        ],
        checklist=[
            "Find any last digit using the cycle of length at most 4.",
            "Count trailing zeroes by counting fives, and say why fives and not twos.",
        ],
        intuition=(
            "Multiply any two numbers and look only at the last digit of the answer. It depends **only** on "
            "the last digits of the two numbers you multiplied. $37 \\times 43$ ends in 1 for the same reason "
            "$7 \\times 3 = 21$ does — everything else lands further left.\n\n"
            "So for the last digit of a huge power, throw away all but the units digit and watch the pattern "
            "repeat. It always repeats within four steps."
        ),
        core=(
            "**Last digit of a power.** Keep only the units digit of the base and list its powers until they "
            "repeat. Powers of 2 go 2, 4, 8, 6 and then start again — a cycle of 4. Every digit's cycle has "
            "length 1, 2 or 4, so you never track more than four cases.\n\n"
            "**Trailing zeroes of a factorial.** Each trailing zero needs a factor of 10, which needs a 2 and "
            "a 5. In any factorial there are far more 2s than 5s, so the number of 5s is the limiting factor. "
            "Count them with $\\lfloor n/5 \\rfloor + \\lfloor n/25 \\rfloor + \\lfloor n/125 \\rfloor + \\cdots$, "
            "where the higher terms catch numbers like 25 that contribute more than one 5."
        ),
        examples=[
            EX(
                stem="Find the last digit of $7^{35}$.",
                solution=(
                    "Powers of 7 end in: $7, 9, 3, 1$, then repeat. The cycle length is 4.\n\n"
                    "$35 \\bmod 4 = 3$, so we want the third entry of the cycle.\n\n"
                    "The last digit is 3."
                ),
                alt="When the remainder is 0, take the last entry of the cycle, not the first.",
            ),
            EX(
                stem="How many trailing zeroes does $100!$ have?",
                solution=(
                    "Count the factors of 5:\n\n"
                    "$\\lfloor 100/5 \\rfloor = 20$\n"
                    "$\\lfloor 100/25 \\rfloor = 4$\n"
                    "$\\lfloor 100/125 \\rfloor = 0$, so we stop.\n\n"
                    "Total $= 20 + 4 = 24$ trailing zeroes.\n\n"
                    "The extra 4 accounts for 25, 50, 75 and 100, each of which supplies a second 5."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Cyclicity of last digits",
                body="Last digits of powers repeat with period 1, 2 or 4. Reduce the exponent modulo the cycle length.",
                example="$3^{22}$: cycle 3, 9, 7, 1 of length 4; $22 \\bmod 4 = 2$, so it ends in 9.",
            ),
            FC(
                title="Trailing zeroes in $n!$",
                body="$\\left\\lfloor \\dfrac{n}{5} \\right\\rfloor + \\left\\lfloor \\dfrac{n}{25} \\right\\rfloor + \\left\\lfloor \\dfrac{n}{125} \\right\\rfloor + \\cdots$",
                example="$50!$ has $10 + 2 = 12$ trailing zeroes.",
            ),
        ],
        traps=[
            "Stopping after $\\lfloor n/5 \\rfloor$ and missing the higher powers of 5.",
            "Counting 2s instead of 5s. There are always more 2s, so they never run out first.",
            "Mishandling a remainder of 0 when locating a position in the cycle.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.numsys.factorials-prime-power",
        prereq="Factorials and prime factorisation.",
        methods=[
            Method(
                name="Highest power of a prime dividing a factorial",
                recognise="'the largest k such that $p^k$ divides $n!$'.",
                steps=[
                    "Use Legendre's formula: add $\\left\\lfloor \\dfrac{n}{p} \\right\\rfloor + \\left\\lfloor \\dfrac{n}{p^2} \\right\\rfloor + \\cdots$",
                    "Stop once the divisor exceeds $n$.",
                    "Each term counts the multiples that contribute one further copy of the prime.",
                ],
                worked="The power of 3 in $50!$ is $16 + 5 + 1 = 22$.",
            ),
        ],
        checklist=[
            "Apply Legendre's formula and explain each term.",
            "Handle a composite divisor by doing each prime separately and taking the binding one.",
        ],
        intuition=(
            "$10!$ means $1 \\times 2 \\times 3 \\times \\cdots \\times 10$. Suppose you want to know how many "
            "2s are hiding inside it. You could multiply the whole thing out — or you could just walk along "
            "and count.\n\n"
            "Every second number contributes a 2. Every fourth number contributes an **extra** one, because "
            "4 is $2 \\times 2$. Every eighth contributes yet another. Adding those counts is Legendre's formula."
        ),
        core=(
            "The highest power of a prime $p$ dividing $n!$ is\n\n"
            "$$\\left\\lfloor \\frac{n}{p} \\right\\rfloor + \\left\\lfloor \\frac{n}{p^2} \\right\\rfloor + "
            "\\left\\lfloor \\frac{n}{p^3} \\right\\rfloor + \\cdots$$\n\n"
            "The first term counts the multiples of $p$. The second catches the fact that multiples of $p^2$ "
            "carry a second copy, the third catches a third copy, and so on. Keep going until the power of $p$ "
            "exceeds $n$, at which point every remaining term is zero."
        ),
        examples=[
            EX(
                stem="Find the highest power of 3 that divides $50!$.",
                solution=(
                    "$\\lfloor 50/3 \\rfloor = 16$\n"
                    "$\\lfloor 50/9 \\rfloor = 5$\n"
                    "$\\lfloor 50/27 \\rfloor = 1$\n"
                    "$\\lfloor 50/81 \\rfloor = 0$, so stop.\n\n"
                    "Total $= 16 + 5 + 1 = 22$.\n\nSo $3^{22}$ divides $50!$ but $3^{23}$ does not."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Legendre's formula",
                body="The exponent of prime $p$ in $n!$ is $\\sum_{k \\geq 1} \\left\\lfloor \\dfrac{n}{p^k} \\right\\rfloor$.",
                example="Power of 2 in $20!$: $10 + 5 + 2 + 1 = 18$.",
            ),
            FC(
                title="Highest power of a composite",
                body="Factorise it first, apply Legendre to each prime, then take the most restrictive.",
                example="For $6^k$ in $20!$: 2s give 18, 3s give 8, so the answer is 8.",
            ),
        ],
        traps=[
            "Stopping after the first term and undercounting badly.",
            "Rounding up instead of taking the floor. Always round down.",
            "For a composite like 6 or 12, forgetting to take the smaller of the two prime counts.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.numsys.rational-irrational",
        prereq="Fractions and decimals.",
        methods=[
            Method(
                name="Turning a recurring decimal into a fraction",
                recognise="a decimal with a bar or 'recurring'.",
                steps=[
                    "Let $x$ be the decimal, and multiply by a power of 10 that shifts one full period.",
                    "Subtract the original from the shifted version, which cancels the recurring tail.",
                    "Solve for $x$ and simplify.",
                ],
                worked="$x = 0.\\overline{36}$ gives $100x - x = 36$, so $x = \\dfrac{36}{99} = \\dfrac{4}{11}$.",
            ),
        ],
        checklist=[
            "Convert any recurring decimal to a fraction.",
            "Say whether a given number is rational, and justify it.",
        ],
        intuition=(
            "A **rational** number is one you can write as a fraction of whole numbers. $0.5$ is $\\frac12$, "
            "and even $0.333\\ldots$ is $\\frac13$. Their decimals either stop or settle into a repeating "
            "pattern forever.\n\n"
            "An **irrational** number never does either. $\\sqrt{2}$ and $\\pi$ run on forever with no repeat, "
            "and no fraction of whole numbers can ever capture them exactly."
        ),
        core=(
            "Rational means expressible as $\\dfrac{p}{q}$ with $q \\neq 0$. Terminating and recurring decimals "
            "are both rational; everything else is irrational.\n\n"
            "Converting a recurring decimal back to a fraction uses a neat pattern: a single repeating digit "
            "sits over 9, a two-digit repeating block over 99, three digits over 999. So "
            "$0.\\overline{27} = \\frac{27}{99} = \\frac{3}{11}$.\n\n"
            "Useful closure facts: rational plus rational is rational, but rational plus irrational is always "
            "irrational. Irrational plus irrational can be either — $\\sqrt2 + (-\\sqrt2) = 0$."
        ),
        examples=[
            EX(
                stem="Express $0.\\overline{36}$ as a fraction in lowest terms.",
                solution=(
                    "A two-digit repeating block sits over 99:\n\n"
                    "$0.\\overline{36} = \\dfrac{36}{99}$\n\n"
                    "Divide top and bottom by 9: $\\dfrac{4}{11}$.\n\n"
                    "Check: $4 \\div 11 = 0.3636\\ldots$"
                ),
                alt=(
                    "The algebraic route: let $x = 0.3636\\ldots$, so $100x = 36.3636\\ldots$. Subtracting gives "
                    "$99x = 36$, hence $x = \\frac{36}{99}$."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Recurring decimal to fraction",
                body="A repeating block of $k$ digits sits over $k$ nines. Then reduce.",
                example="$0.\\overline{123} = \\dfrac{123}{999} = \\dfrac{41}{333}$.",
            ),
            FC(
                title="Closure facts",
                body="Rational $+$ rational is rational. Rational $+$ irrational is irrational. Irrational $+$ irrational may be either.",
                example="$2 + \\sqrt3$ is irrational, but $\\sqrt3 + (2 - \\sqrt3) = 2$ is rational.",
            ),
        ],
        traps=[
            "Calling every decimal that looks messy irrational. If it repeats, it is rational.",
            "Assuming every square root is irrational. $\\sqrt{16} = 4$ is perfectly rational.",
            "Forgetting to reduce the fraction at the end.",
        ],
        minutes=5,
    ),
    LessonSpec(
        mt="qa.modern.probability",
        prereq="Counting — probability is a count divided by a count.",
        methods=[
            Method(
                name="Dice outcomes",
                recognise="one or more dice, asking for a sum or a condition.",
                steps=[
                    "The sample space for two dice is 36 equally likely ordered pairs.",
                    "Count the pairs meeting the condition, treating the dice as distinguishable.",
                    "Divide.",
                ],
                worked="A sum of 8 happens in 5 ways out of 36, so the probability is $\\dfrac{5}{36}$.",
            ),
            Method(
                name="Drawing balls from a bag",
                recognise="coloured items drawn together or in succession.",
                steps=[
                    "Count the total ways to draw using combinations.",
                    "Count the favourable ways, choosing from each colour group.",
                    "Divide. Whether draws are with or without replacement changes the denominator, so check.",
                ],
                worked="Two reds from 5 red and 3 blue: $\\dfrac{\\binom{5}{2}}{\\binom{8}{2}} = \\dfrac{10}{28} = \\dfrac{5}{14}$.",
            ),
        ],
        checklist=[
            "Write down the sample space before counting anything.",
            "Use combinations when order does not matter, permutations when it does.",
            "Notice whether draws replace or not.",
        ],
        intuition=(
            "Probability is just careful counting. Roll a die: there are 6 equally likely outcomes, and 3 of "
            "them are even, so the chance of an even number is $\\frac36 = \\frac12$.\n\n"
            "The whole skill is counting the favourable outcomes and the total outcomes **correctly** — and "
            "making sure every outcome you count really is equally likely."
        ),
        core=(
            "$$P(\\text{event}) = \\frac{\\text{number of favourable outcomes}}{\\text{total number of outcomes}}$$\n\n"
            "Two dice give $6 \\times 6 = 36$ outcomes, not 11 — the sums 2 through 12 are **not** equally "
            "likely, so counting sums would be wrong.\n\n"
            "When drawing objects where order does not matter, count with combinations. Drawing 2 balls from "
            "9 gives $\\binom92 = 36$ possible pairs.\n\n"
            "'At least one' questions are almost always faster backwards: find the probability of **none** and "
            "subtract from 1."
        ),
        examples=[
            EX(
                stem="Two fair dice are thrown. What is the probability that the sum is 7?",
                solution=(
                    "Total outcomes: $6 \\times 6 = 36$.\n\n"
                    "Pairs summing to 7: $(1,6), (2,5), (3,4), (4,3), (5,2), (6,1)$ — that is 6 pairs. "
                    "Note $(2,5)$ and $(5,2)$ are different outcomes.\n\n"
                    "$P = \\dfrac{6}{36} = \\dfrac16$."
                ),
            ),
            EX(
                stem="A bag has 4 red and 5 blue balls. Two are drawn without replacement. What is the probability that both are red?",
                solution=(
                    "Total ways to choose 2 from 9: $\\binom92 = 36$.\n\n"
                    "Ways to choose 2 reds from 4: $\\binom42 = 6$.\n\n"
                    "$P = \\dfrac{6}{36} = \\dfrac16$."
                ),
                alt=(
                    "Sequentially: the first ball is red with probability $\\frac49$, and then only 3 reds "
                    "remain among 8 balls, so $\\frac49 \\times \\frac38 = \\frac{12}{72} = \\frac16$. Same answer."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Basic probability",
                body="$P(E) = \\dfrac{n(E)}{n(S)}$ when all outcomes are equally likely. Always between 0 and 1.",
                example="Drawing an ace from a full deck: $\\dfrac{4}{52} = \\dfrac{1}{13}$.",
            ),
            FC(
                title="Complement and 'at least one'",
                body="$P(\\text{at least one}) = 1 - P(\\text{none})$.",
                example="At least one head in 3 tosses: $1 - \\dfrac18 = \\dfrac78$.",
            ),
            FC(
                title="Addition and multiplication",
                body="$P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$. For independent events, $P(A \\cap B) = P(A)P(B)$.",
                example="Two independent events with $P = 0.5$ each both occur with probability $0.25$.",
            ),
        ],
        traps=[
            "Treating the 11 possible dice sums as equally likely. They are not; work with the 36 ordered outcomes.",
            "Forgetting that 'without replacement' changes the denominator for the second draw.",
            "Adding probabilities of events that can happen together without subtracting the overlap.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.modern.set-theory-venn",
        prereq="Nothing beyond counting, though a drawn diagram helps enormously.",
        methods=[
            Method(
                name="Two overlapping sets",
                recognise="two categories with an overlap, and a total.",
                steps=[
                    "Use $|A \\cup B| = |A| + |B| - |A \\cap B|$.",
                    "If some elements are in neither, subtract them from the total first.",
                    "Solve for whichever quantity is missing.",
                ],
                worked="50 people, 30 tea, 25 coffee, 8 neither: $42 = 30 + 25 - x$, so $x = 13$ like both.",
            ),
            Method(
                name="Three sets",
                recognise="three categories, usually with 'exactly two' or 'all three' mentioned.",
                steps=[
                    "Fill the diagram from the middle outwards: all three first, then the pairwise-only regions, then the singles.",
                    "Remember that 'both A and B' includes those who also have C, whereas 'only A and B' does not.",
                    "Use the alternating inclusion-exclusion formula as a check on the diagram.",
                ],
                worked="Exactly two $=$ (sum of pairwise overlaps) $- 3 \\times$ (all three).",
            ),
        ],
        checklist=[
            "Apply inclusion-exclusion for two and three sets.",
            "Tell 'both' from 'only both' in a stem.",
            "Fill a Venn diagram from the centre outwards.",
        ],
        intuition=(
            "Twenty students play cricket and fifteen play football. How many students are there? You cannot "
            "just say 35 — some of them play both, and you have counted those twice.\n\n"
            "Subtracting the double-counted overlap once is the entire principle of inclusion-exclusion. Two "
            "overlapping circles on paper make it obvious."
        ),
        core=(
            "For two sets: $|A \\cup B| = |A| + |B| - |A \\cap B|$. You add both, then remove the overlap you "
            "counted twice.\n\n"
            "For three sets the pattern alternates: add the singles, subtract the pairs, add the triple back. "
            "The triple overlap gets added three times and subtracted three times, so it needs adding once more "
            "to be counted at all.\n\n"
            "When solving, fill the Venn diagram from the **middle outwards**. Start with the all-three region, "
            "then the pairwise-only regions, then the only-one regions. Filling from the outside in leads to "
            "double counting almost every time."
        ),
        examples=[
            EX(
                stem="In a class of 50, 30 like tea, 25 like coffee, and 8 like neither. How many like both?",
                solution=(
                    "Students liking at least one drink: $50 - 8 = 42$.\n\n"
                    "By inclusion-exclusion, $|T \\cup C| = |T| + |C| - |T \\cap C|$:\n\n"
                    "$42 = 30 + 25 - |T \\cap C|$\n\n"
                    "So $|T \\cap C| = 55 - 42 = 13$ students like both."
                ),
                alt="Check: only tea is $30 - 13 = 17$, only coffee is $25 - 13 = 12$, and $17 + 12 + 13 + 8 = 50$.",
            ),
        ],
        formulas=[
            FC(
                title="Two sets",
                body="$|A \\cup B| = |A| + |B| - |A \\cap B|$",
                example="$|A| = 20$, $|B| = 15$, overlap 5 gives a union of 30.",
            ),
            FC(
                title="Three sets",
                body="$|A \\cup B \\cup C| = |A| + |B| + |C| - |A \\cap B| - |B \\cap C| - |A \\cap C| + |A \\cap B \\cap C|$",
                example="All singles 20, all pairs 8, triple 3 gives $60 - 24 + 3 = 39$.",
            ),
            FC(
                title="Exactly one, exactly two",
                body="Exactly two $=$ (sum of pairwise overlaps) $- 3 \\times$ (triple overlap). Exactly one $=$ union $-$ exactly two $-$ triple.",
                example="Pairwise 8 each and triple 3: exactly two is $24 - 9 = 15$.",
            ),
        ],
        traps=[
            "Reading 'both A and B' (which includes people who also do C) as 'only A and B'.",
            "Forgetting the people in none of the sets when the total is given.",
            "Filling the diagram from the outside in. Always start with the innermost region.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.modern.binomial-theorem",
        prereq="Combinations, and index laws.",
        methods=[
            Method(
                name="A specific term or coefficient",
                recognise="'the coefficient of $x^k$ in $(a + bx)^n$', or 'the rth term'.",
                steps=[
                    "The general term is $T_{r+1} = \\binom{n}{r} a^{n-r} b^r$.",
                    "Set the power of $x$ equal to the one you want and solve for $r$.",
                    "Substitute that $r$ back to get the coefficient.",
                ],
                worked="In $(1 + x)^{10}$ the coefficient of $x^3$ is $\\binom{10}{3} = 120$.",
            ),
        ],
        checklist=[
            "Write the general term and use it to find any coefficient.",
            "Remember the term index is $r + 1$, not $r$.",
        ],
        intuition=(
            "Multiply out $(1+x)^3$ by hand and you get $1 + 3x + 3x^2 + x^3$. Where does that 3 come from? "
            "There are three brackets, and to get a single $x$ you pick it from exactly one of them — three "
            "ways to choose which.\n\n"
            "That is all the binomial theorem is: the coefficients are counts of **how many ways** you can "
            "pick the terms."
        ),
        core=(
            "$$(1 + x)^n = \\binom{n}{0} + \\binom{n}{1}x + \\binom{n}{2}x^2 + \\cdots + \\binom{n}{n}x^n$$\n\n"
            "The coefficient of $x^r$ is $\\binom{n}{r}$, the number of ways to choose which $r$ of the $n$ "
            "brackets contribute an $x$.\n\n"
            "Pascal's triangle builds these quickly: each entry is the sum of the two above it. For CAT, "
            "the two things worth knowing cold are how to pick out a specific term, and the fact that all the "
            "coefficients together sum to $2^n$ (set $x = 1$)."
        ),
        examples=[
            EX(
                stem="Find the coefficient of $x^3$ in $(1+x)^7$.",
                solution=(
                    "The coefficient is $\\binom73 = \\dfrac{7!}{3! \\, 4!} = \\dfrac{7 \\times 6 \\times 5}{3 \\times 2 \\times 1} = 35$."
                ),
                alt="From Pascal's triangle, row 7 reads 1, 7, 21, 35, 35, 21, 7, 1 — the entry for $x^3$ is the fourth, which is 35.",
            ),
            EX(
                stem="Find the sum of all the binomial coefficients in $(1+x)^6$.",
                solution=(
                    "Setting $x = 1$ turns the left side into $2^6$ and the right side into the plain sum of "
                    "all the coefficients.\n\n"
                    "So the sum is $2^6 = 64$.\n\n"
                    "Check against row 6: $1 + 6 + 15 + 20 + 15 + 6 + 1 = 64$."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Binomial expansion",
                body="$(a+b)^n = \\sum_{r=0}^{n} \\binom{n}{r} a^{n-r} b^r$",
                example="$(a+b)^3 = a^3 + 3a^2b + 3ab^2 + b^3$.",
            ),
            FC(
                title="General term",
                body="The term with $b^r$ is $T_{r+1} = \\binom{n}{r} a^{n-r} b^r$.",
                example="In $(2+x)^5$, the $x^2$ term is $\\binom52 2^3 x^2 = 80x^2$.",
            ),
            FC(
                title="Sum of coefficients",
                body="Substituting $x = 1$ gives the sum of all coefficients: $2^n$ for $(1+x)^n$.",
                example="$(1+x)^{10}$ has coefficients summing to 1024.",
            ),
        ],
        traps=[
            "Off-by-one on the term number. The term containing $b^r$ is the $(r+1)$th term.",
            "Forgetting to raise the numerical part too. In $(2+x)^5$ the powers of 2 matter.",
            "Assuming the middle coefficient is always the largest. It is, but only when $a = b = 1$.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.modern.series-sequences-hybrids",
        prereq="Arithmetic and geometric progressions.",
        methods=[
            Method(
                name="Standard summation formulas",
                recognise="the sum of the first n squares, cubes, or integers.",
                steps=[
                    "$\\sum n = \\dfrac{n(n+1)}{2}$, $\\sum n^2 = \\dfrac{n(n+1)(2n+1)}{6}$, $\\sum n^3 = \\left(\\dfrac{n(n+1)}{2}\\right)^2$.",
                    "Match the series to the right formula, then substitute.",
                    "Note the sum of cubes is the square of the sum of integers — a useful check.",
                ],
                worked="$\\sum_{1}^{10} n^2 = \\dfrac{10 \\times 11 \\times 21}{6} = 385$.",
            ),
            Method(
                name="Spotting the pattern in an unfamiliar series",
                recognise="a list of numbers with the next term wanted, and no obvious AP or GP.",
                steps=[
                    "Write the differences between consecutive terms.",
                    "If those are constant it is an AP; if they themselves form a pattern, look at second differences.",
                    "Check ratios instead if the terms grow quickly.",
                ],
                worked="2, 6, 12, 20, 30 has differences 4, 6, 8, 10, so the next term is $30 + 12 = 42$.",
            ),
        ],
        checklist=[
            "Recall the three standard summation formulas.",
            "Use differences and ratios to identify an unfamiliar pattern.",
        ],
        intuition=(
            "Some sequences grow by **adding** the same thing each time: 3, 7, 11, 15 — always plus 4. That is "
            "an arithmetic progression, and it is like climbing stairs of equal height.\n\n"
            "Others grow by **multiplying**: 3, 6, 12, 24 — always doubling. That is a geometric progression, "
            "and it is like a rumour spreading, each round bigger than the last.\n\n"
            "Spotting which one you are looking at is most of the work."
        ),
        core=(
            "For an arithmetic progression, check that consecutive differences are constant. For a geometric "
            "progression, check that consecutive **ratios** are constant.\n\n"
            "The sum of an AP has a lovely shortcut: pair the first term with the last, the second with the "
            "second-last, and each pair has the same total. That is why the sum is just the average of the "
            "first and last terms, times how many terms there are.\n\n"
            "For hybrid or pattern-spotting questions, write out the differences between consecutive terms. If "
            "those differences themselves form a recognisable pattern, you have found the rule."
        ),
        examples=[
            EX(
                stem="Find the sum of the first 20 terms of 5, 9, 13, 17, ...",
                solution=(
                    "The common difference is 4, so this is an AP with $a = 5$ and $d = 4$.\n\n"
                    "The 20th term is $a + 19d = 5 + 76 = 81$.\n\n"
                    "Sum $= \\dfrac{n}{2}(\\text{first} + \\text{last}) = \\dfrac{20}{2}(5 + 81) = 10 \\times 86 = 860$."
                ),
                alt="Pairing shows why: 5 with 81, 9 with 77, and so on — ten pairs each totalling 86.",
            ),
            EX(
                stem="Find the next term in 2, 6, 12, 20, 30, ...",
                solution=(
                    "The differences are 4, 6, 8, 10 — increasing by 2 each time, so the next difference is 12.\n\n"
                    "The next term is $30 + 12 = 42$.\n\n"
                    "(The pattern is $n(n+1)$: $1 \\times 2$, $2 \\times 3$, $3 \\times 4$, and so on.)"
                ),
                alt="When a sequence is neither arithmetic nor geometric, the differences are the first place to look.",
            ),
        ],
        formulas=[
            FC(
                title="Arithmetic progression",
                body="$n$th term $= a + (n-1)d$. Sum $= \\dfrac{n}{2}[2a + (n-1)d] = \\dfrac{n}{2}(\\text{first} + \\text{last})$.",
                example="$a = 3$, $d = 5$, $n = 10$: last term 48, sum $= 5 \\times 51 = 255$.",
            ),
            FC(
                title="Geometric progression",
                body="$n$th term $= ar^{n-1}$. Sum of $n$ terms $= \\dfrac{a(r^n - 1)}{r - 1}$ for $r \\neq 1$.",
                example="$a = 2$, $r = 3$, $n = 4$: terms 2, 6, 18, 54 summing to 80.",
            ),
            FC(
                title="Infinite geometric sum",
                body="If $|r| < 1$, the sum to infinity is $\\dfrac{a}{1 - r}$.",
                example="$1 + \\frac12 + \\frac14 + \\cdots = \\dfrac{1}{1 - 0.5} = 2$.",
            ),
        ],
        traps=[
            "Using $a + nd$ for the $n$th term. It is $a + (n-1)d$ — the first term has taken no steps yet.",
            "Applying the infinite-sum formula when $|r| \\geq 1$, where the series does not converge.",
            "Assuming a sequence is arithmetic after checking only one difference. Check at least two.",
        ],
        minutes=7,
    ),
]
