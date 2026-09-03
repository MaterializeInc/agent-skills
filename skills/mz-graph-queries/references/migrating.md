# Migrating recursive SQL to WMR

How to port a recursive query written for another engine. Read this file to
answer: what does `WITH RECURSIVE` become, when does `UNION ALL` have to become
`UNION`, where does `MAXRECURSION` go, what replaces the `CYCLE` clause and the
visited-array guard, how does Oracle's `CONNECT BY` decompose into a seed and a
join, what does DuckDB's `USING KEY` correspond to, and which habits from those
dialects are silently wrong here rather than loudly rejected.

Fixture tables used: `employees`, `transfers`, `roads`, `customers`,
`customer_links`. Every block assumes `references/fixture.sql` is loaded.

Every query below that is not Materialize SQL is fenced as another dialect and
is not run; it is there to be read against the Materialize block that follows.
Every Materialize block is verified on the fixture. Each translation is a
pattern that already lives in another file of this skill, quoted here in its
verbatim form, so the migration answer and the reference answer cannot drift
apart.

## Translation table

| Elsewhere | Here |
|---|---|
| `WITH RECURSIVE name AS (anchor UNION ALL recursive)` | `WITH MUTUALLY RECURSIVE name(col type, ...) AS (anchor UNION recursive)` |
| `UNION ALL` between the two terms | `UNION`, unless every row derives exactly once |
| No column type declaration | A declared name and type per column, mandatory ([semantics.md#column-types](semantics.md#column-types)) |
| `OPTION (MAXRECURSION n)` (SQL Server), `cte_max_recursion_depth` (MySQL), BigQuery's 500-iteration cap | `ERROR AT RECURSION LIMIT n` when the binding is topped by a `UNION`; `RETURN AT RECURSION LIMIT n` plus a check on the result when it is topped by a reduce ([semantics.md#recursion-limits](semantics.md#recursion-limits)) |
| `CYCLE col SET is_cycle USING path`, a hand-rolled `path \|\| id` with `NOT id = ANY(path)`, Oracle's `NOCYCLE` | Nothing, when the binding carries no counter. `min(depth)` inside the binding when a depth is wanted |
| `WHERE depth < k` written as a cycle guard | Drop it |
| `WHERE depth < k` written as a real hop bound | Keep it, inside the binding |
| `LEVEL` | A `depth` column, seeded at 1 to match Oracle |
| `CONNECT_BY_ROOT col` | A root column carried unchanged from the seed |
| `SYS_CONNECT_BY_PATH(col, '/')` | A `text list` path, `LIST[col]` in the seed and `path \|\| col` in the step |
| `ORDER SIBLINGS BY col` | `ORDER BY path` in the body, with `col` inside the path element |
| `START WITH pred CONNECT BY PRIOR id = parent_id` | The seed branch's `WHERE pred`, and the recursive branch's join |
| A bare `ORDER BY` at the end of the recursive term (SQLite's breadth-first or depth-first knob) | Nothing. Order the body |
| `ORDER BY ... LIMIT` in the recursive term (top-k per node, which standard SQL forbids) | Keep it. It plans as a TopK and the loop honors it |
| DuckDB `USING KEY (k)` reading `recurring.<cte>` | An aggregate or `DISTINCT ON` inside the binding, keyed on the same columns |
| A window function meant as "rank within this level" | An aggregate inside the binding, and a level column if the level is needed |
| Enumerate every path, then `MIN`, `MAX` or `SUM` in the outer query | The same aggregate inside the binding, recursing from the reduced relation |

Two things in that table are absences rather than translations. There is no
default recursion limit here, so a query that relied on SQL Server's implicit
100, MySQL's 1000 or BigQuery's 500 to stop is a query that now runs until it
is cancelled; write the limit yourself. And there is no `RECURSIVE` keyword at
all, which is the subject of the next section.

## Anchor and recursive member

The Postgres shape, everyone under Bob:

```postgresql
WITH RECURSIVE subtree AS (
    SELECT id FROM employees WHERE manager_id = 2
  UNION ALL
    SELECT e.id FROM employees e JOIN subtree s ON e.manager_id = s.id
)
SELECT id FROM subtree ORDER BY id;
```

Pasted unchanged, that does not reach the planner. Materialize has no
`RECURSIVE` keyword, so the parser reads `RECURSIVE` as the name of an ordinary
CTE and then expects `AS`.

<!-- verify: error -->

```sql
WITH RECURSIVE subtree AS (
    SELECT id FROM employees WHERE manager_id = 2
  UNION ALL
    SELECT e.id FROM employees e JOIN subtree s ON e.manager_id = s.id
)
SELECT id FROM subtree ORDER BY id;
```

`ERROR:  Expected AS, found SUBTREE`. The caret points at the CTE name, which
makes the message look like a syntax error in the name rather than a missing
feature. It is the latter: `RECURSIVE` is not a keyword here, so the parser
takes it for the CTE's name and then wants `AS` where `subtree` is.

The translation is
[hierarchies.md#descendants-of-one-node](hierarchies.md#descendants-of-one-node):

```sql
WITH MUTUALLY RECURSIVE
    subtree(id int) AS (
        SELECT id FROM employees WHERE manager_id = 2
        UNION
        SELECT e.id FROM employees e JOIN subtree s ON e.manager_id = s.id
    )
SELECT id FROM subtree ORDER BY id;
```

On the fixture this returns 4, 5, 7, 8: Dee, Eli, Gus and Hal. It converges
because the binding holds a set of ids drawn from `employees`, `UNION` makes
re-deriving a row a no-op, and each iteration adds at most the next level down.

Three edits turn one query into the other.

1. **`MUTUALLY RECURSIVE`, with declared column types.** `subtree(id int)` is
   mandatory, the columns are nullable, and each branch is coerced to the
   declared type with an assignment cast rather than an explicit one
   ([semantics.md#column-types](semantics.md#column-types)). A bare `SELECT
   NULL` or `SELECT '1'` types as `text` and fails against any other declared
   type before the recursion runs.
2. **`UNION ALL` becomes `UNION`.** Postgres tolerates `UNION ALL` here only
   because its working table empties on a tree. A binding is a multiset, and
   convergence means no row's count changed, so a `UNION ALL` that re-derives a
   row it already holds never settles
   ([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).
   Keep `UNION ALL` only where every row derives exactly once.
3. **No restriction on where the binding is referenced.** Postgres permits
   exactly one reference to the recursive CTE, in `FROM`, not inside a
   subquery, and not on the nullable side of an outer join. WMR has none of
   those rules
   ([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)).
   That matters most in reverse: a source query split across three CTEs to
   satisfy the linear-recursion rule usually collapses back into one binding,
   and the workaround is the part to delete.

A fourth change is invisible in this example, and it is the usual porting bug.
The seed filter `manager_id = 2` must stay inside the binding. Predicates are
not pushed into a recursive binding, so a source query that filtered in its
outer `SELECT` becomes a query that expands every subtree and throws almost all
of it away
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).

## Depth guards

A cycle-safe Postgres traversal carries two extra columns. This is the
hand-rolled form; Postgres 14's `CYCLE dst SET is_cycle USING path` generates
exactly these two columns for you.

```postgresql
WITH RECURSIVE hops(dst, depth, path, is_cycle) AS (
    SELECT dst, 1, ARRAY['a1', dst], false
    FROM transfers WHERE src = 'a1'
  UNION ALL
    SELECT t.dst, h.depth + 1, h.path || t.dst, t.dst = ANY(h.path)
    FROM hops h JOIN transfers t ON t.src = h.dst
    WHERE NOT h.is_cycle AND h.depth < 3
)
SELECT dst, MIN(depth) AS hops
FROM hops
WHERE NOT is_cycle AND dst <> 'a1'
GROUP BY dst
ORDER BY 2, 1;
```

The translation is
[reachability.md#within-k-hops](reachability.md#within-k-hops):

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

On the fixture this returns (a2, 1), (a3, 2), (a4, 3). a1 is dropped in the
body because the ring makes it its own three-hop neighbor; a5 is four hops out.
It converges because the binding holds one row per `dst`, `min` can only lower
a value, and the `WHERE h.hops < 3` guard stops production after three rounds.

Of the four devices in the source query, one survives, two disappear and one
moves.

| Source device | Fate |
|---|---|
| `WHERE h.depth < 3` | Survives, and stays inside the binding. It is a real hop bound: the question is "within three hops" |
| `path` and `t.dst = ANY(h.path)` | Gone. `min` inside the binding keeps one row per `dst`, and a lap around the ring can only offer that key a value that is not lower, which `min` discards |
| `is_cycle` | Gone with the path it was computed from |
| `MIN(depth)` in the outer query | Moves inside the binding, which is what makes the row set one per node ([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)) |

The `min` and the cycle guard are the same device, not two. Without `min`, a
node reached at two lengths is two rows and the ring produces a new number
every lap, which is exactly the divergence the visited array was written to
prevent. With `min` inside the binding, removing the hop bound entirely still
converges on this cyclic fixture and returns the full shortest hop count, a5
included, because a value that only descends toward a floor cannot cycle
forever.

That is why the two uses of `WHERE depth < k` translate differently. Written as
a cycle guard, with a number nobody can justify, it is dead weight: delete it.
Written as a hop bound, with a number the question supplied, it is the thing
keeping the loop finite, and it belongs inside the binding rather than in the
body.

Do not replace the deleted guard with `ERROR AT RECURSION LIMIT`. This binding
is topped by a reduce, and the limit tracks changes to the row set rather than
to values, so it goes quiet once every key has a row while the numbers are
still moving
([semantics.md#recursion-limits](semantics.md#recursion-limits)). The hop guard
is what makes this query safe.

## Oracle CONNECT BY

An Oracle hierarchy query with the whole vocabulary in it:

```postgresql
SELECT LEVEL,
       id,
       CONNECT_BY_ROOT id            AS root_id,
       SYS_CONNECT_BY_PATH(name, '/') AS path
FROM   employees
START WITH manager_id IS NULL
CONNECT BY NOCYCLE PRIOR id = manager_id
ORDER SIBLINGS BY name;
```

`CONNECT BY` has no separate anchor and recursive member; `START WITH` supplies
the roots and `CONNECT BY PRIOR` supplies the step. Splitting those two clauses
into the two branches of a union is most of the translation, and it combines
the `levels` binding from
[hierarchies.md#depth-and-root-for-every-node](hierarchies.md#depth-and-root-for-every-node)
with the path list from
[hierarchies.md#ordered-display-with-a-path](hierarchies.md#ordered-display-with-a-path):

```sql
WITH MUTUALLY RECURSIVE
    tree(id int, depth int, root_id int, path text list) AS (
        SELECT id, 1, id, LIST[name] FROM employees WHERE manager_id IS NULL
        UNION
        SELECT e.id, t.depth + 1, t.root_id, t.path || e.name
        FROM employees e JOIN tree t ON e.manager_id = t.id
    )
SELECT id, depth AS level, root_id, path FROM tree ORDER BY path;
```

On the fixture this returns all eight employees in reading order, Ada first at
level 1 with the path `{Ada}`, then Bob, Dee, Gus, Hal, Eli, Cy, Fay. Every row
carries `root_id` 1. It converges because on a tree every node has exactly one
parent and therefore one `(depth, root_id, path)` triple, so each iteration
adds one level and the loop stops one iteration after the deepest.

Clause by clause:

| Oracle | Here |
|---|---|
| `START WITH manager_id IS NULL` | The seed branch's `WHERE manager_id IS NULL` |
| `CONNECT BY PRIOR id = manager_id` | `JOIN tree t ON e.manager_id = t.id` in the recursive branch |
| `LEVEL` | The `depth` column. Oracle starts it at 1, so the seed says `1`, not `0` |
| `CONNECT_BY_ROOT id` | `root_id`, set to `id` in the seed and copied unchanged in the step |
| `SYS_CONNECT_BY_PATH(name, '/')` | `path text list`, `LIST[name]` then `path \|\| e.name` |
| `ORDER SIBLINGS BY name` | `ORDER BY path` in the body |
| `NOCYCLE` | Nothing, and that is the dangerous row. See below |

Four details are worth more than a table row.

**The root column is a choice of attribute, not a fixed thing.**
`CONNECT_BY_ROOT` can be applied to any column, and here it is any column you
copy from the seed unchanged. `root_id` is the common one; `CONNECT_BY_ROOT
name` is the same edit with `name` in the seed instead of `id`.

**`ORDER SIBLINGS BY` is `ORDER BY path`, and the sibling key lives in the path
element.** A `text list` compares element by element, so ordering by the path is
a pre-order walk and siblings come out in the order of whatever the path
elements sort by. `LIST[name]` gives sibling order by name, which is what the
Oracle query asked for. To sort siblings by something else, put the sort key in
front of the element, as the salary variant in
[hierarchies.md#ordered-display-with-a-path](hierarchies.md#ordered-display-with-a-path)
does. Note also that the list form has no separator: the classic
`SYS_CONNECT_BY_PATH` bug, where a name containing the separator character
makes the string sort disagree with the tree order, cannot happen.

**`NOCYCLE` translates to nothing, and this particular block still needs a
guard.** Elsewhere in this skill the answer to a cycle clause is "carry no
counter and `UNION` handles it". That answer does not apply here, because this
binding carries both a `depth` and a `path`. On a manager pointer that closes a
loop, every lap produces a new depth and a longer path, which are new rows that
`UNION` cannot fold away, and the recursion never converges
([hierarchies.md#cycles-in-a-tree](hierarchies.md#cycles-in-a-tree)). Put
`ERROR AT RECURSION LIMIT` on this shape whenever the data is not guaranteed to
be a tree. It works here: the binding is topped by a `UNION`, so every change it
can make is a row change and the limit always raises
([semantics.md#recursion-limits](semantics.md#recursion-limits)). Where the
question is only "which nodes are on a loop", the counter-free audit in
[reachability.md#cycle-membership](reachability.md#cycle-membership) is the
translation of `CONNECT_BY_ISCYCLE`, and it converges on exactly the data that
breaks this block.

**On a graph that is not a tree, both dialects give you one row per path.** A
node with two parents appears twice under `CONNECT BY` and twice here, once per
distinct `(depth, root_id, path)`. If one row per node is wanted, drop the path,
aggregate the depth with `min`, and accept that the two questions are different.

## DuckDB USING KEY and the enumerate-then-aggregate habit

DuckDB 1.3 added `USING KEY` to recursive CTEs. The intermediate result becomes
a keyed table rather than a growing set: inside the recursive term the CTE name
denotes the rows the last iteration added, and `recurring.<cte>` denotes the
accumulated table, so a step can look up what is already known for a key and
decline to produce anything worse. This is the distance-vector routing shape
from DuckDB's own write-up, reduced to a single source over the road network:

```postgresql
WITH RECURSIVE
    sym(src, dst, km) AS (
        SELECT src, dst, km FROM roads
        UNION ALL
        SELECT dst, src, km FROM roads
    ),
    dist(city, km) USING KEY (city) AS (
        SELECT 'A' AS city, 0 AS km
      UNION
        (SELECT s.dst AS city, d.km + s.km AS km
         FROM dist AS d                     -- working table: last iteration's updates
         JOIN sym AS s ON s.src = d.city
         LEFT JOIN recurring.dist AS rec    -- recurring table: the answer so far
           ON rec.city = s.dst
         WHERE d.km + s.km < coalesce(rec.km, 'Infinity'::DOUBLE)
         ORDER BY km)
    )
SELECT city, km FROM dist WHERE city <> 'A' ORDER BY km;
```

The translation is [shortest-paths.md#cheapest-route](shortest-paths.md#cheapest-route):

```sql
WITH MUTUALLY RECURSIVE
    sym(src text, dst text, km int) AS (
        SELECT src, dst, km FROM roads
        UNION ALL
        SELECT dst, src, km FROM roads
    ),
    dist(city text, km int) AS (
        SELECT city, min(km)
        FROM (
            SELECT 'A', 0
            UNION ALL
            SELECT s.dst, d.km + s.km
            FROM dist d JOIN sym s ON s.src = d.city
        ) AS x(city, km)
        GROUP BY city
    )
SELECT city, km FROM dist WHERE city <> 'A' ORDER BY km, city;
```

On the fixture this returns (B, 4), (C, 7), (D, 9), (E, 14). It converges
because the binding holds one row per city, `min` can only lower a value, and
positive weights put a floor under it.

The two queries are the same algorithm with the keyed state expressed
differently. `GROUP BY city` with `min(km)` is the key declaration and the
merge rule in one: the group key is DuckDB's `USING KEY (city)`, and `min` is
what the `LEFT JOIN recurring.dist ... WHERE new < coalesce(rec.km, inf)` test
was doing by hand. Three things fall out of the source query as a result. The
explicit improvement test goes, because `min` keeps the better value anyway.
The two-relation split between `dist` and `recurring.dist` goes, because there
is only one relation here, the binding's current value. And the `ORDER BY km`
inside the term goes, because it carries no `LIMIT` and a bare `ORDER BY` has
no evaluation-order meaning here.

Where the answer needs the route and not only the cost, the argmin form in
[shortest-paths.md#one-witness-path](shortest-paths.md#one-witness-path) uses
`DISTINCT ON (city) ... ORDER BY city, km` instead of `min(km)`, which keeps the
predecessor column alongside the winning value. That is the closer match to
`USING KEY` with payload columns.

**Enumerate, then aggregate.** Most recursive SQL in the wild has this shape
because standard SQL leaves no
alternative: walk everything, then reduce in the outer query. The canonical
connected-components recipe is the "parallel walks" shape, written up by Max
Halford in *Graph components with DuckDB* and credited there to a tutorial by
Torsten Grust. It is the same enumerate-then-aggregate move:

```postgresql
WITH RECURSIVE
    edges(src, dst) AS (
        SELECT a, b FROM customer_links WHERE score >= 0.5
        UNION
        SELECT b, a FROM customer_links WHERE score >= 0.5
    ),
    walks(node, front) AS (
        SELECT id, id AS front FROM customers
      UNION
        SELECT walks.node, edges.dst AS front
        FROM walks, edges
        WHERE walks.front = edges.src
    )
SELECT node, MIN(front) AS component
FROM walks
GROUP BY node
ORDER BY component, node;
```

The translation is
[components.md#connected-components-by-min-label-propagation](components.md#connected-components-by-min-label-propagation):

```sql
WITH MUTUALLY RECURSIVE
    links(a text, b text) AS (
        SELECT a, b FROM customer_links WHERE score >= 0.5
        UNION
        SELECT b, a FROM customer_links WHERE score >= 0.5
    ),
    label(id text, comp text) AS (
        SELECT id, min(comp)
        FROM (
            SELECT id, id FROM customers
            UNION ALL
            SELECT l.b, lb.comp
            FROM links l JOIN label lb ON lb.id = l.a
        ) AS x(id, comp)
        GROUP BY id
    )
SELECT id, comp FROM label ORDER BY id;
```

On the fixture this returns c1, c2 and c3 labelled c1; c4 and c5 labelled c4;
c6 labelled c6; c7 labelled c7. It converges because the row set is one row per
node from the first iteration and a node's label never rises.

Both queries return the same labels. The difference is the intermediate.
`walks` holds one row per (node, reachable node) pair, so a component of k
nodes costs k squared rows before the aggregate runs. `label` holds one row per
node throughout, because the recursive branch reads `label`, which is already
reduced.

That is the general rule, and it is the single edit that most often turns a
ported query from unusable into a maintainable view. **Whatever the outer
aggregate was, move it inside the binding and recurse from the reduced
relation.**

The move is mechanical: wrap the union of the seed branch and the recursive
branch in a derived table, put the `GROUP BY` and the aggregate around it, and
let the recursive branch read the binding rather than the raw walk. `min` for a
shortest distance or a component label, `max` for a topological level
([reachability.md#topological-level-on-a-dag](reachability.md#topological-level-on-a-dag)),
`sum` for a bill of materials
([rollups.md#the-same-with-the-aggregate-inside](rollups.md#the-same-with-the-aggregate-inside)),
`DISTINCT ON` when the row that achieved the extremum is wanted and not only
the value.

It is not free. A binding topped by a reduce is the shape `ERROR AT RECURSION
LIMIT` cannot police, because the limit tracks changes to the row set and a
reduce settles its keys long before its values
([semantics.md#recursion-limits](semantics.md#recursion-limits)). Whatever
made the source query terminate has to be replaced by an argument, not by a
limit: `min` over positive weights descends to a floor, a hop bound stops
production outright, a DAG has finitely many levels. Each pattern file states
its own.

## Semantics that differ silently

These are the differences that produce a query which runs and is wrong, or runs
and never stops, rather than one that fails to parse.

- **A binding is a multiset, and convergence counts multiplicities.** Postgres
  drives `WITH RECURSIVE` from a working table that empties, so `UNION ALL`
  terminates on a tree and loops forever only on a cycle. Here "nothing
  changed" means no row's count changed, so a `UNION ALL` that re-adds rows the
  binding already holds never converges even on acyclic data. The distinct rows
  settle and look correct under `RETURN AT RECURSION LIMIT` while the counts
  climb
  ([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).
- **The recursive term reads the whole binding, not the last iteration's new
  rows.** Postgres's recursive term sees only the working table, and DuckDB's
  `USING KEY` splits the two apart explicitly as `<cte>` and `recurring.<cte>`.
  Here there is one relation and it is the binding's current value
  ([semantics.md#evaluation-model](semantics.md#evaluation-model)). A step
  written to assume "only what is new" re-derives rows the binding already
  holds: under `UNION` that is a no-op, and under `UNION ALL` it is the first
  bullet. A step written to assume "everything so far" was not expressible in
  the source dialect and is expressible here. The one place last iteration's
  value is readable is a binding defined later in the list, which is the delay
  idiom
  ([semantics.md#binding-order-and-the-delay-idiom](semantics.md#binding-order-and-the-delay-idiom)).
- **Aggregates and window functions apply to the whole binding, not to "the
  current level".** There is no level unless a column says so, and the block
  below shows what that costs a ported query. Carry a `depth` column and
  partition by it if per-level ranking is what the source query meant.
- **There is no linear-recursion rule to work around.** One reference to the
  recursive relation, no subquery over it, no outer join with it on the nullable
  side, no aggregate, no `DISTINCT`, no `ORDER BY ... LIMIT`: none of those
  restrictions exist here
  ([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)).
  Read a source query's contortions as evidence of the rule rather than as
  logic, and delete them. Path doubling, `NOT EXISTS` over the binding, and
  several mutually dependent relations are all writable directly.
- **Nothing deduplicates implicitly.** Feldera compiles every mutually
  recursive view as if it had `SELECT DISTINCT`, precisely so that duplicate
  rows cannot make it grow forever. WMR does not: the only deduplication is the
  one you write, as `UNION`, `SELECT DISTINCT`, or an aggregate. A recursive
  view ported from an engine with set semantics needs that `DISTINCT` supplied
  by hand, and the symptom of forgetting is the first bullet.

The window-function bullet is the one worth seeing run. This binding walks the
fixture tree and numbers its rows:

```sql
WITH MUTUALLY RECURSIVE
    walk(id int, depth int, rn bigint) AS (
        SELECT id, depth, row_number() OVER (ORDER BY id)
        FROM (
            SELECT id, 0 AS depth FROM employees WHERE manager_id IS NULL
            UNION
            SELECT e.id, w.depth + 1 FROM employees e JOIN walk w ON e.manager_id = w.id
        ) AS x(id, depth)
    )
SELECT id, depth, rn FROM walk ORDER BY id;
```

On the fixture this returns the eight employees with `rn` running 1 through 8
in id order, Ada at depth 0 and Gus and Hal at depth 3. A per-level numbering
would restart at every level: 1 for Ada, then 1 and 2 for Bob and Cy. It
converges because the row set settles after four iterations and the window is
then computed over a relation that no longer changes. Read it as a
demonstration rather than a pattern: a window over a binding whose rows are
still arriving has no meaning until the fixpoint, so anything you want to be
per-level has to come from a column you carry.

## Pitfalls

- Porting `UNION ALL` unchanged because the source query terminated. It
  terminated under a different evaluation model. Change it to `UNION` unless
  you can name the reason every row derives exactly once.
- Translating `MAXRECURSION` or `cte_max_recursion_depth` into `ERROR AT
  RECURSION LIMIT` on a binding topped by a reduce. The limit stops the loop
  and returns the iteration-n state without raising, so the query serves
  running counters as if they were answers
  ([semantics.md#recursion-limits](semantics.md#recursion-limits)).
- Deleting the depth guard along with the cycle guard. They look identical and
  they are not: one exists because the source dialect had no other way to stop
  a walk, the other is the question's own bound.
- Keeping the `path` array after moving the aggregate inside. It no longer
  guards anything, it is the widest column in the binding, and it is
  re-arranged every iteration
  ([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
- Leaving the outer filter in the outer query. `WHERE id = ...` in the body of
  a WMR query prunes nothing; the recursion has already expanded everything.
  Seed filters and edge filters belong inside the binding.
- Assuming `LEVEL` and a `depth` column agree. Oracle's `LEVEL` starts at 1 and
  the `levels` pattern in this skill starts at 0. Pick one and say which in the
  column name.
- Porting an Oracle query with `NOCYCLE` and no recursion limit. `NOCYCLE`
  stopped the walk; nothing here does, and a binding carrying a depth or a path
  diverges on the first loop in the data
  ([hierarchies.md#cycles-in-a-tree](hierarchies.md#cycles-in-a-tree)).
- Dropping an `ORDER BY` from the recursive term without checking for a
  `LIMIT`. A bare one is inert, because SQLite's queue order has no counterpart
  in a fixpoint; order the body instead. `ORDER BY ... LIMIT` is a different
  thing: it plans as a TopK, the loop honors it, and a top-k-per-node query
  needs it. On the fixture, the `levels` binding with
  `(SELECT ... ORDER BY 1 LIMIT 1)` as its recursive branch returns 2 rows
  instead of 8.
- Translating a query without translating the deployment. Most of these source
  queries are batch jobs or per-request expansions. The reason to port one is
  usually an indexed view or a materialized view that stays current, and that
  choice changes which form to prefer: an enumerate-then-aggregate shape is a
  one-shot form, and the reduced-binding form is the one to maintain. The same
  split applies to the path-doubling closure
  ([reachability.md#whole-graph-closure](reachability.md#whole-graph-closure)).
