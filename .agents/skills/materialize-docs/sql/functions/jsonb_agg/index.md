# jsonb_agg function
Aggregates values (including nulls) as a jsonb array.
The `jsonb_agg(expression)` function aggregates all values indicated by its expression,
returning the values (including nulls) as a [`jsonb`](/sql/types/jsonb) array.
The input values to the aggregate can be [filtered](../filters).

## Syntax

```mzsql
jsonb_agg ( <expression>
  [ORDER BY <col_ref> [ASC | DESC] [NULLS FIRST | NULLS LAST] [, ...]]
)
[FILTER (WHERE <filter_clause>)]

```

| Syntax element | Description |
| --- | --- |
| `<expression>` | The values you want aggregated.  |
| **ORDER BY** `<col_ref>` [**ASC** \| **DESC**] [**NULLS FIRST** \| **NULLS LAST**] [, ...] | Optional. Specifies the ordering of values within the aggregation. If not specified, incoming rows are not guaranteed any order.  |
| **FILTER** (WHERE `<filter_clause>`) | Optional. Specifies which rows are sent to the aggregate function. Rows for which the `<filter_clause>` evaluates to true contribute to the aggregation. See [Aggregate function filters](/sql/functions/filters) for details.  |

## Signatures

Parameter | Type | Description
----------|------|------------
_expression_ | [jsonb](../../types) | The values you want aggregated.

### Return value

`jsonb_agg` returns the aggregated values as a `jsonb` array.

Any `ORDER BY` applied before the aggregate function is evaluated, such as in
a feeding subquery, is ignored. Unless `ORDER BY` is included in the aggregate
function call itself, the order in which the values are aggregated is
unspecified.

## Details

### Usage in dataflows

While `jsonb_agg` is available in Materialize, materializing `jsonb_agg(expression)`
is considered an incremental view maintenance anti-pattern. Any change to the data
underlying the function call will require the function to be recomputed entirely,
discarding the benefits of maintaining incremental updates.

Instead, we recommend that you materialize all components required for the
`jsonb_agg` function call and create a non-materialized view using `jsonb_agg`
on top of that. That pattern is illustrated in the following statements:

```mzsql
CREATE MATERIALIZED VIEW foo_view AS SELECT * FROM foo;
CREATE VIEW bar AS SELECT jsonb_agg(foo_view.bar) FROM foo_view;
```

## Examples

```mzsql
SELECT
  jsonb_agg(t) FILTER (WHERE t.content LIKE 'h%')
    AS my_agg
FROM (
  VALUES
  (1, 'hey'),
  (2, NULL),
  (3, 'hi'),
  (4, 'salutations')
  ) AS t(id, content);
```
```nofmt
                       my_agg
----------------------------------------------------
 [{"content":"hi","id":3},{"content":"hey","id":1}]
```

## See also

* [`jsonb_object_agg`](/sql/functions/jsonb_object_agg)
