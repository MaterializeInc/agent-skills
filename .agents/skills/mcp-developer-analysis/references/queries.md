# Diagnostic Queries Reference

All queries in this file target system catalog tables and run through the MCP
`query_system_catalog` tool, except where a heading says `query`. Use the
`query` tool for cluster-bound operations: `EXPLAIN ANALYZE` on a materialized
view or index, reading user data, and every `mz_introspection` relation. The
`query` tool exists from Materialize v26.30 and takes a required `cluster`
argument; from v26.33 it also takes `cluster_replica`, required for any
`mz_introspection` read on a cluster with more than one replica.

`SKILL.md` states the tool constraints in full. Three of them shape every query
below: rows come back with no column names, so every `AS` alias here is
discarded and you map columns positionally (and `timestamp` columns arrive as
epoch milliseconds unless cast to `text`, which the queries below do); a
response is capped at 1 MB, so
narrow or `LIMIT` anything that could enumerate a whole large catalog; and a
`cluster` argument passed to `query_system_catalog` is silently ignored, so a
cluster-scoped query there answers about the session's default cluster
instead, quietly when that cluster has one replica and with an error otherwise
(`SKILL.md`, Critical Rules). Runtime relations such as `mz_frontiers` and
`mz_compute_exports` are keyed by GlobalId, which equals `mz_objects.id` for
every object as created and for a materialized view after an applied
replacement; a table altered with `ADD COLUMN` keeps its id and gains a
GlobalId per version (`mz_internal.mz_object_global_ids`), so the direct
joins below show its first version, which shares the table's persist shard
and frontier. Joining through `mz_object_global_ids` instead lists retired
versions too.

**Important column name notes:**
- `mz_source_statuses` and `mz_sink_statuses` use `last_status_change_at` (NOT `updated_at`)
- `mz_cluster_replica_statuses` uses `updated_at`
- `mz_cluster_replica_utilization` carries no cluster or replica *name* — JOIN
  `mz_cluster_replicas` and `mz_clusters` to get them. It is keyed by
  `(replica_id, process_id)`, so aggregate or filter by process on
  multi-process sizes.
- When unsure, run `SHOW COLUMNS FROM <table>` first

---

## Environment Overview

### Version
`query_system_catalog` rejects a `SELECT` that references no system catalog
table, so the version probe needs a `FROM`.

```sql
SELECT mz_version() FROM mz_catalog.mz_databases LIMIT 1
```

### Clusters and Replicas
LEFT JOIN, not JOIN: a cluster without replicas has no replica rows, and an
inner join makes it invisible. Count the replica rows rather than reading
`replication_factor`, which is NULL on unmanaged clusters and counts only
billed replicas.

```sql
SELECT
    c.name AS cluster_name,
    c.managed,
    c.size,
    c.replication_factor,
    r.name AS replica_name,
    r.size AS replica_size,
    (i.id IS NOT NULL) AS unbilled
FROM mz_catalog.mz_clusters c
LEFT JOIN mz_catalog.mz_cluster_replicas r ON c.id = r.cluster_id
LEFT JOIN mz_internal.mz_internal_cluster_replicas i ON i.id = r.id
ORDER BY c.name, r.name
```

### Cluster Topology
One row per cluster, zero-replica clusters included, with the replica count,
the replica sizes (an unmanaged cluster has NULL `size` and can mix sizes),
the unbilled support replicas, and the highest current replica memory percent
that the report template's Cluster Topology table asks for. Judge zero
replicas on user clusters (`c.id LIKE
'u%'`): system clusters can legitimately have no replicas (the Emulator
ships every one but `mz_catalog_server` that way), and none of them takes a
`cluster` argument usefully: `mz_system` refuses queries, `mz_probe`,
`mz_support` and `mz_analytics` deny `USAGE`, and `mz_catalog_server` refuses
user objects.

