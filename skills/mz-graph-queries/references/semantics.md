# WITH MUTUALLY RECURSIVE semantics

How `WITH MUTUALLY RECURSIVE` (WMR) evaluates, and the rules that follow from
it. Read this file to answer: why does my recursion never finish, why do I have
duplicate rows, why does the delay trick work, why must I declare column types,
what does a recursion limit do, what will the optimizer refuse to do for me,
how do I read the plan, and what may I write here that standard SQL forbids.

Fixture tables used: `transfers`. Every block assumes `references/fixture.sql`
is loaded.

## Evaluation model

Evaluation is a fixpoint loop over the whole binding list.

1. Every binding starts empty.
2. One iteration updates each binding in list order, evaluating its query
   against the current value of every binding.
3. The loop stops when an iteration changes nothing. The body after the
   bindings then runs against that fixpoint.

Because bindings update in order, a binding sees the values its predecessors
already produced in this iteration and the previous iteration's values of
itself and of everything defined after it.

```sql
WITH MUTUALLY RECURSIVE
    counter(n int) AS (
        SELECT 1
        UNION
        SELECT n + 1 FROM counter WHERE n < 5
    )
SELECT n FROM counter ORDER BY n;
```

On the fixture this returns 1, 2, 3, 4, 5. It converges because each iteration
adds at most one new value and the `WHERE n < 5` guard stops production at 5,
after which an iteration adds nothing.

## Multisets and convergence

A binding is a multiset, not a set. The back edge consolidates rows with the
same values into one row with a count, but it never deduplicates them. "Nothing
changed" therefore means no row's count changed, not merely that no new
distinct row appeared. A recursion whose row counts keep growing never
converges, however long ago the set of distinct rows stopped growing.

This shape is the common accident. It carries the binding forward with
`UNION ALL`, so every row the binding already holds is re-added each iteration
and the counts climb without bound, long after the distinct rows have settled.

<!-- verify: error -->

```sql
WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 20)
    reach(src text, dst text) AS (
        SELECT DISTINCT src, dst FROM transfers
        UNION ALL
        SELECT src, dst FROM reach
        UNION ALL
        SELECT r.src, t.dst FROM reach r JOIN transfers t ON r.dst = t.src
    )
SELECT src, dst FROM reach;
```

It fails with `ERROR:  Evaluation error: Recursive query exceeded the recursion
limit 20.` The limit is what makes the divergence visible; without one the
statement runs until it is cancelled.

`RETURN AT RECURSION LIMIT` stops at a chosen iteration and hands back the
state, which is how to look inside a non-converging binding.

```sql
WITH MUTUALLY RECURSIVE (RETURN AT RECURSION LIMIT 2)
    reach(src text, dst text) AS (
        SELECT DISTINCT src, dst FROM transfers
        UNION ALL
        SELECT src, dst FROM reach
        UNION ALL
        SELECT r.src, t.dst FROM reach r JOIN transfers t ON r.dst = t.src
    )
SELECT src, dst, count(*) AS copies FROM reach GROUP BY src, dst ORDER BY src, dst;
```

After two iterations every one of the fixture's six base edges already carries
`copies = 2`, while the pairs derived in that iteration carry 1. Those
multiplicities are the problem: the `SELECT src, dst FROM reach` branch re-adds
every row the binding already holds, so the binding's total row count roughly
doubles each iteration (17, 38, 79, 160, 321 for iterations 2 through 6 on this
fixture). The distinct pairs settle long before that: 11, 16, then the full 17
at iterations 2, 3 and 4. The counts keep climbing after the distinct set is
complete, so the loop never stops.

The fix is `UNION`, which deduplicates, and dropping the redundant
carry-forward branch. Deduplicating the union makes the counts idempotent, so
the loop stops once no new pair appears.

```sql
WITH MUTUALLY RECURSIVE
    reach(src text, dst text) AS (
        SELECT src, dst FROM transfers
        UNION
        SELECT r.src, t.dst FROM reach r JOIN transfers t ON r.dst = t.src
    )
SELECT count(*) FROM reach;
```

This returns 17, the transitive closure of the fixture's six transfers.

