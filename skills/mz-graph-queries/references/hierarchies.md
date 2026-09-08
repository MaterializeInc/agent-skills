# Trees and hierarchies

Patterns for a parent-pointer table: everyone under a node, everyone above a
node, depth and root for every row, a closure table Materialize keeps up to
date for you, an indented ordered listing, and what to do when the "tree" turns
out to have a cycle in it. Read this file to answer: how do I get a subtree,
how do I get a management chain, how do I number levels, how do I make subtree
lookups cheap, how do I sort a tree for display, and how do I keep a bad parent
pointer from hanging a maintained view.

Fixture tables used: `employees`. Every block assumes `references/fixture.sql`
is loaded.

The fixture tree is Ada (1) over Bob (2) and Cy (3); Bob over Dee (4) and Eli
(5); Cy over Fay (6); Dee over Gus (7) and Hal (8).

## Descendants of one node

```sql
WITH MUTUALLY RECURSIVE
    subtree(id int) AS (
        SELECT id FROM employees WHERE manager_id = 2
        UNION
        SELECT e.id FROM employees e JOIN subtree s ON e.manager_id = s.id
    )
SELECT id FROM subtree ORDER BY id;
```

On the fixture this returns 4, 5, 7, 8: everyone under Bob.

It converges because `subtree` holds a set of ids drawn from `employees`, the
`UNION` makes re-deriving a row a no-op, and each iteration adds at most the
next level down. It runs one iteration per level below the seed, plus one
more that changes nothing and ends the loop.

Standard SQL brings the same shape: `WITH RECURSIVE subtree AS (SELECT id FROM
employees WHERE manager_id = 2 UNION ALL SELECT e.id FROM employees e JOIN
subtree s ON e.manager_id = s.id)`. What changes is `RECURSIVE` becoming
`MUTUALLY RECURSIVE`, the declared column list `subtree(id int)`, and `UNION
ALL` becoming `UNION`. Postgres tolerates `UNION ALL` here only because its
queue empties on a tree; on a cyclic manager chain it loops forever and so does
Materialize. `UNION` is the default for a reason
([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).

The seed filter `manager_id = 2` belongs inside the binding. Writing
`WHERE ... = 2` in the body instead computes every subtree and then throws
almost all of it away, because predicates are not pushed into a recursive
binding
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).

## Ancestors of one node

```sql
WITH MUTUALLY RECURSIVE
    chain(id int, distance int) AS (
        SELECT manager_id, 1 FROM employees WHERE id = 7 AND manager_id IS NOT NULL
        UNION
        SELECT e.manager_id, c.distance + 1
        FROM chain c JOIN employees e ON e.id = c.id
        WHERE e.manager_id IS NOT NULL
    )
SELECT id, distance FROM chain ORDER BY distance;
```

On the fixture this returns (4, 1), (2, 2), (1, 3): Gus reports to Dee, Dee to
Bob, Bob to Ada.

It converges because each iteration takes one step up a finite chain and the
`manager_id IS NOT NULL` guard stops the walk at the root. The `distance`
column is safe here only because the walk terminates. A cycle in `manager_id`
makes `distance` climb forever and the binding never converges, even under
`UNION`, since every trip around the loop produces a row nobody has seen
before. Put `ERROR AT RECURSION LIMIT` on any ancestor walk over data you do
not control; the counter-carrying closure block in the Cycles section below
is that failure.

Standard SQL brings the identical walk with `WITH RECURSIVE`. Nothing about the
logic changes; only the header, the declared types, and the union operator do.

## Depth and root for every node

```sql
WITH MUTUALLY RECURSIVE
    levels(id int, depth int, root_id int) AS (
        SELECT id, 0, id FROM employees WHERE manager_id IS NULL
        UNION
        SELECT e.id, l.depth + 1, l.root_id
        FROM employees e JOIN levels l ON e.manager_id = l.id
    )
SELECT id, depth, root_id FROM levels ORDER BY depth, id;
```

On the fixture this returns all eight rows with `root_id` 1 throughout: Ada at
depth 0, Bob and Cy at 1, Dee, Eli and Fay at 2, Gus and Hal at 3. The seed is
every root, not one root, so a forest works the same way and each node carries
the root it hangs from.

