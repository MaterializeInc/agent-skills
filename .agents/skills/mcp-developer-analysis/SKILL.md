---
name: mcp-developer-analysis
description: 'Analyze a Materialize environment via the MCP Developer endpoint, and/or configure an MCP client (Claude Code, Cursor, VS Code, Zed, Continue, Windsurf, Claude Desktop) to connect to the materialize-developer server. For analysis: check environment health, investigate performance, troubleshoot stale materialized views, diagnose memory pressure, audit resource utilization, run EXPLAIN ANALYZE on user objects, get optimization recommendations. For client connection: configure/connect/set-up an MCP client to materialize-developer (Emulator, Cloud, or self-managed), control which user/role is used, switch between identities. Trigger even if user just says "check my environment", "why is my MV stale", "why is my cluster slow", "what can I optimize", "explain analyze my materialized view", "how do I connect Claude Code to materialize-developer", or "configure Cursor for the Materialize MCP".'
---

# Materialize Developer Analysis

Analyze a Materialize environment via the MCP Developer endpoint and produce a
structured report with health status, performance findings, and optimization
recommendations.

The developer endpoint exposes two read-only tools:

- **`query_system_catalog`** — `SELECT`/`SHOW`/`EXPLAIN` restricted to system
  catalog tables (`mz_*`, `pg_catalog`, `information_schema`). Takes no cluster
  argument, and one passed anyway is silently ignored rather than rejected.
  Catalog reads are auto-routed to the catalog server cluster
  (`mz_catalog_server`), but anything the router cannot serve there — notably
  every `mz_introspection` relation — runs on the environment's default
  cluster. Use for most catalog lookups.
- **`query`** (added in Materialize v26.30) — `SELECT`/`SHOW`/`EXPLAIN` against
  any object the role can access, including user objects on a named cluster.
  Required for `EXPLAIN ANALYZE` (it must run on the MV/index's cluster) and
  for reading user data directly. May be hidden when the operator has disabled
  `enable_mcp_developer_query_tool`.

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

**Do NOT guess column names.** Before writing queries, check whether the
ontology views are available (they live in `mz_internal` and are views, so
`SHOW TABLES` does not list them):

```sql
SHOW VIEWS FROM mz_internal LIKE 'mz_ontology%'
```

### If the ontology views are available

Use it to discover the correct tables, columns, join paths, and ID types:

| Table | What it tells you |
|-------|-------------------|
| `mz_internal.mz_ontology_entity_types` | What catalog entities exist and which `mz_*` table they map to. |
| `mz_internal.mz_ontology_link_types` | Relationships between entities (foreign keys, metrics, etc.). |
| `mz_internal.mz_ontology_properties` | Column names, types, and descriptions for each entity. |
| `mz_internal.mz_ontology_semantic_types` | Typed ID domains (CatalogItemId, ReplicaId, etc.). |

Example queries:
```sql
-- Find the right table for an entity
SELECT name, relation, description
FROM mz_internal.mz_ontology_entity_types
WHERE name LIKE '%source%'

-- Find join paths between entities
SELECT name, source_entity, target_entity, properties, description
FROM mz_internal.mz_ontology_link_types
WHERE source_entity = 'source' OR target_entity = 'source'

-- Find columns for a table
SELECT column_name, semantic_type, description
FROM mz_internal.mz_ontology_properties
WHERE entity_type = 'source_status'
```

### If the ontology views are NOT available

They exist from Materialize v26.24, so an older build is one reason the check
comes back empty. Use `SHOW COLUMNS FROM <schema>.<table>` to verify column
names before querying. Do NOT use `SHOW TABLES FROM mz_internal LIKE '...'` to
find relations: it lists tables only, and most system catalog objects are
views; use `SHOW VIEWS FROM mz_internal LIKE '...'` instead.

## Critical Rules

The server's own `initialize` instructions carry the catalog gotchas (the
column-name pitfalls such as `last_status_change_at`, the replica-to-cluster
JOIN for `mz_cluster_replica_utilization`, the ontology views, `SHOW COLUMNS`
to verify). Most clients forward them; if yours does not, `SHOW COLUMNS` is
the fallback. This section keeps only what those instructions do not say.

