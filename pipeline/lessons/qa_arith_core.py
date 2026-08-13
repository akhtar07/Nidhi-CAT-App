"""
Core arithmetic lessons: percentages, profit & loss, ratio, averages, pipes & cisterns.

These five were previously the largest gap in the bank. Their JSON existed on disk but was not
declared anywhere in this package, so it could not be rebuilt or improved — and what was there
averaged 130 words, roughly a definition and one example, against banks of 30-40 questions each
spanning six or seven distinct archetypes. Declaring them here brings them back under
`build_lessons` and under `check_markdown`.

Depth target, per the Method docstring in __init__.py: one `Method` for every archetype the
topic's questions actually come in (cross-checked against qagen/templates/arith.py and the tags
on content/questions/*.json), so that a learner who reads the lesson has met every shape before
the drill shows it to her.
"""

from __future__ import annotations

from . import EX, FC, LessonSpec, Method

SPECS = [
    # ------------------------------------------------------------------ percentages
    LessonSpec(
        mt="qa.arith.percentages",
        prereq=(
            "Nothing beyond fractions. If you can see that $\\dfrac{1}{4}$ and 25 percent are "
            "the same thing written two ways, you are ready."
        ),
        intuition=(
            "Percent means **per hundred**. That is the whole of the definition: 37 percent is "
            "37 out of every 100, the way 'per hour' means 'for each hour'.\n\n"
            "Picture a chocolate bar scored into 100 tiny squares. Taking 37 percent means "
            "taking 37 squares. Now here is the part that trips people up all through this "
            "topic: if I take 37 percent of **your** bar and 37 percent of a bar twice the "
            "size, I have taken the same percentage but a very different amount of chocolate. "
            "A percentage is meaningless until you know what it is a percentage **of**.\n\n"
            "Almost every mistake in this topic is a mistake about that: the percentage was "
            "correct, but it was applied to the wrong bar."
        ),
        core=(
            "Two habits make this topic easy, and they are worth more than any formula.\n\n"
            "**Habit one: turn every percentage into a multiplier.** A 20 percent rise is "
            "$\\times 1.2$. A 20 percent fall is $\\times 0.8$. A 35 percent discount is "
            "$\\times 0.65$. Once changes are multipliers you can chain them by multiplying, "
            "and the order stops mattering — which is exactly why a 10 percent rise followed by "
            "a 10 percent fall does not return you to where you started: "
            "$1.1 \\times 0.9 = 0.99$, a 1 percent loss.\n\n"
            "**Habit two: name the base.** Write down what the 100 percent refers to before you "
            "compute anything. 'Twenty percent more than B' has B as its base. 'Twenty percent "
            "of the total' has the total as its base. When a question changes base halfway "
            "through — and CAT questions do this deliberately — you will notice.\n\n"
            "Learning a few fraction equivalents saves real seconds under time pressure, "
            "because they turn division into cancellation: "
            "$12.5\\% = \\dfrac{1}{8}$, $16\\tfrac{2}{3}\\% = \\dfrac{1}{6}$, "
            "$33\\tfrac{1}{3}\\% = \\dfrac{1}{3}$, $37.5\\% = \\dfrac{3}{8}$, "
            "$62.5\\% = \\dfrac{5}{8}$."
        ),
        methods=[
            Method(
                name="Successive percentage changes",
                recognise=(
                    "two or more changes applied one after another — 'increased by 20 percent, "
                    "then decreased by 15 percent', or a price marked up then discounted."
                ),
                steps=[
                    "Turn each change into a multiplier: a rise of $r\\%$ is $\\left(1 + \\dfrac{r}{100}\\right)$, a fall of $r\\%$ is $\\left(1 - \\dfrac{r}{100}\\right)$.",
                    "Multiply all the multipliers together.",
                    "Subtract 1 and multiply by 100 to read off the single net percentage change.",
                ],
                worked=(
                    "Up 20 percent then down 15 percent gives "
                    "$1.20 \\times 0.85 = 1.02$, so a net rise of 2 percent — not the "
                    "5 percent you get by subtracting."
                ),
            ),
            Method(
                name="Working backwards to the original",
                recognise=(
                    "the question gives you the value **after** a change and asks for the value "
                    "before it. 'After a 15 percent discount a shirt costs Rs. 850. Find the "
                    "marked price.'"
                ),
                steps=[
                    "Identify the multiplier that was applied.",
                    "Divide the final value by that multiplier. Do not subtract the percentage from the final value — the percentage was of the original, which is precisely the number you do not have yet.",
                ],
                worked=(
                    "Rs. 850 after a 15 percent discount means "
                    "$0.85 \\times \\text{MP} = 850$, so $\\text{MP} = \\dfrac{850}{0.85} = 1000$. "
                    "Adding 15 percent to 850 would have given 977.50, which is wrong."
                ),
            ),
            Method(
                name="A is x percent more or less than B",
                recognise=(
                    "a comparison between two quantities, usually asking for the reverse "
                    "comparison: 'if A is 25 percent more than B, by what percent is B less "
                    "than A?'"
                ),
                steps=[
                    "Set the **base of the given statement** to 100. In 'A is 25 percent more than B', B is the base, so B = 100 and A = 125.",
                    "Now compute the reverse comparison against its own base: B is less than A by $\\dfrac{125 - 100}{125} \\times 100$.",
                ],
                worked=(
                    "$\\dfrac{25}{125} \\times 100 = 20$, so B is 20 percent less than A. "
                    "The two percentages are different because the bases are different."
                ),
            ),
            Method(
                name="Price, consumption and expenditure",
                recognise=(
                    "a price rises and the question asks by how much consumption must be cut so "
                    "spending stays the same (or the other way round)."
                ),
                steps=[
                    "Remember that expenditure $=$ price $\\times$ quantity, so if expenditure is fixed the two multipliers must multiply to 1.",
                    "If price becomes $\\times p$, quantity must become $\\times \\dfrac{1}{p}$.",
                    "Convert that back into a percentage change.",
                ],
                worked=(
                    "Price up 25 percent means $\\times 1.25$, so quantity must be "
                    "$\\times \\dfrac{1}{1.25} = 0.8$ — a 20 percent cut, not 25."
                ),
            ),
            Method(
                name="Pass marks and shortfalls",
                recognise=(
                    "a candidate scores some marks, fails by a margin, and you are asked for the "
                    "maximum marks or the pass percentage."
                ),
                steps=[
                    "Write the pass mark two ways: as (score $+$ shortfall), and as (pass percentage $\\times$ maximum marks).",
                    "Set them equal and solve for the unknown.",
                ],
                worked=(
                    "Scoring 180 and failing by 20 in a 40 percent-pass exam means the pass mark "
                    "is 200, so $0.40M = 200$ and $M = 500$."
                ),
            ),
            Method(
                name="Repeated growth over periods",
                recognise=(
                    "a population, salary or value growing by the same percentage every year for "
                    "several years."
                ),
                steps=[
                    "This is one multiplier applied $n$ times: final $=$ initial $\\times \\left(1 + \\dfrac{r}{100}\\right)^n$.",
                    "For a decline, use $\\left(1 - \\dfrac{r}{100}\\right)^n$.",
                    "If you are given the start and the end and asked for the rate, take the $n$th root.",
                ],
                worked=(
                    "10000 growing at 10 percent for 3 years reaches "
                    "$10000 \\times 1.1^3 = 13310$."
                ),
            ),
            Method(
                name="Percentage change in area or volume",
                recognise=(
                    "a length, side or radius changes by a percentage and the question asks about "
                    "the resulting area or volume."
                ),
                steps=[
                    "Write the multiplier for the length.",
                    "Area depends on two lengths, so square the multiplier; volume depends on three, so cube it.",
                    "Convert back to a percentage.",
                ],
                worked=(
                    "A side up 20 percent is $\\times 1.2$, so area is "
                    "$\\times 1.2^2 = 1.44$ — a 44 percent increase, not 40."
                ),
            ),
        ],
        examples=[
            EX(
                stem="A shopkeeper raises the price of an item by 25 percent and then offers a 20 percent discount on the new price. What is the net percentage change in price?",
                solution=(
                    "Turn both changes into multipliers and chain them.\n\n"
                    "The rise is $\\times 1.25$ and the discount is $\\times 0.80$.\n\n"
                    "$1.25 \\times 0.80 = 1.00$\n\n"
                    "The multiplier is exactly 1, so the price is back where it started: "
                    "**no net change**."
                ),
                alt=(
                    "As fractions this is instant: a 25 percent rise multiplies by "
                    "$\\dfrac{5}{4}$ and a 20 percent discount by $\\dfrac{4}{5}$. Those are "
                    "reciprocals, so they cancel. Spotting reciprocal pairs like "
                    "$\\dfrac{5}{4}$ and $\\dfrac{4}{5}$ saves the arithmetic entirely."
                ),
            ),
            EX(
                stem="After spending 30 percent of her salary on rent and 20 percent of the remainder on food, Nidhi is left with Rs. 22400. What is her salary?",
                solution=(
                    "Watch the base carefully: the 20 percent is of what is **left after rent**, "
                    "not of the salary.\n\n"
                    "After rent she has $70\\%$ of her salary, so a multiplier of $0.70$.\n\n"
                    "She then spends 20 percent of that, keeping 80 percent of it: another "
                    "multiplier of $0.80$.\n\n"
                    "So what remains is $0.70 \\times 0.80 = 0.56$ of her salary.\n\n"
                    "$0.56 \\times S = 22400$, giving $S = \\dfrac{22400}{0.56} = 40000$.\n\n"
                    "Her salary is **Rs. 40000**."
                ),
                alt=(
                    "The trap answer here is 50 percent — adding 30 and 20 as if both applied to "
                    "the salary. They do not: the second percentage has a smaller base, which is "
                    "why the true total spent is 44 percent, not 50."
                ),
            ),
            EX(
                stem="The price of rice rises by 20 percent. By what percentage must a family reduce its consumption so that its spending on rice is unchanged?",
                solution=(
                    "Spending $=$ price $\\times$ quantity, and spending is to stay the same, so "
                    "the two multipliers must multiply to 1.\n\n"
                    "Price is $\\times 1.2$, so quantity must be "
                    "$\\times \\dfrac{1}{1.2} = \\dfrac{5}{6} \\approx 0.8333$.\n\n"
                    "That is a fall of $1 - \\dfrac{5}{6} = \\dfrac{1}{6}$, which is "
                    "$16\\tfrac{2}{3}$ percent.\n\n"
                    "The family must cut consumption by **$16\\tfrac{2}{3}$ percent**."
                ),
                alt=(
                    "This is the reverse-comparison idea again. A 20 percent rise is 'new is 20 "
                    "percent more than old'; the cut needed is 'old is what percent less than "
                    "new' — a different base, hence "
                    "$16\\tfrac{2}{3}$ rather than 20."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Percentage change",
                body="$\\text{change }\\% = \\dfrac{\\text{new} - \\text{old}}{\\text{old}} \\times 100$",
                example="From 80 to 100 is $\\dfrac{20}{80} \\times 100 = 25$ percent.",
            ),
            FC(
                title="Successive changes",
                body=(
                    "Net multiplier $= \\left(1 + \\dfrac{a}{100}\\right)\\left(1 + \\dfrac{b}{100}\\right)$, "
                    "using a negative value for a decrease."
                ),
                example="Up 10 then down 10 gives $1.1 \\times 0.9 = 0.99$: a 1 percent net fall.",
            ),
            FC(
                title="Reverse comparison",
                body=(
                    "If A is $x\\%$ more than B, then B is $\\dfrac{100x}{100 + x}\\%$ less than A. "
                    "If A is $x\\%$ less than B, then B is $\\dfrac{100x}{100 - x}\\%$ more than A."
                ),
                example="A is 25 percent more than B, so B is $\\dfrac{2500}{125} = 20$ percent less than A.",
            ),
            FC(
                title="Fixed expenditure",
                body="Price $\\times$ quantity is constant, so a price multiplier of $p$ needs a quantity multiplier of $\\dfrac{1}{p}$.",
                example="Price up 25 percent needs consumption down 20 percent.",
            ),
            FC(
                title="Useful fraction equivalents",
                body=(
                    "$12.5\\% = \\dfrac{1}{8}$, $16\\tfrac{2}{3}\\% = \\dfrac{1}{6}$, "
                    "$20\\% = \\dfrac{1}{5}$, $25\\% = \\dfrac{1}{4}$, "
                    "$33\\tfrac{1}{3}\\% = \\dfrac{1}{3}$, $37.5\\% = \\dfrac{3}{8}$, "
                    "$62.5\\% = \\dfrac{5}{8}$"
                ),
                example="$37.5\\%$ of 64 is $\\dfrac{3}{8} \\times 64 = 24$, faster than multiplying by 0.375.",
            ),
            FC(
                title="Growth over n periods",
                body="$\\text{final} = \\text{initial} \\times \\left(1 + \\dfrac{r}{100}\\right)^n$",
                example="5000 at 10 percent for 2 years becomes $5000 \\times 1.21 = 6050$.",
            ),
        ],
        traps=[
            "Adding successive percentages instead of multiplying the multipliers. Up 20 then up 30 is a 56 percent rise, not 50.",
            "Applying the percentage to the final value when the question asks for the original. Always divide by the multiplier, never subtract.",
            "Losing track of the base when a question says 'of the remainder' — that is a new, smaller base.",
            "Assuming a rise and a fall of the same percentage cancel. They never do; the result is always a small net loss.",
            "Answering with the change when the question asked for the final value, or the other way round.",
            "Treating a percentage-point difference as a percentage change. Going from 20 percent to 25 percent is 5 percentage points, but a 25 percent increase.",
        ],
        checklist=[
            "Convert any percentage change into a multiplier without thinking about it.",
            "State what the base is before computing anything.",
            "Chain successive changes by multiplying, and recover the original by dividing.",
            "Convert between 'A is x percent more than B' and 'B is y percent less than A'.",
            "Handle the price-consumption-expenditure triangle in either direction.",
        ],
        minutes=12,
    ),
    # ------------------------------------------------------------- profit and loss
    LessonSpec(
        mt="qa.arith.profit-loss-discount",
        prereq="Percentages, especially successive changes and recovering an original value.",
        intuition=(
            "There are only three prices in this entire topic, and every question is about the "
            "gaps between them.\n\n"
            "Imagine a shop. **Cost price** is what the shopkeeper paid the wholesaler. "
            "**Marked price** is the number on the tag in the window. **Selling price** is what "
            "you actually hand over at the till after haggling or a sale.\n\n"
            "Discount is the gap between the tag and the till. Profit is the gap between the "
            "till and the wholesaler. That is it — and the single most common error in the whole "
            "topic is computing one of those gaps as a percentage of the wrong price. Discount "
            "is always a percentage of the tag. Profit is always a percentage of the cost."
        ),
        core=(
            "Write it as two independent multipliers and this topic becomes bookkeeping.\n\n"
            "From cost to selling price: $SP = CP \\times \\left(1 + \\dfrac{\\text{profit}\\%}{100}\\right)$. "
            "A loss is the same thing with a minus sign.\n\n"
            "From marked price to selling price: $SP = MP \\times \\left(1 - \\dfrac{\\text{discount}\\%}{100}\\right)$.\n\n"
            "The selling price is the hinge — it is the only number that appears in both. So when "
            "a question mentions both a discount and a profit, the route is always the same: go "
            "from MP down to SP, then from SP back to CP. Never try to relate the marked price to "
            "the cost price directly.\n\n"
            "A useful sanity check throughout: profit percent is computed on cost, discount "
            "percent on marked price. If you ever find yourself dividing a profit by the marked "
            "price, something has gone wrong."
        ),
        methods=[
            Method(
                name="Selling price from cost and profit percent",
                recognise="the plainest form — cost price and a profit or loss percentage are given.",
                steps=[
                    "Convert the profit percent to a multiplier on cost.",
                    "Multiply. A loss uses a multiplier below 1.",
                ],
                worked="Cost 400 at 15 percent profit gives $400 \\times 1.15 = 460$.",
            ),
            Method(
                name="Successive discounts",
                recognise="two discounts applied one after another, or 'a further x percent off the sale price'.",
                steps=[
                    "Turn each discount into a multiplier.",
                    "Multiply them; do not add the discounts.",
                    "The single equivalent discount is $100(1 - \\text{product})$ percent.",
                ],
                worked=(
                    "20 percent then 10 percent is $0.8 \\times 0.9 = 0.72$, so a single "
                    "equivalent discount of 28 percent — not 30."
                ),
            ),
            Method(
                name="Cost price from marked price, discount and profit",
                recognise="all three prices are involved: a marked price, a discount, and a resulting profit.",
                steps=[
                    "Apply the discount to the marked price to get the selling price.",
                    "Divide the selling price by the profit multiplier to get back to cost.",
                ],
                worked=(
                    "MP 1000, 20 percent off, 25 percent profit: "
                    "$SP = 800$, then $CP = \\dfrac{800}{1.25} = 640$."
                ),
            ),
            Method(
                name="Equal gain and loss on two items sold at the same price",
                recognise=(
                    "two articles sold for the same amount, one at $x$ percent gain and the other "
                    "at $x$ percent loss, asking for the overall result."
                ),
                steps=[
                    "The answer does not depend on the selling price at all: the result is always an overall **loss**.",
                    "The loss percent is $\\dfrac{x^2}{100}$.",
                    "It happens because the item sold at a loss had the larger cost price, so the loss is taken on a bigger base than the gain.",
                ],
                worked="At 10 percent each way the net is a $\\dfrac{100}{100} = 1$ percent loss.",
            ),
            Method(
                name="Target selling price for a required profit",
                recognise="an item sold at a known profit or loss, asking what price would have produced a different profit.",
                steps=[
                    "Work back from the known sale to the cost price first.",
                    "Then apply the required profit multiplier to that cost.",
                ],
                worked=(
                    "Sold at 480 for a 20 percent profit means $CP = \\dfrac{480}{1.2} = 400$; "
                    "for 35 percent profit the price must be $400 \\times 1.35 = 540$."
                ),
            ),
            Method(
                name="False weights",
                recognise=(
                    "a dishonest trader using a weight of, say, 900 g while claiming a kilogram, "
                    "usually while also selling at cost price."
                ),
                steps=[
                    "The gain comes purely from the short measure: he gives less than he charges for.",
                    "Gain percent $= \\dfrac{\\text{true weight} - \\text{false weight}}{\\text{false weight}} \\times 100$.",
                    "The denominator is what he actually hands over, because that is what it cost him.",
                ],
                worked=(
                    "Using 900 g as a kilogram gives "
                    "$\\dfrac{100}{900} \\times 100 = 11\\tfrac{1}{9}$ percent profit."
                ),
            ),
        ],
        examples=[
            EX(
                stem="A trader marks his goods 40 percent above cost and then allows a discount of 25 percent. What is his profit percentage?",
                solution=(
                    "Take the cost price as 100 — with only percentages in play, any convenient "
                    "cost works and 100 makes the arithmetic disappear.\n\n"
                    "Marked price: $100 \\times 1.40 = 140$.\n\n"
                    "Selling price after the discount: $140 \\times 0.75 = 105$.\n\n"
                    "Profit is $105 - 100 = 5$ on a cost of 100, so **5 percent**."
                ),
                alt=(
                    "As one chain: $1.40 \\times 0.75 = 1.05$. The markup multiplier times the "
                    "discount multiplier gives the profit multiplier directly, which is worth "
                    "recognising — nearly every markup-and-discount question is this one line."
                ),
            ),
            EX(
                stem="Two cameras are each sold for Rs. 9600. One is sold at a 20 percent profit and the other at a 20 percent loss. What is the overall result?",
                solution=(
                    "Find each cost price separately — that is where the asymmetry lives.\n\n"
                    "The one sold at a profit: $CP_1 = \\dfrac{9600}{1.2} = 8000$.\n\n"
                    "The one sold at a loss: $CP_2 = \\dfrac{9600}{0.8} = 12000$.\n\n"
                    "Total cost $= 8000 + 12000 = 20000$. Total received "
                    "$= 2 \\times 9600 = 19200$.\n\n"
                    "So there is a loss of $20000 - 19200 = 800$, which on a cost of 20000 is "
                    "**a 4 percent loss**."
                ),
                alt=(
                    "The shortcut confirms it: the loss is always $\\dfrac{x^2}{100}$ percent, "
                    "here $\\dfrac{400}{100} = 4$ percent. Notice the answer never depended on "
                    "the Rs. 9600 — try it with any figure and the loss is still 4 percent."
                ),
            ),
            EX(
                stem="A shopkeeper sells rice at cost price but uses a weight of 800 g in place of 1 kg. Find his profit percentage.",
                solution=(
                    "He charges for 1000 g and hands over 800 g. His cost is the 800 g he "
                    "actually parted with; his gain is the 200 g he kept.\n\n"
                    "Profit percent $= \\dfrac{200}{800} \\times 100 = 25$ percent.\n\n"
                    "So he makes **25 percent** despite selling at 'cost price'."
                ),
                alt=(
                    "The tempting wrong answer is 20 percent, from dividing the 200 g by the "
                    "1000 g he claimed. Profit is always measured against what it cost him, and "
                    "the 1000 g never existed."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Profit and loss percent",
                body=(
                    "$\\text{profit}\\% = \\dfrac{SP - CP}{CP} \\times 100$, and "
                    "$\\text{loss}\\% = \\dfrac{CP - SP}{CP} \\times 100$. Both are on cost."
                ),
                example="Cost 250, sold at 300 gives $\\dfrac{50}{250} \\times 100 = 20$ percent.",
            ),
            FC(
                title="Discount",
                body="$\\text{discount}\\% = \\dfrac{MP - SP}{MP} \\times 100$ — this one is on the marked price.",
                example="Marked 900, sold at 720 is a $\\dfrac{180}{900} \\times 100 = 20$ percent discount.",
            ),
            FC(
                title="Markup and discount together",
                body=(
                    "$SP = CP \\times \\left(1 + \\dfrac{\\text{markup}}{100}\\right)"
                    "\\left(1 - \\dfrac{\\text{discount}}{100}\\right)$"
                ),
                example="40 percent markup with 25 percent discount gives $1.4 \\times 0.75 = 1.05$: 5 percent profit.",
            ),
            FC(
                title="Same price, equal gain and loss",
                body="Always a net loss of $\\dfrac{x^2}{100}$ percent, whatever the selling price.",
                example="20 percent each way is a 4 percent loss.",
            ),
            FC(
                title="False weight",
                body="$\\text{gain}\\% = \\dfrac{\\text{claimed weight} - \\text{actual weight}}{\\text{actual weight}} \\times 100$",
                example="Passing 900 g off as 1 kg gives $11\\tfrac{1}{9}$ percent.",
            ),
        ],
        traps=[
            "Computing profit percent on the selling price or the marked price. It is always on cost.",
            "Adding successive discounts. 20 percent then 10 percent is 28 percent, not 30.",
            "Trying to link marked price to cost price directly. Always route through the selling price.",
            "In the equal-gain-and-loss case, concluding the trader broke even. There is always a loss.",
            "In false-weight questions, dividing by the claimed weight rather than the weight actually handed over.",
            "Forgetting that overheads or transport costs are part of the cost price when a question mentions them.",
        ],
        checklist=[
            "Name which of CP, MP and SP each number in the stem is.",
            "Move from MP to SP with the discount, and SP to CP with the profit — in that order.",
            "Chain a markup and a discount into one multiplier.",
            "Explain why selling two items at the same price with equal gain and loss always loses money.",
            "Handle a false-weight question without being fooled by 'sells at cost price'.",
        ],
        minutes=11,
    ),
    # -------------------------------------------------------------------- ratios
    LessonSpec(
        mt="qa.arith.ratio-proportion-variation",
        prereq="Fractions, and the idea that a fraction can be scaled up or down without changing its value.",
        intuition=(
            "A ratio is a recipe. 'Two parts water to three parts squash' does not tell you how "
            "much drink you are making — it tells you the **shape** of the mixture. You can make "
            "a glass or a bathtub of it; as long as you keep two parts to three, it tastes the "
            "same.\n\n"
            "That is why every ratio question starts the same way: give the parts a size. If the "
            "ratio is $2 : 3$, call the amounts $2k$ and $3k$. The $k$ is the size of one part, "
            "and it is almost always what the question is secretly asking you to find.\n\n"
            "Once you have $k$, everything else falls out in one line. Students who struggle "
            "with this topic are usually the ones trying to work with $2$ and $3$ directly "
            "instead of $2k$ and $3k$."
        ),
        core=(
            "**Direct variation** means two quantities move together: double one, double the "
            "other. Their ratio stays fixed, so $\\dfrac{a}{b}$ is constant. More petrol, more "
            "distance.\n\n"
            "**Inverse variation** means they move oppositely: double one, halve the other. "
            "Their **product** stays fixed, so $ab$ is constant. More workers, fewer days.\n\n"
            "Knowing which of the two you are looking at is the entire difficulty in most "
            "questions, and there is a reliable test: ask what happens if you double the first "
            "quantity. If the second doubles, it is direct and you keep the ratio fixed. If the "
            "second halves, it is inverse and you keep the product fixed.\n\n"
            "**Compounding ratios** happens when ratios chain: if $A : B = 2 : 3$ and "
            "$B : C = 4 : 5$, they cannot be joined directly because B is 3 in one and 4 in the "
            "other. Scale both so B matches — multiply the first by 4 and the second by 3, "
            "giving $A : B = 8 : 12$ and $B : C = 12 : 15$, so $A : B : C = 8 : 12 : 15$."
        ),
        methods=[
            Method(
                name="Dividing an amount in a given ratio",
                recognise="a total is to be shared among two or more people in a stated ratio.",
                steps=[
                    "Add the ratio terms to get the total number of parts.",
                    "Divide the amount by the total parts to find the value of one part, $k$.",
                    "Multiply $k$ by each term to get each share.",
                ],
                worked=(
                    "Rs. 3600 in $2 : 3 : 4$ has 9 parts, so $k = 400$ and the shares are "
                    "800, 1200 and 1600."
                ),
            ),
            Method(
                name="Ages in a ratio, now and later",
                recognise="two ages in a ratio now, and a different ratio some years earlier or later.",
                steps=[
                    "Write the present ages as $ak$ and $bk$.",
                    "Add or subtract the number of years from **both** ages.",
                    "Set the new expressions equal to the second ratio and solve for $k$.",
                ],
                worked=(
                    "If ages are $3k$ and $5k$ and in 4 years the ratio is $5 : 7$, then "
                    "$7(3k + 4) = 5(5k + 4)$, giving $21k + 28 = 25k + 20$, so $k = 2$ and the "
                    "ages are 6 and 10."
                ),
            ),
            Method(
                name="Compounding two ratios with a common term",
                recognise="$A : B$ and $B : C$ given separately, asking for $A : B : C$.",
                steps=[
                    "Look at the two values of the shared term.",
                    "Multiply the first ratio through by the second's value of the shared term, and the second ratio by the first's.",
                    "The shared term now matches, so the three-part ratio can be read off.",
                ],
                worked=(
                    "$A : B = 3 : 4$ and $B : C = 6 : 7$ scale to $18 : 24$ and $24 : 28$, so "
                    "$A : B : C = 18 : 24 : 28$, which reduces to $9 : 12 : 14$."
                ),
            ),
            Method(
                name="Inverse variation",
                recognise=(
                    "more of one thing means less of another — workers and time, speed and "
                    "duration, pipes and filling time."
                ),
                steps=[
                    "Write $x_1 y_1 = x_2 y_2$, because the product is what stays constant.",
                    "Substitute the three known values and solve for the fourth.",
                ],
                worked=(
                    "If 12 workers take 8 days, then 16 workers take "
                    "$\\dfrac{12 \\times 8}{16} = 6$ days."
                ),
            ),
            Method(
                name="Adding the same amount to both terms",
                recognise=(
                    "a ratio that changes when an identical quantity is added to or removed from "
                    "both parts."
                ),
                steps=[
                    "Write the original amounts as $ak$ and $bk$.",
                    "Add the same number $n$ to each, then set the result equal to the new ratio.",
                    "Cross-multiply and solve. Note the ratio always moves **towards** $1 : 1$ when you add to both.",
                ],
                worked=(
                    "$\\dfrac{2k + 6}{5k + 6} = \\dfrac{1}{2}$ gives "
                    "$4k + 12 = 5k + 6$, so $k = 6$ and the original amounts are 12 and 30."
                ),
            ),
        ],
        examples=[
            EX(
                stem="Rs. 6300 is divided among A, B and C in the ratio 3 : 4 : 7. How much more does C get than A?",
                solution=(
                    "Total parts $= 3 + 4 + 7 = 14$.\n\n"
                    "One part $k = \\dfrac{6300}{14} = 450$.\n\n"
                    "C gets $7 \\times 450 = 3150$ and A gets $3 \\times 450 = 1350$.\n\n"
                    "The difference is $3150 - 1350 = 1800$, so C gets **Rs. 1800** more."
                ),
                alt=(
                    "Faster: the difference is $7 - 3 = 4$ parts, so it is "
                    "$4 \\times 450 = 1800$ without computing either share. When a question asks "
                    "for a difference, work in parts and skip straight to it."
                ),
            ),
            EX(
                stem="The ratio of Anu's age to Bala's is 4 : 7. Six years ago it was 2 : 5. How old is Bala now?",
                solution=(
                    "Write the present ages as $4k$ and $7k$.\n\n"
                    "Six years ago they were $4k - 6$ and $7k - 6$, and that ratio was $2 : 5$. "
                    "Cross-multiplying:\n\n"
                    "$5(4k - 6) = 2(7k - 6)$\n\n"
                    "$20k - 30 = 14k - 12$\n\n"
                    "$6k = 18$, so $k = 3$.\n\n"
                    "Present ages are $4 \\times 3 = 12$ and $7 \\times 3 = 21$, so Bala is "
                    "**21 years old**."
                ),
                alt=(
                    "Check against the original wording, not against your own equation: six "
                    "years ago they were 6 and 15, and $6 : 15$ does reduce to $2 : 5$. An "
                    "algebra slip reproduces itself if you only re-check the line you wrote."
                ),
            ),
            EX(
                stem="If 15 workers can build a wall in 24 days, how many days will 20 workers take, working at the same rate?",
                solution=(
                    "More workers means fewer days, so this is inverse variation and the product "
                    "workers $\\times$ days is constant.\n\n"
                    "$15 \\times 24 = 20 \\times d$\n\n"
                    "$360 = 20d$, so $d = 18$.\n\n"
                    "It takes **18 days**."
                ),
                alt=(
                    "Sanity check the direction before trusting the number: 20 workers is more "
                    "than 15, so the answer must be less than 24. It is. Getting a larger number "
                    "would mean the ratio was applied the wrong way up, which is the single most "
                    "common error here."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Dividing in a ratio",
                body="Share of a term $= \\dfrac{\\text{that term}}{\\text{sum of terms}} \\times \\text{total}$",
                example="B's share of 6300 in $3:4:7$ is $\\dfrac{4}{14} \\times 6300 = 1800$.",
            ),
            FC(
                title="Direct variation",
                body="$\\dfrac{a_1}{b_1} = \\dfrac{a_2}{b_2}$ — the ratio is fixed.",
                example="3 books cost 240, so 7 books cost $\\dfrac{240}{3} \\times 7 = 560$.",
            ),
            FC(
                title="Inverse variation",
                body="$a_1 b_1 = a_2 b_2$ — the product is fixed.",
                example="6 taps fill a tank in 8 hours, so 4 taps take $\\dfrac{48}{4} = 12$ hours.",
            ),
            FC(
                title="Compounding ratios",
                body=(
                    "Given $A : B = a : b$ and $B : C = c : d$, then $A : B : C = ac : bc : bd$."
                ),
                example="$2:3$ and $4:5$ compound to $8 : 12 : 15$.",
            ),
        ],
        traps=[
            "Working with the ratio terms as if they were the actual amounts. Always introduce $k$.",
            "Joining $A : B$ and $B : C$ without first making the two values of B agree.",
            "Applying an age change to only one of the two people. Everyone ages at the same rate.",
            "Treating an inverse relationship as direct. Check the direction of the answer against common sense before moving on.",
            "Assuming that adding the same amount to both terms leaves the ratio unchanged. It moves it towards $1 : 1$.",
        ],
        checklist=[
            "Convert any ratio into $ak$, $bk$ form as a reflex.",
            "Split a total in a ratio, and find a difference directly in parts.",
            "Decide whether a situation is direct or inverse variation, and justify it.",
            "Compound two ratios that share a term.",
            "Set up and solve an ages question with a past or future ratio.",
        ],
        minutes=11,
    ),
    # ------------------------------------------------------------------ averages
    LessonSpec(
        mt="qa.arith.averages-weighted-averages",
        prereq="Nothing beyond arithmetic, though ratios help for the weighted-average section.",
        intuition=(
            "An average is what everyone would get if you pooled everything and shared it out "
            "equally. Five people put their pocket money on the table, you mix it up and deal it "
            "back in equal piles — the size of one pile is the average.\n\n"
            "That picture makes the key fact obvious: the **total is all that matters**. The "
            "average of a group and the number of people in it between them fix the total, and "
            "the total is what survives when the group changes. So when someone joins, leaves, "
            "or is replaced, do not fiddle with the average directly — work out what happened to "
            "the total.\n\n"
            "Second picture, for weighted averages: think of a seesaw. Put a heavy group at one "
            "end and a light group at the other, and the balance point sits nearer the heavy "
            "one. The combined average of two groups is never the midpoint unless the groups are "
            "the same size."
        ),
        core=(
            "Everything here comes from one relationship: "
            "$\\text{total} = \\text{average} \\times \\text{count}$. Read it in both directions "
            "and most questions collapse.\n\n"
            "**When one member is replaced**, the count does not change, so the change in the "
            "total is exactly the change in one person's value. If the average of 8 people rises "
            "by 3 when one is replaced, the total rose by $8 \\times 3 = 24$, so the newcomer is "
            "24 more than the person who left. That single sentence answers most replacement "
            "questions.\n\n"
            "**For evenly spaced numbers** — consecutive integers, an arithmetic progression, "
            "consecutive even numbers — the average is simply the midpoint of the first and "
            "last. No summing required, because the terms above the middle exactly balance the "
            "terms below.\n\n"
            "**For two groups combined**, the weighted average is\n\n"
            "$$\\bar{x} = \\frac{n_1 \\bar{x}_1 + n_2 \\bar{x}_2}{n_1 + n_2}$$\n\n"
            "which is just 'total of everything over count of everything'."
        ),
        methods=[
            Method(
                name="Replacing a member",
                recognise="someone leaves and someone else joins, and the average shifts.",
                steps=[
                    "The count is unchanged, so total change $=$ count $\\times$ change in average.",
                    "That total change is the difference between the newcomer and the person replaced.",
                    "Add or subtract it from the known value.",
                ],
                worked=(
                    "The average of 10 boys rises by 2 kg when a 40 kg boy is replaced, so the "
                    "new boy is $40 + 10 \\times 2 = 60$ kg."
                ),
            ),
            Method(
                name="Combining two groups",
                recognise="two groups with their own averages and sizes, asking for the overall average.",
                steps=[
                    "Compute each group's total as average $\\times$ count.",
                    "Add the totals and add the counts.",
                    "Divide. The answer always lies between the two averages, nearer the larger group.",
                ],
                worked=(
                    "20 students averaging 60 and 30 averaging 70 give "
                    "$\\dfrac{1200 + 2100}{50} = 66$."
                ),
            ),
            Method(
                name="Average of consecutive or evenly spaced numbers",
                recognise="consecutive integers, consecutive odd or even numbers, or any arithmetic progression.",
                steps=[
                    "Take the first and last terms.",
                    "The average is their midpoint, $\\dfrac{\\text{first} + \\text{last}}{2}$.",
                    "If asked for the sum, multiply that by the count.",
                ],
                worked="The average of the integers from 11 to 29 is $\\dfrac{11 + 29}{2} = 20$.",
            ),
            Method(
                name="A wrongly read value",
                recognise=(
                    "an average was computed, then a single entry turns out to have been misread "
                    "or mis-copied."
                ),
                steps=[
                    "Compute the total that was originally used.",
                    "Correct it by the difference between the true value and the value used.",
                    "Divide the corrected total by the unchanged count.",
                ],
                worked=(
                    "For 10 numbers averaging 50, if 36 was read as 63 the total is 13 too high, "
                    "so the correct average is $\\dfrac{500 - 13}{10} = 48.7$."
                ),
            ),
            Method(
                name="Excluding a member",
                recognise="the average of a group and of a smaller sub-group are both given, asking for the one left out.",
                steps=[
                    "Compute both totals.",
                    "Subtract. The difference is the value of the excluded members.",
                    "Divide by how many were excluded, if more than one.",
                ],
                worked=(
                    "11 players average 50 and 10 of them average 48, so the eleventh scored "
                    "$550 - 480 = 70$."
                ),
            ),
        ],
        examples=[
            EX(
                stem="The average weight of 8 people increases by 2.5 kg when a new person replaces one weighing 65 kg. What is the weight of the new person?",
                solution=(
                    "The count stays at 8, so the whole change in the average must come from the "
                    "one swap.\n\n"
                    "Total change $= 8 \\times 2.5 = 20$ kg.\n\n"
                    "So the new person is 20 kg heavier than the one who left:\n\n"
                    "$65 + 20 = 85$ kg.\n\n"
                    "The new person weighs **85 kg**."
                ),
                alt=(
                    "Note what is **not** needed: the original average. A replacement question "
                    "never requires it, because only the difference matters. If a question gives "
                    "you the original average here, it is decoration."
                ),
            ),
            EX(
                stem="In a class of 30 students, 18 boys average 62 marks and the girls average 71. What is the class average?",
                solution=(
                    "There are $30 - 18 = 12$ girls.\n\n"
                    "Boys' total: $18 \\times 62 = 1116$.\n\n"
                    "Girls' total: $12 \\times 71 = 852$.\n\n"
                    "Class total: $1116 + 852 = 1968$, over 30 students:\n\n"
                    "$\\dfrac{1968}{30} = 65.6$\n\n"
                    "The class average is **65.6 marks**."
                ),
                alt=(
                    "Sanity check with the seesaw: the answer must fall between 62 and 71, and "
                    "closer to 62 because there are more boys. 65.6 sits where it should. An "
                    "answer outside that range means an arithmetic slip, and you can catch it "
                    "without redoing the sum."
                ),
            ),
            EX(
                stem="The average of 11 numbers is 45. The average of the first six is 49 and of the last six is 52. What is the sixth number?",
                solution=(
                    "The sixth number belongs to both groups of six, which is what makes this "
                    "work.\n\n"
                    "Total of all eleven: $11 \\times 45 = 495$.\n\n"
                    "First six: $6 \\times 49 = 294$. Last six: $6 \\times 52 = 312$.\n\n"
                    "Adding those two gives $294 + 312 = 606$, which counts all eleven numbers "
                    "once — except the sixth, which it counts twice.\n\n"
                    "So the sixth number is $606 - 495 = 111$."
                ),
                alt=(
                    "The structural insight is the double-count: six plus six is twelve, but "
                    "there are only eleven numbers, so exactly one has been counted twice. Any "
                    "question with overlapping groups yields to the same reasoning."
                ),
            ),
        ],
        formulas=[
            FC(
                title="The core relationship",
                body="$\\text{average} = \\dfrac{\\text{total}}{\\text{count}}$, so $\\text{total} = \\text{average} \\times \\text{count}$.",
                example="12 items averaging 15 have a total of 180.",
            ),
            FC(
                title="Replacement",
                body="New value $=$ old value $+$ count $\\times$ change in average.",
                example="8 people, average up 2.5, replacing 65 gives $65 + 20 = 85$.",
            ),
            FC(
                title="Weighted average",
                body="$\\bar{x} = \\dfrac{n_1\\bar{x}_1 + n_2\\bar{x}_2}{n_1 + n_2}$",
                example="20 at 60 and 30 at 70 average $\\dfrac{3300}{50} = 66$.",
            ),
            FC(
                title="Evenly spaced numbers",
                body="Average $= \\dfrac{\\text{first} + \\text{last}}{2}$, and sum $=$ that $\\times$ count.",
                example="The first 20 positive integers average $\\dfrac{1 + 20}{2} = 10.5$, summing to 210.",
            ),
        ],
        traps=[
            "Averaging two averages directly when the groups differ in size. That answer is only right when the groups are equal.",
            "Changing the count in a replacement question. Nobody joined or left the count — one person swapped for another.",
            "Forgetting that a corrected total keeps the same count, so only the numerator changes.",
            "Adding an extra term to an evenly spaced list without re-checking the first and last.",
            "Assuming the average must be one of the values in the list. It usually is not.",
        ],
        checklist=[
            "Move between total, average and count in either direction without hesitating.",
            "Solve a replacement question using only the change in the average.",
            "Combine two unequal groups and predict roughly where the answer must land.",
            "Average an evenly spaced list at sight.",
            "Correct an average after a misread entry.",
        ],
        minutes=10,
    ),
    # ------------------------------------------------------------ pipes and cisterns
    LessonSpec(
        mt="qa.arith.time-work-pipes-cisterns",
        prereq="Fractions, and ideally the time-and-work idea that work done is rate times time.",
        intuition=(
            "A pipe filling a tank is exactly the same problem as a person doing a job, wearing "
            "different clothes. The tank is the job; the pipe is the worker.\n\n"
            "The trick that makes all of these easy is to stop thinking about **how long** and "
            "start thinking about **how much per hour**. A pipe that fills a tank in 6 hours "
            "fills $\\dfrac{1}{6}$ of it each hour. That fraction is the pipe's rate, and rates "
            "are wonderful because they simply add up: two taps running together fill at the sum "
            "of their rates.\n\n"
            "Times do not add. If one pipe takes 6 hours and another 3, together they do not "
            "take 9 hours, or 4.5 — they take 2, which is faster than either alone, as it must "
            "be. Rates add; times do not. Almost every mistake in this topic is a time being "
            "added where a rate should have been.\n\n"
            "A drain pipe is a worker doing the job backwards. Give it a negative rate and every "
            "formula keeps working unchanged."
        ),
        core=(
            "The method never varies:\n\n"
            "Convert every pipe to a rate — a pipe that fills in $t$ hours has rate "
            "$\\dfrac{1}{t}$ tanks per hour. Add the rates of everything that is open, "
            "subtracting for anything that empties. Then invert the combined rate to get the "
            "time.\n\n"
            "$$\\text{time together} = \\frac{1}{\\text{sum of rates}}$$\n\n"
            "There is a shortcut worth having for the common two-pipe case: if the pipes take "
            "$a$ and $b$ hours, together they take $\\dfrac{ab}{a + b}$ hours. It is just the "
            "rate method with the algebra already done.\n\n"
            "When the numbers are ugly, use the **LCM trick** instead of fractions. Take the "
            "capacity of the tank to be the LCM of the given times — say pipes of 12 and 18 "
            "hours, so let the tank hold 36 litres. Then the first pipe does 3 litres an hour "
            "and the second 2, together 5, so the tank fills in $\\dfrac{36}{5} = 7.2$ hours. "
            "Whole numbers throughout, and no fraction arithmetic at all."
        ),
        methods=[
            Method(
                name="Two pipes filling together",
                recognise="two taps, both filling, opened at the same time.",
                steps=[
                    "Write each rate as $\\dfrac{1}{t}$.",
                    "Add them.",
                    "Invert the sum — or go straight to $\\dfrac{ab}{a+b}$.",
                ],
                worked=(
                    "Pipes of 12 and 15 hours: "
                    "$\\dfrac{12 \\times 15}{27} = \\dfrac{180}{27} = 6\\tfrac{2}{3}$ hours."
                ),
            ),
            Method(
                name="A filling pipe with a leak or outlet",
                recognise="one pipe fills while another empties, or a tank has a leak.",
                steps=[
                    "Give the emptying pipe a negative rate.",
                    "Add the rates as usual; the result is the net filling rate.",
                    "If the net rate is negative or zero, the tank never fills — a legitimate answer that some questions are testing for.",
                ],
                worked=(
                    "Fills in 10 hours, leaks empty in 15: net rate is "
                    "$\\dfrac{1}{10} - \\dfrac{1}{15} = \\dfrac{1}{30}$, so 30 hours."
                ),
            ),
            Method(
                name="Three or more pipes",
                recognise="three taps, some filling and some emptying, all open together.",
                steps=[
                    "Use the LCM trick — take the tank's capacity as the LCM of the times so every rate is a whole number.",
                    "Add and subtract the whole-number rates.",
                    "Divide the capacity by the net rate.",
                ],
                worked=(
                    "Pipes of 6, 8 filling and 12 emptying: take 24 litres, giving rates of 4, 3 "
                    "and $-2$, net 5, so $\\dfrac{24}{5} = 4.8$ hours."
                ),
            ),
            Method(
                name="Finding one pipe's time from the combined time",
                recognise="the combined time is given along with one pipe's, asking for the other's.",
                steps=[
                    "Write combined rate $=$ rate of the first $+$ rate of the second.",
                    "Subtract the known rate from the combined rate.",
                    "Invert what is left.",
                ],
                worked=(
                    "Together 4 hours, one alone 6: the other's rate is "
                    "$\\dfrac{1}{4} - \\dfrac{1}{6} = \\dfrac{1}{12}$, so 12 hours."
                ),
            ),
            Method(
                name="Pipes opened at different times",
                recognise="one pipe runs for a while before another is opened, or one is closed partway.",
                steps=[
                    "Work out the fraction of the tank filled during the first stage: rate $\\times$ time.",
                    "Subtract that from 1 to get what remains.",
                    "Divide the remainder by the rate that applies during the second stage.",
                ],
                worked=(
                    "A 1/10-per-hour pipe running 4 hours alone fills $\\dfrac{4}{10}$; the "
                    "remaining $\\dfrac{6}{10}$ at a combined rate of $\\dfrac{1}{6}$ takes "
                    "$\\dfrac{6}{10} \\times 6 = 3.6$ more hours."
                ),
            ),
        ],
        examples=[
            EX(
                stem="Pipe A fills a tank in 20 hours and pipe B in 30 hours. How long do they take together?",
                solution=(
                    "Convert to rates per hour.\n\n"
                    "A fills $\\dfrac{1}{20}$ of the tank each hour, B fills $\\dfrac{1}{30}$.\n\n"
                    "Together: $\\dfrac{1}{20} + \\dfrac{1}{30} = \\dfrac{3 + 2}{60} = \\dfrac{5}{60} = \\dfrac{1}{12}$.\n\n"
                    "A rate of $\\dfrac{1}{12}$ tank per hour means the tank fills in "
                    "**12 hours**."
                ),
                alt=(
                    "By the LCM trick: let the tank hold 60 litres. Then A does 3 litres an hour "
                    "and B does 2, so together 5 litres an hour, and "
                    "$\\dfrac{60}{5} = 12$ hours. No fractions anywhere."
                ),
            ),
            EX(
                stem="A tank is filled by a pipe in 12 hours, but a leak at the bottom empties a full tank in 20 hours. With both operating, how long does the tank take to fill?",
                solution=(
                    "The leak works against the pipe, so it gets a negative rate.\n\n"
                    "Filling rate: $\\dfrac{1}{12}$. Leaking rate: $-\\dfrac{1}{20}$.\n\n"
                    "Net rate: $\\dfrac{1}{12} - \\dfrac{1}{20} = \\dfrac{5 - 3}{60} = \\dfrac{2}{60} = \\dfrac{1}{30}$.\n\n"
                    "So the tank fills in **30 hours**."
                ),
                alt=(
                    "Sanity check the direction: with a leak the answer must be **longer** than 12 "
                    "hours. If your arithmetic ever produces a time shorter than the filling pipe "
                    "alone, you have added the leak instead of subtracting it."
                ),
            ),
            EX(
                stem="Two pipes fill a tank in 15 and 20 hours. Both are opened together, but the first is closed after 5 hours. How much longer does the second take to fill the tank?",
                solution=(
                    "Stage one: both pipes for 5 hours.\n\n"
                    "Combined rate $= \\dfrac{1}{15} + \\dfrac{1}{20} = \\dfrac{4 + 3}{60} = \\dfrac{7}{60}$.\n\n"
                    "In 5 hours they fill $5 \\times \\dfrac{7}{60} = \\dfrac{35}{60} = \\dfrac{7}{12}$ of the tank.\n\n"
                    "Stage two: $1 - \\dfrac{7}{12} = \\dfrac{5}{12}$ remains, and only the second "
                    "pipe is running at $\\dfrac{1}{20}$ per hour.\n\n"
                    "Time $= \\dfrac{5}{12} \\div \\dfrac{1}{20} = \\dfrac{5}{12} \\times 20 = \\dfrac{100}{12} = 8\\tfrac{1}{3}$ hours.\n\n"
                    "The second pipe needs **$8\\tfrac{1}{3}$ hours** more."
                ),
                alt=(
                    "Two-stage questions all have this shape: fill some, find what is left, "
                    "divide the remainder by the new rate. Write down the fraction filled at the "
                    "end of each stage and the problem cannot get away from you."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Rate of a pipe",
                body="A pipe that fills in $t$ hours has rate $\\dfrac{1}{t}$ tanks per hour. An emptying pipe's rate is negative.",
                example="A 6-hour pipe fills $\\dfrac{1}{6}$ of the tank each hour.",
            ),
            FC(
                title="Pipes together",
                body="$\\dfrac{1}{T} = \\dfrac{1}{a} + \\dfrac{1}{b}$, so $T = \\dfrac{ab}{a + b}$.",
                example="Pipes of 4 and 6 hours together take $\\dfrac{24}{10} = 2.4$ hours.",
            ),
            FC(
                title="Fill against a leak",
                body="$\\dfrac{1}{T} = \\dfrac{1}{a} - \\dfrac{1}{b}$, where $b$ is the emptying time. If $b \\le a$ the tank never fills.",
                example="Fill 12, leak 20 gives $\\dfrac{1}{30}$, so 30 hours.",
            ),
            FC(
                title="The LCM trick",
                body="Set the tank's capacity to the LCM of all the given times; every rate becomes a whole number.",
                example="Times of 6 and 8: take 24 units, so rates are 4 and 3 units per hour.",
            ),
        ],
        traps=[
            "Adding times instead of rates. Two pipes together are always faster than either alone.",
            "Adding a leak's rate rather than subtracting it. Check that your answer is slower than the filling pipe alone.",
            "In a two-stage question, applying the second stage's rate to the whole tank instead of the remainder.",
            "Missing that a question with a large leak has no answer — the tank genuinely never fills.",
            "Mixing units: a pipe given in minutes and another in hours must be converted before the rates are added.",
        ],
        checklist=[
            "Turn any 'fills in $t$ hours' into a rate without pausing.",
            "Combine any number of filling and emptying pipes into one net rate.",
            "Use the LCM trick to avoid fraction arithmetic entirely.",
            "Handle a pipe that is opened late or closed early, in two stages.",
            "Recognise when a tank will never fill, and say so.",
        ],
        minutes=11,
    ),
]