It converges because on a tree every node has exactly one parent and therefore
exactly one `(depth, root_id)` pair. Each iteration adds one level, and the
loop stops one iteration after the deepest level stops changing anything
([semantics.md#evaluation-model](semantics.md#evaluation-model)).

When the question is only "which top-level owner does this row belong to",
drop the counter and keep the binding two columns wide:

```sql
WITH MUTUALLY RECURSIVE
    rooted(id int, root_id int) AS (
        SELECT id, id FROM employees WHERE manager_id IS NULL
        UNION
        SELECT e.id, r.root_id FROM employees e JOIN rooted r ON e.manager_id = r.id
    )
SELECT root_id, count(*) AS members FROM rooted GROUP BY root_id ORDER BY root_id;
```

On the fixture this returns a single row, (1, 8): one root, eight people under
it counting Ada herself. On a forest there is one row per root, which is the
usual tenant or org attribution query. `rooted` is the safer of the two shapes
on data that is not strictly a tree: with no depth column, a node reachable by
two paths of different lengths still yields one row, where `levels` yields one
row per distinct depth.

"Level" here means depth measured down from the root. Height measured up from
the leaves is a different recursion, a `max` over children rather than a `+ 1`
from the parent; that one lives in `rollups.md`.

Standard SQL brings `WITH RECURSIVE levels AS (SELECT id, 0 AS depth, id AS
root_id FROM employees WHERE manager_id IS NULL UNION ALL ...)`. Beyond the
header and the type declarations, the change worth noting is `UNION`. On a
tree it removes nothing, because each node derives exactly once, and
consolidation runs either way. It is there for the day a parent pointer forms a
loop, when it is the difference between an answer and a query that never
finishes.

## A maintained closure table

```sql
CREATE VIEW employee_closure AS
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 1000)
    closure(ancestor int, descendant int, distance int) AS (
        SELECT id, id, 0 FROM employees
        UNION
        SELECT c.ancestor, e.id, c.distance + 1
        FROM closure c JOIN employees e ON e.manager_id = c.descendant
    )
SELECT ancestor, descendant, distance FROM closure;

CREATE INDEX employee_closure_by_ancestor ON employee_closure (ancestor);
```

```sql
SELECT descendant, distance FROM employee_closure WHERE ancestor = 2 ORDER BY distance, descendant;
```

On the fixture the read returns (2, 0), (4, 1), (5, 1), (7, 2), (8, 2): Bob at
distance 0 from himself, his two reports, then his two grandchildren.

It converges because on a tree every `(ancestor, descendant)` pair has exactly
one path and therefore exactly one `distance`, which is bounded by the height
of the tree. The pair set stops growing after height-plus-one iterations. Read
the `ERROR AT RECURSION LIMIT 1000` as a guardrail against data that is not a
tree, not as something the recursion needs to terminate.

This is the closure table from Karwin's *SQL Antipatterns*, the standard fix
for slow parent-pointer queries, except that nothing has to maintain it.
Elsewhere the closure rows are a second table kept in step by triggers or
application code, and every insert, move or delete has to fix them up. Here the
recursion is the maintenance job. The `CREATE INDEX` is what turns the view
into a maintained dataflow: with the index in place the closure is computed
once and kept up to date as `employees` changes, so a hire, a departure or a
reorg lands in it without any fixup code
([semantics.md#update-locality](semantics.md#update-locality)).

The index does two jobs. It maintains the closure, and it turns a subtree
question into a lookup instead of a scan:

```sql
EXPLAIN SELECT descendant, distance FROM employee_closure WHERE ancestor = 2;
```

The plan is `Explained Query (fast path)` over an `Index Lookup on ...
employee_closure (using ... employee_closure_by_ancestor)` with `Lookup values:
(2)`, which means the read is answered from the index arrangement. Plan text
changes between Materialize versions; this was produced on v26.38.1. Index the
column your questions filter on: `ancestor` for "who is under this node", a
second index on `descendant` for "who is above this node".

`ERROR AT RECURSION LIMIT 1000` is the guardrail, and it is not optional on a
maintained view. The `distance` column means one corrupt manager pointer that
closes a loop makes this recursion diverge; without a limit the view installs,
never hydrates, and keeps a dataflow spinning until it is dropped
([semantics.md#recursion-limits](semantics.md#recursion-limits)). Set the limit
well above the deepest chain you expect. The next section shows what it catches.

Standard SQL brings the same recursive query, usually run once to populate a
physical `employee_closure` table, plus the triggers that keep that table
correct. What changes is that the view is the table: you write the query and
delete the maintenance code.

## Ordered display with a path

```sql
WITH MUTUALLY RECURSIVE
    paths(id int, path text list) AS (
        SELECT id, LIST[name] FROM employees WHERE manager_id IS NULL
        UNION
        SELECT e.id, p.path || e.name
        FROM employees e JOIN paths p ON e.manager_id = p.id
    )
SELECT repeat('  ', list_length(path) - 1) || e.name AS tree, path
FROM paths p JOIN employees e USING (id)
ORDER BY path;
```

On the fixture this prints the tree in reading order: `Ada`, `  Bob`,
`    Dee`, `      Gus`, `      Hal`, `    Eli`, `  Cy`, `    Fay`. A `text
list` compares element by element, so ordering by the path is exactly a
pre-order walk, and `list_length` gives the indent.

It converges for the same reason `levels` does: one element is appended per
level and a tree has finitely many levels. The path column is as
divergence-prone as `distance`. A cycle makes the list grow without bound.

Siblings come out in name order because the path elements are names. For a
different sibling order, put the sort key in front of the element:

```sql
WITH MUTUALLY RECURSIVE
    paths(id int, path text list) AS (
        SELECT id, LIST[lpad(salary::text, 6, '0') || name]
        FROM employees WHERE manager_id IS NULL
        UNION
        SELECT e.id, p.path || (lpad(e.salary::text, 6, '0') || e.name)
        FROM employees e JOIN paths p ON e.manager_id = p.id
    )
SELECT repeat('  ', list_length(p.path) - 1) || e.name AS tree, e.salary
FROM paths p JOIN employees e USING (id)
ORDER BY p.path;
```

On the fixture this returns Ada, then Cy (190) before Bob (200), then under Bob
Eli (110) before Dee (120), and under Dee Hal (85) before Gus (90): siblings by
ascending salary, with the name appended as the tiebreak. The key is padded
because the comparison is textual. Note that only `id` and `path` recur; `name`
and `salary` for display are joined back in the body, which keeps the binding
narrow ([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).

Standard SQL brings the same trick, usually as a concatenated string path with
a separator character rather than a list, ordered with `ORDER BY path`. The
list form avoids the classic bug where a separator or a differing name length
makes the string sort disagree with the tree order.

## Cycles in a "tree"

Parent-pointer data goes wrong in one particular way: someone becomes their own
manager, directly or through a chain. These blocks use inline data so the
fixture stays a tree. In it 10 reports to 12, 12 reports to 11, and 11 reports
back to 10; 13 reports to 10 and is not on the loop.

```sql
WITH MUTUALLY RECURSIVE
    looped(id int, manager_id int) AS (
        SELECT id, manager_id FROM (VALUES (10, 12), (11, 10), (12, 11), (13, 10)) AS v(id, manager_id)
    ),
    subtree(id int) AS (
        SELECT id FROM looped WHERE manager_id = 10
        UNION
        SELECT l.id FROM looped l JOIN subtree s ON l.manager_id = s.id
    )
SELECT id FROM subtree WHERE id <> 10 ORDER BY id;
```

This returns 11, 12 and 13, and it terminates. The binding holds ids and nothing
else, so once the cycle has been walked around once every derivation repeats a
row `UNION` already deduplicated, and the loop stops. The `WHERE id <> 10` in
the body is there because the cycle genuinely makes 10 its own descendant; drop
it and 10 appears in its own subtree. `looped` is a non-recursive leading
binding, so it is computed once outside the loop.

The same query with `UNION ALL` never converges:

<!-- verify: error -->

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 20)
    looped(id int, manager_id int) AS (
        SELECT id, manager_id FROM (VALUES (10, 12), (11, 10), (12, 11), (13, 10)) AS v(id, manager_id)
    ),
    subtree(id int) AS (
        SELECT id FROM looped WHERE manager_id = 10
        UNION ALL
        SELECT l.id FROM looped l JOIN subtree s ON l.manager_id = s.id
    )
SELECT id FROM subtree WHERE id <> 10;
```

`ERROR:  Evaluation error: Recursive query exceeded the recursion limit 20.`
Every trip around the cycle adds another copy of each id, so the row counts
grow forever even though the distinct ids settled after three iterations. The
limit is what makes it visible; without one the statement runs until cancelled.

A column that counts, such as `distance` or a path, diverges even under
`UNION`. This is the closure binding from the previous section run over the
looped data:

<!-- verify: error -->

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 20)
    looped(id int, manager_id int) AS (
        SELECT id, manager_id FROM (VALUES (10, 12), (11, 10), (12, 11), (13, 10)) AS v(id, manager_id)
    ),
    closure(ancestor int, descendant int, distance int) AS (
        SELECT manager_id, id, 1 FROM looped
        UNION
        SELECT c.ancestor, l.id, c.distance + 1
        FROM closure c JOIN looped l ON l.manager_id = c.descendant
    )
SELECT ancestor, descendant, distance FROM closure;
```

`ERROR:  Evaluation error: Recursive query exceeded the recursion limit 20.`
Each lap produces the same pair at a new distance, and a new distance is a new
row that `UNION` cannot fold away. This is exactly the failure that
`ERROR AT RECURSION LIMIT 1000` on `employee_closure` converts from a
never-hydrating view into a visible error.

Audit the data with a closure that carries no counter, so it converges on
cyclic input, and ask which nodes are their own ancestor:

```sql
WITH MUTUALLY RECURSIVE
    looped(id int, manager_id int) AS (
        SELECT id, manager_id FROM (VALUES (10, 12), (11, 10), (12, 11), (13, 10)) AS v(id, manager_id)
    ),
    closure(ancestor int, descendant int) AS (
        SELECT manager_id, id FROM looped
        UNION
        SELECT c.ancestor, l.id FROM closure c JOIN looped l ON l.manager_id = c.descendant
    )
SELECT descendant AS id FROM closure WHERE ancestor = descendant ORDER BY id;
```

This returns 10, 11, 12: the three nodes on the loop. 13 hangs off the loop but
is not on it, so it is not its own ancestor. The seed is the direct edges
rather than `(id, id, 0)`, which is what makes `ancestor = descendant` mean
"there is a cycle" instead of "this is the reflexive row". Run this as a
maintained view over real parent-pointer data and it is a standing corruption
alarm.

Standard SQL brings `WITH RECURSIVE ... CYCLE id SET is_cycle USING path` in
Postgres 14 and later, or a manual `path` array with a
`NOT path @> ARRAY[id]` guard before that. Materialize has neither; the
`RECURSIVE` keyword itself is not accepted, so `WITH RECURSIVE t(id) AS ...`
fails to parse. Use `UNION` over a counter-free binding when you only need the
reachable set, and a recursion limit when you need to carry a counter.

## Pitfalls

- A `depth`, `distance` or path column in a binding over anything but a tree.
  On a DAG a node reachable by paths of different lengths appears once per
  distinct length: with edges 1 to 2, 2 to 4 and 1 to 4, the `levels` shape
  yields both `(4, 1)` and `(4, 2)`. On a cycle it never converges at all.
  Aggregate the counter with `min` if you want one row per node.
- No recursion limit on a maintained view that carries a counter. One bad
  parent pointer and the view installs, never hydrates, and holds a dataflow
  until dropped.
- Orphans. A row whose `manager_id` points at a missing id is under no root, so
  seeding from `manager_id IS NULL` silently omits it and everything below it.
  Check with `SELECT count(*) FROM employees e WHERE e.manager_id IS NOT NULL
  AND NOT EXISTS (SELECT 1 FROM employees m WHERE m.id = e.manager_id)` before
  trusting a level or path query.
- Filtering the subtree in the body instead of the seed. The predicate is not
  pushed into the binding, so the recursion still expands every node.
- Carrying `name`, `salary` or other payload through the loop. Every declared
  column stays live in the arrangement across every iteration. Recurse on ids
  and join the payload back in the body, as both display blocks do.
- Assuming a plain `CREATE VIEW` is maintained. Without an index it is not
  computed at all until something reads it, and then it is recomputed from
  scratch: a view is a named query, and the index is what makes it a standing
  dataflow. Materializing the closure means creating the index (or a
  materialized view).
- Filtering an indexed closure on the column the index does not cover. With
  `employee_closure_by_ancestor` in place, `WHERE ancestor = 2` is a lookup but
  `WHERE descendant = 7` is a scan of the whole closure. Index each column you
  ask about.
