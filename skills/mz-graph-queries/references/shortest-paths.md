# Shortest paths

Patterns over a weighted, undirected road network: how far away every city is
in hops, how far away it is in kilometres, one concrete route that achieves the
cheapest distance, and the same distance asked for a single destination. Read
this file to answer: how many hops is it from here to there, what is the
cheapest route and what does it cost, which roads does that route actually use,
why is the two-hop way more expensive than the three-hop way, and why does
filtering to one target not make the query cheaper.

Fixture tables used: `roads`. Every block assumes `references/fixture.sql` is
loaded. The node table `cities` is not read by any block below, because every
city in this fixture is reachable from the seed; it is what you left-join
against when that is not true.

`roads` stores each road once, in one direction: (A, B, 4), (B, C, 3),
(A, C, 10), (C, D, 2), (B, D, 8), (D, E, 5). Driving is not one-way, so every
block below symmetrizes first. The interesting fact in this data is D: it is
two hops from A along A to B to D, and that way costs 12 km, while the cheapest
way costs 9 km and takes three hops, A to B to C to D. Hop count and distance
are different questions with different answers on the same graph.

## Symmetrize once

Every block starts with the same non-recursive binding.

<!-- verify: skip -->

```sql
    sym(src text, dst text, km int) AS (
        SELECT src, dst, km FROM roads
        UNION ALL
        SELECT dst, src, km FROM roads
    ),
```

`sym` has no self-reference, so it contributes nothing to the loop and cannot
affect convergence. It is also computed once rather than per iteration: a
non-recursive binding at the head of the list is hoisted out of the recursive
block
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
That is the reason to write it as a leading binding instead of repeating the
`UNION ALL` inside the recursive term.

`UNION ALL` is right here because `roads` holds each road once. If the source
table might already hold both directions, use `UNION`, or the duplicate edge is
joined against twice every iteration for the same answer.

Skipping this step is the most common way to get a wrong answer that looks
right. The fixture's roads all happen to point away from A, so an unsymmetrized
query seeded at A returns the same distances as the symmetrized one and hides
the bug. Seed the same unsymmetrized query at E and it returns only E itself,
because no road in the table points out of E.

Standard SQL brings the identical union, written as a plain non-recursive CTE
ahead of the `WITH RECURSIVE` term. What changes is only that it moves into the
same binding list and declares its column types.

## Fewest hops

```sql
WITH MUTUALLY RECURSIVE
    sym(src text, dst text, km int) AS (
        SELECT src, dst, km FROM roads
        UNION ALL
        SELECT dst, src, km FROM roads
    ),
    hops(city text, hops int) AS (
        SELECT city, min(hops)
        FROM (
            SELECT 'A', 0
            UNION ALL
            SELECT s.dst, h.hops + 1
            FROM hops h JOIN sym s ON s.src = h.city
        ) AS x(city, hops)
        GROUP BY city
    )
SELECT city, hops FROM hops WHERE city <> 'A' ORDER BY hops, city;
```

On the fixture this returns (B, 1), (C, 1), (D, 2), (E, 3). The binding also
holds (A, 0), the seed, and the body drops it. `min` is why that row stays at
zero: the symmetrized graph makes A its own two-hop neighbour, and the
aggregate keeps the smaller of the two.