The rule: use `UNION` in a recursive binding by default. `UNION ALL` is correct
only when every row derives exactly once, as in a tree walk or a bounded
counter, or when the binding feeds an aggregate that collapses each group.

## Binding order and the delay idiom

A `Get` of a binding that appears at or before its own definition in the list
reads the previous iteration's value. In the first iteration that value is
empty. This is not a limitation to work around; it is a one-iteration delay
register that lets a binding subtract its own seed after round one.

```sql
WITH MUTUALLY RECURSIVE
    start(pos int) AS (SELECT 0),
    head(pos int) AS (
        SELECT pos FROM start
        EXCEPT ALL
        SELECT pos FROM start_delayed
        UNION ALL
        SELECT CASE WHEN pos < 3 THEN pos + 1 ELSE pos END FROM head
    ),
    start_delayed(pos int) AS (SELECT pos FROM start)
SELECT pos FROM head;
```

This returns the single row 3. `start_delayed` is defined after `head`, so
`head` reads its previous value.

| Iteration | `start_delayed` read by `head` | `head` after the update |
|---|---|---|
| 1 | empty | `{0}`: the seed survives `EXCEPT ALL`, and the `head` branch is empty |
| 2 | `{0}` | `{1}`: the seed cancels, and `0` advances to `1` |
| 3 | `{0}` | `{2}` |
| 4 | `{0}` | `{3}` |
| 5 | `{0}` | `{3}`, unchanged, so the loop stops |

Without the delay the seed would be re-added every iteration and the binding
would hold `{0, 3}` forever. The delayed binding survives optimization as its
own binding inside the recursive block rather than being inlined into `head`,
so the idiom is stable.

## Column types

Every binding must declare its column names and types. The declaration is
mandatory, the columns are nullable, and each branch's output is coerced to the
declared type with an assignment cast. An assignment cast permits fewer
conversions than an explicit `::` cast, so a value that `::` would convert can
still be rejected here. A string literal types as `text`, and `text` does not
assignment-cast to a number.

<!-- verify: error -->

```sql
WITH MUTUALLY RECURSIVE bar(x int8) AS (SELECT '1') SELECT x FROM bar;
```

`ERROR:  WITH MUTUALLY RECURSIVE query "bar" declared types (bigint), but query returns types (text)`.
Write `SELECT '1'::int8`, and cast every `NULL` placeholder to the declared
type, as in `NULL::int` for an `int` column. A bare `NULL` types as `text` just
like a string literal, so it passes for a `text` column and fails against every
other declared type.

Assignment casts do apply, and they can change values. A declared
`numeric(38,2)` rounds:

```sql
WITH MUTUALLY RECURSIVE t(x numeric(38,2)) AS (SELECT 1.23456) SELECT x FROM t;
```

This returns `1.23`. Declare the scale you want rather than relying on the
literal's.

Type errors inside a binding surface before the recursion runs, and a `UNION`
of mismatched branches is reported as a plain union error, not as a WMR error:

<!-- verify: error -->

```sql
WITH MUTUALLY RECURSIVE mixed(x int) AS (SELECT 1 UNION SELECT 'a') SELECT x FROM mixed;
```

`ERROR:  UNION types integer and text cannot be matched`. The declared `(x int)`
never enters the message, so read it as a branch problem and put an explicit
`::` cast on every branch of the union.

## Recursion limits

There is no default recursion limit. A binding that does not converge runs
until the statement is cancelled or, for a maintained view, forever.

| Option | Behavior at iteration n |
|---|---|
| `ERROR AT RECURSION LIMIT n` | Errors if iteration n still changed something |
| `RETURN AT RECURSION LIMIT n` | Returns the state after n iterations |

