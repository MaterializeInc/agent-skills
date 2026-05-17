---
name: mcp-developer-analysis
description: 'Analyze a Materialize environment via the MCP Developer endpoint, and/or configure an MCP client (Claude Code, Cursor, VS Code, Zed, Continue, Windsurf, Claude Desktop) to connect to the materialize-developer server. For analysis: check environment health, investigate performance, troubleshoot stale materialized views, diagnose memory pressure, audit resource utilization, get optimization recommendations. For client connection: configure/connect/set-up an MCP client to materialize-developer (Emulator, Cloud, or self-managed), control which user/role is used, switch between identities. Trigger even if user just says "check my environment", "why is my MV stale", "why is my cluster slow", "what can I optimize", "how do I connect Claude Code to materialize-developer", or "configure Cursor for the Materialize MCP".'
---

# Materialize Developer Analysis

Analyze a Materialize environment by querying system catalog tables via the MCP
Developer endpoint (`query_system_catalog` tool), and produce a structured
report with health status, performance findings, and optimization recommendations.

## Connecting an MCP client to `materialize-developer`

If the user is asking how to **configure**, **connect**, or **set up** an MCP
client (Claude Code, Cursor, VS Code, Zed, Continue, Windsurf, Claude Desktop)
to talk to the `materialize-developer` server — including how to control which
user or role the connection uses, or how to switch between identities — see
[`mcp-client-connect.md`](mcp-client-connect.md). It covers the Emulator,
Materialize Cloud, and self-managed deployments, with per-client snippets,
authentication patterns, and verification recipes.

The rest of this `SKILL.md` covers what to do *once you are connected* and want
to analyze the environment.

## Discovering Tables and Columns

**Do NOT guess column names.** Before writing queries, check if the `mz_ontology`
schema is available by running:

```sql
SHOW TABLES FROM mz_ontology
```

### If mz_ontology is available

Use it to discover the correct tables, columns, join paths, and ID types:

| Table | What it tells you |
|-------|-------------------|
| `mz_ontology.mz_ontology_entity_types` | What catalog entities exist and which `mz_*` table they map to. |
| `mz_ontology.mz_ontology_link_types` | Relationships between entities (foreign keys, metrics, etc.). |
| `mz_ontology.mz_ontology_properties` | Column names, types, and descriptions for each entity. |
| `mz_ontology.mz_ontology_semantic_types` | Typed ID domains (CatalogItemId, ReplicaId, etc.). |

Example queries:
```sql
-- Find the right table for an entity
SELECT name, relation, description
FROM mz_ontology.mz_ontology_entity_types
WHERE name LIKE '%source%'

-- Find join paths between entities
SELECT name, source_entity, target_entity, properties, description
FROM mz_ontology.mz_ontology_link_types
WHERE source_entity = 'source' OR target_entity = 'source'

-- Find columns for a table
SELECT column_name, semantic_type, description
FROM mz_ontology.mz_ontology_properties
WHERE entity_type = 'source_status'
```

### If mz_ontology is NOT available

Use `SHOW COLUMNS FROM <schema>.<table>` to verify column names before querying.
Refer to the Critical Rules below for known pitfalls.

## Critical Rules

### Known column name pitfalls

Even with the ontology, be aware of these common mistakes:

| Wrong | Correct | Table |
|-------|---------|-------|
| `updated_at` | `last_status_change_at` | `mz_source_statuses`, `mz_sink_statuses` |
| `cluster_name` | Must JOIN through `replica_id` to `mz_cluster_replicas` then `mz_clusters` | `mz_cluster_replica_utilization` |

When unsure, run `SHOW COLUMNS FROM <schema>.<table>` to verify.

### Do NOT query mz_dataflow_arrangement_sizes

**NEVER query `mz_introspection.mz_dataflow_arrangement_sizes`** via MCP. It
fails for two reasons:

1. **Cluster-scoped**: Only returns data for the session's current cluster,
   and the MCP tool does not support `SET cluster = ...` to switch clusters.
2. **Type mismatch**: Its `id` column is `uint8`, not `text` like
   `mz_catalog.mz_objects.id`. JOINs fail with `operator does not exist: uint8 = text`.

Instead, use:
- `mz_internal.mz_cluster_replica_utilization` — memory/CPU/disk percentage
- `mz_internal.mz_cluster_replica_metrics` — raw memory bytes
- `mz_internal.mz_index_advice` — find MVs/indexes that can be removed

### Type casting notes

Some `mz_introspection` views use `uint8` for ID columns instead of `text`.
**Avoid JOINing `mz_introspection` views with `mz_catalog` views unless you
cast IDs explicitly.** The `mz_internal` views all use `text` IDs and are safe
to JOIN with `mz_catalog`.

### Discovering tables without the ontology

If `mz_ontology` is not available, use these fallbacks:
- `SHOW COLUMNS FROM <schema>.<table>` to check a table's columns
- **Do NOT use `SHOW TABLES FROM mz_internal LIKE '...'`** — this only shows
  tables, not views. Most system catalog objects are views.

## Workflow Overview

1. **Connect** — Verify the MCP Developer tools are available
2. **Discover** — Use the ontology + catalog queries to inventory all deployed objects
3. **Analyze** — Assess performance metrics: freshness, hydration, memory, utilization
4. **Report** — Produce a structured markdown report with findings and recommendations

## Step 1: Verify MCP Connection

Confirm you have access to the `query_system_catalog` tool. Run a quick test:

```
query_system_catalog: SELECT mz_version()
```

