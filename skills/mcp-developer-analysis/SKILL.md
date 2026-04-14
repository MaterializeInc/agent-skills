---
name: mz-developer-analysis
description: Analyze a Materialize environment for health, performance, and optimization opportunities using the MCP Developer endpoint. Use this skill when someone wants to check environment health, investigate performance issues, troubleshoot stale materialized views, diagnose memory pressure, audit resource utilization, or get optimization recommendations. Trigger this even if the user just says "check my environment", "why is my MV stale", "why is my cluster slow", or "what can I optimize".
compatibility: []
---

# Materialize Developer Analysis

Analyze a Materialize environment by querying system catalog tables via the MCP
Developer endpoint (`query_system_catalog` tool), and produce a structured
report with health status, performance findings, and optimization recommendations.

> **How this differs from `mz-environment-analysis`**: That skill is for internal
> field engineers connecting via Teleport as `mz_support`. This skill is for
> anyone connected via MCP with their own Materialize credentials — customers,
> SEs, or internal users. No Teleport required.

## Critical Rules

### Never guess column names

**NEVER guess column names.** Use the exact columns listed in this skill.
Common mistakes that cause query failures:

| Wrong | Correct | Table |
|-------|---------|-------|
| `updated_at` | `last_status_change_at` | `mz_source_statuses`, `mz_sink_statuses` |
| `cluster_name` | Must JOIN through `replica_id` → `mz_cluster_replicas` → `mz_clusters` | `mz_cluster_replica_utilization` |
| `st.updated_at` | `ss.last_status_change_at` | `mz_source_statuses`, `mz_sink_statuses` |

**If you are unsure about a column name**, run `SHOW COLUMNS FROM <table>` first
to verify the schema before querying.

### Do NOT query mz_dataflow_arrangement_sizes

**NEVER query `mz_introspection.mz_dataflow_arrangement_sizes`** via MCP. It
will fail for two reasons:

1. **Cluster-scoped**: It only returns data for the session's current cluster,
   and the MCP tool does not support `SET cluster = ...` to switch clusters.
2. **Type mismatch**: Its `id` column is `uint8`, not `text` like
   `mz_catalog.mz_objects.id`. JOINs between them fail with
   `operator does not exist: uint8 = text`.

Instead, use these alternatives for memory visibility:
- `mz_internal.mz_cluster_replica_utilization` — memory/CPU/disk percentage
- `mz_internal.mz_cluster_replica_metrics` — raw memory bytes
- `mz_internal.mz_index_advice` — find MVs/indexes that can be removed

### Discovering tables

- Use `SHOW COLUMNS FROM <schema>.<table>` to check a table's columns.
- To list available tables: `SELECT name FROM mz_catalog.mz_objects WHERE schema_id = (SELECT id FROM mz_catalog.mz_schemas WHERE name = 'mz_internal') AND type IN ('table', 'view', 'materialized-view', 'source') ORDER BY name`
- **Do NOT use `SHOW TABLES FROM mz_internal LIKE '...'`** — this only shows
  tables, not views. Most system catalog objects are views and won't appear.

### Type casting notes

Some `mz_introspection` views use `uint8` for ID columns instead of `text`.
These cannot be directly compared to `text` IDs from `mz_catalog` views without
an explicit cast. **Avoid JOINing `mz_introspection` views with `mz_catalog`
views unless you cast IDs explicitly.** The `mz_internal` views listed in this
skill all use `text` IDs and are safe to JOIN with `mz_catalog`.

## System Catalog Schema Reference

These are the exact columns for the most commonly used tables. **Use these
column names exactly — do not guess or infer column names.**

### mz_internal.mz_source_statuses
| Column | Type | Notes |
|--------|------|-------|
| `id` | text | Source ID |
| `name` | text | Source name |
| `type` | text | Source type (kafka, postgres, etc.) |
| `last_status_change_at` | timestamptz | **NOT `updated_at`** |
| `status` | text | running, stalled, starting, etc. |
| `error` | text | Error message if any |
| `details` | jsonb | Additional status details |

