# CREATE MATERIALIZED VIEW
`CREATE MATERIALIZED VIEW` defines a view that is persisted in durable storage and incrementally updated as new data arrives.
Use `CREATE MATERIALIZED VIEW` to:

- Create a materialized view that maintains [fresh
  results](/concepts/reaction-time) by persisting them in durable storage and
  incrementally updating them as new data arrives.

- Create a replacement for an existing materialized view that can be applied in
  place with [`ALTER MATERIALIZED VIEW ... APPLY
  REPLACEMENT`](/sql/alter-materialized-view/).

Materialized views are particularly useful when you need **cross-cluster
access** to results or want to sink data to external systems like
[Kafka](/sql/create-sink). When you create a materialized view, a
[cluster](/concepts/clusters/), responsible for maintaining the view, is
associated with it, but the results can be **queried from any cluster**. This
allows you to separate the compute resources used for view maintenance from
those used for serving queries.

If you do not need durability or cross-cluster sharing, and you are primarily
interested in fast query performance within a single cluster, you may prefer to
[create a view and index it](/concepts/views/#views). In Materialize, [indexes
on views](/concepts/indexes/) also maintain results incrementally, but store
them in memory, scoped to the cluster where the index was created. This approach
offers lower latency for direct querying within that cluster.

## Syntax

**CREATE MATERIALIZED VIEW:**

### Create materialized view

```mzsql
CREATE MATERIALIZED VIEW [IF NOT EXISTS] <view_name>
[(<col_ident>, ...)]
[IN CLUSTER <cluster_name>]
[WITH (<with_options>)]
AS <select_stmt>;

```