### mz_dataflow_arrangement_sizes needs the `query` tool

`mz_introspection.mz_dataflow_arrangement_sizes`, like every `mz_introspection`
relation, is cluster-scoped: it answers about the session's current cluster,
and `query_system_catalog` cannot target a cluster, so through that tool it
returns another cluster's numbers or an empty result, with no error. Read it
through the `query` tool with the `cluster` argument, plus `cluster_replica` on
a cluster with more than one replica — that one is not a refinement but a hard
requirement for *any* `mz_introspection` read there, and without it the read
fails with `log source reads must target a replica`. Its `id` column is a
dataflow id (`uint8`), not `mz_catalog.mz_objects.id` (`text`), so a JOIN on
ids fails with `operator does not exist: uint8 = text`. Reach the catalog
through `mz_introspection.mz_compute_exports` instead (`dataflow_id` matches
its `id`, `export_id` matches `mz_catalog.mz_objects.id`), or match `name`,
which reads `Dataflow: <database>.<schema>.<object>` for user objects — system
dataflows such as `Dataflow: introspection-subscribe-t65` do not follow that
shape, so neither path accounts for all the arrangement memory on the cluster.

On builds that predate materialize#38462, the server's own `initialize`
instructions still say never to query `mz_dataflow_arrangement_sizes`. That
rule was written for `query_system_catalog`, before the `query` tool existed;
with a `cluster` argument the relation is readable, and the guidance here
supersedes it.

Without the `query` tool, use:
- `mz_internal.mz_cluster_replica_utilization`: memory/CPU/disk percentage
- `mz_internal.mz_cluster_replica_metrics`: raw memory bytes
- `mz_internal.mz_index_advice`: find MVs/indexes that can be removed

## Workflow Overview

1. **Connect** — Verify the MCP Developer tools are available
2. **Discover** — Use the ontology + catalog queries to inventory all deployed objects
3. **Analyze** — Assess performance metrics: freshness, hydration, memory, utilization
4. **Report** — Produce a structured markdown report with findings and recommendations

## Step 1: Verify MCP Connection

Confirm you have access to the `query_system_catalog` tool. Run a quick test:

```
query_system_catalog: SELECT mz_version() FROM mz_catalog.mz_databases LIMIT 1
```

The `FROM` clause is not decoration: `query_system_catalog` rejects any
`SELECT` that references no system catalog table, so a bare
`SELECT mz_version()` fails with `Query must reference at least one system
catalog table` and looks like a broken connection.

Check whether a `query` tool is among the tools your client exposes to you
(a shell-capable agent can also ask the endpoint directly with the
`tools/list` curl in `mcp-client-connect.md`). If it's there, you can also
run `EXPLAIN ANALYZE` and queries against user objects on a named cluster.
If it's not listed (operator has disabled it, or the environment is on a
pre-v26.30 build), fall back to `query_system_catalog` for everything that
fits.

If `query_system_catalog` fails, check:
- The MCP server is registered in your client's MCP configuration (the
  file and key differ per client, see `mcp-client-connect.md`)
- The `enable_mcp_developer` feature flag is enabled on the environment
- Your authentication credentials are valid

### Running Queries

Both tools accept a single read-only statement per call. Write it without a
trailing semicolon — one is tolerated today, but two statements are rejected
with `Only one query allowed at a time` — and no `SET`.

Results come back as a bare array of rows with no column names; every `AS`
alias is discarded and you map columns positionally, so keep the `SELECT` list
short and in the order you intend to read it. A response is capped at 1 MB and
a request at 60 seconds, both surfacing as errors, so put a `LIMIT` on anything
that could enumerate a whole large catalog.

**`query_system_catalog`** — preferred for catalog work:
- `SELECT`, `SHOW`, `EXPLAIN` only
- System tables only for `SELECT` and `EXPLAIN`: `mz_*`, `pg_catalog`,
  `information_schema` (no user tables). `SHOW` forms are not checked against
  that list, so `SHOW TABLES`, `SHOW COLUMNS` and `SHOW CREATE …` do reach user
  objects here. Treat that as a fallback for when `query` is missing, not as
  what this tool is for — use `query` for user objects.