### mz_internal.mz_sink_statuses
| Column | Type | Notes |
|--------|------|-------|
| `id` | text | Sink ID |
| `name` | text | Sink name |
| `type` | text | Sink type |
| `last_status_change_at` | timestamptz | **NOT `updated_at`** |
| `status` | text | running, stalled, starting, etc. |
| `error` | text | Error message if any |
| `details` | jsonb | Additional status details |

### mz_internal.mz_cluster_replica_statuses
| Column | Type | Notes |
|--------|------|-------|
| `replica_id` | text | Replica ID |
| `process_id` | uint8 | Process ID |
| `status` | text | ready, not-ready |
| `reason` | text | Reason if not ready |
| `updated_at` | timestamptz | This one DOES have `updated_at` |

### mz_internal.mz_cluster_replica_utilization
| Column | Type | Notes |
|--------|------|-------|
| `replica_id` | text | **Must JOIN to get cluster/replica name** |
| `process_id` | uint8 | Process ID |
| `cpu_percent` | double | CPU utilization percentage |
| `memory_percent` | double | Memory utilization percentage |
| `disk_percent` | double | Disk utilization percentage |

**To get cluster and replica names**, always JOIN:
```sql
SELECT c.name AS cluster_name, r.name AS replica_name, r.size,
       u.cpu_percent, u.memory_percent, u.disk_percent
FROM mz_internal.mz_cluster_replica_utilization u
JOIN mz_catalog.mz_cluster_replicas r ON u.replica_id = r.id
JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
ORDER BY u.memory_percent DESC NULLS LAST
```

### mz_internal.mz_materialization_lag
| Column | Type | Notes |
|--------|------|-------|
| `object_id` | text | Object ID — JOIN with `mz_objects` for name |
| `local_lag` | interval | Lag within the cluster |
| `global_lag` | interval | End-to-end lag |

### mz_internal.mz_hydration_statuses
| Column | Type | Notes |
|--------|------|-------|
| `object_id` | text | Object ID |
| `replica_id` | text | Replica ID |
| `hydrated` | bool | true = hydrated |

### mz_internal.mz_source_statistics
| Column | Type | Notes |
|--------|------|-------|
| `id` | text | Source ID |
| `snapshot_committed` | bool | Whether initial snapshot completed |
| `messages_received` | uint8 | Total messages received |
| `bytes_received` | uint8 | Total bytes received |
| `updates_staged` | uint8 | Updates staged |
| `updates_committed` | uint8 | Updates committed |

### mz_internal.mz_index_advice
| Column | Type | Notes |
|--------|------|-------|
| `object_id` | text | Object ID |
| `hint` | text | keep, drop unless queried directly, convert to a view, etc. |
| `details` | text | Explanation of the advice |

### mz_catalog.mz_materialized_views
| Column | Type | Notes |
|--------|------|-------|
| `id` | text | MV ID |
| `name` | text | MV name |
| `schema_id` | text | Schema ID — JOIN with `mz_schemas` for name |
| `cluster_id` | text | Cluster ID — JOIN with `mz_clusters` for name |
| `definition` | text | **The SQL body of the MV** (not the full CREATE statement) |

To get the full `CREATE MATERIALIZED VIEW` statement, use:
```sql
SHOW CREATE MATERIALIZED VIEW <schema>.<name>
```

### mz_catalog.mz_views
| Column | Type | Notes |
|--------|------|-------|
| `id` | text | View ID |
| `name` | text | View name |
| `schema_id` | text | Schema ID |
| `definition` | text | **The SQL body of the view** |

### mz_catalog.mz_indexes
| Column | Type | Notes |
|--------|------|-------|
| `id` | text | Index ID |
| `name` | text | Index name |
| `on_id` | text | ID of the object the index is on — JOIN with `mz_objects` |
| `cluster_id` | text | Cluster ID |
| `create_sql` | text | **Full CREATE INDEX statement. Note: NOT `definition`** |

