# Outer joins: lowerings, costs, and provable conversions

Companion to the mz-optimize-memory skill. Dispatched for LEFT
JOIN and other outer-join memory questions: recognizing which lowering
a plan uses, deciding where the memory actually is, converting
provably-total LEFT JOINs to INNER, and the pushdown gaps worth
working around.

## The one-paragraph model

An outer join lowers into one of four shapes: **equi**, **general**, **VOJ**
(variadic outer join, for stacks of two or more LEFT JOINs), or **correlated**
(rare; laterals usually decorrelate into the others, and one that does not is a
decorrelation problem: subqueries.md). Every shape but the VOJ splits the
preserving side and re-unions it with a `Negate` in the middle (the VOJ reads
the driver twice and puts the diamond on each right side's null augmentation)
(`Negate Diffs` in `EXPLAIN ANALYZE` and the arrow-text plans, plain `Negate`
in the verbose physical text): the Union/Negate "diamond" this file refers to.
Searching a plan for `Negate` finds all outer joins, and also every EXCEPT and
anti-join, so confirm the shape before concluding. The shapes have very
different memory profiles, and each has an optimizer gap you can work around
from SQL. But a dataflow with an outer join often spends little on the
outer-join machinery itself: the bytes sit in the join input arrangements and
the downstream reduces and TopKs, and then rewriting the outer join buys
little. Attribute before you size.

## Recognizing the lowering

- **Equi**: `Negate` over a join whose inner side is a NARROW `Distinct
  project=[join keys]`. The cheapest binary shape. It collapses further when
  the right side is known unique on the join key (SemijoinIdempotence, below).
- **General**: `Negate` over a WIDE `Distinct project=[all preserving columns]`
  plus a self-join equating every preserving column, which costs two full-width
  arrangements and two full-width Distincts of the preserving side. The
  lowering classifies the ON conjunct by conjunct: the join takes the equi
  shape when at least one conjunct is a cross-side `=` (any expression on each
  side, so `l.a / l.b = r.v` or a cast stays equi, folded into the join key)
  and no conjunct is a Theta predicate. Theta predicates: a non-`=` predicate
  touching both sides (an inequality, an OR across the sides, `IS NOT DISTINCT
  FROM` on nullable columns; on NOT NULL columns it canonicalizes to `=`), an
  `=` whose one side mixes both inputs, a predicate that can raise a literal
  error (`1/0`) or an `error_if_null` call, and any reference to a subquery in
  the ON. Predicates on one side only, and constants, are tolerated. An ON with
  no cross-side `=` at all (`ON true`, a pure inequality) is general too.
- **VOJ**: `Negate` inside a `Threshold`, under a `Map (null, ...)`,
  with `Map (true)` real-row markers, feeding one large join.
  `Threshold` is the crisp VOJ marker. A chained VOJ (each LEFT JOIN
  keyed off the previous right side's nullable column) shows computed
  join keys of the form `case when #k IS NULL then null else ... end`,
  and it also loses the delta implementation the clean stack gets.
  Restructuring the SQL so every LEFT JOIN keys off the same base
  column yields one clean stack instead. A stack that shows `n`
  differential joins with a matched-key Distinct each and no
  `Threshold` has lost the lowering ("What breaks the VOJ lowering",
  below), and whether the lowering pays at all is a match-rate question
  ("When the VOJ lowering is the cheaper one", below).
- A LEFT JOIN whose RIGHT side is correlated (a LATERAL that references the
  left) never gets the equi lowering, whatever its ON says: the lowering
  evaluates the right side against the distinct left rows and closes the join
  with an anti-lookup keyed by the whole left row, so the plan carries the
  general shape's wide `Distinct`s over every preserving column plus the
  decorrelation's `Distinct` over the correlation columns, the most expensive
  lowering. That cost is why subqueries.md rules `LEFT JOIN LATERAL` out as a
  fix for a per-row subquery.
- Beware two false friends when classifying: column ranges printed as
  `#0..=#5` hide the real width of a Distinct, and a Distinct with
  `exp_group_size` is an aggregation, not outer-join machinery.

## Where the outer-join memory is

The machinery's cost is set by the PRESERVING (left) side and by the
lowering shape, and for the equi and general shapes the right side's size
barely enters it:

- equi: the matched-key Distinct and the anti-join run at
  distinct-left-key record counts, at key width, less when the right
  side is known unique on the key (SemijoinIdempotence, below).
- general: TWO full-width arrangements of the preserving side plus TWO
  all-columns Distincts, one over the whole preserving relation and one over
  its matched rows. A Distinct is two arrangements in the census (`Arranged
  DistinctBy` input plus `DistinctBy` output), so the shape counts as six
  full-width copies, one of which holds only the unmatched rows. The
  whole-relation Distinct is typically the largest single operator in the
  dataflow. The shape measured at roughly 4.5x a single full-width copy of the
  preserving side, the worst by far.
- VOJ: the Thresholds and the null-augment key copy run at
  distinct-key record counts, at key width. Unlike the equi and general
  shapes, a VOJ cannot read its right sides from an index: each right side is
  arranged privately over its null-augmented Union (`(*** full scan ***)` in
  the `Used Indexes` footer where an INNER join shows `(delta join lookup)`),
  at right-side scale and right-side width, once per consuming dataflow.

Consequently, this is a size question about the left input, not a default in
either direction. With a bounded or windowed left side (a recent-window
driver), the machinery is usually noise next to the join input arrangements,
TopKs, and aggregates, and the real bytes live there; attribute first. With a
large unbounded left side, the diamonds alone run at left-side scale and can be
a major share of the dataflow (a diamond-heavy dataflow can run at roughly
twice its INNER equivalent), and a general lowering over a wide left side can
dominate the dataflow outright. Settle it with per-operator attribution, never
by assumption.

## The unique-right-side collapse (SemijoinIdempotence)

An equi LEFT JOIN whose RIGHT (non-preserving) side is known unique on
the equality join key lowers without most of the diamond: when each
left row can match at most one right row, the matched-left multiset
needs no dedup, so the anti-join branch reuses the main join directly.
With the key known, the whole lowering is one join plus a Union/Negate
over the join's own CTE; with the same query against the same relation
minus the key knowledge, the plan adds a matched-key Distinct, an extra
arrangement, and a second join, all at left-side key scale.

Users can often MAKE the key known. Key inference derives uniqueness from query
structure: a right side whose outermost construct is `GROUP BY k` or `DISTINCT
ON (k)` exports `k` as a unique key, and a materialized view carries its
derived keys to every consumer through the catalog. Indexes do NOT declare
uniqueness, and plain tables have no declared keys. So when the right side is
semantically unique on the join key but the optimizer cannot see it,
restructure so it can: route consumers through a view or MV whose outermost
construct derives the key. Check what the optimizer sees with `EXPLAIN
OPTIMIZED PLAN WITH (keys)` (the annotation prints as `keys: "([n])"` on each
read; a physical plan prints none). Weigh the cost when the key must be
manufactured: a `DISTINCT ON (k)` added only to declare uniqueness pays a keyed
TopK arrangement to delete the diamonds, which tends to pay off when several
consumers share the right side (one keyed boundary serves them all); settle it
like any boundary change, with a plan diff and a measured build.

## Provable LEFT-to-INNER conversion

A LEFT JOIN whose right side carries no key the optimizer knows pays its
outer-join diamond (matched-key distinct, negate/union arrangements) at the
scale of the LEFT side, even when the right side always matches, because the
optimizer cannot derive semantic coverage guarantees. Where the key IS known,
the collapse above has already deleted the diamond and the conversion buys
nothing (LEFT and INNER then measure byte-identical, the surviving Union/Negate
holding nothing), so read the plan before spending effort here. The lever has
no census signature, so hunt for it deliberately on every rebuild. Two
guarantee classes cover most of the query-visible cases and make the conversion
a one-keyword edit:

1. **Driver-rooted right side**: the right side is a view whose
   outermost SELECT is `FROM <driver> LEFT JOIN ...` with no top-level
   WHERE and no non-guaranteed INNER join, so it emits at least one
   row per driver row by construction, and it is joined back on the
   driver key.
2. **Own-row aggregate**: the right side aggregates a join whose
   predicate is satisfied by the driver row itself (a non-strict time
   bound, no status filter), so the group is never empty.

Both classes additionally require the join key NOT NULL on the left
side; otherwise INNER drops NULL-key rows that LEFT kept. Guarantees
compose along chains: an INNER join FROM the driver TO a guaranteed
view preserves the guarantee. What is NOT provable, only askable:
foreign-key-style data properties ("the dimension row always exists").
Offer those as a question to the user, never as an assumption.
Multiplicity is never a concern; the conversion only changes the
cannot-happen empty-match case.

Size the payoff by the LEFT side ("Where the outer-join memory is" above): a
windowed driver makes the conversion a cheap rider on the next rebuild once the
guarantee holds, an unbounded one can halve a diamond-heavy dataflow. Verify
with a plan-diff A/B counting ArrangeBy blocks and arrangement entries; plan
TEXT size is misleading (wide inner delta joins grow the text while shrinking
the structure).

## The pushdown gaps and their SQL workarounds

1. **Equi cannot push a predicate into the preserving side.** A WHERE above an
   equi LEFT JOIN is re-applied to consumers but not to the shared inner join's
   preserving read. Workaround: wrap the preserving side in `(SELECT ... WHERE
   pred)`. This works only when no index on the preserving relation is
   competing for adoption: with such an index the planner keeps the read
   unfiltered to preserve adoption and lifts the filter above the join either
   way, so the workaround only moves the filter and does not shrink the
   arrangement. The block is the matched-key Distinct itself: when the right
   side is known unique on the key, SemijoinIdempotence removes it and the
   predicate then pushes all the way into the source read (`filter=` and
   `pushdown=` on `Source`), so declaring the key (a `GROUP BY k` or `DISTINCT
   ON (k)` view over the right side) is the other workaround.
2. **General cannot push a projection through itself.** The
   anti-join equates every preserving column, so all columns look used
   and unused ones ride through every arrangement. Workaround:
   pre-project the preserving side to the columns needed downstream
   plus join keys; better, rewrite the ON to a plain equi-join if the
   semantics allow. Diagnose it at a glance with `EXPLAIN OPTIMIZED
   PLAN WITH (arity)`: a general lowering shows full-width Distincts
   and ArrangeBys (arity = every preserving column, and a join
   condition equating all of them) beneath a Return whose arity is
   just the handful of columns the query reads. That arity gap is the
   dead width the workaround removes.
3. **VOJ cannot push a predicate into the augment-key read.** A WHERE
   above a VOJ stack filters the main preserving copy but not the
   distinct-keys copy that builds the null augmentation, and the double
   read also disables the storage-level pushdown for the driver.
   Workaround: push the filter into the preserving side below the
   stack. Exact, but not always cheaper, because it grows every
   Threshold; the condition is in "When the VOJ lowering is the cheaper
   one" below. Keys on the right sides do not unblock VOJ.

## What breaks the VOJ lowering

A stack of two or more LEFT JOINs gets the VOJ shape only if the whole
contiguous run of LEFT JOIN nodes survives a narrow set of checks. Every
failure is silent and drops the affected joins to the per-join equi shape
(the FALLBACK this file measures VOJ against; or to general, when the ON
also defeats the equi classifier). Count
`Threshold` nodes to see how many joins kept the lowering: `n` for a clean
`n`-deep stack, zero when the whole stack fell back. Two failure families
cut in OPPOSITE directions.

**Spine cuts** put a node the VOJ lowering will not walk through between two
LEFT JOINs. Each side of the cut is lowered on its own: a side with two or more
LEFT JOINs keeps a VOJ of its own, a side with one is lowered per join.

- An INNER (or RIGHT, or FULL) join between two LEFT JOINs. Either end of
  the stack restores the lowering, both ends are exact when the inner
  join's ON references only the driver and its own relation, and which
  end is cheaper depends on what the inner join does to the rows that
  then flow through every outer join. Check two things before moving it:
  its selectivity (a count probe of the driver's rows before and after
  the inner join) and the width it adds. A selective, narrow inner join
  belongs BELOW the stack, where it shrinks the driver for all the outer
  joins; one that multiplies rows or brings in wide columns belongs ABOVE
  the stack, so the multiplied or widened rows never enter the outer-join
  machinery. Above the stack it fuses into one join carrying two key sets
  and loses the delta implementation, which, for a neutral narrow inner
  join, can cost more than leaving the cut in place. So build both
  placements and compare; a cut that stays may be the right
  answer when the inner join is both amplifying and wide.
- `USING` and `NATURAL`, which plan as a Project over the join. The Project
  appears only when the join column is not already the leftmost column of the
  left input, and only above the first such join, so a five-deep `USING` stack
  loses exactly its bottom join, while a stack whose `USING` joins name a
  different column each loses every join, since each key is non-leftmost after
  the previous join. Write `ON l.k = r.k` instead, or reorder the driver so the
  key leads; a `USING` after an `ON` on the same column name fails (the common
  column appears more than once), so convert the whole stack at once.

**ON-clause failures** make the attempt bail. The joins BELOW the failing
one keep a VOJ if at least two remain; the failing join and everything
above it are lowered per join. One bad ON on the second join of a ten-deep
stack therefore costs all ten, so fix the LOWEST offender first. The ON
must be a conjunction of bare `column = column` equalities that each cross
from the new right side to ONE prior input, and nothing else. It is
inspected before any canonicalization, so all of the following break it,
and each is tolerated by the binary equi lowering:

- A local predicate on either side (`r.status = 'x'`, `r.v > 5`,
  `l.flag`). On the right, push it into a derived table (`LEFT JOIN
  (SELECT * FROM r WHERE ...) r ON ...`), which is always exact; on the
  left, lift it to a WHERE above the stack.
- Any expression wrapping a key: a function, a cast, arithmetic,
  `coalesce`. Precompute it as a column in a derived table on that side
  and join on the column.
- A literal comparison. `AND true` is tolerated (`USING` generates it), but
  `AND 1 = 1` is not, and a dead one left in a generated query costs the
  whole stack its lowering.
- An equality between two columns of the SAME side, one right column
  equated to two different left columns, or an ON binding the right side
  to two different prior inputs.
- A subquery in the ON, which additionally drops that join to the general
  shape, as does `ON true`.

**Correlation** disables it outright: inside a correlated subquery or a LATERAL
the attempt bails on nonzero outer arity. An outer join inside a correlated
subquery still gets the equi lowering when its ON qualifies, but with the
correlation columns prefixed to every key of its diamond (the matched-key
Distinct and both anti-join arrangements are keyed by correlation columns plus
join key) and its inputs cross-joined with the distinct outer keys, so every
diamond arrangement carries the correlation key at its width. An UNCORRELATED
derived table or scalar subquery around the stack keeps the full VOJ, so the
trigger is correlation, not subquery-ness. A `LEFT JOIN LATERAL` inside the
stack breaks it; one at the top leaves the joins below intact if at least two
of them remain. Decorrelate by hand: compute the stack once at the top level,
aggregate by the correlation key, and LEFT JOIN that to the outer relation
(wrapping the aggregate in `coalesce` where the scalar subquery's default
differs). Worth doing on its own, since the correlated form carries the outer
key through every arrangement of the stack.

On a 3-deep stack each of these costs 1.4x to 2.0x the VOJ form, the
whole-stack failures more than the partial ones. Confirm a fix by counting
`Threshold` nodes, and prove it exact with
`EXCEPT ALL` in both directions, seeded with NULL keys and duplicate keys.

## When the VOJ lowering is the cheaper one

VOJ is not a strict improvement. Three things decide the common case, and each
can flip the sign on its own: the match rate, whether the right sides are known
unique on the join key, and a selective predicate on the driver. Check them in
that order, adjust for depth and width, then check the two topology traps
below, which can flip it as well.

**Match rate**, the fraction of the driver's distinct join keys that find
a row on the right. VOJ gives each right side one all-null augmentation
row per UNMATCHED driver key and maintains a key-width Threshold over the
symmetric difference of the two key sets, so its cost rises as the match
rate falls, while the per-join fallback's matched-key Distinct empties
out. Measured on a 3-deep stack (200,000-row driver, 97,500 distinct
keys, 100,000-row right sides without a declared key), varying only the
overlap:

    match rate                    100%   75%    50%    25%    0%
    fallback/VOJ, unkeyed rights  2.07x  1.28x  0.99x  0.67x  0.51x

(above 1.0 the fallback costs more, so VOJ wins).

**Declared keys on the right sides** move that crossover a long way. When a
right side is known unique on the join key (a `GROUP BY k` or `DISTINCT ON (k)`
view, or a materialized view over either; check with `EXPLAIN OPTIMIZED PLAN
WITH (keys)`), the fallback's diamond collapses through SemijoinIdempotence:
three plain joins and no Distinct where the unkeyed stack has six joins and
three Distincts. VOJ gets NO equivalent, because its augmented right is a Union
whose key no longer holds, and the lowering discards the key set outright. The
keyed fallback is also nearly flat in the match rate, since the collapse
deletes exactly the part that was sensitive to it. A separate build of the same
stack with keyed rights:

    match rate                    100%   75%    50%
    fallback/VOJ, keyed rights    1.64x  1.00x  0.81x

So on that shape the crossover sits near a 50% match rate with unkeyed rights
and near 75% with keyed ones. Depth and width move it, so treat both as
starting estimates and settle a close call with a build. The unique-right-side
collapse that helps a binary LEFT JOIN therefore also makes a multi-join stack
a worse fit for VOJ.

**A selective predicate on the driver** above the stack is where the two
lowerings are furthest apart, in both directions. Neither pushes it on
its own: the equi lowering cannot push a predicate to the preserving side
while its diamond stands, and VOJ's augment-key
branch reads the driver unfiltered, which additionally disables the
storage-level pushdown, so `Source <driver>` shows no `filter=` line at
all. With UNKEYED rights VOJ wins big (3.2x on a 1%-selective filter),
because the fallback's block is the worse of the two. With KEYED rights
the collapse unblocks the fallback completely, `Source <driver>` gains
`filter=` and `pushdown=`, and the fallback wins by 1.28x, on CPU as
well. VOJ cannot be unblocked by keys.

Pushing that filter into the driver below the stack fixes VOJ's
augment-key read and is always exact, but it is not always cheaper: it
shrinks the key Distinct while GROWING every Threshold, whose arrangement
holds the symmetric difference of the driver's and the right side's key
sets: 1.15x worse with 100,000-key right sides, 23x better with 1,000-key
ones. Push it down when the right sides hold no
more keys than the filtered driver will ask about, and confirm from the
Threshold-feeding `ArrangeBy` record counts before and after.

**Stack depth and payload width** both favour VOJ, because both inflate the
fallback's per-level intermediates (fallback/VOJ): 1.60x at depth 2, 2.07x at
3, 2.81x at 5, and 2.77x with a 100-character payload on each right.

Two topology traps sit outside that model. A CHAINED stack, where a LEFT JOIN
keys off a column of the previous right side rather than the driver, loses the
delta implementation and costs about 7% more than the fallback even when it
plans cleanly (a fallback/VOJ ratio of 0.93x); restructure it to key off the
driver where the semantics allow (they do not when an intermediate key can be
NULL). And with `enable_eager_delta_joins` on (default off; settable per
cluster only on Cloud, environment-wide elsewhere), the chained shape whose
chained column is the previous right's own join column plans a spurious CROSS
JOIN against the driver: look for `ArrangeBy keys=[[], ...]` with an empty key
list, `[×]` in `WITH (join implementations)`, and an `ArrangeBy[[]]` whose
records all sit on one worker. It costs 23.7x the CPU of the correct plan while
using LESS memory, so a byte census will not find it.

Why the VOJ lowering gets a delta join at all with `enable_eager_delta_joins`
off: `JoinImplementation` first plans a differential join, which arranges
each join input by the one key its order uses, then re-runs and switches
to delta only when every lookup of every delta path is already served by
those arrangements or by an index (the `A` in `[#0]KA` in `WITH (join
implementations)`). Each augmented right is looked up by a single key, so
it is always served; the driver is looked up by every key the rights
use. One shared driver key (a star) is therefore free. A stack whose
rights join the driver on two or more different columns stays
differential unless the driver carries an index on EACH of those columns
(an index on only some of them changes nothing), and a chained stack
stays differential because the previous right is looked up by a second
key. That second key is VOJ's own construction, `case when <augmentation
marker> IS NULL then null else <column> end`, and when the chained column
is the one already equated to the driver, the expression spans two
inputs and cannot be an arrangement key at all. With the eager flag on,
VOJ always ends as a delta join (the driver simply gets one new
arrangement per key), and that unarrangeable key is what becomes the
cross join above; chaining on a different column of the previous right
gets an honest delta join under the flag and a differential one without
it. VOJ's memory case rests on the delta implementation: as a
differential join it keeps its per-right Distinct, Threshold, and
augmentation copies and re-acquires the per-level intermediates, which
is the 0.93x chained result above.

Before building anything, the match rate is one query:

```sql
SELECT round(count(*) FILTER (
         WHERE EXISTS (SELECT 1 FROM <right> r WHERE r.k = dk.k)
       ) * 100.0 / count(*), 1) AS match_pct
FROM (SELECT DISTINCT k FROM <driver> WHERE k IS NOT NULL) dk;
```

Read which case a plan is in from the census: under a VOJ, compare each
right-side `ArrangeBy`'s record count with that relation's own row count (equal
means every driver key matched and the augmentation is free; the excess is the
number of unmatched driver keys). Under the fallback, the tell is one binary
join per level, each holding the running result in an explicit `ArrangeBy` at
output scale and accumulated width, which is exactly what VOJ deletes (a
`JoinStage` line belongs to a multi-input linear join, such as a chained VOJ).

Indexes narrow the gap without closing it. VOJ cannot read a right side from an
index (it always builds its private augmented arrangement), so an index on
every right moved a 2.07x win to 1.52x by helping only the fallback. An index
on the DRIVER is worse than neutral for VOJ whenever a predicate on the driver
would otherwise filter the read: the plan adopts the index for both driver
reads and lifts the filter above the join, so every driver row enters the join
and is discarded after. That costs CPU (about 15% on the insert path) and shows
up nowhere in a byte census.

On the update path VOJ was cheaper in every cleanly planned case measured (8%
to 19% less CPU per single-row driver insert), including the ones where it
costs more memory, because one delta join beats a chain of differential joins
with diamonds between them. The exception is the selective-filter case above,
where the keyed fallback's pushdown wins on CPU as well as on memory.

When VOJ is wrong for one query, restructure that query, never ask for the
flag. `enable_variadic_left_join_lowering` is not session-settable and never
applies to one object. It carries cluster scope, but per-cluster values are
served only by the Cloud flag service, so on self-managed and on the emulator
the only lever is an environment-wide `ALTER SYSTEM SET` as `mz_system`, which
demotes every LEFT JOIN stack in the environment for the sake of one. The
surgical opt-out is a spine cut in the query: nest each LEFT JOIN in its own
derived table with an explicit column list that reorders columns, which
reproduces the flag-off lowering operator for operator (by reordering columns,
so not textually) and is provably exact. The same cut removes the chained-stack
cross join.

## The eager-delta flag

Not a recommended lever. The caveat, the measurement method, and the
controlled alternative are in indexes.md, "Flipping
differential joins to delta".