```sql
SELECT
    c.name AS cluster_name,
    c.managed,
    c.size,
    string_agg(DISTINCT r.size, ', ') AS replica_sizes,
    c.replication_factor,
    count(DISTINCT r.id) AS replicas,
    count(DISTINCT i.id) AS unbilled_replicas,
    max(u.memory_percent) AS max_memory_percent
FROM mz_catalog.mz_clusters c
LEFT JOIN mz_catalog.mz_cluster_replicas r ON r.cluster_id = c.id
LEFT JOIN mz_internal.mz_internal_cluster_replicas i ON i.id = r.id
LEFT JOIN mz_internal.mz_cluster_replica_utilization u ON u.replica_id = r.id
GROUP BY c.name, c.managed, c.size, c.replication_factor
ORDER BY c.name
```

### Schemas
```sql
SELECT
    d.name AS database_name,
    s.name AS schema_name
FROM mz_catalog.mz_schemas s
JOIN mz_catalog.mz_databases d ON s.database_id = d.id
WHERE s.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY d.name, s.name
```

---

## Object Inventory

### Sources
`mz_sources` has a row for every subsource and `progress` collection too, so
this returns many more rows than the user would call sources. Add
`AND s.type NOT IN ('subsource', 'progress')` before reporting a count.

```sql
SELECT
    s.name AS source_name,
    sc.name AS schema_name,
    s.type AS source_type,
    c.name AS cluster_name
FROM mz_catalog.mz_sources s
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
LEFT JOIN mz_catalog.mz_clusters c ON s.cluster_id = c.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY s.name
```

### Materialized Views
```sql
SELECT
    mv.name AS mv_name,
    sc.name AS schema_name,
    c.name AS cluster_name
FROM mz_catalog.mz_materialized_views mv
JOIN mz_catalog.mz_schemas sc ON mv.schema_id = sc.id
JOIN mz_catalog.mz_clusters c ON mv.cluster_id = c.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY mv.name
```

### Views (non-materialized)
```sql
SELECT
    v.name AS view_name,
    sc.name AS schema_name
FROM mz_catalog.mz_views v
JOIN mz_catalog.mz_schemas sc ON v.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY v.name
```

### Sinks
```sql
SELECT
    sk.name AS sink_name,
    sc.name AS schema_name,
    sk.type AS sink_type,
    c.name AS cluster_name
FROM mz_catalog.mz_sinks sk
JOIN mz_catalog.mz_schemas sc ON sk.schema_id = sc.id
LEFT JOIN mz_catalog.mz_clusters c ON sk.cluster_id = c.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY sk.name
```

### Indexes
```sql
SELECT
    i.name AS index_name,
    o.name AS on_object,
    sc.name AS schema_name,
    c.name AS cluster_name
FROM mz_catalog.mz_indexes i
JOIN mz_catalog.mz_objects o ON i.on_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
JOIN mz_catalog.mz_clusters c ON i.cluster_id = c.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY i.name
```

### Connections
```sql
SELECT
    conn.name AS connection_name,
    sc.name AS schema_name,
    conn.type AS connection_type
FROM mz_catalog.mz_connections conn
JOIN mz_catalog.mz_schemas sc ON conn.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY conn.name
```

---

## Object Definitions

Pull the actual SQL definitions to analyze query patterns, join strategies, and
optimization opportunities.

### Materialized View Definitions
```sql
SELECT
    sc.name AS schema_name,
    mv.name AS mv_name,
    mv.definition
FROM mz_catalog.mz_materialized_views mv
JOIN mz_catalog.mz_schemas sc ON mv.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY sc.name, mv.name
```

### View Definitions (non-materialized)
```sql
SELECT
    sc.name AS schema_name,
    v.name AS view_name,
    v.definition
FROM mz_catalog.mz_views v
JOIN mz_catalog.mz_schemas sc ON v.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY sc.name, v.name
```

### Index Definitions
Note: `mz_indexes` does not have a `definition` column — use `create_sql` for
the full DDL. `mz_sources` is the same. `mz_views` and `mz_materialized_views`
*do* have `definition`.

```sql
SELECT
    sc.name AS schema_name,
    i.name AS index_name,
    o.name AS on_object,
    o.type AS on_type,
    c.name AS cluster_name,
    i.create_sql
FROM mz_catalog.mz_indexes i
JOIN mz_catalog.mz_objects o ON i.on_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
JOIN mz_catalog.mz_clusters c ON i.cluster_id = c.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY sc.name, i.name
```