### mz_catalog.mz_sources
| Column | Type | Notes |
|--------|------|-------|
| `id` | text | Source ID |
| `name` | text | Source name |
| `schema_id` | text | Schema ID |
| `type` | text | Source type (kafka, postgres, mysql, load-generator, etc.) |
| `cluster_id` | text | Cluster ID |
| `definition` | text | **The SQL body (nullable — subsources may not have one)** |

### Object definition queries

Use these queries to retrieve SQL definitions for optimization analysis:

```sql
-- Materialized view definitions
SELECT sc.name AS schema_name, mv.name AS mv_name, mv.definition
FROM mz_catalog.mz_materialized_views mv
JOIN mz_catalog.mz_schemas sc ON mv.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY sc.name, mv.name
```

```sql
-- Index definitions (uses create_sql, NOT definition)
SELECT sc.name AS schema_name, i.name AS index_name, o.name AS on_object, i.create_sql
FROM mz_catalog.mz_indexes i
JOIN mz_catalog.mz_objects o ON i.on_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY sc.name, i.name
```

```sql
-- Source definitions
SELECT sc.name AS schema_name, s.name AS source_name, s.type, s.definition
FROM mz_catalog.mz_sources s
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
  AND s.definition IS NOT NULL
ORDER BY sc.name, s.name
```

## Workflow Overview

1. **Connect** — Verify the MCP Developer tools are available
2. **Discover** — Run catalog queries to inventory all deployed objects
3. **Analyze** — Assess performance metrics: freshness, hydration, memory, utilization
4. **Report** — Produce a structured markdown report with findings and recommendations

## Step 1: Verify MCP Connection

Before starting, confirm you have access to the `query_system_catalog` tool from
the `materialize-developer` MCP server. Run a quick test:

```
query_system_catalog: SELECT mz_version()
```

If this fails, check:
- The MCP server is configured in `.mcp.json` (see the demo guide)
- The `enable_mcp_developer` feature flag is enabled on the environment
- Your authentication credentials are valid

### Running Queries

All queries in this skill are run via the `query_system_catalog` MCP tool. This
tool accepts a single read-only SQL statement (SELECT, SHOW, or EXPLAIN) and
only allows access to system catalog tables (`mz_*`, `pg_catalog`,
`information_schema`).

**Important constraints:**
- One statement per call (no semicolons to chain statements)
- Read-only: SELECT, SHOW, EXPLAIN only
- System tables only: no access to user tables
- The tool does NOT support `SET` statements — for cluster-scoped queries (like
  `mz_dataflow_arrangement_sizes`), see the workaround in Step 3

When filtering out system schemas, always exclude: `mz_catalog`, `mz_internal`,
`pg_catalog`, `information_schema`, and `mz_introspection`.

## Step 2: Discover — Inventory the Environment

Run the discovery queries to understand what is deployed. See
`references/queries.md` for the full query set. The discovery phase covers:

### Environment Overview
- Materialize version (`SELECT mz_version()`)
- Clusters and replicas — names, sizes, and replica counts
- Schemas in use

### Deployed Objects Inventory
- **Sources**: type (Kafka, Postgres, MySQL, Webhook, etc.), cluster assignment, status
- **Materialized Views**: cluster assignment, indexes, dependencies
- **Views**: (non-materialized) and their usage patterns
- **Sinks**: type, destination, cluster assignment
- **Indexes**: what they're on, cluster assignment
- **Connections**: external system connections configured

Build a mental model of the data pipeline: what data comes in (sources), how it's
transformed (views/MVs), and where it goes out (sinks).

### Object Definitions

After inventorying objects, retrieve the SQL definitions for materialized views,
views, indexes, and sources. Use the definitions queries from
`references/queries.md`.

This is critical for optimization analysis — metadata alone (names, sizes,
clusters) only tells you *what exists*. The SQL definitions tell you *how*
things are computed, which is where most optimization opportunities live:
- Join patterns and join order
- Filter predicates (or lack thereof — missing temporal filters are a common issue)
- Aggregation strategies
- Whether MVs duplicate logic that could be shared
- Index key column choices

