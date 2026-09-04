---
name: mz-graph-queries
description: >
  Write correct, convergent, maintainable graph and hierarchy queries in
  Materialize with WITH MUTUALLY RECURSIVE. Use when a user asks for a
  recursive CTE or WITH RECURSIVE in Materialize, or for anything over a tree,
  hierarchy, or graph: org charts, bill of materials, category trees,
  descendants or ancestors, depth or level, rollups along a hierarchy,
  reachability or transitive closure, k-hop neighbours, shortest or cheapest
  path, connected components, entity resolution clusters, strongly connected
  components, cycle detection, topological order, lineage or dependency impact
  analysis, permission or role inheritance, or multi-hop traversal of a context
  graph. Also use when translating WITH RECURSIVE, CONNECT BY, or DuckDB USING
  KEY queries to Materialize, or when a recursive view never returns or never
  hydrates.
---

# Graph and hierarchy queries with WITH MUTUALLY RECURSIVE

Materialize spells recursion `WITH MUTUALLY RECURSIVE`, and it evaluates a
fixpoint: every binding starts empty, one iteration updates each binding in
list order, the loop stops when an iteration changes nothing, and the body runs
against that fixpoint
([semantics.md#evaluation-model](references/semantics.md#evaluation-model)).
Almost any SQL is legal inside a binding, aggregates and `DISTINCT ON` and
`NOT EXISTS` over the binding included. The work is to pick the pattern, prove
it converges, and keep it cheap to maintain.

## Hand-offs

- An existing recursive view lags wall-clock time: `materialize-debug-freshness`.
- A recursive view costs too much memory: `mz-optimize-memory`.
- How to model the entities and relationships it walks: `mz-ontology-design`.

## Step 1: Classify the ask

Answer four questions first. **Structure**: tree, DAG, or general graph with
cycles. **Direction**: directed, undirected and therefore symmetrized first, or
mutual. **Output**: membership, a per-node min, max or sum, or a witness path.
**Lifetime**: a one-shot `SELECT`, or a maintained, indexed view.

| The ask sounds like | Family | Pattern | Where |
|---|---|---|---|
| "everyone under", "reports to", "subtree" | descendants | `subtree` | [hierarchies.md#descendants-of-one-node](references/hierarchies.md#descendants-of-one-node) |
| "path to the top", "which division", "breadcrumb" | ancestors and root | `chain`, `rooted` | [hierarchies.md#ancestors-of-one-node](references/hierarchies.md#ancestors-of-one-node), [#depth-and-root-for-every-node](references/hierarchies.md#depth-and-root-for-every-node) |
| "level", "depth", "how deep" | depth from the root, or height from the leaves, which is a different recursion | `levels`, `height` | [hierarchies.md#depth-and-root-for-every-node](references/hierarchies.md#depth-and-root-for-every-node), [rollups.md#height-above-the-leaves](references/rollups.md#height-above-the-leaves) |
| "total under each", "roll up", "headcount", "how many of each part" | rollups | `team`, `totals`, `needed`, `needed_agg` | [rollups.md#sum-along-a-tree-aggregate-inside-the-binding](references/rollups.md#sum-along-a-tree-aggregate-inside-the-binding), [#bill-of-materials-quantities-multiply-along-each-path](references/rollups.md#bill-of-materials-quantities-multiply-along-each-path) |
| "connected to", "reachable", "downstream", "upstream", "impact", "lineage" | reachability | `reach`, `closure`, `downstream`, `upstream` | [reachability.md#everything-reachable-from-a-seed](references/reachability.md#everything-reachable-from-a-seed), [#impact-analysis-both-directions](references/reachability.md#impact-analysis-both-directions) |
| "within n hops", "all paths within" | k-hop with `min` inside | `hops` | [reachability.md#within-k-hops](references/reachability.md#within-k-hops) |
| "shortest", "cheapest", "fewest hops", "route" | shortest paths | `sym`, `hops`, `dist`, `best`, `route` | [shortest-paths.md#fewest-hops](references/shortest-paths.md#fewest-hops), [#cheapest-route](references/shortest-paths.md#cheapest-route), [#one-witness-path](references/shortest-paths.md#one-witness-path) |
| "clusters", "groups of linked", "same customer", "duplicates", "rings" | components or SCC | `links`, `label`, `scc_closure`, `scc_trim` | [components.md#connected-components-by-min-label-propagation](references/components.md#connected-components-by-min-label-propagation), [#strongly-connected-components-without-the-closure](references/components.md#strongly-connected-components-without-the-closure) |
| "loop", "circular", "is this a tree" | cycle audit | `closure` | [reachability.md#cycle-membership](references/reachability.md#cycle-membership) |
| "build order", "which first" | topological level | `level` | [reachability.md#topological-level-on-a-dag](references/reachability.md#topological-level-on-a-dag) |
| "effective permissions", "inherits access", "can user see" | permissions | `effective`, `user_access`, `holds` | [permissions.md#inheritance-down-a-group-tree-with-overrides](references/permissions.md#inheritance-down-a-group-tree-with-overrides), [#per-user-and-a-point-check](references/permissions.md#per-user-and-a-point-check) |
| "convert this `WITH RECURSIVE` / `CONNECT BY` / `USING KEY`" | migration | the same pattern, quoted verbatim | [migrating.md#translation-table](references/migrating.md#translation-table) |
| "never returns", "never hydrates", "stuck hydrating" | convergence | the binding's top, and what it is unioned with | [semantics.md#multisets-and-convergence](references/semantics.md#multisets-and-convergence), [#pitfalls](references/semantics.md#pitfalls) |
| "agent", "context graph", "knowledge graph traversal" | routes to one of the above | typed `edges` from the registry | [context-graphs.md#agent-questions-to-patterns](references/context-graphs.md#agent-questions-to-patterns) |

Resolve these mis-specifications first; each one changes the answer.

- "All paths" almost always means reachability. Path enumeration is a different
  query whose output grows exponentially
  ([reachability.md#within-k-hops](references/reachability.md#within-k-hops)).
- "Connected" on a directed relation is ambiguous: weak connectivity
  symmetrizes the edges, strong connectivity is the SCC question
  ([components.md#strongly-connected-components-from-the-closure](references/components.md#strongly-connected-components-from-the-closure)).
- "Total under each node" needs two decisions: is the node's own value in, and
  is a shared child counted once or once per path
  ([rollups.md#shared-components-once-or-per-path](references/rollups.md#shared-components-once-or-per-path)).
- Undirected data is usually stored one way. Symmetrize in a leading binding
  ([shortest-paths.md#symmetrize-once](references/shortest-paths.md#symmetrize-once)).
- "The shortest path" with ties means one witness unless the asker says
  otherwise, and the two shapes are not extensions of each other
  ([shortest-paths.md#one-witness-path](references/shortest-paths.md#one-witness-path)).

## Step 2: Write the recursion

1. Declare a name and type for every column, and cast every branch. A string
   literal and a bare `NULL` both type as `text`
   ([semantics.md#column-types](references/semantics.md#column-types)).
2. Put the aggregate inside the binding and recurse from the reduced relation,
   instead of enumerating paths and reducing in the body
   ([migrating.md#translation-table](references/migrating.md#translation-table)).
3. Use `UNION` by default. `UNION ALL` is correct only when every row derives
   exactly once, or when an aggregate above it collapses each group
   ([semantics.md#multisets-and-convergence](references/semantics.md#multisets-and-convergence)).
4. Carry narrow keys through the loop and join the payload back in the body;
   every declared column is kept and re-arranged each iteration
   ([semantics.md#what-the-optimizer-will-not-do](references/semantics.md#what-the-optimizer-will-not-do)).
5. Keep hop bounds, temporal filters and pruning inside the binding. Predicates
   are never pushed into a recursive binding, so a filter in the body computes
   the whole answer first
   ([reachability.md#within-k-hops](references/reachability.md#within-k-hops)).

Non-recursive prep goes in a leading binding, where it is hoisted out of the
loop and computed once. The canonical shape:

<!-- verify: skip -->

```sql
WITH MUTUALLY RECURSIVE (RETURN AT RECURSION LIMIT 1000)
    -- non-recursive prep (symmetrize, filter, type) is hoisted out of the loop
    edges(src text, dst text) AS (
        SELECT src, dst FROM base_edges
        UNION
        SELECT dst, src FROM base_edges
    ),
    -- the recursive binding: aggregate inside, recurse from the reduced relation
    result(node text, value int) AS (
        SELECT node, min(value)
        FROM (
            SELECT seed_node, 0 FROM seeds
            UNION ALL
            SELECT e.dst, r.value + 1
            FROM result r JOIN edges e ON e.src = r.node
        ) AS x(node, value)
        GROUP BY node
    )
-- payload joins and display filters live in the body
SELECT r.node, r.value, n.name
FROM result r JOIN nodes n ON n.id = r.node;
```

That skeleton names tables outside the bundled fixture, so it is marked
`verify: skip`; every block the verifier runs is checked against recorded
output. `result` is reduce-topped, so the guard is `RETURN AT` and the body
owes a check on the returned state, per Step 4.

## Step 3: Prove termination

Before running it, state which of these holds
([semantics.md#multisets-and-convergence](references/semantics.md#multisets-and-convergence)):

- The binding is monotone and topped by `UNION`, over a finite domain: it can
  only add distinct rows, and there are finitely many.
- An aggregate bounds how often each row's value can change: `min` only falls
  and has a floor, `max` only rises and has a ceiling, one row per key.
- Cycles are handled, either by set semantics (a counter-free `UNION` closure
  converges on cyclic data) or by the aggregate. A `distance` column added to a
  `UNION` closure is what turns a cycle into divergence
  ([hierarchies.md#cycles-in-a-tree](references/hierarchies.md#cycles-in-a-tree)).
- For `EXCEPT ALL` bindings, state-machine bindings and anything non-monotone,
  name the progress measure explicitly: what strictly decreases each iteration
  ([semantics.md#binding-order-and-the-delay-idiom](references/semantics.md#binding-order-and-the-delay-idiom)).

"Nothing changed" counts multiplicities, not distinct rows: a `UNION ALL`
carry-forward branch re-adds rows the binding holds, so the loop never stops.

## Step 4: Guard and verify

Every maintained recursive view ships a limit; what tops the binding decides
which one and what it proves ([semantics.md#recursion-limits](references/semantics.md#recursion-limits)):

- **`UNION`-topped**: `ERROR AT RECURSION LIMIT n`, with n well above the
  expected graph diameter. Every change it can make is a row change, so the
  limit fires.
- **Reduce- or TopK-topped** (`min`, `max`, `sum`, `DISTINCT ON`): `ERROR AT`
  goes silent once the key set settles and only the values keep moving. Ship
  `RETURN AT RECURSION LIMIT n` anyway, n above the expected iteration count: it
  bounds runtime. Correctness is then a check on the returned state rejecting a
  value at or near the limit, plus a standing audit of whatever the floor rests
  on ([reachability.md#topological-level-on-a-dag](references/reachability.md#topological-level-on-a-dag)).

When a block mixes shapes, the recursive binding's top governs the choice: the
limit is per block ([semantics.md#recursion-limits](references/semantics.md#recursion-limits)),
and a non-recursive prep binding is hoisted out of the loop anyway
([semantics.md#what-the-optimizer-will-not-do](references/semantics.md#what-the-optimizer-will-not-do)).

A limited recursion over cyclic data is not a safe fallback. A materialized view
of that shape installs, hydrates, reports `hydrated = t`, and serves iteration-n
counters that look like answers; only the unlimited form fails visibly, by never
hydrating ([reachability.md#topological-level-on-a-dag](references/reachability.md#topological-level-on-a-dag)).
That is why the reduce-topped guard is a limit *and* a check: the limit bounds
runtime, the check on the returned state keeps iteration-n state out of answers.

Then verify. Step the binding with `RETURN AT RECURSION LIMIT 1`, `2`, `3` and
watch it grow. For a maintained view, insert an edge and confirm the answer
moves, then delete it and confirm it moves back. The three typing errors that
surface before the recursion runs ([semantics.md#column-types](references/semantics.md#column-types)):

| Error or symptom | Cause | Fix |
|---|---|---|
| `declared types (bigint), but query returns types (text)` | an untyped literal: `SELECT '1'`, or a bare `NULL` | cast every branch, `'1'::int8` and `NULL::int` |
| `UNION types integer and text cannot be matched` | the union's branches disagree before the declaration is consulted | cast each branch of the union, not just the declaration |
| a value silently changes, e.g. `1.23456` stored as `1.23` | the declared typmod applies as an assignment cast | declare the scale you want, not the literal's |

## Step 5: Make it maintainable

Index the loop-invariant inputs on the join key. Imported indexes on base
tables are usable inside the loop, and they are the main performance lever;
arrangements of the binding itself do not survive the back edge
([semantics.md#what-the-optimizer-will-not-do](references/semantics.md#what-the-optimizer-will-not-do)).

Then check update locality: one input change should touch a bounded number of
rows per iteration
([semantics.md#update-locality](references/semantics.md#update-locality)).
Reachability has it, and a rollup over a tree of height h touches at most 2h
rows. Naive PageRank and k-means do not: every row's value depends on every
other's, so one input change recomputes most of the state. Compute those
one-shot with `RETURN AT RECURSION LIMIT` or outside the database.

## Reading the plan

`EXPLAIN` a recursive query and read it in this order
([semantics.md#reading-explain](references/semantics.md#reading-explain)):

- An outer `With` above the recursive node is the hoist: those reads happen
  once, not per iteration.
- `With Mutually Recursive` wraps one `cte [recursion_limit=N] lN =` block per
  binding. The limit is per block, rendered on every binding's cte.
- A `Stream lN` inside `cte lN` is the back edge.
- A `Distinct GroupAggregate` is where `UNION` planned its deduplication, the
  operator that makes the fixpoint reachable.
- An `Arrange` over the `Stream` under a join is the binding re-arranged every
  iteration, the cost the back edge imposes.
- `EXPLAIN OPTIMIZED PLAN WITH (linear chains) AS TEXT FOR ...` is rejected
  for recursive plans.

## What is allowed inside a binding

Standard SQL forbids all of this; the patterns in this skill depend on it
([semantics.md#what-standard-sql-forbids-that-wmr-allows](references/semantics.md#what-standard-sql-forbids-that-wmr-allows)).

| Allowed | What it unlocks |
|---|---|
| `min`, `max`, `sum` over the binding | shortest path and cheapest cost, kept per key each iteration |
| `SELECT DISTINCT` and `UNION` | the deduplication that makes a fixpoint reachable at all |
| `LEFT JOIN` with the binding on the outer side | defaults and overrides: inherit only where a child has none |
| More than one reference to the binding | path doubling: closure in log(diameter) iterations |
| Subquery or `NOT EXISTS` over the binding | one witness path, cycle guards, negation-based fixpoints |
| `ORDER BY ... LIMIT` and `DISTINCT ON` | argmin and top-k per node, kept inside the loop |
| More than one recursive relation | mutual recursion across the whole binding list |
| A nested recursive block in derived-table position | inner fixpoints per outer iteration |
| A binding with no base case | constraint-propagation shapes with no natural seed |

## Reference map

| File | What is in it |
|---|---|
| [semantics.md](references/semantics.md) | evaluation model, multisets, the delay idiom, typing, recursion limits, optimizer blind spots, `EXPLAIN`, update locality |
| [hierarchies.md](references/hierarchies.md) | `subtree`, `chain`, `levels`, `rooted`, `closure`, `paths`: descendants, ancestors, depth and root, a maintained closure table, ordered display, cycles in a "tree" |
| [rollups.md](references/rollups.md) | `team`, `totals`, `height`, `needed`, `needed_agg`: subtree sums, height, BOM explosion with quantities, kit cost, once against per path |
| [reachability.md](references/reachability.md) | `reach`, `closure`, `hops`, `level`, `downstream`, `upstream`: closure, k-hop, expiring edges, cycle audit, topological level, impact both ways |
| [shortest-paths.md](references/shortest-paths.md) | `sym`, `hops`, `dist`, `best`, `route`: fewest hops, cheapest route, one witness path, a single target |
| [components.md](references/components.md) | `links`, `label`, `scc_closure`, `scc_trim`: min-label propagation, match thresholds, golden records, SCC with and without the closure |
| [permissions.md](references/permissions.md) | `effective`, `user_access`, `holds`: inheritance with overrides, multiple parents, an indexed point check, denies, the Zanzibar shape |
| [migrating.md](references/migrating.md) | `WITH RECURSIVE`, SQL Server `MAXRECURSION`, Postgres `CYCLE`, Oracle `CONNECT BY`, DuckDB `USING KEY`, and the habits that are silently wrong here |
| [context-graphs.md](references/context-graphs.md) | agent questions routed to families, typed edges from the relationship registry, as-of traversal on effective-dated edges |
| [fixture.sql](references/fixture.sql) | the example world every block above runs against: load it and run any of them |
