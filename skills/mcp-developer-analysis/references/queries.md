# Diagnostic Queries Reference

All queries in this file target system catalog tables and run through the MCP
`query_system_catalog` tool. The developer endpoint also exposes a `query`
tool (when `enable_mcp_developer_query_tool` is on) that takes a `cluster`
argument and can additionally reach user objects — use it for `EXPLAIN ANALYZE`
on a materialized view or index, and for inspecting user data while debugging.

**Shared constraints (both tools):**
- One statement per call (no semicolons, no multi-statement batches)
- SELECT, SHOW, or EXPLAIN only

**`query_system_catalog` only:**
- System catalog tables only (`mz_*`, `pg_catalog`, `information_schema`)
- No cluster argument; cluster-scoped queries are not supported

**`query` only:**
- `cluster` argument required
- May read user objects in addition to the system catalog

**Important column name notes:**
- `mz_source_statuses` and `mz_sink_statuses` use `last_status_change_at` (NOT `updated_at`)
- `mz_cluster_replica_statuses` uses `updated_at`
- `mz_cluster_replica_utilization` only has `replica_id` — must JOIN to get names
- When unsure, run `SHOW COLUMNS FROM <table>` first

---

## Environment Overview

### Version
```sql
SELECT mz_version()
```

### Clusters and Replicas
```sql
SELECT
    c.name AS cluster_name,
    r.name AS replica_name,
    r.size,
    c.managed,
    c.replication_factor
FROM mz_catalog.mz_clusters c
JOIN mz_catalog.mz_cluster_replicas r ON c.id = r.cluster_id
ORDER BY c.name, r.name
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
the full DDL.

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
    s.definition
FROM mz_catalog.mz_sources s
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
  AND s.definition IS NOT NULL
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

Hint types:
- `keep` — object is needed (feeds a sink or cross-cluster dependency)
- `drop unless queried directly` — no structural dependencies; only useful if
  SELECT queries hit it
- `convert to a view` — MV can be dematerialized entirely
- `convert to a view with an index` — MV can be a view, but keep its indexes
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

```sql
SELECT
    c.name AS cluster_name,
    r.name AS replica_name,
    r.size,
    s.credits_per_hour,
    c.replication_factor,
    s.credits_per_hour * c.replication_factor AS total_credits_per_hour,
    (s.credits_per_hour * c.replication_factor * 730)::numeric(10,1) AS monthly_credits
FROM mz_catalog.mz_clusters c
JOIN mz_catalog.mz_cluster_replicas r ON c.id = r.cluster_id
JOIN mz_catalog.mz_cluster_replica_sizes s ON r.size = s.size
ORDER BY monthly_credits DESC
```

### Total Monthly Compute Cost
```sql
SELECT
    SUM(s.credits_per_hour * c.replication_factor)::numeric(10,2) AS total_credits_per_hour,
    (SUM(s.credits_per_hour * c.replication_factor) * 730)::numeric(10,1) AS total_monthly_credits
FROM mz_catalog.mz_clusters c
JOIN mz_catalog.mz_cluster_replicas r ON c.id = r.cluster_id
JOIN mz_catalog.mz_cluster_replica_sizes s ON r.size = s.size
```

---

## Performance: Freshness / Lag

### Materialization Lag
```sql
SELECT
    o.name AS object_name,
    o.type AS object_type,
    sc.name AS schema_name,
    l.local_lag,
    l.global_lag
FROM mz_internal.mz_materialization_lag l
JOIN mz_catalog.mz_objects o ON l.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY l.global_lag DESC NULLS LAST
LIMIT 30
```

### Write Frontiers (sorted oldest first)

The `write_frontier` is of type `mz_timestamp` (uint8 milliseconds since epoch).
You **cannot** subtract it from `now()`. Sort ascending to find the most-lagging
objects, and use `to_timestamp()` for human-readable time.

```sql
SELECT
    o.name AS object_name,
    o.type AS object_type,
    sc.name AS schema_name,
    f.write_frontier::text AS write_frontier,
    to_timestamp(f.write_frontier::bigint / 1000) AS frontier_time
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
    to_timestamp(f.write_frontier::bigint / 1000) AS frontier_time
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
Returns only objects that are NOT fully hydrated. Empty result = everything is
healthy.

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
JOIN mz_catalog.mz_cluster_replicas r ON h.replica_id = r.id
JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
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
```sql
SELECT
    c.name AS cluster_name,
    r.name AS replica_name,
    rs.status,
    rs.reason,
    rs.updated_at
FROM mz_catalog.mz_cluster_replicas r
JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
LEFT JOIN mz_internal.mz_cluster_replica_statuses rs ON r.id = rs.replica_id
ORDER BY c.name, r.name
```

> **Note**: `mz_introspection.mz_dataflow_arrangement_sizes` is cluster-scoped
> and `query_system_catalog` does not accept a cluster argument, so it cannot
> reach it. For per-cluster memory visibility, prefer
> `mz_internal.mz_cluster_replica_utilization`, or — when the `query` tool is
> available — run `EXPLAIN ANALYZE MEMORY FOR MATERIALIZED VIEW <schema>.<mv>`
> (or `FOR INDEX <name>`) on the relevant cluster to get per-operator memory
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
```sql
SELECT
    s.name AS source_name,
    st.snapshot_committed,
    st.messages_received,
    st.bytes_received,
    st.updates_staged,
    st.updates_committed
FROM mz_catalog.mz_sources s
JOIN mz_internal.mz_source_statistics st ON s.id = st.id
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY s.name
```
