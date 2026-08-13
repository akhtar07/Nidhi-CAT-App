"""Arithmetic lessons. Analogy first, then the mechanism, then the formula."""

from __future__ import annotations

from . import EX, FC, LessonSpec

SPECS = [
    LessonSpec(
        mt="qa.arith.si-ci-instalments",
        intuition=(
            "Imagine you lend a friend Rs. 1000 and charge Rs. 100 a year. Under **simple interest** "
            "you charge Rs. 100 every single year, forever, because you always charge on the original "
            "Rs. 1000. It is like rent on a room: the room does not grow, so the rent does not change.\n\n"
            "**Compound interest** is different. At the end of year one your friend owes Rs. 1100, and "
            "now you charge on the whole Rs. 1100. Next year the interest is bigger. It is a snowball "
            "rolling downhill: each turn it picks up more snow, so each turn it grows faster than the last."
        ),
        core=(
            "Simple interest is a straight line. The same amount gets added every year, so after "
            "$T$ years you have added $T$ equal slices.\n\n"
            "Compound interest is a curve. Each year you multiply by the same factor, so the growth "
            "feeds on itself. This is why the two are equal after one year and drift apart after that — "
            "the gap is exactly the interest that the earlier interest has itself earned.\n\n"
            "When compounding happens more often than yearly (half-yearly, quarterly), split the rate "
            "and multiply the number of periods to match."
        ),
        examples=[
            EX(
                stem="Find the simple interest on Rs. 8000 at 12 percent per annum for 3 years.",
                solution=(
                    "Each year the interest is $\\dfrac{8000 \\times 12}{100} = 960$. Over 3 years that is "
                    "$960 \\times 3 = 2400$.\n\nSo the simple interest is Rs. 2400."
                ),
                alt="Straight to the formula: $SI = \\dfrac{PRT}{100} = \\dfrac{8000 \\times 12 \\times 3}{100} = 2400$.",
            ),
            EX(
                stem="Find the difference between compound and simple interest on Rs. 10000 at 10 percent per annum for 2 years.",
                solution=(
                    "Simple interest: $\\dfrac{10000 \\times 10 \\times 2}{100} = 2000$.\n\n"
                    "Compound: after year 1 the amount is $10000 \\times 1.1 = 11000$; after year 2 it is "
                    "$11000 \\times 1.1 = 12100$. So the compound interest is $12100 - 10000 = 2100$.\n\n"
                    "The difference is $2100 - 2000 = 100$."
                ),
                alt=(
                    "That Rs. 100 is exactly 10 percent of the first year's Rs. 1000 of interest — the "
                    "interest earned by interest. For 2 years the gap is always "
                    "$P\\left(\\dfrac{R}{100}\\right)^2 = 10000 \\times 0.01 = 100$."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Simple interest",
                body="$SI = \\dfrac{P \\times R \\times T}{100}$, and Amount $= P + SI$.",
                example="$P = 5000$, $R = 8$, $T = 2$ gives $SI = \\dfrac{5000 \\times 8 \\times 2}{100} = 800$.",
            ),
            FC(
                title="Compound interest",
                body="$A = P\\left(1 + \\dfrac{R}{100}\\right)^T$ and $CI = A - P$.",
                example="$P = 5000$, $R = 8$, $T = 2$ gives $A = 5000 \\times 1.08^2 = 5832$, so $CI = 832$.",
            ),
            FC(
                title="Gap between CI and SI over 2 years",
                body="$CI - SI = P\\left(\\dfrac{R}{100}\\right)^2$",
                example="$P = 20000$, $R = 5$ gives a difference of $20000 \\times 0.0025 = 50$.",
            ),
            FC(
                title="Compounding more often than yearly",
                body=(
                    "Half-yearly: use rate $\\dfrac{R}{2}$ for $2T$ periods. Quarterly: use $\\dfrac{R}{4}$ "
                    "for $4T$ periods."
                ),
                example="Rs. 8000 at 10 percent for 1 year half-yearly gives $8000 \\times 1.05^2 = 8820$.",
            ),
        ],
        traps=[
            "Halving the rate for half-yearly compounding but forgetting to double the number of periods.",
            "Reporting the amount when the question asked for the interest, or the other way round.",
            "Assuming CI and SI differ in the first year — over one year with annual compounding they are identical.",
            "Applying the 2-year difference formula to a 3-year question. It is specific to 2 years.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.arith.mixtures-alligation",
        intuition=(
            "Picture two jugs of squash. One is weak, one is strong. Pour them into a bigger jug and the "
            "result sits somewhere between the two — closer to whichever jug you poured more of.\n\n"
            "That single sentence is the whole topic. Alligation is just a fast way to answer: how much "
            "of each jug do I need so the mixture lands on exactly the strength I want?"
        ),
        core=(
            "The trick that makes every mixture question easy is to stop tracking the mixture and start "
            "tracking **one ingredient**. Count litres of pure acid, or grams of pure gold, and ignore "
            "everything else. That quantity only changes when you actually add or remove that ingredient.\n\n"
            "So when you dilute a solution with water, the acid does not change at all — only the total "
            "volume does. When you repeatedly draw off some mixture and top it back up with water, each "
            "round removes the same **fraction** of whatever milk is left, which is why the answer involves "
            "a power rather than a subtraction."
        ),
        examples=[
            EX(
                stem="30 litres of a 40 percent acid solution is mixed with 20 litres of a 60 percent acid solution. What is the concentration of the result?",
                solution=(
                    "Track the acid only.\n\n"
                    "From the first: $30 \\times 0.40 = 12$ litres of acid.\n"
                    "From the second: $20 \\times 0.60 = 12$ litres of acid.\n\n"
                    "Total acid $= 24$ litres in a total volume of $50$ litres, so the concentration is "
                    "$\\dfrac{24}{50} \\times 100 = 48$ percent."
                ),
                alt="Sanity check: the answer must lie between 40 and 60, and nearer 40 since there is more of the weaker solution. 48 fits.",
            ),
            EX(
                stem="A vessel holds 50 litres of pure milk. 10 litres are drawn off and replaced with water. This is done twice in total. How much milk remains?",
                solution=(
                    "Each operation removes one-fifth of whatever is in the vessel and replaces it with water, "
                    "so four-fifths of the milk survives each round.\n\n"
                    "After round 1: $50 \\times \\dfrac{4}{5} = 40$ litres of milk.\n"
                    "After round 2: $40 \\times \\dfrac{4}{5} = 32$ litres of milk.\n\n"
                    "So 32 litres of milk remain."
                ),
                alt=(
                    "In one step: $50 \\times \\left(\\dfrac{4}{5}\\right)^2 = 32$. The fraction is the same "
                    "every round because the vessel is always topped back up to 50 litres."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Alligation rule",
                body=(
                    "To hit a mean price $m$ using ingredients priced $c$ (cheaper) and $d$ (dearer), the "
                    "quantities must be in the ratio $\\dfrac{\\text{cheaper}}{\\text{dearer}} = \\dfrac{d - m}{m - c}$."
                ),
                example="Blending Rs. 30/kg and Rs. 50/kg rice to cost Rs. 42/kg needs a ratio $\\dfrac{50-42}{42-30} = \\dfrac{8}{12} = 2:3$.",
            ),
            FC(
                title="Repeated replacement",
                body="After $n$ rounds of removing $x$ from a vessel of volume $V$ and topping up: remaining $= V\\left(1 - \\dfrac{x}{V}\\right)^n$.",
                example="$V = 40$, $x = 8$, $n = 2$ leaves $40 \\times 0.8^2 = 25.6$ litres.",
            ),
        ],
        traps=[
            "Averaging the two concentrations directly. That is only correct when the two volumes happen to be equal.",
            "In replacement problems, subtracting the drawn amount each time instead of multiplying by the surviving fraction.",
            "Mixing up which difference goes on top in alligation. The quantity of the cheaper ingredient pairs with the distance from the mean to the dearer one.",
            "Forgetting that adding water changes the total volume but never the amount of solute.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.arith.tsd-relative-speed",
        intuition=(
            "Sit in a moving train and look out of the window. A train coming the other way flashes past "
            "in a second. A train going the same way as you, at almost your speed, seems to crawl alongside "
            "for ages.\n\n"
            "Neither train changed speed. What changed is the speed **relative to you**. Coming towards you, "
            "the speeds add. Going the same way, they subtract."
        ),
        core=(
            "Relative speed lets you pretend one object is standing still. Instead of tracking two moving "
            "things, you freeze one and give the other the combined speed. The distance between them then "
            "closes at that single rate, and the problem becomes an ordinary distance-equals-speed-times-time "
            "question.\n\n"
            "Opposite directions: add the speeds. Same direction: subtract them. That is the entire idea, "
            "and it powers trains, boats, races and circular tracks too."
        ),
        examples=[
            EX(
                stem="Two cars 300 km apart drive towards each other at 60 km/h and 40 km/h. When do they meet?",
                solution=(
                    "They approach each other at $60 + 40 = 100$ km/h.\n\n"
                    "The 300 km gap closes at 100 km/h, so they meet after $\\dfrac{300}{100} = 3$ hours."
                ),
                alt="Freeze one car and let the other drive at 100 km/h — the meeting time is unchanged.",
            ),
            EX(
                stem="A man walks to school at 4 km/h and returns along the same road at 6 km/h. What is his average speed?",
                solution=(
                    "Average speed is total distance over total time, never the average of the two speeds.\n\n"
                    "Take the one-way distance as 12 km (any number works). Going takes $\\dfrac{12}{4} = 3$ hours; "
                    "returning takes $\\dfrac{12}{6} = 2$ hours. Total: 24 km in 5 hours.\n\n"
                    "Average speed $= \\dfrac{24}{5} = 4.8$ km/h."
                ),
                alt=(
                    "For two equal distances use the harmonic mean: $\\dfrac{2 \\times 4 \\times 6}{4 + 6} = 4.8$. "
                    "Note it is below 5, the naive average — you spend longer at the slower speed, so the slow leg counts for more."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Relative speed",
                body="Towards each other: $v_1 + v_2$. Same direction: $|v_1 - v_2|$.",
                example="At 70 and 50 km/h: closing at 120 km/h head-on, or 20 km/h if one chases the other.",
            ),
            FC(
                title="Average speed over two equal distances",
                body="$\\text{Average} = \\dfrac{2 v_1 v_2}{v_1 + v_2}$",
                example="60 km/h out and 40 km/h back gives $\\dfrac{2 \\times 60 \\times 40}{100} = 48$ km/h.",
            ),
            FC(
                title="Unit conversion",
                body="Multiply by $\\dfrac{5}{18}$ to turn km/h into m/s, and by $\\dfrac{18}{5}$ to go back.",
                example="72 km/h $= 72 \\times \\dfrac{5}{18} = 20$ m/s.",
            ),
        ],
        traps=[
            "Taking the plain average of two speeds. That is only right if the two legs took equal time, not equal distance.",
            "Mixing km/h and m/s in the same calculation without converting.",
            "Adding speeds when the objects move the same way, or subtracting when they move towards each other.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.arith.tsd-trains",
        intuition=(
            "Think about walking past a doorway versus walking past a long wall. To clear the doorway you "
            "only need to move your own body length. To clear the wall you need your length plus the wall's "
            "length.\n\n"
            "A train works exactly the same way. Passing a pole means covering just the train's own length, "
            "because a pole has no width worth counting. Passing a platform means covering the train's length "
            "**plus** the platform's."
        ),
        core=(
            "Every train question is answered by asking one thing: how much distance must the front of the "
            "train travel for the back of the train to be clear of the object?\n\n"
            "Pole or man: the train's length alone.\n"
            "Platform, bridge or tunnel: the train's length plus the object's length.\n"
            "Another train: the sum of both trains' lengths.\n\n"
            "Then divide that distance by the relative speed, converting km/h to m/s first."
        ),
        examples=[
            EX(
                stem="A 180 m long train running at 54 km/h crosses a platform 270 m long. How long does it take?",
                solution=(
                    "Distance to cover $= 180 + 270 = 450$ m.\n\n"
                    "Speed $= 54 \\times \\dfrac{5}{18} = 15$ m/s.\n\n"
                    "Time $= \\dfrac{450}{15} = 30$ seconds."
                ),
            ),
            EX(
                stem="Two trains, 150 m and 200 m long, run towards each other at 45 km/h and 27 km/h. How long do they take to cross completely?",
                solution=(
                    "Opposite directions, so the speeds add: $45 + 27 = 72$ km/h $= 72 \\times \\dfrac{5}{18} = 20$ m/s.\n\n"
                    "They must clear both lengths: $150 + 200 = 350$ m.\n\n"
                    "Time $= \\dfrac{350}{20} = 17.5$ seconds."
                ),
                alt="Freeze the first train; the second then rushes at it at 20 m/s and must travel 350 m to get fully past.",
            ),
        ],
        formulas=[
            FC(
                title="What distance does the train cover?",
                body=(
                    "Pole or standing man: train length. Platform or bridge: train length $+$ platform length. "
                    "Another train: sum of both lengths."
                ),
                example="A 120 m train crossing a 180 m bridge covers 300 m.",
            ),
            FC(
                title="Train and a moving person",
                body="Use the relative speed: add if they move towards each other, subtract if the same way. The person contributes no length.",
                example="A 200 m train at 63 km/h passing a man walking at 9 km/h the same way: relative speed 54 km/h = 15 m/s, so the time is $\\dfrac{200}{15}$ seconds.",
            ),
        ],
        traps=[
            "Forgetting to add the platform length, and treating a platform like a pole.",
            "Adding the person's length. People are treated as points.",
            "Leaving the speed in km/h while the lengths are in metres.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.arith.tsd-boats-streams",
        intuition=(
            "Walking on an airport travelator: walk with it and you fly along, walk against it and you barely "
            "make progress. Your own walking speed never changed — the floor is helping or fighting you.\n\n"
            "A river does the same to a boat. Downstream the current adds to the boat's speed; upstream it "
            "takes away."
        ),
        core=(
            "There are two hidden speeds — the boat in still water ($b$) and the stream ($s$) — and two "
            "observable ones: downstream ($b + s$) and upstream ($b - s$).\n\n"
            "Because the stream is added in one and subtracted in the other, adding the two observed speeds "
            "cancels the stream entirely and subtracting them cancels the boat. That is why you can always "
            "recover both hidden speeds from the two observed ones."
        ),
        examples=[
            EX(
                stem="A boat goes downstream at 18 km/h and upstream at 12 km/h. Find the speed of the boat in still water and of the stream.",
                solution=(
                    "Adding cancels the stream: $b = \\dfrac{18 + 12}{2} = 15$ km/h.\n\n"
                    "Subtracting cancels the boat: $s = \\dfrac{18 - 12}{2} = 3$ km/h.\n\n"
                    "Check: $15 + 3 = 18$ and $15 - 3 = 12$."
                ),
            ),
            EX(
                stem="A boat whose speed in still water is 10 km/h rows 24 km downstream and back. The stream flows at 2 km/h. Find the total time.",
                solution=(
                    "Downstream speed $= 12$ km/h, so that leg takes $\\dfrac{24}{12} = 2$ hours.\n\n"
                    "Upstream speed $= 8$ km/h, so the return takes $\\dfrac{24}{8} = 3$ hours.\n\n"
                    "Total time $= 5$ hours."
                ),
                alt=(
                    "Notice the round trip took 5 hours, not the $\\dfrac{48}{10} = 4.8$ hours it would have "
                    "taken in still water. A current always costs you time overall, because you spend longer "
                    "on the slow leg than you save on the fast one."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Downstream and upstream speeds",
                body="Downstream $= b + s$. Upstream $= b - s$.",
                example="Boat 12 km/h, stream 3 km/h: 15 km/h down, 9 km/h up.",
            ),
            FC(
                title="Recovering the hidden speeds",
                body="$b = \\dfrac{\\text{down} + \\text{up}}{2}$ and $s = \\dfrac{\\text{down} - \\text{up}}{2}$",
                example="Down 20, up 14 gives $b = 17$ and $s = 3$.",
            ),
        ],
        traps=[
            "Thinking a round trip takes the same time as the still-water journey. It always takes longer.",
            "Swapping the two halves: half the sum is the boat, half the difference is the stream.",
            "Reading a stated speed as the downstream speed when it is actually the still-water speed.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.arith.tsd-races",
        intuition=(
            "Two children race across a playground. When the faster one touches the wall, the slower one is "
            "still a few steps behind. Those few steps are the whole story: the two ran for the **same amount "
            "of time**, so the gap between them tells you exactly how their speeds compare."
        ),
        core=(
            "The key to every race question is that both runners are running for the same duration. When time "
            "is equal, distance is directly proportional to speed. So if A beats B by some metres, then\n\n"
            "$$\\frac{\\text{speed of A}}{\\text{speed of B}} = \\frac{\\text{distance A ran}}{\\text{distance B ran}}$$\n\n"
            "A head start (or 'start of $x$ metres') means B begins $x$ metres up the track, so B only has to "
            "run the remaining distance. A dead heat means both finish at the same moment."
        ),
        examples=[
            EX(
                stem="In a 100 m race, A beats B by 20 m. Compare their speeds.",
                solution=(
                    "In the time A covers 100 m, B covers only $100 - 20 = 80$ m.\n\n"
                    "Equal time means speeds are in the ratio of distances: "
                    "$\\dfrac{\\text{A}}{\\text{B}} = \\dfrac{100}{80} = \\dfrac{5}{4}$.\n\n"
                    "So A is 1.25 times as fast as B."
                ),
            ),
            EX(
                stem="A and B have speeds in the ratio 5 : 4. In a 200 m race, what head start must A give B for a dead heat?",
                solution=(
                    "In the time A runs 200 m, B runs $200 \\times \\dfrac{4}{5} = 160$ m.\n\n"
                    "For them to finish together, B must already be $200 - 160 = 40$ m up the track.\n\n"
                    "So A gives B a 40 m head start."
                ),
                alt="Equivalently, B needs to cover only 160 m in the time A covers 200 m — and a 40 m start achieves exactly that.",
            ),
        ],
        formulas=[
            FC(
                title="Beating by a distance",
                body="If A beats B by $d$ in a race of length $L$, then $\\dfrac{v_A}{v_B} = \\dfrac{L}{L - d}$.",
                example="Beaten by 25 m in 200 m gives a speed ratio $\\dfrac{200}{175} = \\dfrac{8}{7}$.",
            ),
            FC(
                title="Beating by a time",
                body="If A finishes in $t_A$ and B in $t_B$, then A beats B by the distance B covers in $t_B - t_A$, i.e. $\\dfrac{L}{t_B}(t_B - t_A)$.",
                example="A takes 20 s and B 25 s over 100 m: B's speed is 4 m/s, so A wins by $4 \\times 5 = 20$ m.",
            ),
        ],
        traps=[
            "Treating 'beats by 20 m' as though B ran the full distance. B ran 20 m less.",
            "Confusing 'beats by 5 seconds' with 'beats by 5 metres' — one is a time gap, the other a distance gap.",
            "Forgetting that a head start reduces the distance B must run, not B's speed.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.arith.tsd-circular-tracks",
        intuition=(
            "Think of the hands of a clock. The minute hand keeps catching up to the hour hand, over and over. "
            "They do not need to reach a finish line — they meet whenever the faster one has gained a full lap "
            "on the slower one.\n\n"
            "A circular running track is the same. There is no end, so 'meeting' means the gap between the "
            "runners has grown (or shrunk) to exactly one whole lap."
        ),
        core=(
            "Two different questions get asked, and they need different tools.\n\n"
            "**Meeting anywhere on the track** is a relative-speed question. Running in opposite directions "
            "they close a full lap at the sum of their speeds; running the same way the faster gains a full "
            "lap at the difference.\n\n"
            "**Meeting at the starting point** is a completely different, LCM question. Each runner is back at "
            "the start only after a whole number of laps, so you need the first time that is a whole-number "
            "multiple of both of their individual lap times."
        ),
        examples=[
            EX(
                stem="Two runners start together on a 400 m circular track, running in opposite directions at 6 m/s and 4 m/s. When do they first meet?",
                solution=(
                    "Running towards each other around the loop, they close the gap at $6 + 4 = 10$ m/s.\n\n"
                    "Between two meetings they must together cover one full lap of 400 m.\n\n"
                    "Time $= \\dfrac{400}{10} = 40$ seconds."
                ),
            ),
            EX(
                stem="On the same 400 m track, the two run in the same direction at 6 m/s and 4 m/s. When does the faster first lap the slower?",
                solution=(
                    "Same direction, so the gap grows at $6 - 4 = 2$ m/s.\n\n"
                    "To lap the other runner, the faster must gain a whole 400 m.\n\n"
                    "Time $= \\dfrac{400}{2} = 200$ seconds."
                ),
                alt="Notice it takes far longer than the head-on case — the same reason a slow overtake on a motorway feels endless.",
            ),
        ],
        formulas=[
            FC(
                title="First meeting on a circular track",
                body="Opposite directions: $\\dfrac{C}{v_1 + v_2}$. Same direction: $\\dfrac{C}{|v_1 - v_2|}$, where $C$ is the circumference.",
                example="On a 600 m track at 5 and 3 m/s: 75 s head-on, 300 s same direction.",
            ),
            FC(
                title="Meeting again at the starting point",
                body="Take the LCM of the individual lap times $\\dfrac{C}{v_1}$ and $\\dfrac{C}{v_2}$. This is not a relative-speed calculation.",
                example="Lap times of 40 s and 60 s coincide at the start after LCM$(40, 60) = 120$ s.",
            ),
        ],
        traps=[
            "Using relative speed for a 'meet at the starting point' question. That one needs an LCM of lap times.",
            "Forgetting that meeting anywhere on the track happens far more often than meeting at the start.",
            "Using the sum of speeds for runners going the same way.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.arith.time-work-efficiency-wages",
        intuition=(
            "If you can paint a room in 4 hours, then in one hour you paint a quarter of it. That is your "
            "**rate**. If your friend takes 6 hours, their rate is one sixth per hour.\n\n"
            "Put you both in the room and in one hour you finish a quarter plus a sixth. You cannot add the "
            "times (4 and 6 hours) — that would be nonsense, since two people should finish faster, not slower. "
            "You add the rates."
        ),
        core=(
            "Convert every worker into work-per-day and the topic becomes simple addition. Someone who "
            "finishes in $n$ days does $\\dfrac{1}{n}$ of the job per day.\n\n"
            "Efficiency is just another word for rate. Being 'twice as efficient' means twice the rate, which "
            "means half the time. Efficiency and time are inversely related — always.\n\n"
            "Wages follow work done, not hours present. If A does twice as much of the job as B, A gets twice "
            "the money, so the pay splits in the ratio of their rates."
        ),
        examples=[
            EX(
                stem="A can do a job in 12 days and B in 24 days. How long do they take together?",
                solution=(
                    "A's rate is $\\dfrac{1}{12}$ per day; B's is $\\dfrac{1}{24}$ per day.\n\n"
                    "Together: $\\dfrac{1}{12} + \\dfrac{1}{24} = \\dfrac{2}{24} + \\dfrac{1}{24} = \\dfrac{3}{24} = \\dfrac{1}{8}$ per day.\n\n"
                    "So they finish in 8 days."
                ),
                alt="Sanity check: 8 days is less than either 12 or 24. Adding a helper must always reduce the time.",
            ),
            EX(
                stem="A can do a job in 10 days, B in 15 days. They work together and earn Rs. 3000 in total. What is A's share?",
                solution=(
                    "Rates: A is $\\dfrac{1}{10}$, B is $\\dfrac{1}{15}$ per day. Working the same number of days, "
                    "the work they each do is in the ratio of their rates.\n\n"
                    "$\\dfrac{1}{10} : \\dfrac{1}{15} = 3 : 2$ (multiply both by 30).\n\n"
                    "A's share $= \\dfrac{3}{5} \\times 3000 = 1800$."
                ),
                alt="Shortcut: the ratio of rates for times $a$ and $b$ is simply $b : a$ — the times, flipped.",
            ),
        ],
        formulas=[
            FC(
                title="Rate of work",
                body="Finishing in $n$ days means a rate of $\\dfrac{1}{n}$ per day. Add rates, never times.",
                example="Rates $\\dfrac{1}{6}$ and $\\dfrac{1}{12}$ combine to $\\dfrac{1}{4}$, so 4 days together.",
            ),
            FC(
                title="Efficiency and time",
                body="If B is $p$ percent more efficient than A, then B takes $\\dfrac{100}{100 + p}$ of A's time.",
                example="25 percent more efficient than someone who takes 20 days means $20 \\times \\dfrac{100}{125} = 16$ days.",
            ),
            FC(
                title="Wages",
                body="Pay splits in the ratio of work done. For workers taking $a$ and $b$ days, that ratio is $b : a$.",
                example="Times 8 and 12 days split the money 12 : 8, i.e. 3 : 2.",
            ),
        ],
        traps=[
            "Adding the times instead of the rates. If the combined time is not smaller than every individual time, something went wrong.",
            "Splitting wages equally, or in the ratio of days taken rather than the ratio of work done.",
            "Reading 'twice as efficient' as 'twice the time'. It means half the time.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.arith.time-work-chain-rule",
        intuition=(
            "Digging a hole takes a certain amount of total effort — say, 60 hours of one person's shovelling. "
            "It does not matter whether that is one person for 60 hours, or ten people for 6 hours. The hole "
            "does not care who does the work.\n\n"
            "That fixed lump of effort is the idea behind the chain rule. Count it in **man-days** (or "
            "man-hours), and then redistribute it however the question asks."
        ),
        core=(
            "For a fixed job, the total effort is constant:\n\n"
            "$$M_1 \\times D_1 \\times H_1 = M_2 \\times D_2 \\times H_2$$\n\n"
            "where $M$ is the number of workers, $D$ the days and $H$ the hours per day. More workers means "
            "fewer days; that is an inverse relationship.\n\n"
            "If the size of the job changes too, put the work on the other side: "
            "$\\dfrac{M_1 D_1 H_1}{W_1} = \\dfrac{M_2 D_2 H_2}{W_2}$. Everything that supplies effort "
            "multiplies on top; the amount of work divides underneath."
        ),
        examples=[
            EX(
                stem="If 12 men build a wall in 15 days, how long will 20 men take?",
                solution=(
                    "Total effort $= 12 \\times 15 = 180$ man-days, and the wall needs that much regardless of "
                    "the crew size.\n\n"
                    "With 20 men: $\\dfrac{180}{20} = 9$ days."
                ),
                alt="More men, fewer days — and 9 is indeed less than 15, so the direction is right.",
            ),
            EX(
                stem="If 10 men working 8 hours a day finish a job in 6 days, how many days will 15 men working 4 hours a day take?",
                solution=(
                    "Total effort $= 10 \\times 8 \\times 6 = 480$ man-hours.\n\n"
                    "The new crew supplies $15 \\times 4 = 60$ man-hours per day.\n\n"
                    "Days needed $= \\dfrac{480}{60} = 8$ days."
                ),
                alt=(
                    "The crew grew but the working day shrank more, so the job takes longer than 6 days. "
                    "Checking the direction of change before computing catches most errors here."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Chain rule",
                body="$\\dfrac{M_1 D_1 H_1}{W_1} = \\dfrac{M_2 D_2 H_2}{W_2}$",
                example="8 men, 10 days, 6 hours on 1 job equals 12 men, $D$ days, 4 hours on 1 job, giving $D = 10$.",
            ),
            FC(
                title="Man-days",
                body="Total effort $=$ workers $\\times$ days $\\times$ hours per day. For a fixed job this is invariant.",
                example="15 men for 8 days is 120 man-days, the same job as 20 men for 6 days.",
            ),
        ],
        traps=[
            "Setting up a direct proportion where it should be inverse. More workers must mean fewer days.",
            "Forgetting to scale by the size of the job when the second job is bigger or smaller.",
            "Dropping the hours-per-day factor when it differs between the two scenarios.",
        ],
        minutes=6,
    ),
]
