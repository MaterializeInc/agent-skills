# Snapshotting
Learn about snapshotting in Materialize: the initial sync of a source's data from an upstream system.
Snapshotting is the initial sync of a table's data. It reads from the upstream
system and writes the data into Materialize's storage. The initial snapshot is
committed to storage atomically, with all records assigned the same ingestion
timestamp.

## When snapshotting occurs

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

## Snapshot duration

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
  across workers <a class="private-preview-inline" href="https://materialize.com/preview-terms/">(feature in private preview)</a>
. See [MySQL snapshot
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

## Queries during snapshotting

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

## Impact on upstream system

Snapshotting has the following upstream impacts:

- **Read load.** Snapshotting puts read, CPU, and network load on the upstream
  system. The total load is proportional to the volume of data being
  snapshotted, while the source cluster's [parallelism](#parallelism) affects
  the peak load: more workers compress the reads into a shorter window.

- **Change-log retention for CDC database sources.** When ingesting data from
  CDC database sources (PostgreSQL, MySQL, SQL Server), the upstream system must
  retain its change-log data until Materialize consumes it. During the initial
  snapshot, changes accumulate from the source's starting position until the
  snapshot completes and Materialize has consumed the accumulated changes. A
  stalled or long-running snapshot can therefore increase disk usage on the
  upstream database.

## Related pages

- [Ingest data](/ingest-data/)
- [Sources](/concepts/sources/)
- [Troubleshooting data ingestion](/ingest-data/troubleshooting/)
