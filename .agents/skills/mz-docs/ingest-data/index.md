# Ingest data

Best practices for ingesting data into Materialize from external systems.

You can ingest data into Materialize from various external systems:

| Type | External system |
|------|-----------------|
| **Databases (CDC): native connectors** | [PostgreSQL](/ingest-data/postgres/) <br> [MySQL](/ingest-data/mysql/) <br> [SQL Server](/ingest-data/sql-server/) |
| **Databases (CDC): via the Kafka connector** | [CockroachDB](/ingest-data/cdc-cockroachdb/) (using changefeeds) <br> [MongoDB](/ingest-data/mongodb/) (using Debezium) |
| **Message brokers** | [Kafka](/ingest-data/kafka/) <br> [Redpanda](/sql/create-source/kafka) |
| **Webhooks** | [Amazon EventBridge](/ingest-data/webhooks/amazon-eventbridge/) <br> [Segment](/ingest-data/webhooks/segment/) <br> [HubSpot](/ingest-data/webhooks/hubspot/) <br> [RudderStack](/ingest-data/webhooks/rudderstack/) <br> [SnowcatCloud](/ingest-data/webhooks/snowcatcloud/) <br> [Stripe](/ingest-data/webhooks/stripe/)|

## Sources and clusters

Materialize ingests data from external systems using
[sources](/fundamentals/concepts/sources/). For the sources, you need to associate a
[cluster](/fundamentals/concepts/clusters/) to provide the compute resources needed to ingest
data.

> **Tip:** If possible, dedicate a cluster just for sources.

## Snapshotting

Snapshotting is the initial sync of a table's data. It reads from the upstream
system and writes the data into Materialize's storage. The initial snapshot is
committed to storage atomically, with all records assigned the same ingestion
timestamp.

### When snapshotting occurs

When snapshotting occurs depends on the syntax.