### Source Definitions
```sql
SELECT
    sc.name AS schema_name,
    s.name AS source_name,
    s.type AS source_type,
    s.create_sql
FROM mz_catalog.mz_sources s
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY sc.name, s.name
```

---

## Index Advice and Query Activity

### Index Advice (built-in optimizer)
```sql
SELECT
    o.name AS object_name,
    o.type AS object_type,
    sc.name AS schema_name,
    ia.hint,
    ia.details
FROM mz_internal.mz_index_advice ia
JOIN mz_catalog.mz_objects o ON ia.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY ia.hint, o.name
```

Hint types — these six are the whole set, so do not filter on a subset:
- `keep` — the object is needed as-is
- `drop unless queried directly` — fewer than two downstream dependencies (or
  none at all, or an index on a source); only useful if SELECT queries hit it
- `convert to a view` — MV can be dematerialized entirely, saving its
  arrangement memory
- `convert to a view with an index` — MV can be a view, but keep its indexes
- `convert to materialized view` — a view with indexes on more than one cluster
  should be an MV instead
- `add index` — object would benefit from an index

### Summary by Hint Type
```sql
SELECT
    ia.hint,
    COUNT(*) AS object_count
FROM mz_internal.mz_index_advice ia
JOIN mz_catalog.mz_objects o ON ia.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
GROUP BY ia.hint
ORDER BY object_count DESC
```

---

## Cost Analysis

### Credit Rates per Cluster Size
```sql
SELECT size, credits_per_hour
FROM mz_catalog.mz_cluster_replica_sizes
ORDER BY credits_per_hour
```

### Current Compute Cost per Cluster
Monthly credits per cluster projected from the replicas running right now
(730 hours/month), not a past month's spend.

Price the replicas, not the cluster: each replica row carries its own size,
so summing `credits_per_hour` over `mz_cluster_replicas` covers managed and
unmanaged clusters alike, mixed sizes included, with no `replication_factor`
(NULL on unmanaged clusters; multiplying by it on top of a replica join counts
a cluster twice). Support-created replicas
(`mz_internal.mz_internal_cluster_replicas`) are unbilled, so they are
excluded here, though they still run, still show in utilization, and still
count toward the replica rules; `replica_sizes` lists every replica,
`billed_replicas` and the credits only the billed ones. The LEFT JOIN keeps
zero-replica clusters at 0. System clusters (`s` ids: `mz_system`, `mz_catalog_server`, `mz_probe`,
`mz_support`, `mz_analytics`) are not billed, so both queries keep user
clusters only; `quickstart` is a user cluster. Credits are a Cloud billing
unit; on self-managed the shipped sizes carry Cloud's numbers and
operator-defined sizes carry whatever the operator set (the Helm template
defaults to 0.0), so treat them as relative weights at best and say so when
they read 0.

```sql
SELECT
    c.name AS cluster_name,
    c.managed,
    string_agg(DISTINCT r.size, ', ') AS replica_sizes,
    count(r.id) FILTER (WHERE i.id IS NULL) AS billed_replicas,
    coalesce(sum(s.credits_per_hour), 0) AS cluster_credits_per_hour,
    (coalesce(sum(s.credits_per_hour), 0) * 730)::numeric(10,1) AS monthly_credits
FROM mz_catalog.mz_clusters c
LEFT JOIN mz_catalog.mz_cluster_replicas r ON r.cluster_id = c.id
LEFT JOIN mz_internal.mz_internal_cluster_replicas i ON i.id = r.id
LEFT JOIN mz_catalog.mz_cluster_replica_sizes s ON s.size = r.size AND i.id IS NULL
WHERE c.id LIKE 'u%'
GROUP BY c.name, c.managed
ORDER BY cluster_credits_per_hour DESC
```

### Total Monthly Compute Cost
A projection from the replicas running right now (current rate times 730
hours), not the spend of any past month.

