# Indexes, boundaries, and arrangement mining

Companion to the mz-optimize-memory skill. Dispatched for
cross-dataflow duplication, index key correctness, flipping differential joins
to delta, composite re-keys and boundary mining, late materialization,
intra-dataflow twins, computed-view indexes, and shared indexes for temporal
filters. Also home of the adoption-verification rules (incl. the index-to-delta
hot-key hazard) and the data-free plan rig.

## Ground rule: count arrangements in the physical plan

A ground rule for all arrangement counting: the optimized (MIR) plan
is not the authority on which arrangements exist, in either
direction. Lowering to the physical plan both ELIDES MIR ArrangeBys
(an operator whose output is already arranged by the needed key, such
as a Reduce feeding a join on its group key, needs no new
arrangement) and INSERTS ArrangeBys that MIR never showed. When the
question is which arrangements a dataflow actually holds, read the
physical (LIR) plan (`EXPLAIN PHYSICAL PLAN`) or the live
introspection sizes, never the MIR text.

## When an index helps at all

Within one dataflow the optimizer already shares each distinct (collection,
key, projection) arrangement, so a single-copy private arrangement cannot be
shrunk by deduplication: an index has nothing to collapse. Other levers can
still shrink it (slimming its columns, retuning its hint, restructuring the
query that needs it; the skill's lever table dispatches on the signatures), and
when no signature applies, large is not by itself a problem: leave-alone is the
verdict (the skill's ground rules). An index pays in two ways. By sharing
across dataflows:

1. The same (collection, key) arrangement is built in several
   dataflows: the index builds it once and every dataflow imports it
   (N copies become 1).
2. The index sits on an expensive computed view consumed by several
   dataflows: it dedups the whole computation (memory, CPU, and
   hydration), which pays even when consumers read it unkeyed, because
   the alternative is recomputing, not a narrow copy. Do not reject a
   computed-view index on a full-scan footer alone.

Or by changing the plan inside one dataflow, covered in later sections:
pre-arranging the inputs of a multi-input join lets the planner drop the
differential intermediates (the delta flip), and an index on a
union-width view collapses an intra-dataflow twin pair into one import
(a boundary move). Either way the index's own arrangement is the price
and the arrangements it removes are the win, so the same width
accounting applies.

What an index can replace: join-input arrangements (a Threshold's whole-row
input is always a Union, so no index reaches it). It never replaces the input
arrangement a Reduce or TopK builds for itself: those operators always arrange
their own input in their own layout (a Reduce holds group key plus the
aggregate arguments, a bucketed min/max hierarchy and every TopK level key by
(hash, group key)), so no existing arrangement can be consumed, shared, or
replaced, whatever the aggregate class. An index chosen to "help a GROUP BY" or
a DISTINCT ON therefore saves nothing on that operator's state; those are hint
and rewrite territory (what that state must hold, and why, is in the skill's
cost model).

Detect duplication by measurement, not by reading SQL: the mining procedure
below. `mz_introspection.mz_arrangement_sharing` is the live refcount of an
existing arrangement: its export plus the consumers that read it as an
arrangement, so full-scan readers do not count.

## The wide-index penalty and the width model

An index holds the full-width row of its view. The per-dataflow private
arrangements it replaces are narrow, demand-projected copies. The real
win is:

    sum(narrow private copies) - (one full-width index)

not `sum(copies)`. Compute bytes/row (total memory ÷ total records) on both
sides before creating anything, for your own candidates as much as for
proposals you adjudicate; a wide base with a few narrow consumers makes the
index a wash or a net loss, with adoption looking perfectly clean in the plan.
The fix for that case is a slim projection view carrying exactly the
column-union the consumers need, an index on that view, and repointed consumers
(an index on a view serves only references to that view).

Width estimates sharpen with the key-amortization model:

    bytes/row ~= sum(value column widths)
               + sum(key column widths) / rows-per-distinct-key
               + per-row overhead

Keys are stored once per distinct key, so a coarse key amortizes to
nearly nothing while a near-unique key pays full freight. Fit the
model against a few measured arrangements of the same relation before
trusting it for predictions.

## Width math gates; only measurement settles

Static width math is the gate that decides whether an experiment is
worth running. It does not settle the verdict, in either direction:

- Shared arrangements can restructure multi-way join plans. With
  inputs pre-arranged, differential cascades flip to delta plans and
  their intermediate stage arrangements vanish, a saving the
  join-input width math cannot see. A boundary index that loses on
  width arithmetic can win on the measured build.
- The same fat index adopted verbatim can be catastrophic: an MV
  rebuilt against a full-width index can grow its dataflow more than
  tenfold, the plan restructured against the wide arrangement in the
  wrong direction.

So: gate with the width math, pre-check adoption free on the rig
(below), settle with a measured build.

## Index key correctness

- The key must exactly match the join key as a set of columns (and, for the
  join order's start input, in the right order: composite key ORDER, below). A
  composite join key (several columns equated in one join) is ONE key and gets
  ONE index on all of its columns: an index that is too narrow (some of those
  columns), over-wide (extra columns), or simply wrong is read only as a full
  scan, and the consumer builds its private arrangement anyway, so for that
  consumer the index is pure added memory, not neutral.
- Read the join key from the plan's join equivalences, not from domain
  intuition. The "natural" entity id is frequently not the join key.
- A literal equality on an input (`t.b = 'x'`, in the ON or the WHERE) is a
  filter, never part of the join key, and it is what makes the wrong composite
  index easy to propose. The join key of `s JOIN t ON t.a = s.a AND t.b = 'x'`
  is `a` alone: an index on `t(a, b)` (in either order) serves neither the join
  nor the filter, is read as a full scan, and the plan says so (`Notice: Index
  ... is too wide to use for literal equalities`). Two indexes can serve that
  input, and the planner uses at most one of them: an index on the join key,
  `t(a)`, is adopted for the join and the filter is lifted above it, so the
  join runs over all of `t`; an index on exactly the literal columns, `t(b)`,
  serves the filter as a `(lookup)` (`lookup value=(...)` in the plan, `IN`
  lists included; never an inequality, never a prefix of the index) and the
  surviving rows are then arranged privately by `a`; with both present only the
  lookup is used. For memory, count the survivors: whichever index the consumer
  does not adopt, its private arrangement of that input holds only the filter's
  survivors, because the filter sits below the Arrange. With a selective
  literal filter the cheapest form is therefore often no index on that input at
  all, and an index on it pays only through its other consumers. Serving both
  from one `(join key, literal column)` index is a known gap in the planner.
- A relation joined on DIFFERENT keys at different join sites needs one
  index per key. The key holding the memory may not be the key you were
  asked to index; find which key the measured arrangement uses, then
  index that.
- Composite key ORDER: arrangement keys match as exact ordered lists,
  so an index is adopted only when its columns are declared in the order
  the planner asks for; the order written in the ON clause never
  matters. Only the join's START input (leftmost in the `implementation`
  line) can lose: every later input imposes its own arrangement's order,
  and a delta join adopts every input's index whatever its order. The
  start's required order is the second input's key order: that input's
  index order if it has one, else its column order (a pass-through
  view's SELECT order is normalized away by projection pushdown, a GROUP
  BY list's is not). So a lone `(b, a)` index is full-scanned only when
  its relation starts the order and the other side reads `(a, b)`, and
  two indexes in disagreeing orders lose the start's; the loser is read
  as a full scan and re-arranged privately. Which input starts depends
  on filters and unique keys, so re-check after any query change. Fix by
  declaring the losing arrangement in the required order (its index
  definition or GROUP BY list) or by adding an index in that order.
- Filters on a consumer do not block adoption by themselves: the planner lifts
  them above the join or drops null-rejecting ones. The exception is an input
  that also needs a second key no index provides: the planner keeps the filter
  below the arrangement it has to build anyway and full-scans the index the
  input does have (the delta-flip section). Do not create per-filter view
  variants.
- Verify adoption in the `Used Indexes` footer: `(differential join)` or
  `(delta join lookup)` is clean; `(lookup)` is a literal-equality lookup on
  the index key (a filter, not a join); `(*** full scan ***)` is a key mismatch
  when the consumer wanted a keyed read, and the normal footer when it did not
  (a computed-view index read unkeyed, a VOJ's right sides); `(delta join 1st
  input (full scan))` is a normal delta snapshot path, not a mismatch; `(***
  full scan ***, index export)` is what an index built over an already-indexed
  view prints. The footer names only the index a read came from: a relation
  with several non-matching indexes shows one of them as the full scan and the
  others nowhere, so absence from the footer is no evidence that an index is
  unused.

## Flipping differential joins to delta

When a `type=differential` join's `Differential Join` operator lines carry big
memory (that memory IS the eliminable intermediate; the skill's cost model
explains the reading), the lever is to supply the input arrangements that let
the planner choose a delta join instead, which maintains no intermediates at
all (a two-input join is always differential whatever indexes exist, so
this lever needs three or more inputs):

1. Read the join keys from the plan (every stage's lookup keys); the indexes to
   add are the probe keys the delta paths need that no arrangement provides yet
   (step 2). A relation probed on two different keys needs two of them, the
   common case for the central fact relation of a multi-way join.
2. Under the default configuration the planner picks delta when the
   delta plan needs NO NEW arrangements beyond the ones the
   differential plan would build anyway. What you must supply as
   indexes is therefore only the EXTRA probe keys the delta paths
   need, not every key of every input: a star join where every input
   is probed on the same key is already delta with no indexes at all.
   The flip is still all-or-nothing per join, so one missing probe key
   leaves the differential cascade in place, and it can cost more than
   the flip: when the input missing a key also carries a filter or a
   projection (the `IS NOT NULL` guards on nullable join columns
   count), the planner keeps that below the input's arrangement, since
   it has to build one anyway, and then even the index that input does
   have is read as a full scan, so the cascade also builds a private
   arrangement where a lookup was available.
   Supplying the missing key lifts the filter and restores both.
3. Rebuild the consumers (plans are fixed at CREATE time) and verify:
   `EXPLAIN OPTIMIZED PLAN WITH (join implementations)` shows `type=delta` with
   per-path stage keys; the `Used Indexes` footer shows
   `(delta join lookup)` per input, and `(delta join 1st input (full
   scan))` on one input is the normal snapshot path, not a problem.
4. Net the accounting like any index package: the indexes you add are
   real arrangements (full-width, the wide-index penalty applies) and
   they pay off across ALL consumers of those relations, against the
   intermediates they eliminate. Width math gates, a measured build
   settles.
5. Check the hazards before shipping: a delta path that streams
   through a high-fan-out lookup funnels that key's traffic through
   one worker (see the verification section below), and the closure
   audit applies to every index you add (see the skill's landmines).

Do NOT reach for the `enable_eager_delta_joins` flag as a shortcut. It lets the
planner flip differential joins to delta joins whenever that needs no more new
arrangements than the differential would build, cluster-wide and by arrangement
count alone. The intermediate-stage arrangements it eliminates are real, but on
a well-indexed cluster it can be net negative (measured so on one):
differential joins ride the wide shared indexes for free, while each delta path
needs a per-key projected arrangement that no existing index provides, so the
flag re-materializes large base relations under path keys. The planner compares
arrangement counts, never bytes, so a count-neutral flip can still cost memory.
Deliberate indexes on exactly those keys, plus a measured build, are the
controlled form of the same lever. It also has a known bad plan: on a chained
LEFT JOIN stack (each join keying off the previous right side) the eager
planner can add a delta path that cross-joins the driver, which uses less
memory than the correct plan and over twenty times the CPU; outer-joins.md
lists the tells.

## Arrangement mining and boundary reorganization

The existing view decomposition may have been written for readability
rather than for arrangement reuse: plain views are inlined per consumer
(the skill's cost model), so reuse happens only where an INDEXED view
sits at exactly the
(collection, key) a consumer needs. Treat the set of indexed view
boundaries as a design variable, and mine rather than guess:

1. Collect every sized arrangement across all dataflows on the
   cluster (`mz_introspection.mz_arrangement_sizes` joined to
   `mz_dataflow_operator_dataflows`, or per-MV `EXPLAIN ANALYZE
   MEMORY` dumps).
2. Cluster them by record count, within a few percent (the skill's
   cross-dataflow duplication probe, which explains the tolerance and the
   fingerprint).
3. Resolve each big cluster in the plans: which collection, which key,
   which columns are carried. The typical find is a recurring
   composite re-key of a base relation that no existing single-column
   index serves, so every consumer reads the shared index and then
   privately re-arranges the relation by the composite.
4. Fix: a new narrow view at exactly that (collection, composite key,
   column-union) point, an index on it, and repointed join sites. One
   view per key; column-union per view (the wide-index penalty applies
   inside boundaries too).
5. Composition order: build the shared composite boundary FIRST and
   repoint consumers through it before judging per-view index
   candidates. Many per-view candidates that look like independent
   wins become cheap adopters, or entirely unnecessary, once the
   boundary exists; judging them pre-boundary double-counts the same
   savings.

A named special case the optimization docs call LATE MATERIALIZATION
("Further Optimize with Late Materialization"): when joins
follow primary/foreign-key structure, create narrow two-column views
(primary key, foreign key) with indexes on both columns, and rewrite
the join to route through them, joining the wide relations only once,
by primary key, where their payload is needed. The wide collection is
then arranged once (by its key) instead of once per join site, and the
narrow key-pair arrangements change less often than payload columns
do. This is the same boundary vocabulary as above with the key-pair
view as the boundary; size it the same way (narrow arrangements added
vs wide copies removed) and note it composes with delta joins (all
inputs pre-arranged).

Intra-dataflow twins count too (the skill's twin census): per-consumer
projection divergence made them different (collection, key, projection)
triples, so the sharing rule at the top of this file did not fire. The fix is
the same
boundary move applied inside the dataflow: one view at the union width, indexed
by the shared key. Caveat: the boundary freezes projection pushdown across it,
so a consumer that needed a tiny slice now reads the union width; check per
consumer before lifting.

## Shared indexes for temporal filters

A view with an `mz_now()` window is a plain `Filter` in the plan, with no
Union/Negate/Threshold shape to look for: the temporal Map/Filter/Project (MFP)
emits each live row at its lower bound and its negation at its upper bound.
Every arrangement of that view built FROM THE SOURCE therefore shows roughly
two records per logical row in `mz_arrangement_sizes` (the live row in its
trace, the pending retraction in its batcher or, under temporal bucketing, for
far-future ones in the `Temporal delay` line just ahead of it, the same total
either way), the shared one as much as the private ones. An arrangement built
from an existing arrangement of the same view instead reads the consolidated
as-of-now collection and holds one record per row, because the pending
retractions stay in the arrangement that first materialized them. The first
thing the shared index buys is the N-copies-to-1 dedup: the index holds the
same two records per logical row as each private copy it replaces, at full
width, so net it against the narrow copies it removes like any other index.
When a temporally-filtered view feeds several consumers, evaluate the shared
index even when plain width math looks marginal, and settle it with a measured
build.

The shared index dedups more than the consumers' arrangements. Within one
dataflow a future-dated retraction is parked exactly once, by the first
time-batching operator after the filter (the skill's cost model), and an MV's
persist sink is that operator only when the MV carries the `mz_now()` predicate
itself with nothing arranging in between. Repointing such an MV at the shared
index takes the predicate out of its plan and empties its `mv_sink(..)::write`
line; consumers that already arranged the filtered view were never parking in
their sinks. Count parked copies by the plans that still show the `mz_now()`
Filter, not by the MVs that depend on the view. The copies are moved, not
deleted: the surviving one sits in the index's `Temporal delay` line under
temporal bucketing, or in its merge batcher without it (figures measured on a
two-column row: about 28 to 37 B/record in the delay line, 64 B/record in the
batcher, against about 27 B/record in a sink buffer), so the lever pays off by
count, and for filter-and-project consumers alone it breaks even at about two
of them.

## Verifying an index or boundary change

- New shared indexes can flip a join onto a hot key (the skill's landmines).
  After adding indexes, check `EXPLAIN OPTIMIZED PLAN WITH (join
  implementations)` on the big consumers and inspect delta paths whose stage
  keys can fan out; confirm with `EXPLAIN ANALYZE CPU WITH SKEW FOR
  MATERIALIZED VIEW <mv>` post-rebuild (the skill's worker-skew probe). Also
  compare every rebuilt dataflow's hydration time with its pre-change one
  (`mz_internal.mz_compute_hydration_times`, `time_ns` per object and replica,
  NULL while still hydrating): a hydration that got much longer after an index
  package is this hazard until proven otherwise. Mitigation: carve the hot
  stage into an indexed view keyed on the downstream probe key (computing the
  hot join once, redistributed by the index key), or withhold the enabling
  index from that cluster.
- Consumers' plans must show the index read with an adopting footer annotation
  (`differential join`, `delta join lookup`, `delta join 1st input (full
  scan)`, or `lookup`), and a bare `*** full scan ***` only where the consumer
  wanted no keyed read (a computed-view index, a VOJ right side; the annotation
  list under "Index key correctness").
- Count private ArrangeBy BLOCKS per dataflow and explain every change in the
  count: the blocks the change was meant to remove must be gone, and a block
  that appears needs a reason (a delta path's extra probe key, a narrow copy
  behind a new boundary, the survivors of a lookup) and gets sized, because the
  verdict is measured bytes, not the count. Raw `arrangements[...]` entry-line
  counts are blind to the improvement: they stay flat or go up on a strictly
  improving change, because adopted index reads print their read specs as extra
  lines. (Those entry lines appear only in the verbose text of `EXPLAIN
  PHYSICAL PLAN`; `AS TEXT` switches to the arrow format, which has none.)
  Absence of an Arrange is what reuse looks like (the skill's operator table: a
  node lists only the arrangements it builds, and one whose keys all exist is
  elided). Releases before mid-2025 listed reused keys on the node as well, so
  entry counts from old plans double-count.
- Untouched dataflows must keep the same plan and the same set of
  arrangements. Their byte totals drift with batching, so compare
  structure exactly and sizes only within the duplication probe's
  tolerance.

## The data-free plan rig

Adoption, key-order, and plan-restructuring questions can be settled
for free, before paying for any hydration on the experiment cluster.
Plans depend on the catalog, not on data, with two exceptions: the
optimizer's unique-key knowledge, and cardinality-based join ordering,
which is off by default (`enable_cardinality_estimates`) and would make
plans data-dependent in an environment that turned it on. Reproduce the
unique-key knowledge with keyed materialized views:

1. Mock each base relation as a raw table, declaring NOT NULL columns
   normally: `CREATE TABLE t_raw (pk int NOT NULL, ...)`.
2. Create a materialized view named exactly like the real relation:
   `CREATE MATERIALIZED VIEW t AS SELECT DISTINCT ON (pk) ... FROM
   t_raw ORDER BY pk`. The MV boundary exports the DISTINCT ON-derived
   unique key to every consumer through the catalog, while the TopK
   implementing it stays inside the MV's own dataflow, invisible to
   consumer plans.
3. Replay the real views, MVs, and candidate indexes verbatim on top,
   and diff `EXPLAIN OPTIMIZED PLAN` structurally against the real
   environment's plans: join types, ArrangeBy keys, footer
   annotations. `EXPLAIN OPTIMIZED PLAN` and `EXPLAIN PHYSICAL PLAN`
   reject a plain view (`RAW PLAN FOR VIEW` and `LOCALLY OPTIMIZED
   PLAN FOR VIEW` accept one, the latter the more useful of the two
   since it shows the MIR after local transforms), so explain the
   materialized view, the index, or a `SELECT` that reads the view.
4. Check rig fidelity with `EXPLAIN OPTIMIZED PLAN WITH (keys)` (also `LOCALLY
   OPTIMIZED PLAN ... FOR VIEW`; a physical or raw plan silently prints no key
   annotations): the read of each keyed mock must show its unique key (`keys:
   "([0])"`), and reads of the raw mocks show `keys: "()"`. Explain a query the
   fast path declines, such as a join, because `WITH (keys) FOR SELECT * FROM
   <relation>` can take the fast path and then prints no key annotations at
   all. Declare keys faithfully; a missing or wrong key changes join lowerings
   (for example, a LEFT JOIN's Union/Negate diamond, outer-joins.md, collapses
   only when the right side is known unique on the join key).

Where to run it: a local Materialize emulator (`docker run
materialize/materialized`), or as empty objects on the already-approved
experiment cluster. Ask the user before starting a local container; it is their
machine. The emulator runs with RBAC checks off by default (as do self-managed
instances not created with `enableRbac: true`), so rehearsing the experiment
role's privileges on it needs `ALTER SYSTEM SET enable_rbac_checks = true`
first, issued as `mz_system` on the internal SQL port. Limits: the rig proves
adoption and plan shape, never savings in bytes, and this trick declares one
unique key per relation, so a plan that depends on a second declared key cannot
be reproduced with it.