For environments with many objects, focus on pulling definitions for:
1. The largest MVs by memory (identified in the arrangement size queries)
2. MVs with the most indexes (may indicate complex query patterns)
3. Any MVs that appear in deep dependency chains

## Step 3: Analyze — Performance and Resource Metrics

### Freshness (Lag Analysis)
Query `mz_internal.mz_materialization_lag` for per-object lag.

Also query `mz_internal.mz_frontiers` joined with catalog tables to understand
how far behind each object is from real-time.

**Important**: The `write_frontier` column is of type `mz_timestamp` (a uint8),
not a standard timestamp. You cannot subtract it from `now()` directly. Instead,
sort by `write_frontier ASC` to find the most-lagging objects (lowest frontiers =
furthest behind). To interpret the values, `mz_timestamp` represents milliseconds
since the Unix epoch. Cast to get a human-readable time:
`to_timestamp(write_frontier::bigint / 1000)`.

Use the freshness queries from `references/queries.md` to identify:
- Objects with the oldest (lowest) write frontiers
- Whether frontiers are consistent across objects (healthy) or divergent (indicates bottlenecks)

### Hydration Status
Query `mz_internal.mz_hydration_statuses` to check whether all dataflows are
hydrated. Non-hydrated objects after initial startup may indicate resource
pressure or configuration issues.

### Memory and Resource Consumption
Use the memory queries from `references/queries.md` to identify:
- Cluster replica utilization via `mz_internal.mz_cluster_replica_utilization`
- Whether replicas are right-sized for their workload

**DO NOT use `mz_dataflow_arrangement_sizes`** — see the Critical Rules section
above. It is cluster-scoped, requires `SET cluster`, and has `uint8` ID type
mismatches. It will fail via MCP.

**Use these instead:**
- `mz_internal.mz_cluster_replica_utilization` for memory/CPU percentage per replica
- `mz_internal.mz_cluster_replica_metrics` for raw memory metrics
- `mz_internal.mz_index_advice` to identify which MVs/indexes can be optimized

These views work correctly via MCP and give sufficient memory visibility.

### Index Advice
Query `mz_internal.mz_index_advice` — Materialize's built-in advisor that
analyzes object dependencies to recommend index and MV changes. This is one of
the most valuable queries in the analysis. Hint types:
- **"keep"** — the MV/index is needed as-is (e.g., feeds a sink or cross-cluster dependency)
- **"drop unless queried directly"** — no structural dependencies; only useful for direct SELECT queries
- **"convert to a view"** — MV can be dematerialized entirely, saving all arrangement memory
- **"convert to a view with an index"** — convert MV to a view but keep its indexes
- **"add index"** — object would benefit from an index

Pay special attention to large MVs with "convert to a view" advice — these
represent the biggest memory savings opportunities.

### Cost Analysis (optional — include if requested)
Query `mz_catalog.mz_cluster_replica_sizes` to get credit rates per cluster
size, then calculate:
- **Current compute cost**: `credits_per_hour * replication_factor * 730 hours/month`
- **Potential savings from right-sizing**: credit difference of downsizing
- **Potential savings from dropping indexes/MVs**: credit savings from smaller size

Reference credit rates:

| Size | Credits/Hour | Monthly Credits (730h) |
|------|-------------|----------------------|
| 25cc | 0.25 | 182.5 |
| 50cc | 0.5 | 365 |
| 100cc | 1 | 730 |
| 200cc | 2 | 1,460 |
| 300cc | 3 | 2,190 |
| 400cc | 4 | 2,920 |
| 600cc | 6 | 4,380 |
| 800cc | 8 | 5,840 |
| 1200cc | 12 | 8,760 |
| 1600cc | 16 | 11,680 |

Full rates are available from `mz_catalog.mz_cluster_replica_sizes`.