```sql
SELECT
    coalesce(sum(s.credits_per_hour), 0)::numeric(10,2) AS total_credits_per_hour,
    (coalesce(sum(s.credits_per_hour), 0) * 730)::numeric(10,1) AS total_monthly_credits
FROM mz_catalog.mz_clusters c
JOIN mz_catalog.mz_cluster_replicas r ON r.cluster_id = c.id
LEFT JOIN mz_internal.mz_internal_cluster_replicas i ON i.id = r.id
JOIN mz_catalog.mz_cluster_replica_sizes s ON s.size = r.size
WHERE c.id LIKE 'u%' AND i.id IS NULL
```

---

## Performance: Freshness / Lag

### Materialization Lag
`local_lag` and `global_lag` are plain `interval`s, so they sort and compare
directly. `slowest_global_input_id` names the input that is holding the object
back.

```sql
SELECT
    o.name AS object_name,
    o.type AS object_type,
    sc.name AS schema_name,
    l.local_lag,
    l.global_lag,
    si.name AS slowest_global_input
FROM mz_internal.mz_materialization_lag l
JOIN mz_catalog.mz_objects o ON l.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
LEFT JOIN mz_catalog.mz_objects si ON l.slowest_global_input_id = si.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY l.global_lag DESC NULLS LAST
LIMIT 30
```

### Write Frontiers (sorted oldest first)

`write_frontier` lives on `mz_internal.mz_frontiers` and is of type
`mz_timestamp` (milliseconds since epoch). You cannot subtract it from `now()`,
and `::bigint` fails with `CAST does not support casting from mz_timestamp to
bigint`; it casts to `text`, `timestamp` and `timestamptz`, so
`write_frontier::timestamptz::text` is the readable form (without the `::text`
the tools return it as epoch milliseconds again) and `write_frontier::text` the
raw millisecond number. Sort ascending to
find the most-lagging objects. A frontier of `0` means the object has never
been written, not that it was written in 1970.

```sql
SELECT
    o.name AS object_name,
    o.type AS object_type,
    sc.name AS schema_name,
    f.write_frontier::text AS write_frontier,
    f.write_frontier::timestamptz::text AS frontier_time
FROM mz_internal.mz_frontiers f
JOIN mz_catalog.mz_objects o ON f.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
  AND f.write_frontier IS NOT NULL
ORDER BY f.write_frontier ASC
LIMIT 30
```

### Source Status and Freshness
Driven from `mz_source_statuses`, which carries a row per source-fed table
(`type = 'table'`) as well as per source and subsource; a join from
`mz_sources` would hide every `CREATE TABLE ... FROM SOURCE` table. The view
reports webhook and `progress` rows as `running` unconditionally, and
`created` for a source with no status recorded yet.

```sql
SELECT
    ss.name AS source_name,
    ss.type AS source_type,
    ss.status,
    ss.error,
    sc.name AS schema_name,
    f.write_frontier::text AS write_frontier,
    f.write_frontier::timestamptz::text AS frontier_time
FROM mz_internal.mz_source_statuses ss
LEFT JOIN mz_internal.mz_frontiers f ON ss.id = f.object_id
LEFT JOIN mz_catalog.mz_objects o ON ss.id = o.id
LEFT JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE sc.name IS NULL OR sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY f.write_frontier ASC NULLS FIRST
```

---

## Performance: Hydration

### Non-Hydrated Objects
Returns only objects that are NOT fully hydrated. The replica joins have to be
LEFT JOINs: `mz_hydration_statuses` records `replica_id IS NULL` when there is
no replica to hydrate on, so inner joins drop every object on a zero-replica
cluster. A NULL replica in the result means there is no replica to hydrate on;
confirm with the Clusters and Replicas query for that object's cluster.

```sql
SELECT
    o.name AS object_name,
    o.type AS object_type,
    sc.name AS schema_name,
    c.name AS cluster_name,
    r.name AS replica_name,
    h.hydrated
FROM mz_internal.mz_hydration_statuses h
JOIN mz_catalog.mz_objects o ON h.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
LEFT JOIN mz_catalog.mz_cluster_replicas r ON h.replica_id = r.id
LEFT JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
  AND h.hydrated = false
ORDER BY o.name
```

---

## Performance: Memory and Resource Usage

