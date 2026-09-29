<!-- mz-docs page: releases -->

# Releases

Materialize release notes

> **Note:** Starting with the v26.1.0 release, Materialize releases on a weekly schedule for
> both Cloud and Self-Managed. See [Release schedule](/releases/schedule) for details.

## v26.43.0
*Released to Materialize Cloud: 2026-09-23* <br>
*Released to Materialize Self-Managed: 2026-09-24* <br>

### Iceberg support for Databricks on Azure {#v26.43-iceberg-support-for-databricks-on-azure}

> **Public Preview:** This feature is in public preview.

Iceberg sinks can now write to Apache Iceberg tables registered in [Databricks
Unity Catalog](/export-data/iceberg-databricks/) on Azure, where catalogs store
their data in Azure Data Lake Storage Gen2. Set `STORAGE PROVIDER = 'adls'` on
the Iceberg catalog connection alongside `ACCESS DELEGATION =
'vended-credentials'`, and Materialize writes to Azure Data Lake Storage with
temporary, table-scoped credentials that Unity Catalog vends. Materialize
refreshes both the OAuth2 token and the vended credentials while the sink runs,
so the sink needs no Azure credentials of its own.

```mzsql
CREATE SECRET databricks_oauth
  AS '<client_id>:<client_secret>';

CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 'rest',
    URL = 'https://adb-<workspace_id>.<region_id>.azuredatabricks.net/api/2.1/unity-catalog/iceberg-rest',
    WAREHOUSE = '<catalog_name>',
    CREDENTIAL = SECRET databricks_oauth,
    OAUTH2 SERVER URL = 'https://adb-<workspace_id>.<region_id>.azuredatabricks.net/oidc/v1/token',
    SCOPE = 'all-apis',
    ACCESS DELEGATION = 'vended-credentials',
    STORAGE PROVIDER = 'adls'
);

CREATE SINK <sink_name>
  IN CLUSTER <sink_cluster>
  FROM <my_materialize_object>
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = '<unity_catalog_schema>',
    TABLE = '<my_iceberg_table>'
  )
  MODE APPEND
  WITH (COMMIT INTERVAL = '<commit_interval>');
```

