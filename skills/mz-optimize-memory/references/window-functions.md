# Window functions

Companion to the mz-optimize-memory skill. Dispatched when a
pipeline uses `OVER (PARTITION BY ...)` window functions
(`ROW_NUMBER`, `LAG`/`LEAD`, `FIRST_VALUE`/`LAST_VALUE`, running
aggregates) and memory or CPU concentrates around them.

## How Materialize executes them (the gadget)

Window functions are not executed like ordinary aggregates. Every
window function compiles to the same three-operator gadget, which
looks like this in `EXPLAIN OPTIMIZED PLAN` (operator names as of v26.39):

```
Map (record_get[0](record_get[1](#1)), record_get[0](#1))
  FlatMap unnest_list(#0{row_number})
    Reduce group_by=[<partition cols>]
      aggregates=[row_number[order_by=...](row(list[row(<packed columns>)], <order col>))]
```

A Reduce collects each partition into a list of packed rows and runs the window
logic over it; a `FlatMap unnest_list` re-emits one row per input row; a `Map`
of `record_get` calls unpacks the results. To find the gadgets in a plan, grep
for `unnest_list` or `record_get`, and identify the function by the aggregate's
name inside the Reduce: `row_number[`, `rank[`, `dense_rank[`, `lag[`, `lead[`,
`first_value[`, `last_value[`, and `window_agg[` (the generic name for windowed
aggregates: a running `sum(...) OVER ...` prints as `window_agg[sum
order_by=...]`).

Fusion is narrower than it looks. Only VALUE window functions (`lag`, `lead`,
`first_value`, `last_value`) fuse with each other, and window AGGREGATES fuse
with each other. The two classes never fuse together, and the ranking functions
(`row_number`, `rank`, `dense_rank`) never fuse at all. Fusion also needs the
same window FRAME and, for window aggregates, the same `DISTINCT`, not just the
same partition and order. What fuses prints as one aggregate named
`fused_value_window_func[` or `fused_window_agg(`, and the second carries no
bracket, so grep the bare names. A fused aggregate is one gadget for all the
functions in it, so their state and per-partition recompute are paid once, and
a rewrite removes the gadget only when every fused function is rewritten. Two
window functions that do NOT fuse become two STACKED gadgets, and the outer one
packs the inner one's output on top of the original columns, so its packed row
is wider than the input. The input-slimming fix below applies unchanged to
every gadget in a stack.

Two cost consequences:

- **State holds the packed rows, twice.** The Reduce retains every partition
  element at the packed width on its input arrangement (logged in
  `mz_arrangement_sizes` as `Arranged FusedReduceUnnestList`, or as `Arranged
  ReduceInaccumulable`, the name basic aggregates also carry, when the unnest
  is not fused) and again on its output arrangement, so budget roughly 2x the
  packed input. When a filter on the window's result is fused into the Reduce
  (`WHERE rn = 1` prints as `mfp_after` under `Reduce::Basic` in the physical
  plan) the output arrangement holds only the surviving rows, and the state is
  one copy plus the survivors. The packed columns are the `row(...)` that lists
  plain column references, under a `list[` for the ranking functions and nested
  inside `row(row(...))` for the value functions and window aggregates. `lag`
  and `lead` carry a second `row(...)` at the same depth holding their argument
  triple, which is why the plain column references are the tell (a
  `fused_window_agg` packs plain references in both siblings; there the packed
  row is the first of the two). Read it verbatim to see what the state carries.
- **Recompute is per partition.** Any change to any row of a partition
  recomputes the window outputs of that entire partition. Hot or huge
  partitions turn into CPU hot spots at update time.

One syntax note that is not a memory matter: a `RANGE` frame other than
the default `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` is
rejected for every window function (`ERROR: RANGE in non-default window
frames not yet supported`), and `GROUPS` frames are rejected outright.
The fix is the equivalent `ROWS` frame, not a rewrite. `ROWS` matches
`RANGE` only when the ORDER BY key is unique within the partition,
because a RANGE frame includes the current row's peers and a ROWS frame
stops at the current row.