When writing optimization recommendations, **always quantify the credit impact**.
For example: "Converting this MV to a view would free enough memory to downsize
from 600cc (6 credits/hr) to 100cc (1 credit/hr), saving 5 credits/hr
(3,650 credits/month)."

### Object Dependencies
Query `mz_internal.mz_object_dependencies` to understand the dependency graph.
Look for:
- Deep dependency chains that amplify recomputation
- Materialized views that could be consolidated
- Indexes that may be redundant or missing

## Step 4: Report — Generate the Analysis

Produce a structured markdown report with the following sections:

```markdown
# Environment Analysis

**Date**: <date>
**Materialize Version**: <version>

## Executive Summary

<2-3 paragraph high-level assessment: what the environment is doing, overall
health, top concerns, and most impactful recommendations>

## Cluster Topology

| Cluster | Size | Replicas | Credits/Hr | Monthly Credits | Utilization |
|---------|------|----------|-----------|----------------|-------------|
<one row per cluster>

## Deployed Objects

### Sources (<count>)
<table of sources with type, cluster, status, freshness>

### Materialized Views (<count>)
<table of MVs with cluster, freshness, hydration status>

### Sinks (<count>)
<table of sinks with type, cluster, status>

### Indexes (<count>)
<table of indexes with target object, cluster>

## Performance Analysis

### Freshness
<analysis of lag across objects, highlight any with concerning lag>

### Hydration
<hydration status summary, flag anything not fully hydrated>

### Cluster Utilization
<per-cluster resource utilization assessment>

## Cost Analysis (if requested)

### Current Monthly Compute Cost
<table with cluster sizes, credit rates, monthly cost, total>

### Projected Savings from Recommendations
<for each optimization, calculate credit savings>

## Index Advice Summary

<Summary table of all advice grouped by hint type:
- Objects recommended to "convert to a view" — biggest easy wins
- Indexes flagged as "drop unless queried directly"
- Objects recommended to "add index"
- Objects marked "keep" — correctly configured>

## SQL-Level Analysis

### Materialized View Definitions
<for significant MVs, include the definition and analysis. Flag:
- Missing temporal filters
- Inefficient join patterns
- Redundant computation across MVs
- Opportunities to restructure for lower memory>

### Index Analysis
<assess whether index key columns align with likely query patterns.
Flag redundant indexes and suggest consolidation.>

## Optimization Recommendations

<numbered list of specific, actionable recommendations, ordered by impact.
For each:
- What to change
- Why it matters (quantify impact)
- How to implement it (specific SQL)>
```

### Writing Recommendations

**Always include specific SQL commands** to implement each recommendation. Do not
just describe what to do — give the user copy-pasteable SQL. For example:

Good:
> **Recommendation:** Dematerialize `my_schema.unused_mv` to save memory.
> ```sql
> -- Step 1: Save the definition
> SHOW CREATE MATERIALIZED VIEW my_schema.unused_mv;
> -- Step 2: Drop the materialized view
> DROP MATERIALIZED VIEW my_schema.unused_mv;
> -- Step 3: Recreate as a regular view
> CREATE VIEW my_schema.unused_mv AS <definition from step 1>;
> ```

Bad:
> **Recommendation:** Consider dematerializing `my_schema.unused_mv`.

Common optimization areas to evaluate:
- **Cluster right-sizing**: Over- or under-provisioned?
- **Index strategy**: Missing indexes on frequently-queried MVs, or redundant indexes wasting memory
- **View consolidation**: Multiple MVs that could be combined
- **Temporal filters**: Sources or MVs retaining more history than needed
- **Source configuration**: Envelope settings, snapshot strategies
- **Dematerialization**: MVs that mz_index_advice flags as "convert to a view"

## Troubleshooting Runbooks

For focused troubleshooting (instead of a full analysis), use these diagnostic
paths. **Always end with specific SQL commands to fix the issue.**

### "Why is my materialized view stale?"