| Syntax element | Description |
| --- | --- |
| `IF NOT EXISTS` | If specified, do not generate an error if a materialized view of the same name already exists.  |
| `<view_name>` | A name for the materialized view.  |
| `(<col_ident>, ...)` | Rename the `SELECT` statement's columns to the list of identifiers. Both must be the same length. Note that this is required for statements that return multiple columns with the same identifier.  |
| `IN CLUSTER <cluster_name>` | The cluster to maintain this materialized view. If not specified, defaults to the active cluster.  |
| `WITH (<with_options>)` | The following `<with_options>` are supported:  \| Field \| Value \| Description \| \|-------\|-------\|-------------\| \| `ASSERT NOT NULL` *col_ident* \| `text` \| The column identifier for which to create a [non-null assertion](#non-null-assertions). To specify multiple columns, use the option multiple times. \| \| `PARTITION BY` *columns* \| `(ident [, ident]*)` \| The key by which Materialize should internally partition this durable collection. See the [partitioning guide](/transform-data/patterns/partition-by/) for restrictions on valid values and other details. \| \| `RETAIN HISTORY FOR` *retention_period* \| `interval` \| ***Private preview.*** Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/transform-data/patterns/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`. \|  |
| `<select_stmt>` | The [`SELECT` statement](/sql/select) whose results you want to maintain incrementally updated.  |

**CREATE REPLACEMENT MATERIALIZED VIEW:**

### Create replacement materialized view

> **Public Preview:** This feature is in public preview.

Create a replacement materialized view for an existing materialized view.

```mzsql
CREATE REPLACEMENT MATERIALIZED VIEW <name>
FOR <target_name>
[IN CLUSTER <cluster_name>]
[WITH (<with_options>)]
AS <select_stmt>;

```

| Syntax element | Description |
| --- | --- |
| `<name>` | A name for the replacement materialized view.  |
| `<target_name>` | The name of the existing materialized view to be replaced. The replacement materialized view can only be applied to this materialized view.  |
| `IN CLUSTER <cluster_name>` | The cluster to maintain this replacement materialized view. If not specified, defaults to the active cluster.  |
| `WITH (<with_options>)` | Same options as `CREATE MATERIALIZED VIEW`.  |
| `<select_stmt>` | The [`SELECT` statement](/sql/select) for the replacement view. The statement must produce the same output schema as the target materialized view; i.e., column names, column types, column order, nullability, and keys must all match.  |

The created replacement materialized view starts hydrating immediately and can
later be applied to replace the specified materialized view. For more
information, see [Creating replacement materialized
views](#creating-replacement-materialized-views).

## Details

### Usage pattern

In Materialize, both <a href="/concepts/indexes" >indexes</a> on views and <a href="/concepts/views/#materialized-views" >materialized
views</a> incrementally update the view
results when Materialize ingests new data. Whereas materialized views persist
the view results in durable storage and can be accessed across clusters, indexes
on views compute and store view results in memory within a <strong>single</strong> cluster.
<p>Some general guidelines for usage patterns include:</p>
<table>
  <thead>
      <tr>
          <th>Usage Pattern</th>
          <th>General Guideline</th>
      </tr>
  </thead>
  <tbody>
      <tr>
          <td>View results are accessed from a single cluster only;<br>such as in a 1-cluster or a 2-cluster architecture.</td>
          <td>View with an <a href="/sql/create-index" >index</a></td>
      </tr>
      <tr>
          <td>View used as a building block for stacked views; i.e., views not used to serve results.</td>
          <td>View</td>
      </tr>
      <tr>
          <td>View results are accessed across <a href="/concepts/clusters" >clusters</a>;<br>such as in a 3-cluster architecture.</td>
          <td>Materialized view (in the transform cluster)<br>Index on the materialized view (in the serving cluster)</td>
      </tr>
      <tr>
          <td>Use with a <a href="/serve-results/sink/" >sink</a> or a <a href="/sql/subscribe" ><code>SUBSCRIBE</code></a> operation</td>
          <td>Materialized view</td>
      </tr>
      <tr>
          <td>Use with <a href="/transform-data/patterns/temporal-filters/" >temporal filters</a></td>
          <td>Materialized view</td>
      </tr>
  </tbody>
</table>

### Indexing materialized views

Although you can query a materialized view directly, these queries will be
issued against Materialize's storage layer. This is expected to be fast, but
still slower than reading from memory. To improve the speed of queries on
materialized views, we recommend creating [indexes](../create-index) based on
common query patterns.

It's important to keep in mind that indexes are **local** to a cluster, and
maintained in memory. As an example, if you create a materialized view and
build an index on it in the `quickstart` cluster, querying the view from a
different cluster will _not_ use the index; you should create the appropriate
indexes in each cluster you are referencing the materialized view in.

[//]: # "TODO(morsapaes) Point to relevant operational guide on indexes once
this exists+add detail about using indexes to optimize materialized view
stacking."

### Non-null assertions

Because materialized views may be created on arbitrary queries, it may not in
all cases be possible for Materialize to automatically infer non-nullability of
some columns that can in fact never be null. In such a case, `ASSERT NOT NULL`
clauses may be used as described in the syntax section above. Specifying
`ASSERT NOT NULL` for a column forces that column's type in the materialized
view to include `NOT NULL`. If this clause is used erroneously, and a `NULL`
value is in fact produced in a column for which `ASSERT NOT NULL` was
specified, querying the materialized view will produce an error until the
offending row is deleted.

### Creating replacement materialized views

> **Public Preview:** This feature is in public preview.

You can use [`CREATE REPLACEMENT MATERIALIZED
VIEW`](/sql/create-materialized-view/) with [`ALTER MATERIALIZED VIEW ... APPLY
REPLACEMENT`](/sql/alter-materialized-view) to replace materialized views
in-place without recreating dependent objects or incurring downtime.

<p>To create a replacement materialized view, you must:</p>
<ul>
<li>Specify the target materialized view.</li>
<li>Specify a <code>SELECT</code> statement for the replacement view that produces the
same output schema (including column order and keys) as the target view.</li>
</ul>
<p>Upon creation, the replacement view starts hydrating in the background.</p>

Before applying the replacement view, verify that the replacement view is
hydrated to avoid downtime:

The replacement view is dropped when you apply the replacement view. For more
information on applying the replacement view, including recommendations and
CPU/memory considerations, see [`ALTER MATERIALIZED VIEW ... APPLY
REPLACEMENT...`](/sql/alter-materialized-view/#replacing-a-materialized-view)

See also:

- [Replace materialized
views](/transform-data/updating-materialized-views/replace-materialized-view/)
guide for a step-by-step tutorial.

#### Query performance of replacement views

You can query a replacement materialized view to validate its results before
replacing. However, when queried, replacement materialized views are treated
like a [view](/sql/create-view), and the query results are re-computed as part
of the query execution. As such, queries against replacement materialized views
are slower and more computationally expensive than queries against regular
materialized views.

#### Restrictions and limitations

A replacement materialized view can only be applied to the target materialized
view specified in the `FOR` clause of the [`CREATE REPLACEMENT MATERIALIZED
VIEW`](/sql/create-materialized-view/) statement.

You cannot create dependent objects using [replacement materialized
views](/sql/create-materialized-view/#creating-replacement-materialized-views);
for example, you cannot create an index on a replacement materialized view or
create other views on a replacement materialized view.

## Examples

### Creating a materialized view

The following example creates a `winning_bids` materialized view:
```mzsql
CREATE MATERIALIZED VIEW winning_bids AS
SELECT DISTINCT ON (a.id) b.*, a.item, a.seller
FROM auctions AS a
JOIN bids AS b
  ON a.id = b.auction_id
WHERE b.bid_time < a.end_time
  AND mz_now() >= a.end_time
ORDER BY a.id,
  b.amount DESC,
  b.bid_time,
  b.buyer;

```

### Using non-null assertions

```mzsql
CREATE MATERIALIZED VIEW users_and_orders WITH (
  -- The semantics of a FULL OUTER JOIN guarantee that user_id is not null,
  -- because one of `users.id` or `orders.user_id` must be not null, but
  -- Materialize cannot yet automatically infer that fact.
  ASSERT NOT NULL user_id
)
AS
SELECT
  coalesce(users.id, orders.user_id) AS user_id,
  ...
FROM users FULL OUTER JOIN orders ON users.id = orders.user_id
```

[//]: # "TODO(morsapaes) Add more elaborate examples with \timing that show
things like querying materialized views from different clusters, indexed vs.
non-indexed, and so on."

### Creating a replacement materialized view

> **Public Preview:** This feature is in public preview.

The following example creates a replacement materialized view
`winning_bids_replacement` for the `winning_bids` materialized view. The
replacement view specifies a different filter `mz_now() > a.end_time` than
the existing view `mz_now() >= a.end_time`.
```mzsql
CREATE REPLACEMENT MATERIALIZED VIEW winning_bids_replacement
FOR winning_bids AS
SELECT DISTINCT ON (a.id) b.*, a.item, a.seller
FROM auctions AS a
JOIN bids AS b
  ON a.id = b.auction_id
WHERE b.bid_time < a.end_time
  AND mz_now() > a.end_time
ORDER BY a.id,
  b.amount DESC,
  b.bid_time,
  b.buyer;

```

To replace the existing view with its replacement, see [`ALTER MATERIALIZED
VIEW`](../alter-materialized-view).

See also:

- [Replace materialized views guide
](/transform-data/updating-materialized-views/replace-materialized-view/)

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `CREATE` privileges on the containing cluster.
- `USAGE` privileges on all types used in the materialized view definition.
- `USAGE` privileges on the schemas for the types used in the statement.

## Additional information

- Materialized views are not monotonic; that is, materialized views cannot be
  recognized as append-only.

## Related pages

- [`ALTER MATERIALIZED VIEW`](../alter-materialized-view)
- [`SHOW MATERIALIZED VIEWS`](../show-materialized-views)
- [`SHOW CREATE MATERIALIZED VIEW`](../show-create-materialized-view)
- [`DROP MATERIALIZED VIEW`](../drop-materialized-view)