- No cluster argument; catalog reads are auto-routed to `mz_catalog_server`,
  everything else runs on the environment's default cluster

**`query`** — required for cluster-bound operations:
- Same `SELECT`/`SHOW`/`EXPLAIN` allowlist
- Takes a required `cluster` argument
- Can reach user objects in addition to the system catalog
- Use for `EXPLAIN ANALYZE` (it runs on the specified cluster) and for reading
  user data while debugging

When filtering out system schemas, always exclude: `mz_catalog`, `mz_internal`,
`pg_catalog`, `information_schema`, and `mz_introspection`. Two more system
schemas exist, `mz_catalog_unstable` and `mz_unsafe`; they hold no user-visible
objects, but they do show up when you enumerate schemas.

## Step 2: Discover — Inventory the Environment

Run the discovery queries to understand what is deployed. See
`references/queries.md` for the full query set. The discovery phase covers:

### Environment Overview
- Materialize version
- Clusters and replicas — names, sizes, and replica counts. Start from
  `mz_clusters` and LEFT JOIN the replicas: a cluster at replication factor 0
  has no replica rows and drops out of any inner join, which is exactly the
  cluster a stale object tends to be sitting on.
- Schemas in use

### Deployed Objects Inventory
- **Sources**: type (Kafka, Postgres, MySQL, Webhook, etc.), cluster
  assignment, status. `mz_sources` also has a row for every subsource and
  `progress` collection, so filter `type NOT IN ('subsource', 'progress')`
  before reporting a source count.
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
Query `mz_internal.mz_materialization_lag` for per-object lag. Its `local_lag`
and `global_lag` columns are plain `interval`s, so they compare and sort
directly, and `slowest_global_input_id` names the input holding the object
back.

**Important**: the relation with a `write_frontier` column is
`mz_internal.mz_frontiers`, and its type is `mz_timestamp`, not a standard
timestamp. You cannot subtract it from `now()` directly, and it casts to `text`
and to nothing else, so the human-readable form is
`to_timestamp(write_frontier::text::bigint / 1000)` — a direct `::bigint` fails
with `CAST does not support casting from mz_timestamp to bigint`.

### Hydration Status
Query `mz_internal.mz_hydration_statuses` to check whether all dataflows are
hydrated. Non-hydrated objects after initial startup may indicate resource
pressure or configuration issues. Join the replica columns with a LEFT JOIN:
`replica_id` is NULL when there is no replica to hydrate on, and an inner join
hides precisely the objects worth finding.

### Memory and Resource Consumption
- `mz_internal.mz_cluster_replica_utilization` for memory/CPU percentage per replica
- `mz_internal.mz_cluster_replica_metrics` for raw memory metrics
- `mz_internal.mz_index_advice` to identify which MVs/indexes can be optimized

### Worker Skew (CPU imbalance across workers)

Use `WITH SKEW` to find operators where one worker does disproportionate
CPU/memory work.

**Run these through the `query` tool**, not `query_system_catalog`:
`EXPLAIN ANALYZE` executes on the cluster you pass as the `cluster` argument
— for the object-level commands, that must be the cluster the MV/index lives
on, otherwise the introspection sources are empty. Nothing errors when you get
this wrong: on another cluster, or through `query_system_catalog`, the
object-level commands return an EMPTY result, which reads like "no skew". If
`query` is not available, this section is not actionable on the current
environment.

**Cluster-level (run on the cluster you want to inspect):**

```sql
EXPLAIN ANALYZE CLUSTER CPU WITH SKEW
```

**Object-level (run for both the MV and its indexes):**

```sql
EXPLAIN ANALYZE CPU WITH SKEW FOR MATERIALIZED VIEW <schema>.<mv_name>
```
```sql
EXPLAIN ANALYZE CPU WITH SKEW FOR INDEX <schema>.<index_name>
```

If skew is present: identify the skewed operator (often TopK/window/agg/join/distinct), then inspect definitions (`SHOW CREATE ...`) and recommend a concrete SQL change (remove/adjust hints, refactor keys/partitioning, or rewrite the MV).