**Diagnostic steps:**
1. Check `mz_internal.mz_materialization_lag` for the MV's lag
2. Check `mz_internal.mz_hydration_statuses` — is it hydrated?
3. Check `mz_internal.mz_cluster_replica_statuses` — is the replica healthy?
4. Check `mz_internal.mz_cluster_replica_utilization` — memory pressure causing restarts?
5. Check `mz_internal.mz_source_statuses` — upstream source errors?

**Common fixes:**

*If the cluster is overloaded (high memory/CPU):*
```sql
-- Option A: Scale up the cluster
ALTER CLUSTER <cluster_name> SET (SIZE = '<next_size_up>');

-- Option B: Move the MV to a different cluster
-- Step 1: Get the MV definition
SHOW CREATE MATERIALIZED VIEW <schema>.<mv_name>;
-- Step 2: Drop and recreate on a different cluster
DROP MATERIALIZED VIEW <schema>.<mv_name>;
CREATE MATERIALIZED VIEW <schema>.<mv_name> IN CLUSTER <new_cluster> AS <definition>;
```

*If the MV is not hydrated and the cluster recently restarted:*
```sql
-- Check cluster replica status for recent restarts
SELECT rs.status, rs.reason, rs.updated_at
FROM mz_internal.mz_cluster_replica_statuses rs
JOIN mz_catalog.mz_cluster_replicas r ON rs.replica_id = r.id
JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
WHERE c.name = '<cluster_name>'
```
Hydration will complete on its own once the cluster stabilizes. If it persists,
the cluster likely needs more memory.

*If an upstream source has errors:*
```sql
-- Check source status
SELECT name, status, error, last_status_change_at
FROM mz_internal.mz_source_statuses
WHERE status != 'running'
```
Fix the upstream source issue first — MV freshness depends on source health.

### "Why is my cluster running out of memory?"

**Diagnostic steps:**
1. Check `mz_internal.mz_cluster_replica_utilization` for memory percentage
2. Check `mz_internal.mz_index_advice` for MVs that can be dematerialized
3. Check MV definitions for missing temporal filters
4. Check for redundant indexes

**Common fixes:**

*Dematerialize MVs that don't need to be materialized:*
```sql
-- Find candidates
SELECT o.name, o.type, sc.name AS schema_name, ia.hint, ia.details
FROM mz_internal.mz_index_advice ia
JOIN mz_catalog.mz_objects o ON ia.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE ia.hint = 'convert to a view'

-- For each candidate:
SHOW CREATE MATERIALIZED VIEW <schema>.<mv_name>;
DROP MATERIALIZED VIEW <schema>.<mv_name>;
CREATE VIEW <schema>.<mv_name> AS <definition>;
```

*Drop unused indexes:*
```sql
-- Find candidates
SELECT o.name, o.type, sc.name AS schema_name, ia.hint, ia.details
FROM mz_internal.mz_index_advice ia
JOIN mz_catalog.mz_objects o ON ia.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE ia.hint = 'drop unless queried directly'

-- Verify with the user before dropping
DROP INDEX <schema>.<index_name>;
```

*Scale up the cluster:*
```sql
ALTER CLUSTER <cluster_name> SET (SIZE = '<next_size_up>');
```

### "Are my sources healthy? / Has my source finished snapshotting?"

**Diagnostic steps:**
1. Check `mz_internal.mz_source_statuses` for source errors
2. Check `mz_internal.mz_source_statistics` for ingestion progress
3. Check `mz_internal.mz_materialization_lag` for end-to-end lag
4. Check cluster utilization for resource pressure

**Key queries:**
```sql
-- Source health with last status change
SELECT s.name, s.type, ss.status, ss.error, ss.last_status_change_at
FROM mz_catalog.mz_sources s
JOIN mz_internal.mz_source_statuses ss ON s.id = ss.id
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY ss.status DESC, s.name

-- Snapshot progress
SELECT s.name, st.snapshot_committed, st.messages_received, st.bytes_received
FROM mz_catalog.mz_sources s
JOIN mz_internal.mz_source_statistics st ON s.id = st.id
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
```

If `snapshot_committed` is `false`, the source is still loading its initial
snapshot. This is normal for large sources — wait for it to complete.