`ERROR AT RECURSION LIMIT` tracks changes to the row set, not to values, and on
v26.38.1 the difference is observable. A binding topped by a reduce or a TopK
raises while it is still adding or removing rows, then goes silent once only
its values keep changing, returning the iteration-n state instead
([rollups.md#the-same-with-the-aggregate-inside](rollups.md#the-same-with-the-aggregate-inside)).
For such a shape the guardrail is `RETURN AT RECURSION LIMIT` plus a check on
the returned state, or a `UNION`-topped shape, whose every change is a row
change and which therefore always raises. The rest of this section describes
that ordinary case.

```sql
WITH MUTUALLY RECURSIVE (RETURN AT RECURSION LIMIT 3)
    counter(n int) AS (
        SELECT 1
        UNION
        SELECT n + 1 FROM counter WHERE n < 100
    )
SELECT n FROM counter ORDER BY n;
```

This returns 1, 2, 3: the counter would have reached 100, and the limit hands
back the state after three iterations instead.

A limit is per `WITH MUTUALLY RECURSIVE` block, not per query and not per
binding, and it survives view inlining: a limited block inside a view keeps its
limit when the view is used elsewhere. A view over a divergent recursion still
installs successfully. It simply never hydrates: `mz_internal.mz_hydration_statuses`
reports `hydrated = f` for it indefinitely, and its dataflow keeps iterating on
the cluster until the view is dropped.

Put `ERROR AT RECURSION LIMIT` on every maintained recursive view, with the
limit well above the expected graph diameter. It converts a silent
never-hydrating dataflow into a loud failure. Use `RETURN AT RECURSION LIMIT`
for debugging, and for fixed-iteration numeric methods where the iteration
count is the answer's definition.

## What the optimizer will not do

Optimizations that hold everywhere else stop at the boundary of a recursive
binding. Plan for that when writing one.

| Optimization | Inside a recursive binding | Consequence |
|---|---|---|
| Predicate pushdown | Never pushed in | Write the filter inside the binding, not in the body |
| Projection pushdown | All declared columns are kept | Carry narrow keys; join the wide attributes back in the body |
| Cardinality estimates | None available | Join order is not chosen for you; order joins by hand |
| Constant folding across bindings | Not performed | Fold constants yourself before the block |
| Arrangements across the back edge | Not carried | Every join against the binding re-arranges it each iteration |
| Imported indexes on base tables | Used inside the loop | The main lever: index the static side on the join key |
| Non-recursive prefix bindings | Hoisted out of the loop | Put non-recursive setup in leading bindings and it is computed once |

## Reading EXPLAIN

```sql
EXPLAIN WITH MUTUALLY RECURSIVE (ERROR AT RECURSION LIMIT 100)
    reach(src text, dst text) AS (
        SELECT src, dst FROM transfers
        UNION
        SELECT r.src, t.dst FROM reach r JOIN transfers t ON r.dst = t.src
    )
SELECT src, dst FROM reach;
```

The plan has an outer `With` holding the non-recursive read of `transfers` as
`cte l0`, then a `With Mutually Recursive` node, then `Return`. That outer
`With` is the hoist: the base table read happens once, not per iteration.
Inside the recursive node each recursive binding is one
`cte [recursion_limit=100] lN =` block; the block's single limit is rendered on
every binding's cte, so seeing it repeated does not mean it is per binding. A
`Stream l1` appearing inside `cte l1` is the back edge. The `Distinct
GroupAggregate` is where `UNION` planned its deduplication, and it is the
operator that makes the fixpoint reachable. The `Arrange (#1{dst})` over
`Stream l1` under the `Differential Join` is the per-iteration re-arrangement of
the binding, which is the cost the back edge imposes. The final `Return`
streams the fixpoint into the body.

Plan text changes between Materialize versions; the recorded output for this
block was produced on v26.38.1, and the operator names may differ on yours
while the shape stays the same.

One `EXPLAIN` option is unavailable here:

<!-- verify: error -->

```sql
EXPLAIN OPTIMIZED PLAN WITH (linear chains) AS TEXT FOR
WITH MUTUALLY RECURSIVE
    reach(src text, dst text) AS (
        SELECT src, dst FROM transfers
        UNION
        SELECT r.src, t.dst FROM reach r JOIN transfers t ON r.dst = t.src
    )
SELECT src, dst FROM reach;
```

`ERROR:  error while rendering explain output: The linear_chains option is not
supported with WITH MUTUALLY RECURSIVE.` Read recursive plans in the default
tree form.

## Update locality

A maintained recursive view is cheap to keep up to date when one input change
touches a bounded number of rows per iteration. Reachability over a graph with
many redundant paths has that property: removing one edge rarely removes any
reachable pair, and adding one edge adds few. A rollup over a tree of height h
has it too: one leaf change touches at most 2h rows, a retraction and an
addition at each of h levels. Recursions without update locality are the ones that make a
maintained view expensive: naive PageRank, k-means, and any all-pairs score
recompute a large fraction of their state for a single input change, because
every row's value depends on every other row's. Compute those one-shot with
`RETURN AT RECURSION LIMIT`, on demand, or outside the database, and maintain
only the inputs they read.

## What standard SQL forbids that WMR allows

Standard SQL's `WITH RECURSIVE` requires a non-recursive base case and a
linear, monotone recursive term: one reference to the recursive relation, no
aggregates, no `DISTINCT`, no outer join with the relation on the outer side,
no subqueries over it. WMR drops all of that, because it evaluates a fixpoint
rather than a queue-driven expansion.

| Standard SQL forbids | WMR allows | What it unlocks |
|---|---|---|
| Aggregate in the recursive term | `min`, `max`, `sum` over the binding | Shortest path and cheapest cost by keeping the min per key each iteration |
| `DISTINCT` in the recursive term | `SELECT DISTINCT` and `UNION` | Deduplication that makes the fixpoint reachable at all |
| `LEFT JOIN` with the recursive relation on the outer side | Any join direction | Defaults and overrides: inherit a parent's value only where a child has none |
| More than one reference to the recursive relation | Non-linear recursion, the binding joined to itself | Path doubling: closure in log(diameter) iterations instead of diameter |
| Subquery or `NOT EXISTS` over the recursive relation | Both | One witness path per pair, cycle guards, negation-based fixpoints |
| `ORDER BY ... LIMIT` and `DISTINCT ON` in the recursive term | Both | Top-k per node kept inside the loop instead of after it |
| More than one recursive relation | Mutual recursion across the whole binding list | Two-relation problems such as alternating levels or reachable-plus-frontier |
| Nested recursive blocks | A `WITH MUTUALLY RECURSIVE` in derived-table position inside another, `FROM (WITH MUTUALLY RECURSIVE ...) AS x` | Inner fixpoints per outer iteration |
| Omitting the non-recursive base case | Bindings may reference each other with no seed branch | Constraint-propagation shapes with no natural seed |

Postgres and SQL Server users reach for `WITH RECURSIVE ... UNION ALL` with a
seed branch and a single self-reference, then filter in the outer query. In
Materialize, drop the `RECURSIVE` keyword for `MUTUALLY RECURSIVE`, declare the
column types, change `UNION ALL` to `UNION` unless every row derives once, move
the outer filter inside the binding because it will not be pushed down, and add
a recursion limit.

## Pitfalls

- `UNION ALL` in a recursive binding that re-adds rows it already holds. The
  distinct answer looks right under `RETURN AT RECURSION LIMIT` and the query
  still never converges. Count with `count(*)` per key to see it.
- No recursion limit on a maintained view. It installs, never hydrates, and
  keeps its dataflow on the cluster until dropped. Nothing errors.
- Assuming a cycle in the data is what makes a recursion diverge. Multiset
  growth diverges on an acyclic graph too, and `UNION` converges on a cyclic
  one.
- Untyped literals in a binding. `SELECT '1'` and a bare `SELECT NULL` both
  type as `text`, and both fail against any non-`text` declared type before
  anything runs.
- Nesting a recursive block in a scalar subquery. On current versions a nested
  `WITH MUTUALLY RECURSIVE` belongs in derived-table position,
  `FROM (WITH MUTUALLY RECURSIVE ...) AS x`; the scalar-subquery form has been
  observed to abort `environmentd` on v26.38.1.
- Filtering in the body instead of in the binding. The predicate is not pushed
  into the recursion, so the binding still computes everything.
- Reading a binding defined later and expecting this iteration's value. It is
  the previous iteration's value, and empty in iteration one. That is the delay
  idiom when intended, and a silent off-by-one iteration when not.
- Wide recursive bindings. Every declared column is carried and re-arranged
  every iteration; recurse on keys and join the payload back in the body.
