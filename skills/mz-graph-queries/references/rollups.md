# Rollups along a hierarchy

Patterns that aggregate over a tree or a DAG: the total for every subtree, the
same total when the amounts live in a separate table, height measured up from
the leaves, a bill of materials exploded with quantities, the cost of that
bill, and the choice between counting a shared node once and counting it once
per path. Read this file to answer: how do I sum a subtree without building a
closure first, where does the aggregate go, how tall is this node, how many
bolts does a bike need, and does my rollup want "once" or "per path".

Fixture tables used: `employees`, `parts`, `bom`. Every block assumes
`references/fixture.sql` is loaded.

The fixture tree is Ada (1) over Bob (2) and Cy (3); Bob over Dee (4) and Eli
(5); Cy over Fay (6); Dee over Gus (7) and Hal (8). The fixture BOM is a bike
(1) made of 2 wheels (2) and 1 frame (3); a wheel of 32 spokes (4), 1 tire (6)
and 4 bolts (5); a frame of 6 bolts. The bolt is the shared part.

## Sum along a tree, aggregate inside the binding

```sql
WITH MUTUALLY RECURSIVE
    team(id int, manager_id int, total int) AS (
        SELECT e.id, e.manager_id, e.salary + coalesce(sum(t.total), 0)::int
        FROM employees e LEFT JOIN team t ON t.manager_id = e.id
        GROUP BY e.id, e.manager_id, e.salary
    )
SELECT id, total FROM team ORDER BY id;
```

On the fixture this returns Ada 1195, Bob 605, Cy 290, Dee 295, Eli 110, Fay
100, Gus 90, Hal 85: every person's own salary plus the salary of everyone
below them. The `LEFT JOIN` is what makes a leaf work. With no children `sum`
is NULL, `coalesce` turns it into 0, and the leaf's total is its own salary.

