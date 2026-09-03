# Reachability, closure and impact

Patterns over a directed edge table: everything reachable from one node, the
closure of the whole graph, the neighborhood within k hops, a closure whose
edges expire on a clock, the audit that says whether anything is circular, the
topological level of a task on a DAG, and impact analysis in both directions.
Read this file to answer: what can this account reach, how big is the closure,
what is within three hops, how do I keep a closure honest as edges age out, is
there a cycle in my dependency graph, what order do these tasks run in, what
breaks if I change this table, and what fed the table that is wrong.

Fixture tables used: `accounts`, `transfers`, `pipelines`, `depends_on`. Every
block assumes `references/fixture.sql` is loaded.

The fixture's transfers form a ring, a1 to a2 to a3 and back to a1, with a3 to
a4 to a5 hanging off it and a separate a6 to a7 in its own component. The
fixture's `depends_on` is a dbt-shaped DAG: `raw_orders` feeds `stg_orders`,
`raw_customers` feeds `stg_customers`, both staging models feed `fct_sales`,
and `fct_sales` feeds `rpt_daily` and `rpt_churn`, which also depends on
`stg_customers` directly. Edges point from a task to its prerequisite.

## Everything reachable from a seed

```sql
WITH MUTUALLY RECURSIVE
    reach(dst text) AS (
        SELECT dst FROM transfers WHERE src = 'a1'
        UNION
        SELECT t.dst FROM reach r JOIN transfers t ON t.src = r.dst
    )
SELECT dst FROM reach ORDER BY dst;
```

On the fixture this returns a1, a2, a3, a4, a5. a1 is in its own reachable set
because the ring comes back to it, not because the seed was added by hand; a6
and a7 sit in another component and never appear.

