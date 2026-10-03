# Troubleshooting

Troubleshooting guides for queries that are slow, unresponsive, or expensive in Materialize.

This section contains troubleshooting guides for queries that don't perform as
expected. Each guide starts from a symptom, helps you find the cause with SQL
against the system catalog, and describes how to fix it.

## Troubleshooting guides

| Guide | Description |
|-------|-------------|
| [Slow queries](/serve-results/troubleshooting/slow-queries/) | Find which stage of a query's lifecycle takes the most time, and fix it. Includes a section for self-managed deployments. |
| [Unresponsive queries](/serve-results/troubleshooting/unresponsive-queries/) | Find why a query hangs or never returns, and cancel it. |
| [Expensive queries](/serve-results/troubleshooting/expensive-queries/) | Find queries that use a lot of CPU or memory on a cluster, and reduce their cost. |

## Query history

All three guides use the statement log, which records a sample of the SQL
statements issued against Materialize in the last **24 hours**. You can browse
it in the **Query history** tab of the [Materialize
console](/developer-tools/console/), or query it through
[`mz_internal.mz_recent_activity_log`](/sql/system-catalog/mz_internal/#mz_recent_activity_log).

To query the statement log, connect as a *superuser* or as a user granted the
[`mz_monitor` role](/security/appendix/appendix-built-in-roles/#system-catalog-roles).

Statements are sampled and throttled, so not every statement appears in the
log. In Materialize Cloud, Materialize controls the sample rate and may change
it at any time. In self-managed deployments, the operator sets it.

### Control the sample rate on Materialize Self-Managed

The fraction of statements logged is the smaller of two values:

| Parameter | Scope | Description |
|-----------|-------|-------------|
| `statement_logging_max_sample_rate` | System | Upper bound for every session. `0` disables statement logging. |
| `statement_logging_sample_rate` | Session | Rate the session requests. New sessions start at `statement_logging_default_sample_rate`. |

A higher sample rate makes the log more complete, which helps when you need to
find a specific slow query. The tradeoff is CPU overhead on `environmentd`, which
grows with statement throughput. Separately,
`statement_logging_target_data_rate` caps the bytes written per second, so on a
busy instance some sampled statements are still dropped even at a rate of `1.0`.

To change the system-wide rates, connect as the `mz_system` user and run:

```mzsql
ALTER SYSTEM SET statement_logging_max_sample_rate = 0.5;
ALTER SYSTEM SET statement_logging_default_sample_rate = 0.5;
```

To log every statement in your own session while you debug, run:

```mzsql
SET statement_logging_sample_rate = 1.0;
```

To check the rates in effect:

```mzsql
SHOW statement_logging_max_sample_rate;
SHOW statement_logging_sample_rate;
```

`ALTER SYSTEM SET` takes effect immediately and overrides the Helm chart value.
For the Helm chart settings, storage costs, and how to revert an override, see
[Query History](/self-managed-deployments/query-history/).

For a complete history of DDL statements, use
[`mz_audit_events`](/sql/system-catalog/mz_catalog/#mz_audit_events).

---

## Troubleshooting: Expensive queries

This guide helps you find queries that use a lot of CPU or memory on a
cluster, and how to reduce their cost.

A query that can't be answered from an existing index makes the cluster build a
temporary dataflow, compute the result, and then drop the dataflow. The cluster
does this work on every execution, alongside the work of maintaining its
indexes and materialized views. Expensive queries slow down other queries on
the same cluster, and can make the cluster run out of memory.

## Common causes

- **No usable index**: Frequent queries that join, aggregate, or filter on
  columns without an index build a dataflow on every execution.
- **Ad-hoc queries on a production cluster**: Exploratory queries, such as
  large joins or full scans, compete for CPU and memory with the indexes and
  materialized views that serve your application.
- **Large results**: Queries without filters or limits read and return much
  more data than needed.

## Diagnosing the issue

### Find the most expensive queries

Queries with the `standard` execution strategy built a temporary dataflow. To
find the ones that consumed the most time over the last day, grouped by query
text, query the [statement log](/serve-results/troubleshooting/#query-history):

```mzsql
SELECT
  left(sql, 60) AS sql,
  cluster_name,
  count(*) AS executions,
  round(sum(extract(epoch FROM finished_at - began_at)), 3) AS total_seconds,
  max(result_size) AS max_result_bytes
FROM mz_internal.mz_recent_activity_log
WHERE execution_strategy = 'standard'
  AND cluster_name NOT LIKE 'mz_%'
  AND began_at > now() - INTERVAL '1 day'
GROUP BY sql_hash, sql, cluster_name
ORDER BY total_seconds DESC
LIMIT 10;
```

```nofmt
                             sql                              | cluster_name | executions | total_seconds | max_result_bytes
--------------------------------------------------------------+--------------+------------+---------------+------------------
 SELECT o.customer_id, t.total FROM orders o JOIN order_total | quickstart   |          1 |         0.081 |              234
 SELECT count(*) FROM orders                                  | quickstart   |          1 |         0.026 |               20
 SELECT * FROM order_counts WHERE customer_id = 5             | quickstart   |          1 |         0.015 |               21
```

Look for two patterns:

- A query with many `executions` runs often enough that its total cost adds
  up, even if each execution is fast. Make it a [fast path
  query](#make-frequent-queries-fast-path).
- A query with a high `total_seconds` for few executions is an expensive
  ad-hoc query. [Isolate it](#isolate-ad-hoc-queries) or [reduce the data it
  reads](#return-less-data).

Canceled and failed statements have no `execution_strategy`, so this query
doesn't include them. To find long-running statements that were canceled or
failed, filter on `finished_status IN ('canceled', 'error')` instead.

### Find expensive queries that are running now

Dataflows for queries that are running are currently named
`oneshot-select-<id>`. This name is not a stable interface and can change
between releases. To see how much CPU time each one has used, run the
following on the cluster that runs the queries:

```mzsql
SET cluster = quickstart;

SELECT
  mdo.name,
  mse.elapsed_ns / 1000 * '1 MICROSECONDS'::interval AS elapsed_time
FROM mz_introspection.mz_scheduling_elapsed AS mse,
  mz_introspection.mz_dataflow_operators AS mdo,
  mz_introspection.mz_dataflow_addresses AS mda
WHERE mse.id = mdo.id
  AND mdo.id = mda.id
  AND list_length(mda.address) = 1
  AND mdo.name LIKE 'Dataflow: oneshot-select-%'
ORDER BY mse.elapsed_ns DESC;
```

```nofmt
             name              |  elapsed_time
-------------------------------+-----------------
 Dataflow: oneshot-select-t176 | 00:00:35.980703
 Dataflow: oneshot-select-t190 | 00:00:14.433187
```

To find the query text and cancel a running query, see [Find running
queries](/serve-results/troubleshooting/unresponsive-queries/#find-running-queries).

### Compare with the cost of indexes and materialized views

To see how the CPU and memory of your indexes and materialized views compare,
run [`EXPLAIN ANALYZE CLUSTER`](/sql/explain-analyze/#explain-analyze-cluster-)
on the cluster:

```mzsql
EXPLAIN ANALYZE CLUSTER CPU, MEMORY;
```

If the indexes and materialized views account for most of the cluster's CPU and
memory, the queries are not the main cost. To see which operators of an index
or materialized view use the most resources, see [`EXPLAIN
ANALYZE`](/sql/explain-analyze/) and [Dataflow
troubleshooting](/transform-data/dataflow-troubleshooting/).

### Check the query plan

Run [`EXPLAIN`](/sql/explain-plan/) on an expensive query to see what the
dataflow does:

```mzsql
EXPLAIN SELECT o.customer_id, t.total
FROM orders o
JOIN order_totals t USING (customer_id)
WHERE o.id < 10;
```

Look for operators that read full collections, such as joins without a
matching index, or `Read` operators on large sources or materialized views.

## Resolution

### Make frequent queries fast path

A query that reads from an index and applies only filters and projections
doesn't build a dataflow. `EXPLAIN` shows `Explained Query (fast path)` for
these queries.

- Create an [index](/fundamentals/concepts/indexes/) on the columns that the
  query filters on.
- Move joins and aggregations into a view, and index the view on the lookup
  key. For example:

  ```mzsql
  CREATE VIEW order_totals AS
    SELECT customer_id, sum(amount) AS total
    FROM orders
    GROUP BY customer_id;

  CREATE INDEX order_totals_idx ON order_totals (customer_id);

  -- Fast path lookup
  SELECT * FROM order_totals WHERE customer_id = 5;
  ```

- Run the query on the same cluster as the index. Indexes are local to a
  cluster.

For more techniques, see [Optimization](/transform-data/optimization/).

### Isolate ad-hoc queries

Run exploratory queries on a separate cluster, so they can't slow down or
crash the cluster that serves your application:

```mzsql
CREATE CLUSTER adhoc (SIZE = '25cc');
SET cluster = adhoc;
```

For guidance on how to split work across clusters, see [Operational
guidelines](/clusters/operational-guidelines/).

### Return less data

- Add filters, and use [temporal
  filters](/transform-data/patterns/temporal-filters/) on timestamp columns.
  Materialize can skip over old data in storage that doesn't match the filter.
- Add a `LIMIT` clause to exploratory queries.
- Select only the columns you need.

The `max_query_result_size` [configuration
parameter](/sql/set/#other-configuration-parameters) makes a query fail if its
result exceeds the limit. It doesn't limit the memory that the temporary
dataflow uses to compute the result.

### Size up the cluster

If the queries are already optimized, [size up the
cluster](/sql/alter-cluster/) to give it more CPU and memory.

---

## Troubleshooting: Slow queries

This guide helps you find out why a query takes longer than expected to return
results, and how to fix it.

## Common causes

- **Lagging dependencies**: A materialized view, index, or source that the query
  reads from is behind. Materialize waits for it to catch up before it returns
  a consistent result.
- **No usable index**: The query can't be answered from an existing index, so
  Materialize builds a temporary dataflow or reads from storage for every
  execution.
- **Busy cluster**: Other work on the cluster, such as maintaining indexes and
  materialized views or running other queries, is using the CPU.
- **Transactions**: All statements in a transaction run at the same timestamp,
  so a fast object can wait for a slower one.
- **Large results or client distance**: Transmitting a large result, or a long
  network path between the client and Materialize, adds latency after the query
  has executed.

## Diagnosing the issue

### Find slow queries

List the slowest queries of the last hour from the [statement
log](/serve-results/troubleshooting/#query-history):

```mzsql
SELECT
  left(sql, 60) AS sql,
  cluster_name,
  execution_strategy,
  finished_at - began_at AS duration
FROM mz_internal.mz_recent_activity_log
WHERE statement_type = 'select'
  AND finished_status = 'success'
  AND cluster_name NOT LIKE 'mz_%'
  AND began_at > now() - INTERVAL '1 hour'
ORDER BY duration DESC
LIMIT 10;
```

```nofmt
                             sql                              | cluster_name | execution_strategy |   duration
--------------------------------------------------------------+--------------+--------------------+--------------
 SELECT o.customer_id, t.total FROM orders o JOIN order_total | quickstart   | standard           | 00:00:00.081
 SELECT count(*) FROM orders                                  | quickstart   | standard           | 00:00:00.026
 SELECT * FROM order_counts WHERE customer_id = 5             | quickstart   | standard           | 00:00:00.015
 SELECT * FROM order_totals WHERE customer_id = 5             | quickstart   | fast-path          | 00:00:00.005
```

The `execution_strategy` column shows how Materialize executed the query:

| Strategy | Meaning |
|----------|---------|
| `fast-path` | The cluster read the result directly from an existing index, without building a dataflow. |
| `persist-fast-path` | The cluster read the result directly from storage, without building a dataflow. Materialize uses this for [small `LIMIT` queries](#return-less-data). |
| `standard` | The cluster built a temporary dataflow to compute the result, then dropped it. |
| `constant` | Materialize computed the result without a cluster. |

The query only lists successful statements. Canceled and failed statements
have no `execution_strategy`. To include them, remove the `finished_status`
filter.

The **Query history** tab in the [Materialize
console](/developer-tools/console/) shows the same information, and lets you
filter and sort statements by duration.

### Break down where the time goes

[`mz_statement_lifecycle_history`](/sql/system-catalog/mz_internal/#mz_statement_lifecycle_history)
records when each query reaches each stage of its lifecycle. Use it to split a
query's duration into stages:

```mzsql
WITH events AS (
  SELECT
    statement_id,
    max(occurred_at) FILTER (WHERE event_type = 'execution-began') AS began,
    max(occurred_at) FILTER (WHERE event_type = 'optimization-finished') AS optimized,
    max(occurred_at) FILTER (WHERE event_type = 'storage-dependencies-finished') AS storage_ready,
    max(occurred_at) FILTER (WHERE event_type = 'compute-dependencies-finished') AS compute_ready,
    max(occurred_at) FILTER (WHERE event_type = 'execution-finished') AS finished
  FROM mz_internal.mz_statement_lifecycle_history
  WHERE occurred_at > now() - INTERVAL '1 hour'
  GROUP BY statement_id
)
SELECT
  left(a.sql, 40) AS sql,
  a.execution_strategy,
  e.optimized - e.began AS optimization,
  greatest(e.storage_ready, e.compute_ready) - e.optimized AS dependency_wait,
  e.finished - greatest(e.storage_ready, e.compute_ready) AS execution,
  e.finished - e.began AS total
FROM mz_internal.mz_recent_activity_log AS a
JOIN events AS e ON e.statement_id = a.execution_id
WHERE a.statement_type = 'select'
  AND a.cluster_name NOT LIKE 'mz_%'
  AND a.began_at > now() - INTERVAL '1 hour'
ORDER BY total DESC
LIMIT 10;
```

```nofmt
                   sql                    | execution_strategy | optimization | dependency_wait |  execution   |    total
------------------------------------------+--------------------+--------------+-----------------+--------------+--------------
 SELECT o.customer_id, t.total FROM order | standard           | 00:00:00.006 | 00:00:00.001    | 00:00:00.074 | 00:00:00.081
 SELECT count(*) FROM orders              | standard           | 00:00:00.007 | 00:00:00        | 00:00:00.019 | 00:00:00.026
 SELECT * FROM order_counts WHERE custome | standard           | 00:00:00.003 | 00:00:00        | 00:00:00.012 | 00:00:00.015
 SELECT * FROM order_totals WHERE custome | fast-path          | 00:00:00.003 | 00:00:00.001    | 00:00:00.001 | 00:00:00.005
```

Use the stage that dominates to pick a resolution:

| Stage | What happens | Resolution |
|-------|--------------|------------|
| `optimization` | Materialize parses, plans, and optimizes the query, and picks a timestamp. With [real-time recency](/sql/set/#other-configuration-parameters) enabled, this includes waiting for the latest upstream offsets. | Simplify the query, or [index a view](#use-an-index) that performs the complex part. In self-managed deployments, see [Check `environmentd`](#check-environmentd). |
| `dependency_wait` | Materialize waits for the sources, tables, materialized views, and indexes the query reads from to catch up to the chosen timestamp. | [Fix lagging dependencies](#fix-lagging-dependencies). |
| `execution` | The cluster computes the result and returns it to Materialize. Sending the rows to the client is not included. | [Use an index](#use-an-index), [reduce cluster load](#reduce-cluster-load), or [return less data](#return-less-data). |

If `total` is small but your client reports a much higher latency, the time is
spent outside of Materialize. See [Reduce client-side
latency](#reduce-client-side-latency).

### Check for lagging dependencies

To see how far behind each of your objects is, query
[`mz_wallclock_global_lag`](/sql/system-catalog/mz_internal/#mz_wallclock_global_lag):

```mzsql
SELECT o.name, o.type, l.lag
FROM mz_internal.mz_wallclock_global_lag AS l
JOIN mz_catalog.mz_objects AS o ON o.id = l.object_id
WHERE o.id LIKE 'u%'
ORDER BY l.lag DESC NULLS LAST
LIMIT 10;
```

A lag of a few seconds is expected. Lag that is much higher, or that keeps
growing, means the object can't keep up with its inputs. To see lag visually,
open the object's workflow graph in the console: click **Clusters**, select the
cluster, select the object under **Materialized Views** or **Indexes**, then
open the **Workflow** tab.

To find why an object is lagging, see [Freshness
troubleshooting](/transform-data/freshness-troubleshooting/) and [Dataflow
troubleshooting](/transform-data/dataflow-troubleshooting/). For a lagging
source, see [Troubleshoot ingestion](/ingest-data/troubleshooting/).

### Check the query plan

Run [`EXPLAIN`](/sql/explain-plan/) on the query, on the cluster where the
query runs:

```mzsql
EXPLAIN SELECT * FROM order_totals WHERE customer_id = 5;
```

```nofmt
Explained Query (fast path):
  →Map/Filter/Project
    Project: #0, #1
    →Index Lookup on materialize.public.order_totals (using materialize.public.order_totals_idx)
      Lookup values: (5)

Used Indexes:
  - materialize.public.order_totals_idx (lookup)

Target cluster: quickstart
```

`Explained Query (fast path)` means that no dataflow is built: an `Index
Lookup` or `Indexed` operator reads from an index, and `ReadStorage` reads from
storage. A plan without `(fast path)` means Materialize builds a temporary
dataflow on every execution, even if the plan lists `Used Indexes`.

### Check cluster utilization

A cluster near 100% CPU delays every query that runs on it:

```mzsql
SELECT c.name AS cluster, r.name AS replica, u.process_id, u.cpu_percent, u.memory_percent
FROM mz_internal.mz_cluster_replica_utilization AS u
JOIN mz_catalog.mz_cluster_replicas AS r ON r.id = u.replica_id
JOIN mz_catalog.mz_clusters AS c ON c.id = r.cluster_id
WHERE c.name = 'quickstart';
```

You can also see CPU and memory for each cluster under **Clusters** in the
console.

## Resolution

### Fix lagging dependencies

- To find and fix the cause of lag in a materialized view or index, see
  [Freshness troubleshooting](/transform-data/freshness-troubleshooting/) and
  [Dataflow troubleshooting](/transform-data/dataflow-troubleshooting/). For a
  lagging source, see [Troubleshoot ingestion](/ingest-data/troubleshooting/).
- Avoid chaining materialized views where you don't need to. Each materialized
  view in a chain adds a small amount of lag to the next one.
- If you don't need [strict serializable](/serve-results/isolation-level/)
  results, use the `serializable` isolation level. Materialize can then serve
  results at the latest timestamp that all inputs can already serve, instead
  of waiting for the lagging object. The whole result is then as stale as the
  most lagging input.
- If you run queries inside a transaction, see [Avoid
  transactions](#avoid-unnecessary-transactions).
- If the dependencies can't keep up with their inputs, [size up the
  cluster](/sql/alter-cluster/) that maintains them.

### Use an index

- If the objects the query reads from don't have an
  [index](/fundamentals/concepts/indexes/), create one on the key the query filters or joins
  on. See [Optimization](/transform-data/optimization/).
- Run the query on the same cluster as the index. Indexes are local to a
  cluster.
- Make the index key match how you query the data. For example, a filter on
  `customer_id` needs an index on `customer_id`.
- Move joins and aggregations out of the query and into a view, then index the
  view. The query becomes a lookup against an existing index.

### Reduce cluster load

- Move queries that build dataflows onto a separate cluster, so that they don't
  compete with indexes and materialized views for CPU. Indexes are local to a
  cluster, so a query that uses an index on the original cluster can become
  more expensive on the new one. See [Expensive
  queries](/serve-results/troubleshooting/expensive-queries/).
- [Size up the cluster](/sql/alter-cluster/).

### Return less data

- Filter results with [temporal
  filters](/transform-data/patterns/temporal-filters/). Materialize can skip
  over old data in storage that doesn't match the filter.
- Add a `LIMIT` clause to exploratory queries. A query that selects from a
  single source, table, or materialized view with only simple filters and
  projections, no ordering, and a `LIMIT` plus `OFFSET` below 25 reads directly
  from storage. `EXPLAIN` shows
  `Explained Query (fast path)` for these queries.
- Select only the columns you need. A large `result_size` in
  `mz_recent_activity_log` adds time to transmit the result.

### Avoid unnecessary transactions

All statements in a [transaction](/sql/begin/) run at the same timestamp, and
that timestamp must be valid for every object the transaction may access. As a
result, a query against a fast object can wait for a slower object in the same
schema.

- Don't use transactions for single statements.
- Check whether your SQL library or ORM wraps every query in a transaction, and
  disable that behavior.

### Reduce client-side latency

Run clients in the same cloud region as your Materialize region. For example,
if your Materialize region is in AWS `us-east-1`, run your client in AWS
`us-east-1`. To reuse connections instead of opening a new one for each query,
see [Connection pooling](/serve-results/connection-pooling/).

## Self-managed deployments

In self-managed deployments, you also operate the components between the client
and the cluster: `balancerd`, which terminates TLS and proxies connections, and
`environmentd`, which plans every query and dispatches it to a cluster. Either
can add latency that doesn't show up in cluster metrics.

### Make sure statement logging is enabled

The steps above need the statement log. Operator Helm chart versions earlier
than v26.40.0 disable statement logging. To check:

```mzsql
SHOW statement_logging_max_sample_rate;
```

If the result is `0`, the statement log is empty. To enable statement logging
and understand its cost, see [Query
History](/self-managed-deployments/query-history/).

### Attribute latency to a component

Compare three measurements over the same time window. Each one covers a smaller
part of the query path, so the gap between two of them tells you where the
time goes.

| Measurement | Covers |
|-------------|--------|
| Latency reported by your client | The full round trip: client, network, `balancerd`, `environmentd`, and the cluster. |
| `finished_at - began_at` in `mz_recent_activity_log` | `environmentd` and the cluster. |
| [`mz_compute_peek_duration_seconds`](/observability/essential-metrics/#compute-metrics) | From when `environmentd` sends the query to the cluster until the result arrives. This includes waiting for dependencies and, for `standard` queries, building the temporary dataflow. |

To compute the average statement log latency over the last minute:

```mzsql
SELECT
  count(*) AS statements,
  round(avg(extract(epoch FROM finished_at - began_at)) * 1000, 1) AS avg_ms,
  round(max(extract(epoch FROM finished_at - began_at)) * 1000, 1) AS max_ms
FROM mz_internal.mz_recent_activity_log
WHERE began_at > now() - INTERVAL '1 minute'
  AND statement_type = 'select'
  AND finished_status = 'success'
  AND cluster_name NOT LIKE 'mz_%';
```

Then compare:

- **Client latency is much higher than the statement log**: The time is spent
  in the client, the network, or `balancerd`. See [Check
  `balancerd`](#check-balancerd) and [Check the client](#check-the-client).
- **Statement log latency is much higher than peek duration**: The time is
  spent in `environmentd` before the query reaches the cluster, for example in
  optimization or timestamp selection. See [Check
  `environmentd`](#check-environmentd).
- **Peek duration is high**: Use the [lifecycle
  breakdown](#break-down-where-the-time-goes) to see whether the query waits for
  dependencies or for execution on the cluster, then follow the steps in
  [Resolution](#resolution).

`mz_compute_peek_duration_seconds` has an `instance_id` label that holds the
cluster ID. Filter on it to compare the same clusters as the statement log
query, which excludes system clusters.

To collect `mz_compute_peek_duration_seconds` and other Prometheus metrics, see
[Grafana](/observability/self-managed/grafana/).

### Check `environmentd`

Every query passes through `environmentd`. Watch the CPU of the `environmentd`
pod while queries are slow. If it is saturated, or throttled by a CPU limit,
while cluster CPU is low, give `environmentd` more CPU with
`environmentdResourceRequirements` in the Materialize custom resource. See
[Materialize CRD field
descriptions](/self-managed-deployments/materialize-crd-field-descriptions/).
Applying the change rolls out a new `environmentd`. With the `v1alpha1` CRD,
also set `requestRollout` to a new UUID, or the operator does not roll out the
change. See [Modifying the custom
resource](/self-managed-deployments/#modifying-the-custom-resource).

### Check `balancerd`

`balancerd` handles every byte of every connection.

- Don't set CPU limits on `balancerd` pods, and run at least two replicas.
- Its memory use grows with the number of connections. Check the pods' restart
  count: a `balancerd` pod that is killed for running out of memory causes
  connection errors and latency spikes.

> **Warning:** A CPU-throttled pod can look idle on CPU usage graphs, because usage never
> exceeds the configured limit. To detect throttling, check the
> `container_cpu_cfs_throttled_periods_total` metric from cAdvisor instead of CPU
> usage.

### Check the client

- Don't set CPU limits on load-testing or client processes. A throttled client
  queues requests and reports the queueing time as query latency.
- Don't measure through `kubectl port-forward` or SSH tunnels. They cap
  throughput far below what the deployment can serve.
- Run the client in the same region and network as Materialize.

---

## Troubleshooting: Unresponsive queries

This guide helps you find out why a query hangs or doesn't return results, and
how to fix it.

A query that reads from an object that can't serve results yet waits until the
object is ready. This is how Materialize makes sure that every result is
consistent.

## Common causes

- **Snapshotting source**: A new source must read a snapshot of the existing
  upstream data before queries on it return.
- **Stalled source**: A source has stopped ingesting data, so its dependencies
  can't advance.
- **Hydrating objects**: After an index or materialized view is created, or its
  cluster restarts or is resized, Materialize rebuilds the object's state.
  Queries that read from it wait until *hydration* finishes.
- **Unhealthy cluster**: The cluster is out of memory and restarting, or its
  CPU is saturated.

If none of these causes applies, the query may be running, just slowly. See
[Slow queries](/serve-results/troubleshooting/slow-queries/).

## Diagnosing the issue

### Find running queries

List the queries that are still running, from the [statement
log](/serve-results/troubleshooting/#query-history):

```mzsql
SELECT
  a.execution_id,
  s.connection_id,
  a.cluster_name,
  now() - a.began_at AS running_for,
  left(a.sql, 60) AS sql
FROM mz_internal.mz_recent_activity_log AS a
JOIN mz_internal.mz_sessions AS s ON s.id = a.session_id
WHERE a.finished_at IS NULL
ORDER BY a.began_at;
```

```nofmt
             execution_id             | connection_id | cluster_name | running_for  |                             sql
--------------------------------------+---------------+--------------+--------------+--------------------------------------------------------------
 01a0ee6a-3442-7115-a3bb-f502ad3e5a30 |    1518224533 | quickstart   | 00:00:06.021 | SELECT count(*) FROM orders a, orders b WHERE a.amount + b.a
```

Note the `connection_id`. You need it to [cancel the
query](#cancel-the-query).

The statement log is sampled and written in batches, so a running query may
not appear here, especially if it started only a few seconds ago.

### Check for snapshotting sources

```mzsql
SELECT s.name, s.type, st.snapshot_committed
FROM mz_internal.mz_source_statistics AS st
JOIN mz_catalog.mz_sources AS s ON s.id = st.id
WHERE s.id LIKE 'u%'
  AND NOT st.snapshot_committed;
```

Any source in the result is still snapshotting, and queries that depend on it
wait until the snapshot completes.

### Check for stalled sources

```mzsql
SELECT name, type, status, error
FROM mz_internal.mz_source_statuses
WHERE id LIKE 'u%'
  AND status IN ('stalled', 'paused');
```

A source in the result isn't ingesting data. The `error` column shows why.

### Check for hydrating objects

```mzsql
SELECT o.name, o.type, r.name AS replica
FROM mz_internal.mz_hydration_statuses AS h
JOIN mz_catalog.mz_objects AS o ON o.id = h.object_id
JOIN mz_catalog.mz_cluster_replicas AS r ON r.id = h.replica_id
WHERE h.hydrated IS NOT TRUE;
```

Any object in the result is still hydrating on that replica. You can also see
hydration status on the object's workflow graph in the console: click
**Clusters**, select the cluster, select the object under **Materialized
Views** or **Indexes**, then open the **Workflow** tab.

### Check cluster health

Check whether the cluster's replicas restarted recently:

```mzsql
SELECT c.name AS cluster, rh.replica_name AS replica, h.status, h.reason, h.occurred_at
FROM mz_internal.mz_cluster_replica_status_history AS h
JOIN mz_internal.mz_cluster_replica_history AS rh ON rh.replica_id = h.replica_id
JOIN mz_catalog.mz_clusters AS c ON c.id = rh.cluster_id
WHERE h.occurred_at > now() - INTERVAL '1 day'
ORDER BY h.occurred_at DESC
LIMIT 10;
```

A status of `offline` with reason `oom-killed` means the replica ran out of
memory and restarted. Queries running on it restart from the beginning. If the
query itself caused the out-of-memory error, the replica restarts in a loop
until you [cancel the query](#cancel-the-query).

To check CPU and memory utilization, see [Check cluster
utilization](/serve-results/troubleshooting/slow-queries/#check-cluster-utilization).

## Resolution

### Cancel the query

Cancel a running query with
[`pg_cancel_backend`](/sql/functions/#pg_cancel_backend), using the
`connection_id` from [Find running queries](#find-running-queries):

```mzsql
SELECT pg_cancel_backend(1518224533);
```

The statement log then records the query with `finished_status = 'canceled'`.
The cluster can take a while to tear down the query's dataflow, so its CPU and
memory usage may stay high for some time after you cancel it.

### Wait for the snapshot or hydration

Snapshotting and hydration take time proportional to data volume and query
complexity. They finish on their own.

- To make snapshots and hydration faster, size up the cluster. See [Optimize
  hydration requirements](/clusters/optimize-hydration-requirements/).
- On Materialize Cloud, clusters also rehydrate after restarts during the
  [routine maintenance window](/releases/schedule/#cloud-upgrade-schedule).
- To learn more about hydration, see
  [Hydration](/fundamentals/concepts/hydration/).

### Fix the source

To fix a stalled source, see [Troubleshoot
ingestion](/ingest-data/troubleshooting/).

### Fix the cluster

- If your query caused the cluster to run out of memory or saturate its CPU,
  cancel it, then reduce its cost. See [Expensive
  queries](/serve-results/troubleshooting/expensive-queries/).
- If other work on the cluster caused it, wait for that work to finish, run
  the query on a different cluster, or [size up the
  cluster](/sql/alter-cluster/).
- To get notified before a cluster reaches its capacity, set up
  [alerting](/observability/cloud/alerting/#thresholds).

