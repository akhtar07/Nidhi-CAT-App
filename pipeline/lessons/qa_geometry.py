"""Geometry lessons."""

from __future__ import annotations

from . import EX, FC, LessonSpec

SPECS = [
    LessonSpec(
        mt="qa.geometry.lines-angles",
        intuition=(
            "Stand facing north and spin all the way round back to north. You have turned 360 degrees. Turn "
            "only half of that and you are facing south — a straight line, 180 degrees.\n\n"
            "Those two numbers, 360 for a full turn and 180 for a straight line, generate almost every angle "
            "fact in geometry. Everything else is bookkeeping."
        ),
        core=(
            "Angles on a straight line add to 180. Angles round a point add to 360. Two crossing lines make "
            "vertically opposite angles, which are always equal.\n\n"
            "When a transversal cuts two **parallel** lines, three relationships appear:\n\n"
            "**Corresponding** angles (same position at each crossing) are equal.\n"
            "**Alternate** angles (opposite sides of the transversal, between the parallels) are equal.\n"
            "**Co-interior** angles (same side, between the parallels) add to 180.\n\n"
            "Two of the three are equalities and only one is a sum — mixing them up is the commonest error here."
        ),
        examples=[
            EX(
                stem="Two parallel lines are cut by a transversal. One co-interior angle is 65 degrees. Find the other.",
                solution=(
                    "Co-interior angles between parallel lines are supplementary, meaning they add to 180.\n\n"
                    "The other angle is $180 - 65 = 115$ degrees."
                ),
                alt="Sanity check: co-interior angles are equal only when both are 90. Since 65 is not 90, the two must differ.",
            ),
            EX(
                stem="Three angles meet at a point on one side of a straight line. Two are 55 and 70 degrees. Find the third.",
                solution=(
                    "Angles on a straight line total 180 degrees.\n\n"
                    "$180 - 55 - 70 = 55$ degrees."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Angle sums",
                body="On a straight line: 180 degrees. Around a point: 360 degrees. Vertically opposite angles are equal.",
                example="If one angle at a crossing is 40, the opposite one is 40 and each neighbour is 140.",
            ),
            FC(
                title="Parallel lines and a transversal",
                body="Corresponding angles equal. Alternate angles equal. Co-interior angles add to 180.",
                example="A transversal making 70 degrees gives another 70 (corresponding) and a 110 (co-interior).",
            ),
        ],
        traps=[
            "Using an equality rule for co-interior angles. Those are the only pair that sum rather than match.",
            "Applying parallel-line rules when the lines are not actually stated to be parallel.",
            "Assuming a diagram is to scale. Work from the stated values, never from how it looks.",
        ],
        minutes=5,
    ),
    LessonSpec(
        mt="qa.geometry.triangles",
        intuition=(
            "Tear the three corners off a paper triangle and place them side by side. They always form a "
            "perfectly straight line. That is the 180-degree rule, and it holds for every triangle ever drawn.\n\n"
            "**Similar** triangles are photocopies at different zoom levels: same shape, same angles, all sides "
            "scaled by the same factor. **Congruent** triangles are the same photocopy — identical in every way."
        ),
        core=(
            "Angles sum to 180. Any exterior angle equals the sum of the two opposite interior angles.\n\n"
            "The **triangle inequality** says any two sides must together exceed the third; otherwise the "
            "triangle cannot close.\n\n"
            "Similarity is the real workhorse. If two triangles have equal angles, their sides are in a fixed "
            "ratio — and their **areas** are in the square of that ratio. Doubling every length quadruples the "
            "area, which surprises people every time.\n\n"
            "Pythagoras applies only to right-angled triangles. Memorising a few triples (3-4-5, 5-12-13, "
            "8-15-17) and their multiples saves real time."
        ),
        examples=[
            EX(
                stem="A right triangle has legs 9 cm and 12 cm. Find its hypotenuse.",
                solution=(
                    "$h^2 = 9^2 + 12^2 = 81 + 144 = 225$, so $h = 15$ cm.\n\n"
                    "This is the 3-4-5 triple scaled by 3."
                ),
                alt="Recognising 9-12-15 as $3 \\times (3,4,5)$ gives the answer with no arithmetic at all.",
            ),
            EX(
                stem="Two similar triangles have corresponding sides 4 cm and 6 cm. The smaller has area 20 square cm. Find the area of the larger.",
                solution=(
                    "The ratio of sides is $\\dfrac{6}{4} = \\dfrac32$.\n\n"
                    "Areas scale as the **square** of that ratio: $\\left(\\dfrac32\\right)^2 = \\dfrac94$.\n\n"
                    "Area $= 20 \\times \\dfrac94 = 45$ square cm."
                ),
                alt="A common wrong answer is 30, from scaling the area by $\\frac32$ instead of $\\frac94$.",
            ),
        ],
        formulas=[
            FC(
                title="Angle facts",
                body="Interior angles sum to 180. An exterior angle equals the sum of the two remote interior angles.",
                example="Angles 50 and 60 force the third to be 70, and the exterior angle there is 110.",
            ),
            FC(
                title="Area",
                body="$\\dfrac12 \\times \\text{base} \\times \\text{height}$, or Heron's $\\sqrt{s(s-a)(s-b)(s-c)}$ with $s = \\dfrac{a+b+c}{2}$.",
                example="Sides 13, 14, 15 give $s = 21$ and area $\\sqrt{21 \\times 8 \\times 7 \\times 6} = 84$.",
            ),
            FC(
                title="Similarity",
                body="Equal angles mean sides in a constant ratio $k$. Areas are then in the ratio $k^2$.",
                example="Sides in 2 : 3 means areas in 4 : 9.",
            ),
            FC(
                title="Triangle inequality",
                body="Each pair of sides must sum to more than the third side.",
                example="Sides 3, 4 and 8 cannot form a triangle, since $3 + 4 < 8$.",
            ),
        ],
        traps=[
            "Scaling areas by the side ratio instead of its square.",
            "Applying Pythagoras to a triangle that is not right-angled.",
            "Forgetting to check the triangle inequality when a question asks which side lengths are possible.",
        ],
        minutes=8,
    ),
    LessonSpec(
        mt="qa.geometry.quadrilaterals-polygons",
        intuition=(
            "Walk all the way around the edge of a field and back to where you started, facing the same way. "
            "You have turned a full 360 degrees, no matter how many corners the field has — three or thirty.\n\n"
            "That fact gives you the exterior angles instantly. Each interior angle is then just what is left "
            "over from a straight line."
        ),
        core=(
            "Exterior angles of **any** polygon sum to 360. For a regular polygon with $n$ sides, each "
            "exterior angle is $\\dfrac{360}{n}$, and each interior angle is its supplement.\n\n"
            "Interior angles sum to $(n-2) \\times 180$, because the polygon splits into $n - 2$ triangles.\n\n"
            "For quadrilaterals, the family tree matters: a square is a rectangle **and** a rhombus; every "
            "rectangle is a parallelogram. Diagonals distinguish them — a rectangle's are equal, a rhombus's "
            "cross at right angles, a square's do both."
        ),
        examples=[
            EX(
                stem="Find each interior angle of a regular octagon.",
                solution=(
                    "Each exterior angle is $\\dfrac{360}{8} = 45$ degrees.\n\n"
                    "Each interior angle is $180 - 45 = 135$ degrees.\n\n"
                    "Check: $8 \\times 135 = 1080 = (8-2) \\times 180$."
                ),
            ),
            EX(
                stem="How many diagonals does a decagon have?",
                solution=(
                    "Each of the 10 vertices connects to $10 - 3 = 7$ others by a diagonal (excluding itself "
                    "and its two neighbours).\n\n"
                    "That counts $10 \\times 7 = 70$, but each diagonal is counted from both ends.\n\n"
                    "Diagonals $= \\dfrac{70}{2} = 35$."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Polygon angles",
                body="Interior angles sum to $(n-2) \\times 180$. Exterior angles always sum to 360.",
                example="A hexagon's interiors total 720; each is 120 if regular.",
            ),
            FC(
                title="Diagonals",
                body="A polygon with $n$ sides has $\\dfrac{n(n-3)}{2}$ diagonals.",
                example="A pentagon has $\\dfrac{5 \\times 2}{2} = 5$.",
            ),
            FC(
                title="Quadrilateral areas",
                body="Parallelogram: base $\\times$ height. Trapezium: $\\dfrac12(a+b)h$. Rhombus: $\\dfrac12 d_1 d_2$.",
                example="A rhombus with diagonals 6 and 8 has area 24.",
            ),
        ],
        traps=[
            "Using $n \\times 180$ for the interior sum instead of $(n-2) \\times 180$.",
            "Forgetting to halve when counting diagonals, so counting each one twice.",
            "Assuming a parallelogram has equal diagonals. Only rectangles and squares do.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.geometry.circles",
        intuition=(
            "Stand in the middle of a round room and look at a painting on the wall. Now walk to the wall "
            "yourself and look at the same painting from there. From the centre it looks twice as wide as it "
            "does from the edge.\n\n"
            "That is the central-angle theorem: the angle at the centre is always double the angle at the "
            "circumference, when both look at the same arc."
        ),
        core=(
            "Three facts do most of the work.\n\n"
            "**Centre doubles.** The angle at the centre is twice any angle at the circumference standing on "
            "the same arc. A special case: an angle in a semicircle is always 90 degrees.\n\n"
            "**Tangents meet radii at right angles**, and the two tangents drawn from an external point are "
            "equal in length.\n\n"
            "**Cyclic quadrilaterals** — with all four corners on the circle — have opposite angles summing "
            "to 180."
        ),
        examples=[
            EX(
                stem="An arc subtends 40 degrees at a point on the circumference. What angle does it subtend at the centre?",
                solution=(
                    "The angle at the centre is double the angle at the circumference on the same arc.\n\n"
                    "$2 \\times 40 = 80$ degrees."
                ),
            ),
            EX(
                stem="Find the area of a sector of radius 14 cm subtending 90 degrees at the centre. Use $\\pi = \\frac{22}{7}$.",
                solution=(
                    "A 90-degree sector is $\\dfrac{90}{360} = \\dfrac14$ of the whole circle.\n\n"
                    "Full area $= \\dfrac{22}{7} \\times 14^2 = \\dfrac{22}{7} \\times 196 = 616$ square cm.\n\n"
                    "Sector area $= \\dfrac{616}{4} = 154$ square cm."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Circle basics",
                body="Circumference $= 2\\pi r$. Area $= \\pi r^2$.",
                example="$r = 7$ gives circumference 44 and area 154 with $\\pi = \\frac{22}{7}$.",
            ),
            FC(
                title="Sector and arc",
                body="Arc length $= \\dfrac{\\theta}{360} \\times 2\\pi r$. Sector area $= \\dfrac{\\theta}{360} \\times \\pi r^2$.",
                example="A 60-degree sector is one sixth of the circle.",
            ),
            FC(
                title="Angle theorems",
                body="Angle at centre $= 2 \\times$ angle at circumference. Angle in a semicircle is 90. Opposite angles of a cyclic quadrilateral sum to 180.",
                example="A cyclic quadrilateral with one angle 70 has its opposite angle 110.",
            ),
            FC(
                title="Tangents",
                body="A tangent is perpendicular to the radius at the point of contact, and the two tangents from an external point are equal.",
                example="From a point 13 cm from the centre of a circle of radius 5, the tangent length is 12.",
            ),
        ],
        traps=[
            "Halving instead of doubling when moving from circumference to centre.",
            "Using degrees directly in an arc-length formula without the $\\frac{\\theta}{360}$ fraction.",
            "Applying cyclic-quadrilateral rules to a quadrilateral whose corners are not all on the circle.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.geometry.coordinate-geometry",
        intuition=(
            "Coordinate geometry is geometry with a street map. Instead of describing a point as 'over there', "
            "you give it an address: 3 blocks east, 4 blocks north.\n\n"
            "Once every point has an address, distances and midpoints become arithmetic. The distance formula "
            "is just Pythagoras applied to the east-west and north-south gaps."
        ),
        core=(
            "The distance between two points is $\\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$ — the horizontal and "
            "vertical gaps are the legs of a right triangle, and the distance is its hypotenuse.\n\n"
            "The **section formula** finds a point dividing a segment in a given ratio. For the midpoint, the "
            "ratio is 1 : 1 and it collapses to simply averaging the coordinates.\n\n"
            "A line's **slope** is rise over run. Parallel lines share a slope; perpendicular lines have slopes "
            "multiplying to $-1$."
        ),
        examples=[
            EX(
                stem="Find the distance between $(2, 3)$ and $(7, 15)$.",
                solution=(
                    "Horizontal gap $= 7 - 2 = 5$. Vertical gap $= 15 - 3 = 12$.\n\n"
                    "$d = \\sqrt{5^2 + 12^2} = \\sqrt{25 + 144} = \\sqrt{169} = 13$."
                ),
                alt="The 5-12-13 triple appears again — worth recognising on sight.",
            ),
            EX(
                stem="Find the point dividing the segment from $(1, 2)$ to $(7, 8)$ in the ratio 2 : 1.",
                solution=(
                    "By the section formula with $m = 2$, $n = 1$:\n\n"
                    "$x = \\dfrac{2(7) + 1(1)}{3} = \\dfrac{15}{3} = 5$\n\n"
                    "$y = \\dfrac{2(8) + 1(2)}{3} = \\dfrac{18}{3} = 6$\n\n"
                    "The point is $(5, 6)$."
                ),
                alt="A 2 : 1 split sits two-thirds of the way along, and $(5,6)$ is indeed two-thirds from $(1,2)$ to $(7,8)$.",
            ),
        ],
        formulas=[
            FC(
                title="Distance and midpoint",
                body="$d = \\sqrt{(x_2-x_1)^2 + (y_2-y_1)^2}$. Midpoint $= \\left(\\dfrac{x_1+x_2}{2}, \\dfrac{y_1+y_2}{2}\\right)$.",
                example="From $(0,0)$ to $(6,8)$: distance 10, midpoint $(3,4)$.",
            ),
            FC(
                title="Section formula",
                body="Dividing internally in ratio $m : n$ gives $\\left(\\dfrac{mx_2+nx_1}{m+n}, \\dfrac{my_2+ny_1}{m+n}\\right)$.",
                example="Ratio 1 : 3 from $(0,0)$ to $(8,4)$ gives $(2,1)$.",
            ),
            FC(
                title="Slope",
                body="$m = \\dfrac{y_2-y_1}{x_2-x_1}$. Parallel lines have equal slopes; perpendicular slopes multiply to $-1$.",
                example="A line of slope 2 is perpendicular to one of slope $-\\frac12$.",
            ),
            FC(
                title="Area of a triangle from vertices",
                body="$\\dfrac12 |x_1(y_2-y_3) + x_2(y_3-y_1) + x_3(y_1-y_2)|$",
                example="$(0,0)$, $(4,0)$, $(0,3)$ gives area 6.",
            ),
        ],
        traps=[
            "Sign errors when subtracting coordinates. Squaring hides them in distance, but not in slope.",
            "Swapping $m$ and $n$ in the section formula. The ratio $m : n$ weights the **far** point by $m$.",
            "Forgetting the absolute value in the area formula, and reporting a negative area.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.geometry.trigonometry",
        intuition=(
            "Lean a ladder against a wall. Keep the angle the same but use a ladder twice as long, and both "
            "the height it reaches and its distance from the wall double. The **ratio** between them does not "
            "change at all.\n\n"
            "That constant ratio, fixed by the angle alone, is what sine, cosine and tangent record. That is "
            "why a single angle plus one length tells you everything else."
        ),
        core=(
            "In a right-angled triangle, relative to an angle:\n\n"
            "$\\sin = \\dfrac{\\text{opposite}}{\\text{hypotenuse}}$, "
            "$\\cos = \\dfrac{\\text{adjacent}}{\\text{hypotenuse}}$, "
            "$\\tan = \\dfrac{\\text{opposite}}{\\text{adjacent}}$.\n\n"
            "For heights-and-distances questions, tangent is almost always the one you want, because it links "
            "the height you cannot reach to the ground distance you can measure.\n\n"
            "Angle of **elevation** is measured looking up from the horizontal; angle of **depression** looking "
            "down. The two are equal between the same pair of points, which often shortcuts a diagram."
        ),
        examples=[
            EX(
                stem="From a point 50 m from the foot of a tower, the angle of elevation of the top is 60 degrees. Find the tower's height.",
                solution=(
                    "The height is opposite the angle and the 50 m is adjacent, so use tangent.\n\n"
                    "$\\tan 60^\\circ = \\dfrac{h}{50}$\n\n"
                    "$h = 50\\sqrt3 \\approx 86.6$ m."
                ),
            ),
            EX(
                stem="A ladder 10 m long leans against a wall at 30 degrees to the ground. How high up the wall does it reach?",
                solution=(
                    "The height is opposite the angle and the ladder is the hypotenuse, so use sine.\n\n"
                    "$\\sin 30^\\circ = \\dfrac{h}{10}$, and $\\sin 30^\\circ = \\dfrac12$.\n\n"
                    "$h = 10 \\times \\dfrac12 = 5$ m."
                ),
            ),
        ],
        formulas=[
            FC(
                title="The three ratios",
                body="$\\sin\\theta = \\dfrac{O}{H}$, $\\cos\\theta = \\dfrac{A}{H}$, $\\tan\\theta = \\dfrac{O}{A} = \\dfrac{\\sin\\theta}{\\cos\\theta}$.",
                example="In a 3-4-5 triangle, the angle opposite 3 has $\\sin = 0.6$, $\\cos = 0.8$, $\\tan = 0.75$.",
            ),
            FC(
                title="Standard angles",
                body=(
                    "$\\sin 30 = \\dfrac12$, $\\sin 45 = \\dfrac{1}{\\sqrt2}$, $\\sin 60 = \\dfrac{\\sqrt3}{2}$. "
                    "Cosine runs the same list backwards. $\\tan 30 = \\dfrac{1}{\\sqrt3}$, $\\tan 45 = 1$, $\\tan 60 = \\sqrt3$."
                ),
                example="$\\cos 60 = \\frac12$, matching $\\sin 30$.",
            ),
            FC(
                title="Identities",
                body="$\\sin^2\\theta + \\cos^2\\theta = 1$, and $1 + \\tan^2\\theta = \\sec^2\\theta$.",
                example="If $\\sin\\theta = 0.6$ then $\\cos\\theta = 0.8$.",
            ),
        ],
        traps=[
            "Picking the wrong ratio. Identify which sides the question gives and wants before choosing.",
            "Mixing up elevation and depression when drawing the diagram.",
            "Forgetting that 'opposite' and 'adjacent' are relative to the angle you are using, and swap for the other acute angle.",
        ],
        minutes=7,
    ),
    LessonSpec(
        mt="qa.geometry.mensuration-2d",
        intuition=(
            "Area is how much paint you need to cover a shape. Perimeter is how much fence you need around it. "
            "They are completely different quantities, and two shapes with the same perimeter can have wildly "
            "different areas — a long thin rectangle versus a square, for instance.\n\n"
            "Most exam questions are one standard shape, or a standard shape with a piece added or removed."
        ),
        core=(
            "Learn the handful of standard formulas, then treat every complicated figure as standard shapes "
            "**added together or subtracted from each other**. A path around a garden is the big rectangle "
            "minus the small one. A shaded region is usually one shape with another cut out.\n\n"
            "One relationship worth internalising: scaling every length by $k$ multiplies the perimeter by $k$ "
            "but the area by $k^2$. Doubling a room's dimensions quadruples the carpet needed."
        ),
        examples=[
            EX(
                stem="A rectangular garden 20 m by 15 m is surrounded by a 2 m wide path on the outside. Find the area of the path.",
                solution=(
                    "The path adds 2 m on **each** side, so the outer rectangle is $20 + 4 = 24$ m by "
                    "$15 + 4 = 19$ m.\n\n"
                    "Outer area $= 24 \\times 19 = 456$ square m.\n"
                    "Garden area $= 20 \\times 15 = 300$ square m.\n\n"
                    "Path area $= 456 - 300 = 156$ square m."
                ),
                alt="Adding 2 m only once to each dimension is the classic error — the path runs along both sides.",
            ),
            EX(
                stem="Find the area of a circle inscribed in a square of side 14 cm. Use $\\pi = \\frac{22}{7}$.",
                solution=(
                    "An inscribed circle touches all four sides, so its diameter equals the square's side.\n\n"
                    "Diameter 14, so radius 7.\n\n"
                    "Area $= \\dfrac{22}{7} \\times 49 = 154$ square cm."
                ),
            ),
        ],
        formulas=[
            FC(
                title="Standard areas",
                body="Rectangle $lb$. Triangle $\\dfrac12 bh$. Circle $\\pi r^2$. Trapezium $\\dfrac12(a+b)h$. Parallelogram $bh$.",
                example="A trapezium with parallel sides 8 and 12 and height 5 has area 50.",
            ),
            FC(
                title="Perimeters",
                body="Rectangle $2(l+b)$. Circle $2\\pi r$. Square $4a$.",
                example="A square of side 9 has perimeter 36 and area 81.",
            ),
            FC(
                title="Scaling",
                body="Multiplying every length by $k$ multiplies perimeter by $k$ and area by $k^2$.",
                example="Tripling the side of a square makes the area nine times larger.",
            ),
        ],
        traps=[
            "Adding a border width only once per dimension instead of twice.",
            "Confusing radius and diameter in circle formulas.",
            "Mixing units — metres with centimetres — inside one calculation.",
        ],
        minutes=6,
    ),
    LessonSpec(
        mt="qa.geometry.mensuration-3d",
        intuition=(
            "Volume is how much water a container holds. Surface area is how much wrapping paper you would "
            "need to cover it. A closed box needs paper on all six faces; an open tank needs only five.\n\n"
            "Reading whether the shape is open or closed, solid or hollow, decides which formula applies — and "
            "that is where most marks are lost."
        ),
        core=(
            "For any prism or cylinder, volume is simply **base area times height**. A cylinder is a circle "
            "extruded upward, so its volume is $\\pi r^2 h$.\n\n"
            "Cones and pyramids taper to a point and hold exactly **one third** as much as the prism or "
            "cylinder with the same base and height.\n\n"
            "For surface area, decide what surfaces actually exist. A cylindrical pipe open at both ends has "
            "only the curved surface $2\\pi r h$; a sealed tin adds two circular ends."
        ),
        examples=[
            EX(
                stem="Find the volume of a cylinder of radius 7 cm and height 10 cm. Use $\\pi = \\frac{22}{7}$.",
                solution=(
                    "Volume $= \\pi r^2 h = \\dfrac{22}{7} \\times 49 \\times 10$.\n\n"
                    "$= 22 \\times 7 \\times 10 = 1540$ cubic cm."
                ),
            ),
            EX(
                stem="A cube of side 6 cm is melted and recast into smaller cubes of side 2 cm. How many small cubes are formed?",
                solution=(
                    "Volume is conserved when melting and recasting.\n\n"
                    "Large cube: $6^3 = 216$ cubic cm.\n"
                    "Small cube: $2^3 = 8$ cubic cm.\n\n"
                    "Number $= \\dfrac{216}{8} = 27$."
                ),
                alt="Since $6 = 3 \\times 2$, the big cube is 3 small cubes along each edge: $3^3 = 27$.",
            ),
        ],
        formulas=[
            FC(
                title="Volumes",
                body="Cuboid $lbh$. Cube $a^3$. Cylinder $\\pi r^2 h$. Cone $\\dfrac13\\pi r^2 h$. Sphere $\\dfrac43\\pi r^3$.",
                example="A cone of radius 3 and height 7 holds $\\frac13 \\pi \\times 9 \\times 7 = 21\\pi$.",
            ),
            FC(
                title="Surface areas",
                body="Cube $6a^2$. Cylinder: curved $2\\pi rh$, total $2\\pi r(r+h)$. Sphere $4\\pi r^2$.",
                example="A closed cylinder with $r = 7$, $h = 10$ has total surface $2 \\times \\frac{22}{7} \\times 7 \\times 17 = 748$.",
            ),
            FC(
                title="Melting and recasting",
                body="Volume is conserved. Set the old volume equal to the new one and solve.",
                example="A sphere of radius 3 recast into spheres of radius 1 gives 27 of them.",
            ),
        ],
        traps=[
            "Including the ends of an open cylinder, or omitting them from a closed one.",
            "Dropping the one-third for cones and pyramids.",
            "Using slant height where vertical height is needed in a cone's volume. Volume uses the vertical height; curved surface area uses the slant.",
        ],
        minutes=7,
    ),
]
