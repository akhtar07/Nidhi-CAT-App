"""Algebra lessons."""

from __future__ import annotations

from . import EX, FC, LessonSpec, Method

SPECS = [
    LessonSpec(
        mt="qa.algebra.linear-equations",
        prereq="Comfort rearranging an equation, and turning a sentence into symbols.",
        methods=[
            Method(
                name="Two equations in two unknowns",
                recognise="two separate facts about two unknown quantities.",
                steps=[
                    "Line the equations up with the variables in the same order.",
                    "Eliminate one variable by adding or subtracting suitable multiples, or substitute one equation into the other.",
                    "Solve for the survivor, then back-substitute for the other.",
                ],
                worked="$2x + 3y = 23$ and $x - y = 4$ give $x = y + 4$, so $2(y+4) + 3y = 23$, hence $5y = 15$, $y = 3$ and $x = 7$.",
            ),
            Method(
                name="Sum and difference",
                recognise="'the sum of two numbers is 40 and their difference is 8'.",
                steps=[
                    "Add the two facts to get twice the larger; halve it.",
                    "Subtract them to get twice the smaller; halve that.",
                    "This is faster than full elimination and worth recognising on sight.",
                ],
                worked="Sum 40, difference 8 give $\\dfrac{48}{2} = 24$ and $\\dfrac{32}{2} = 16$.",
            ),
            Method(
                name="Coins, tickets and mixed-item word problems",
                recognise="a count of items and a total value, with items of differing worth.",
                steps=[
                    "Write one equation for the number of items and one for the total value.",
                    "The value equation multiplies each count by its denomination.",
                    "Solve the pair as usual.",
                ],
                worked="30 coins of Rs. 1 and Rs. 5 worth Rs. 78 give $x + y = 30$ and $x + 5y = 78$, so $y = 12$.",
            ),
        ],
        checklist=[
            "Solve a two-variable system by both elimination and substitution.",
            "Spot a sum-and-difference pair and answer it in one line.",
            "Turn a worded count-and-value situation into two equations.",
        ],
        intuition=(
            "A balance scale with the same weight on both pans stays level. Add 3 kg to one side and you "
            "must add 3 kg to the other, or it tips. An equation is that scale, and the equals sign is the "
            "pivot.\n\n"
            "Solving means peeling away everything around the unknown, doing the identical thing to both "
            "sides each time, until the unknown sits alone."
        ),
        core=(
            "One equation with one unknown pins it down. One equation with **two** unknowns does not — "
            "$x + y = 10$ has endless solutions. You need as many independent equations as unknowns.\n\n"
            "To solve a pair, get rid of one variable. **Elimination** scales the two equations so one "
            "variable has matching coefficients, then subtracts. **Substitution** rearranges one equation "
            "and plugs it into the other. Both work; elimination is usually faster when coefficients are tidy."
        ),
        examples=[
            EX(
                stem="Solve $2x + 3y = 16$ and $3x - y = 2$.",
                solution=(
                    "The second equation gives $y = 3x - 2$. Substitute into the first:\n\n"
                    "$2x + 3(3x - 2) = 16$, so $2x + 9x - 6 = 16$, giving $11x = 22$ and $x = 2$.\n\n"
                    "Then $y = 3(2) - 2 = 4$.\n\nCheck: $2(2) + 3(4) = 16$ and $3(2) - 4 = 2$. Both hold."
                ),
                alt="By elimination: multiply the second by 3 to get $9x - 3y = 6$, add to the first, and the $y$ terms cancel to give $11x = 22$.",
            ),
            EX(
                stem="A box has 20 coins of Rs. 5 and Rs. 10, worth Rs. 145 in total. How many Rs. 5 coins are there?",
                solution=(
                    "Let $x$ be the number of Rs. 5 coins, so $20 - x$ are Rs. 10 coins.\n\n"
                    "$5x + 10(20 - x) = 145$\n\n"
                    "$5x + 200 - 10x = 145$, so $-5x = -55$ and $x = 11$.\n\n"
                    "There are 11 five-rupee coins and 9 ten-rupee coins. Check: $55 + 90 = 145$."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Solving a 2 by 2 system",
                body="For $a_1x + b_1y = c_1$ and $a_2x + b_2y = c_2$: $x = \\dfrac{c_1b_2 - c_2b_1}{a_1b_2 - a_2b_1}$.",
                example="$2x + 3y = 16$, $3x - y = 2$ gives $x = \\dfrac{16(-1) - 2(3)}{2(-1) - 3(3)} = \\dfrac{-22}{-11} = 2$.",
            ),
            FC(
                title="When there is no unique solution",
                body="If $a_1b_2 = a_2b_1$ the lines are parallel: either no solution, or infinitely many if the equations are multiples of each other.",
                example="$2x + 4y = 6$ and $x + 2y = 3$ are the same line, so every point on it is a solution.",
            ),
        ],
        traps=[
            "Doing something to one side of the equation and forgetting the other.",
            "Sign errors when subtracting one equation from another. Write out the subtraction rather than doing it in your head.",
            "Not checking the answer back in both original equations. It takes ten seconds and catches most mistakes.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.algebra.integer-solutions",
        prereq="Linear equations, and comfort with divisibility.",
        methods=[
            Method(
                name="Counting positive integer solutions",
                recognise="$ax + by = c$ with both unknowns required to be positive whole numbers.",
                steps=[
                    "Solve for one variable in terms of the other.",
                    "Find the smallest value of the free variable that makes the other a positive integer.",
                    "Step forward by $\\dfrac{b}{\\gcd(a,b)}$ and count how many fit before the other goes non-positive.",
                ],
                worked="$3x + 5y = 100$ with both positive: $100 - 5y$ must be a positive multiple of 3, which forces $y = 2, 5, 8, 11, 14, 17$ — six solutions.",
            ),
            Method(
                name="Allowing zero as well",
                recognise="'non-negative' rather than 'positive'.",
                steps=[
                    "Do exactly the same count, but let each variable reach 0.",
                    "This usually adds one or two solutions at the ends of the range.",
                ],
                worked="The same equation with non-negatives adds $y = 20$, which gives $x = 0$ — seven solutions rather than six.",
            ),
        ],
        checklist=[
            "Decide which variable to make the subject so divisibility is easiest to read.",
            "Find the step size between consecutive solutions.",
            "Count solutions for positive and non-negative constraints separately.",
        ],
        intuition=(
            "You have only Rs. 5 and Rs. 7 coins and need to pay exactly Rs. 43. You cannot hand over half a "
            "coin, so most combinations simply will not work. The question is not 'what is $x$' but 'how many "
            "whole-number combinations exist at all'.\n\n"
            "That restriction to whole numbers is what makes these questions different from ordinary equations."
        ),
        core=(
            "For $ax + by = c$ with $x, y$ whole numbers, the practical method is to sweep one variable "
            "through its possible range and test whether the rest divides cleanly.\n\n"
            "Since $x$ cannot be negative and $ax \\leq c$, you only need to try $x = 0, 1, 2, \\ldots$ up to "
            "$\\lfloor c/a \\rfloor$. For each, check whether $c - ax$ is a multiple of $b$.\n\n"
            "Solutions, when they exist, are evenly spaced: increasing $x$ by $b$ and decreasing $y$ by $a$ "
            "always lands on another solution. So once you find one, you can step to all the others."
        ),
        examples=[
            EX(
                stem="How many non-negative integer solutions does $3x + 5y = 30$ have?",
                solution=(
                    "Sweep $y$ from 0 upward and check whether $30 - 5y$ is divisible by 3.\n\n"
                    "$y = 0$: $30$, divisible by 3, so $x = 10$. Valid.\n"
                    "$y = 1$: $25$, not divisible by 3.\n"
                    "$y = 2$: $20$, not divisible by 3.\n"
                    "$y = 3$: $15$, so $x = 5$. Valid.\n"
                    "$y = 4$: $10$, no. $y = 5$: $5$, no. $y = 6$: $0$, so $x = 0$. Valid.\n\n"
                    "That gives 3 solutions: $(10, 0)$, $(5, 3)$ and $(0, 6)$."
                ),
                alt="Notice the solutions step by 5 in $x$ and 3 in $y$ — exactly the two coefficients, swapped.",
            ),
        ],
        formulas=[
            FC(
                title="When solutions exist",
                body="$ax + by = c$ has integer solutions if and only if $\\gcd(a, b)$ divides $c$.",
                example="$4x + 6y = 9$ has none, since $\\gcd(4,6) = 2$ does not divide 9.",
            ),
            FC(
                title="Stepping between solutions",
                body="From one solution $(x_0, y_0)$, every other is $(x_0 + kb', y_0 - ka')$ where $a' = a/\\gcd$ and $b' = b/\\gcd$.",
                example="From $(10, 0)$ for $3x + 5y = 30$: subtract 5 from $x$ and add 3 to $y$ to get $(5, 3)$.",
            ),
        ],
        traps=[
            "Missing the boundary cases $x = 0$ or $y = 0$. 'Non-negative' includes zero; 'positive' does not.",
            "Reading 'positive integers' as 'non-negative integers'. That usually changes the count by one or two.",
            "Sweeping the variable with the smaller coefficient, which means many more cases to test. Sweep the larger one.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.algebra.quadratic-equations",
        prereq="Factorising, and the idea that a product is zero only if a factor is zero.",
        methods=[
            Method(
                name="Sum and product of roots",
                recognise="the question asks about the roots without needing their individual values.",
                steps=[
                    "For $ax^2 + bx + c = 0$, the sum is $-\\dfrac{b}{a}$ and the product is $\\dfrac{c}{a}$.",
                    "Express what is asked in terms of those two. For instance $\\alpha^2 + \\beta^2 = (\\alpha+\\beta)^2 - 2\\alpha\\beta$.",
                    "Substitute. You never need to solve the equation.",
                ],
                worked="For $x^2 - 7x + 12$, sum 7 and product 12, so $\\alpha^2 + \\beta^2 = 49 - 24 = 25$.",
            ),
            Method(
                name="Nature of the roots from the discriminant",
                recognise="'real and distinct', 'equal', 'no real roots', or a condition on a parameter.",
                steps=[
                    "Compute $D = b^2 - 4ac$.",
                    "$D > 0$ means two distinct real roots, $D = 0$ means one repeated root, $D < 0$ means none.",
                    "If a parameter is involved, turn the condition on $D$ into an inequality in that parameter.",
                ],
                worked="$x^2 + kx + 9$ has equal roots when $k^2 - 36 = 0$, so $k = \\pm 6$.",
            ),
            Method(
                name="Finding a specific root",
                recognise="the larger root, the smaller root, or a numerical value is wanted.",
                steps=[
                    "Try factorising first — CAT quadratics usually factorise.",
                    "Otherwise use $x = \\dfrac{-b \\pm \\sqrt{D}}{2a}$.",
                    "The larger root takes the plus sign when $a > 0$.",
                ],
                worked="$x^2 - 5x + 6$ factorises to $(x-2)(x-3)$, so the roots are 2 and 3.",
            ),
            Method(
                name="Building an equation from its roots",
                recognise="roots are given, or described, and the equation is wanted.",
                steps=[
                    "Compute the sum $S$ and product $P$ of the required roots.",
                    "The equation is $x^2 - Sx + P = 0$.",
                    "Scale up if integer coefficients are needed.",
                ],
                worked="Roots 3 and $-5$ give $S = -2$, $P = -15$, so $x^2 + 2x - 15 = 0$.",
            ),
        ],
        checklist=[
            "Answer a question about the roots without solving the equation.",
            "Read off the nature of the roots from the discriminant.",
            "Construct an equation from a required sum and product.",
        ],
        intuition=(
            "Throw a ball straight up. It rises, slows, stops, and falls back. Plot its height against time "
            "and you get an arch — a parabola. A quadratic equation asks: at what times was the ball at "
            "ground level? Those two moments are the **roots**.\n\n"
            "Sometimes the ball never reaches the height you asked about, and then there are no real roots at "
            "all. The discriminant is what tells you which case you are in, before you do any work."
        ),
        core=(
            "For $ax^2 + bx + c = 0$, the discriminant $D = b^2 - 4ac$ decides everything:\n\n"
            "$D > 0$: two distinct real roots (the parabola cuts the axis twice).\n"
            "$D = 0$: one repeated root (it just touches).\n"
            "$D < 0$: no real roots (it misses entirely).\n\n"
            "You often do not need the roots themselves. Vieta's relations give their sum and product straight "
            "from the coefficients, which answers a surprising share of CAT questions without any solving."
        ),
        examples=[
            EX(
                stem="Find the roots of $x^2 - 7x + 12 = 0$.",
                solution=(
                    "Look for two numbers that multiply to 12 and add to 7. Those are 3 and 4.\n\n"
                    "So $x^2 - 7x + 12 = (x - 3)(x - 4) = 0$, giving $x = 3$ or $x = 4$.\n\n"
                    "Check: $3 + 4 = 7$ and $3 \\times 4 = 12$. Both match the coefficients."
                ),
                alt="By formula: $x = \\dfrac{7 \\pm \\sqrt{49 - 48}}{2} = \\dfrac{7 \\pm 1}{2}$, so 4 or 3.",
            ),
            EX(
                stem="Without solving, find the sum and product of the roots of $3x^2 - 12x + 9 = 0$.",
                solution=(
                    "Sum of roots $= -\\dfrac{b}{a} = -\\dfrac{-12}{3} = 4$.\n\n"
                    "Product of roots $= \\dfrac{c}{a} = \\dfrac{9}{3} = 3$.\n\n"
                    "(The roots happen to be 1 and 3, which do sum to 4 and multiply to 3.)"
                ),
                alt="Vieta's relations save real time when the question only asks about the sum or product, not the roots themselves.",
            ),
        ],
        formulas=[
            FC(
                title="Quadratic formula",
                body="$x = \\dfrac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$",
                example="For $2x^2 - 4x - 6 = 0$: $x = \\dfrac{4 \\pm \\sqrt{16 + 48}}{4} = \\dfrac{4 \\pm 8}{4}$, so 3 or $-1$.",
            ),
            FC(
                title="Discriminant",
                body="$D = b^2 - 4ac$. Positive means two real roots, zero means one repeated root, negative means none.",
                example="$x^2 + 2x + 5$ has $D = 4 - 20 = -16 < 0$, so it never touches the $x$-axis.",
            ),
            FC(
                title="Vieta's relations",
                body="Sum of roots $= -\\dfrac{b}{a}$, product of roots $= \\dfrac{c}{a}$.",
                example="$x^2 - 5x + 6$: sum 5, product 6, consistent with roots 2 and 3.",
            ),
        ],
        traps=[
            "Sign slips on $-\\dfrac{b}{a}$. If $b$ is already negative, the sum of roots is positive.",
            "Forgetting to divide by $a$ when $a$ is not 1. The relations use $b/a$ and $c/a$, not $b$ and $c$.",
            "Concluding 'no solution' when $D < 0$ — there are no **real** roots, but complex roots still exist.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.algebra.polynomials-remainder-factor",
        prereq="Substituting a value into an expression, and basic algebra.",
        methods=[
            Method(
                name="Remainder when dividing by a linear factor",
                recognise="'find the remainder when $p(x)$ is divided by $x - a$'.",
                steps=[
                    "The remainder theorem says the answer is simply $p(a)$.",
                    "Substitute and evaluate — no long division needed.",
                    "For $x + a$, substitute $-a$.",
                ],
                worked="$p(x) = x^3 - 2x + 5$ divided by $x - 2$ leaves $p(2) = 8 - 4 + 5 = 9$.",
            ),
            Method(
                name="Finding an unknown coefficient",
                recognise="a polynomial with a letter in it, plus a stated factor or remainder.",
                steps=[
                    "If $x - a$ is a factor, then $p(a) = 0$; if the remainder is $r$, then $p(a) = r$.",
                    "Substitute and solve the resulting equation for the unknown.",
                ],
                worked="If $x - 3$ divides $x^2 + kx - 6$ then $9 + 3k - 6 = 0$, so $k = -1$.",
            ),
        ],
        checklist=[
            "Use the remainder theorem instead of dividing.",
            "Translate 'is a factor' into 'the polynomial vanishes there'.",
            "Solve for a missing coefficient from a factor or remainder condition.",
        ],
        intuition=(
            "Divide 17 by 5 and you get 3 remainder 2. Polynomials divide the same way, but there is a "
            "wonderful shortcut: to find the remainder when dividing by $(x - a)$, you do not divide at all. "
            "You just plug in $x = a$.\n\n"
            "It feels like cheating the first time you see it, but it follows directly from what division means."
        ),
        core=(
            "Any division can be written as $p(x) = (x - a) \\cdot q(x) + r$, where $r$ is the remainder. "
            "Now substitute $x = a$. The $(x - a)$ term becomes zero and wipes out the whole quotient, leaving "
            "$p(a) = r$.\n\n"
            "That is the **Remainder Theorem**. The **Factor Theorem** is the special case where $r = 0$: "
            "$(x - a)$ divides $p(x)$ exactly when $p(a) = 0$. So checking whether something is a factor is a "
            "single substitution."
        ),
        examples=[
            EX(
                stem="Find the remainder when $x^3 - 4x^2 + 5x - 2$ is divided by $(x - 3)$.",
                solution=(
                    "By the Remainder Theorem, substitute $x = 3$:\n\n"
                    "$27 - 4(9) + 5(3) - 2 = 27 - 36 + 15 - 2 = 4$.\n\n"
                    "The remainder is 4. No long division needed."
                ),
            ),
            EX(
                stem="Find $k$ if $(x - 2)$ is a factor of $x^3 + kx^2 - 4x + 4$.",
                solution=(
                    "If $(x-2)$ is a factor then substituting $x = 2$ must give zero:\n\n"
                    "$8 + 4k - 8 + 4 = 0$\n\n"
                    "$4k + 4 = 0$, so $k = -1$.\n\n"
                    "Check with $k = -1$: $8 - 4 - 8 + 4 = 0$. Correct."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Remainder Theorem",
                body="The remainder when $p(x)$ is divided by $(x - a)$ is $p(a)$.",
                example="$p(x) = x^2 + 3x + 1$ divided by $(x - 2)$ leaves $p(2) = 4 + 6 + 1 = 11$.",
            ),
            FC(
                title="Factor Theorem",
                body="$(x - a)$ is a factor of $p(x)$ if and only if $p(a) = 0$.",
                example="$p(x) = x^2 - 5x + 6$ has $p(2) = 0$, so $(x - 2)$ is a factor.",
            ),
        ],
        traps=[
            "Using $x = -a$ when dividing by $(x - a)$. Set the divisor to zero: $x - a = 0$ means $x = a$.",
            "With a divisor like $(x + 3)$, the substitution is $x = -3$, not $x = 3$.",
            "Applying the theorem to a quadratic divisor. It only works for linear divisors.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.algebra.inequalities-modulus",
        prereq="Solving equations, and the number line as a picture.",
        methods=[
            Method(
                name="Quadratic inequalities",
                recognise="a quadratic expression compared to zero.",
                steps=[
                    "Find the roots, which split the line into intervals.",
                    "For an upward parabola the expression is negative **between** the roots and positive outside.",
                    "Pick the intervals the inequality asks for, minding whether the endpoints are included.",
                ],
                worked="$x^2 - 5x + 6 < 0$ has roots 2 and 3, so the answer is $2 < x < 3$.",
            ),
            Method(
                name="Counting integer solutions of a modulus inequality",
                recognise="$|x - a| < b$ or similar, asking how many integers satisfy it.",
                steps=[
                    "Read $|x - a| < b$ as 'distance from $a$ is less than $b$', giving $a - b < x < a + b$.",
                    "Count the integers strictly inside, or inclusive if the sign allows equality.",
                ],
                worked="$|x - 4| \\le 3$ gives $1 \\le x \\le 7$: seven integers.",
            ),
        ],
        checklist=[
            "Read a modulus as a distance on the number line.",
            "Decide where a quadratic is positive or negative from its roots.",
            "Count integers in an interval without off-by-one errors.",
        ],
        intuition=(
            "$|x|$ just means 'how far is $x$ from zero, ignoring direction'. Both 5 and $-5$ are five steps "
            "from zero, so both have modulus 5.\n\n"
            "So $|x - 3| < 4$ reads as: how far can $x$ wander from 3 before it is more than 4 steps away? "
            "Answer: it can go 4 steps either way, so anywhere strictly between $-1$ and $7$."
        ),
        core=(
            "Turn modulus into a range. $|x - a| < b$ becomes $a - b < x < a + b$, a single interval centred "
            "on $a$. $|x - a| > b$ becomes two separate pieces: $x < a - b$ or $x > a + b$.\n\n"
            "For inequalities generally, the one rule that catches everyone: **multiplying or dividing by a "
            "negative number flips the direction**. And for a product like $(x - p)(x - q) < 0$, the product "
            "is negative exactly between the two roots, because that is where the factors have opposite signs."
        ),
        examples=[
            EX(
                stem="How many integers satisfy $|x - 5| < 3$?",
                solution=(
                    "$|x - 5| < 3$ means $x$ is within 3 of 5, so $2 < x < 8$.\n\n"
                    "Strictly between, so the integers are 3, 4, 5, 6 and 7.\n\n"
                    "That is 5 integers."
                ),
                alt="For a strict inequality $|x - a| < b$ with whole $b$, the count is always $2b - 1$: here $2(3) - 1 = 5$.",
            ),
            EX(
                stem="Solve $(x - 2)(x + 3) < 0$.",
                solution=(
                    "The roots are $x = 2$ and $x = -3$. These split the line into three regions.\n\n"
                    "For $x < -3$: both factors negative, product positive.\n"
                    "For $-3 < x < 2$: first negative, second positive, product negative. This is what we want.\n"
                    "For $x > 2$: both positive, product positive.\n\n"
                    "So the solution is $-3 < x < 2$."
                ),
                alt="For a product of two linear factors, 'less than zero' always means strictly between the roots.",
            ),
        ],
        formulas=[
            FC(
                title="Modulus as a range",
                body="$|x - a| < b$ means $a - b < x < a + b$. $|x - a| > b$ means $x < a - b$ or $x > a + b$.",
                example="$|x + 2| \\leq 5$ becomes $-7 \\leq x \\leq 3$ (write $x + 2$ as $x - (-2)$).",
            ),
            FC(
                title="Sign of a product",
                body="$(x-p)(x-q) < 0$ holds strictly between the roots; $> 0$ holds outside them.",
                example="$(x-1)(x-4) > 0$ gives $x < 1$ or $x > 4$.",
            ),
            FC(
                title="The flip rule",
                body="Multiplying or dividing an inequality by a negative number reverses the sign.",
                example="From $-2x > 6$, dividing by $-2$ gives $x < -3$, not $x > -3$.",
            ),
        ],
        traps=[
            "Forgetting to flip the inequality when multiplying by a negative.",
            "Treating $|x - a| > b$ as one interval. It is two disjoint pieces.",
            "Counting endpoints when the inequality is strict, or omitting them when it is not.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.algebra.logarithms",
        prereq="Powers and indices — a logarithm is only an index written the other way round.",
        methods=[
            Method(
                name="Evaluating a logarithm directly",
                recognise="$\\log_a b$ with a clean answer.",
                steps=[
                    "Ask: what power of the base gives this number?",
                    "Rewrite the number as a power of the base if it is not obvious.",
                ],
                worked="$\\log_2 32 = 5$ because $2^5 = 32$.",
            ),
            Method(
                name="Combining logs with the same base",
                recognise="several logs added or subtracted, or a coefficient in front of one.",
                steps=[
                    "Use $\\log a + \\log b = \\log ab$ and $\\log a - \\log b = \\log \\dfrac{a}{b}$.",
                    "Move any coefficient inside as a power: $n\\log a = \\log a^n$.",
                    "Then evaluate the single log that remains.",
                ],
                worked="$\\log_3 9 + \\log_3 27 = \\log_3 243 = 5$.",
            ),
            Method(
                name="Solving an equation containing a log",
                recognise="the unknown appears inside a logarithm.",
                steps=[
                    "Collect everything into a single logarithm on one side.",
                    "Convert to exponential form: $\\log_a b = c$ means $a^c = b$.",
                    "Solve, then discard any root that makes a logarithm's argument zero or negative.",
                ],
                worked="$\\log_2(x - 3) = 4$ gives $x - 3 = 16$, so $x = 19$.",
            ),
        ],
        checklist=[
            "Convert between logarithmic and exponential form in either direction.",
            "Combine and split logs using the product, quotient and power rules.",
            "Reject solutions that would need the log of a non-positive number.",
        ],
        intuition=(
            "A logarithm answers one question: **how many times do I multiply this number by itself to get "
            "that number?**\n\n"
            "$\\log_2 8$ asks: how many 2s multiplied together make 8? Since $2 \\times 2 \\times 2 = 8$, the "
            "answer is 3. That is all a log is — an exponent, written the other way round."
        ),
        core=(
            "$\\log_b x = y$ and $b^y = x$ say exactly the same thing. Being fluent at flipping between those "
            "two forms solves most log questions immediately.\n\n"
            "The rules all come from what exponents already do. Multiplying powers adds their exponents, so "
            "logs of a product add. Dividing subtracts. Raising to a power multiplies. Nothing new to memorise "
            "if you remember where they come from."
        ),
        examples=[
            EX(
                stem="Evaluate $\\log_3 81$.",
                solution=(
                    "How many 3s multiply together to make 81?\n\n"
                    "$3 \\times 3 = 9$, $\\times 3 = 27$, $\\times 3 = 81$. That is four 3s.\n\n"
                    "So $\\log_3 81 = 4$."
                ),
            ),
            EX(
                stem="Evaluate $\\log_2 8 + \\log_2 4$.",
                solution=(
                    "Separately: $\\log_2 8 = 3$ and $\\log_2 4 = 2$, so the sum is 5.\n\n"
                    "Or use the product rule: $\\log_2 8 + \\log_2 4 = \\log_2 (8 \\times 4) = \\log_2 32 = 5$, "
                    "since $2^5 = 32$.\n\nBoth routes agree."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Definition",
                body="$\\log_b x = y$ means exactly $b^y = x$.",
                example="$\\log_5 125 = 3$ because $5^3 = 125$.",
            ),
            FC(
                title="The three rules",
                body=(
                    "$\\log_b(mn) = \\log_b m + \\log_b n$, "
                    "$\\log_b\\left(\\dfrac{m}{n}\\right) = \\log_b m - \\log_b n$, "
                    "$\\log_b(m^k) = k\\log_b m$."
                ),
                example="$\\log 8 = \\log 2^3 = 3\\log 2$.",
            ),
            FC(
                title="Change of base",
                body="$\\log_b x = \\dfrac{\\log_a x}{\\log_a b}$ for any valid base $a$.",
                example="$\\log_8 32 = \\dfrac{\\log_2 32}{\\log_2 8} = \\dfrac{5}{3}$.",
            ),
        ],
        traps=[
            "Writing $\\log(m + n)$ as $\\log m + \\log n$. The product rule applies to products, never to sums.",
            "Forgetting that logs of zero or negative numbers are undefined.",
            "Losing track of the base. $\\log_2 8$ and $\\log_8 2$ are very different numbers.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.algebra.surds-indices",
        prereq="The index laws, and multiplying out brackets.",
        methods=[
            Method(
                name="Simplifying with index laws",
                recognise="powers multiplied, divided, or raised to further powers.",
                steps=[
                    "Rewrite every base as a power of the same prime where possible.",
                    "Apply $a^m a^n = a^{m+n}$, $\\dfrac{a^m}{a^n} = a^{m-n}$ and $(a^m)^n = a^{mn}$.",
                    "Compare exponents if the equation has matching bases on both sides.",
                ],
                worked="$\\dfrac{8^4}{4^5} = \\dfrac{2^{12}}{2^{10}} = 2^2 = 4$.",
            ),
            Method(
                name="Rationalising a denominator",
                recognise="a surd in the bottom of a fraction, often $a + \\sqrt{b}$.",
                steps=[
                    "Multiply top and bottom by the conjugate, $a - \\sqrt{b}$.",
                    "The denominator becomes $a^2 - b$, which is rational.",
                    "Simplify the numerator.",
                ],
                worked="$\\dfrac{1}{3 + \\sqrt{2}} = \\dfrac{3 - \\sqrt{2}}{9 - 2} = \\dfrac{3 - \\sqrt{2}}{7}$.",
            ),
        ],
        checklist=[
            "Bring several powers to a common base.",
            "Rationalise a denominator using the conjugate.",
            "Compare exponents once bases match, rather than evaluating the powers.",
        ],
        intuition=(
            "$2^5$ just means five 2s multiplied together. So $2^5 \\times 2^3$ is five 2s next to three 2s — "
            "eight 2s in total, which is $2^8$. You add the exponents because you are literally counting how "
            "many copies you have.\n\n"
            "Every index rule is that same counting argument. None of them need memorising if you picture the "
            "copies."
        ),
        core=(
            "Multiplying powers of the same base adds exponents; dividing subtracts them; a power of a power "
            "multiplies them.\n\n"
            "A **surd** is a root that will not simplify to a whole number, like $\\sqrt{2}$. The standard "
            "move is **rationalising**: to clear a surd out of a denominator, multiply top and bottom by the "
            "conjugate. Since $(a + \\sqrt{b})(a - \\sqrt{b}) = a^2 - b$, the roots vanish from the bottom. "
            "The value of the fraction never changes — you multiplied by 1 in disguise."
        ),
        examples=[
            EX(
                stem="Simplify $\\dfrac{3^7}{3^4}$.",
                solution=(
                    "Seven 3s on top, four 3s underneath. Four of them cancel, leaving three 3s.\n\n"
                    "$\\dfrac{3^7}{3^4} = 3^{7-4} = 3^3 = 27$."
                ),
            ),
            EX(
                stem="Rationalise $\\dfrac{1}{3 + \\sqrt{5}}$.",
                solution=(
                    "Multiply top and bottom by the conjugate $3 - \\sqrt{5}$:\n\n"
                    "$$\\frac{1}{3 + \\sqrt{5}} \\times \\frac{3 - \\sqrt{5}}{3 - \\sqrt{5}} = "
                    "\\frac{3 - \\sqrt{5}}{9 - 5} = \\frac{3 - \\sqrt{5}}{4}$$\n\n"
                    "The denominator is now a plain whole number."
                ),
                alt="The conjugate works because $(a+b)(a-b) = a^2 - b^2$, and squaring a square root removes it.",
            ),
        ],
        formulas=[
            FC(
                title="Index rules",
                body="$a^m \\times a^n = a^{m+n}$, $\\dfrac{a^m}{a^n} = a^{m-n}$, $(a^m)^n = a^{mn}$, $a^0 = 1$, $a^{-n} = \\dfrac{1}{a^n}$.",
                example="$\\dfrac{2^6 \\times 2^{-2}}{2^3} = 2^{6-2-3} = 2^1 = 2$.",
            ),
            FC(
                title="Fractional powers",
                body="$a^{1/n} = \\sqrt[n]{a}$ and $a^{m/n} = \\sqrt[n]{a^m}$.",
                example="$8^{2/3} = (\\sqrt[3]{8})^2 = 2^2 = 4$.",
            ),
            FC(
                title="Rationalising",
                body="Multiply numerator and denominator by the conjugate: $\\dfrac{1}{a + \\sqrt{b}} = \\dfrac{a - \\sqrt{b}}{a^2 - b}$.",
                example="$\\dfrac{1}{2 + \\sqrt{3}} = \\dfrac{2 - \\sqrt{3}}{4 - 3} = 2 - \\sqrt{3}$.",
            ),
        ],
        traps=[
            "Adding exponents when the bases differ. $2^3 \\times 3^2$ does not simplify to a single power.",
            "Writing $\\sqrt{a + b}$ as $\\sqrt{a} + \\sqrt{b}$. That is false — try $a = b = 9$.",
            "Sign errors in the conjugate. The conjugate of $a + \\sqrt{b}$ is $a - \\sqrt{b}$, flipping only the middle sign.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.algebra.functions",
        prereq="Substitution — a function is a rule you feed a number into.",
        methods=[
            Method(
                name="Composite functions",
                recognise="$f(g(x))$, or 'apply g then f'.",
                steps=[
                    "Work from the inside out: evaluate the inner function first.",
                    "Feed that result into the outer function.",
                    "Order matters — $f(g(x))$ is generally not $g(f(x))$.",
                ],
                worked="With $f(x) = 2x + 1$ and $g(x) = x^2$, $f(g(3)) = f(9) = 19$, while $g(f(3)) = g(7) = 49$.",
            ),
            Method(
                name="Inverse functions",
                recognise="'find $f^{-1}$', or a question that undoes the rule.",
                steps=[
                    "Write $y = f(x)$.",
                    "Swap $x$ and $y$, then make $y$ the subject.",
                    "Check by confirming $f(f^{-1}(x)) = x$.",
                ],
                worked="For $f(x) = 3x - 4$, swapping gives $x = 3y - 4$, so $f^{-1}(x) = \\dfrac{x + 4}{3}$.",
            ),
        ],
        checklist=[
            "Evaluate a composite in the right order.",
            "Find an inverse and verify it by composition.",
        ],
        intuition=(
            "A function is a machine. Put a number in the top, and a number comes out of the bottom. "
            "$f(x) = 2x + 3$ is the machine that doubles whatever you feed it and then adds 3.\n\n"
            "A **composite** function is two machines bolted together: the output of the first is poured "
            "straight into the second. An **inverse** function is the machine running backwards — it undoes "
            "what the original did."
        ),
        core=(
            "$(f \\circ g)(x)$ means $f(g(x))$: $g$ runs **first**, then $f$. The order matters, and reading "
            "it right to left is what keeps people out of trouble.\n\n"
            "The inverse $f^{-1}$ answers 'what input would have produced this output?'. To find it, write "
            "$y = f(x)$, swap the roles of $x$ and $y$, and solve. If $f$ doubles and adds 3, then $f^{-1}$ "
            "subtracts 3 and halves — the same steps, reversed and undone."
        ),
        examples=[
            EX(
                stem="If $f(x) = 3x + 1$ and $g(x) = x - 4$, find $(f \\circ g)(6)$.",
                solution=(
                    "Inside first: $g(6) = 6 - 4 = 2$.\n\n"
                    "Then feed that into $f$: $f(2) = 3(2) + 1 = 7$.\n\n"
                    "So $(f \\circ g)(6) = 7$."
                ),
                alt="Note $(g \\circ f)(6) = g(19) = 15$, a completely different answer. Order is not optional.",
            ),
            EX(
                stem="If $f(x) = 4x - 5$, find $f^{-1}(11)$.",
                solution=(
                    "We want the input that gives an output of 11.\n\n"
                    "$4x - 5 = 11$, so $4x = 16$ and $x = 4$.\n\n"
                    "So $f^{-1}(11) = 4$. Check: $f(4) = 16 - 5 = 11$."
                ),
                alt="The general inverse is $f^{-1}(y) = \\dfrac{y + 5}{4}$: add 5, then divide by 4 — undoing the original steps in reverse order.",
            ),
        ],
        formulas=[
            FC(
                title="Composition",
                body="$(f \\circ g)(x) = f(g(x))$ — apply $g$ first. In general $f \\circ g \\neq g \\circ f$.",
                example="$f(x) = x^2$, $g(x) = x+1$: $(f \\circ g)(2) = f(3) = 9$ but $(g \\circ f)(2) = g(4) = 5$.",
            ),
            FC(
                title="Inverse",
                body="$f^{-1}$ satisfies $f(f^{-1}(x)) = x$. Find it by setting $y = f(x)$ and solving for $x$.",
                example="$f(x) = 2x + 7$ gives $f^{-1}(x) = \\dfrac{x - 7}{2}$.",
            ),
        ],
        traps=[
            "Applying the outer function first. In $f(g(x))$, $g$ goes first.",
            "Reading $f^{-1}(x)$ as $\\dfrac{1}{f(x)}$. The superscript $-1$ means inverse, not reciprocal.",
            "Assuming every function has an inverse. It needs each output to come from exactly one input.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.algebra.maxima-minima",
        prereq="Quadratics, and the shape of a parabola.",
        methods=[
            Method(
                name="Vertex of a quadratic",
                recognise="a quadratic expression whose greatest or least value is wanted.",
                steps=[
                    "The turning point sits at $x = -\\dfrac{b}{2a}$.",
                    "Substitute back to get the extreme value.",
                    "If $a > 0$ the parabola opens upward, so this is a minimum; if $a < 0$, a maximum.",
                ],
                worked="$x^2 - 6x + 11$ turns at $x = 3$, giving a minimum of $9 - 18 + 11 = 2$.",
            ),
            Method(
                name="AM-GM for a sum with a fixed product",
                recognise="an expression like $x + \\dfrac{k}{x}$ for positive $x$.",
                steps=[
                    "The arithmetic mean is at least the geometric mean, so $x + \\dfrac{k}{x} \\ge 2\\sqrt{k}$.",
                    "Equality holds when the two terms are equal, which fixes the value of $x$.",
                    "Check the variable really is restricted to positive values — AM-GM needs that.",
                ],
                worked="$x + \\dfrac{9}{x}$ has minimum $2\\sqrt{9} = 6$, at $x = 3$.",
            ),
        ],
        checklist=[
            "Locate a parabola's vertex and say whether it is a maximum or a minimum.",
            "Apply AM-GM and state when equality is attained.",
        ],
        intuition=(
            "You have 40 metres of fencing and want to enclose the biggest possible rectangular garden. A long "
            "thin strip encloses almost nothing. So does a very short wide one. Somewhere in between is the "
            "best shape — and it turns out to be the square.\n\n"
            "That is the pattern behind most optimisation questions: when a total is fixed, the product or "
            "area is largest when the parts are **equal**."
        ),
        core=(
            "Two tools cover almost every CAT question here.\n\n"
            "**Quadratic vertex.** A parabola $ax^2 + bx + c$ turns at $x = -\\dfrac{b}{2a}$. If $a > 0$ it "
            "opens upward and that point is the minimum; if $a < 0$ it is the maximum.\n\n"
            "**AM-GM.** For positive numbers the arithmetic mean is at least the geometric mean, with equality "
            "only when all the numbers are equal. So for a fixed sum, the product peaks when the terms match — "
            "and for a fixed product, the sum bottoms out at the same place."
        ),
        examples=[
            EX(
                stem="Two positive numbers add to 20. What is their largest possible product?",
                solution=(
                    "Try a few: $1 \\times 19 = 19$, $5 \\times 15 = 75$, $9 \\times 11 = 99$, $10 \\times 10 = 100$.\n\n"
                    "The product peaks when the numbers are equal, at $10 \\times 10 = 100$.\n\n"
                    "This is AM-GM: with a fixed sum, equal parts maximise the product."
                ),
                alt="Algebraically, the product is $x(20 - x) = -x^2 + 20x$, a downward parabola with vertex at $x = 10$.",
            ),
            EX(
                stem="Find the minimum value of $f(x) = 2x^2 - 8x + 11$.",
                solution=(
                    "Since $a = 2 > 0$, the parabola opens upward, so the vertex is a minimum.\n\n"
                    "Vertex at $x = -\\dfrac{b}{2a} = -\\dfrac{-8}{4} = 2$.\n\n"
                    "$f(2) = 2(4) - 16 + 11 = 8 - 16 + 11 = 3$.\n\nThe minimum value is 3."
                ),
                alt=(
                    "Completing the square: $2(x^2 - 4x) + 11 = 2(x-2)^2 - 8 + 11 = 2(x-2)^2 + 3$. "
                    "A square is never negative, so the smallest value is 3, reached at $x = 2$."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Vertex of a parabola",
                body="$ax^2 + bx + c$ turns at $x = -\\dfrac{b}{2a}$. Minimum if $a > 0$, maximum if $a < 0$.",
                example="$x^2 - 6x + 5$ turns at $x = 3$, where the value is $-4$.",
            ),
            FC(
                title="AM-GM inequality",
                body="For positive $a, b$: $\\dfrac{a + b}{2} \\geq \\sqrt{ab}$, with equality only when $a = b$.",
                example="Fixed sum 12 gives a maximum product of $6 \\times 6 = 36$.",
            ),
        ],
        traps=[
            "Applying AM-GM to negative numbers. It requires all terms to be positive.",
            "Reporting the $x$ at which the extreme occurs when the question asked for the value there, or vice versa.",
            "Assuming the vertex is a minimum without checking the sign of $a$.",
        ],
        minutes=7,
    ),
]