For more information, see:
- [Guide: Databricks Unity Catalog](/export-data/iceberg-databricks/)
- [`CREATE CONNECTION`: Iceberg catalog](/sql/create-connection/#iceberg-catalog), including [storage access delegation](/sql/create-connection/#iceberg-catalog-access-delegation)
- [`CREATE SINK`: Iceberg](/sql/create-sink/iceberg/), including [append mode](/sql/create-sink/iceberg/#append-mode)

### Claude Code and Codex plugins for Materialize {#v26.43-agent-skills-plugins}

The [Materialize agent skills](/developer-tools/mcp-server/coding-agent-skills/)
are now available as a plugin for Claude Code and Codex. The plugin installs all
the skills at once, and helps you keep them up to date automatically.

In Claude Code:

```
/plugin marketplace add MaterializeInc/agent-skills
/plugin install materialize@materialize
```

In Codex:

```bash
codex plugin marketplace add MaterializeInc/agent-skills
codex plugin add materialize@materialize
```

If you installed the skills with `npx skills`, remove them before you install
the plugin, so each skill appears only once. For more information, see [Agent
Skills](/developer-tools/mcp-server/coding-agent-skills/#install-as-a-plugin).

### Improvements {#v26.43-improvements}
- **Graceful cluster resizes wait for replacements to catch up**: A graceful resize now retires the outgoing replicas only once the new replicas have hydrated and caught up to the replicas they replace, so cut-overs no longer stall query progress. A resize that cannot catch up in time follows its `ON TIMEOUT` policy, which defaults to `ROLLBACK`.
- **Swap usage in replica metrics**: `mz_internal.mz_cluster_replica_metrics` and `mz_cluster_replica_metrics_history` now report `swap_bytes` for each replica process, and `mz_internal.mz_cluster_replica_utilization` and `mz_cluster_replica_utilization_history` expose `swap_percent` as a share of the replica's heap allocation, so you can see how much of a replica's memory has spilled to swap.
- **Per-process peaks in replica hydration history**: `mz_internal.mz_replica_hydration_history` now records one row per replica process, carrying that process's own memory and disk peaks, so resource skew across the processes of a multi-process replica is visible.

### Guides {#v26.43-guides}
- [Understand the lifecycle of a sink](/export-data/lifecycle-of-a-sink/)
- [PostgreSQL: Supported database operations](/ingest-data/postgres/#supported-database-operations)
- [SQL Server: Supported database operations](/ingest-data/sql-server/#supported-database-operations)

### Bug Fixes {#v26.43-bug-fixes}
- Fixed `DEALLOCATE`, `CLOSE`, `EXECUTE`, and `FETCH` failing with a "does not exist" error and aborting the surrounding transaction when the prepared statement or cursor name was given in double quotes; a name created over the extended wire protocol is stored exactly as it arrives, but these statements re-quoted it before looking it up, so drivers such as psqlODBC that prepare statements over the protocol and later deallocate them by quoted name could not release them.
- Fixed an abort that dropped every session in the environment when a cursor declared over a `CLOSE` statement naming that same cursor was fetched from.
- Fixed Iceberg sinks applying a commit's changes on top of newer table state when retrying, which could duplicate written data if an earlier attempt had in fact succeeded or another writer had taken over; the sink now inspects the catalog's table state before applying the commit.
- Fixed `object_count` in `mz_internal.mz_replica_hydration_history` counting a replica's built-in introspection dataflows, which made it disagree with the rows recorded in `mz_internal.mz_object_hydration_history` for the same episode; introspection-only episodes are still recorded, with `object_count = 0`.

## v26.42.0
*Released to Materialize Self-Managed: 2026-09-18* <br>

### Safely drop upstream constraints in your Postgres sources {#v26.42-constraint-exclusion-for-postgres-sources}
Materialize now allows you to `EXCLUDE CONSTRAINTS` when creating a table from a Postgres source. You can use this workflow to safely drop an upstream constraint, without causing your source to stall. Today, the Postgres source incorporates `PRIMARY KEY`, `UNIQUE` and `NOT NULL` constraints.

```mzsql
CREATE TABLE orders
  FROM SOURCE pg_source (REFERENCE public.orders)
  WITH (EXCLUDE CONSTRAINTS ('orders_customer_email_key'));
```

If you want to exclude all constraints, you can do that too:

```mzsql
CREATE TABLE orders
  FROM SOURCE pg_source (REFERENCE public.orders)
  WITH (EXCLUDE ALL CONSTRAINTS);
```

For more details, see [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/postgres/) for PostgreSQL and the guide on [handling upstream schema changes](/ingest-data/postgres/source-versioning/).

### Size clusters using hydration history {#v26.42-hydration-history}
You can now track how long a cluster took to hydrate, and what resources it needed. Every completed hydration is now recorded in two new introspection tables:
- [`mz_internal.mz_replica_hydration_history`](/sql/system-catalog/mz_internal/#mz_replica_hydration_history) to track hydration metrics per replica
- [`mz_internal.mz_object_hydration_history`](/sql/system-catalog/mz_internal/#mz_object_hydration_history) to track hydration metrics per object

Use these tables to determine your hydration requirements, and right-size your clusters accordingly.

```mzsql
SELECT
    rh.replica_name AS replica,
    rh.size,
    h.started_at,
    h.finished_at - h.started_at AS hydration_time,
    h.object_count,
    pg_size_pretty(h.peak_memory_bytes) AS peak_memory,
    pg_size_pretty(h.peak_disk_bytes) AS peak_disk
FROM mz_internal.mz_replica_hydration_history AS h
JOIN mz_internal.mz_cluster_replica_history AS rh ON rh.replica_id = h.replica_id
WHERE rh.cluster_name = 'analytics'
ORDER BY h.started_at DESC;
```

```none
 replica | size  |          started_at           | hydration_time | object_count | peak_memory | peak_disk
---------+-------+-------------------------------+----------------+--------------+-------------+-----------
 r1      | 400cc | 2026-09-08 09:12:04.117841+00 | 00:04:11.83    |           41 | 11 GB       | 2438 MB
(1 row)
```

Compare `peak_memory` against the replica sizes in [`mz_catalog.mz_cluster_replica_sizes`](/sql/system-catalog/mz_catalog/#mz_cluster_replica_sizes) to find the size that fits your workload. This lets you create a cluster at a generous size, hydrate once, and then size down with confidence. The new [cluster sizing guide](/clusters/sizing/) walks through that workflow, and [Optimize hydration requirements](/clusters/optimize-hydration-requirements/) covers what to do when a single object accounts for most of the peak.

### Improvements {#v26.42-improvements}
- **Vended credentials for Iceberg sink to GCP BigLake**: `CREATE CONNECTION ... TO ICEBERG CATALOG` now accepts a storage provider option, and `ACCESS DELEGATION` is allowed on GCP BigLake catalog connections, so an Iceberg catalog backed by Google Cloud Storage can authenticate with credentials the catalog vends. For more information, see [GCP BigLake](/export-data/iceberg-gcp/).
- **IANA time zone data updated to 2026c**: Time zone rules now follow IANA tzdata 2026c, covering Morocco's move to permanent +00 on 2026-09-20, Alberta's permanent -06, British Columbia's permanent -07, and Moldova's EU transition instants since 2022.
- **Pod priority classes in Self-Managed deployments**: Operators can set `environmentd.priorityClassName` and `clusterd.priorityClassName` in the Helm chart, so a higher-priority pod scheduled onto a full node no longer evicts Materialize ahead of other workloads.
- **Composite types in `mz-deploy` projects**: `mz-deploy` records the full catalog type for composite types such as records in `types.lock`, so views that read a dependency's record-typed column type check offline instead of resolving to a pseudo type.

### Guides {#v26.42-guides}
- [Size clusters for hydration](/clusters/sizing/)
- [Optimize hydration requirements](/clusters/optimize-hydration-requirements/)
- [Autoscaling for hydration](/clusters/autoscaling/)
- [Troubleshoot anomalies in memory usage](/clusters/troubleshoot-clusters/memory-spike/)
- [Troubleshoot anomalies in CPU usage](/clusters/troubleshoot-clusters/cpu-troubleshooting/)

### Bug Fixes {#v26.42-bug-fixes}
- Fixed `CREATE TABLE ... FROM SOURCE` and `ALTER SOURCE` connecting to a source's upstream system before checking the caller's privileges on that source, which let a role holding no privilege on the source read upstream schema, table, and column names out of the resulting purification errors; `CREATE TABLE ... FROM SOURCE` now requires `SELECT` on the source plus schema `USAGE`, and `ALTER SOURCE` requires ownership.
- Fixed `ALTER CLUSTER` resource-limit enforcement during graceful reconfiguration, which predicted a reshape's peak replica overlap instead of checking the replica set actually being created; a target that does not fit now leaves the existing replicas serving and reports `INSUFFICIENT_RESOURCES` with a hint.
- Fixed `ALTER CLUSTER ... WITH (WAIT UNTIL READY (..., ON TIMEOUT = 'COMMIT'))` needing room for the old and new replica sets at once when its deadline passed; the cut-over is now a single transaction that creates the target and retires the previous replicas together, so only the net change has to fit.
- Fixed cluster- and replica-scoped configuration not reaching the replacement replicas the cluster controller creates during a reconfiguration, so those replicas now apply the overrides before their first render.
- Fixed `mz_object_dependencies` omitting a sink's dependency on a user-defined type that the sink references through a `DOC ON TYPE` or `DOC ON COLUMN` option.
- Fixed `mz-deploy compile` rejecting valid SQL with `precision for type numeric must be between 1 and 39` when a view aggregated a `bigint` or `uint8` column with `sum()` and another view in the project read it, and fixed declared `numeric(p, s)` columns being stubbed with the scale in the precision position.

## v26.41.0
*Released to Materialize Cloud: 2026-09-10* <br>
*Released to Materialize Self-Managed: 2026-09-11* <br>

### Improvements {#v26.41-improvements}
- **Improved Clusters Page on console**: The Clusters Page now shows you per-replica usage, including CPU, memory, disk, and heap usage. Use the filters on the page to quickly identify unhealthy clusters. We've also sped up the page; page-loads which previously took ~600ms now take 25-50ms on environments with 2,000 objects.
- **MySQL snapshot parallelism enabled by default**: In v26.39, we launched [parallelized snapshots](/ingest-data/mysql/snapshot-parallelism/) for [MySQL sources](/ingest-data/mysql/) on tables which have a `CHAR` or `VARCHAR` primary key using the `utf8mb4` character set with the `utf8mb4_bin` collation. In our tests, we saw snapshot speedups of up to 80%. This behavior is now enabled by default.
- **Pre-flight reference checks in `mz-deploy`**: `mz-deploy apply`, `apply tables`, and their `--dry-run` forms now check every `CREATE TABLE ... FROM SOURCE` reference against what the source can actually expose before creating anything, and report the mismatches grouped by source with close-name suggestions instead of failing partway through the batch with a raw server error.

### Guides {#v26.41-guides}
- **Reorganized documentation**: The docs are now grouped by what you are trying to do, with [Fundamentals](/fundamentals/), [Clusters](/clusters/), [Developer tools](/developer-tools/), and [Export data](/export-data/). Every moved page redirects from its previous URL.
- [Export data to Snowflake on AWS, using the Iceberg Sink to AWS S3 Tables](/export-data/iceberg-aws-snowflake/)
- [Query History for Self-Managed](/self-managed-deployments/query-history/)
- [ADBC (Arrow Database Connectivity)](/serve-results/adbc/)
- [Understand the lifecycle of a source](/ingest-data/lifecycle-of-a-source/)
- [Upgrade the major version of your PostgreSQL source](/ingest-data/postgres/major-version-upgrade/)

### Bug Fixes {#v26.41-bug-fixes}
- Fixed `ALTER MATERIALIZED VIEW ... APPLY REPLACEMENT` run while a zero-downtime upgrade was in progress leaving the upgraded environment on the view's previous definition, which either put `environmentd` into a crash loop that restarting could not clear or left the view silently computing and serving the replaced definition.
- Fixed `EXPLAIN TIMESTAMP AS DOT` aborting `environmentd`, which let any role that can run SQL take an environment down with a single statement; the statement now returns an unsupported-format error.
- Fixed `environmentd` entering a crash loop that restarting could not clear, after an `ALTER MATERIALIZED VIEW ... APPLY REPLACEMENT` was followed by dropping the old definition's dependencies.
- Fixed a coordinator panic during `ALTER TABLE ... ADD COLUMN` when the schema change committed but its response was lost, so the retry now recognizes the evolution as already applied instead of reporting a mismatch.
- Fixed Iceberg sinks panicking during Parquet writes when the sink's schema no longer matched that of an existing table, which could recur on every sink restart or zero-downtime upgrade; the sink now reports the mismatch instead.
- Fixed MCP clients built on the official SDK failing the handshake, because Materialize answered `notifications/initialized` with `200` rather than the `202` the Streamable HTTP transport requires for a message that carries no reply.
- `ALTER CLUSTER ... WITH (WAIT FOR ...)` now rolls back when its timeout is processed while the target replicas are still unhydrated, matching `WAIT UNTIL READY`'s safe default instead of forcing a cut-over that can cause downtime; request the previous behavior explicitly with `WAIT UNTIL READY (..., ON TIMEOUT = 'COMMIT')`.
- Fixed the Console showing the previous region's clusters and Object Explorer contents after a region switch, until a full page refresh.

## v26.40.2
*Released to Materialize Cloud: 2026-09-07* <br>
*Released to Materialize Self-Managed: 2026-09-08* <br>

### Bug Fixes {#v26.40.2-bug-fixes}
- Fixed `ALTER MATERIALIZED VIEW ... APPLY REPLACEMENT` run while a zero-downtime upgrade was in progress leaving the upgraded environment on the view's previous definition, which either put `environmentd` into a crash loop that restarting could not clear or left the view silently computing and serving the replaced definition.

## v26.40.0
*Released to Materialize Cloud: 2026-09-02* <br>
*Released to Materialize Self-Managed: 2026-09-03* <br>

### Iceberg support for Databricks on AWS {#v26.40-iceberg-support-for-databricks-on-aws}

> **Public Preview:** This feature is in public preview.

Iceberg sinks can now write to Apache Iceberg tables registered in [Databricks
Unity Catalog](/export-data/iceberg-databricks/) on AWS, reached through
Unity Catalog's Iceberg REST catalog endpoint. Two new Iceberg catalog
connection options make this work: `OAUTH2 SERVER URL`, which names a token
endpoint that does not sit under the catalog URI, and `ACCESS DELEGATION =
'vended-credentials'`, which asks the catalog for temporary, table-scoped
storage credentials instead of static keys. Materialize refreshes both the
OAuth2 token and the vended credentials while the sink runs, so a sink that
outlives one credential lifetime keeps writing.

```mzsql
CREATE SECRET databricks_oauth
  AS '<client_id>:<client_secret>';

CREATE CONNECTION iceberg_catalog_connection TO ICEBERG CATALOG (
    CATALOG TYPE = 'rest',
    URL = 'https://<workspace>.cloud.databricks.com/api/2.1/unity-catalog/iceberg-rest',
    WAREHOUSE = '<catalog_name>',
    CREDENTIAL = SECRET databricks_oauth,
    OAUTH2 SERVER URL = 'https://<workspace>.cloud.databricks.com/oidc/v1/token',
    SCOPE = 'all-apis',
    ACCESS DELEGATION = 'vended-credentials'
);

CREATE SINK <sink_name>
  IN CLUSTER <sink_cluster>
  FROM <my_materialize_object>
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = '<unity_catalog_schema>',
    TABLE = '<my_iceberg_table>'
  )
  MODE APPEND
  WITH (COMMIT INTERVAL = '<commit_interval>');
```

For more information, see:
- [Guide: Databricks on AWS](/export-data/iceberg-databricks/)
- [`CREATE CONNECTION`: Iceberg catalog](/sql/create-connection/#iceberg-catalog), including [storage access delegation](/sql/create-connection/#iceberg-catalog-access-delegation)
- [`CREATE SINK`: Iceberg](/sql/create-sink/iceberg/), including [append mode](/sql/create-sink/iceberg/#append-mode)

### Improvements {#v26.40-improvements}
- **Query History for Self-Managed**: Self-Managed deployments can now use the Console's Query History view to debug latency and performance.
- **Bounded staleness isolation is generally available**: The [`bounded staleness <duration>`](/serve-results/isolation-level/#bounded-staleness) transaction [isolation level](/serve-results/isolation-level/) is out of public preview and is now a supported part of the [`transaction_isolation`](/serve-results/isolation-level/#setting-isolation-level) surface. See [when to use bounded staleness](/serve-results/isolation-level/#when-to-use-bounded-staleness) and its [restrictions](/serve-results/isolation-level/#restrictions).
- **Replica resource usage introspection**: A new `mz_introspection.mz_cluster_replica_resource_usage` relation reports each replica process's own memory, swap, and disk observations at a higher cadence than the roughly once-a-minute orchestrator samples, so a spike between two samples is no longer invisible.
- **Self-Managed: Automatic rollouts on GKE node pool upgrades**: The Materialize operator can now detect GKE node pool upgrades and automatically trigger rollouts to move workloads onto the new nodes, preventing outages from automatic node evictions. Deployments that use the [Materialize Terraform modules](/self-managed-deployments/installation/#install-using-terraform-modules) (v9.0.0 and later) get this configured for them, with no action needed; for all other deployments, see [GKE node pool upgrades](/self-managed-deployments/deployment-guidelines/gke-node-pool-upgrades/) for the setup steps.

### Agent Skills {#v26.40-agent-skills}
- **mz-optimize-memory**: A new skill that works top-down from a cluster's largest arrangements to a table of memory-reducing fixes — index changes, outer-join and subquery rewrites, window-function patterns, and arrangement size hints — with rules for estimating each saving before making the change and verifying it afterwards.

### Bug Fixes {#v26.40-bug-fixes}
- Fixed the MCP servers rejecting `tools/list`, `ping`, and `notifications/initialized` requests that carry any `params` — including the `_meta` field MCP clients are allowed to attach — with a non-JSON-RPC HTTP 422 that clients read as the server being unavailable.
- Fixed `ALTER MATERIALIZED VIEW ... APPLY REPLACEMENT` leaving a stale cached query plan behind, which put `environmentd` into a crash loop on every subsequent restart once a dependency of the replaced definition was dropped, and could otherwise leave the view computing its old definition.
- `CREATE TABLE ... FROM SOURCE` now requires `SELECT` on the source and `USAGE` on its schema, closing a case where `CREATE` on any schema a role controlled was enough to read a source that role had been denied; deployments where a platform team owns sources and application teams attach tables into their own schemas will need those `SELECT` grants added.
- Fixed `ALTER CONNECTION` letting a connection owner keep secrets and connections they lack `USAGE` privileges on, and read those secrets during content checks or connection validation.
- Fixed `ANY`/`ALL` over a `NULL` array or list returning the empty-set answer instead of `NULL`, and `array_position` failing to find `NULL` elements, both now matching PostgreSQL.
- Fixed `round(numeric, scale)` erroring on a scale that reaches past the value's fractional digits, such as `round(123::numeric, 38)`, which could also let filter pushdown discard data a query matched.
- Fixed identity-provider group sync silently finding nothing when `oidc_group_claim` names a claim the token declares directly, such as `roles`, so group-to-role mapping now works without a custom claim or JWT prehook.
- Fixed Arrow ADBC clients failing to connect by adding the missing `pg_type.typsend` column, and fixed `typreceive` rendering as a numeric OID rather than the function name, so those clients resolve every column to its real type.
- Fixed Iceberg sinks ignoring a table's `write.data.path` property and always writing data files to the default location.
- Fixed sources on the Console's Objects page being described in replica-hydration terms, which could show a healthy source as `Not Hydrated`, leave a webhook source with no status, and hold a completed snapshot at 99%.
- Fixed several `dbt-materialize` error paths reporting confusing failures instead of the intended messages, covering the index config parser, renaming a view, dropping an unsupported relation type, connection option parsing, and the version check against a server that is not Materialize.
- Fixed the `mz` CLI failing on read-only commands such as `mz sql` when `mz.toml` sits on a read-only mount.

## v26.39.0
*Released to Materialize Cloud: 2026-08-26* <br>
*Released to Materialize Self-Managed: 2026-08-27* <br>

### Improvements {#v26.39-improvements}
- **Improved connect modal in the console**: We've updated the UI to make it easier to connect coding agents to our MCP servers, and connect applications to Materialize.
- **Faster MySQL table snapshots** (private preview): Initial snapshots for MySQL tables are now parallelized. We saw speedups of up to 80%. When we tested a snapshot of a 2bn row table (2.45TB), previously the snapshot completed in 220 minutes. With the new parallelization, the snapshot completed in 43 minutes. Tables are eligible for parallel snapshots when they have a single-column `CHAR` or `VARCHAR` primary key using the `utf8mb4` character set with the `utf8mb4_bin` collation. For more information, see [MySQL snapshot parallelism](/ingest-data/mysql/snapshot-parallelism/).
- **App password expiration** (<red>*Materialize Cloud only*</red>): When creating an app password in the [Materialize Console](/developer-tools/console/), you can now set an optional expiration, after which the app password is no longer valid.

### Agent Skills {#v26.39-agent-skills}
- **mz-ontology-design**: A new skill that structures a Materialize SQL code base as a canonical ontology — a shared `raw` database, a shared `core` database, and one database per use case — with rules for semantic object grain and identity, temporal semantics, and a machine-readable relationship registry.
- **materialize-debug-freshness**: A new skill that diagnoses why an object is behind wall-clock time, sweeping source and sink status, attributing lag hop by hop, and ranking the dataflows and operators responsible.

### Bug Fixes {#v26.39-bug-fixes}
- Fixed zero-downtime upgrades cutting over before built-in materialized views rebuilt by the upgrade had hydrated, which made them all hydrate at once at cut-over, spiking `mz_catalog_server` CPU and slowing catalog queries.
- Fixed crashes and coordinator stalls when planning queries with long `JOIN` chains or long chains of CTEs.
- Fixed a `column "table_func_0" does not exist` error when a table function in the `SELECT` list is combined with `GROUP BY`, aggregates, or `HAVING`.
- Fixed out-of-memory crashes caused by large `SELECT` results over the HTTP and WebSocket APIs and by slow-reading `SUBSCRIBE` clients, with results now streaming incrementally over the WebSocket API, the result size limit now enforced on the HTTP API, and an error returned when a `SUBSCRIBE` client falls too far behind.
- Fixed hangs where a `SUBSCRIBE` over a query the optimizer folds to a constant would never end, and stopped dataflows from retaining source collections none of their outputs read.
- Fixed filter pushdown skipping data that matched a query, which could return too few rows, and fixed replica crashes when reading data with legacy or malformed statistics.
- Fixed SQL Server sources reporting inflated ingestion lag during the initial snapshot.
- `CREATE CONNECTION`, `ALTER CONNECTION`, and `VALIDATE CONNECTION` for AWS PrivateLink now reject a `SERVICE NAME` that is not an AWS VPC endpoint service name, such as a DNS hostname, instead of failing later with a misleading missing-availability-zones error.

## v26.38.2
*Released to Materialize Cloud: 2026-08-19* <br>
*Released to Materialize Self-Managed: 2026-08-25* <br>

### Dictionary compression {#v26.38-dictionary-compression}

> **Public Preview:** This feature is in public preview.

Dictionary compression reduces the memory that
[arrangements](/fundamentals/concepts/arrangements/#arrangements) use when a column holds the same values repeatedly. Instead of storing a repeated column value each time it appears, Materialize stores that value once and has each row reference it. This can reduce steady state memory requirements after [hydration](/fundamentals/concepts/hydration/) has completed.

Dictionary compression is off by default. You opt in per cluster with the
`EXPERIMENTAL ARRANGEMENT COMPRESSION` option:

```mzsql
-- Turn compression on for a new cluster
CREATE CLUSTER my_cluster (
    SIZE = '100cc',
    EXPERIMENTAL ARRANGEMENT COMPRESSION = true
);

-- Or turn it on for an existing cluster
ALTER CLUSTER my_cluster SET (EXPERIMENTAL ARRANGEMENT COMPRESSION = true);
```

For more information, see:
- [Guide: Dictionary compression](/transform-data/dictionary-compression/), including [when it helps and when it does not](/transform-data/dictionary-compression/#the-tradeoff)
- [`CREATE CLUSTER`: Dictionary compression](/sql/create-cluster/#dictionary-compression)
- [`ALTER CLUSTER`: Dictionary compression](/sql/alter-cluster/#dictionary-compression)

### Integrate with your observability stack {#v26.38-self-managed-observability}

<red>*Materialize Self-Managed only*</red>

Materialize Self-Managed now integrates with the observability tools you already
run. You can export metrics, and optionally logs, from Materialize to Datadog,
Honeycomb, Google Cloud Monitoring, Prometheus remote write, or any monitoring
backend with an Open Telemetry (OTLP) endpoint. Template dashboards and alerts are provided to
help you get started.

Follow the instructions for your destination:
- [Datadog](/observability/self-managed/datadog/)
- [Honeycomb](/observability/self-managed/honeycomb/)
- [Google Cloud Monitoring](/observability/self-managed/google-cloud-monitoring/)
- [Prometheus remote write](/observability/self-managed/prometheus-remote-write/), for Mimir, Amazon Managed Prometheus, or Grafana Cloud
- [OpenTelemetry](/observability/self-managed/opentelemetry/), for any other OTLP endpoint, including your own collector

If you don't have an observability stack set up, the [Materialize Terraform
modules](/self-managed-deployments/installation/#install-using-terraform-modules)
can deploy one alongside Materialize. It collects metrics from Materialize and
from your Kubernetes cluster, collects Materialize's container logs and
Kubernetes events, stores both in your own object storage, and ships [Grafana](/observability/self-managed/grafana/)
dashboards and Alertmanager alert rules to query them. The stack is controlled by
the `enable_observability` variable, which defaults to `true` starting with
v11.0.0 of the modules.

For more information, see:
- [Monitoring Self-Managed Materialize](/observability/self-managed/)
- [How logs and metrics are stored and delivered](/observability/self-managed/storage/)
- [Alerting](/observability/self-managed/alerting/)

### Improvements {#v26.38-improvements}
- **Notice for single-replica sources on multi-replica clusters**: Materialize now warns when a command leaves a cluster holding more than one replica alongside PostgreSQL, MySQL, or SQL Server sources, which always run on a single replica, since the extra replicas make those sources neither more fault tolerant nor faster to ingest.
- **Self-Managed: Graceful resizing of system clusters**: `ALTER CLUSTER ... SET (SIZE ...)` on a system cluster such as `mz_catalog_server` or `mz_system` now runs as a background graceful reconfiguration, with a 24-hour default deadline and a rollback on timeout, instead of recreating the whole replica set at once, so `SHOW CLUSTERS` settles on the new configuration rather than flipping to it.

### Agent Skills {#v26.38-agent-skills}
- **materialize-debug-freshness**: New agent skill for diagnosing why an object is behind wall-clock time, whether that surfaces as a stale materialized view, index, or sink, or as a freshness alert. Running on the read-only tools of the Materialize developer MCP server, it ranks what is lagging, attributes the lag to a single hop, then rules out in-progress hydration, a replica dominated by one dataflow, and per-worker skew before naming the culprit operator and the SQL responsible for the expensive work.
- **mz-deploy**: New agent skill covering the `mz-deploy` CLI — project layout, the compile/test/apply/stage/promote workflow, deploy IDs and staging suffixes, schema-granularity conflict detection, stable API schemas, profile resolution, and the `EXECUTE UNIT TEST` grammar.
- **mz-sql-lsp**: New Claude Code plugin, installable from the `agent-skills` repository's new `materialize` plugin marketplace, that registers the `mz-deploy` language server for `.sql` files so agents can use go-to-definition, hover, and workspace symbols in an mz-deploy project instead of text search.

### Bug Fixes {#v26.38-bug-fixes}
- Fixed an `INSERT` that ran concurrently with an `ALTER TABLE ... ADD COLUMN` crashing the server; the insert now fails with a retryable serialization error instead.
- Fixed an environment restarting every few seconds and never becoming reachable when it held a sealed collection whose dependency had no readable history left; such a collection no longer blocks startup, so an operator can drop and recreate the affected object.
- Fixed filter pushdown discarding data that matched the query when a float column contained negative `NaN` values, so the query returned too few rows.
- Fixed a `TIMESTAMPTZ` literal near the end of the representable range, and rounding such a value to a lower precision, aborting the server.
- Fixed several date/time and range text-format bugs: a sub-second value that rounded up to a full second rendered about a second early, a `TIME` string naming no time field was accepted instead of erroring, a quoted range bound kept its quotes so a `tsrange` could not survive a `::text::tsrange` round trip, and a BC date was not quoted inside a composite value.
- Fixed a regular expression exhausting server memory before erroring — a pattern under the documented 1 MiB limit could allocate several gigabytes while being translated — by also rejecting patterns with more than 2000 character classes, counting each Unicode, Perl, or POSIX class such as `\p{L}`, `\d`, or `[[:alpha:]]`, and each range such as `a-z`.
- Fixed a webhook source's `CHECK` expression having no bound on the memory it may allocate, which let concurrent requests to a source with an amplifying check exhaust server memory; a check that exceeds the budget, 20 MiB per request by default, is now refused with a `400` response.
- Fixed the enforced connection limit picking up an `ALTER SYSTEM SET max_connections` from a transaction that was then rolled back, so the limit clients were held to could differ from the committed value.
- Fixed `dbt-materialize`'s `deploy_init` failing when `CI_TAG` is set, the setup the blue/green deployment documentation prescribes, and made it quote the deployment schema consistently so a schema name that is not a bare lowercase identifier is handled correctly throughout the operation.
- Fixed the comment `dbt-materialize`'s `deploy_promote` puts on each promoted schema ending without a timestamp.

## v26.37.0
*Released to Materialize Cloud: 2026-08-12* <br>
*Released to Materialize Self-Managed: 2026-08-13* <br>

### Improvements {#v26.37-improvements}
- **Self-Managed: Highly available operator**: The Materialize operator now runs two replicas by default, so rolling out an operator update no longer interrupts the CRD conversion webhook. Installations that manage their own RBAC must grant the operator `get`, `create`, and `update` on `leases` in `coordination.k8s.io`, because the two replicas coordinate through lease-based leader election.
- **`IF NOT EXISTS` for clusters and replicas**: `CREATE CLUSTER` and `CREATE CLUSTER REPLICA` now accept an `IF NOT EXISTS` clause, so an existing cluster returns an `already exists, skipping` notice instead of an error. Provisioning scripts can now run idempotently, without a pre-flight existence check.

### Bug Fixes {#v26.37-bug-fixes}
- Fixed a prepared statement with a parameterized `LIMIT` failing with `Top-level LIMIT must be a constant expression` whenever the bound parameter's type was not `bigint`.
- Fixed `ALTER CLUSTER ... SET (REPLICATION FACTOR ...)` on a built-in cluster such as `mz_system` or `mz_support` being undone on the next restart, which could also wedge later replication-factor changes.
- Fixed session parameter changes that an implicit transaction reverts not being announced to the client, so drivers that cache `ParameterStatus` such as pgjdbc and psycopg kept reporting a value the server had already discarded.
- Fixed extended-protocol `Parse` and `Bind` messages carrying more than 32767 parameters, parameter types, or format codes being misdecoded, which left the rest of the message misaligned.
- Fixed Avro object container file decoding reading a previous block's bytes into values, and bounded a block's declared object count so that a malformed file of a few dozen bytes can no longer cost minutes of decoding work.
- Fixed a bare `map` in an option value failing to parse, which broke statements such as a Kafka sink with `TOPIC = "map"` and a materialized view's `PARTITION BY`.
- Fixed the binary wire format accepting `Infinity` and `-Infinity` as a `numeric` parameter, a value no SQL literal can name.
- Fixed a stalled catalog snapshot in the MCP server hanging a request indefinitely instead of failing it at the configured request timeout.
- Fixed `balancerd` panicking at startup when the target `environmentd` service's DNS name was not yet resolvable, which could happen during an upgrade; startup now retries with backoff for a configurable 30 seconds.
- Fixed Iceberg sinks counting every row twice in `messages_staged`, which drew the Console's Staged line at double the committed rate, and fixed the Console's sink statistics charts rendering a failed subscribe as an empty chart pinned at 0.
- Fixed `ALTER NETWORK POLICY`, `GRANT`/`REVOKE USAGE ON NETWORK POLICY`, and `ALTER NETWORK POLICY ... OWNER TO` failing to resolve a quoted identifier such as `"hyphenated-name"`.
- Fixed a query with a very large `LIMIT` crashing a cluster replica in a loop, which any user able to query an indexed relation could trigger with a single statement.
- Fixed a persist command that retried for minutes committing a stale lease heartbeat, which could cost a read handle its lease.
- Fixed Self-Managed deployments defaulting to an alternative materialized view sink implementation that could block cluster worker threads and cost readers their leases; it is now off by default, matching Materialize Cloud.
## v26.36.0
*Released to Materialize Cloud: 2026-08-07 on as-needs basis* <br>
*Released to Materialize Self-Managed: 2026-08-07* <br>

### Improvements {#v26.36-improvements}
- **`dbt-materialize`: `AUTO SCALING STRATEGY` support**: The dbt adapter now supports the `AUTO SCALING STRATEGY` cluster option, so you can speed up cluster hydration from your dbt workflows. You can set, reset, and disable it on a cluster, and `deploy_init` will automatically copy strategy configuration during blue/green deploys.
- **Updated timezone data**: The IANA timezone database has been updated from 2022g to 2025b, correcting timezone rules for Egypt, Kazakhstan, Paraguay, and Greenland that changed since 2023. Numeric timezone abbreviations (e.g., `+05`) now render correctly in `pg_timezone_names`.

### Bug Fixes {#v26.36-bug-fixes}
- Fixed a coordinator panic when a client abandoned a connection attempt that had already failed, such as an HTTP request that disconnects or times out.
- Fixed `EXTRACT(YEAR ...)` and `make_timestamp` returning incorrect results for BC dates, where year numbering was off by one.
- Fixed interval range qualifiers incorrectly dropping fields above the range's high end, causing expressions like `INTERVAL '1 2:03' HOUR TO MINUTE` to lose the day component.
- Fixed date parsing to honor the `DateStyle` MDY convention, so `date '01/02/03'` now correctly parses as `2003-01-02` instead of `0001-02-03`.
- Fixed array and list text output not quoting elements matching `NULL` case-insensitively, causing values like `'null'` to round-trip incorrectly as `NULL`.
- Fixed interval text output spelling the months field as `month(s)` instead of `mon(s)`, which caused psycopg to silently drop all components after the months field.
- Fixed `CREATE VIEW` and `CREATE MATERIALIZED VIEW` silently accepting a column name list shorter than the number of output columns.
- Fixed binary-protocol time parameters outside the valid range being accepted instead of rejected with an error.
- Fixed `INTERSECT` queries with many branches exhausting environmentd memory during query planning.
- Fixed `DISCARD ALL` not resetting session variables to their defaults when using the extended query protocol.
- Fixed `SET extra_float_digits` being accepted but having no effect on query output. Zero and negative values now limit float precision as in PostgreSQL.
- Fixed out-of-range `REFRESH AT` or `ALIGNED TO` times causing a coordinator panic that dropped all client connections.
- Fixed queries larger than 2 MiB terminating the client's connection instead of returning a recoverable error.
- Fixed `SHOW CLUSTER REPLICAS` and `SHOW OBJECTS` returning incorrect results or missing rows when a cluster replica and a catalog item shared the same internal ID.
- Fixed `UNION ALL` of record types failing with an internal error when fields differed only in nullability.
- Fixed SQL Server sources with `CHAR(N)` columns using multi-byte character encodings failing to replicate correctly.
- Fixed MySQL sources where dropping a table during snapshotting could jam the entire source instead of erroring only the affected table.
- Fixed an `ALTER CLUSTER` without a `WITH (WAIT ...)` clause resetting the deadline of an in-flight graceful cluster reconfiguration.
- Fixed `mz-deploy apply-all` failing when a cluster file references a project-defined role, because the roles phase ran after the clusters phase.
- Fixed `mz-deploy compile` and `mz-deploy stage` failing with `type "text[]" does not exist` for projects whose dependencies have array-typed columns.

## v26.35.0
*Released to Materialize Cloud: 2026-07-29* <br>
*Released to Materialize Self-Managed: 2026-07-30* <br>

### Asynchronous Cluster Reconfiguration {#v26.35-background-cluster-reconfiguration}
`ALTER CLUSTER` now runs configuration changes (such as resizing) in the background, rather than blocking until the new replica set is ready. This means you can start a reconfiguration and move on to other tasks while the process completes.

Because the command is now asynchronous, you can monitor the
progress of an in-flight reconfiguration using `SHOW CLUSTERS`.

```mzsql
SHOW CLUSTERS;
```
```nofmt
    name    | replicas   |           activity           | comment
------------+------------+------------------------------+---------
 my_cluster | r1 (400cc) | reconfiguring size to 1600cc |
```

For detailed status, query
[`mz_internal.mz_cluster_reconfigurations`](/sql/system-catalog/mz_internal/#mz_cluster_reconfigurations),
which reports the target shape, the deadline, and the reconfiguration's
lifecycle `status` (`in-progress`, then a terminal `finalized`, `timed-out`,
`cancelled`, or `resource-exhausted`):

```mzsql
SELECT cluster_id, status, deadline, on_timeout, target, changes
FROM mz_internal.mz_cluster_reconfigurations;
```

For more information, see [`ALTER CLUSTER`: Resizing process](/sql/alter-cluster/#resizing-process).

### AWS Glue Schema Registry Support for Sinks {#v26.35-aws-glue-schema-registry-support-sinks}

> **Public Preview:** This feature is in public preview.

Kafka sinks can now use [AWS Glue Schema
Registry](/sql/create-connection/#aws-glue-schema-registry) for Avro schema
management, via the new `FORMAT AVRO USING AWS GLUE SCHEMA REGISTRY` syntax on
[`CREATE SINK`](/sql/create-sink/kafka/). With Glue now supported on both sources and sinks, you can manage your Kafka schemas end to end on AWS.

```mzsql
-- Authenticate to AWS Glue through an AWS connection.
CREATE CONNECTION aws_connection TO AWS (
    ASSUME ROLE ARN = 'arn:aws:iam::123456789000:role/MaterializeGlue'
);

CREATE CONNECTION glue_connection TO AWS GLUE SCHEMA REGISTRY (
    AWS CONNECTION = aws_connection,
    REGISTRY = 'default-registry'
);

-- Write Avro-encoded output, registering schemas with AWS Glue.
CREATE SINK avro_sink
  IN CLUSTER my_io_cluster
  FROM my_materialized_view
  INTO KAFKA CONNECTION kafka_connection (TOPIC 'test_topic')
  KEY (key)
  FORMAT AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION glue_connection (
    KEY SCHEMA NAME = 'test_topic-key',
    VALUE SCHEMA NAME = 'test_topic-value'
  )
  ENVELOPE UPSERT;
```

For more information, see [`CREATE SINK`: Using AWS Glue Schema Registry](/sql/create-sink/kafka/#using-aws-glue-schema-registry).

### Kafka: Source versioning {#v26.35-kafka-source-versioning}

Kafka sources now support source versioning, so you can adopt upstream Avro schema changes without downtime. This uses the same mechanism already available for PostgreSQL, MySQL, and SQL Server sources, by creating a new table with the evolved schema and swapping it into place with a blue/green cutover.

There is new syntax for [`CREATE SOURCE`](/sql/create-source/kafka-v2/) and [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/kafka/) for creating and versioning tables independently. Materialize resolves the latest registered Avro schema when the `CREATE TABLE` statement runs, and pins it as the table's reader schema.

For more information, refer to:
- [Guide: Handling upstream schema changes with zero
  downtime](/ingest-data/kafka/source-versioning/)
- [Syntax: `CREATE SOURCE`](/sql/create-source/kafka-v2/)
- [Syntax: `CREATE TABLE`](/sql/create-table/kafka/)

### Improvements {#v26.35-improvements}
- **Faster read queries under write load**: Read-only queries (e.g., `SELECT 1`) are no longer blocked by concurrent write transactions; under high write load, victim query latency drops from multiple seconds to single-digit milliseconds.
- **Better query plans for correlated subqueries**: Queries using patterns like `1 IN (SELECT 1 WHERE p)` and `NOT EXISTS (SELECT 1 WHERE p)` are now optimized to a simple filter, eliminating unnecessary semi/anti-joins for faster queries.
- **Account hierarchy billing**: Organizations running multiple Materialize accounts under one parent (e.g., separate production and staging accounts) can now see consolidated billing and usage at the parent level, broken out per child account; each child account sees only its own usage. Available on request — talk to your account executive to see if you qualify.
- **`mz-debug` CPU profiling**: The `mz-debug` diagnostic tool now automatically collects CPU profiles alongside memory profiles for Self-Managed deployments.

### Bug Fixes {#v26.35-bug-fixes}
- Fixed queries with many chained `INTERSECT` operations (e.g., 35+ inputs) exhausting environmentd memory during planning, causing the environment to become unresponsive.
- Fixed a MySQL source stalling entirely when one of its tables was dropped while the initial snapshot was running; the dropped table now reports an error on its own and the rest of the snapshot proceeds.
- Fixed a critical bug where a pending replacement materialized view could destroy the data of its live target materialized view after an environmentd restart.
- Fixed `COPY FROM PARQUET` failing for columns of types `oid`, `time`, `timestamptz`, `char`, `varchar`, and `mz_timestamp`.
- Fixed incorrect results for `variance`, `stddev`, and related aggregate functions when used with `DISTINCT` on inputs containing values that differ only in sign (e.g., `-2` and `2`).
- Fixed `ALTER CLUSTER ... WITH (WAIT UNTIL READY ...)` hanging indefinitely and rolling back when the cluster hosts a single-replica source (PostgreSQL, MySQL, or SQL Server).
- Fixed `mz_object_arrangement_sizes` silently omitting arrangements smaller than 10 MiB and showing stale sizes after an environmentd restart.
- Fixed `EXPLAIN FILTER PUSHDOWN FOR MATERIALIZED VIEW` crashing environmentd when the materialized view's cached plan referenced a since-dropped index.
- Fixed array literals with empty dimensions (e.g., `'{{},{}}'::text[]`) and multi-dimensional `array_fill` calls silently producing incorrect results instead of returning errors matching PostgreSQL behavior.
- Fixed replica utilization charts in the Console failing to load on initial page render and flashing a loading spinner when switching time filters.
- Fixed replica crash and OOM markers not appearing in the "Last hour" and "Last 3 hours" Console utilization chart windows.

## v26.34.1
*Released to Materialize Self-Managed: 2026-07-24* <br>

### Asynchronous Cluster Reconfiguration {#v26.34.1-graceful-cluster-reconfiguration}

<red>*Materialize Self-Managed only*</red>

`ALTER CLUSTER` now runs configuration changes (such as resizing) in the background, rather than blocking until the new replica set is ready. This means you can start a reconfiguration and move on to other tasks while the process completes.

Because the command is now asynchronous, you can monitor the
progress of an in-flight reconfiguration using `SHOW CLUSTERS`.

```mzsql
SHOW CLUSTERS;
```
```nofmt
    name    | replicas   |           activity           | comment
------------+------------+------------------------------+---------
 my_cluster | r1 (400cc) | reconfiguring size to 1600cc |
```

For detailed status, query
[`mz_internal.mz_cluster_reconfigurations`](/sql/system-catalog/mz_internal/#mz_cluster_reconfigurations),
which reports the target shape, the deadline, and the reconfiguration's
lifecycle `status` (`in-progress`, then a terminal `finalized`, `timed-out`,
`cancelled`, or `resource-exhausted`):

```mzsql
SELECT cluster_id, status, deadline, on_timeout, target, changes
FROM mz_internal.mz_cluster_reconfigurations;
```

For more information, see [`ALTER CLUSTER`: Resizing process](/sql/alter-cluster/#resizing-process).

### Bug Fixes {#v26.34.1-bug-fixes}
- Fixed an issue where `ALTER CLUSTER ... WITH (WAIT UNTIL READY ...)` would deadlock on clusters hosting single-replica sources (Postgres, MySQL, SQL Server), causing graceful reconfiguration to time out and roll back without resizing.

## v26.34.0
*Released to Materialize Cloud: 2026-07-21* <br>
*Released to Materialize Self-Managed: 2026-07-21* <br>

### Autoscaling to speed up hydration {#v26.34-autoscaling-hydration}

> **Public Preview:** This feature is in public preview.

Managed clusters can now temporarily scale up to accelerate hydration.

Using the `AUTO SCALING STRATEGY (ON HYDRATION)` strategy, Materialize runs an extra burst replica at the
larger `HYDRATION SIZE` while the cluster's objects are un-hydrated. Once a steady-size replica hydrates, the burst replica is retired. An optional `LINGER DURATION` keeps the burst replica running for a grace period after the steady-size replicas hydrate.

```mzsql
-- Create a cluster that spins up a 1600cc burst replica while hydrating
CREATE CLUSTER my_cluster (
    SIZE = '400cc',
    AUTO SCALING STRATEGY = (
        ON HYDRATION (HYDRATION SIZE = '1600cc', LINGER DURATION = '600s')
    )
);
```

You can add, change, or remove the strategy on an existing cluster with
`ALTER CLUSTER`:

```mzsql
ALTER CLUSTER my_cluster SET (
    AUTO SCALING STRATEGY = (ON HYDRATION (HYDRATION SIZE = '1600cc'))
);
```

For more information, see the `AUTO SCALING STRATEGY` option on
[`CREATE CLUSTER`](/sql/create-cluster/#autoscaling) and
[`ALTER CLUSTER`](/sql/alter-cluster/#speed-up-hydration-by-autoscaling-to-a-larger-size).

### Role Mapping via SCIM {#v26.34-role-mapping-scim}

<red>*Materialize Cloud only*</red>

You can provision identity provider groups via SCIM and map their members to Materialize database roles. The revised setup described in the guide uses an explicit intermediate mapping: assign each synced group a custom organization role, then create a database role matching that organization role’s JWT key. IdP group names can differ from database role names. For setup and migration steps, see [Sync IdP groups](/security/cloud/users-service-accounts/sync-idp-groups/).

### Improvements {#v26.34-improvements}
- **Azure SQL source support**: Materialize can now ingest data from Azure SQL databases using the [SQL Server source connector](/ingest-data/sql-server/).
- **Configurable Iceberg sink commit interval**: The [commit interval](/sql/create-sink/iceberg/#commit-interval-tradeoffs) of an existing Iceberg sink can now be altered using `ALTER ... SET COMMIT INTERVAL`, with a minimum of 1 second.
- **MCP query tool replica routing**: The MCP developer query tool now accepts a `cluster_replica` parameter, enabling `EXPLAIN ANALYZE` on clusters with more than one replica.
- **Smaller container images**: The `environmentd` and `clusterd` container images now use a distroless base, reducing image size and attack surface for Self-Managed deployments.

### Agent Skills {#v26.34-agent-skills}
To start using our skills, install them with `npx skills add MaterializeInc/agent-skills`. To update your installed skills, run `npx skills update`. For more information, see [Coding agent skills](/developer-tools/mcp-server/coding-agent-skills/).

- **Materialize Terraform Provider**: New agent skill covering Terraform provider configuration for Cloud and self-managed deployments, resource conventions, cross-resource patterns, import workflows, and known gotchas.
- **Materialize Terraform Self-Managed**: New agent skill covering the Terraform modules for deploying self-managed Materialize on AWS, Azure, and GCP, including IAM-based storage auth, upgrade procedures, and project integration patterns.

### Bug Fixes {#v26.34-bug-fixes}
- Fixed a critical bug where a pending replacement materialized view could destroy the data of its live target materialized view after an environmentd restart, by advancing the shared persist shard's since to the empty frontier.
- Fixed a correctness bug in join processing where incoming batches could be silently dropped after trace compaction, causing lost updates without error.
- Fixed multiple soundness bugs in persist filter pushdown that could silently drop matching rows or cause `persist filter pushdown correctness violation` panics.
- Fixed a bug in multi-statement read transactions where a timestamp-independent first statement (e.g., a query over a constant-folded view) could cause subsequent statements to read from incorrect time domains, resulting in errors or incorrect results.
- Fixed `ALTER MATERIALIZED VIEW ... APPLY REPLACEMENT` crashing the coordinator when a temporary view or index depended on the target materialized view.
- Fixed non-temporary objects (views, indexes, etc.) being allowed to depend on temporary objects, which could lead to dangling references when the session ended.
- Fixed stack overflow crashes in the adapter when processing environments with deeply nested object dependencies.
- Fixed a stack overflow when comparing deeply nested values (e.g., deeply nested JSONB) in query result ordering.
- Fixed a stack overflow when executing read-then-write statements (e.g., `INSERT INTO ... SELECT`) over deeply chained view hierarchies.
- Fixed stack overflow or memory exhaustion when resolving pathologically deep or wide custom types.
- Fixed a crash on diskless replicas where restarting upsert sources could encounter stale RocksDB state.
- Fixed environmentd crash-looping on startup when a tombstoned persist shard was still referenced in the catalog.
- Fixed `SET TRANSACTION ... READ WRITE` silently modifying session state before returning an error.
- `CREATE ROLE` now rejects the reserved role specification names `current_user`, `current_role`, `session_user`, `user`, and `none`.
- Fixed a user-created schema named `information_schema` bypassing the `mz_catalog_server` cluster restriction, allowing user queries to run on a reserved system cluster.
- Fixed `kubectl apply --server-side` failing for Materialize v1 CRDs when managed fields were originally recorded at v1alpha1, blocking GitOps tooling in Self-Managed deployments.
- Fixed the Self-Managed Console deriving the MCP server URL from the pgwire hostname instead of the HTTP endpoint, causing MCP connections to fail when pgwire and HTTP are served on separate hostnames.

## v26.33.0
*Released to Materialize Cloud: 2026-07-16* <br>
*Released to Materialize Self-Managed: 2026-07-17* <br>

### Improved hydration times on Materialize Cloud {#v26.33-upgraded-cloud-hardware}

<red>*Materialize Cloud only*</red>

We've upgraded cluster hardware for all Materialize Cloud environments. The new hardware speeds up compute-intensive
operations. We've observed a 10%–66% reduction in hydration times. You don't need to take any actions. The improvement is live across all Materialize Cloud
environments, on all new and existing clusters.

### READ COMMITTED isolation for PostgreSQL metadata databases {#v26.33-pg-consensus-read-committed}

<red>*Materialize Self-Managed only*</red>

Starting in v26.33, self-managed deployments that use a PostgreSQL metadata
database can configure Materialize to run its internal metadata queries under
`READ COMMITTED` transaction isolation instead of `SERIALIZABLE`. This improves metadata
write throughput. To enable this isolation mode, enable the `persist_pg_consensus_read_committed` system parameter after completing an upgrade to v26.33.

> **Note:** The parameter applies only to PostgreSQL metadata databases. Only enable it
> after you have upgraded your self-managed deployment to v26.33 or later.

For details, see the [Self-Managed upgrade
notes](/self-managed-deployments/upgrading/version-notes/).

### Improvements {#v26.33-improvements}
- **`EXPLAIN ANALYZE` on multi-replica clusters via MCP**: The Materialize MCP developer endpoint's `query` tool now accepts an optional cluster replica parameter, so `EXPLAIN ANALYZE` can target a specific replica.
- **Faster queries on busy environments**: We've improved query latency on query-heavy clusters. We've reduced by caching the catalog snapshot for the duration of a session. In our tests, we've seen QPS improvements of up to 13%.
- **Improved responsiveness under load**: A slow timestamp oracle no longer stalls unrelated sessions that are running `EXPLAIN TIMESTAMP` or `SUBSCRIBE`.
- **New materialize-dbt [agent skill](/developer-tools/mcp-server/coding-agent-skills/)**: The
  `materialize-dbt` skill helps coding agents build and manage dbt models for
  Materialize.

### Bug Fixes {#v26.33-bug-fixes}
- Fixed server crashes triggered by stack overflows while computing object dependencies and read privileges.
- Fixed catalog corruption and coordinator panics triggered by `ALTER SCHEMA RENAME` when the target schema contains user-defined types, functions, or temporary objects.
- Fixed a crash that could occur when a `SUBSCRIBE` ran while an index or other dependency it read was concurrently dropped; the query now returns a clean error.
- Fixed a crash triggered by binding a non-UTF-8 `char` parameter over the extended query protocol.
- Calling `mz_any` or `mz_all` with a non-boolean argument now returns a planning error instead of crashing a compute worker.
- Polymorphic array functions such as `array_remove` now return a planning error instead of dropping the connection when an argument would produce an array of `list` or `map`.
- Fixed a class of crashes where cancelling or tearing down a statement (for example, `DROP CLUSTER`) while it was being dispatched could abort the server.
- Fixed a crash where scraping the usage metrics endpoint could abort the server when an unmanaged cluster replica was present.
- Fixed queries with nested, shadowed common table expressions returning incorrect results.
- Fixed queries that reference a correlated CTE from a nested correlated scope returning incorrect results.
- Fixed `SHOW COLUMNS` returning duplicate rows for certain system catalog objects after upgrading across releases.
- Query results that fit within `max_result_size` are no longer incorrectly rejected by an over-counted memory estimate.
- `DROP SCHEMA` without `CASCADE` no longer silently drops a schema that contains only user-defined types or functions; it now correctly treats the schema as non-empty.
- Casting large OID values from text (`2147483648` through `4294967295`) and copying into `oid` columns no longer fail with an invalid-input error.
- `NUL` bytes supplied to text values through query parameters, the HTTP SQL API, `COPY FROM`, and `convert_from` are now rejected, matching PostgreSQL.
- A `COPY` that fails before entering copy mode no longer corrupts or hangs the connection for clients such as pgx and libpq.
- `RESET` and `DISCARD ALL` now restore client-supplied startup parameters, such as the connected database, rather than server defaults, fixing connection poolers that rebound pooled sessions to the wrong database.
- Fixed PostgreSQL sources so that upgrades correctly handle `oid` values above the signed 32-bit range instead of leaving replication stuck.
- Fixed PostgreSQL sources that exclude a column erroneously halting when the excluded column and its constraint were dropped upstream.
- Kafka source and sink metadata refresh intervals below one second are now rejected, and existing definitions with smaller values are migrated automatically on upgrade.
- `COPY FROM` can now read array columns from Arrow files that were written by `COPY TO`.
- `GRANT` and `REVOKE USAGE ON ALL POLICIES` now correctly grant and revoke network-policy privileges instead of silently succeeding as a no-op.
- Fixed the system administrator role being unable to invoke certain side-effecting functions, such as terminating backend sessions.
- Closed a resource-isolation gap that allowed `INSERT ... SELECT` and `COPY ... TO <url>` reads of user objects to run on the reserved `mz_catalog_server` cluster.
- Fixed inline credentials in `CREATE CONNECTION` options being written in clear text to redacted SQL and telemetry.
- Error messages that include connection URLs now redact embedded credentials instead of exposing the username and password.

## v26.32.0
*Released to Materialize Cloud: 2026-07-09* <br>
*Released to Materialize Self-Managed: 2026-07-10* <br>

### Improvements {#v26.32-improvements}
- **`COPY TO` replica routing**: `COPY TO` now honors the session's `cluster_replica` setting, matching the behavior of regular `SELECT` queries.

### Agent Skills {#v26.32-agent-skills}
- **MCP Developer Analysis**: Updated to document the developer `query` tool and `EXPLAIN ANALYZE` workflow for querying user objects on named clusters.

### Bug Fixes {#v26.32-bug-fixes}
- Fixed internal HTTP endpoints not enforcing role-based authorization in Self-Managed deployments with password or OIDC authentication, allowing any authenticated user to access internal administration routes.
- Fixed `CREATE REPLACEMENT MATERIALIZED VIEW ... FOR <target>` not requiring ownership of the target view, allowing another role to block the owner from using the replacement workflow on their own object.
- Fixed secret values potentially appearing in `mz_internal.mz_statement_execution_history` error messages when `CREATE SECRET` or `ALTER SECRET` commands failed.
- Fixed `COMMENT` bodies and `PARTITION BY` option values not being redacted in redacted SQL output, leaking user-provided text across the redaction boundary.
- Fixed float-to-integer casts silently accepting out-of-range boundary values instead of raising errors, affecting `float4`-to-`uint32`/`uint64` and `float8`-to-`uint8` conversions.
- Fixed narrowing integer casts (`uint4` to `uint2`, `smallint`, or `integer`) silently filtering out rows with out-of-range values instead of raising errors when used in indexed filter expressions.
- Fixed incorrect results when casting arrays between element types.
- Fixed `varchar` columns reporting incorrect column type metadata.
- Fixed read-only transactions incorrectly accepting write operations after a constant expression peek (e.g., `SELECT 1`), which could silently commit data or cause panics on subsequent writes.
- Fixed a priority inversion where sustained strict-serializable reads could stall the coordinator by starving group commit, causing the environment to appear stuck until clients disconnected.
- Fixed coordinator stalls when granting privileges to many roles in a single transaction.
- Fixed `generate_series` entering an infinite loop when called with a timestamp interval that mixes months and days in a way that prevents forward progress (e.g., `INTERVAL '1 month -29 days'`).
- Fixed `mz_sleep` panicking on invalid input values instead of returning an error.
- Fixed stale query cancellations from a previous statement incorrectly canceling the next statement within an explicit transaction.
- Fixed `ALTER CLUSTER ... WITH (WAIT FOR ...)` and `WITH (WAIT UNTIL READY ...)` being silently accepted and ignored on unmanaged clusters instead of returning an error.
- Fixed `SUBSCRIBE` returning an internal error code (`XX000`) instead of the standard "undefined object" code (`42704`) when referencing a non-existent object.
- Fixed `TopK` query optimization losing `expected_group_size` hints during operator fusion, causing unnecessary overhead in query execution.
- Fixed `app.kubernetes.io/name` label missing from environmentd Kubernetes resources when using the `v1alpha1` CRD.

## v26.31.2
*Released to Materialize Self-Managed: 2026-07-08* <br>

### Bug Fixes {#v26.31.2-bug-fixes}

- Fixed a priority inversion bug where sustained strict-serializable / real-time-recency reads
  could starve group commit, leading to livelock in the database coordinator. This would cause
  queries to hang until pending reads drained.

## v26.31.0
*Released to Materialize Cloud: 2026-07-02* <br>
*Released to Materialize Self-Managed: 2026-07-03* <br>

### AWS Glue Schema Registry Support {#v26.31-aws-glue-schema-registry-support}
Kafka sources can now use AWS Glue Schema Registry for Avro schema management via the new `FORMAT AVRO USING AWS GLUE SCHEMA REGISTRY` syntax. This is an alternative to the Confluent Schema Registry, enabling organizations that standardize on AWS Glue to connect their Kafka topics to Materialize without switching schema registries.

### Materialize CRD v1 for Self-Managed {#v26.31-materialize-crd-v1}
Self-managed Kubernetes deployments can now opt in to the v1 Materialize Custom Resource Definition (`materialize.cloud/v1`). The v1 CRD simplifies rollout behavior: rollouts trigger automatically when spec fields change, so you no longer need to set a new `requestRollout` UUID on every change. Adopting `v1` is opt-in, and existing `v1alpha1` deployments continue to work unchanged.

For more information, see the [Self-Managed upgrade notes](/self-managed-deployments/upgrading/).

### OAuth sign-in for MCP servers {#v26.31-mcp-oauth}
The `materialize-agent` and `materialize-developer` MCP servers now support OAuth (browser-based) sign-in, so MCP-compatible clients such as Claude Code, Claude Desktop, and Cursor can authenticate through your browser instead of a Base64-encoded token. With OAuth, the client connects as your own user role with your existing privileges.

For more information, see [MCP Server for Agents](/developer-tools/mcp-server/mcp-agent/) and [MCP Server for Developers](/developer-tools/mcp-server/mcp-developer/).

### Improvements {#v26.31-improvements}
- **Faster `count(*)` over `generate_series`**: Queries like `SELECT count(*) FROM generate_series(1, N)` now evaluate in constant time instead of materializing all rows.
- **System parameter override introspection**: Added `mz_internal.mz_overridden_system_parameters`, a catalog view that lists environment-wide system parameter overrides set via `ALTER SYSTEM`, readable by all users.
- **Kubernetes resource labels for Self-Managed**: Standard `app.kubernetes.io/*` labels are now applied to all Kubernetes resources (pods, services, statefulsets, deployments) managed by the operator.

### Bug Fixes {#v26.31-bug-fixes}
- Fixed `ALTER CONNECTION ... ROTATE KEYS` silently dropping concurrent `ALTER CONNECTION SET` changes when both commands ran at the same time.
- Fixed `COPY INTO` not respecting the target table's numeric precision, causing incorrect decimal values in downstream sinks.
- Fixed the optimizer panicking when a scalar subquery's body was provably empty, producing a count of zero.
- Fixed an overflow in array cardinality calculation when dimension lengths multiply to exceed the maximum integer value.
- Fixed multiple panics during proto/Row and persist state decoding when encountering malformed input, improving availability against corrupted data.
- Fixed Iceberg sinks accumulating the entire source snapshot in memory during hydration instead of flushing incrementally.
- Fixed the MCP `restrict_to_user_objects` guard being bypassed for deferred plans, allowing restricted MCP connections to access system catalog objects.
- Fixed Console password authentication breaking when the cached OIDC token expires, causing all subsequent requests to fail with "authentication credentials have expired."
- Fixed PostgreSQL source creation panicking when excluded columns include primary key columns.
- Fixed SQL parenthesization errors in `SHOW CREATE` output that could cause the generated SQL to fail to reparse.
- Fixed replicas doubling in memory during zero-downtime upgrades due to unbounded correction buffer growth in read-only materialized view sinks.

## v26.30.1
*Released to Materialize Cloud: 2026-06-25* <br>
*Released to Materialize Self-Managed: 2026-06-26* <br>

### PostgreSQL Physical Replica Support {#v26.30.1-postgresql-physical-replica-support}
Materialize now supports replicating from a physical PostgreSQL replica (hot standby), not just the primary server. This lets you offload replication load from the primary to a read replica. Connecting to a physical replica requires PostgreSQL 16 or later. If the replica is promoted to primary, the source fails and must be recreated, consistent with how Materialize handles a primary failover today.

For more information, see [CREATE SOURCE: PostgreSQL](/sql/create-source/postgres-v2/).

### MCP Developer Query Tool {#v26.30.1-mcp-developer-query-tool}
The MCP server for developers now includes a `query` tool for running `SELECT`, `SHOW`, and `EXPLAIN` queries against user objects and clusters, mirroring the agent endpoint's query capability.

### Advisory {#v26.30.1-advisory}

- **MySQL zero-value YEAR columns**: This release changes how the MySQL source decodes zero-value `YEAR` columns (`0000`). Previously, zero values were decoded inconsistently: as `0` during the initial snapshot and as `1900` (an invalid year) from the binlog. Both are now decoded as the 4-digit string `0000`, matching MySQL's own representation. Non-zero years (1901–2155) are unaffected.

  **Upgrade impact**: If you replicate a `YEAR` column that can hold zero values, rows ingested before the upgrade retain their old representation (`0` or `1900`) until the upstream row is modified and re-decoded. To make all rows consistent and avoid potential source errors, drop and recreate the affected source (or subsource/table) after upgrading. Sources without zero-value `YEAR` data require no action.

### Improvements {#v26.30.1-improvements}
- **mz-debug OIDC and SASL authentication**: The `mz-debug` diagnostic tool now supports OIDC and SASL authentication modes in addition to password authentication.
- **Faster LIKE pattern matching**: `LIKE` patterns with multiple `%` wildcards (e.g., `%a%a%a`) no longer exhibit super-linear matching time against long strings, while common patterns like `%substring%` remain on the fast string matcher.
- **Fivetran Destination restored**: The Fivetran Destination integration, which was removed in v26.29.0, has been restored.
- **Self-managed monitoring docs refreshed**: Self-managed deployments now have a published reference of the metrics Materialize exposes: [essential metrics](/observability/essential-metrics/) and an [appendix of all metrics](/observability/appendix-metrics/). The self-managed monitoring guides for [Prometheus and Grafana](/observability/self-managed/grafana/) and [Datadog](/observability/self-managed/datadog/) have been refreshed with updated scrape configurations and dashboards.

### Bug Fixes {#v26.30.1-bug-fixes}
- Fixed `IS [NOT] DISTINCT FROM` binding too loosely relative to `AND`/`OR`, causing `a IS DISTINCT FROM b AND c` to silently produce wrong results by parsing as `a IS DISTINCT FROM (b AND c)` instead of `(a IS DISTINCT FROM b) AND c`.
- Fixed the query optimizer incorrectly propagating errors through `AND`/`OR` expressions, causing queries like `false AND <error>` to produce an error instead of returning `false`.
- Fixed `GRANT ALL ON TABLE` and `REVOKE ALL ON TABLE` on views, materialized views, and sources only granting or revoking `SELECT` instead of the full table privilege set (`SELECT`, `INSERT`, `UPDATE`, `DELETE`).
- Fixed MySQL sources incorrectly decoding zero-value `YEAR` columns during both snapshot and replication.
- Fixed Avro-formatted sources failing to decode records after a nullable column's type was promoted to a wider numeric type (e.g., `int` to `double`).
- Fixed `array_fill` incorrectly rejecting arrays between 128 MB and 256 MB due to an operator precedence bug in the size limit calculation.
- Fixed `pg_catalog.pg_description` returning an error when any user object was named `pg_class`, `pg_type`, or `pg_namespace`.
- Fixed CSV source ingestion crashing or silently producing corrupted rows when encountering malformed input.
- Fixed `EXPLAIN ANALYZE` and `EXPLAIN ANALYZE CLUSTER` silently dropping every-other worker's results.
- Fixed a panic when a `GROUP BY` clause repeated a positional column reference, such as `GROUP BY 1, 1`.
- Fixed a panic when resizing a managed cluster that hosts a replica-targeted materialized view with a `COMMENT`.
- Fixed a panic when decoding binary-format `numeric` values with an out-of-range scale in the wire header.
- Fixed a panic when specifying out-of-range interval values in `WITH` options such as `INTROSPECTION INTERVAL` or `REFRESH EVERY`.
- Fixed a panic when casting `regtype`, `regclass`, or `mz_aclitem` to text in contexts that disallow subqueries, such as a `RETURNING` clause.
- Fixed a panic when setting a non-`MANUAL` schedule on a cluster with `REPLICATION FACTOR > 1`.
- Fixed a crash when using `COPY FROM` with a URL or S3 source without specifying a format, or with an unsupported format like `TEXT` or `BINARY`.
- Fixed table functions silently accepting unsupported `FILTER`, `OVER`, and `DISTINCT` clauses instead of returning an error.
- Fixed `COPY TO STDOUT` silently accepting unsupported `ESCAPE` and `HEADER` options instead of returning an error.
- Fixed `SHOW CREATE TABLE ... FROM SOURCE` emitting internal options that prevented the output from being replayed.
- Fixed `SHOW CREATE TABLE` failing to round-trip for SQL Server and load generator sources due to incorrect database references.
- Fixed multiple SQL parser and pretty-printer bugs that caused `SHOW CREATE` output to fail to reparse, including incorrect keyword quoting and operator precedence in displayed expressions.
- Fixed Avro source ingestion crashing when encountering malformed input such as invalid block lengths, unbounded recursion, or unmatched schema references.
- Fixed `COPY FROM STDIN` being able to exhaust the shared connection pool by holding blocking threads idle, which could stall all other queries in the environment.
- Fixed a panic when creating a Kafka sink with a non-positive `TOPIC METADATA REFRESH INTERVAL`.
- Fixed a panic when a Kafka topic refresh interval was set to less than 1 second.
- Fixed the MCP `read_data_product` tool failing when the `restrict_to_user_objects` option was enabled.

## v26.29.0
*Released to Materialize Cloud: 2026-06-18* <br>
*Released to Materialize Self-Managed: 2026-06-19* <br>

### Bounded Staleness Isolation Level {#v26.29-bounded-staleness-isolation-level}

> **Public Preview:** This feature is in public preview.

Bounded staleness is a new SQL isolation level that lets you set a freshness target for your queries. For example, you can configure a session to only serve data that is at most 10 seconds stale. If sufficiently fresh data is unavailable, the query immediately returns an error (`SQLSTATE 40001`) rather than blocking. This positions bounded staleness between [Serializable](/serve-results/isolation-level/#serializable) and [Strict Serializable](/serve-results/isolation-level/#strict-serializable): it never blocks on input frontiers, but errors immediately when the staleness bound cannot be met. Bounded staleness is read-only and can be set at the session or connection level.

```mzsql
-- Serve data no more than 10 seconds stale; error immediately if unavailable.
SET TRANSACTION_ISOLATION TO 'bounded staleness 10s';
```

For more information, see [Bounded Staleness](/serve-results/isolation-level/#bounded-staleness).

### mz-deploy (v0.1) {#v26.29-mz-deploy}

[mz-deploy](/developer-tools/mz-deploy/) is a new CLI for declarative Materialize deployments. You can use mz-deploy to define sources, views, indexes, clusters, and other Materialize objects as code—and so can your coding agents. Projects compile locally with no running Materialize instance required: run unit tests, inspect query plans, and validate changes entirely inside a sandbox before touching a shared environment. Built in Rust, mz-deploy cold-compiles a project with 40,000+ models in under 500ms, with most incremental changes compiling in under 10ms. Deployments only redeploy changed objects, support blue-green deployments, and allow concurrent deployments with conflict detection at promote time.

For instance, to create a new Materialize project called `order-monitoring`:

```bash
mz-deploy new order-monitoring
```

This scaffolds the following directory structure:

```nofmt
order-monitoring/
├── models/
│   └── materialize/
│       └── public/        # SQL files → materialize.public.<filename>
├── clusters/              # Cluster definitions
├── roles/                 # Role definitions
├── network-policies/      # Network policy definitions
├── project.toml           # Project configuration
├── README.md
└── .gitignore
```

For more information, see [mz-deploy](/developer-tools/mz-deploy/).

### Iceberg Sinks for Google Cloud Platform {#v26.29-google-cloud-support-for-iceberg-sinks}

Iceberg sinks can now deliver data into [GCP Lakehouse](https://docs.cloud.google.com/lakehouse/docs/introduction) managed Iceberg tables. A new `GCP` connection type handles Google service account credentials, enabling Materialize to authenticate with BigLake's Iceberg REST catalog.

```mzsql
-- Create a GCP service account connection
CREATE CONNECTION gcp_connection TO GCP (
  SERVICE ACCOUNT KEY = SECRET gcp_sa_key
);

-- Create an Iceberg catalog connection using BigLake
CREATE CONNECTION biglake_catalog TO ICEBERG CATALOG (
  CATALOG TYPE = 'rest',
  URL = 'https://biglake.googleapis.com/iceberg/v1/restcatalog',
  GCP CONNECTION = gcp_connection,
  WAREHOUSE = 'gs://my-gcs-bucket'
);

-- Create an Iceberg sink writing into a GCP Lakehouse managed Iceberg table
CREATE SINK my_gcp_iceberg_sink
  IN CLUSTER sink_cluster
  FROM my_materialized_view
  INTO ICEBERG CATALOG CONNECTION biglake_catalog (
    NAMESPACE = 'my_namespace',
    TABLE = 'my_table'
  )
  KEY (id)
  MODE UPSERT
  WITH (COMMIT INTERVAL = '60s');
```

For more information, see [Syntax: CREATE SINK... INTO ICEBERG](/sql/create-sink/iceberg).

### Improvements {#v26.29-improvements}
- **Correct SQLSTATEs for evaluation errors**: Evaluation errors such as division by zero, out-of-range casts, and invalid input now return their correct PostgreSQL-standard SQLSTATE codes instead of the generic `XX000` (internal error).
- **PostgreSQL-compatible binary encoding diagnostics**: When a type has no binary output function (e.g., `list`, `map`, `aclitem`), Materialize now returns PostgreSQL's `SQLSTATE 42883` with the message `no binary output function available for type <t>`.

### Bug Fixes {#v26.29-bug-fixes}

- Fixed a panic when a cluster is dropped concurrently with statement execution on that cluster.
- Fixed stack overflows on deeply nested query expressions by converting expression visitors to iterative traversals.
- Fixed a panic when using `COPY ... TO STDOUT WITH (FORMAT binary)` on types without binary encoding support, including `list`, `map`, `aclitem`, and records or arrays containing these types.
- Fixed a panic when specifying `TEXT COLUMNS` with an empty list.
- Fixed a panic when specifying `EXCLUDE COLUMNS` with an empty list.
- Fixed `oidc_group_claim` and `oidc_group_role_sync_strict` being incorrectly modifiable by environment superusers via `ALTER SYSTEM SET`; these parameters now correctly require `mz_system` access.
- Fixed a stack overflow when using Avro schemas with recursive references in maps.
- Fixed data corruption in MySQL sources when a table is dropped and immediately recreated with the same name and a compatible schema.
- Fixed HTTP health probes (`/api/livez`, `/api/readyz`) and the metrics endpoint failing when the coordinator is unhealthy in deployments with OIDC authentication.
- Fixed a crash caused by duplicate statement execution logging that could bring down the entire environment.
- Fixed array values failing to write to Iceberg sinks due to the array dimension being stored as a narrower integer type than Iceberg requires.

## v26.28.0
*Released to Materialize Cloud: 2026-06-11* <br>
*Released to Materialize Self-Managed: 2026-06-12* <br>

### Improvements {#v26.28-improvements}

- **Improved performance using temporal filters**: We've made a second round of improvements to temporal filter performance. Steady state CPU usage while using temporal filters is significantly reduced; we saw a drop from 75% CPU to 4% CPU in internal tests.
- **Multi-item `DROP` with dependencies**: `DROP` statements now succeed
  when multiple co-dependent items are named in the same command,
  matching PostgreSQL behavior.
- **Self-Managed OIDC configuration**: Environment superusers can now
  configure `oidc_group_claim` and `oidc_group_role_sync_strict` via
  `ALTER SYSTEM SET` without requiring `mz_system` access.
- **OIDC group claim nested paths**: OIDC group claims now support
  dot-separated paths (e.g., `groups.materialize`) for navigating
  nested JWT structures.
- **Self-Managed Console connection info**: The Console in self-managed
  deployments now displays the actual balancerd hostname in the OIDC
  and MCP connection dialogs.
- **Password redaction in system catalog**: `pg_catalog.pg_user.passwd`
  now returns `'********'` instead of the actual password hash,
  matching PostgreSQL behavior.

### Bug Fixes {#v26.28-bug-fixes}

- Fixed Kafka sources appearing healthy after a low-watermark data-loss
  error by preventing automatic restarts that masked the stalled state.
- Fixed Kafka sources becoming unhealthy and producing stale data due to
  transient connection failures when fetching low watermarks.
- Fixed Kafka sinks using upsert envelope becoming permanently stale
  when a concurrent writer advanced the output shard.
- Fixed `generate_subscripts` returning incorrect results for arrays
  with custom lower bounds.
- Fixed `array_lower` and `array_upper` returning incorrect results for
  arrays with custom lower bounds.
- Fixed `SUM(float8)` returning incorrect results when summing large
  finite values.
- Fixed `date_bin` returning incorrect results for timestamps exactly on
  a bin boundary before the origin.
- Fixed `INSERT INTO ... SELECT` queries being incorrectly classified as
  constant, potentially producing wrong results.
- Fixed `SHOW CREATE SINK` including an internal version number that
  prevented the output from being used to recreate the sink.
- Fixed MCP `read_data_product` failing when the role lacks `USAGE`
  privilege on the data product's cluster; the tool now falls back to
  the default cluster instead.
- Fixed a panic when setting `statement_timeout` or similar duration
  parameters with Unicode numeric characters.
- Fixed a panic when calling `pg_cancel_backend(NULL)`; now returns
  `NULL` to match PostgreSQL behavior.
- Fixed a crash when using `SUBSCRIBE` with duplicate columns in the
  key; now returns a clear error.
- Fixed a crash when using `CREATE TABLE ... FROM SOURCE` with only
  constraints and no explicit columns.
- Fixed a panic when setting `default_timestamp_interval` to `0`; now
  returns an error.
- Fixed cluster size options appearing in incorrect order in the Console.

## v26.27.0
*Released to Materialize Cloud: 2026-06-04* <br>
*Released to Materialize Self-Managed: 2026-06-05* <br>

This release includes improvements to the MCP Server for Agents, general
improvements, and bug fixes.

### MCP Server for Agents
We've made several improvements to our MCP Server for Agents, which can be used to give agents in production fresh context from Materialize.

- **`query` tool enabled by default**: The MCP Server for Agents now
  enables the [`query` tool](/developer-tools/mcp-server/mcp-agent-tools/#query)
  by default, allowing agents to join across data products.
- **Data product routing**: The `read_data_product` tool now
  automatically routes queries to the data product's catalog cluster,
  eliminating the need to specify the cluster manually.
- **Data product hydration status**: The MCP Server for Agents now
  surfaces hydration readiness state for data products, enabling agents
  to check whether a data product is fully hydrated before querying.

For more information, refer to:
- [MCP Server for Agents](/developer-tools/mcp-server/mcp-agent/)

### Improvements {#v26.27-improvements}

- **Improved `EXPLAIN` output**: Default `EXPLAIN` output now uses
  cleaner formatting for joins and explicitly identifies cross joins.

### Bug Fixes {#v26.27-bug-fixes}

- Fixed the Console in self-managed deployments not displaying the
  balancerd hostname in the connection dialog.
- Fixed incorrect query results from filter pushdown when using
  timestamp or date arithmetic with interval values.
- Fixed incorrect query results from filter pushdown when using `CASE`
  expressions over JSON columns with keys present in only one branch.
- Fixed `LATERAL` subqueries with table functions returning wrong
  results when the input table has an index on a non-leading column.
- Fixed `COPY FROM` CSV decoding silently treating quoted `NULL` markers
  as SQL `NULL` and dropping rows after a quoted end-of-copy marker.
- Fixed a panic when applying a timezone offset to a near-maximum
  timestamp value.
- Fixed a panic when applying a timezone offset to a leap-second
  timestamp value.
- Fixed a panic when a replica targeted by `CREATE MATERIALIZED VIEW ...
  IN CLUSTER ... REPLICA <name>` was concurrently dropped.
- Fixed a panic when specifying a `REFRESH` interval shorter than
  1 millisecond; now returns a clear error instead.
- Fixed SSH tunnel connections to HTTPS schema registries failing with
  TLS handshake errors when the URL omitted the default port.
- Fixed Iceberg sink errors when writing tables with `smallint` columns,
  map-typed columns, or `range`-typed equality delete keys.
- Fixed `SHOW CREATE` incorrectly displaying passwords and `AS OF`
  clauses.

## v26.26.0
*Released to Materialize Cloud: 2026-05-28* <br>
*Released to Materialize Self-Managed: 2026-05-29* <br>

This release includes Single Sign-On (SSO) for Self-Managed, a new Objects page
in the Console, performance improvements, and bug fixes.

### Single Sign-On (SSO) for Self-Managed

> **Public Preview:** This feature is in public preview.

Self-managed deployments can now configure single sign-on via any OIDC-compliant identity provider (Okta, Microsoft Entra ID, Auth0, Keycloak). Users authenticate via their IdP and receive a JWT token that Materialize validates; new users are auto-provisioned as database roles on first login, and existing users with matching emails map automatically to their current accounts. Enabling SSO is backward compatible: password-based auth continues to work for applications and service accounts.

For more information, refer to:
- [Single sign-on (SSO)](https://materialize.com/docs/security/self-managed/sso/)

### Objects page

The Console includes a new Objects page, which provides a unified view of all
sources, materialized views, indexes and sinks. You can track real-time freshness
metrics, hydration status, and cluster assignments. If an object is stale, you can diagnose why.
If lag is inherited from upstream, you can visualize the critical path. And if an object itself
is the cause of lag, you can diagnose the root cause.

### Improvements {#v26.26-improvements}

- **More performant temporal filters**: We've significantly improved the performance of
  temporal filters. While specific results will vary by workload, in our tests we saw CPU utilization drop from 75% to
  4% on workloads dominated by temporal filter evaluation.
- **Faster DDL at scale**: DDL operations (`CREATE TABLE`, `DROP TABLE`,
  etc.) are now up to 65% faster in environments with many objects by
  eliminating a per-table loop that previously ran on every group commit.
- **Faster storage usage collection**: Periodic storage usage collection is
  now up to 17x faster at 10,000 shards, reducing coordinator stalls from
  ~500ms to ~30ms per cycle.
- **`dbt-materialize`: `PARTITION BY` support**: Added a `partition_by`
  config option for materialized views, generating the `PARTITION BY (...)`
  clause in `CREATE MATERIALIZED VIEW`.
- **`dbt-materialize`: Unmanaged cluster support for blue/green
  deployments**: The `deploy_init` macro now supports unmanaged clusters by
  cloning each replica's size and availability zone, enabling blue/green
  deployments for environments not using managed clusters.

### Bug Fixes {#v26.26-bug-fixes}

- Fixed wrong results for `JOIN ... USING (col) AS t` with `RIGHT` or
  `FULL` joins.
- Fixed `round()` producing `-0` for negative fractional values that round
  to zero, causing mismatches in `DISTINCT`, `UNION`, and `GROUP BY`.
- Fixed `list_length_max` returning incorrect results for list-of-lists with
  `NULL` siblings before non-`NULL` sublists.
- Fixed incorrect query results when casting `text` to `"char"` or `bytea`
  in index lookups and equality filters.
- Fixed incorrect query results when casting `text` to `name` or
  `varchar(n)` in contexts that rely on uniqueness, such as `DISTINCT` or
  joins.
- Fixed MySQL sources failing to decode `TIMESTAMP` and `DATETIME` columns
  when using `TEXT COLUMNS`.
- Fixed `COPY FROM ... (FORMAT PARQUET)` producing range values that did not
  compare equal to logically-identical values constructed in SQL.
- Fixed missing audit log entries for `ALTER TABLE ADD COLUMN` and
  `ALTER SOURCE ... SET (TIMESTAMP INTERVAL)`.
- Fixed the Console Data Explorer page intermittently failing to load due to
  a WebSocket connection race condition.

## v26.25.0
*Released to Materialize Cloud: 2026-05-21* <br>
*Released to Materialize Self-Managed: 2026-05-22* <br>

This release includes source versioning for MySQL sources, improvements, and
bug fixes.

### MySQL: Source versioning

> **Public Preview:** This feature is in public preview.

For MySQL sources, we've introduced new syntax for [`CREATE
SOURCE`](/sql/create-source/mysql-v2/) and [`CREATE
TABLE`](/sql/create-table/). This allows you to better handle schema changes
in your source MySQL tables.

> **Note:** - Changing column types is currently unsupported.

For more information, refer to:
- [Guide: Handling upstream MySQL schema changes with zero
  downtime](/ingest-data/mysql/source-versioning/)
- [Syntax: `CREATE SOURCE`](/sql/create-source/mysql-v2/)
- [Syntax: `CREATE TABLE`](/sql/create-table/)

### Improvements {#v26.25-improvements}

- **Source versioning in public preview**: Source versioning helps you handle
  upstream schema changes without downtime in Materialize. With v26.25, source
  versioning has graduated from private preview to public preview, and is now
  available by default across all environments. For more information, refer to
  the source versioning guides:
    - [PostgreSQL](/ingest-data/postgres/source-versioning/)
    - [MySQL](/ingest-data/mysql/source-versioning/)
    - [SQL Server](/ingest-data/sql-server/source-versioning/)

### Bug Fixes {#v26.25-bug-fixes}

- Fixed dependents of replica-targeted materialized views being left in an
  inconsistent state when the target replica is dropped, causing subsequent
  queries against those dependents to fail.
- Fixed `ALTER CLUSTER ... SET (SIZE, WORKLOAD CLASS) WITH (WAIT FOR ...)`
  silently dropping the workload class change during zero-downtime
  reconfiguration.
- Fixed `CREATE TABLE FROM SOURCE` retaining the old source name in the stored
  definition after the source is renamed.
- Fixed `ALTER CONNECTION IF EXISTS` notice reporting the wrong object type.
- Fixed ambiguous column names being silently accepted in sink `KEY` clauses
  instead of returning an error.
- Fixed a panic during query optimization when `EXPECTED GROUP SIZE` is set
  to `0`.
- Fixed real-time recency timeout and dropped-object errors returning generic
  error messages instead of the correct SQL error codes and descriptions.
- Fixed Kafka sources hanging indefinitely when the start offset no longer
  exists due to topic retention or compaction.
- Fixed `EXPLAIN` plans omitting join projections, making some join closures
  appear as identity when they were not.
- Fixed Self-Managed replica scheduling when `availability_zones` is set,
  where `minDomains` could leave additional replicas stuck in a pending state.

## v26.24.3
*Released to Materialize Self-Managed: 2026-05-20* <br>

This patch release fixes a MySQL source ingestion bug.

### Bug Fixes {#v26.24.3-bug-fixes}

- Fixed MySQL sources failing to decode `TIMESTAMP` and `DATETIME` columns
  ingested via `TEXT COLUMNS`. Zero-value timestamps (`0000-00-00 00:00:00`)
  continue to require `TEXT COLUMNS` plus a `CAST` in user queries.

## v26.24.2
*Released to Materialize Self-Managed: 2026-05-18* <br>

This patch release extends the v26.24.0 catalog migration repair to cover
additional edge cases.

### Bug Fixes {#v26.24.2-bug-fixes}

- Extended the v26.24.0 catalog migration repair to also clear residual
  negative multiplicities and normalize Role rows still stored in the
  pre-v81 byte form.

## v26.24.1
*Released to Materialize Cloud: 2026-05-14 on as-needs basis* <br>

This patch release adds configurable Kafka sink message and batch size limits.

### Improvements {#v26.24.1-improvements}
Configurable Kafka sink size limits: The maximum size of individual Kafka sink messages and message batches can now be configured beyond their previous defaults.

## v26.24.0
*Released to Materialize Cloud: 2026-05-14* <br>

This release introduces the built-in MCP server for agents, improvements, and
bug fixes.

### MCP Server for Agents

> **Public Preview:** This feature is in public preview.

Give your agents fresh context using Materialize. Materialize environments now
include a built-in Model Context Protocol (MCP) [server for agents
(`/api/mcp/agent`)](/developer-tools/mcp-server/mcp-agent/). Once connected, an
agent can discover your data products, understand the underlying data ontology,
and run queries to fetch fresh data.

Agents can discover [materialized views](/sql/create-materialized-view/) or [indexed](/sql/create-index/) views. You can use [comments](/sql/comment-on/) to document the data products, and describe them to agents. Agents authenticate as [roles](/sql/create-role/) in Materialize, so [RBAC privileges](/manage/access-control/) govern which data products are visible. Finally, you can set up a dedicated [cluster](/fundamentals/concepts/clusters/) for your agents, so they're isolated from the rest of your environment.

The MCP server for agents complements the [MCP server for
developers](/developer-tools/mcp-server/mcp-developer/) released in v26.20.2. The
developer server gives coding agents (like Claude Code) access to Materialize's
observability so you can build on Materialize faster; the agent server gives
production agents fresh, governed context from your data products.

For more information, refer to:
- [Integrations: MCP Server for Agents](/developer-tools/mcp-server/mcp-agent/)

### Improvements {#v26.24-improvements}

- **`dbt-materialize` connection overrides**: The dbt adapter now supports
  passing custom connection options via the `options` field in `profiles.yml`,
  enabling OIDC authentication and other advanced connection configurations.
- **`COPY FROM` rejects HTTP redirects**: `COPY FROM` now returns a clear error
  if the target URL responds with an HTTP redirect, preventing unexpected data
  sources and potential security issues.
- **[Agent skills](/developer-tools/mcp-server/coding-agent-skills/) — improved `mcp-developer-analysis` client setup**: The skill now includes a comprehensive playbook for connecting MCP-capable clients (Claude Code, Cursor, VS Code, Zed, Continue, Windsurf, Claude Desktop) to the [MCP server for developers](/developer-tools/mcp-server/mcp-developer/).

### Bug Fixes {#v26.24-bug-fixes}

- Fixed MySQL sources with RDS IAM authentication failing when the database
  username contains special characters like `&` or `#`.
- Fixed joins incorrectly failing with a type mismatch error when join columns
  differed only in nullability.
- Fixed fast-path `SELECT` queries returning incorrect results when `OFFSET`
  was specified.
- Fixed `string_to_array` returning incorrect results when `null_string` is
  specified and the delimiter is empty.
- Fixed `INSERT INTO ... SELECT` silently ignoring the `OFFSET` clause in the
  source query.
- Fixed `seahash` function catalog metadata reporting the wrong return type
  (`uint4` instead of `uint8`).
- Fixed `mz_egress_ips` storing non-canonical CIDR notation (e.g.,
  `10.0.5.7/24` instead of `10.0.5.0/24`).
- Fixed Console crashing on OIDC-protected routes when the identity provider
  initialization fails, instead of falling through to password-based sign-in.
- Fixed catalog migration bug from v26.18.0 by which a
  `Non-positive multiplicity in DistinctBy` error could occur on queries
  containing `SELECT DISTINCT` over role-derived catalog views (e.g.,
  anything reading from `mz_roles`, `mz_role_members`, or views that
  internally project role columns). The error is resolved automatically by
  upgrading to v26.24.2 or newer.

## v26.23.2
*Released to Materialize Cloud: 2026-05-11* <br>

This patch release includes bug fixes.

### Bug Fixes {#v26.23.2-bug-fixes}

- Fixed a regression in v26.23.0 that caused storage replicas to spend a large
  share of their CPU time walking small data fragments during Parquet decode,
  slowing queries that read from object storage.
- Fixed a regression in v26.23.0 that caused storage replicas to retain extra
  memory when reading from object storage.

## v26.23.0
*Released to Materialize Cloud: 2026-05-07* <br>

This release introduces enhanced Kafka PrivateLink routing options, security
improvements, and bug fixes.

### Features {#v26.23-features}

- **Dynamic Kafka brokers with AWS PrivateLink**: Kafka connections can now
  route dynamically discovered brokers through a PrivateLink tunnel, rather than
  requiring every advertised broker to be enumerated in the `BROKERS (...)`
  clause. Two new options are available:
  - `MATCHING 'pattern' USING AWS PRIVATELINK conn (...)` inside `BROKERS (...)`
    associates a PrivateLink connection with any broker whose advertised
    hostname matches `pattern`, including brokers that only appear in Kafka
    metadata after the connection is established.
  - `BOOTSTRAP BROKER 'addr' USING AWS PRIVATELINK conn (...)` pins the initial
    bootstrap address to an explicit PrivateLink tunnel.

  Together, these resolve availability-zone mismatches that previously affected
  MSK and other Kafka clusters that rely on broker discovery, by ensuring every
  broker, including those learned from metadata, is reached through a
  PrivateLink endpoint in the broker's own AZ. Refer to our documentation on
  [AWS PrivateLink connections](/ingest-data/network-security/privatelink/) and
  the [Kafka `CREATE CONNECTION` PrivateLink syntax](/sql/create-connection/#kafka-privatelink-syntax)
  for more information.

### Improvements {#v26.23-improvements}

- **New `repeat_row_non_negative` SQL function**: The new
  `repeat_row_non_negative` table function generates a specified number of rows
  but errors on negative input rather than silently producing incorrect results,
  making it safer to use in general-purpose queries than the existing
  `repeat_row`.
- **Queries fail gracefully on internal errors**: Certain internal errors that
  previously caused `environmentd` to crash now return a query error instead,
  improving cluster stability.
- **dbt deploy retries on concurrent DDL conflicts**: `dbt deploy` now
  automatically retries the `ALTER SWAP` atomic deployment when it encounters a
  DDL interrupt from concurrent catalog operations, preventing spurious
  deployment failures in busy environments.
- **Clearer temporal filter error messages**: Error messages for unsupported
  temporal predicates now include the actual filter expression, making it easier
  to identify and fix the offending query.
- **`COPY TO S3` Parquet type validation at planning time**: `COPY TO S3` with
  `FORMAT PARQUET` now rejects Parquet-incompatible column types (such as
  `interval`) at query planning time with a clear error, rather than failing at
  execution time with an opaque message.
- **`mcp-developer-analysis`**: A new
  [coding agent skill](/developer-tools/mcp-server/coding-agent-skills/) that pairs with the
  `/api/mcp/developer` endpoint to provide diagnostic workflows, system catalog
  references, and remediation runbooks for AI-powered troubleshooting.
- **System catalog ontology for the MCP developer server**: The system
  catalog now exposes an ontology that describes how `mz_*` tables relate to
  one another and which tables to consult for common diagnostic questions. The
  [MCP server for developers](/developer-tools/mcp-server/mcp-developer/) uses
  this ontology to plan catalog queries directly instead of probing the schema,
  reducing the number of round trips needed to answer questions about
  hydration, freshness, and resource usage.
- **~10% faster materialized view hydration**: We've reduced the work performed
  during initial materialized view hydration, observing approximately 10%
  faster hydration times across our benchmarks. This shortens the window
  between creating (or restarting) a materialized view and the point at which
  it begins serving up-to-date results.

### Bug Fixes {#v26.23-bug-fixes}

- Fixed `statement_timeout = 0` (which means "disabled" in PostgreSQL semantics)
  causing every `SELECT` and `EXPLAIN FILTER PUSHDOWN` to fail immediately with a
  spurious `StatementTimeout` error.
- Tightened default validation on headers in Self-Managed deployments.
- Enhanced session-based HTTP authentication.
- Fixed `SHOW CREATE TYPE` emitting the bare type name instead of the
  fully-qualified `database.schema.type` name, unlike every other `SHOW CREATE`
  variant.
- Fixed Self-Managed `orchestratord` `--enable-rbac False` silently inverting
  the value and enabling RBAC instead of disabling it.
- Fixed SQL Server source composite primary key columns being recorded in
  non-deterministic order, causing incorrect constraint definitions and
  non-deterministic behavior across `ALTER SOURCE` and re-purification.
- Fixed PostgreSQL source RLS policy validation producing false positives that
  blocked replication for users whose roles inherit BYPASSRLS through role
  membership.
- Fixed SQL Server source growing memory without bound during table snapshots due
  to a `RowArena` that was never cleared between rows.
- Fixed `SELECT` queries with both `LIMIT` and `OFFSET` processing all remaining
  rows instead of stopping after the limit was reached.
- Fixed SQL Server source opening one upstream connection per Timely worker
  instead of one total, multiplying SQL Server connections and
  `sp_cdc_cleanup_change_table` calls by the worker count.
- Fixed SQL Server source with PrivateLink connections only attempting the first
  resolved IP address instead of trying all available addresses.
- Fixed `regexp_replace` returning an invalid regular expression error instead of
  `NULL` when called with a `NULL` replacement column and a literal pattern that
  fails to compile.
- Fixed `pg_index.indnatts` counting columns of the indexed table instead of the
  index itself, and `pg_class.relnatts` always reporting `0` for index rows,
  improving compatibility with tools that introspect the PostgreSQL catalog.
- Fixed toggling `memory_limiter_interval` from `0s` to a non-zero value at
  runtime potentially triggering an immediate replica kill even when memory usage
  was well below the limit.
- Fixed Self-Managed Kubernetes deployments where setting both
  `cluster_topology_spread_soft = on` and `cluster_topology_spread_min_domains`
  caused all replica pod creation to fail with an admission error.

## v26.22.0
*Released to Materialize Cloud: 2026-04-30* <br>
*Released to Materialize Self-Managed: 2026-05-01* <br>

This release includes various improvements, including faster sink performance
with up to 50% lower memory usage, and bug fixes.

### Improvements {#v26.22-improvements}

#### Sink improvements {#v26.22-improvements-sink}

- **Faster sink performance with up to 50% lower memory usage**: Sink operations
  now process data more efficiently by walking arrangements directly via
  cursors, reducing memory overhead and improving throughput. For large sinks,
  we have seen memory usage reduced by up to 50%.
- **Iceberg sink support for interval and range types**: Iceberg sinks now
  support `interval` and `range` data types, expanding compatibility with
  complex data schemas.

#### MCP security improvements {#v26.22-improvements-mcp-security}

- **Enhanced MCP server security**: MCP server origin validation now uses CORS
  allowlists instead of self-comparison checks, preventing DNS rebinding
  attacks.
- **Stricter MCP search path security**: MCP developer endpoint now sets a tight
  `search_path` to prevent bypass attacks.

#### General improvements {#v26.22-improvements-general}

- Catalog synchronization now uses more efficient consolidation algorithms,
  reducing overhead for environments with many objects.

- Improved query optimization by pushing `COALESCE` operations into `CASE WHEN`
  expressions where beneficial.

### Bug Fixes {#v26.22-bug-fixes}

- Fixed Iceberg upsert sinks dropping delete operations when handling more than
  100,000 distinct keys.
- Fixed `EXPLAIN OPTIMIZED PLAN` failure after renaming materialized views,
  indexes, or continual tasks.
- Fixed Parquet map key handling to properly deduplicate keys and use the final
  value when duplicates exist.
- Fixed subquery handling to properly account for negative diffs in accumulation
  logic.
- Fixed PostgreSQL source compatibility by using only `pg_catalog.server_version_num` for version detection.
- Fixed PostgreSQL `format_type` output to properly quote the `"char"` type (OID
  18).
- Fixed an issue in the Console where the cursor would not appear in the SQL
  editor.
- Fixed incorrect results from `mz_dataflow_global_ids` view when multiple
  objects shared the same dataflow.
- Fixed interval conversion overflow in Arrow utilities when converting
  microseconds to nanoseconds.
- Fixed OpenTelemetry rate limiting filter that was incorrectly suppressing all
  events instead of just rate-limited ones.
- Fixed catalog leak when dropping replacement collections without applying
  them.
- Enhanced security by ensuring sensitive authentication data is properly
  cleared from memory after use.
- Enhanced security by ensuring TLS certificate data is properly zeroized when
  dropped.
- Improved SQL name escaping in catalog operations for better reliability.
- Removed unused `memory_request` field from replica allocation configuration.
- Added regression test for Kafka sink handling of negative accumulations.

## v26.20.2
*Released to Materialize Cloud: 2026-04-16* <br>
*Released to Materialize Self-Managed: 2026-04-17* <br>

This release introduces the built-in Developer MCP server, Console
improvements, and bug fixes.

### MCP Server for Developers

> **Public Preview:** This feature is in public preview.

Materialize environments now include a built-in Model Context Protocol (MCP)
[Developer endpoint
(`/api/mcp/developer`)](/developer-tools/mcp-server/mcp-developer/). Connecting an
MCP-compatible coding agent (such as Claude Code, Claude Desktop, or Cursor) to
this endpoint lets you ask natural language questions about your environment.

For example, you could ask *why is my materialized view stale?* or *how much memory is my cluster using?*. You'll receive a diagnosis and recommendations on how to fix isssues.

For more information, refer to:
- [Integrations: MCP Server for
  Developers](/developer-tools/mcp-server/mcp-developer/)

### Improvements {#v26-20-improvements}
- **Better Console schema navigation**: The schema dropdown in the SQL Shell now
  prioritizes schemas from the current database, making it easier to find
  relevant schemas.

### Bug Fixes {#v26-20-bug-fixes}
- Fixed Console RBAC users tab that was displaying incorrectly for cloud users
  due to null `rolcanlogin` values.
- Fixed builtin dependency ordering issue that could cause system catalog
  inconsistencies.

## v26.19.0
*Released to Materialize Cloud: 2026-04-09* <br>
*Released to Materialize Self-Managed: 2026-04-10* <br>

This release introduces append mode for [Iceberg sinks](/sql/create-sink/iceberg/),
and bug fixes.

### Iceberg sink append mode

When an [Iceberg sink](/sql/create-sink/iceberg/) is created in append
mode, all changes are written as data rows — no Iceberg delete files are
produced. This is especially useful if you're sinking data from a materialized
view with temporal filters, and you don't want data to be deleted from your Iceberg table as it ages out.

```mzsql
CREATE SINK events_log_iceberg
  IN CLUSTER analytics_cluster
  FROM user_events
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = 'events',
    TABLE = 'user_events_log'
  )
  USING AWS CONNECTION aws_connection
  MODE APPEND
  WITH (COMMIT INTERVAL = '5m');
```

For more information, refer to:
- [Guide: Apache Iceberg sink](/export-data/iceberg/)
- [Reference: `CREATE SINK ICEBERG`](/sql/create-sink/iceberg/)

### Bug Fixes {#v26.19-bug-fixes}

- Fixed identifier display in system catalog tables `mz_kafka_source_tables`,
  `mz_mysql_source_tables`, and `mz_postgres_source_tables` to show raw values
  without SQL quoting (e.g., `my-kafka-topic` instead of `"my-kafka-topic"`).

## v26.18.0
*Released to Materialize Cloud: 2026-04-02* <br>
*Released to Materialize Self-Managed: 2026-04-03* <br>

This release includes various improvements and bug fixes.

### Improvements {#v26.18-improvements}

- **Improved Console reconnect behavior**. The Console shell now reconnects
  more reliably, with toast notifications that no longer stack.

- **Expanded `COPY FROM` data type support**. [`COPY FROM` parquet
  files](/sql/copy-from/#parquet-formatting) now supports `map` and `interval`
  data types.

- **Improved query performance on wide tables**. Queries on tables with many
  columns now execute faster.

### Bug Fixes {#v26.18-bug-fixes}

- Fixed SSL certificate loading to properly handle all certificates in PEM
  bundles instead of only the first one.
- Fixed materialized view sinks getting stuck when instantiated with output
  shards whose initial frontier is less than the dataflow as-of.
- Fixed panic when dropping computed tables with active `SUBSCRIBE` operations.
- Fixed `EXPLAIN ANALYZE` not working correctly due to quoting issues in
  `mz_mappable_objects`.

## v26.17.1
*Released to Materialize Self-Managed: 2026-03-27* <br>

This release includes a bug fix.

### Bug Fixes {#v26.17.1-bug-fixes}

- Fixed Iceberg sinks failing to write unsigned integer types (UInt8,
  UInt16, UInt32, UInt64) by mapping them to Iceberg-compatible signed
  types.

## v26.17.0
*Released to Materialize Cloud: 2026-03-26* <br>
*Released to Materialize Self-Managed: 2026-03-27* <br>

This release includes performance improvements and bug fixes.

### Improvements {#v26.17-improvements}

- **10% improved transactional DDL performance**: We've eliminated an O(n^2) operation. DDL transactions (such as creating multiple tables from a source in a single transaction) now execute faster.
- **Reduced catalog server load during blue/green deploys**: The dbt-materialize adapter now uses a single batched query instead of
  per-cluster sequential polling. This is especially useful when creating a large number of objects.

### Bug Fixes {#v26.17-bug-fixes}

- Fixed a correctness bug where LEFT JOIN, RIGHT JOIN, and FULL JOIN with an
  empty relation produced incorrect results (empty instead of NULLs) due to
  join identity elision.
- Fixed Kafka sinks incorrectly writing negative Avro timestamps (pre-epoch
  dates) by treating the timestamp microseconds as unsigned instead of signed.
- Fixed Avro fixed-decimal encoding not left-padding unscaled bytes to the
  schema's fixed size, which could cause `UnexpectedEof` errors or data
  corruption in downstream consumers.
- Fixed a race condition in persist where a batch could be selected before
  obtaining a lease, potentially causing unexpected read-time halts.
- Fixed PROXY protocol v2 header parsing failing when headers arrived across
  multiple TCP segments, which could corrupt subsequent HTTP parsing between
  balancerd and environmentd.
- Fixed the Fivetran destination connector logging `app_password` in plaintext
  in connection logs.
- Fixed queries with expensive functions in subqueries (e.g., `UNION ALL`,
  `EXISTS`, scalar subqueries) being incorrectly routed to `mz_catalog_server`
  instead of the user's cluster.
- Fixed webhook secret cache not invalidating when secrets are changed,
  requiring a restart to pick up new secret values.
- Fixed orchestratord image reference parsing treating registry ports (e.g.,
  `gcr.io:443/...`) and digest separators (`@sha256:...`) as image tags,
  producing invalid references for Self-Managed deployments.
- Fixed optimizer feature flags being auto-enabled during item parsing, which
  rendered plan caching ineffective.
- Fixed `mz_catalog_raw` not being consistently readable under strict
  serializable isolation by keeping the catalog shard's frontier up-to-date
  with the oracle read timestamp.
- Fixed a security vulnerability in the `lz4_flex` dependency
  (RUSTSEC-2026-0041).
- Fixed a bad assertion in oneshot source storage worker reconciliation that
  could cause panics.
- Fixed hydration check errors during 0dt upgrades for replica-targeted
  collections, where non-target replicas would report `CollectionMissing`
  errors.
- Fixed SQL Server source `Transaction::drop` not sending ROLLBACK, leaving
  the SQL Server session in an open transaction after drop.
- Fixed a panic in authentication when receiving a proof of unexpected length.
- Fixed an issue causing console session variables to be lost after a reconnect.

## v26.16.0
*Released to Materialize Cloud: 2026-03-19* <br>
*Released to Materialize Self-Managed: 2026-03-20* <br>

This release adds support for copying Parquet files from object storage, performance improvements, and bug fixes.

### `COPY FROM` Parquet files in object storage

`COPY FROM` now supports bulk importing data from Parquet files stored in Amazon
S3 and any S3-compatible object storage service, such as Google Cloud Storage,
Cloudflare R2, or MinIO. You can import Parquet files using an AWS connection or
a presigned URL.

```mzsql
COPY INTO my_table
FROM 's3://my_bucket/my_data.parquet'
(FORMAT PARQUET, AWS CONNECTION = my_aws_conn);
```

For more information, refer to:
- [Syntax: COPY FROM](/sql/copy-from/)
- [Syntax: CREATE CONNECTION (S3-compatible)](/sql/create-connection/#s3-compatible-object-storage)

### Improvements {#v26.16-improvements}

- **Improved [`AS OF`](/sql/subscribe/#as-of) error messages**: Error messages
  for `AS OF` queries now use user-facing terminology (e.g., "Indexed
  input", "Storage inputs") instead of internal names.
- **Streamed [WebSocket](/serve-results/websocket-api/) query results**:
  WebSocket query results are now streamed directly instead of buffered,
  reducing memory usage for large result sets.

### Bug Fixes {#v26.16-bug-fixes}

- Fixed an RBAC security bypass that allowed a non-superuser with
  `CREATEROLE` privilege to strip superuser status from any role via
  `ALTER ROLE ... NOSUPERUSER`.
- Fixed indexes on older versions of altered tables or replaced
  materialized views being lost during environment bootstrap, which
  could cause panics.
- Fixed pgwire encoding errors leaving partial messages in the connection
  buffer, which caused clients to see "lost synchronization" errors
  instead of proper error messages.
- Fixed unbounded queue growth in storage since-downgrade processing that
  could lead to out-of-memory conditions in environments with many
  storage collections.
- Fixed a correctness bug when parsing large Avro fixed-size decimals
  from Kafka sources, where values were returned as raw bytes instead of
  decoded decimal numbers.
- Fixed subqueries being incorrectly allowed in the `SET` clause of
  `UPDATE` statements.
- Fixed `COPY FROM S3` requiring manual column specification for tables
  with `NOT NULL` columns by removing a redundant non-null check during
  planning.
- Fixed a correctness issue with `COPY FROM STDIN` when using headers.
- Fixed column name deduplication bug in `COPY TO` / Parquet writer that
  could produce duplicate column names.
- Fixed `RETAIN HISTORY` value being ignored for webhook tables.
- Fixed `DROP OWNED BY` and `REASSIGN OWNED BY` not including network
  policies, which could block `DROP ROLE` for roles that own network
  policies.
- Fixed false positive wallclock lag reporting (showing ~56 years of lag)
  during replica startup for compute introspection indexes.

## v26.15.0
*Released to Materialize Cloud: 2026-03-12* <br>
*Released to Materialize Self-Managed: 2026-03-13* <br>

This release includes various improvements and bug fixes.

### Improvements {#v26.15-improvements}

- **Improved memory efficiency for joins on `varchar` and `text` columns**:
  Previously, joining on these columns required creating a new arrangement,
  effectively doubling memory usage. Materialize can now reuse existing
  arrangements on these columns. We've seen memory improvements by as much as 25%
  in some cases involving `varchar` indexes.
- Added support for setting `cpu_request` independently of `cpu_limit`
  in cluster replica sizes for Self-Managed deployments.
- Renamed the **Org ID** label to **Environment ID** in the Console Shell
  to disambiguate organization IDs from environment IDs, which was
  causing confusion for Self-Managed deployments.

### Bug Fixes {#v26.15-bug-fixes}

- Fixed unmaterializable functions (e.g., `now()`) being allowed in
  `AS OF` queries, which could return incorrect results.
- Fixed Kafka sink creation failing with an authorization error when the
  progress topic already exists, which affected workflows where topics
  are pre-created by a superuser.
- Fixed a panic when running `COPY FROM STDIN` concurrently with table
  drops.
- Fixed unbounded command queue buildup in internal storage writer tasks
  that could lead to out-of-memory conditions when environments have a
  large number of indexes.
- Fixed the Role Filters display in dark mode in the Console.
- Fixed an incorrect join condition in the Console cluster list that
  could cause incorrect cluster information to be displayed.

## v26.14.1
*Released to Materialize Cloud: 2026-03-05* <br>
*Released to Materialize Self-Managed: 2026-03-06* <br>

This release introduces `COPY FROM` support for CSVs in object storage, source versioning for SQL Server sources, and performance improvements to DDL.

### `COPY FROM` CSVs in object storage

`COPY FROM` now supports bulk importing data directly from Amazon S3 and any
S3-compatible object storage service, such as Google Cloud Storage, Cloudflare
R2, or MinIO. You can import CSV files using an AWS connection or a presigned
URL.

```mzsql
COPY INTO my_table
FROM 's3://my_bucket/my_data.csv'
(FORMAT CSV, AWS CONNECTION = my_aws_conn);
```

For more information, refer to:
- [Syntax: COPY FROM](/sql/copy-from/)
- [Syntax: CREATE CONNECTION (S3-compatible)](/sql/create-connection/#s3-compatible-object-storage)

### SQL Server: Source versioning

For SQL Server sources, we've introduced new syntax
for [`CREATE SOURCE`](/sql/create-source/sql-server-v2/) and [`CREATE
TABLE`](/sql/create-table/). This allows you to better handle schema changes
in your source SQL Server tables.

> **Note:** - Changing column types is currently unsupported.

For more information, refer to:
- [Guide: Handling upstream schema changes with zero
  downtime](/ingest-data/sql-server/source-versioning/)
- [Syntax: `CREATE SOURCE`](/sql/create-source/sql-server-v2/)
- [Syntax: `CREATE TABLE`](/sql/create-table/)

### Improvements {#v26.14-improvements}

- **Faster DDL at scale**: We've improved DDL (e.g., `CREATE VIEW`, `CREATE INDEX`, `DROP`) latency by 37-55% for environments with many objects by making the internal catalog state a persistent data structure with structural sharing.
- **Faster Iceberg sink commits**: We've improved Iceberg sink commit performance by disabling the duplicate check for RowDelta actions, which was causing significant commit time overhead.
- **Up to 28x faster `COPY FROM STDIN`**: We've improved `COPY FROM STDIN` performance by parallelizing ingestion and using constant memory.

### Bug Fixes {#v26.14-bug-fixes}

- Fixed the jsonb contains operator (`?`) to correctly return NULL when
  the left operand is NULL, matching PostgreSQL behavior.
- Internal optimization that reduces resource usage of the catalog server; this can
  reduce resource consumption on restart when indexes are added.
- Fixed a panic when using `COPY FROM` with invalid range values (e.g.,
  `[7,3)` where lower bound exceeds upper bound), now returning a
  proper error message.
- Fixed incorrect replication lag display in the Console during
  PostgreSQL source snapshots, where `offset_committed` was incorrectly
  reported as zero until the snapshot completed.
- Fixed a panic when dropping materialized views that had active
  subscribes depending on older GlobalIds.
- Fixed dataflows being incorrectly re-planned after an environmentd
  restart due to missing per-cluster optimizer feature overrides.
- Fixed query formatting for SQL Server and MySQL sources.

## v26.13.0
*Released to Materialize Cloud: 2026-02-26* <br>
*Released to Materialize Self-Managed: 2026-02-27* <br>

This release includes the release of our Iceberg Sink, performance improvements to `SUBSCRIBE`, and bugfixes.

### Iceberg Sink
> **Public Preview:** This feature is in public preview.

Iceberg sinks provide exactly once delivery of updates from Materialize into [Apache
Iceberg](https://iceberg.apache.org/) tables hosted on [Amazon S3
Tables](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html).
As data changes in Materialize, the corresponding Iceberg tables are
automatically kept up to date. You can sink data from a materialized view, a
source, or a table.

```mzsql
CREATE SINK my_iceberg_sink
  IN CLUSTER sink_cluster
  FROM materialized_view_mv1
  INTO ICEBERG CATALOG CONNECTION iceberg_catalog_connection (
    NAMESPACE = 'my_iceberg_namespace',
    TABLE = 'mv1'
  )
  USING AWS CONNECTION aws_connection
  KEY (row_id)
  MODE UPSERT
  WITH (COMMIT INTERVAL = '60s');
```

For more information, refer to:
- [Guide: How to export results from Materialize to Apache Iceberg Tables](/export-data/iceberg)
- [Blog: Making Iceberg work for Operational Data](https://materialize.com/blog/making-iceberg-work-for-operational-data/)
- [Syntax: CREATE SINK... INTO ICEBERG ](/sql/create-sink/iceberg)

### Improvements {#v26.13-improvements}
- **Improved `SUBSCRIBE` Performance**: We've optimized `SUBSCRIBE` to skip initial snapshots in more cases. This can speed up `SUBSCRIBE` start times.
- **Improved compatibility with external tools**: We've added `strpos` as a
  synonym for the `position` function, improving compatibility with tools such
  as PowerBI.
- **Improved database concurrency**: We've reduced contention when a single
  collection experiences a high volume of updates.

### Bug Fixes {#v26.13-bug-fixes}
- Fixed a panic when constructing multi-dimensional arrays with null values,
  now treating null elements as zero-dimensional arrays consistent with
  PostgreSQL behavior.
- Fixed a bug where dropping a replacement materialized view (instead of
  applying the replacement) could seal the target materialized view for all
  times after an environmentd restart.
- Fixed a bug where `Int2Vector` to `Array` casting did not correctly handle
  element type conversions, potentially causing incorrect results or errors.
- Fixed the Self-Managed bug in the memory-based calculation of replica size
  credits, which was incorrectly multiplying by the number of workers instead of
  using the correct per-process memory limit.
- Fixed an overflow display issue on the roles page in the console.
- Fixed SSO connection configuration pages in the console, which did not load properly due to missing content security policy entries.

## v26.12.0
*Released to Materialize Cloud: 2026-02-19* <br>
*Released to Materialize Self-Managed: 2026-02-20* <br>

This release introduces our Roles and Users page, performance improvements, and bugfixes.

### Role Management
The new Roles and Users page on the Materialize Console allows organization administrators to create roles, grant privileges, and assign roles to users. You can also track the hierarchy of roles using the graph view.

![Create Role experience](/images/releases/v2612_create_role.png)

![Graph View experience](/images/releases/v2612_graph_view.png)

You can navigate to the Roles and Users page directly from the Materialize console. If you're on Materialize Self-Managed, upgrade to v26.12 first. If you're on Materialize Cloud, you can go directly to https://console.materialize.com/roles to reach the page.

### Improvements {#v26.12-improvements}
- **Updated default resource requirements** (<red>*Materialize Self-Managed only*</red>): We've updated the Materialize Self-Managed Helm charts to ensure correct operation on Kind clusters
- **Improved console query history performance**: We've optimized RBAC queries to use OIDs instead of names, resulting in 2-3x faster page execution.

### Bug Fixes {#v26.12-bug-fixes}
- Fixed a panic when using unsupported types (e.g., float) with range
  expressions, now returning a proper error message instead of an internal error.
- Fixed a panic when using empty `int2vector` values, which could cause internal
  errors during query optimization or execution.
- Fixed internal errors that could occur during query optimization due to type
  checking mismatches in `ColumnKnowledge` and related transforms, adding
  fallback handling to prevent crashes.
- Fixed compatibility with older Amazon Aurora PostgreSQL versions when using
  parallel snapshots, by using `SELECT current_setting()` instead of `SHOW` for
  version retrieval.
- Fixed version comparison in the Materialize Kubernetes operator to correctly
  follow semver precedence rules, no longer rejecting upgrades that differ only in build metadata.

## v26.11.0
*Released to Materialize Cloud: 2026-02-19* <br>
*Released to Materialize Self-Managed: 2026-02-13* <br>

This release includes improvements to Avro Schema references, `EXPLAIN` commands, and bug fixes.

### Improvements {#v26.11-improvements}
- **Avro Schema References**: Sources can now use avro schemas which reference
  other schemas when using Confluent Schema Registry.
- **`EXPLAIN` improvements**: `EXPLAIN` now allows you to inspect the query plan
  for `SUBSCRIBE` statements. It also fully qualifies index names if there are
  identically-named indexes across different schemas.
- **More efficient dbt-adapter**: We've added indexes on `mz_hydration_statuses` and `mz_materialization_lag`.
  This should speed up "deployment ready" queries made by our dbt-adapter.

### Bug Fixes {#v26.11-bug-fixes}
- Fixed a bug where `IS DISTINCT FROM` could fail typechecking in certain cases
  involving different data types, causing query errors.
- Improved the error message when `INSERT INTO ... SELECT` transitively
  references a source.

## v26.10.1
*Released to Materialize Cloud: 2026-02-05* <br>
*Released to Materialize Self-Managed: 2026-02-06* <br>

This release introduces Replacement Materialized Views, performance improvements,
and bugfixes.

### Replacement Materialized Views
> **Public Preview:** This feature is in public preview.

Replacement materialized views allow you to modify the definition of an existing materialized view, while preserving all downstream dependencies. Materialize is able to replace a materialized view in place, by calculating the *diff* between the original and the replacement. Once applied, the *diff* flows downstream to all dependent objects.

For more information, refer to:
- [Guide: Replace Materialized Views](/transform-data/updating-materialized-views/replace-materialized-view)
- [Syntax: CREATE REPLACEMENT MATERIALIZED VIEW](/sql/create-materialized-view)
- [Syntax: ALTER MATERIALIZED VIEW](/sql/alter-materialized-view)

### Improvements {#v26.10-improvements}
- **Improved hydration times for PostgreSQL sources**: PostgreSQL sources now perform parallel snapshots. This should improve initial hydration times, especially for large tables.

### Bug Fixes {#v26.10-bug-fixes}
- Fixed an issue where floating-point values like `-0.0` and `+0.0` could be
  treated as different values in equality comparisons but the same in ordering,
  causing incorrect results in operations like `DISTINCT`.
- Fixed an issue where certain SQL keywords required incorrect quoting in
  expressions.
- Fixed the `ORDER BY` clause in `EXPLAIN ANALYZE MEMORY` to correctly sort by
  memory usage instead of by the text representation.
- Fixed a bug where the optimizer could mishandle nullability inside record
  types.
- Fixed an issue where the `mz_roles` system table could produce invalid
  retractions when certain system variables were changed.
- *Console*: Fixed SQL injection vulnerability in identifier quoting where only
  the first quote character was being escaped.

## v26.9.0
*Released to Materialize Cloud: 2026-01-29* <br>
*Released to Materialize Self-Managed: 2026-01-30* <br>

v26.9 includes significant performance improvements to QPS & query latency.

### Improvements {#v26.9-improvements}
- **Up to 2.5x increased QPS**: <a name="v26.9-qps"></a>We've significantly optimized how `SELECT` statements are processed; they are now processed outside the main thread. In our tests, this change increased QPS by as much as 2.5x.
![Chart of QPS before/after](/images/releases/v2609_qps.png)
- **Significant reduction in query latency**: <a
  name="v26.9-latency-reduction"></a>Moving `SELECT` statements off the main
  thread has significantly reduced latency. p99 has reduced by up to 50% for
some workloads. ![Chart of latency
before/after](/images/releases/v2609_latency.png)
- **Dynamically configure system parameters using a ConfigMap** (<red>*Materialize Self-Managed only*</red>): <a name="v26.9-sm-configmap"></a>You can now use a ConfigMap to dynamically update system parameters at runtime. In many cases, this means you don't need to restart Materialize for new system parameters to take effect. You can also specify system parameters which survive restarts and upgrades. Refer to our [documentation on configuring system parameters](/self-managed-deployments/configuration-system-parameters/#configure-system-parameters-via-configmap).
- Added `ABORT` as a PostgreSQL-compatible alias for the `ROLLBACK` transaction command, to improve compatibility with GraphQL engines like Hasura

### Bug Fixes {#v26.9-bug-fixes}
- Fixed an issue causing new generations to be promoted prematurely when using the `WaitUntilReady` upgrade strategy (<red>*Materialize Self-Managed only*</red>)
- Fixed a race condition in source reclock that could cause panics when the `as_of` timestamp was newer than the cached upper bound.
- Improved error messages when the load balancer cannot connect to the upstream environment server

## v26.8.0
*Released to Materialize Cloud: 2026-01-22* <br>
*Released to Materialize Self-Managed: 2026-01-23* <br>

v26.8 includes a new notice in the Console to help catch common SQL mistakes,
Protobuf compatibility improvements, and performance optimizations for view
creation.

### Improvements {#v26.8-improvements}
- Added a Console notice when users write `= NULL`, `!= NULL`, or `<>
  NULL` in SQL expressions instead of `IS NULL` or `IS NOT NULL`. Comparisons
  using `=`, `!=`, or `<>` with `NULL` always evaluate to `NULL`.
- Protobuf schemas that import well-known types (such as `google.protobuf.Timestamp` or `google.protobuf.Duration`) now work automatically when using a Confluent Schema Registry connection.
- Improved performance of view creation by caching optimized expressions, resulting in approximately 2x faster view creation in some scenarios.

## v26.7.0
*Released to Materialize Self-Managed: 2026-01-16* <br>
*Released to Materialize Cloud: 2026-01-17* <br>

v26.7 improves compatibility with go-jet and includes bug fixes.

### Improvements {#v26.7-improvements}

- **Improved compatibility with go-jet**: We've added the `attndims` column to `pg_attribute`. We've also fixed `pg_type.typelem` to correctly report element types for named list types.
- **Pretty print SQL in the console**: We've made it easier to read the definitions for views and materialized views in the console.

### Bug Fixes {#v26.7-bug-fixes}
- Fixed an issue where type error messages could inadvertently expose constant values from queries.
- The console reconnects more gracefully if the connection to the backend is interrupted

## v26.6.0
*Released to Materialize Cloud: 2026-01-08*<br>
*Released to Materialize Self-Managed: 2026-01-09*<br>

v26.6.0 includes bug fixes for Kafka sinks and Self-Managed deployments.

### Bug Fixes {#v26.6-bug-fixes}
- Fixed an issue where console and balancer deployments could fail to upgrade to the correct version during Self-Managed environment upgrades.
- Fixed an issue where `ALTER SINK ... SET FROM` on Kafka sinks could incorrectly restart in snapshot mode even when the sink had already made progress, causing unnecessary resource consumption and potential out-of-memory errors.

## v26.5.1
*Released to Materialize Self-Managed: 2025-12-23* <br>
*Released to Materialize Cloud: 2026-01-08* <br>

v26.5.1 enhances our SQL Server source, improves performance, and strengthens Materialize Self-Managed reliability.

### Improvements {#v26.5-improvements}
- **VARCHAR(MAX) and NVARCHAR(MAX) support for SQL Server**: The Materialize SQL Server source now supports `varchar(max)` and `nvarchar(max)` data types.
- **Faster authentication for connection poolers**: We've added an index to the `pg_authid` system catalog. This should significantly improve the performance of default authentication queries made by connection poolers like pgbouncer.
- **Faster Kafka sink startup**: We've updated the default Kafka progress topic configuration to reduce the amount of progress data processed when creating new [Kafka sinks](/export-data/kafka/).
- **dbt strict mode**: We've introduced `strict_mode` to dbt-materialize, our dbt adapter. `strict_mode` enforces production-ready isolation rules and improves cluster health monitoring. It does so by validating source idempotency, schema isolation, cluster isolation and index restrictions.
- **SQL Server Always On HA failover support** (<red>*Materialize Self-Managed only*</red>): Materialize Self-Managed now offers better support for handling failovers, without downtime, in SQL Server Always On sources. [Contact our support team](/support/) to enable this in your environment.
- **Auto-repair accidental changes** (<red>*Materialize Self-Managed only*</red>): Improvements to the controller logic allow Materialize to auto-repair changes such as deleting a StatefulSet. This means that your production setups should be more robust in the face of accidental changes.
- **Track deployment status after upgrades** (<red>*Materialize Self-Managed only*</red>): The Materialize custom resource now displays both active and desired `environmentd` versions. This makes it easier to track deployment status after upgrades.

### Bug fixes {#v26.5-bug-fixes}
- Added additional checks to string functions (`replace`, `translate`, etc.) to help prevent out-of-memory errors from inflationary string operations.
- Fixed an issue which could cause panics during connection drops; this means improved stability when clients disconnect.
- Fixed an issue where disabling console or balancers would fail if they were already running.
- Fixed an issue where balancerd failed to upgrade and remained stuck on its pre-upgrade version.

## v26.4.0

*Released to Materialize Self-Managed: 2025-12-17* <br>
*Released to Materialize Cloud: 2025-12-18*

v26.4.0 introduces several performance improvements and bugfixes.

### Improvements {#v26.4-improvements}
- **Over 2x higher connections per second (CPS)**: We've optimized how Materialize handles inbound connection requests. In our tests, we've observed 2x - 4x improvements to the rate at which new client connections can be established. This is especially beneficial when spinning up new environments, warming up connection pools, or scaling client instances.
- **Up to 3x faster hydration times for large PostgreSQL tables**: We've reduced the overhead incurred by communication between multiple *workers* on a large cluster. We've observed up to 3x throughput improvement when ingesting 1 TB PostgreSQL tables on large clusters.
- **More efficient source ingestion batching**: Sources now batch writes more effectively. This can result in improved freshness and lower resource utilization, especially when a source is doing a large number of writes.
- **CloudSQL HA failover support** (<red>*Materialize Self-Managed only*</red>): Materialize Self-Managed now offers better support for handling failovers in CloudSQL HA sources, without downtime. [Contact our support team](/support/) to enable this in your environment.
- **Manual Promotion** (<red>*Materialize Self-Managed only*</red>): [Rollout strategies](/self-managed-deployments/upgrading/#rollout-strategies) allow you control how Materialize transitions from the current generation to a new generation during an upgrade. We've added a new rollout strategy called `ManuallyPromote` which allows you to choose when to promote the new generation. This means that you can minimize the impact of potential downtime.

### Bug Fixes {#v26.4-bug-fixes}
- Fixed timestamp determination logic to handle empty read holds correctly.
- Fixed lazy creation of temporary schemas to prevent schema-related errors.
- Reduced SCRAM iterations in scalability framework and fixed fallback image configuration.

## v26.3.0

*Released to Materialize Cloud & Materialize Self-Managed: 2025-12-12*<br>

### Improvements {#v26.3-improvements}
- For Self-Managed: added version upgrade window validation, to prevent skipping required intermediate versions during upgrades.
- Improved activity log throttling to apply across all statement executions, not just initial prepared statement execution, providing more consistent logging behavior.

### Bug Fixes {#v26.3-bug-fixes}
- Fixed validation for replica sizes to prevent configurations with zero scale or workers, which previously caused division-by-zero errors and panics.
- Fixed frontend `SELECT` sequencing to gracefully handle collections that are dropped during real-time recent timestamp determination.

## v26.2.0

*Released Cloud: 2025-12-05*<br>
*Released Self-Managed: 2025-12-09*

This release focuses primarily on bug fixes.

### Bug fixes {#v26.2-bug-fixes}
- **Catalog updates**: Fixed a bug where catalog item version updates were incorrectly ignored when the `create_sql` didn't change, which could cause version updates to not be applied properly.

- **Console division by zero**: Fixed a division by zero error in the console, specifically when viewing `mz_console_cluster_utilization_overview`.

- **ALTER SINK improvements**: Fixed `ALTER SINK ... SET FROM` to prevent panics in certain situations.

- **Improved rollout handling**: Fixed an issue where rollouts could leave a pod at their previous configuration.

- **Dependency drop handling**: Fixed panics that could occur when dependencies are dropped during a SELECT or COPY TO. These operations now gracefully return a `ConcurrentDependencyDrop` error.

## v26.1.0
*Released Self-Managed: 2025-11-26*

v26.1.0 introduces `EXPLAIN ANALYZE CLUSTER`, console bugfixes, and improvements for SQL Server support, including the ability to create a SQL Server Source via the Console.

### `EXPLAIN ANALYZE CLUSTER`
The [`EXPLAIN ANALYZE`](/sql/explain-analyze/) statement helps analyze how objects, namely indexes or materialized views, are running. We've introduced a variation of this statement, `EXPLAIN ANALYZE CLUSTER`, which presents a summary of every object running on your current cluster.

You can use this statement to understand the CPU time spent and memory consumed per object on a given cluster. You can also reveal whether an object has skewed operators, where work isn't evenly distributed among workers.

For example, to get a report on memory, you can run `EXPLAIN ANALYZE CLUSTER MEMORY`, and you'll receive an output similar to the table below:
| object                                  | global_id | total_memory | total_records |
| --------------------------------------- | --------- | ------------ | ------------- |
| materialize.public.idx_top_buyers       | u85496    | 2086 bytes   | 25            |
| materialize.public.idx_sales_by_product | u85492    | 1909 kB      | 148607        |
| materialize.public.idx_top_buyers       | u85495    | 1332 kB      | 77133         |

To understand worker skew, you can run `EXPLAIN ANALYZE CLUSTER CPU WITH SKEW`, and you'll receive an output similar the table below:
| object                                  | global_id | worker_id | max_operator_cpu_ratio | worker_elapsed  | avg_elapsed     | total_elapsed   |
| --------------------------------------- | --------- | --------- | ---------------------- | --------------- | --------------- | --------------- |
| materialize.public.idx_sales_by_product | u85492    | 0         | 1.18                   | 00:00:00.094447 | 00:00:00.079829 | 00:00:00.159659 |
| materialize.public.idx_top_buyers       | u85495    | 0         | 1.15                   | 00:00:01.371221 | 00:00:01.363659 | 00:00:02.727319 |
| materialize.public.idx_top_buyers       | u85495    | 1         | 1.03                   | 00:00:01.356098 | 00:00:01.363659 | 00:00:02.727319 |
| materialize.public.idx_top_buyers       | u85496    | 1         | 1.01                   | 00:00:00.021163 | 00:00:00.021048 | 00:00:00.042096 |
| materialize.public.idx_top_buyers       | u85496    | 0         | 0.99                   | 00:00:00.020932 | 00:00:00.021048 | 00:00:00.042096 |
| materialize.public.idx_sales_by_product | u85492    | 1         | 0.82                   | 00:00:00.065211 | 00:00:00.079829 | 00:00:00.159659 |

### Improved SQL Server support

Materialize v26.1.0 includes improved support for SQLServer, including the ability to create a SQLServer Source via the console.

### Upgrade notes for v26.1.0

- To upgrade to `v26.1` or future versions, you must first upgrade to `v26.0`

## Self-Managed v26.0.0

*Released: 2025-11-18*

### Swap support

Starting in v26.0.0, Self-Managed Materialize enables swap by default. Swap
allows for infrequently accessed data to be moved from memory to disk. Enabling
swap reduces the memory required to operate Materialize and improves cost
efficiency.

To facilitate upgrades from v25.2, Self-Managed Materialize added new labels to
the node selectors for `clusterd` pods. To upgrade, you must prepare your nodes
by adding the required labels. For detailed instructions, see [Prepare for swap
and upgrade to v26.0](/self-managed-deployments/appendix/upgrade-to-swap/).

### SASL/SCRAM-SHA-256 support

Starting in v26.0.0, Self-Managed Materialize supports SASL/SCRAM-SHA-256
authentication for PostgreSQL wire protocol connections. For more information,
see [Authentication](/security/self-managed/authentication/).

When SASL authentication is enabled:

- **PostgreSQL connections** (e.g., `psql`, client libraries, [connection
  poolers](/serve-results/connection-pooling/)) use SCRAM-SHA-256 authentication
- **HTTP/Web Console connections** use standard password authentication

This hybrid approach provides maximum security for SQL connections while maintaining
compatibility with web-based tools.

### License Key

Starting in v26.0.0, Self-Managed Materialize requires a license key.

| License key type | Deployment type | Action |
| --- | --- | --- |
| Community | New deployments | <p>To get a license key:</p> <ul> <li>If you have a Cloud account, visit the <a href="https://console.materialize.com/license/" ><strong>License</strong> page in the Materialize Console</a>.</li> <li>If you do not have a Cloud account, visit <a href="https://materialize.com/self-managed/community-license/" >https://materialize.com/self-managed/community-license/</a>.</li> </ul> |
| Community | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |
| Enterprise | New deployments | Visit <a href="https://materialize.com/self-managed/enterprise-license/" >https://materialize.com/self-managed/enterprise-license/</a> to purchase an Enterprise license. |
| Enterprise | Existing deployments | Contact <a href="https://materialize.com/docs/support/" >Materialize support</a>. |

For new deployments, you configure your license key in the Kubernetes Secret
resource during the installation process. For details, see the [installation
guides](/self-managed-deployments/installation/). For existing deployments, you can configure your
license key via:

```bash
kubectl -n materialize-environment patch secret materialize-backend -p '{"stringData":{"license_key":"<your license key goes here>"}}' --type=merge
```

### PostgreSQL: Source versioning

For PostgreSQL sources, starting in v26.0.0, Materialize introduces new syntax
for [`CREATE SOURCE`](/sql/create-source/postgres-v2/) and [`CREATE
TABLE`](/sql/create-table/) to allow better handle DDL changes to the upstream
PostgreSQL tables.

> **Note:** - This feature is currently supported for PostgreSQL sources, with
> additional source types coming soon.
> - Changing column types is currently unsupported.

For more information, see:
- [Guide: Handling upstream schema changes with zero
  downtime](/ingest-data/postgres/source-versioning/)
- [`CREATE SOURCE`](/sql/create-source/postgres-v2/)
- [`CREATE TABLE`](/sql/create-table/)

### Deprecation

The `inPlaceRollout` setting has been deprecated and will be ignored. Instead,
use the new setting `rolloutStrategy` to specify either:

- `WaitUntilReady` (*Default*)
- `ImmediatelyPromoteCausingDowntime`

For more information, see [`rolloutStrategy`](/self-managed-deployments/upgrading/#rollout-strategies).

### Terraform helpers

The following sample Terraform modules are available for deploying Materialize:

| Module | Description |
| --- | --- |
| <a href="https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/aws" >Amazon Web Services (AWS)</a> | An example Terraform module for deploying Materialize on AWS. See <a href="/self-managed-deployments/installation/install-on-aws/" >Install on AWS</a> for detailed instructions usage. |
| <a href="https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/azure" >Azure</a> | An example Terraform module for deploying Materialize on Azure. See <a href="/self-managed-deployments/installation/install-on-azure/" >Install on Azure</a> for detailed instructions usage. |
| <a href="https://github.com/MaterializeInc/materialize-terraform-self-managed/tree/main/gcp" >Google Cloud Platform (GCP)</a> | An example Terraform module for deploying Materialize on GCP. See <a href="/self-managed-deployments/installation/install-on-gcp/" >Install on GCP</a> for detailed instructions usage. |

#### Upgrade notes for v26.0.0

- Upgrading to `v26.0.0` is a major version upgrade. To upgrade to `v26.0` from
  `v25.2.X` or `v25.1`, you must first upgrade to `v25.2.16` and then upgrade to
  `v26.0.0`.

- For upgrades, the `inPlaceRollout` setting has been deprecated and will be
  ignored. Instead, use the new setting `rolloutStrategy` to specify either:
  - `WaitUntilReady` (*Default*)
  - `ImmediatelyPromoteCausingDowntime`

  For more information, see
  [`rolloutStrategy`](/self-managed-deployments/upgrading/#rollout-strategies).

- New requirements were introduced for [license keys](/releases/#license-key).
  To upgrade, you will first need to add a license key to the `backendSecret`
  used in the spec for your Materialize resource.

  See [License key](/releases/#license-key) for details on getting your license
  key.

- Swap is now enabled by default. Swap reduces the memory required to
  operate Materialize and improves cost efficiency. Upgrading to `v26.0`
  requires some preparation to ensure Kubernetes nodes are labeled
  and configured correctly. As such:

  - If you are using the Materialize-provided Terraforms, upgrade to version
    `v0.6.1` of the Terraform.

  - If you are <red>**not**</red> using a Materialize-provided Terraform, refer
    to [Prepare for swap and upgrade to v26.0](/self-managed-deployments/appendix/upgrade-to-swap/).

See also [Version-specific upgrade
notes](/self-managed-deployments/upgrading/version-notes/).

## See also

- [Release Schedule](/releases/schedule/)

---

## Materialize v26.45

---

## Materialize v26.44

---

## Materialize v26.43

---

## Materialize v26.42

---

## Materialize v26.41

---

## Materialize v26.40

---

## Materialize v26.39

---

## Materialize v26.38

---

## Materialize v26.37

---

## Materialize v26.36

---

## Materialize v26.35

---

## Materialize v26.34

---

## Materialize v26.33

---

## Materialize v26.32

---

## Materialize v26.31

---

## Materialize v26.30

---

## Materialize v26.29

---

## Materialize v26.28

---

## Materialize v26.27

---

## Materialize v26.26

---

## Materialize v26.25

---

## Materialize v26.24

---

## Materialize v26.23

---

## Materialize v26.22

---

## Materialize v26.21

---

## Materialize v26.20

---

## Materialize v26.19

---

## Materialize v26.18

---

## Materialize v26.17

---

## Materialize v26.16

---

## Materialize v26.15

---

## Materialize v26.14

---

## Materialize v26.13

---

## Materialize v26.12

---

## Materialize v26.11

---

## Materialize v26.10

---

## Materialize v26.9

---

## Materialize v26.8

---

## Materialize v26.7

---

## Materialize v26.6

---

## Materialize v26.5

---

## Materialize v26.4

---

## Materialize v26.3

---

## Materialize v26.2

---

## Materialize v26.1

---

## Materialize v26.0

---

## Materialize v0.164

---

## Materialize v0.163

---

## Materialize v0.162

---

## Materialize v0.161

---

## Materialize v0.160

---

## Materialize v0.159

---

## Materialize v0.158

---

## Materialize v0.157

---

## Materialize v0.156

---

## Materialize v0.155

---

## Materialize v0.154

---

## Materialize v0.153

---

## Materialize v0.152

---

## Materialize v0.151

---

## Materialize v0.150

---

## Materialize v0.149

---

## Materialize v0.148

---

## Materialize v0.147

---

## Materialize v0.146

---

## Materialize v0.145

---

## Materialize v0.144

---

## Materialize v0.143

---

## Materialize v0.142

---

## Materialize v0.141

---

## Materialize v0.140

---

## Materialize v0.139

---

## Materialize v0.138

---

## Materialize v0.137

---

## Materialize v0.136

---

## Materialize v0.135

---

## Materialize v0.134

---

## Materialize v0.133

---

## Materialize v0.132

---

## Materialize v0.131

---

## Materialize v0.130

---

## Materialize v0.129

---

## Materialize v0.128

---

## Materialize v0.127

---

## Materialize v0.126

---

## Materialize v0.125

---

## Materialize v0.124

---

## Materialize v0.123

---

## Materialize v0.122

---

## Materialize v0.121

---

## Materialize v0.120

---

## Materialize v0.118

---

## Materialize v0.117

---

## Materialize v0.116

---

## Materialize v0.115

---

## Materialize v0.114

---

## Materialize v0.113

---

## Materialize v0.112

---

## Materialize v0.111

---

## Materialize v0.110

## v0.110

---

## Materialize v0.109

<!-- mz-docs page: releases/schedule -->

# Release Schedule
Release schedule for Materialize Cloud and Self-Managed
Starting with the v26.1.0 release, Materialize releases on a weekly schedule for
both Cloud and Self-Managed.

## Cloud upgrade schedule

In general, Materialize Cloud uses the following weekly schedule to upgrade all
regions to the latest release, the listed times may vary based on operational needs:

Region        | Day of week | Time
--------------|-------------|-----------------------------
aws/eu-west-1 | Wednesday   | 2100-2300 [Europe/Dublin]
aws/us-east-1 | Thursday    | 0500-0700 [America/New_York]
aws/us-west-2 | Thursday    | 0500-0700 [America/New_York]

During an upgrade, clients may experience brief connection interruptions, but
the service otherwise remains fully available. Upgrade windows were chosen to be
outside of business hours in the most representative time zone for the region.

> **Note:** - Materialize may occasionally deploy unscheduled releases to fix urgent bugs.
> - Actual cutover time may fall outside of the upgrade window.
> - Releases may skip some weeks.
> - Upgrade windows follow any daylight saving time or summer time rules
> for their indicated time zone.

[America/New_York]: https://time.is/New_York
[Europe/Dublin]: https://time.is/Dublin

## Self-Managed release schedule

In general, Materialize releases new Self-Managed versions on Friday.

> **Note:** - Materialize may occasionally have unscheduled releases to fix urgent bugs.
> - Releases may skip some weeks.


<!-- mz-docs page: releases/v0.100 -->

# Materialize v0.100
## v0.100

#### SQL

* Add a [`MAP` expression](/sql/types/map/#construction) that allows constructing a `map`
  from a list of key–value pairs or a subquery.

  ```mzsql
  SELECT MAP['a' => 1, 'b' => 2];

       map
  -------------
   {a=>1,b=>2}
  ```

#### Bug fixes and other improvements

* Support the [`COPY TO`](/sql/copy-to/) command in the WebSocket API, so it's
  possible to run it from the SQL Shell.

<!-- mz-docs page: releases/v0.101 -->

# Materialize v0.101
## v0.101

#### Sources and sinks

* Allow configuring the initial and the maximum snapshot size for [load generator sources](/sql/create-source/load-generator/)
  via the new `AS OF` and `UP TO` `WITH` options.

#### SQL

* Disallow using the [`mz_now()` function](/sql/functions/now_and_mz_now/) in
  all positions and dependencies of `INSERT`, `UPDATE`, and `DELETE`
  statements.

#### Bug fixes and other improvements

* Extend `pg_catalog` and `information_schema` system catalog coverage for
  compatibility with Metaplane ([#27155](https://github.com/MaterializeInc/materialize/issues/27155)).

* Add details to errors related to insufficient privileges pointing to the
  missing permissions ([#27176](https://github.com/MaterializeInc/materialize/issues/27176)).

* Avoid resetting sink statistics when using the [`ALTER CONNECTION`](/sql/alter-connection/)
  command ([#27236](https://github.com/MaterializeInc/materialize/issues/27236)).

* Modify the output of the [`SHOW CREATE SOURCE`](/sql/show-create-source/)
  command for [load generator sources](/sql/create-source/load-generator/) to
  always include the `FOR ALL TABLES` clause, which is required ([#27250](https://github.com/MaterializeInc/materialize/issues/27250)).

<!-- mz-docs page: releases/v0.106 -->

# Materialize v0.106
[//]: # "NOTE(morsapaes) v0.106 shipped support for the new `VALUE DECODING
ERRORS` clause behind a feature flag, which allows Kafka upsert sources to
continue ingesting data in the presence of decoding errors."

## v0.106

#### SQL

* Add support for the [`SHOW CREATE CLUSTER`](/sql/show-create-cluster/)
  command, which returns the DDL statement used to create a cluster.

  ```mzsql
  SHOW CREATE CLUSTER c;
  ```
  ```nofmt
      name          |    create_sql
  ------------------+--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
   c                | CREATE CLUSTER "c" (DISK = false, INTROSPECTION DEBUGGING = false, INTROSPECTION INTERVAL = INTERVAL '00:00:01', MANAGED = true, REPLICATION FACTOR = 1, SIZE = '100cc', SCHEDULE = MANUAL)
  ```

#### Bug fixes and other improvements

* Add the `mz_catalog_unstable` and [`mz_introspection`](/sql/system-catalog/mz_introspection/)
  system schemas to the system catalog, in support of the ongoing migration of
  unstable and replica introspection relations from the [`mz_internal`](/sql/system-catalog/mz_internal/)
  system schema into dedicated schemas.

* Add `introspection_debugging` and `introspection_interval` to the
  `mz_clusters` system catalog table. These columns are useful for feature
  development.

* Fix a bug in the [MySQL source](https://materialize.com/docs/sql/create-source/mysql/)
  that unecessarily enforced the `replica_preserve_commit_order` configuration
  parameter when connecting to a primary server for replication. This
  configuration parameter is only required when connecting to a MySQL
  read-replica.

<!-- mz-docs page: releases/v0.107 -->

# Materialize v0.107
## v0.107

#### Sources and sinks

* Support exporting data to Google Cloud Storage (GCS) using [AWS connections](/sql/create-connection/#aws)
  and the [`COPY TO`](/sql/copy-to/) command. While Materialize does not natively
  support Google Cloud Platform (GCP) connections, GCS is interoperable with
  Amazon S3 (via the [XML API](https://cloud.google.com/storage/docs/interoperability)),
  which allows GCP users to take advantage of [S3 bulk exports](/sql/copy-to/#copy-to-s3)
  also for GCS.

#### SQL

* Add the [`@>` and `<@` operators](/sql/types/list/#list-containment), which
  allow checking if a list contains the elements of another list. Like
  [array containment operators in PostgreSQL](https://www.postgresql.org/docs/current/functions-array.html#FUNCTIONS-ARRAY),
  list containment operators in Materialize **do not** account for duplicates.

  ```mzsql
  SELECT LIST[7,3,1] @> LIST[1,3,3,3,3,7] AS contains;
  ```
  ```nofmt
   contains
  ----------
   t
  ```

* Add `database_name` and `search_path` to the
  [mz_internal.mz_recent_activity_log](/sql/system-catalog/mz_internal/#mz_recent_activity_log)
  system catalog view. These columns show the value of the `database` and
  `search_path` configuration parameters at execution time, respectively.

* Add `connection_id` to the [mz_internal.mz_sessions](/sql/system-catalog/mz_internal/#mz_sessions)
  system catalog table. This column shows the connection ID of the session, which
  is unique for active sessions and corresponds to `pg_backend_pid()`.

#### Bug fixes and other improvements

* Move the `PROGRESS TOPIC REPLICATION FACTOR` option to the `CREATE CONNECTION`
  command for [Kafka connections](/sql/create-connection/#kafka)
  ([#27931](https://github.com/MaterializeInc/materialize/issues/27931)). The progress topic is a property of the connection, not the
  source or sink.

<!-- mz-docs page: releases/v0.108 -->

# Materialize v0.108
## v0.108

#### Sources and sinks

* Allow specifying the message key format and the message value format
  separately in [Kafka sinks](/sql/create-sink/kafka/), using the new `KEY
  FORMAT ... VALUE FORMAT ...` option.

* Support including a header row in `CSV` files exported using [S3 bulk exports](/sql/copy-to/#copy-to-s3).

  ```mzsql
  COPY some_view TO 's3://mz-to-snow/csv/'
  WITH (
      AWS CONNECTION = aws_role_assumption,
      FORMAT = 'csv',
      HEADER = true
    );
  ```

#### SQL

* Add `hydration_time` to the [`mz_internal.mz_compute_hydration_statuses`](/sql/system-catalog/mz_internal/#mz_compute_hydration_statuses)
  system catalog view. This column shows the amount of time it took for a
  dataflow-powered object to hydrate (i.e., be backfilled with any pre-existing
  data).

#### Bug fixes and other improvements

* Disallow creating sinks that directly depend on system catalog objects ([#28122](https://github.com/MaterializeInc/materialize/issues/28122)).

<!-- mz-docs page: releases/v0.27 -->

# Materialize v0.27
v0.27.0 is the first cloud-native release of Materialize. It contains
substantial breaking changes from [v0.26 LTS].

## v0.27.0

* Add [clusters](/sql/create-cluster) and [cluster replicas](/sql/create-cluster-replica/),
  which together allocate isolated, highly available, and horizontally scalable
  compute resources that incrementally maintain a "cluster" of indexes.

* Add [materialized views](/sql/create-materialized-view), which are views that
  are persisted in durable storage and incrementally updated as new data
  arrives.

  A materialized view is created in a
  [cluster](/fundamentals/concepts/clusters/) that
  is tasked with keeping its results up-to-date, but **can be referenced in any
  cluster**.

  The result of a materialized view is not maintained in memory, unless you
  create an [index](/sql/create-index) on it. However, intermediate state
  necessary for efficient incremental updates of the materialized view may be
  maintained in memory.

* Add [connections](/sql/create-connection/), which describe how to connect to
  and authenticate with external systems. Once created, a connection is reusable
  across multiple [`CREATE SOURCE`](/sql/create-source) and
  [`CREATE SINK`](/sql/create-sink) statements.

* Add [secrets](/sql/create-secret), which securely store sensitive credentials
  (like passwords and SSL keys) for reference in connections.

* Durably record data ingested from [sources](/sql/create-source).

  Once a source has acknowledged data upstream (e.g., via committing a Kafka
  offset or advancing a PostgreSQL replication slot), it will never re-read that
  data. As a result, PostgreSQL sources no longer have a "single
  materialization" limitation. All sources are directly queryable via
  [`SELECT`](/sql/select).

* Allow provisioning the size of a source or sink.

  Each source and sink now runs with an isolated set of compute resources. You
  can adjust the size of the resource allocation with the
  [`SIZE`](/sql/create-source/#sizing-a-source) parameter.

* Add [load generator sources](/sql/create-source/load-generator), which
  produce synthetic data for use in demos and performance tests.

* Add an [HTTP API](/serve-results/http-api) which supports executing SQL queries
  over HTTP.

* **Breaking change.** Require all [indexes](/sql/create-index) to be associated
  with a cluster.

* **Breaking change.** Require the use of [connections](/sql/create-connection/)
  with Kafka sources, PostgreSQL sources, and Kafka sinks.

* **Breaking change.** Rename `TAIL` to [`SUBSCRIBE`](/sql/subscribe).

* **Breaking change.** Change the meaning of `CREATE MATERIALIZED VIEW`.

  `CREATE MATERIALIZED VIEW` now creates a new type of object called a
  [materialized view](/sql/create-materialized-view), rather than providing a
  shorthand for creating a view with a default index.

  To emulate the old behavior, explicitly create a default index after creating
  a view:

  ```mzsql
  CREATE VIEW <name> ...;
  CREATE DEFAULT INDEX ON <name>;
  ```

* **Breaking change.** Remove the `MATERIALIZED` option from `CREATE SOURCE`.

  `CREATE MATERIALIZED SOURCE` is no longer shorthand for creating a source with
  a default index. Instead, you must explicitly create a default index after
  creating a source:

  ```mzsql
  CREATE SOURCE <name> ...;
  CREATE DEFAULT INDEX ON <name>;
  ```

* **Breaking change.** Remove support for the following source types:

  * PubNub
  * Kinesis
  * S3

* **Breaking change.** Remove the `reuse_topic` option from
  [Kafka sinks](/sql/create-sink).

  The exactly-once semantics enabled by `reuse_topic` are now on by default.

* **Breaking change.** Remove the `consistency_topic` option from
  [Kafka sinks](/sql/create-sink).

* **Breaking change.** Do not default to the [Debezium
  envelope](/sql/create-sink/kafka/#debezium-envelope) in `CREATE SINK`. You
  must explicitly specify the envelope to use.

* **Breaking change.** Remove the `CREATE VIEWS` statement, which was used to
  separate the data in a PostgreSQL source into a single relation per upstream
  table.

  The PostgreSQL source now automatically creates a relation in Materialize
  for each upstream table.

* **Breaking change.** Overhaul the system catalog.

  The relations in the [`mz_catalog`](/sql/system-catalog/mz_catalog) schema
  have been adjusted substantially to support the above changes. Many column
  and relation names were adjusted for consistency. The resulting relations
  are now part of Materialize's stable interface.

  Relations which were not ready for stabilization were moved to a new
  [`mz_internal`](/sql/system-catalog/mz_internal) schema.

* **Breaking change.** Rename `mz_logical_timestamp()` to [`mz_now`](/sql/functions/now_and_mz_now/).

## Upgrade guide

Following are several examples of how to adapt source and view definitions
from Materialize v0.26 LTS for Materialize v0.27:

### Authenticated Kafka source

Change from:

```mzsql
CREATE SOURCE kafka_sasl
  FROM KAFKA BROKER 'broker.tld:9092' TOPIC 'top-secret' WITH (
      security_protocol = 'SASL_SSL',
      sasl_mechanisms = 'PLAIN',
      sasl_username = '<BROKER_USERNAME>',
      sasl_password = '<BROKER_PASSWORD>'
  )
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY 'https://schema-registry.tld' WITH (
      username = '<SCHEMA_REGISTRY_USERNAME>',
      password = '<SCHEMA_REGISTRY_PASSWORD>'
  );
```

to:

```mzsql
CREATE SECRET kafka_password AS '<BROKER_PASSWORD>';
CREATE SECRET csr_password AS '<SCHEMA_REGISTRY_PASSWORD>';

CREATE CONNECTION kafka FOR KAFKA
    BROKER 'broker.tld:9092',
    SASL MECHANISMS 'PLAIN',
    SASL USERNAME 'materialize',
    SASL PASSWORD SECRET kafka_password;

CREATE CONNECTION csr
  FOR CONFLUENT SCHEMA REGISTRY
    USERNAME = '<SCHEMA_REGISTRY_USERNAME>',
    PASSWORD = SECRET csr_password;

CREATE SOURCE kafka_top_secret
  FROM KAFKA CONNECTION kafka TOPIC ('top-secret')
  FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr
  WITH (SIZE = '3xsmall');
```

### Materialized view

Change from:

```mzsql
CREATE MATERIALIZED VIEW v AS SELECT ...
```

to:

```mzsql
CREATE VIEW v AS SELECT ...
CREATE DEFAULT INDEX ON v
```

### Materialized source

Change from:

```mzsql
CREATE MATERIALIZED SOURCE src ...
```

to:

```mzsql
CREATE SOURCE src ...
```

If you are performing point lookups on `src` directly, consider building an
index on `src` directly:

```
CREATE INDEX on src (lookup_col1, lookup_col2)
```

### `TAIL`

Change from:

```mzsql
COPY (TAIL t) TO STDOUT
```

to:

```mzsql
COPY (SUBSCRIBE t) TO STDOUT
```

[v0.26 LTS]: https://materialize.com/docs/lts/release-notes/#v0.26.4

<!-- mz-docs page: releases/v0.28 -->

# Materialize v0.28
## v0.28.0

* Use [static IPs](/ops/network-security/static-ips/) when initiating connections from sources
  and sinks. You can use these IPs in your firewall configuration to authorize
  connections from your Materialize region.

* Improve the syntax for [`CREATE CONNECTION`](/sql/create-connection). The
  `FROM` keyword was replaced with `TO`, and the option list must now be
  enclosed in parenthesis.

  **New syntax**

  ```mzsql
  CREATE CONNECTION kafka_connection TO KAFKA (
    BROKER 'unique-jellyfish-0000.us-east-1.aws.confluent.cloud.io:9092',
    SASL MECHANISMS = 'SCRAM-SHA-256',
    SASL USERNAME = 'foo',
    SASL PASSWORD = SECRET kafka_password
  );
  ```

  **Old syntax**

  ```mzsql
  CREATE CONNECTION kafka_connection FOR KAFKA
    BROKER 'unique-jellyfish-0000.us-east-1.aws.confluent.cloud:9092',
    SASL MECHANISMS = 'SCRAM-SHA-256',
    SASL USERNAME = 'foo',
    SASL PASSWORD = SECRET kafka_password;
  ```

  The old syntax is still supported for backwards compatibility, but its use is
  discouraged.

* Improve the usability of the `EXPLAIN` command. For an overview of the new
  `EXPLAIN` syntax, check the [updated documentation](/sql/explain-plan/).

* Include all indexes when running the [`SHOW INDEXES`](/sql/show-indexes)
  command, regardless of the number of columns. Previously, `SHOW INDEXES`
  would omit any indexes with 0 columns.

* Include all indexes when a schema is specified using `SHOW INDEXES ON`.
  Previously, the command would not correctly display existing indexes in
  non-active schemas.

* Add a default index for all `SHOW` commands in the
  [`mz_introspection`](/sql/show-clusters/#mz_catalog_server-system-cluster)
  cluster. For the best performance when executing `SHOW` commands, switch to
  the `mz_introspection` cluster using:

  ```mzsql
  SET CLUSTER = mz_introspection;
  ```

* Correctly use the `char` type for `pg_type.typcategory`. Previously,
  `typcategory` used the `text` type, which caused errors in language drivers
  that expect the documented `char` type, like sqlx.

* Add the [`mz_introspection` system
  cluster](/sql/show-clusters/#mz_catalog_server-system-cluster) to support
  efficiently serving common introspection queries.

* Add the [`mz_system` system
  cluster](/sql/show-clusters/#mz_system-system-cluster) to support various
  internal system tasks.

* **Breaking change.** Change the type of a materialized view in the
  `mz_objects` relation from `materialized view` to `materialized-view`, for
  consistency with how multi-word types are represented elsewhere in the
  catalog.

<!-- mz-docs page: releases/v0.29 -->

# Materialize v0.29
## v0.29.0

* Fix a bug where implicit type casts prevented indexes from being used ([#15476](https://github.com/MaterializeInc/materialize/issues/15476)).

* Improve Materialize's ability to use indexes when comparing column expressions
  to literal values, particularly in cases where e.g. `col_a` was of type
  `VARCHAR`:

  ```mzsql
  SELECT * FROM table_foo WHERE col_a = 'hello';
  ```

* Fix a bug that prevented using pre-existing topics with multiple partitions in
  Kafka sinks ([#15609](https://github.com/MaterializeInc/materialize/issues/15609)). Previously, the sink would use the default
  Kafka cluster configuration also for pre-existing
  topics, instead of the user-configured number of partitions.

* Improve ordering for joins that have filters applied to their inputs. This
  leads to an order of magnitude performance improvement in cases with highly
  selective filters ([#15120](https://github.com/MaterializeInc/materialize/issues/15120)).

* Treat some errors as transient instead of fatal in the [PostgreSQL source](/sql/create-source/postgres/).
  Errors that would previously set the source into an error state will now retry
  ([#15200](https://github.com/MaterializeInc/materialize/issues/15200)).

* Allow users to create indexes on system objects to optimize the performance of
  [troubleshooting](/ops/troubleshooting/) queries.

* Include indexes created on system objects when running the [`SHOW INDEXES`](/sql/show-indexes)
  command if the `IN CLUSTER` clause is specified.

* Add a `TPCH` [load generator source](/sql/create-source/load-generator/#tpch),
  which implements the TPC-H benchmark specification.

<!-- mz-docs page: releases/v0.30 -->

# Materialize v0.30
## v0.30.0

* Fix a bug that could cause updates in [sinks](/sql/create-sink) to appear as
  two separate records, instead of consolidated into a single update record ([#15748](https://github.com/MaterializeInc/materialize/issues/15748)). Previously, updates for multiple keys that occurred at the same
  timestamp would either emit a deletion tombstone followed by a record with the
  new value (`ENVELOPE UPSERT`), or a `{"before": "OLDVALUE", "after": null}`
  record followed by a `{"before": null, "after": "NEWVALUE"}` record (`ENVELOPE
  DEBEZIUM`).

* Improve error message for unsupported types in the
  [PostgreSQL source](/sql/create-source/postgres/), specifying the table and
  column containing an unsupported type:

  ```mzsql
  CREATE SOURCE pg_source
	FROM POSTGRES CONNECTION pg_connection (PUBLICATION 'mz_source')
	FOR ALL TABLES
	WITH (SIZE = '3xsmall');

	ERROR:  column "person.current_mood" uses unrecognized type
	DETAIL:  type with OID 211538 is unknown
	HINT:  You may be using an unsupported type in Materialize, such as an enum. Try excluding the table from the publication.
  ```

  Fine-grained control for casting unsupported types into valid
  [Materialize types](/sql/types/) is a work in progress ([#15716](https://github.com/MaterializeInc/materialize/issues/15716)).

* When using both signed and unsigned integers as inputs to a function, cast the
  inputs to a larger lossless type rather than [`double`](/sql/types/float). For
  example, when determining equality between [`integer`](/sql/types/integer)
  (32-bit signed integer) and [`uint4`](/sql/types/uint) (32-bit unsigned
  integer), both values are now cast to [`bigint`](/sql/types/integer)
  (64-bit signed integer). Previously both values would be cast to
  [`double`](/sql/types/double) (64-bit floating point number).

* Improve the performance of DDL statements, especially when many DDL statements
  are run within the same 24 hour period.

* Add an `xlarge` size for sources and sinks.

<!-- mz-docs page: releases/v0.31 -->

# Materialize v0.31
## v0.31.0

* **Breaking change.** Fix a bug that caused `NULLIF` to be incorrectly
    converted to `COALESCE` ([#15943](https://github.com/MaterializeInc/materialize/issues/15943)). Existing views and materialized
    views using `NULLIF` must be manually dropped and recreated.

* Include the replica status in the output of [`SHOW CLUSTER REPLICAS`](/sql/show-cluster-replicas/)
  as a new column named `ready`, which indicates if a cluster replica is
  online (`t`) or not (`f`).

* Improve the output of [`EXPLAIN PLAN`](/sql/explain-plan/) to make the printing of index
  lookups consistent regardless of whether the explained query uses the fast
  path or not. For both cases, the output will look similar to:

  ```nofmt
  ReadExistingIndex materialize.public.t1 lookup values [("l2"); ("l3")]
  ```

* Fix a bug where subsources were counted towards resource limits for existing
  sources ([#15958](https://github.com/MaterializeInc/materialize/issues/15958)). This resulted in an error for users of the PostgreSQL
  source if the number of replicated tables exceeded the default value for
  `max_sources` (25).

<!-- mz-docs page: releases/v0.32 -->

# Materialize v0.32
## v0.32.0

* Add support for replicating tables that contain unsupported types in the
  [PostgreSQL source](/sql/create-source/postgres/), using the new `TEXT
  COLUMNS` option:

  ```mzsql
  CREATE SOURCE mz_source
	FROM POSTGRES CONNECTION pg_connection (
	  PUBLICATION 'mz_source',
	  TEXT COLUMNS (tbl.col_of_unsupported_type)
	) FOR ALL TABLES
  WITH (SIZE = '3xsmall');
  ```

  Any columns specified via this option will be treated as `text` in
  Materialize regardless of the original PostgreSQL type. Examples of
  unsupported types that can now be ingested are `enum`,
  arbitrary precision `numeric`, `money`, and `citext`.

* Improve error message for unexpected or mismatched type catalog errors,
  specifying the catalog item type:

  ```mzsql
  DROP VIEW mz_table;

  ERROR:  "materialize.public.mz_table" is a table not a view
  ```

* Fix a bug in the [`#>>` `jsonb` operator](/sql/types/jsonb/#operators) that
  caused an error when specifying an array index that does not exist, instead
  of returning `NULL` ([#15978](https://github.com/MaterializeInc/materialize/issues/15978)).

* Fix a bug where relations in `pg_catalog` and `information_schema` would
  contain information about all databases, rather than just the current
  database ([#15841](https://github.com/MaterializeInc/materialize/issues/15841)).

* **Private preview.** Add support for
  [AWS PrivateLink connections](/sql/create-connection/#aws-privatelink),
  which establish links to
  [AWS PrivateLink](https://aws.amazon.com/privatelink/) services.

## Patch releases

### v0.32.4

* Stabilize the performance of ad hoc `SELECT` statements against unindexed
  objects in large clusters ([#16090](https://github.com/MaterializeInc/materialize/issues/16090)).

* Fix a bug that caused query performance on unindexed objects to slowly degrade
  over time ([#16127](https://github.com/MaterializeInc/materialize/issues/16127)).

* Fix a bug in predicate pushdown that could result in incorrect query plans ([#16147](https://github.com/MaterializeInc/materialize/issues/16147)).

<!-- mz-docs page: releases/v0.33 -->

# Materialize v0.33
## v0.33.0

* Add support for connecting to Kafka brokers using an [SSH tunnel connection](/sql/create-connection/#ssh-tunnel)
to an SSH bastion server.

  ```mzsql
  CREATE CONNECTION kafka_connection TO KAFKA (
    BROKERS (
      'broker1:9092' USING SSH TUNNEL ssh_connection,
      'broker2:9092' USING SSH TUNNEL ssh_connection
      )
  );
  ```

* Add [`mz_internal.mz_source_status`](/sql/system-catalog/mz_internal/#mz_source_statuses) and
  [`mz_internal.mz_source_status_history`](/sql/system-catalog/mz_internal/#mz_source_status_history)
  to the system catalog. These objects respectively expose the current
  and historical state for each source in the system, including potential
  error messages and additional metadata helpful for debugging.

* Add [`mz_internal.mz_cluster_replica_metrics`](https://materialize.com/docs/sql/system-catalog/mz_internal/#mz_cluster_replica_metrics) to the system
  catalog. This table records the last known CPU and RAM utilization statistics
  for all processes of all extant cluster replicas.

<!-- mz-docs page: releases/v0.36 -->

# Materialize v0.36
## v0.36.0

* Add `mz_internal.mz_sink_status` and `mz_internal.mz_sink_status_history`
  to the system catalog. These objects respectively expose the current and
  historical state for each sink in the system, including potential error
  messages and additional metadata helpful for debugging.

* Add `mz_internal.mz_cluster_replica_sizes`
  to the system catalog. This table provides a mapping of logical sizes
  (e.g. `xlarge`) to the number of processes, as well as CPU and memory
  allocations for each process. To monitor the resource utilization for
  all extant cluster replicas as a % of the total allocation, you can now
  use:

  ```mzsql
  SELECT
    r.id AS replica_id,
    m.process_id,
    m.cpu_nano_cores / s.cpu_nano_cores * 100 AS cpu_percent,
    m.memory_bytes / s.memory_bytes * 100 AS memory_percent
  FROM mz_cluster_replicas AS r
  JOIN mz_internal.mz_cluster_replica_sizes AS s ON r.size = s.size
  JOIN mz_internal.mz_cluster_replica_metrics AS m ON m.replica_id = r.id;
  ```

  It's important to note that these tables are part of an unstable interface of
  Materialize (`mz_internal`), which means that their values may change at any
  time, and you should not rely on them for tasks like capacity planning for the
  time being.

* Add `mz_catalog.mz_aws_privatelink_connections` to the system catalog. This
  table contains a row for each [AWS PrivateLink connection](/sql/create-connection/#aws-privatelink)
  in the system, and allows you to retrieve the AWS principal that
  Materialize will use to connect to the VPC endpoint.

* Return an error rather than crashing if the value of the `AVRO KEY FULLNAME`
  or `AVRO VALUE FULLNAME` option in an Avro-formatted Kafka sink is not a
  valid Avro name ([#16433](https://github.com/MaterializeInc/materialize/issues/16433)).

* Return the current timestamp of the `EpochMillis` timeline when the `mz_now
  ()` function is used outside the context of a specific timeline, such as
  `SELECT mz_now();`. The old behavior was to return [`u64::MAX`](https://doc.rust-lang.org/std/primitive.u64.html#associatedconstant.MAX).

## Patch releases

### v0.36.2

* Fix incorrect decoding of negative timestamps (i.e. prior to the Unix epoch:
  January 1st, 1970 at 00:00:00 UTC) in Avro records ([#16609](https://github.com/MaterializeInc/materialize/issues/16609)).

<!-- mz-docs page: releases/v0.37 -->

# Materialize v0.37
## v0.37.0

* Add support for connecting to Confluent Schema Registry using an
  [SSH tunnel](/sql/create-connection/#ssh-tunnel) connection to an SSH bastion
  server.

* Add [`mz_internal.mz_cluster_replica_utilization`](/sql/system-catalog/mz_internal/#mz_cluster_replica_utilization)
  to the system catalog. This view allows you to monitor the resource utilization for
  all extant cluster replicas as a % of the total resource allocation:

  ```mzsql
  SELECT * FROM mz_internal.mz_cluster_replica_utilization;
  ```

  ```nofmt
    replica_id | process_id |     cpu_percent      |    memory_percent
   ------------+------------+----------------------+----------------------
    1          | 0          |            9.6629961 |   0.6772994995117188
    2          | 0          |  0.10735560000000001 |   0.3876686096191406
    3          | 0          |           46.8730398 |      0.7110595703125
  ```

  It's important to note that these tables are part of an unstable interface of
  Materialize (`mz_internal`), which means that their values may change at any
  time, and you should not rely on them for tasks like capacity planning for the
  time being.

* Add `mz_internal.mz_storage_host_metrics` and
  `mz_internal.mz_storage_host_sizes` to the system catalog. These objects
  respectively expose the last known CPU and RAM utilization statistics for all
  processes of all extant storage hosts, and a mapping of logical sizes
  (e.g. `xlarge`) to the number of processes, as well as CPU and memory
  allocations for each process.

  The concept of a storage host is not user-facing, and is intentionally
  undocumented. It refers to the physical resource allocation on which
  Materialize can schedule multiple sources and sinks behind the scenes.

* Rename system catalog objects to adhere to the naming conventions defined in
  the Materialize [SQL style guide](https://github.com/chaas/materialize/blob/main/doc/developer/style.md).
  The affected objects are:

  | Schema        | Old name           | New name           |
  | ------------- | ------------------ | --------------------- |
  | `mz_internal` | `mz_source_status` | `mz_source_statuses` |
  | `mz_internal` | `mz_sink_status`   | `mz_sink_statuses`   |

* Support `JSON` as an output format of [`EXPLAIN TIMESTAMP`](https://materialize.com/docs/sql/explain-timestamp/).

* Fix a bug where the `to_timestamp` function would truncate the fractional part
  of negative timestamps (i.e. prior to the Unix epoch: January 1st, 1970 at
  00:00:00 UTC) ([#16610](https://github.com/MaterializeInc/materialize/issues/16610)), and return an error instead of `NULL` when the
  timestamp is out of range. The new behavior matches PostgreSQL.

* **Private preview.** Add a [WebSocket API endpoint](/serve-results/websocket-api/)
	which supports interactive SQL queries over WebSockets.

* Change the JSON serialization for rows emitted by the [HTTP API endpoint](/serve-results/http-api/)
  to exactly match the JSON serialization used by `FORMAT JSON` Kafka sinks.
  Previously, the HTTP SQL endpoint serialized datums using slightly different
  rules.

<!-- mz-docs page: releases/v0.38 -->

# Materialize v0.38
## v0.38.0

* Add `cpu_percent_normalized` to the `mz_internal.mz_{source,sink,cluster_replica}_utilization`
  system catalog views. This column provides an approximation of CPU utilization
  as a % of the total of compute workers.

* Add `mz_internal.mz_cluster_replica_frontiers`
  to the system catalog. This table describes the frontiers of each
  dataflow in the system.

* **Private preview.** Support the [`AS OF`](/sql/subscribe/#as-of) and [`UP TO`](/sql/subscribe/#up-to)
  clauses in `SUBSCRIBE`. These clauses allow specifying a timestamp at
  which `SUBSCRIBE` should begin returning results (`AS OF`), or cease
  running (`UP TO`).

  As is, all user-defined sources and tables have a retention window of one
  second, so `AS OF` is of limited use beyond subscribing to queries over
  specific system catalog objects (including `mz_cluster_replicas`,
  `mz_sources`, `mz_sinks`, `mz_internal.mz_cluster_replica_metrics`, and
  `mz_internal.mz_cluster_replica_sizes`).

<!-- mz-docs page: releases/v0.39 -->

# Materialize v0.39
## v0.39.0

* Add `mz_internal.mz_source_statistics` to the system catalog. This table
  contains statistics for each process of each source in the system, like the
  number of messages and bytes received from the upstream external system.

* Add `mz_internal.mz_object_dependencies` to the system catalog. This table
  describes the dependency structure between all objects in Materialize. As an
  example, you can now get an overview of the relationship between user-defined
  objects using:

  ```mzsql
  SELECT
    object_id,
	o.name,
	o.type,
	referenced_object_id,
	ro.name,
	ro.type
  FROM mz_internal.mz_object_dependencies
  JOIN mz_objects o ON object_id = o.id
  JOIN mz_objects ro ON referenced_object_id = ro.id
  WHERE o.id LIKE 'u%' AND ro.id NOT LIKE 's%'
  ORDER BY o.name DESC, ro.name ASC;
  ```

  It's important to note that these tables are part of an unstable interface of
  Materialize (`mz_internal`), which means that their values may change at any
  time, and you should not rely on them for tasks like capacity planning for
  the time being.

* Add an `mz_version` system configuration parameter, which reports the
  Materialize version information. The value of this parameter is the same as
  the value returned by the existing `mz_version()` function, but the parameter
  form can be more convenient for downstream applications.

  ```mzsql
  SHOW mz_version;
  ```

  ```nofmt
         mz_version
   ---------------------
   v0.39.2 (e6af8921b)
  ```

* Automatically create a linked cluster associated with each source and sink.
  The mappings between sources/sinks and their respective linked cluster are
  exposed in the `mz_internal.mz_cluster_links` system catalog table.

  The concept of a linked cluster is not user-facing, and is intentionally
  undocumented. Linked clusters are meant to preserve the soon-to-be legacy
  interface for sizing sources and sinks, where a `SIZE` parameter is specified
  on the source/sink rather than the cluster replica.

* Add the `IDLE ARRANGEMENT MERGE EFFORT` advanced option to `CREATE CLUSTER
  REPLICA`, which enables configuring the amount of effort a replica exerts on
  compacting arrangements during idle periods.

* **Private preview.** Support [bearer token authentication](/serve-results/websocket-api/#endpoint)
  in the WebSocket API endpoint, which supports interactive SQL queries over WebSockets.

<!-- mz-docs page: releases/v0.40 -->

# Materialize v0.40
## v0.40.0

* Allow configuring an `AVAILABILITY ZONE` option for each broker when creating
  a Kafka connection using [AWS PrivateLink](/sql/create-connection/#kafka-network-security):

  ```mzsql
  CREATE CONNECTION privatelink_svc TO AWS PRIVATELINK (
      SERVICE NAME 'com.amazonaws.vpce.us-east-1.vpce-svc-0e123abc123198abc',
      AVAILABILITY ZONES ('use1-az1', 'use1-az4')
  );

  CREATE CONNECTION kafka_connection TO KAFKA (
      BROKERS (
          'broker1:9092' USING AWS PRIVATELINK privatelink_svc (AVAILABILITY ZONE 'use1-az1'),
          'broker2:9092' USING AWS PRIVATELINK privatelink_svc (
            AVAILABILITY ZONE 'use1-az4',
            PORT 9093
          )
      )
  );
  ```

  Specifying the correct availability zone for each broker allows Materialize to
  be more efficient with its network connections. Without the `AVAILABILITY
  ZONE` option, when Materialize initiates a connection to a Kafka broker, it
  must attempt to connect to each availability zone in sequence to determine
  which availability zone the broker is running in. With the `AVAILABILITY
  ZONE` option, Materialize can connect immediately to the correct availability
  zone.

<!-- mz-docs page: releases/v0.41 -->

# Materialize v0.41
## v0.41.0

* Add [`mz_internal.mz_sink_statistics`](/sql/system-catalog/mz_internal/#mz_sink_statistics)
  to the system catalog. This table contains statistics for each
  process of each sink in the system, like the number of messages
  and bytes committed to the external system.

* Add [`mz_internal.mz_postgres_sources`](/sql/system-catalog/mz_internal/#mz_postgres_sources)
  to the system catalog. This table exposes the randomly-generated
  name of the replication slot created in the upstream PostgreSQL
  database that Materialize will create for each source.

    ```mzsql
    SELECT * FROM mz_internal.mz_postgres_sources;

       id   |             replication_slot
    --------+----------------------------------------------
     u8     | materialize_7f8a72d0bf2a4b6e9ebc4e61ba769b71
    ```

* Allow placing sources and sinks in existing clusters using the `IN CLUSTER`
  clause in [`CREATE SOURCE`](/sql/create-source) and [`CREATE SINK`](/sql/create-sink)
  statements, as an alternative to provisioning dedicated
  resources via the `SIZE` parameter.

  **New syntax**

  ```mzsql
  CREATE SOURCE kafka_connection
    IN CLUSTER quickstart
    FROM KAFKA CONNECTION qck_kafka_connection (TOPIC 'test_topic')
    FORMAT AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION csr_connection
    ENVELOPE DEBEZIUM;
  ```

  It's important to note that clusters containing sources and sinks can have at
  most one replica, and may contain any number of indexes and materialized
  views *or* any number of sources and sinks, but not both types of objects.
  These restrictions will be removed in a future release.

* Support using [`SUBSCRIBE`](/sql/subscribe) with queries over introspection
  sources for [troubleshooting](/ops/troubleshooting/).

<!-- mz-docs page: releases/v0.42 -->

# Materialize v0.42
## v0.42.0

This release focuses on stabilization work and performance improvements. It does
not introduce any new user-facing features or bug fixes. 👷

<!-- mz-docs page: releases/v0.43 -->

# Materialize v0.43
## v0.43.0

* Limit the size of SQL statements to **1MB**. Statements that exceed this limit
  will be rejected.

* Add the `bool_and` and `bool_or` [aggregate functions](/sql/functions/#aggregate-functions),
  which compute whether a column contains all true values or at least one
  true value, respectively.

* Improve the output of `EXPLAIN [MATERIALIZED] VIEW $view_name` and `EXPLAIN
  PHYSICAL PLAN FOR [MATERIALIZED] VIEW $view_name` to print the name of the
  view. The output will now look similar to:

  ```mzsql
  EXPLAIN VIEW v;

      Optimized Plan
  ----------------------------------
   materialize.public.v:           +
     Filter (#0 = 1) AND (#3 = 3)  +
       Get materialize.public.data +
  ```

* Disallow `NATURAL JOIN` and `*` expressions in views that directly reference
  system objects. Instead, project the required columns and convert all
  `NATURAL JOIN`s to `USING` joins.

* Fix a bug where active [subscriptions](/sql/subscribe/) were not terminated when
  their underlying relations were dropped ([#17476](https://github.com/MaterializeInc/materialize/issues/17476)).

<!-- mz-docs page: releases/v0.44 -->

# Materialize v0.44
## v0.44.0

* Remove the `cpu_percent_normalized` column from the
  `mz_internal.mz_cluster_replica_utilization` system catalog view. CPU
  utilization metrics will be restored in a future release.

* Add the `timing` option to `EXPLAIN`. Using this option annotates the output
  with the time spent in optimization (including decorrelation), which is
  useful to detect performance regressions in internal benchmarking.

* Add a `MAX CARDINALITY` parameter to the `COUNTER` load generator source. If
  specified, the counter load generator will begin retracting the oldest
  emitted value for each new value it emits, once it has crossed the max
  cardinality threshold. This is useful for internal load testing.

<!-- mz-docs page: releases/v0.45 -->

# Materialize v0.45
## v0.45.0

#### Sources and sinks

* Expose source progress metadata as a subsource that can be used to
  monitor **ingestion progress**. The name of the progress subsource can be
  specified using the `EXPOSE PROGRESS AS` clause in `CREATE SOURCE`;
  otherwise, it will be named `<src_name>_progress` by default.

  **Example**

  ```mzsql
  -- Given a "purchases" Kafka source, a "purchases_progress"
  -- subsource is automatically created
  SELECT partition, "offset"
  FROM (
	    SELECT upper(partition)::uint8 AS partition, "offset"
	    FROM purchases_progress
  )
  WHERE partition IS NOT NULL;

   partition |  offset
  -----------+----------
   0         | 13645902
   1         | 13659722
   2         | 13656787
  ```

  For Kafka sources, the progress subsource returns the next possible offset to
  consume from the identified partitions, and for PostgreSQL sources it returns
  the last Log Sequence Number (LSN) consumed from the upstream replication
  stream.

#### SQL

* Improve the behavior of the `search_path` configuration parameter to match that of
  [PostgreSQL](https://www.postgresql.org/docs/current/ddl-schemas.html#DDL-SCHEMAS-PATH).
  You can now specify multiple schemas and Materialize will correctly resolve
  unqualified names by following the search path, as well as create objects in
  the first schema named (i.e. the _current schema_).

* Support `options` settings on connection startup. As an example, you can
now specify the cluster to connect to in the `psql` connection string:

  ```mzsql
  psql "postgres://user%40domain.com@host:6875/materialize?options=--cluster%3Dfoo"
  ```

* Add support for the `\du` meta-command, which lists all roles/users of the database.

* Add support for new SQL functions:

  | Function                                        | Description                                                             |
  | ----------------------------------------------- | ----------------------------------------------------------------------- |
  | [`ceiling`](/sql/functions/#numbers-functions)       | Works as an alias of the `ceil` function.                               |

<br>

* Remove the `CREATE USER` command, as well as the `LOGIN` and `SUPERUSER`
  attributes from the [`CREATE ROLE`](/sql/create-role/) command. This is part
  of the work to enable **Role-based access control** (RBAC) in a future release
  ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

#### Bug fixes and other improvements

* Improve the error message for naming collisions, specifying the catalog item
  type.

  **Example**

  ```mzsql
  CREATE VIEW foo AS SELECT 'bar';

  ERROR:  view "materialize.public.foo" already exists
  ```

* Fix a bug that would sporadically prevent clusters from coming online ([#17774](https://github.com/MaterializeInc/materialize/issues/17774)).

* Improve `SUBSCRIBE` error handling. Prior to this release, subscriptions
  ignored errors in their input, which could lead to correctness issues.

* Return an error rather than crashing if source data contains invalid
  retractions, which might happen in the presence of e.g. incomplete or invalid
  data ([#17709](https://github.com/MaterializeInc/materialize/issues/17709)).

* Fix a bug that could cause Materialize to crash when expressions in `CREATE
  TABLE ... DEFAULT` clauses or `INSERT ... RETURNING` clauses contained nested
  parentheses ([#17723](https://github.com/MaterializeInc/materialize/issues/17723)).

* Avoid panicking when attempting to parse a range from strings containing
  multibyte characters ([#17803](https://github.com/MaterializeInc/materialize/issues/17803)).

<!-- mz-docs page: releases/v0.46 -->

# Materialize v0.46
## v0.46.0

#### SQL

* Add [`mz_internal.mz_subscriptions`](/sql/system-catalog/mz_internal/#mz_subscriptions)
  to the system catalog. This table describes all active `SUBSCRIBE` operations
  in the system.

* Add support for new SQL functions:

  | Function                                        | Description                                                             |
  | ----------------------------------------------- | ----------------------------------------------------------------------- |
  | [`uuid_generate_v5`](/sql/functions/#uuid-functions) | Generates a UUID in the given namespace using the specified input name. |

* Add the `is_superuser` configuration parameter, which reports whether the
  current session is a _superuser_ with admin privileges. This is part of the
  work to enable **Role-based access control** (RBAC) in a future release ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

* Add the [`ALTER ROLE`](/sql/alter-role) command, as well as role attributes to
  the [`CREATE ROLE`](/sql/create-role/) command. This is part of the work to
  enable **Role-based access control** (RBAC)([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

  It's important to note that no role attributes or privileges will be
  considered when executing `CREATE ROLE` statements. These attributes will be
  saved and considered in a future release.

#### Bug fixes and other improvements

* Fix a bug that would cause the `mz_sources` and `mz_sinks` system tables to
  report the wrong size for a source after an `ALTER {SOURCE|SINK} ... SET
  (SIZE = ...)` command.

## Patch releases

### v0.46.1

* Stabilizate resource utilization in the [`mz_introspection`](/sql/show-clusters/#mz_catalog_server-system-cluster)
  system cluster.

<!-- mz-docs page: releases/v0.47 -->

# Materialize v0.47
## v0.47.0

#### SQL

* Add the [`GRANT ROLE`](/sql/grant-role) and [`REVOKE ROLE`](/sql/revoke-role)
  commands, which allow granting/revoking membership of one role to/from another
  role. This is part of the work to enable **Role-based access control** (RBAC)
  in a future release ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

* Allow rejecting user queries based on role attributes. This privilege is
  exclusive to _superusers_. This is part of the work to enable **Role-based
  access control** (RBAC) in a future release ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

* Add [`mz_internal.mz_dataflow_operator_parents`](/sql/system-catalog/mz_introspection/#mz_dataflow_operator_parents)
  to the system catalog. This view describes how operators are nested into
  scopes, by relating operators to their parent operators, which is useful for
  internal system observability.

* Add `dataflow_id` to the [`mz_compute_exports`](/sql/system-catalog/mz_introspection/#mz_compute_exports)
  introspection source. This introspection source describes the dataflows
  created by indexes, materialized views, and subscriptions in the system.

<!-- mz-docs page: releases/v0.48 -->

# Materialize v0.48
## v0.48.0

#### SQL

* Introduce **object owners**, who can manage privileges for other roles on
  each object in the system by adding or revoking grants. In this release,
  object owners have limited functionality and are assigned as follows:

  * All objects that exist at the time of a new Materialize deployment
    (including all system objects) are owned by the `mz_system` role.
  * All objects that predate the release are owned by the new `default_owner`
    role.
  * Any new object is owned by the user who created it.

  This is part of the work to enable **Role-based access control** (RBAC) in a
  future release ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

* Support specifying multiple roles in the [`GRANT ROLE`](/sql/grant-role) and
  [`REVOKE ROLE`](/sql/revoke-role) commands.

  ```mzsql
  -- Grant role
  GRANT data_scientist TO joe, mike;

  -- Revoke role
  REVOKE data_scientist FROM joe, mike;
  ```

  This is part of the work to enable **Role-based access control** (RBAC) in a
  future release ([#11579](https://github.com/MaterializeInc/materialize/issues/11579)).

* Add [`mz_internal.mz_sessions`](/sql/system-catalog/mz_internal/#mz_sessions)
  to the system catalog. This table describes all active sessions in the
  system.

#### Bug fixes and other improvements

* Fix a bug where subsources were created in the `public` schema instead of
  being correctly created in the same schema as the source ([#17868](https://github.com/MaterializeInc/materialize/issues/17868)).
  This resulted in confusing name resolution for users of the PostgreSQL and
  load generator sources.

[//]: # "NOTE(morsapaes) The `details` column was introduced in v0.47, but we
missed the release note then and it now fits a little cosier with the change
shipping in v0.48 -— so mentioning it here."

* Improve the error messages reported in `mz_internal.mz_{source|sink}_status_history`
  and `mz_internal.mz_{source|sink}_statuses` with more helpful pointers to
  troubleshoot Kafka sources and sinks ([#17805](https://github.com/MaterializeInc/materialize/issues/17805)). From this release, the
  `error` column reports the full error message, and other helpful suggestions
  are added under `details`.

* Stop silently ignoring `NULL` keys in sources using `ENVELOPE UPSERT` ([#6350](https://github.com/MaterializeInc/materialize/issues/6350)). The new behavior is to throw an error when trying to query the
  source. To recover an errored source, you must produce a record with a `NULL`
  value and a `NULL` key to the topic, to force a retraction. As an example,
  you can use [`kcat`](https://docs.confluent.io/platform/current/clients/kafkacat-usage.html) to
  produce an empty message:

  ```bash
  echo ":" | kcat -b $BROKER -t $TOPIC -Z -K: \
    -X security.protocol=SASL_SSL \
    -X sasl.mechanisms=SCRAM-SHA-256 \
    -X sasl.username=$KAFKA_USERNAME \
    -X sasl.password=<KAFKA_PASSWORD>
  ```

* Fix a bug that prevented the correct parsing of connection settings specified
  using the [`-c` option](https://www.postgresql.org/docs/current/app-psql.html)
  ([#18239](https://github.com/MaterializeInc/materialize/issues/18239)).

* Respect session settings even in the case where the first statement executed
  errors ([#18317](https://github.com/MaterializeInc/materialize/issues/18317)). Previously, such errors led to these settings being
  ignored.