### Cluster Replica Utilization
One row per (replica, process); `process_id` tells them apart on multi-process
sizes (`mz_cluster_replica_sizes.processes` says how many a size has).
`mz_cluster_replica_metrics` is keyed the same way, so sum its `memory_bytes`
across processes for a replica total. `heap_percent` is RAM plus swap against
the limit, the reading the stale-MV runbook pairs with `memory_percent`.

```sql
SELECT
    c.name AS cluster_name,
    r.name AS replica_name,
    r.size,
    u.process_id,
    u.cpu_percent,
    u.memory_percent,
    u.heap_percent,
    u.disk_percent
FROM mz_internal.mz_cluster_replica_utilization u
JOIN mz_catalog.mz_cluster_replicas r ON u.replica_id = r.id
JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
ORDER BY u.memory_percent DESC NULLS LAST
```

### Replica Restarts (OOM loop)
The current status and a utilization sample often look healthy between two
kills; the status history is what shows a loop. Replicas that were dropped or
replaced since keep their history rows, hence the LEFT JOIN. The reason
`oom-killed` covers the cgroup OOM killer, the replica's own heap limiter and
a full lgalloc spill disk alike, so it says memory (or spill disk), not which
limit. The emulator's process
orchestrator records no reason at all, so there only `offline_events` counts.

```sql
SELECT
    c.name AS cluster_name,
    r.name AS replica_name,
    h.replica_id,
    h.process_id,
    count(*) FILTER (WHERE h.status = 'offline') AS offline_events,
    count(*) FILTER (WHERE h.reason = 'oom-killed') AS oom_kills,
    max(h.occurred_at) FILTER (WHERE h.reason = 'oom-killed')::text AS last_oom
FROM mz_internal.mz_cluster_replica_status_history h
LEFT JOIN mz_catalog.mz_cluster_replicas r ON h.replica_id = r.id
LEFT JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
WHERE h.occurred_at > now() - INTERVAL '24 hours'
GROUP BY 1, 2, 3, 4
HAVING count(*) FILTER (WHERE h.status = 'offline') > 0
ORDER BY oom_kills DESC, offline_events DESC
```

### Cluster Replica Statuses
Driven from `mz_clusters` so that a cluster with no replicas still shows up,
with a NULL replica name and status; otherwise one row per replica process.

```sql
SELECT
    c.name AS cluster_name,
    c.replication_factor,
    r.name AS replica_name,
    rs.process_id,
    rs.status,
    rs.reason,
    rs.updated_at::text
FROM mz_catalog.mz_clusters c
LEFT JOIN mz_catalog.mz_cluster_replicas r ON r.cluster_id = c.id
LEFT JOIN mz_internal.mz_cluster_replica_statuses rs ON r.id = rs.replica_id
ORDER BY c.name, r.name
```

### Arrangement Sizes (`query` tool)
`mz_introspection.mz_dataflow_arrangement_sizes` is cluster-scoped: run this
through `query` with the cluster to inspect, plus `cluster_replica` if it has
more than one replica. Its `id` is a dataflow id (`uint8`), never
`mz_objects.id` (`text`), so the catalog is reached through
`mz_compute_exports`. A NULL object is a dataflow that exports nothing in
`mz_objects`: an internal introspection subscribe
(`Dataflow: introspection-subscribe-...`), a user or Console `SUBSCRIBE`, a
running `SELECT` (`Dataflow: oneshot-select-...`), or the retired version of a
materialized view after `APPLY REPLACEMENT`, which keeps the view's old name
until it is dropped; those still count toward the cluster's memory. A
dataflow is named after the object as created, so a replaced view's live
dataflow carries the replacement's name. The query groups per dataflow
and lists what each one exports, so a dataflow with several exports appears
once and `exported_objects` 0 is a NULL-object dataflow. For one object's
per-operator memory, run `EXPLAIN ANALYZE MEMORY FOR MATERIALIZED VIEW
<schema>.<mv>` (or `FOR INDEX <name>`) on the same cluster.

