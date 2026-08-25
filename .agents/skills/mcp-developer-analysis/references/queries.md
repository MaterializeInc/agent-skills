# Diagnostic Queries Reference

All queries in this file target system catalog tables and run through the MCP
`query_system_catalog` tool. That tool takes no cluster argument: catalog reads
are auto-routed to the catalog server cluster (`mz_catalog_server`), while
anything the router cannot serve there — notably every `mz_introspection`
relation — runs on the environment's default cluster. For cluster-bound
operations — `EXPLAIN ANALYZE` on a materialized view or index, reading user
data — use the `query` tool instead (added in Materialize v26.30; takes a
required `cluster` argument).

**Shared constraints (both tools):**
- One statement per call; write it without a trailing semicolon (one is
  tolerated today, two statements are rejected)
- SELECT, SHOW, or EXPLAIN only
- Rows come back with no column names — every `AS` alias below is discarded, so
  map columns positionally, in the order the `SELECT` list gives them
- A response is capped at 1 MB and a request at 60 seconds; narrow or `LIMIT`
  anything that could enumerate a whole large catalog

**`query_system_catalog` only:**
- System catalog tables only (`mz_*`, `pg_catalog`, `information_schema`)
- No cluster argument; passing one is silently ignored, not rejected, so a
  cluster-scoped query answers about the wrong cluster instead of failing

**`query` only:**
- `cluster` argument required
- `cluster_replica` required as well for any `mz_introspection` read on a
  cluster with more than one replica
- Can also reach user objects

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
LEFT JOIN, not JOIN: a cluster at replication factor 0 has no replica rows, and
an inner join makes it invisible.

```sql
SELECT
    c.name AS cluster_name,
    c.size,
    c.replication_factor,
    c.managed,
    r.name AS replica_name
FROM mz_catalog.mz_clusters c
LEFT JOIN mz_catalog.mz_cluster_replicas r ON c.id = r.cluster_id
ORDER BY c.name, r.name
```

### Cluster Topology
One row per cluster, with the replica count and peak utilization the report
template's Cluster Topology table asks for.

```sql
SELECT
    c.name AS cluster_name,
    c.size,
    c.replication_factor,
    count(r.id) AS replicas,
    max(u.memory_percent) AS peak_memory_percent
FROM mz_catalog.mz_clusters c
LEFT JOIN mz_catalog.mz_cluster_replicas r ON r.cluster_id = c.id
LEFT JOIN mz_internal.mz_cluster_replica_utilization u ON u.replica_id = r.id
GROUP BY c.name, c.size, c.replication_factor
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
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema')
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
- `convert to a view` — MV can be dematerialized entirely
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
Monthly credit consumption per cluster (assuming 730 hours/month).

Size the cluster from `mz_clusters`, not from a join to `mz_cluster_replicas`.
Joining the replicas *and* multiplying by `replication_factor` counts an
N-replica cluster N² times, and hides the zero-replica clusters, which cost
nothing but also run nothing.

```sql
SELECT
    c.name AS cluster_name,
    c.size,
    c.replication_factor,
    s.credits_per_hour,
    (s.credits_per_hour * c.replication_factor) AS cluster_credits_per_hour,
    (s.credits_per_hour * c.replication_factor * 730)::numeric(10,1) AS monthly_credits
FROM mz_catalog.mz_clusters c
JOIN mz_catalog.mz_cluster_replica_sizes s ON c.size = s.size
ORDER BY cluster_credits_per_hour DESC
```

### Total Monthly Compute Cost
```sql
SELECT
    SUM(s.credits_per_hour * c.replication_factor)::numeric(10,2) AS total_credits_per_hour,
    (SUM(s.credits_per_hour * c.replication_factor) * 730)::numeric(10,1) AS total_monthly_credits
FROM mz_catalog.mz_clusters c
JOIN mz_catalog.mz_cluster_replica_sizes s ON c.size = s.size
```

Both cover the system clusters as well. Only `mz_catalog_server` adds anything;
the others sit at replication factor 0 and contribute zero. Subtract it if the
report is about user-owned spend.

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
`mz_timestamp` (milliseconds since epoch). You **cannot** subtract it from
`now()`, and it casts to `text` and to nothing else: `::bigint` fails with
`CAST does not support casting from mz_timestamp to bigint`, so go through
`::text::bigint`. Sort ascending to find the most-lagging objects, and use
`to_timestamp()` for human-readable time. A frontier of `0` means the object
has never been written, not that it was written in 1970.

```sql
SELECT
    o.name AS object_name,
    o.type AS object_type,
    sc.name AS schema_name,
    f.write_frontier::text AS write_frontier,
    to_timestamp(f.write_frontier::text::bigint / 1000) AS frontier_time
