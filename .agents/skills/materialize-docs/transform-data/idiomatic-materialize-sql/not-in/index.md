# `NOT IN` subquery
Use idiomatic Materialize SQL for `NOT IN (subquery)` predicates to avoid a cross join in the dataflow plan.
## Overview

The `fieldX NOT IN (<subquery>)` predicate returns `true` if `fieldX` does not
equal any value returned by the subquery. For predicates where `fieldX` or the
`<subquery>` can contain `NULL` values, Materialize provides idiomatic SQL
alternatives.

### Materialize and `NOT IN (<subquery>)`

When evaluating a `WHERE fieldX NOT IN (<subquery>)` predicate involving
possible `NULL` values for `fieldX` or `<subquery>`, Materialize performs a
cross join between the outer relation and the subquery to preserve SQL `NULL`
semantics, which can significantly increase memory usage. If possible, rewrite
the query to avoid the cross join.

## Idiomatic Materialize SQL

For `fieldX NOT IN (<subquery>)` predicates involving possible `NULL` values,
the following rewrites are available:

> **Note:** Neither rewrite is strictly equivalent to `NOT IN (<subquery>)`.
> Both rewrites avoid the `NULL` propagation semantics of `NOT IN`; that is, they
> treat subquery `NULL` values as non-matches rather than allowing them to
> invalidate the comparison. In addition, the `NOT EXISTS` rewrite retains outer
> rows whose value is `NULL`, whereas both `NOT IN` and the filter-`NULL`s rewrite
> exclude them.

- Rewrite to [`NOT EXISTS`](/sql/functions/#not-exists) with a correlated
  subquery.
- Retain `NOT IN`, but filter out `NULL` values from both the outer field and
  the subquery.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>
<tr>
<td><blue>Materialize SQL</blue></td>
<td class="copyableCode">

**Rewrite to `NOT EXISTS` with a correlated subquery.**

```mzsql
SELECT t1.*
FROM t1
WHERE NOT EXISTS (SELECT 1 FROM t2 WHERE t2.a = t1.a)
;
```

**Filter out `NULL`s on both sides of the `NOT IN`.**

```mzsql
SELECT t1.*
FROM t1
WHERE t1.a IS NOT NULL
  AND t1.a NOT IN (SELECT t2.a FROM t2 WHERE t2.a IS NOT NULL)
;
```

</td>
</tr>
<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid `NOT IN (<subquery>)` predicates, which force a cross join
between the outer relation and the subquery.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT t1.*
FROM t1
WHERE t1.a NOT IN (SELECT t2.a FROM t2) -- Anti-pattern. Avoid.
;
```

</td>
</tr>

</tbody>
</table>

If the subquery uses [`UNNEST()`](/sql/functions/#unnest) on a column whose
value depends on the outer row:
- Factor the `UNNEST()` into an uncorrelated [Common Table Expression
  (CTE)](/sql/select/#common-table-expressions-ctes) first.
- Then apply the rewrite against the CTE. See the [example
  below](#find-items-not-currently-on-sale).

## Examples

> **Note:** The example data can be found in the
> [Appendix](/transform-data/idiomatic-materialize-sql/appendix/example-orders).

### Find items not currently on sale

Using idiomatic Materialize SQL, the following examples find items in the
`items` table whose `item` value (declared `NOT NULL`) does not appear in any of
this week's sales arrays in `sales_items`, a nullable `text[]`. The subquery
uses [`UNNEST()`](/sql/functions/#unnest) to expand each week's `items` array
into individual values for comparison.

If the subquery uses [`UNNEST()`](/sql/functions/#unnest) on a column whose
value depends on the outer row:

- First, factor the `UNNEST()` into an uncorrelated [Common Table Expression
  (CTE)](/sql/select/#common-table-expressions-ctes).
- Then, apply the rewrite against the CTE.

<table>
<thead>
<tr>
<th></th>
<th></th>
</tr>
</thead>
<tbody>

<tr>
<td><blue>Materialize SQL</blue> ✅</td>
<td class="copyableCode">

Because the subquery uses [`UNNEST()`](/sql/functions/#unnest) on a column
of the outer-correlated row, factor the `UNNEST()` into an uncorrelated
[Common Table Expression
(CTE)](/sql/select/#common-table-expressions-ctes) first.

***Rewrite to `NOT EXISTS` with a CTE for the `UNNEST()`***

```mzsql
WITH this_weeks_sales AS (
  SELECT unnest(items) AS sale_item
  FROM sales_items
  WHERE week_of = date_trunc('week', current_timestamp)
)
SELECT i.item, i.price
FROM items i
WHERE NOT EXISTS (
  SELECT 1 FROM this_weeks_sales s WHERE s.sale_item = i.item
)
ORDER BY i.item
;
```

***Filter out `NULL`s with a CTE for the `UNNEST()`***

```mzsql
WITH this_weeks_sales AS (
  SELECT unnest(items) AS sale_item
  FROM sales_items
  WHERE week_of = date_trunc('week', current_timestamp)
)
SELECT i.item, i.price
FROM items i
WHERE i.item IS NOT NULL
  AND i.item NOT IN (
    SELECT sale_item FROM this_weeks_sales WHERE sale_item IS NOT NULL
  )
ORDER BY i.item
;
```

</td>
</tr>

<tr>
<td><red>Anti-pattern</red> ❌</td>
<td>

<red>Avoid `NOT IN (<subquery>)`, which forces a cross join.</red>

```nofmt
-- Anti-pattern. Avoid. --
SELECT i.item, i.price
FROM items i
WHERE i.item NOT IN (
  SELECT unnest(items) FROM sales_items
  WHERE week_of = date_trunc('week', current_timestamp)
)
ORDER BY i.item
;
```

</td>
</tr>

</tbody>
</table>

## See also

- [`NOT EXISTS`](/sql/functions/#not-exists)

- [Idiomatic Materialize SQL
  Chart](/transform-data/idiomatic-materialize-sql/appendix/idiomatic-sql-chart/)
