# Subqueries: when decorrelation costs memory, and the rewrites

Companion to the mz-optimize-memory skill. Dispatched when a plan
shows a `CrossJoin`, or a `Distinct` and `ArrangeBy` keyed on the outer
relation's own columns, feeding a join back to that relation: the signature of
a subquery that the decorrelation joined back on the outer key. The skill's
"Query shapes to recognize" section carries the short dispatch signature. This
file holds the full signature list, the mechanism, the rewrites with their
exactness obligations, the cases the optimizer already handles, and the cases
no rewrite fixes.

## Why a subquery costs memory

Lowering decorrelates a subquery into a join. Logically it is evaluated once
per distinct value of the outer columns it references, but the plan computes it
once, as a dataflow over a `Distinct` of those values joined back on them, so
there is no re-execution per outer row. The cost is that join's arrangements
plus what the subquery's own operators hold, and when the outer keys are joined
in below an aggregate or a `LIMIT` those operators hold one group per distinct
outer value over the whole subquery input (the aggregate and `LIMIT` cases
under "Already handled well"). A subquery made only of Map, Filter, Project,
and table-function calls, and reading no relation, is inlined (a subquery
inside a `CASE` never is). Anything else, a subquery that reads a relation or
carries an aggregate, `DISTINCT`, `LIMIT`, a join, or a set operation, takes
the general path: `Distinct` over the correlation key, the subquery, join back
on that key. When nothing ties the subquery to the outer row (an uncorrelated
scalar subquery; `IN` and `EXISTS` supply an equality of their own) the
correlation key is empty and the join back is a `CrossJoin`.

The memory is every arrangement keyed by the correlation key, at whatever width
that key has: the join-back pair, one per side, the `Distinct` over the key
(input and output), and every arrangement the subquery itself builds. A
subquery correlated on a `jsonb` document arranges the document as the key. A
subquery in an outer join's `ON` costs even when it is uncorrelated: it makes
the `ON` a Theta predicate, which forces the general outer-join lowering, and
that lowering keys its anti-side on every preserving column. One that also
references the preserving side pays both, the general lowering and the
decorrelation, and rewrite 3 cannot lift it.

## SQL triage, before you EXPLAIN