It converges because `reach` holds a set of ids drawn from a finite column,
`UNION` makes re-deriving an id a no-op, and each iteration adds at most the
next frontier out from the seed. The iteration count is the longest shortest
path from the seed, plus one iteration that changes nothing and ends the loop
([semantics.md#evaluation-model](semantics.md#evaluation-model)). Nothing here
counts, so the cycle costs nothing: once the ring has been walked once, every
further derivation repeats a row `UNION` already holds.

The seed filter `src = 'a1'` is inside the binding. In the body it would
compute every account's reachable set and discard all but one, because
predicates are not pushed into a recursive binding
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).

Whether the seed itself belongs in the answer is a decision, not a fact. Here
a1 appears because of the ring; on an acyclic graph it would not. For the
reflexive reading, seed from the node table instead, with `SELECT id FROM
accounts WHERE id = 'a1'` as the base branch. That form also keeps an isolated
node, one with no transfers at all, from vanishing: an edge-derived recursion
only ever produces nodes that some edge points at.

Standard SQL brings the same shape: `WITH RECURSIVE reach(dst) AS (SELECT dst
FROM transfers WHERE src = 'a1' UNION SELECT t.dst FROM reach r JOIN transfers
t ON t.src = r.dst)`. What changes is `RECURSIVE` becoming `MUTUALLY
RECURSIVE`, the declared column list `reach(dst text)`, and moving the seed
filter inside the binding. The `UNION` is not a Materialize detail: a Postgres
user who reaches for `UNION ALL` out of habit gets a work queue that never
empties on this ring, and in Materialize the same query never converges
([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).
Oracle's `CONNECT BY` needs its `NOCYCLE` keyword for this graph; a
counter-free `UNION` binding needs no equivalent.

## Whole-graph closure

Every pair, not one seed's set:

```sql
WITH MUTUALLY RECURSIVE
    closure(src text, dst text) AS (
        SELECT src, dst FROM transfers
        UNION
        SELECT c.src, t.dst FROM closure c JOIN transfers t ON t.src = c.dst
    )
SELECT count(*) AS pairs FROM closure;
```

On the fixture this returns 17: the three ring members reach each other and
themselves, nine pairs, plus a4 and a5 from each of those three, six more, plus
a4 to a5 and a6 to a7.

It converges because the pairs are drawn from a finite set, at most the square
of the node count, `UNION` makes a re-derived pair a no-op, and the binding
only ever grows. The linear form takes one iteration per unit of graph
diameter.

The same closure with the binding joined to itself instead of to the edge
table:

```sql
WITH MUTUALLY RECURSIVE
    closure(src text, dst text) AS (
        SELECT src, dst FROM transfers
        UNION
        SELECT c1.src, c2.dst FROM closure c1 JOIN closure c2 ON c1.dst = c2.src
    )
SELECT count(*) AS pairs FROM closure;
```

This returns 17 as well. It converges by the same argument, and it gets there
in fewer iterations because each one doubles the path length it can express
rather than extending it by one edge. Measured with `RETURN AT RECURSION LIMIT`
on this fixture:

| Iterations | Linear form | Path-doubling form |
|---|---|---|
| 1 | 6 | 6 |
| 2 | 11 | 11 |
| 3 | 16 | 17 |
| 4 | 17 | 17 |

The fixture's diameter is small, so the saving is one iteration. In general the
linear form needs iterations proportional to the diameter and the doubling form
needs the logarithm of it. What it costs is size: joining the binding to itself
scans and re-arranges a relation that is already quadratic in the node count,
on both sides, every iteration
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
That trade suits a small dense graph and a one-shot query. For a maintained
view prefer the linear form, whose right-hand side stays the edge table rather
than a second copy of a quadratic relation.

Standard SQL brings the linear form and only the linear form. `WITH RECURSIVE`
permits one reference to the recursive relation, so the doubling shape cannot
be written at all
([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)).
The other change is the usual one: a Postgres closure over a cyclic graph needs
`UNION`, and it is recomputed on every read, where an indexed view here is kept
up to date as edges arrive.

## Within k hops

```sql
WITH MUTUALLY RECURSIVE
    hops(dst text, hops int) AS (
        SELECT dst, min(hops)
        FROM (
            SELECT dst, 1 FROM transfers WHERE src = 'a1'
            UNION ALL
            SELECT t.dst, h.hops + 1
            FROM hops h JOIN transfers t ON t.src = h.dst
            WHERE h.hops < 3
        ) AS x(dst, hops)
        GROUP BY dst
    )
SELECT dst, hops FROM hops WHERE dst <> 'a1' ORDER BY hops, dst;
```

On the fixture this returns (a2, 1), (a3, 2), (a4, 3). a1 is excluded in the
body because the ring makes it its own three-hop neighbor, which is true and
almost never wanted; a5 is four hops out and does not appear.

It converges because the binding holds one row per `dst`, `min` can only lower
a value, and the values are bounded below by 1. The `WHERE h.hops < 3` guard
stops production entirely after three rounds, so termination here is
structural, not a matter of the values settling.

Two placements matter, and both are forced. The hop bound is inside the binding
because a `WHERE hops <= 3` in the body would let the recursion expand the
whole graph first and then filter
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
The `min` is inside because without it a node reachable two ways at two
different lengths is two rows, and the row set never settles into one row per
node; that is the same failure the `distance` column causes in
[hierarchies.md#cycles-in-a-tree](hierarchies.md#cycles-in-a-tree), where the
counter-carrying closure diverges on a loop. With `min` in place the bound is
the only thing the loop needs, and removing the bound
entirely still converges on this cyclic fixture: it returns the full shortest
hop count, (a2, 1), (a3, 2), (a1, 3), (a4, 3), (a5, 4), because a value that
only descends toward a floor cannot cycle forever.

This binding's top level is an aggregate, so `ERROR AT RECURSION LIMIT` will
not raise on it on v26.38.1
([semantics.md#recursion-limits](semantics.md#recursion-limits)). It does not
need to here, because the hop guard bounds the loop by construction. Do not
add a limit and call the query guarded.

The phrase to push back on is "all the paths within three hops". Nearly always
the asker wants this set, the nodes and how far away they are. Enumerating
paths is a different query whose output grows exponentially with the hop bound,
and on a graph with a cycle inside the bound it is exponential in the bound
rather than in the graph.

Standard SQL brings `WITH RECURSIVE` with a depth column and `WHERE depth < 3`
in the recursive term, then `SELECT dst, MIN(depth) ... GROUP BY dst` in the
outer query. That works and it is the right answer, but the aggregate runs
after every path has been materialized. Moving `min` inside the binding is what
`WITH RECURSIVE` forbids and what keeps the loop at one row per node.

## Edges that expire

Reachability is often meant to be recent: accounts that have transacted inside
a window, not ever. A temporal filter inside the binding says so.

```sql
WITH MUTUALLY RECURSIVE
    reach(dst text) AS (
        SELECT dst FROM transfers
        WHERE src = 'a1' AND mz_now() <= ts + interval '10 years'
        UNION
        SELECT t.dst
        FROM reach r JOIN transfers t ON t.src = r.dst
        WHERE mz_now() <= t.ts + interval '10 years'
    )
SELECT dst FROM reach ORDER BY dst;
```

On the fixture this returns the same a1 through a5 as the unfiltered query. The
fixture's timestamps are all in January 2026 and the window is ten years, so
every edge is live and the result is deterministic until 2036.

It converges for exactly the reason the unfiltered version does. The filter
only ever removes edges from the relation the binding reads, and a recursion
that terminates on a graph terminates on every subgraph of it.

The window is doing real work, not decoration. The same query with a
one-month window finds nothing, because every fixture edge aged out in February
2026:

```sql
WITH MUTUALLY RECURSIVE
    reach(dst text) AS (
        SELECT dst FROM transfers
        WHERE src = 'a1' AND mz_now() <= ts + interval '1 month'
        UNION
        SELECT t.dst
        FROM reach r JOIN transfers t ON t.src = r.dst
        WHERE mz_now() <= t.ts + interval '1 month'
    )
SELECT count(*) AS reachable FROM reach;
```

This returns 0. Note that the filter appears on both branches. The seed branch
and the recursive branch read `transfers` separately, and a filter on one says
nothing about the other; leaving it off the recursive join is the way to get a
closure that expires its first hop and keeps everything past it.

Maintained, the window is what makes the closure shrink on its own:

```sql
CREATE MATERIALIZED VIEW live_reach AS
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 100)
    reach(dst text) AS (
        SELECT dst FROM transfers
        WHERE src = 'a1' AND mz_now() <= ts + interval '10 years'
        UNION
        SELECT t.dst
        FROM reach r JOIN transfers t ON t.src = r.dst
        WHERE mz_now() <= t.ts + interval '10 years'
    )
SELECT dst FROM reach;
```

```sql
SELECT dst FROM live_reach ORDER BY dst;
```

The read returns a1 through a5. A recursive binding accepts `mz_now()`, and a
materialized view over one installs and hydrates. This is the difference
between a filter on the clock and a filter on a column: the view is a standing
dataflow, so a pair leaves it when the edge supporting it ages past the window,
with no input change and no recomputation. That retraction is Materialize's
documented temporal-filter behavior: an `mz_now()` bound in a `WHERE` clause
drops a row when the clock passes it, which is what the `now()` and `mz_now()`
function reference calls a temporal filter. `mz_now()` is the function that
does this, and it is the only one available: swapping in
`now()` makes the same view fail to create, with `ERROR:  cannot materialize
call to current_timestamp`.

Standard SQL brings nothing comparable. A Postgres closure with a
`ts > now() - interval '30 days'` predicate is correct at the instant it runs
and stale immediately after, so the pattern there is a cron job that
recomputes. What changes is that the recomputation disappears.

## Cycle membership

The cheap answer to "is anything circular":

```sql
WITH MUTUALLY RECURSIVE
    closure(src text, dst text) AS (
        SELECT src, dst FROM transfers
        UNION
        SELECT c.src, t.dst FROM closure c JOIN transfers t ON t.src = c.dst
    )
SELECT id
FROM (SELECT src AS id FROM closure WHERE src = dst) AS on_cycle
ORDER BY id;
```

On the fixture this returns a1, a2, a3: the three accounts on the ring. a4 and
a5 are reachable from the ring but not on it, so they are not their own
successors.

It converges because it is the closure binding of the previous section, whose
convergence does not depend on the graph being acyclic, plus a body that runs
once at the fixpoint. That is the point of the query: the audit that tells you
whether the data is cyclic must itself be safe on cyclic data, which a
counter-free `UNION` binding is and a `distance`-carrying one is not
([hierarchies.md#cycles-in-a-tree](hierarchies.md#cycles-in-a-tree)). The seed
is the direct edges rather than a reflexive `(id, id)` row, so `src = dst`
means "there is a cycle through this node" and not "this is the identity row".

Run it as a maintained view over any graph that is supposed to be acyclic, a
dependency DAG or a parent-pointer table, and it is a standing alarm. It tells
you which nodes are on some cycle. It does not tell you which nodes are on the
same cycle, or how many cycles there are; that is the strongly connected
component problem, and it lives in `components.md`.

Standard SQL brings Postgres 14's `CYCLE id SET is_cycle USING path` clause, or
a hand-rolled path array with a containment guard before that, both of which
attach cycle detection to a walk. Materialize has neither, and for this
question needs neither: the closure converges on cyclic input, so the cycle
shows up as an ordinary row rather than as a special flag.

## Topological level on a DAG

```sql
WITH MUTUALLY RECURSIVE
    level(task text, level int) AS (
        SELECT task, max(level)
        FROM (
            SELECT p.id, 0
            FROM pipelines p
            WHERE NOT EXISTS (SELECT 1 FROM depends_on d WHERE d.task = p.id)
            UNION ALL
            SELECT d.task, l.level + 1
            FROM level l JOIN depends_on d ON d.prereq = l.task
        ) AS x(task, level)
        GROUP BY task
    )
SELECT task, level FROM level ORDER BY level, task;
```

On the fixture this returns `raw_customers` and `raw_orders` at 0,
`stg_customers` and `stg_orders` at 1, `fct_sales` at 2, and `rpt_churn` and
`rpt_daily` at 3. The level is the length of the longest prerequisite chain
below a task, which is what a scheduler wants: everything at level n can run
once level n-1 has finished. `max`, not `min`: `rpt_churn` depends on both
`stg_customers` at level 1 and `fct_sales` at level 2, and it has to wait for
the later one.

It converges on a DAG because the binding holds one row per task, a task's
value is final one iteration after all of its prerequisites' values are, and
the longest chain is finite. Here that chain is `raw_orders`, `stg_orders`,
`fct_sales`, `rpt_daily`, so the values are settled after four iterations and
the fifth changes nothing. (`RETURN AT RECURSION LIMIT 3` still shows
`rpt_churn` at 2, on its way up from `stg_customers` before `fct_sales` has
reached its own final level.)

The seed comes from `pipelines`, the node table, not from `depends_on`. A task
that appears in no dependency row at all is still a task, and seeding from the
node table puts it at level 0 instead of dropping it.

On cyclic data this recursion has no fixpoint, and the limit does not save it.
The binding is topped by an aggregate, so on v26.38.1 `ERROR AT RECURSION
LIMIT` does not raise
([rollups.md#the-same-with-the-aggregate-inside](rollups.md#the-same-with-the-aggregate-inside)).
This block runs the same shape over inline data where `t0` feeds `t1`, and
`t1`, `t2`, `t3` form a cycle among themselves:

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 20)
    looped(task text, prereq text) AS (
        SELECT task, prereq
        FROM (VALUES ('t1', 't0'), ('t2', 't1'), ('t3', 't2'), ('t1', 't3')) AS v(task, prereq)
    ),
    level(task text, level int) AS (
        SELECT task, max(level)
        FROM (
            SELECT l.prereq, 0
            FROM looped l
            WHERE NOT EXISTS (SELECT 1 FROM looped d WHERE d.task = l.prereq)
            UNION ALL
            SELECT d.task, l.level + 1
            FROM level l JOIN looped d ON d.prereq = l.task
        ) AS x(task, level)
        GROUP BY task
    )
SELECT task, level FROM level ORDER BY task;
```

It returns `t0` at 0, `t2` at 17, `t3` at 18 and `t1` at 19, with no error.
Those are not levels; they are the running counters at iteration 20, and at
`ERROR AT RECURSION LIMIT 30` they come back as 27, 28 and 29 instead. A
materialized view of this shape installs, and it serves. A read of one built
over this exact block returns those same four rows in well under a second, and
`mz_internal.mz_hydration_statuses` reports `hydrated = f` for it the whole
time. The limit is what makes that possible: it stops the loop, so the view has
a state to hand out, and iteration-20 counters are indistinguishable from
levels to whatever reads them. Only the unlimited form behaves the way an
unconverged view is supposed to, holding a dataflow and returning nothing
([semantics.md#recursion-limits](semantics.md#recursion-limits)).

Guard it with the `on_cycle` audit above, which converges on exactly the data
that breaks this one. For a self-check inside the query itself, use `RETURN AT
RECURSION LIMIT` with the limit set above the number of tasks, and reject the
result when any level reaches that number: no level on a DAG of n tasks can
exceed n-1, and a cycle's counters top out at the limit minus one, so the check
only means something when the limit is larger than n. At or below n it passes
on fabricated levels.

Standard SQL brings "traverse every path from every root, then `GROUP BY task`
with `MAX(depth)` outside". It gives the same answer on a DAG and it
materializes one row per path to get there, and the number of paths is
exponential in the depth: k diamonds stacked on each other have 2^k paths from
top to bottom. Moving `max` inside the binding keeps the state at one row per
task
([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)).

## Impact analysis, both directions

Downstream, following edges from a prerequisite to the tasks that depend on it:

```sql
WITH MUTUALLY RECURSIVE
    downstream(task text) AS (
        SELECT task FROM depends_on WHERE prereq = 'raw_customers'
        UNION
        SELECT d.task FROM downstream s JOIN depends_on d ON d.prereq = s.task
    )
SELECT task FROM downstream ORDER BY task;
```

On the fixture this returns `fct_sales`, `rpt_churn`, `rpt_daily` and
`stg_customers`: everything that would be wrong or stale if `raw_customers`
changed or broke.

Upstream, following the same edges the other way:

```sql
WITH MUTUALLY RECURSIVE
    upstream(prereq text) AS (
        SELECT prereq FROM depends_on WHERE task = 'rpt_churn'
        UNION
        SELECT d.prereq FROM upstream u JOIN depends_on d ON d.task = u.prereq
    )
SELECT prereq FROM upstream ORDER BY prereq;
```

On the fixture this returns `fct_sales`, `raw_customers`, `raw_orders`,
`stg_customers` and `stg_orders`: everything `rpt_churn` is computed from,
including `raw_orders`, which reaches it only through `stg_orders` and
`fct_sales`.

Both converge by the seeded-reach argument: a finite set of task names, `UNION`
making re-derivation a no-op, one frontier per iteration. Neither carries a
counter, so both are safe to run before the cycle audit has cleared the graph.

The two are the same query with the join and the seed column swapped, and
choosing between them is the whole job:

| Question | Direction | Query |
|---|---|---|
| What breaks if I change this | Downstream | `downstream`, seeded on `prereq` |
| Who is affected by this outage | Downstream | `downstream`, seeded on `prereq` |
| Why is this number wrong | Upstream | `upstream`, seeded on `task` |
| What do I have to backfill first | Upstream | `upstream`, seeded on `task` |
| Can I drop this table | Downstream, and empty means yes | `downstream`, seeded on `prereq` |

"Impact" and "lineage" are both used for both directions, so the word in the
request does not settle it. The test that does: name the node you already know
is bad and ask whether the answer should be the causes or the consequences.

Standard SQL brings the identical pair with `WITH RECURSIVE`, and the same
trap: the two queries differ by one join condition and one column, so a
copy-and-edit produces a query that runs, returns plausible task names, and
answers the other question. Nothing about the port changes that; declaring the
binding `downstream(task text)` and `upstream(prereq text)` at least makes the
column being followed visible in the header.

## Pitfalls

- `UNION ALL` on a graph with a cycle. It never converges, and the distinct
  rows look correct under `RETURN AT RECURSION LIMIT` while the row counts
  climb
  ([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).
  Reachability wants `UNION`.
- A hop, depth or path column in a binding without an aggregate over it. It
  defeats the deduplication that makes the fixpoint reachable: a node reached
  at two lengths is two rows, and around a cycle it is a new row every lap
  ([hierarchies.md#cycles-in-a-tree](hierarchies.md#cycles-in-a-tree)). Wrap it
  in `min` inside the binding, as the `hops` block does.
- Trusting `ERROR AT RECURSION LIMIT` on `hops` or `level`. Both are topped by
  an aggregate, and on v26.38.1 the limit returns the iteration-n state instead
  of raising. `hops` is bounded by its own guard; `level` needs the `on_cycle`
  audit standing next to it.
- Leaving the direction unstated. "Everything connected to this account" and
  "everything downstream of this model" are two queries, and on a directed
  graph they give different answers. Undirected reachability needs the edge
  relation symmetrized first, which is `components.md`.
- Reading "all the paths within n hops" literally. The node set with its
  minimum hop count is almost always the question; path enumeration is
  exponential and, on a graph with a cycle inside the bound, exponential in the
  bound.
- Whole-graph closure on a dense graph. The result approaches the square of the
  node count, so a 100,000-node graph with a large strongly connected component
  is a closure nobody can hold. Seed it, bound the hops, or work on components
  instead.
- The path-doubling form in a maintained view. It converges in fewer iterations
  and it re-arranges a quadratic relation on both sides of the join every one
  of them. Save it for one-shot queries on small graphs.
- A temporal filter on the seed branch only. Both branches read the edge table
  independently, so the window has to appear on each of them; on one, the
  closure expires its first hop and keeps everything reached through it.
- Filtering the reachable set in the body when the filter is really a seed. The
  predicate is not pushed into the binding, so the recursion still expands the
  whole graph
  ([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
- Assuming the seed is in the answer, or that it is not. Here a1 appears
  because the ring returns to it. On an acyclic graph the same query omits the
  seed. Seed from the node table when the reflexive reading is the one you
  want.