## The projection-pushdown blocker

The gadget packs the window's full input scope, not the columns the
query needs: with a ten-column input, `row_number()` over it packs all
ten columns into the list even when the query reads only the partition
key and the window output. The consequence in the census: a bytes/row
outlier on the window's Reduce at roughly the full input row width.

Two facts about the fix:

- **Slimming the SELECT list does NOT help.** A subquery that selects
  only `k, row_number() OVER (...)` from the wide table produces a
  byte-identical plan, still packing every column: the whole FROM
  scope gets packed regardless of the SELECT list.
- **Narrow the window's input RELATION instead.** Wrap the input in an
  explicit projection and apply the window over that:

  ```sql
  SELECT k, row_number() OVER (PARTITION BY k ORDER BY ts) AS rn
  FROM (SELECT k, ts FROM t) slim
  ```

  The packed row then shrinks to exactly the projected columns
  (`list[row(#0{k}, #1{ts})]` in the plan). Project the partition keys, the
  ordering columns, the window function arguments, and any columns that must
  pass through to the output; payload that only the output needs is extracted
  early (the skill's extract-in-place lever, the preferred form) or fetched
  back by a unique key after the window step, which re-arranges the fat
  relation at full width and costs back most of the saving when the slimmed
  pipeline held only a copy or two.

## The arity diagnostic

`EXPLAIN OPTIMIZED PLAN WITH (arity)` makes this a one-glance check: an arity
on the operator feeding the window Reduce far above what the gadget consumes
(partition keys + ordering columns + function arguments + passed-through
columns) means it is hauling dead columns, and the packed `row(...)` list
confirms which.

## Rewrites to incremental forms

Many window uses have idiomatic Materialize equivalents that render as ordinary
incremental operators (hierarchical TopKs and reduces), which are hint-tunable.
The window gadget recomputes an entire partition on every update to it, while a
correctly hinted TopK or reduce recomputes one bucket (in one experiment, a
single-row insert into a 30,000-row partition cost 329 ms of extra CPU as a
window, 142 ms as a TopK at GROUP SIZE 1, and nothing measurable at the hint
the tuning advice suggested). Which form is smaller depends on the family and
on how much the window's output is filtered, so propose every mechanical
rewrite labelled by its memory effect: an improvement is an ordinary
recommendation; a roughly neutral one is proposed for freshness, not memory; a
regression is still proposed, with the measured cost stated, because the window
form may be the one with freshness problems. A rewrite that is not mechanical
is a discussion with the user.

- `FIRST_VALUE`/`LAST_VALUE` to `MIN`/`MAX`, and whole-partition window
  aggregates to a `GROUP BY` joined back, win on both axes (a running or
  cumulative frame is not this rewrite, see below). A hierarchical reduce with
  a small hint keeps one copy of its thinned input plus one row per group,
  where the unfiltered window gadget keeps two full copies of packed rows
  (measured 2.1x to 2.6x smaller for `MIN`, 3.5x to 4x for `SUM`). The
  exception is a very large number of very small groups, where an accumulable
  pays about 160 bytes per group and can lose.
- `ROW_NUMBER() ... WHERE rn <= k` to `DISTINCT ON` or the lateral top-k buys
  freshness and COSTS about 2x memory at a hint at or above the group size, far
  more un-hinted at the 8-level default. The window's filter fuses into its
  Reduce, so the gadget holds one copy of the input plus only the surviving
  rows, while a TopK holds its input plus the retractions of every row it does
  not emit. The exception is a limit that reaches the partition size, where the
  TopK's second arrangement stays empty and it wins outright; partitions barely
  above the limit hold one retraction each and the two forms are close.

Before crediting a rewrite with a memory saving on a WIDE input, apply the
slim-the-input fix from the pushdown section to the window first: most of the
apparent saving is projection pushdown, which the TopK gets for free and the
window gets from an explicit projection (measured on a 16-column input with a
3-column output: window 28.4 MB unslimmed, 11.3 MB slimmed, rewrite 21.7 MB).
Hint the rewritten operator from the bottom: `INPUT GROUP SIZE = 1` renders
zero hierarchy levels, the cheapest rendering and the same whole-partition
recompute the window already had, so it is no freshness regression against the
form it replaces (the 142 ms against 329 ms above); then raise it by
measurement (hint-sizing.md) to buy the update-cost reduction.

ONE HARD EXCEPTION: never rewrite into an INEQUALITY join. A non-window form
that needs a range or inequality join condition is worse than the window
function it replaces (see the quadratic-join shape in the skill); keep the
window function in that case. The common mechanical rewrites:

- `ROW_NUMBER() ... WHERE rn = 1`: rewrite to `DISTINCT ON (k) ...
  ORDER BY k, <rank col>`. Top-k for k > 1: a lateral join of the
  distinct group keys to a correlated `ORDER BY ... LIMIT k`
  subquery. Both forms then get a GROUP SIZE hint
  (hint-sizing.md). The lateral form joins the group keys back with
  `t.k = g.k`, so it silently DROPS rows whose partition key is NULL,
  which the window function keeps as a partition of its own. Require
  the partition key NOT NULL, or handle the NULL partition in a
  separate `UNION ALL` branch. The `DISTINCT ON` form for k = 1 has no
  such gap.
- `FIRST_VALUE`/`LAST_VALUE`: when the windowed expression IS the ordering
  column and that column is NOT NULL, rewrite to a `MIN`/`MAX` group aggregate
  joined back on the partition key. Two traps: `LAST_VALUE` under the DEFAULT
  frame is the current row's value, not the partition maximum, so the rewrite
  holds only when the frame is spelled `ROWS BETWEEN UNBOUNDED PRECEDING AND
  UNBOUNDED FOLLOWING`, and on a nullable ordering column the two forms that
  yield the maximum (`first_value` under DESC, `last_value` under ASC) return
  the NULL that sorts at that end while `MAX` skips NULLs; the two that yield
  the minimum (`first_value` under ASC, `last_value` under DESC) agree with
  `MIN`. When the payload of the extreme row is needed, use the `DISTINCT ON`
  pick instead.
- `LAG`/`LEAD`: when the ordering column advances in a REGULAR pattern (a fixed
  interval or step), rewrite to a self equi-join on `t1.k = t2.k AND t1.ts =
  t2.ts + <step>` (inner join drops the boundary row, LEFT JOIN keeps it with a
  null, so pick the one matching the window semantics). That formula is the
  `LAG` direction, `LEAD` flips the sign. The equi-join form carries two
  obligations the window function does not: the partition key must be NOT NULL
  (an equi-join drops the NULL partition that `LAG` keeps, silently under the
  LEFT variant), and `(partition key, ordering column)` must be unique (a
  duplicate pair fans the self-join out). The LEFT variant additionally pays a
  full equi outer-join diamond, measured at 3x the INNER form, so take INNER
  wherever the boundary row is expendable. When the spacing is irregular there
  is no window-free equivalent: keep the `LAG`/`LEAD` and slim its input per
  the pushdown section. Never fall back to an inequality join for adjacency.
- Running or cumulative aggregates over an unbounded frame have no
  clean incremental substitute; treat them as a design conversation
  with the user rather than a mechanical rewrite.

All such rewrites carry the standard exactness obligation: two-way
EXCEPT ALL against the original, with tie and boundary seeds (window
functions with underspecified ORDER BY ties are a classic source of
legitimate output differences; pin the tie-break before comparing).

## When to leave them alone

Beyond the inequality-join exception above, keep the window function when the
rewrite is nontrivial while the partitions are small, bounded, and low-churn:
there the whole-partition recompute is cheap, the state is small, and a risky
rewrite buys little. In every kept case, still apply the slim-the-input fix
from the pushdown section; it is mechanical and composes with keeping the
window.