If this fails, check:
- The MCP server is configured in `.mcp.json`
- The `enable_mcp_developer` feature flag is enabled on the environment
- Your authentication credentials are valid

### Running Queries

All queries are run via the `query_system_catalog` MCP tool. Constraints:
- One statement per call (no semicolons)
- Read-only: SELECT, SHOW, EXPLAIN only
- System tables only: no access to user tables
- No `SET` statements

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

Retrieve SQL definitions for materialized views, views, indexes, and sources
using `references/queries.md`. This is critical for optimization analysis —
the SQL definitions tell you *how* things are computed:
- Join patterns and join order
- Filter predicates (or lack thereof — missing temporal filters are a common issue)
- Aggregation strategies
- Whether MVs duplicate logic that could be shared

## Step 3: Analyze — Performance and Resource Metrics

### Freshness (Lag Analysis)
Query `mz_internal.mz_materialization_lag` for per-object lag.

**Important**: The `write_frontier` column is of type `mz_timestamp` (a uint8),
not a standard timestamp. You cannot subtract it from `now()` directly. Cast to
get a human-readable time: `to_timestamp(write_frontier::bigint / 1000)`.

### Hydration Status
Query `mz_internal.mz_hydration_statuses` to check whether all dataflows are
hydrated. Non-hydrated objects after initial startup may indicate resource
pressure or configuration issues.

### Memory and Resource Consumption
- `mz_internal.mz_cluster_replica_utilization` for memory/CPU percentage per replica
- `mz_internal.mz_cluster_replica_metrics` for raw memory metrics
- `mz_internal.mz_index_advice` to identify which MVs/indexes can be optimized

### Index Advice
Query `mz_internal.mz_index_advice` — Materialize's built-in advisor. Hint types:
- **"keep"** — the MV/index is needed as-is
- **"drop unless queried directly"** — no structural dependencies; only useful for direct SELECT queries
- **"convert to a view"** — MV can be dematerialized entirely, saving all arrangement memory
- **"convert to a view with an index"** — convert MV to a view but keep its indexes
- **"add index"** — object would benefit from an index

### Cost Analysis (optional)
Query `mz_catalog.mz_cluster_replica_sizes` to get credit rates per cluster
size, then calculate: `credits_per_hour * replication_factor * 730 hours/month`.

When writing recommendations, **always quantify the credit impact**.

### Object Dependencies
Query `mz_internal.mz_object_dependencies` to understand the dependency graph.

## Step 4: Report — Generate the Analysis

Produce a structured markdown report:

```markdown
# Environment Analysis

**Date**: <date>
**Materialize Version**: <version>

## Executive Summary
<2-3 paragraph high-level assessment>

## Cluster Topology
| Cluster | Size | Replicas | Credits/Hr | Monthly Credits | Utilization |

## Deployed Objects
### Sources (<count>)
### Materialized Views (<count>)
### Sinks (<count>)
### Indexes (<count>)

## Performance Analysis
### Freshness
### Hydration
### Cluster Utilization

## Cost Analysis (if requested)

## Index Advice Summary

## SQL-Level Analysis
### Materialized View Definitions
### Index Analysis

## Optimization Recommendations
<numbered list with specific SQL for each>
```

### Writing Recommendations

**Always include specific SQL commands.** For example:

Good:
> **Recommendation:** Dematerialize `my_schema.unused_mv` to save memory.
> ```sql
> SHOW CREATE MATERIALIZED VIEW my_schema.unused_mv;
> DROP MATERIALIZED VIEW my_schema.unused_mv;
> CREATE VIEW my_schema.unused_mv AS <definition>;
> ```

Bad:
> **Recommendation:** Consider dematerializing `my_schema.unused_mv`.

## Troubleshooting Runbooks

For focused troubleshooting, use these diagnostic paths.
**Always end with specific SQL commands to fix the issue.**

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
SHOW CREATE MATERIALIZED VIEW <schema>.<mv_name>;
DROP MATERIALIZED VIEW <schema>.<mv_name>;
CREATE MATERIALIZED VIEW <schema>.<mv_name> IN CLUSTER <new_cluster> AS <definition>;
```

*If the MV is not hydrated and the cluster recently restarted:*
Hydration will complete on its own once the cluster stabilizes. If it persists,
the cluster likely needs more memory.

*If an upstream source has errors:*
```sql
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

**Common fixes:**

*If a source is stalled or erroring:*
```sql
SELECT name, status, error
FROM mz_internal.mz_source_statuses
WHERE status != 'running'

-- If the connection credentials are wrong:
ALTER SECRET <secret_name> AS '<new_value>';
```

If `snapshot_committed` is `false`, the source is still loading its initial
snapshot. This is normal for large sources — wait for it to complete.

### "What's the health of my environment?"

Run these checks in order:
1. `mz_internal.mz_cluster_replica_statuses` — all replicas ready?
2. `mz_internal.mz_source_statuses` — all sources running?
3. `mz_internal.mz_sink_statuses` — all sinks running?
4. `mz_internal.mz_cluster_replica_utilization` — resource pressure?

### "What can I optimize to save costs?"

1. Check `mz_internal.mz_index_advice` for optimization candidates
2. Check cluster utilization — are clusters over-provisioned?
3. Check credit rates from `mz_catalog.mz_cluster_replica_sizes`

## Notes

- All queries run through the MCP Developer endpoint are read-only.
- Query results are limited to system catalog tables — no access to user data.
- Access is governed by RBAC — you only see objects your credentials have access to.
- Freshness numbers are point-in-time snapshots. Re-run to check if lag is stable or growing.