### Index Advice
Query `mz_internal.mz_index_advice` — Materialize's built-in advisor. Hint types:
- **"keep"** — the MV/index is needed as-is
- **"drop unless queried directly"** — fewer than two downstream dependencies (or none at all, or an index on a source); only useful for direct SELECT queries
- **"convert to a view"** — MV can be dematerialized entirely, saving all arrangement memory
- **"convert to a view with an index"** — convert MV to a view but keep its indexes
- **"convert to materialized view"** — a view carrying indexes on more than one cluster should be an MV instead
- **"add index"** — object would benefit from an index

Those six are the whole set the advisor emits; anything filtering on a subset
of them silently drops real recommendations.

### Cost Analysis (optional)
Query `mz_catalog.mz_cluster_replica_sizes` to get credit rates per cluster
size, then calculate `credits_per_hour * replication_factor * 730 hours/month`
over **one row per cluster** from `mz_catalog.mz_clusters`. Joining
`mz_cluster_replicas` in as well multiplies an N-replica cluster by N a second
time, and drops zero-replica clusters from the picture entirely.

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
### Worker Skew
### Source and Sink Health

## Cost Analysis (if requested)

## Index Advice Summary

## SQL-Level Analysis
### Materialized View Definitions
### Index Analysis

## Optimization Recommendations
<numbered list with specific SQL for each>
```

The Cluster Topology row wants a replica count and a utilization figure per
cluster, which the per-replica queries do not give you. The `Cluster Topology`
query in `references/queries.md` produces both, and includes clusters with no
replicas.

### Writing Recommendations

**Always include specific SQL commands.** For example:

Good:
> **Recommendation:** Dematerialize `my_schema.unused_mv` to save memory.
> ```sql
> SHOW CREATE MATERIALIZED VIEW my_schema.unused_mv;
> DROP MATERIALIZED VIEW my_schema.unused_mv;
> CREATE VIEW my_schema.unused_mv AS <definition>
> ```

Bad:
> **Recommendation:** Consider dematerializing `my_schema.unused_mv`.

## Troubleshooting Runbooks

For focused troubleshooting, use these diagnostic paths.
**Always end with specific SQL commands to fix the issue.** Every fix below is
DDL, which both tools reject (`Only SELECT, SHOW, and EXPLAIN statements are
allowed`), so hand the commands to the user to run rather than trying to apply
them yourself.

### "Why is my materialized view stale?"

**Diagnostic steps:**
1. Check `mz_catalog.mz_clusters.replication_factor` for the MV's cluster
   first. A cluster with zero replicas runs nothing: its objects never hydrate,
   their frontiers never advance, and it appears in no replica-joined query, so
   the steps below all come back empty and read as health.
2. Check `mz_internal.mz_materialization_lag` for the MV's lag
3. Check `mz_internal.mz_hydration_statuses` — is it hydrated?
4. Check `mz_internal.mz_cluster_replica_statuses` — is the replica healthy?
5. Check `mz_internal.mz_cluster_replica_utilization` — memory pressure causing restarts?
6. Check `mz_internal.mz_source_statuses` — upstream source errors?
7. If the `query` tool is available, run
   `EXPLAIN ANALYZE MEMORY FOR MATERIALIZED VIEW <schema>.<mv>` on the MV's
   cluster to see per-operator memory and spot expensive shapes (large
   arrangements, joins without indexes, missing temporal filters).

**Common fixes:**

*If the MV's cluster has no replicas:*
```sql
ALTER CLUSTER <cluster_name> SET (REPLICATION FACTOR 1)
```

*If the cluster is overloaded (high memory/CPU):*
```sql
-- Option A: Scale up the cluster
ALTER CLUSTER <cluster_name> SET (SIZE = '<next_size_up>')
```
```sql
-- Option B: Move the MV to a different cluster
SHOW CREATE MATERIALIZED VIEW <schema>.<mv_name>;
DROP MATERIALIZED VIEW <schema>.<mv_name>;
CREATE MATERIALIZED VIEW <schema>.<mv_name> IN CLUSTER <new_cluster> AS <definition>
```

*If the MV is not hydrated and the cluster recently restarted:*
Hydration will complete on its own once the cluster stabilizes. If it persists,
the cluster likely needs more memory.

*If an upstream source is not running:*
```sql
SELECT name, status, error, last_status_change_at
FROM mz_internal.mz_source_statuses
WHERE status != 'running'
```
`status != 'running'` covers more than errors: `created` and `starting` are
transient, `paused` means the source's cluster has no replicas, and only
`stalled` and `failed` carry an `error`. Fix the upstream source issue first —
MV freshness depends on source health.

### "Why is my cluster running out of memory?"

**Diagnostic steps:**
1. Check `mz_internal.mz_cluster_replica_utilization` for memory percentage
2. Check `mz_internal.mz_index_advice` for MVs that can be dematerialized
3. Check MV definitions for missing temporal filters
4. Check for redundant indexes
5. If the `query` tool is available, run
   `EXPLAIN ANALYZE MEMORY FOR MATERIALIZED VIEW <schema>.<mv>` (or
   `FOR INDEX <name>`) on the suspect object's cluster to see which operators
   hold the most memory — the most direct way to confirm which arrangement is
   responsible.

**Common fixes:**

*Dematerialize MVs that don't need to be materialized:*
```sql
SELECT o.name, o.type, sc.name AS schema_name, ia.hint, ia.details
FROM mz_internal.mz_index_advice ia
JOIN mz_catalog.mz_objects o ON ia.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE ia.hint = 'convert to a view'
```

This filter sees one of the advisor's six hints. Read the whole advice set
first (the Index Advice query in `references/queries.md`): `convert to a view
with an index` and `convert to materialized view` are real memory
recommendations with different remediations, and a single-hint filter can come
back empty on an environment that has several.

```sql
-- For each candidate:
SHOW CREATE MATERIALIZED VIEW <schema>.<mv_name>;
DROP MATERIALIZED VIEW <schema>.<mv_name>;
CREATE VIEW <schema>.<mv_name> AS <definition>
```

*Drop unused indexes:*
```sql
SELECT o.name, o.type, sc.name AS schema_name, ia.hint, ia.details
FROM mz_internal.mz_index_advice ia
JOIN mz_catalog.mz_objects o ON ia.object_id = o.id
JOIN mz_catalog.mz_schemas sc ON o.schema_id = sc.id
WHERE ia.hint = 'drop unless queried directly'
```

```sql
-- Verify with the user before dropping
DROP INDEX <schema>.<index_name>
```

*Scale up the cluster:*
```sql
ALTER CLUSTER <cluster_name> SET (SIZE = '<next_size_up>')
```

### "Are my sources healthy? / Has my source finished snapshotting?"

**Diagnostic steps:**
1. Check `mz_internal.mz_source_statuses` for source errors
2. Check `mz_internal.mz_source_statistics` for ingestion progress
3. Check `mz_internal.mz_materialization_lag` for end-to-end lag

**Common fixes:**

*If a source is not running:*
```sql
SELECT name, status, error
FROM mz_internal.mz_source_statuses
WHERE status != 'running'
```

The status is one of `created`, `starting`, `running`, `paused`, `stalled`,
`failed`, `dropped`, and only `stalled` and `failed` carry an `error`.
`created` and `starting` are transient and normal; `paused` means the source's
cluster has no replicas, which no amount of waiting fixes:

```sql
-- paused: give the source's cluster a replica
ALTER CLUSTER <cluster_name> SET (REPLICATION FACTOR 1)
```
```sql
-- stalled/failed on bad credentials:
ALTER SECRET <secret_name> AS '<new_value>'
```

If `snapshot_committed` is `false`, the source is still loading its initial
snapshot. This is normal for large sources — wait for it to complete. A source
with no `mz_source_statistics` row at all is a different case: it is not
snapshotting, so check its status and its cluster's `replication_factor`
instead of waiting.

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
- `query_system_catalog` cannot `SELECT` user tables, though `SHOW` still
  reaches user-object metadata and DDL through it. The `query` tool reads user
  data directly, by design.
- Access is governed by RBAC, so you only see the *data* your credentials have
  access to. The catalog is not gated the same way: a role with no object
  grants still reads the full object inventory, every view and MV `definition`,
  and all of `mz_index_advice`. RBAC checks are off by default on the Emulator,
  where every principal sees everything.
- Freshness numbers are point-in-time snapshots. Re-run to check if lag is stable or growing.