**Common fixes:**

*If a source is stalled or erroring:*
```sql
-- Check the error message
SELECT name, status, error
FROM mz_internal.mz_source_statuses
WHERE status != 'running'

-- If the connection credentials are wrong, update them:
ALTER SECRET <secret_name> AS '<new_value>';

-- If the source needs to be restarted:
ALTER SOURCE <schema>.<source_name> DROP SUBSOURCE <subsource_name>;
ALTER SOURCE <schema>.<source_name> ADD SUBSOURCE <subsource_name>;
```

### "What's the health of my environment?"

**Diagnostic steps:**
1. Check `mz_internal.mz_cluster_replica_statuses` — all replicas ready?
2. Check `mz_internal.mz_source_statuses` — all sources running?
3. Check `mz_internal.mz_sink_statuses` — all sinks running?
4. Check `mz_internal.mz_cluster_replica_utilization` — resource pressure?

**Key queries:**
```sql
-- Cluster replica health
SELECT c.name AS cluster_name, r.name AS replica_name,
       rs.status, rs.reason, rs.updated_at
FROM mz_internal.mz_cluster_replica_statuses rs
JOIN mz_catalog.mz_cluster_replicas r ON rs.replica_id = r.id
JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
ORDER BY c.name, r.name

-- Source health
SELECT s.name, ss.status, ss.error, ss.last_status_change_at
FROM mz_catalog.mz_sources s
JOIN mz_internal.mz_source_statuses ss ON s.id = ss.id
JOIN mz_catalog.mz_schemas sc ON s.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
ORDER BY ss.status DESC, s.name

-- Sink health
SELECT sk.name, ss.status, ss.error, ss.last_status_change_at
FROM mz_catalog.mz_sinks sk
JOIN mz_internal.mz_sink_statuses ss ON sk.id = ss.id
JOIN mz_catalog.mz_schemas sc ON sk.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema')
ORDER BY ss.status DESC, sk.name

-- Resource utilization
SELECT c.name AS cluster_name, r.name AS replica_name, r.size,
       u.cpu_percent, u.memory_percent, u.disk_percent
FROM mz_internal.mz_cluster_replica_utilization u
JOIN mz_catalog.mz_cluster_replicas r ON u.replica_id = r.id
JOIN mz_catalog.mz_clusters c ON r.cluster_id = c.id
ORDER BY u.memory_percent DESC NULLS LAST
```

### "What can I optimize to save costs?"

**Diagnostic steps:**
1. Check `mz_internal.mz_index_advice` for optimization candidates
2. Check cluster utilization — are clusters over-provisioned?
3. Check credit rates from `mz_catalog.mz_cluster_replica_sizes`

**Key queries:**
```sql
-- Optimization candidates
SELECT o.name, o.type, sc.name AS schema_name, ia.hint, ia.details
FROM mz_internal.mz_index_advice ia
JOIN mz_catalog.mz_objects o ON ia.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE sc.name NOT IN ('mz_catalog', 'mz_internal', 'pg_catalog', 'information_schema', 'mz_introspection')
  AND ia.hint IN ('convert to a view', 'drop unless queried directly')
ORDER BY ia.hint, o.name

-- Cost per cluster
SELECT c.name, r.size, s.credits_per_hour,
       (s.credits_per_hour * c.replication_factor * 730)::numeric(10,1) AS monthly_credits
FROM mz_catalog.mz_clusters c
JOIN mz_catalog.mz_cluster_replicas r ON c.id = r.cluster_id
JOIN mz_catalog.mz_cluster_replica_sizes s ON r.size = s.size
ORDER BY monthly_credits DESC
```

## Notes

- All queries run through the MCP Developer endpoint are read-only. You cannot
  modify any objects.
- Query results are limited to system catalog tables — you cannot access user
  data.
- Access is governed by RBAC — you only see objects your credentials have access to.
- Freshness numbers are point-in-time snapshots. If something looks concerning,
  re-run the query to see if lag is stable or growing.