It converges because the binding holds one row per city, `min` can only lower a
city's value, and the values are bounded below by zero. There is no cycle guard
and none is needed: a quantity that only descends toward a floor cannot go
round a loop forever
([semantics.md#evaluation-model](semantics.md#evaluation-model)).

The `min` is inside the binding, and the recursion reads `hops`, which is the
reduced relation. Only the current minimum for a city is ever extended, so the
binding is one row per city rather than one row per walk. Move the aggregate to
the body and the loop has nothing left to collapse it:

<!-- verify: error -->

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 20)
    sym(src text, dst text, km int) AS (
        SELECT src, dst, km FROM roads
        UNION ALL
        SELECT dst, src, km FROM roads
    ),
    walks(city text, hops int) AS (
        SELECT 'A', 0
        UNION
        SELECT s.dst, w.hops + 1
        FROM walks w JOIN sym s ON s.src = w.city
    )
SELECT city, min(hops) FROM walks GROUP BY city ORDER BY city;
```

It fails with `ERROR:  Evaluation error: Recursive query exceeded the recursion
limit 20.` The `UNION` deduplicates, but `(B, 1)` and `(B, 3)` are different
rows, so every lap around A to B to A produces a hop count nobody has seen
before and the binding never settles
([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).
A counter in a recursive binding needs an aggregate over it, not a `UNION`
under it.

Standard SQL brings `WITH RECURSIVE` with a `depth + 1` column and
`SELECT city, MIN(depth) ... GROUP BY city` in the outer query. That gives the
same four rows, and to get there on an undirected graph it needs Postgres 14's
`CYCLE` clause or a hand-rolled visited array, because the walk-enumerating
recursion is exactly the diverging shape above. What changes is that `min`
moves inside the binding, which `WITH RECURSIVE` forbids
([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)),
and the cycle guard disappears with it.

## Cheapest route

The same shape with kilometres summed instead of hops counted.

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

On the fixture this returns (B, 4), (C, 7), (D, 9), (E, 14).

Compare that with the hop counts above:

| City | Fewest hops | Cheapest km | Cheapest route |
|---|---|---|---|
| B | 1 | 4 | A, B |
| C | 1 | 7 | A, B, C |
| D | 2 | 9 | A, B, C, D |
| E | 3 | 14 | A, B, C, D, E |

C is one hop from A along the 10 km road and 7 km along the two-hop way. D is
two hops away and 12 km, or three hops away and 9 km. Neither column is
derivable from the other. Decide which one the question is asking for before
writing the query; "how far" in a request usually means kilometres, and
"within three of me" usually means hops
([reachability.md#within-k-hops](reachability.md#within-k-hops)).

It converges for the same reason `hops` does, with one extra condition: the
weights must be positive. `min` can only lower a city's value and zero is the
floor only while every edge adds something. A negative cycle removes the floor,
and then the minimum falls forever:

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 20)
    neg(src text, dst text, km int) AS (
        SELECT src, dst, km
        FROM (VALUES ('A', 'B', 1), ('B', 'C', -3), ('C', 'A', 1)) AS v(src, dst, km)
    ),
    dist(city text, km int) AS (
        SELECT city, min(km)
        FROM (
            SELECT 'A', 0
            UNION ALL
            SELECT s.dst, d.km + s.km
            FROM dist d JOIN neg s ON s.src = d.city
        ) AS x(city, km)
        GROUP BY city
    )
SELECT city, km FROM dist ORDER BY city;
```

It returns A at -6, B at -5 and C at -7, and it does not raise. Those are not
distances; they are the running totals at iteration 20, and they get more
negative if the limit does. The limit did not miss this because the binding is
topped by an aggregate. It missed it because it tracks changes to the row set
and not to values
([semantics.md#recursion-limits](semantics.md#recursion-limits)). Measured on
v26.38.1 against this exact block, it raises at 2 and 3, the iterations in
which a new city first appears, and stops raising from 4 onward, once every
city is present and only the numbers are still falling. A shortest-path binding
reaches all its keys early and then spends the rest of the loop lowering
values, so the guardrail goes quiet at exactly the point it would have to
speak. Check the
weights instead, with a standing `SELECT count(*) FROM roads WHERE km <= 0`, and
treat the limit as a bound on runtime rather than as a correctness check.

Standard SQL brings one of two things, and neither is a query. The first is
Dijkstra in a procedural language, a priority queue in PL/pgSQL or a stored
procedure, because `WITH RECURSIVE` cannot keep the minimum per node as it
goes. The second is an enumerate-all-paths CTE that carries a running cost and
a visited-nodes array as a cycle guard, then takes `MIN(cost) ... GROUP BY dst`
in the outer query. That one is a query, and it materializes one row per simple
path, which grows factorially with the node count on a dense graph. Both
disappear here: the aggregate inside the binding is the whole algorithm, and it
holds one row per city throughout.

## One witness path

A distance is often not the answer. The answer is the route. Keep a breadcrumb
alongside the minimum and walk it back in a second binding.

```sql
WITH MUTUALLY RECURSIVE
    sym(src text, dst text, km int) AS (
        SELECT src, dst, km FROM roads
        UNION ALL
        SELECT dst, src, km FROM roads
    ),
    best(city text, km int, prev text) AS (
        SELECT DISTINCT ON (city) city, km, prev
        FROM (
            SELECT 'A', 0, NULL::text
            UNION ALL
            SELECT s.dst, b.km + s.km, b.city
            FROM best b JOIN sym s ON s.src = b.city
        ) AS x(city, km, prev)
        ORDER BY city, km, prev
    ),
    route(city text, step int) AS (
        SELECT 'E', 0
        UNION
        SELECT b.prev, r.step + 1
        FROM route r JOIN best b ON b.city = r.city
        WHERE b.prev IS NOT NULL
    )
SELECT r.step, r.city, b.km
FROM route r JOIN best b ON b.city = r.city
ORDER BY r.step DESC;
```

On the fixture this returns (4, A, 0), (3, B, 4), (2, C, 7), (1, D, 9) and
(0, E, 14): read top to bottom, the route A, B, C, D, E, with the running cost
at each stop and the total, 14 km, on the last row. Joining `route` back to
`best` in the body is what puts the distance and the route in one answer, and
"the shortest path" usually wants both; `SELECT city, step FROM route` alone
gives the sequence without the cost. `best` itself holds (A, 0, NULL),
(B, 4, A), (C, 7, B), (D, 9, C) and (E, 14, D), which is the same distance
column the previous section computed plus the predecessor that achieved it.

`DISTINCT ON (city) ... ORDER BY city, km, prev` is an argmin. It keeps the
cheapest row per city and carries that row's other columns along, which is the
part `min(km)` cannot do. `prev` in the `ORDER BY` is a tiebreak, not a
preference: no city in this fixture has two equally cheap predecessors, so it
changes nothing here, and it is what makes the same query over tied data return
the same witness every time instead of an arbitrary one.

Both bindings converge, and for different reasons. `best` converges by the
`dist` argument: one row per city, a value that only falls, a floor at zero
while the weights are positive. `route` converges because at the fixpoint every
`prev` step moves to a strictly cheaper city, so the walk back from E is finite
and `UNION` makes re-deriving a step a no-op. `route` is recomputed from the
current `best` on every iteration, so breadcrumbs from a half-finished `best`
do not survive into the answer; only the fixpoint's predecessors do. Positive
weights are load-bearing twice over: they are what stops `prev` from forming a
loop that `route` would walk forever.

One witness is almost always what "the shortest path" means. All shortest paths
is a different question and a much larger answer: keep every predecessor
achieving the minimum instead of one, and the number of distinct shortest
routes can be exponential in the graph size even when every distance is small.
Ask which one is wanted before choosing the shape, because the argmin form
cannot be extended into the enumerating form by adding a column.

Standard SQL brings the array accumulator: `WITH RECURSIVE` carrying
`path || n.id`, a `NOT (n.id = ANY(path))` cycle guard, and
`DISTINCT ON (dst) ... ORDER BY dst, cost` in the outer query. It enumerates
every simple path first and picks per destination afterwards. The rewrite is
mechanical and the change is where the pruning happens: `DISTINCT ON` in the
recursive term is forbidden in standard SQL
([semantics.md#what-standard-sql-forbids-that-wmr-allows](semantics.md#what-standard-sql-forbids-that-wmr-allows)),
and moving it inside replaces both the array and the cycle guard.

## One target

Asking for one destination looks like a filter on the body.

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
SELECT city, km FROM dist WHERE city = 'E';
```

On the fixture this returns the single row (E, 14). It converges exactly as the
unfiltered `dist` does, because it is the unfiltered `dist` with one row
selected from the fixpoint.

That is the honest description of the cost too. The `WHERE city = 'E'` stays in
the body and does no pruning: predicates are not pushed into a recursive
binding
([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)),
so the loop still computes the distance to every city and the body throws four
of the five rows away. Single-target and all-targets cost the same here. That
is not a bug to route around; on a maintained view it is usually what you want,
since the same dataflow serves every destination.

When the graph is large enough that the difference matters, the pruning has to
be written inside the binding. A budget is the simplest form: stop extending a
partial route once it is already more expensive than the answer can be.

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
            WHERE d.km + s.km <= 12
        ) AS x(city, km)
        GROUP BY city
    )
SELECT city, km FROM dist ORDER BY city;
```

On the fixture this returns A at 0, B at 4, C at 7 and D at 9. The 12 is not
arbitrary: it is the cost of a route to D that is already in hand, the two-hop
A to B to D way, so any cheaper route to D stays inside the budget and nothing
that could beat the known route is pruned. E is gone, because it is 14 km away.
That is the shape of the trade. A budget bounds the search for the one target
it was derived from and silently truncates every other. It converges for the
`dist` reason plus a structural one: the guard bounds the total weight, so with
positive weights the loop can only run a bounded number of rounds whatever the
values do. The budget must be an upper bound you can defend, such as a known
route's cost or a service-level limit. Set it too low and the target quietly
vanishes from the result rather than reporting that it was unreachable within
the budget.

Standard SQL brings the same two placements and the same trap. A Postgres
Dijkstra stops as soon as the target is popped from the queue, which is a real
early exit that a fixpoint has no equivalent of; a Postgres `WITH RECURSIVE`
with the target filter in the outer query prunes exactly as little as this one
does. The change is that here the filter's placement is the only lever, so it
has to be a deliberate choice rather than a habit.

## Pitfalls

- Reading a one-directional edge table as if it were a road network. Symmetrize
  first, in a leading non-recursive binding. On this fixture the bug is
  invisible from A, because every road happens to point away from it, and
  obvious from E, which reaches nothing but itself.
- A `km` or `hops` column in a recursive binding with no aggregate over it. Two
  routes to the same city are two rows, and around a cycle each lap is a new
  number, so the loop enumerates walks forever. `UNION` does not save it: the
  rows genuinely differ
  ([semantics.md#multisets-and-convergence](semantics.md#multisets-and-convergence)).
- Negative or zero weights. `min` converges because it descends toward a floor,
  and a negative cycle removes the floor. Zero-weight edges leave `dist` and
  `best` converging and can break `route`. Two cities joined by a zero-weight
  road have the same `km`, so the `prev` tiebreak decides, and when a city's
  zero-weight neighbour sorts ahead of its real predecessor the two point at
  each other and the walk back never reaches the seed. It depends on the names:
  with roads (A, B, 4) and (B, C, 0) the tiebreak prefers A over C, `best` gives
  B the predecessor A, and `route` from C terminates; rename the seed to Z and
  the same two roads give B the predecessor C and C the predecessor B, and
  `route` runs forever. A zero road out of the seed always loses, because `NULL`
  sorts last and the seed's own row cannot win the tie.
- Treating `ERROR AT RECURSION LIMIT` as a correctness check on `hops`, `dist`
  or `best`. All three are topped by a reduce, and on v26.38.1 the limit stops
  raising once the set of keys has settled, which on a distance recursion is
  long before the values have
  ([semantics.md#recursion-limits](semantics.md#recursion-limits)). Validate the
  weights instead.
- Answering the hop question with the distance query or the other way round. On
  this fixture the cheapest route to D takes more hops than the shortest one,
  and both answers are correct for their own question.
- Expecting `WHERE city = 'E'` in the body to make the query cheaper. It does
  not; the recursion still visits everything
  ([semantics.md#what-the-optimizer-will-not-do](semantics.md#what-the-optimizer-will-not-do)).
  Prune inside the binding with a budget, and accept that the budget can hide
  the target.
- Asking for "the shortest path" and building the all-shortest-paths query, or
  the reverse. One witness is a breadcrumb column and an argmin; every witness
  is a set of predecessors per city and an output that can be exponential.
- Reaching for this file when the question is "can I get there at all". A `min`
  over weights is an expensive way to compute a reachable set, and it needs a
  weight column that the question does not care about. That is
  [reachability.md](reachability.md).
- Assuming the whole graph is connected. `dist` returns nothing at all for a
  city in another component, rather than a row with a null or infinite
  distance. If the answer needs one row per city, left-join `cities` against
  the fixpoint in the body. Which cities are mutually reachable at all is a
  separate question, and it belongs in
  [components.md#connected-components-by-min-label-propagation](components.md#connected-components-by-min-label-propagation).