```sql
SELECT
    s.name AS dataflow_name,
    s.records,
    s.size,
    count(o.id) AS exported_objects,
    string_agg(o.type || ' ' || o.name, ', ' ORDER BY o.name) AS objects
FROM mz_introspection.mz_dataflow_arrangement_sizes s
LEFT JOIN mz_introspection.mz_compute_exports e ON e.dataflow_id = s.id
LEFT JOIN mz_catalog.mz_objects o ON o.id = e.export_id
GROUP BY s.id, s.name, s.records, s.size
ORDER BY s.size DESC NULLS LAST
LIMIT 30
```

---

## Object Dependencies

### Dependency Graph
Objects also depend on the builtin types and functions their definitions
reference, one row each, so the parent side excludes types and functions; system relations a view reads (say
`mz_catalog.mz_tables`) stay, since that is a real dependency. Still
unbounded: add a `LIMIT`, or narrow to the objects under investigation, before
running it into the 1 MB response cap.

```sql
SELECT
    parent.name AS parent_name,
    parent.type AS parent_type,
    child.name AS child_name,
    child.type AS child_type
FROM mz_internal.mz_object_dependencies d
JOIN mz_catalog.mz_objects parent ON d.referenced_object_id = parent.id
JOIN mz_catalog.mz_objects child ON d.object_id = child.id
JOIN mz_catalog.mz_schemas sc ON child.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
  AND parent.type NOT IN ('type', 'function')
ORDER BY parent.name, child.name
```

---

## Health: Source and Sink Statuses

### Source Statuses
Driven from `mz_source_statuses` so that source-fed tables (`type = 'table'`)
are included; see Source Status and Freshness.

```sql
SELECT
    ss.name AS source_name,
    ss.type AS source_type,
    ss.status,
    ss.error,
    ss.last_status_change_at::text,
    sc.name AS schema_name
FROM mz_internal.mz_source_statuses ss
LEFT JOIN mz_catalog.mz_objects o ON ss.id = o.id
LEFT JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE sc.name IS NULL OR sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY ss.status DESC, ss.name
```

### Sink Statuses
```sql
SELECT
    sk.name AS sink_name,
    sk.type AS sink_type,
    ss.status,
    ss.error,
    ss.last_status_change_at::text,
    sc.name AS schema_name
FROM mz_catalog.mz_sinks sk
JOIN mz_internal.mz_sink_statuses ss ON sk.id = ss.id
JOIN mz_catalog.mz_schemas sc ON sk.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY ss.status DESC, sk.name
```

### Source Statistics
`mz_source_statistics` is keyed on (source, replica), which is not one row per
replica: Kafka and load-generator sources run on every replica and get one row
each with independent counters (never sum across rows), while PostgreSQL,
MySQL and SQL Server sources always run on one replica and have one row.
Rows outlive their replica: after a pause, resize or replica change the old
row stays for a day, stale, next to a fresh one for the new replica id whose
counters restart at zero, so judge by `replica_exists`, not by row count.
Webhook sources run on no replica and carry a NULL `replica_id` (even on a
cluster without replicas). An ingestion that never ran, because its cluster
has no replicas or no table is attached to it, has no row, so its
`snapshot_committed` reads as missing rather than `false`. Statistics are
written once a minute and the first row for a (source, replica) is all
zeros, so for about two minutes after a source or replica starts the counters
read 0 and `snapshot_committed` reads `false` whatever the truth. `progress`
collections have no row. Source-fed tables and subsources have their own rows
and the parent source's row is the SUM of them (`offset_known` the MAX,
`offset_committed` the MIN), so never add a source row to its tables' rows;
the query joins `mz_objects` because `id` may be a table.

```sql
SELECT
    o.name AS source_name,
    o.type AS object_type,
    st.replica_id,
    (r.id IS NOT NULL) AS replica_exists,
    st.snapshot_committed,
    st.messages_received,
    st.bytes_received,
    st.updates_staged,
    st.updates_committed
FROM mz_internal.mz_source_statistics st
LEFT JOIN mz_catalog.mz_objects o ON st.id = o.id
LEFT JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
LEFT JOIN mz_catalog.mz_cluster_replicas r ON r.id = st.replica_id
WHERE sc.name IS NULL OR sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY o.name, st.replica_id
```