FROM mz_internal.mz_frontiers f
JOIN mz_catalog.mz_objects o ON f.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
  AND f.write_frontier IS NOT NULL
ORDER BY f.write_frontier ASC
LIMIT 30
```

### Source Status and Freshness
```sql
SELECT
    s.name AS source_name,
    ss.status,
    ss.error,
    sc.name AS schema_name,
    f.write_frontier::text AS write_frontier,
    to_timestamp(f.write_frontier::text::bigint / 1000) AS frontier_time
FROM mz_catalog.mz_sources s
JOIN mz_internal.mz_source_statuses ss ON s.id = ss.id
LEFT JOIN mz_internal.mz_frontiers f ON s.id = f.object_id
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY f.write_frontier ASC NULLS FIRST
```

---

## Performance: Hydration

### Non-Hydrated Objects
Returns only objects that are NOT fully hydrated. The replica joins have to be
LEFT JOINs: `mz_hydration_statuses` records `replica_id IS NULL` when there is
no replica to hydrate on, so inner joins drop every object on a zero-replica
cluster — exactly the objects this query exists to find. A NULL replica in the
result means there is no replica to hydrate on; check
`mz_clusters.replication_factor` for that object's cluster.

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
```sql
SELECT
    c.name AS cluster_name,
    r.name AS replica_name,
    r.size,
    u.cpu_percent,
    u.memory_percent,
    u.disk_percent
FROM mz_internal.mz_cluster_replica_utilization u
JOIN mz_catalog.mz_cluster_replicas r ON u.replica_id = r.id
JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
ORDER BY u.memory_percent DESC NULLS LAST
```

### Cluster Replica Statuses
Driven from `mz_clusters` so that a cluster with no replicas still shows up,
with a NULL replica name and status.

```sql
SELECT
    c.name AS cluster_name,
    c.replication_factor,
    r.name AS replica_name,
    rs.status,
    rs.reason,
    rs.updated_at
FROM mz_catalog.mz_clusters c
LEFT JOIN mz_catalog.mz_cluster_replicas r ON r.cluster_id = c.id
LEFT JOIN mz_internal.mz_cluster_replica_statuses rs ON r.id = rs.replica_id
ORDER BY c.name, r.name
```

> **Note**: `mz_introspection.mz_dataflow_arrangement_sizes` is cluster-scoped
> and `query_system_catalog` does not accept a cluster argument, so it can't
> reach it. For per-cluster memory visibility, prefer
> `mz_internal.mz_cluster_replica_utilization`. When the `query` tool is
> available, `EXPLAIN ANALYZE MEMORY FOR MATERIALIZED VIEW <schema>.<mv>` (or
> `FOR INDEX <name>`) on the relevant cluster gives per-operator memory
> attributed to a specific object.

---

## Object Dependencies

### Dependency Graph
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
ORDER BY parent.name, child.name
```

---

## Health: Source and Sink Statuses

### Source Statuses
```sql
SELECT
    s.name AS source_name,
    s.type AS source_type,
    ss.status,
    ss.error,
    ss.last_status_change_at,
    sc.name AS schema_name
FROM mz_catalog.mz_sources s
JOIN mz_internal.mz_source_statuses ss ON s.id = ss.id
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY ss.status DESC, s.name
```

### Sink Statuses
```sql
SELECT
    sk.name AS sink_name,
    sk.type AS sink_type,
    ss.status,
    ss.error,
    ss.last_status_change_at,
    sc.name AS schema_name
FROM mz_catalog.mz_sinks sk
JOIN mz_internal.mz_sink_statuses ss ON sk.id = ss.id
JOIN mz_catalog.mz_schemas sc ON sk.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema')
ORDER BY ss.status DESC, sk.name
```

### Source Statistics
`mz_source_statistics` holds one row per (source, replica), so a source on a
multi-replica cluster appears once per replica — select `replica_id` and do not
sum the counters across rows. A source that is not ingesting at all has **no**
row here, so its `snapshot_committed` reads as missing rather than `false`;
check `mz_source_statuses` and the cluster's `replication_factor` for those.

```sql
SELECT
    s.name AS source_name,
    st.replica_id,
    st.snapshot_committed,
    st.messages_received,
    st.bytes_received,
    st.updates_staged,
    st.updates_committed
FROM mz_catalog.mz_sources s
JOIN mz_internal.mz_source_statistics st ON s.id = st.id
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY s.name, st.replica_id
```