- With the legacy [`CREATE SOURCE ... FOR <ALL
  TABLES|TABLES|SCHEMAS>`](/sql/create-source/#legacy-syntax), you run a single
  statement to create both the source and the tables that ingest data.
  Snapshotting begins when you run the statement. For an existing source, the
  legacy [`ALTER SOURCE ... ADD SUBSOURCE`](/sql/alter-source/) starts the
  snapshotting for the added table.

- With the source-versioning syntax, you create the source and its tables
  separately using [`CREATE SOURCE ...`](/sql/create-source/#new-syntax) and
  [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/). Snapshotting begins when
  you run `CREATE TABLE ... FROM SOURCE`.

### Duration

Snapshot duration depends on:

- Volume of upstream data
- Size of the source's cluster
- Upstream capacity to serve the read, on top of its normal workload
- Network path between the upstream system and Materialize

In cloud environments, an instance's network and disk throughput are typically
capped by its instance type, so a busy or throughput-limited upstream, or a
constrained network path, can be the bottleneck regardless of the source
cluster's size.

For **upsert** sources, snapshotting can be especially resource-intensive
(compared to append-only), and large upsert sources can take hours to snapshot.

To reduce the operational burden of snapshotting on the upstream system and
ensure you are only bringing in the volume of data that you need in Materialize,
we recommend:

- If possible, running source creation operations during **off-peak hours** to
  minimize operational risk in both the upstream system and Materialize.

- **Limiting the volume of data** that is synced into Materialize on source
  creation. This will help speed up snapshotting, as well as make data
  exploration more lightweight. See [Limit the volume of
  data](#limit-the-volume-of-data) for best practices.

- **For upsert sources**, overprovisioning the source cluster for snapshotting,
  then right-sizing once the snapshot is complete and you have a better grasp on
  the steady-state resource needs of your upsert source(s). See [Best practices:
  Upsert sources](#upsert-sources).

### Parallelism

Materialize can parallelize snapshotting across the workers of the cluster
hosting the source.

- **PostgreSQL sources** are parallelized by table, i.e., different tables
  are read concurrently by different workers. On PostgreSQL 14 and later,
  Materialize additionally attempts to partition each table's read across
  workers. Tables that cannot be partitioned fall back to a single worker.

- **MySQL sources** are parallelized by table, i.e., different tables are
  read concurrently by different workers. For tables that meet certain
  requirements, Materialize can additionally partition the table's read
  across workers. See [MySQL snapshot
  parallelism](/ingest-data/mysql/snapshot-parallelism/).

- **Kafka sources** are parallelized by topic partition, with partitions
  distributed across workers, so parallelism is bounded by the topic's
  partition count.

- **SQL Server sources** are not parallelized: a single worker reads all
  tables.

The degree of snapshot parallelism depends on the number of workers. A
cluster's [size](/sql/create-cluster/#available-sizes) determines its number
of workers, so a larger cluster can shorten the snapshot, to the extent the
work parallelizes and the upstream database keeps up. The volume read from
the upstream database is unchanged, it is compressed into a shorter window
of more concurrent queries and connections. To determine whether
snapshotting is overloading the upstream database, and for ways to mitigate
the load, see [Is the upstream database
overloaded?](/ingest-data/troubleshooting/#is-the-upstream-database-overloaded)

### Monitoring progress

While snapshotting is taking place, you can monitor the progress of the
operation in the **overview page** for the source in the [Materialize
Console](/developer-tools/console/data/#sample-source-overview). Alternatively, you can manually
keep track of using information from the system catalog. See [Monitoring the
snapshotting
progress](/ingest-data/monitoring-data-ingestion/#monitoring-the-snapshotting-progress)
for guidance.

It's also important to **monitor CPU and memory utilization** for the cluster
hosting the source during snapshotting. If there are signs of resource
exhaustion, you may need to [resize the cluster](#use-a-larger-cluster-for-upsert-source-snapshotting).

### Queries during snapshotting

<!--
Syntax-specific (legacy and source-versioning) query behavior during
snapshotting. For the generic (syntax-agnostic) version, see
headless/ingestion/snapshotting-ingestion.md.
-->

Queries on a table that is snapshotting are blocked until its snapshot
completes.

- With the legacy `CREATE` syntax:

  - None of the subsources created as part of `CREATE SOURCE ... FOR ...` are
    queryable until they have all finished snapshotting.

  - When altering a source to add a new subsource (`ALTER SOURCE ... ADD
    SUBSOURCE`), only the new subsource snapshots. The source's other subsources
    remain queryable. **However**, ingestion for these subsources is temporarily
    blocked, so they stop advancing until the snapshot completes.

- With the source-versioning `CREATE TABLE FROM SOURCE` syntax:

  - None of the tables created within a [transaction
    block](/sql/begin/#ddl-only-transactions) are queryable until all their
    snapshots complete.

  - When you create new tables from a source that already has tables, only the
    new tables snapshot. The source's existing tables remain queryable.
    **However**, ingestion for the existing tables is temporarily blocked, so
    they stop advancing until the snapshots for the new tables complete.

### Modifying an existing source

<!--
Generic (syntax-agnostic) version of the "existing tables blocked" behavior.
Keep in sync with the syntax-specific version in
headless/ingestion/snapshotting-queries.md.
-->

When you create additional tables for a source that already has tables ingesting
data, ingestion for the existing tables is blocked while the new tables
snapshot. The existing tables remain queryable, but they stop advancing until
the new tables' snapshots complete.

If possible, resize the cluster to speed up the snapshot, then right-size it once
snapshotting completes.

## Running/steady-state

Once snapshotting completes, Materialize transitions to Running state. During
this state, Materialize continually ingests changes from the upstream system.

### Queries during steady-state

Although Materialize is continually ingesting changes from the upstream system,
depending on the volume of the upstream changes, Materialize may lag behind the
upstream system. If the lag is significant, queries may block until Materialize
has caught up sufficiently with the upstream system when using the default
[isolation level](/serve-results/isolation-level/) of [strict
serializability](/serve-results/isolation-level/#strict-serializable).

In the Materialize Console, you can see a source's data freshness from the
**Data Explorer** screen. Alternatively, you can run a query to monitor the lag.
See [Monitoring hydration/data freshness status](/ingest-data/monitoring-data-ingestion/#monitoring-hydrationdata-freshness-status).

## Hydration

Hydration is the reconstruction of an object's in-memory state by reading
from Materialize's storage layer and existing indexes; hydration does not
read from the upstream system.

When a cluster is restarted (such as after resizing), certain objects on that
cluster  (such as Kafka upsert sources, indexes, materialized views, and sinks)
undergo hydration. For the full list of events that trigger hydration and the
affected objects, see [Hydration](/fundamentals/concepts/hydration/).

> **Tip:** If possible, use a dedicated cluster just for sources. That is, avoid
> using the same cluster for sources and other objects, such as sinks, etc.
> See [Best practices](#best-practices) for more details.

### Process

During hydration, data from Materialize's storage layer is read to reconstruct
the in-memory state of the object. As part of the hydration process:

- Internal data structures are re-created.

- Various processes are re-initiated. These processes may also require
  re-reading of their in-memory state.

### Duration

For a source, the duration of its hydration depends on the type and the size
of the source; e.g., large `UPSERT` sources can take hours to complete.

### Queries during hydration

During hydration, queries usually block until the process has been completed.

## Best practices

The following lists some general best practice guidelines as well as additional
guidelines for upsert sources.

### Scheduling

If possible, schedule creating new sources during off-peak hours to mitigate
the impact of snapshotting on both the upstream system and the Materialize
cluster.

### Dedicate a cluster for the sources

If possible, dedicate a cluster just for sources. That is, avoid using the same
cluster for sources and sinks/indexes/materialized views (and other compute objects).

### Limit the volume of data

If possible, limit the volume of data that needs to be synced into Materialize
on source creation. This will help speed up snapshotting as well as make data
exploration more lightweight.

For example, when creating a PostgreSQL source, you may want to create a
publication with specific tables rather than for all tables in the database.

Once the data is in Materialize, you can further [reduce the size of the
data](/transform-data/optimization/#reduce-the-size-of-the-data) maintained by
your view definitions.

### Upsert sources

In addition to the general best practices, the following additional best
practices apply to upsert sources.

#### Use a larger cluster for upsert source snapshotting

When you create a new source, Materialize performs a one-time [snapshotting
operation](#snapshotting) to initially populate the source in Materialize. For
upsert sources, snapshotting is a resource-intensive operation that can require
a significant amount of CPU and memory.

Consider using a [larger cluster size](/sql/alter-cluster/#alter-cluster-size)
during snapshotting for upsert sources. Once the snapshotting operation is
complete, you can downsize the cluster to align with the steady-state ingestion.

If the cluster hosting the source restarts during snapshotting (e.g., because it
ran out of memory), you can scale up to a [larger
size](/sql/alter-cluster/#alter-cluster-size) to complete the operation.

```sql
ALTER CLUSTER <cluster_name> SET ( SIZE = <new_size> );
```

> **Note:** Resizing a cluster with sources requires the cluster to restart. This operation
> incurs downtime for the duration it takes for all objects in the cluster to
> [hydrate](/ingest-data/#hydration).
> You might want to let the new-sized replica hydrate before shutting down the
> current replica. See the [resizing
> process](/sql/alter-cluster/#resizing-process) about automating
> this process.

Once the initial snapshot has completed, you can resize the cluster for steady
state.

#### Right-size the cluster for steady-state

Once the initial snapshot has completed, you can
[resize](/sql/alter-cluster/#resizing)  the cluster
to align with the volume of changes being replicated from your upstream in
steady-state.

```sql
ALTER CLUSTER <cluster_name> SET ( SIZE = <new_size> );
```

> **Note:** Resizing a cluster with sources requires the cluster to restart. This operation
> incurs downtime for the duration it takes for all objects in the cluster to
> [hydrate](#hydration).
> You might want to let the new-sized replica hydrate before shutting down the
> current replica. See the [resizing
> process](/sql/alter-cluster/#resizing-process) about automating
> this process.

## See also

- [Monitoring data ingestion](/ingest-data/monitoring-data-ingestion)
- [Troubleshooting data ingestion](/ingest-data/troubleshooting)

## Pages in this section

- [Amazon EventBridge](/ingest-data/webhooks/amazon-eventbridge/index.md): How to stream data from Amazon EventBridge to Materialize using webhooks
- [AWS PrivateLink connections (Cloud-only)](/ingest-data/network-security/privatelink/index.md): How to connect Materialize Cloud to a Kafka broker, a Confluent Schema Registry server, a PostgreSQL database, or a MySQL database through an AWS PrivateLink service.
- [Change a webhook source's included headers](/ingest-data/webhooks/change-included-headers/index.md): Use ALTER SCHEMA ... SWAP WITH to change which headers a webhook source exposes, without changing the endpoint URL your senders use.
- [CockroachDB CDC using Kafka and Changefeeds](/ingest-data/cdc-cockroachdb/index.md): How to propagate Change Data Capture (CDC) data from a CockroachDB database to Materialize
- [Debezium](/ingest-data/debezium/index.md): How to propagate Change Data Capture (CDC) data from a database to Materialize using Debezium
- [Fivetran](/ingest-data/fivetran/index.md): How to use Fivetran to sync data into Materialize
- [HubSpot](/ingest-data/webhooks/hubspot/index.md): How to stream data from HubSpot to Materialize using webhooks
- [Ingestion performance](/ingest-data/performance/index.md): How Materialize sustains freshness and throughput during ingestion, with predictable load on upstream systems.
- [Kafka](/ingest-data/kafka/index.md): Connecting Materialize to a Kafka source.
- [MongoDB](/ingest-data/mongodb/index.md): Connecting Materialize to a MongoDB database for Change Data Capture (CDC).
- [Monitoring data ingestion](/ingest-data/monitoring-data-ingestion/index.md): How to monitor the snapshotting progress and data lag for your sources.
- [MySQL](/ingest-data/mysql/index.md): Connecting Materialize to a MySQL database for Change Data Capture (CDC).
- [Patterns](/ingest-data/patterns/index.md): Learn about common Materialize ingestion patterns.
- [PostgreSQL](/ingest-data/postgres/index.md): Connecting Materialize to a PostgreSQL database for Change Data Capture (CDC).
- [Redpanda](/ingest-data/redpanda/index.md): Get details about using Materialize with Redpanda
- [RudderStack](/ingest-data/webhooks/rudderstack/index.md): How to stream data from RudderStack to Materialize using webhooks
- [Segment](/ingest-data/webhooks/segment/index.md): How to stream data from Segment to Materialize using webhooks
- [SnowcatCloud](/ingest-data/webhooks/snowcatcloud/index.md): How to stream data from SnowcatCloud to Materialize using webhooks
- [SQL Server](/ingest-data/sql-server/index.md): Connecting Materialize to a SQL Server database for Change Data Capture (CDC).
- [SSH tunnel connections](/ingest-data/network-security/ssh-tunnel/index.md): How to connect Materialize to a Kafka broker, a MySQL database, or PostgreSQL database using an SSH tunnel connection to a SSH bastion server
- [Static IP addresses (Cloud-only)](/ingest-data/network-security/static-ips/index.md): Materialize Cloud provides static IP addresses that you can use to configure egress policies in your virtual networks that target outbound traffic to Materialize.
- [Striim Cloud](/ingest-data/striim/index.md): How to ingest Striim Change Data Capture (CDC) data into Materialize using the Kafka source
- [Stripe](/ingest-data/webhooks/stripe/index.md): How to stream data from Stripe to Materialize using webhooks
- [Troubleshooting](/ingest-data/troubleshooting/index.md): How to troubleshoot common data ingestion scenarios where Materialize is not working as expected.
- [Understand the lifecycle of a source](/ingest-data/lifecycle-of-a-source/index.md): The states a source and its tables move through, how to monitor each one, and the error states you might encounter.
- [Webhooks quickstart](/ingest-data/webhooks/webhook-quickstart/index.md): Learn and prototype with the webhook source without external deoendencies