It converges because the binding holds exactly one row per employee in every
iteration, so the only thing that can change is a total. A node's total is
final one iteration after all of its children's are, so the values settle after
height-plus-one iterations, four on this fixture, and the next iteration
changes nothing and ends the loop. (`RETURN AT RECURSION LIMIT 3` still shows
Ada at 1020, and limit 4 shows 1195.) There is no `UNION` anywhere: the binding
is a plain query over itself, and the `GROUP BY` collapses each id to a single
row, so the multiset growth that breaks `UNION ALL` recursions cannot happen
here
([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).

Maintained, this is cheap. One salary change retracts and re-adds one row at
each level above it, at most 2h rows for a tree of height h
([semantics.md#update-locality](semantics.md#update-locality)). Keep the
binding to the three columns it needs; `manager_id` is in it because the join
needs it, and `name` is not because the body can join it back
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).

Standard SQL brings a two-step shape, because `WITH RECURSIVE` forbids an
aggregate in the recursive term. Build the closure first, join the facts on the
descendant, then group by the ancestor:

```postgresql
WITH RECURSIVE closure(ancestor, descendant) AS (
    SELECT id, id FROM employees
    UNION ALL
    SELECT c.ancestor, e.id FROM closure c JOIN employees e ON e.manager_id = c.descendant
)
SELECT c.ancestor AS id, sum(e.salary) AS total
FROM closure c JOIN employees e ON e.id = c.descendant
GROUP BY c.ancestor;
```

That materializes one row per ancestor-descendant pair, which is quadratic in
the size of a deep subtree, and it has to be recomputed from scratch when a
salary changes. The Materialize form keeps one row per node and pays only for
the rows an update actually touches.

## Folder-totals form

The same answer with the contributions arriving through a `UNION ALL` that a
`GROUP BY` collapses:

```sql
WITH MUTUALLY RECURSIVE
    totals(id int, total int) AS (
        SELECT id, sum(amount)::int
        FROM (
            SELECT id, salary AS amount FROM employees
            UNION ALL
            SELECT e.manager_id, t.total
            FROM totals t JOIN employees e ON e.id = t.id
            WHERE e.manager_id IS NOT NULL
        ) AS x(id, amount)
        GROUP BY id
    )
SELECT id, total FROM totals ORDER BY id;
```

On the fixture this returns the same eight rows as `team`: Ada 1195, Bob 605,
Cy 290, Dee 295, and each leaf at its own salary.

It converges for the same reason and on the same schedule as `team`, four
iterations to the final values on this fixture and one more that changes
nothing. The `UNION ALL` inside the derived table is safe precisely because the
`GROUP BY` sits above it: the seed branch is re-read every iteration, but the
aggregate collapses each id to one row, so no row count can grow. That is the
narrow exception to the "use `UNION`" rule
([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).

Prefer `team` when the parent pointer lives on the same row as the amount, as
it does on `employees`. Prefer `totals` when the contributions come from a
separate table: folders and files, accounts and postings, projects and time
entries. In that case the first branch becomes a join to the fact table
(`SELECT f.folder_id, f.bytes FROM files f`), the binding stays two columns
wide, and the fact rows never travel around the loop.

Standard SQL brings the same closure-then-group shape as the previous section,
usually written as "recursive descendants of each folder, join files, sum".
What changes is that the aggregate moves inside the recursion, so the
intermediate closure is never built.

## Height above the leaves

```sql
WITH MUTUALLY RECURSIVE
    height(id int, manager_id int, h int) AS (
        SELECT e.id, e.manager_id, coalesce(max(c.h) + 1, 0)
        FROM employees e LEFT JOIN height c ON c.manager_id = e.id
        GROUP BY e.id, e.manager_id
    )
SELECT id, h FROM height ORDER BY h DESC, id;
```

On the fixture this returns Ada 3, Bob 2, Cy 1, Dee 1, and 0 for Eli, Fay, Gus
and Hal: the number of levels below each node.

It converges by the same argument as `team`, with `max` in place of `sum`: one
row per node, a value that is final one iteration after its children's are,
final after height-plus-one iterations on this fixture, then a no-op iteration.

Height is not depth. `levels` in
[hierarchies.md](hierarchies.md#depth-and-root-for-every-node) counts down from
the root; `height` counts up from the leaves. Cy is at depth 1 and height 1;
Dee is at depth 2 and height 1; Gus is at depth 3 and height 0. When someone
asks for "the level", ask which end they are counting from. Depth answers
"where does this sit in the org", height answers "how many approval steps are
still below this node" or "how long is the longest assembly chain under this
part".

Standard SQL brings, again, a post-recursion aggregate: build the closure with
a `distance` column and take `max(distance)` per ancestor, or compute depth
top-down and take `max(depth) - depth` over each subtree. Both need the whole
closure. Putting `max` inside the binding is the thing `WITH RECURSIVE`
forbids.

## Bill of materials, quantities multiply along each path

```sql
WITH MUTUALLY RECURSIVE
    needed(part_id int, qty int) AS (
        SELECT child_id, qty FROM bom WHERE parent_id = 1
        UNION ALL
        SELECT b.child_id, n.qty * b.qty
        FROM needed n JOIN bom b ON b.parent_id = n.part_id
    )
SELECT part_id, sum(qty) AS qty FROM needed GROUP BY part_id ORDER BY part_id;
```

On the fixture this returns wheel 2, frame 1, spoke 64, tire 2, bolt 14: one
bike needs 64 spokes (2 wheels times 32) and 14 bolts (2 wheels times 4, plus 6
in the frame).

Here `UNION ALL` is the correct operator, not the accident it usually is. The
binding holds one row per path from the kit down to a part, every path derives
exactly once, and the bolt's two paths must both count. `UNION` would fold the
two bolt rows together whenever their quantities happened to be equal and
silently undercount. It converges because a BOM is a DAG: each iteration
extends every path by one edge, the longest path under the bike is two edges,
and iteration three derives nothing new
([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).

The seed filter `parent_id = 1` is inside the binding. In the body it would
explode every kit in the catalog and then discard all but one, because
predicates are not pushed into a recursive binding
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).

"It is a DAG" is an assumption about the data, and the data can break it. A
part that transitively contains itself makes the path set infinite, and the
quantities grow without bound. This block and the one in the next section use
inline data so the fixture stays a DAG; in it part 1 contains 2, part 2
contains 3, and part 3 contains 2 again:

<!-- verify: error -->

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 20)
    looped_bom(parent_id int, child_id int, qty int) AS (
        SELECT parent_id, child_id, qty
        FROM (VALUES (1, 2, 2), (2, 3, 3), (3, 2, 1)) AS v(parent_id, child_id, qty)
    ),
    needed(part_id int, qty int) AS (
        SELECT child_id, qty FROM looped_bom WHERE parent_id = 1
        UNION ALL
        SELECT b.child_id, n.qty * b.qty
        FROM needed n JOIN looped_bom b ON b.parent_id = n.part_id
    )
SELECT part_id, sum(qty) AS qty FROM needed GROUP BY part_id;
```

`ERROR:  Evaluation error: Recursive query exceeded the recursion limit 20.`
Put `ERROR AT RECURSION LIMIT` on any maintained explosion, set well above the
deepest assembly you expect; without it the view installs, never hydrates, and
holds a dataflow until it is dropped
([semantics.md#recursion-limits](semantics.md#recursion-limits)).

Standard SQL brings this one almost unchanged: `WITH RECURSIVE needed AS
(SELECT child_id, qty FROM bom WHERE parent_id = 1 UNION ALL SELECT
b.child_id, n.qty * b.qty FROM needed n JOIN bom b ON b.parent_id =
n.part_id)`. It is the textbook Postgres BOM query, it is linear and monotone,
and it keeps its `UNION ALL`. What changes is the header, the declared column
types, moving the seed filter inside the binding, and the recursion limit.

## The same with the aggregate inside

```sql
WITH MUTUALLY RECURSIVE
    needed_agg(part_id int, qty int) AS (
        SELECT child_id, sum(q)::int
        FROM (
            SELECT child_id, qty AS q FROM bom WHERE parent_id = 1
            UNION ALL
            SELECT b.child_id, n.qty * b.qty
            FROM needed_agg n JOIN bom b ON b.parent_id = n.part_id
        ) AS x(child_id, q)
        GROUP BY child_id
    )
SELECT part_id, qty FROM needed_agg ORDER BY part_id;
```

On the fixture this returns the same five rows as `needed`: wheel 2, frame 1,
spoke 64, tire 2, bolt 14.

The two are equivalent because the quantity of a part in the kit is the sum,
over the part's parents, of the parent's quantity times the edge quantity, plus
whatever the kit uses directly. Summing over paths and summing over parents
level by level are the same arithmetic, distributed differently. This form is
the better one to maintain: the binding holds one row per part, where `needed`
holds one row per path, and the number of paths grows exponentially with depth
in a wide BOM while the number of parts does not. It converges because a part's
row is final one iteration after all of its parents' rows are, and the DAG has
finitely many levels.

The guardrail from the previous section does not transfer, and this is worth
knowing before relying on it. On v26.38.1 a binding whose top level is an
aggregate does not trip `ERROR AT RECURSION LIMIT`; the block behaves like
`RETURN AT RECURSION LIMIT` and hands back whatever state it had reached. Run
`needed_agg` over the same self-containing data:

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 20)
    looped_bom(parent_id int, child_id int, qty int) AS (
        SELECT parent_id, child_id, qty
        FROM (VALUES (1, 2, 2), (2, 3, 3), (3, 2, 1)) AS v(parent_id, child_id, qty)
    ),
    needed_agg(part_id int, qty int) AS (
        SELECT child_id, sum(q)::int
        FROM (
            SELECT child_id, qty AS q FROM looped_bom WHERE parent_id = 1
            UNION ALL
            SELECT b.child_id, n.qty * b.qty
            FROM needed_agg n JOIN looped_bom b ON b.parent_id = n.part_id
        ) AS x(child_id, q)
        GROUP BY child_id
    )
SELECT part_id, qty FROM needed_agg ORDER BY part_id;
```

It returns part 2 at 59048 and part 3 at 177144, with no error. Those are not
answers; they are the running totals at iteration 20, and they get bigger if
the limit does. The `needed` form over the same data errors. So for an
aggregate-inside explosion, do not treat the limit as the safety net: keep a
cycle check standing next to it. The counter-free closure audit in
[hierarchies.md](hierarchies.md#cycles-in-a-tree) works on `bom` with
`parent_id` and `child_id` in place of `manager_id` and `id`, and it converges
on cyclic input, so it can alarm on exactly the data that would corrupt this
view.

Standard SQL brings nothing here. An aggregate in the recursive term is
forbidden, so a Postgres or SQL Server user has to explode the paths and group
afterwards, which is the `needed` form and its exponential intermediate. The
per-part loop is only available because WMR evaluates a fixpoint rather than a
queue
([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)).

## Kit cost

```sql
WITH MUTUALLY RECURSIVE
    needed_agg(part_id int, qty int) AS (
        SELECT child_id, sum(q)::int
        FROM (
            SELECT child_id, qty AS q FROM bom WHERE parent_id = 1
            UNION ALL
            SELECT b.child_id, n.qty * b.qty
            FROM needed_agg n JOIN bom b ON b.parent_id = n.part_id
        ) AS x(child_id, q)
        GROUP BY child_id
    )
SELECT sum(n.qty * p.unit_cost) AS kit_cost
FROM needed_agg n JOIN parts p ON p.id = n.part_id
WHERE p.unit_cost IS NOT NULL;
```

On the fixture this returns `73.4`: 64 spokes at 0.50, 14 bolts at 0.10, and 2
tires at 20.00. Materialize prints `numeric` without padding to a scale, so the
value shows as `73.4` rather than `73.40`; casting to `numeric(38,2)` does not
add the trailing zero either. Format currency in the client.

The costed join lives in the body, not in the binding. `unit_cost` never enters
the recursion, so the loop carries two `int` columns and the price list is read
once
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
Convergence is `needed_agg`'s: the body runs once, after the fixpoint.

`unit_cost IS NOT NULL` is a modeling decision, not a rounding one. Assemblies
in this fixture carry no price, so the sum is over purchased parts only. If
assemblies did carry a price it would double count, since the assembly's cost
already contains its children's.

Standard SQL brings the identical body; only the recursive part above it
differs, in the ways the previous two sections describe.

## Shared components: once or per path

The same subtree, counted two ways:

```sql
WITH MUTUALLY RECURSIVE
    under(part_id int) AS (
        SELECT child_id FROM bom WHERE parent_id = 1
        UNION
        SELECT b.child_id FROM under u JOIN bom b ON b.parent_id = u.part_id
    )
SELECT 'distinct parts' AS counting, count(*) AS n FROM under;

WITH MUTUALLY RECURSIVE
    under_paths(part_id int) AS (
        SELECT child_id FROM bom WHERE parent_id = 1
        UNION ALL
        SELECT b.child_id FROM under_paths u JOIN bom b ON b.parent_id = u.part_id
    )
SELECT 'paths' AS counting, count(*) AS n FROM under_paths;
```

On the fixture the first returns 5 and the second 6. Five distinct parts go
into a bike; there are six paths to them, because the bolt is reachable through
the wheel and through the frame. Both converge: `UNION` deduplicates and the
part set is finite, and `UNION ALL` terminates only because the BOM is a DAG
with finitely many paths, which is the assumption the previous sections had to
guard.

One of those numbers is the answer and the other is a bug, and which is which
depends on the question:

| Question | Operator | Because |
|---|---|---|
| How many distinct parts are in this product | `UNION` | A part is a thing, and it exists once |
| How many bolts do I have to buy | `UNION ALL` | Each use consumes its own bolts |
| Headcount under this manager | `UNION` | A person reporting into two teams is one person |
| Rolled-up cost of a shared subassembly | `UNION ALL` | Each occurrence is bought and paid for again |
| Total spend under a chart-of-accounts node | `UNION` | A posting must be counted once |

Org charts, permission graphs and charts of accounts want "once". Bills of
materials and effort estimates want "per path". A DAG makes the two different;
on a strict tree they agree, which is why the mistake survives testing on a
tree and shows up on real data.

Standard SQL brings exactly the same choice, and the same two operators mean
the same two things. What is different is the failure mode: in Postgres a
`UNION ALL` walk over a cyclic graph loops forever on its own work queue, and
in Materialize it fails to converge; neither gives you an answer, so `UNION`
plus a cycle audit is the safer default in both.

## Pitfalls

- Forgetting whether the node's own value is in or out. `team` includes it, so
  Bob's 605 is his own 200 plus his reports. For "everyone below me but not
  me", subtract in the body (`SELECT t.id, t.total - e.salary FROM team t JOIN
  employees e ON e.id = t.id`), not in the binding, where the subtraction would
  compound at every level.
- Using a tree rollup on DAG data. `needed`'s 14 bolts is correct because each
  use consumes bolts; the same shape over an org chart where someone reports to
  two managers counts that person twice at the top. Pick the operator from the
  "once or per path" table before writing the recursion.
- Trusting `ERROR AT RECURSION LIMIT` on an aggregate-topped binding. On
  v26.38.1 it does not fire; `needed_agg` over self-containing data returns
  iteration-20 numbers with no error, where the `needed` form raises. Guard
  aggregate rollups with a standing cycle audit as well as a limit.
- A plain `sum` where the rollup is signed. A chart of accounts with contra
  accounts, or an inventory with returns, signs the node's own amount inside
  the binding and adds the children's totals unchanged: `e.amount * e.sign +
  coalesce(sum(t.total), 0)` in the `team` shape. Signing the children's totals
  instead (`sum(t.total * e.sign)`) applies the sign again at every level
  below, so a contra account flips its whole subtree rather than its own
  amount, and flipping signs after the recursion has the same effect.
- `UNION` over a quantity-carrying binding. Two paths that happen to derive the
  same `(part_id, qty)` pair collapse into one and the total silently drops.
  Quantity rollups need `UNION ALL` and a cycle guard, never `UNION`.
- Carrying `name`, `unit_cost` or other payload through the loop. Recurse on
  ids and quantities and join the descriptions back in the body, as the kit
  cost block does.
- Assuming a rollup and a level query agree on the word "level". Depth counts
  from the root, height counts from the leaves, and Dee is at depth 2 and
  height 1.