`NOT IN (SELECT ...)` or `<> ALL` with a nullable side. `IN` or `ANY` on a
nullable comparison anywhere other than a filter conjunct (a top-level `WHERE`,
an inner join's `ON`, and `HAVING` are conjunct positions; a SELECT list,
`ORDER BY`, `CASE`, `COALESCE`, an `OR` branch, and an outer join's `ON` are
not; `EXISTS` outside a conjunct costs only a true/false diamond at
correlation-key scale, not this). `IN` over a subquery that aggregates or uses
`LIMIT`, even as a top-level `WHERE` conjunct. Any subquery inside a LEFT,
RIGHT, or FULL JOIN's `ON`. `= ANY(<array or list column>)` in any position, an
inner join's `ON` included. A scalar subquery, `ARRAY(SELECT ...)`, or `LATERAL
(... LIMIT 1)` correlated only on the current row. The same subquery text
repeated in two UNION branches. Nested `IN (SELECT ... WHERE ... IN (SELECT
...))`.

## Plan signatures (`EXPLAIN OPTIMIZED PLAN WITH (arity)`)

1. `CrossJoin` with a `Distinct project=[...]` over the outer relation on one
   side: the outer keys seeding a correlated subquery whose own `FROM` is
   uncorrelated (`NOT IN`, `IN` outside a filter conjunct). A `CrossJoin`
   against the outer relation itself, with no `Distinct`, is a fully
   uncorrelated subquery when the SQL has one; a written cross join, a join
   without an equality, and `IS NOT DISTINCT FROM` on nullable columns print
   the same (the skill's query shapes).
2. `Reduce group_by=[...] aggregates=[any(<pred>)]` over a `CrossJoin`, wrapped
   in `Union`/`Negate`/`Map (false)` and `Map (null)` diamonds: an `IN` or
   `ANY` that is not a filter conjunct, on a nullable comparison (either side).
3. `Distinct project=[#0..=#N]` over every column of a wide relation, an
   `ArrangeBy keys=[[#0..=#N]]`, and a join equating all N columns: an outer
   join whose `ON` mentions a subquery (any other Theta predicate in the `ON`
   produces the same general lowering, outer-joins.md). Six extra full copies
   of the relation, keyed by the entire row: two `ArrangeBy` nodes plus two
   whole-row `Distinct`s (one over the whole relation, one over its matched
   rows), each an input and an output arrangement (the general shape in
   outer-joins.md).
4. A `Distinct` or `ArrangeBy` whose key is a `jsonb`, `list`, `array`, or long
   `text` column: a per-row subquery, or a `LATERAL (... LIMIT 1)`, correlated
   on a payload column, when the SQL has one; a `DISTINCT`, `GROUP BY`, or join
   on the payload column keys an arrangement on it the same way with no
   subquery involved. The payload is the key. A payload-keyed arrangement
   stores each distinct payload once, so repeated documents collapse and
   per-row documents, the usual case, cost one copy per row.
5. A `Union`/`Negate` over a `Distinct` over a `Filter` reading
   `... IS NULL OR ... IS NULL OR ... =` over a `CrossJoin`: `NOT IN`
   or `<> ALL` on nullable columns. The `Filter` prints its columns
   with their names (`(#0{a}) IS NULL ...`), so match the shape rather
   than a literal string.
6. `FlatMap unnest_list | unnest_array` fed by a `Distinct` of the outer
   relation and joined back: `= ANY(<array or list column>)`.
7. A join whose implementation shows every input as `[×]`: a correlated join
   whose `ON` mixes outer columns with both inner relations (a written cross
   join or an equality-free join prints the same without any correlation). No
   decorrelation rewrite fixes this one (see "Unfixable by rewrite" below).

## Already handled well, do not rewrite

These look like signatures in the SQL but already plan as the rewrite would;
check the plan before touching any of them.

- An uncorrelated `x IN (SELECT y FROM t)` over a plain `SELECT`, as a filter
  conjunct (a top-level `WHERE`, an inner join's `ON`, `HAVING`): planned as a
  semijoin (a `Join` against a `Distinct` of the subquery), identical to the
  hand-written `JOIN (SELECT DISTINCT ...)`. Not so when the subquery
  aggregates or uses `LIMIT`: the outer keys then seed it, as an equi-join with
  the outer's distinct keys below the aggregate when the compared column is the
  subquery's group key (the correlated-aggregate lowering, so rewrite 4 trades
  under rewrite 8's condition), and otherwise as a `CrossJoin` of the outer's
  distinct values with the whole subquery input under a `Reduce` or `TopK`
  grouped by the outer value, so the aggregate or top-k runs once per distinct
  outer value over all of it and rewrite 4 is the fix outright.
- `EXISTS` and `NOT EXISTS` with an equality correlation, in any position:
  already a semijoin or antijoin with the required `Distinct` on the inner side
  (outside a conjunct they add a true/false diamond keyed on the correlation
  columns, no cross join). Rewriting to a plain `JOIN` breaks multiplicity.
- A scalar subquery that is unused, or under a trivially true
  predicate: folded away entirely.
- Anything nullability-gated, once the columns are `NOT NULL`: `NOT IN` becomes
  a plain antijoin and a SELECT-list `IN` a semijoin with a `Negate` complement
  for the false rows. Check nullability before rewriting either.
- A correlated subquery made only of Map, Filter, Project, and table-function
  calls, reading no relation: inlined as a `Map`, or a `FlatMap` where it calls
  a table function, no join back.

## Rewrites and their exactness obligations

Each rewrite below carries the obligation stated with it, and the
standard two-way `EXCEPT ALL` proof applies to all of them.

1. **`NOT IN` to `NOT EXISTS`**: `NOT EXISTS (SELECT 1 FROM t2 WHERE
   t2.a = t1.a)` removes the cross join. Not equivalent: `NOT IN`
   returns no rows at all when the subquery yields a NULL and drops
   outer rows whose value is NULL, while `NOT EXISTS` treats NULL as
   non-matching and keeps NULL outer rows. The alternative `t1.a IS
   NOT NULL AND t1.a NOT IN (SELECT a FROM t2 WHERE a IS NOT NULL)`
   drops NULL outer rows instead, which matches `NOT IN` only while
   the subquery is non-empty: over an empty subquery result `NOT IN`
   is true even for a NULL outer value. Cheapest of all: declare the
   columns `NOT NULL`, and the cross join never appears.
2. **`IN` or `ANY` outside a filter conjunct**: move it into a `WHERE` conjunct
   when the boolean's consumer is a filter. A projected boolean has only the
   other form: precompute it per key in a CTE and `LEFT JOIN` that with
   `COALESCE(..., false)`. Keep the three-valued result if the outer key is
   nullable or the subquery's column can be NULL, as one inner NULL turns every
   non-match into NULL. Outside a filter conjunct the cliff is nullability
   (inside one, a nullable comparison still plans as a semijoin), and it tests
   the whole comparison: the semijoin plan needs BOTH the compared outer
   expression and the subquery's expression non-nullable, so `NOT NULL` on one
   side alone changes nothing.
3. **Subquery in a LEFT JOIN's `ON`**, when it references only the right side:
   lift it into a CTE that filters the right side, then LEFT JOIN the CTE on
   the equality alone. Predicates on the preserved side must stay in the `ON`,
   and a subquery that references the preserved side cannot be lifted (it
   decides which left rows match) and keeps the general lowering.
4. **`IN` over an uncorrelated aggregating or `LIMIT`ed subquery**: hoist the
   subquery into a CTE, `WITH s AS (...) ... JOIN s ON t.k = s.k`. Join
   directly only if `s.k` is unique (a `GROUP BY` key is), otherwise `SELECT
   DISTINCT` first. This is the fix for the aggregate and `LIMIT` cases under
   "Already handled well". When the compared column is the subquery's group key
   the original already aggregates only the outer's keys, so rewrite 8's
   condition applies: the CTE aggregates every key of the subquery's input.
5. **Nested `IN (... IN (...))`**: a correlated `EXISTS` at each level.
   `EXISTS` does not duplicate rows; a plain `JOIN` does, so never
   flatten an `EXISTS` to a `JOIN` without a `DISTINCT`.
6. **`= ANY(<array or list column>)`**: `unnest` the collection in a CTE and
   equi-join on the elements, with `DISTINCT` if the collection can repeat
   values. For a literal element test, `col @> ARRAY[x]` (or `LIST[x]`) is a
   plain filter fused into the source read (`filter=` on the Source line).
7. **Per-row subquery over `unnest` or `jsonb_array_elements`**: put the table
   function in `FROM` and aggregate at the outer level with `GROUP BY` or pick
   with `DISTINCT ON`. Inner-join semantics: outer rows with an empty or NULL
   collection disappear, and `count(*)` yields no row rather than `0`, so
   re-add those rows explicitly if they matter. An unordered `LIMIT 1` picks an
   arbitrary row in the original and in the `DISTINCT ON` form alike, so add
   the `ORDER BY` that makes the pick unique before claiming exactness. `LEFT
   JOIN LATERAL ... ON true` is NOT the fix: it keeps the wide-key diamond and
   adds an outer-join diamond keyed on the whole row. When the flatten cannot
   be made exact, narrow the correlated column first (`WITH j AS (SELECT id,
   data -> 'items' AS items FROM t)`): the arrangement key shrinks from the
   whole `jsonb` value to the extracted part. When per-row subqueries are a
   large share of a cluster's memory even after trying to rewrite them, tell
   Materialize: a planned optimizer change would compile a subquery that
   depends only on the current row into a `FlatMap` with no join back, and
   knowing about affected clusters helps prioritize it.
8. **Correlated aggregate with an equality correlation**: `WITH m AS (SELECT k,
   agg(...) ... GROUP BY k)` and `LEFT JOIN m`, when the outer's distinct
   correlation keys cover most of the inner relation's keys. The correlated
   form aggregates only the keys the outer has (its lowering joins the outer's
   distinct keys in below the aggregate) while the CTE aggregates every key of
   the inner relation, so count distinct keys on both sides first. Measured on
   the rig with the inner relation holding 100x the outer's keys, the CTE form
   was 1.7x larger for `count(*)` and 16x larger for an un-hinted `max`; with
   the outer holding 100x the inner's keys it was 3.3x and 2.4x smaller. Empty
   groups differ: the scalar subquery yields NULL, `count()` yields 0; match
   with `LEFT JOIN` plus `COALESCE`.
9. **The same subquery text in two UNION branches whose outer sides differ** (a
   different filter or relation on each branch): hoist the subquery into a CTE
   and have every branch read the CTE (`IN (SELECT k FROM cte)`, or a join
   against it), which plans it once. Materialize's common-subexpression
   elimination runs on the MIR plan and shares structurally identical subtrees,
   so identical branches are already computed once, and so is a derived table
   repeated in `FROM`. What defeats it is the subquery lowering: it joins each
   branch's distinct outer keys into its copy of the subquery, below the
   aggregate, so the copies differ and the aggregate runs once per branch.

## Unfixable by rewrite

- Correlation through a non-equality (`WHERE t2.a < t1.a`, `ON x * f.k = y *
  d.k`): no equi-join exists, and the `CrossJoin` is the plan. An inequality
  correlation crosses with or without an `OR` beside it, so the `OR` is not the
  trigger, and an equality correlation under `OR` decorrelates fine. Shrink the
  inputs instead if possible (filter, pre-aggregate, bucket).
- An uncorrelated scalar subquery in a SELECT list: the cross join is
  the semantics. It is not free even when the subquery returns one
  row, because the outer relation is arranged whole under an empty
  key, on one worker, in the columns the query demands, where without
  the subquery there is no arrangement at all. It gets worse when the
  subquery can return many rows, and that is a runtime error after the
  work is done.
