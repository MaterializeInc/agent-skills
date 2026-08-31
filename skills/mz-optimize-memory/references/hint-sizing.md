# GROUP SIZE hint sizing

Companion to the mz-optimize-memory skill. Dispatched when
`EXPLAIN ANALYZE HINTS` flags operators with savings, or when un-hinted
min/max aggregates show up in plans. This is usually the cheapest lever
on a cluster: no logic change, bounded risk, measured savings.

## Mechanism

Hierarchical `TopK` and `MIN`/`MAX` aggregates render as base-16 bucketed
hierarchy levels. The level count comes from a query hint on the source clause:

- `OPTIONS (AGGREGATE INPUT GROUP SIZE = N)` on a `GROUP BY` with
  min/max aggregates, placed AFTER the `GROUP BY` (and `HAVING`):
  `... FROM t GROUP BY k OPTIONS (AGGREGATE INPUT GROUP SIZE = N)`;
  before the `GROUP BY` it is a parse error,
- `OPTIONS (DISTINCT ON INPUT GROUP SIZE = N)` on a `DISTINCT ON`, after its
  `WHERE` (and any `GROUP BY` or `HAVING`) and before `ORDER BY`; placed right
  after `FROM` with a `WHERE` following, or after `ORDER BY`, it is a parse
  error,
- `OPTIONS (LIMIT INPUT GROUP SIZE = N)` on a per-group `LIMIT k`
  (in the lateral-subquery top-k form, the OPTIONS clause goes INSIDE
  the lateral subquery, between its WHERE and ORDER BY).

Every hint from 0 through 16 renders the same thing, zero hierarchy levels, a
single pass over the whole group; the brackets are 0..16 for zero levels,
17..256 for one, 257..4096 for two, and so on. That also bounds the advice:
`hint = pow(16, levels - to_cut) - 1` (`to_cut` = the levels the advice would
remove; the hierarchy's first level is never a candidate, so `to_cut` stays
below `levels`) can never propose less than 15, which IS the zero-level
rendering, and a hierarchy already down to one level is never flagged.

Over-sized hints allocate hierarchy levels that retain state without earning
it. An aggregate with NO hint defaults to an 8-level hierarchy, which budgets
for four billion rows per group, and that is why the single biggest hint win is
usually an un-hinted min/max rather than a mis-tuned one. Eight is the default,
not a ceiling: a hint above 16^8 (about 4.3 billion) buys a ninth level.
Recognize the un-hinted case by `levels = 8` in HINTS, or by the absence of
`exp_group_size` on the `Reduce` or `TopK` node in `EXPLAIN OPTIMIZED PLAN`.
For min/max only, the physical plan also spells the levels out as a bucket
list: in the operator label in the arrow text and in HINTS (`buckets: 268435456
16777216 ... 16`), on its own `buckets=` line in the verbose physical plan; the
list has one entry per level below the top, so `levels` in HINTS reads one more
than the list is long. A `Non-monotonic TopK` never prints buckets, and hinted
and un-hinted top-k physical plans are identical.

## Method

1. Measure. Start with the cluster-wide overview (workflow step 2:
   `mz_introspection.mz_expected_group_size_advice`), read with the session
   targeted at the cluster and at one replica on a multi-replica cluster. Then
   run `EXPLAIN ANALYZE HINTS FOR MATERIALIZED VIEW <mv>` (also `FOR INDEX
   <idx>`) on the objects whose savings are substantial; it gives the same
   measurements per object, one row per LIR node in descending LIR-id order,
   not plan order (the skill's mapping technique handles that). The dataflow
   must be hydrated: a premature read returns NULL measurements from HINTS, and
   from the advice view either no row or provisional numbers (in one
   observation two levels fewer and a hint one 16x step smaller than the
   hydrated reading), so gate it on `mz_hydration_statuses` like every other
   measurement. Per flagged operator you get the current `levels`, `to_cut`,
   the measured suggested `hint`, and the reclaimable `savings`. Always use the
   measured value, never a guess from the group's grain (the coherence check at
   the end of this file): data skew makes some tightly-windowed aggregates
   legitimately need a large hint, and the measurement already accounts for it.
2. Map every flagged operator to its exact source clause with the skill's
   mapping technique ("Mapping measurements back to SQL"). Two hint-specific
   landmarks on top of it: for sibling `DISTINCT ON` clauses sharing a group
   key, the `ORDER BY` column, read from `EXPLAIN PHYSICAL PLAN` (HINTS does
   not show it); thinning renumbers the order column, so twins can print the
   same `order_by=[#1 ...]`, in which case use the marker. And read current
   hint values in `EXPLAIN OPTIMIZED PLAN`: on a min/max operator the physical
   plan's bucket list narrows the value only to its 16^n bracket, and a top-k
   operator's physical plan does not carry the hint at all.
3. Reconcile counts. HINTS flagged N operators, so you must finish with N
   mapped clauses. N is the count of rows carrying a non-null `levels`: HINTS
   prints the whole plan tree, one row per LIR node, with NULLs on every
   non-hierarchical row. Fewer mapped clauses means you missed a sibling
   clause; walk the neighbourhood until the count matches.
4. Probe the population. The measured suggestion reflects today's data.
   Check the group-size population (max group size and its distribution over
   the group key) to learn whether it can grow: a population bounded by the
   schema or the window justifies no headroom beyond step 5's one level, a
   legitimately growing one justifies more, and an old hint that such a
   population has outrun must be raised, not trusted. Nothing in the instrument
   will tell you so: the advice is one-directional, since the view only ever
   proposes CUTTING levels, so an undersized hint is never flagged.
5. Set the new value to the measured suggestion plus one level (16x) of
   headroom. The headroom is not waste: it is insurance against update-cost
   spikes and key skew when a group outgrows the hint. A memory-only A/B will
   always tell you to shave it off; do not, unless the user explicitly accepts
   the update-cost risk. What a level costs (the skill's cost model): close to
   nothing when it does real reduction, about one full copy of the retained
   input when it does not (measured on 500,000 narrow rows, scaling with row
   width: +0.3 MB per level on 5,000-row groups, +9 to +12 MB per level on
   2-row groups); a min/max hierarchy pays about twice that per level, because
   each bucket level retains a negated copy as well as its input. So take the
   headroom by default where the suggestion sits at or below the group's real
   grain, and measure it first where the population is small and bounded. Leave
   correctly-sized hints alone: not flagged is no reason to retune one
   downward, and the one reason to touch an unflagged hint is step 4's outrun
   population, which asks for a raise.
6. Rebuild to adopt. Hints are applied at plan time, so edit the view
   definitions and then drop and recreate the materialized views and indexes
   whose dataflows inline the edited view (indexes first, then MVs; see the
   skill's "Making changes" section). Their own downstream consumers read
   persisted or arranged output and keep their plans.
7. Verify. Re-run HINTS after the rebuild. The residual savings should
   be exactly your deliberate headroom level (`to_cut = 1` on the
   retuned operators). Anything more means a mapping missed its
   clause.

## Grain heuristic (coherence check only)

Suggested sizes track the number of DISTINCT (group key, aggregate
argument) tuples per group, which is what the hierarchy's input holds
(the skill's cost model, Reduce), not the number of rows.
Per-key single-row picks (`DISTINCT ON (pk) ... LIMIT 1`) measure tiny
(about 15), per-entity picks over long histories measure large (about
4095), and the suggestion lands on a 16^n bracket, so it can sit a
level or two off the grain you expect. Use this only to double-check
your clause mapping. A measured value that does not match the grain is
a prompt to re-verify which clause the operator maps to, not evidence
against the measurement.
