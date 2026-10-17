# PostgreSQL

Connecting Materialize to a PostgreSQL database for Change Data Capture (CDC).

## Change Data Capture (CDC)

Materialize supports PostgreSQL as a real-time data source. The
[PostgreSQL source](/sql/create-source/postgres/) uses PostgreSQL's
[replication protocol](/sql/create-source/postgres/#change-data-capture)
to **continually ingest changes** resulting from CRUD operations in the upstream
database. The native support for PostgreSQL Change Data Capture (CDC) in
Materialize gives you the following benefits:

* **No additional infrastructure:** Ingest PostgreSQL change data into
    Materialize in real-time with no architectural changes or additional
    operational overhead. In particular, you **do not need to deploy Kafka and
    Debezium** for PostgreSQL CDC.

* **Transactional consistency:** The PostgreSQL source ensures that transactions
    in the upstream PostgreSQL database are respected downstream. Materialize
    will **never show partial results** based on partially replicated
    transactions.

* **Incrementally updated materialized views:** Materialized views in PostgreSQL
    are computationally expensive and require manual refreshes. You can use
    Materialize as a read-replica to build views on top of your PostgreSQL data
    that are efficiently maintained and always up-to-date.

When a source is created, Materialize parallelizes the initial snapshot
across the cluster's workers and, on PostgreSQL 14 and later, splits each
table's read across workers. See [Snapshot
parallelism](/fundamentals/concepts/snapshotting/#parallelism).

### Supported versions and services

The PostgreSQL source requires **PostgreSQL 11+** and is compatible with most
common PostgreSQL hosted services.

### Integration guides

To help you get started, the following integration guides are available:

- [AlloyDB for PostgreSQL](/ingest-data/postgres/alloydb/)
- [Amazon Aurora for PostgreSQL](/ingest-data/postgres/amazon-aurora/)
- [Amazon RDS for PostgreSQL](/ingest-data/postgres/amazon-rds/)
- [Azure DB for PostgreSQL](/ingest-data/postgres/azure-db/)
- [Google Cloud SQL for PostgreSQL](/ingest-data/postgres/cloud-sql/)
- [Neon](/ingest-data/postgres/neon/)
- [Self-hosted PostgreSQL](/ingest-data/postgres/self-hosted/)

## Supported data types

### Supported types

<p>Materialize natively supports the following PostgreSQL types (including the
array type for each of the types):</p>
<ul style="column-count: 3"><li><code>bool</code></li><li><code>bpchar</code></li><li><code>bytea</code></li><li><code>char</code></li><li><code>date</code></li><li><code>daterange</code></li><li><code>float4</code></li><li><code>float8</code></li><li><code>int2</code></li><li><code>int2vector</code></li><li><code>int4</code></li><li><code>int4range</code></li><li><code>int8</code></li><li><code>int8range</code></li><li><code>interval</code></li><li><code>json</code></li><li><code>jsonb</code></li><li><code>numeric</code></li><li><code>numrange</code></li><li><code>oid</code></li><li><code>text</code></li><li><code>time</code></li><li><code>timestamp</code></li><li><code>timestamptz</code></li><li><code>tsrange</code></li><li><code>tstzrange</code></li><li><code>uuid</code></li><li><code>varchar</code></li></ul>

Replicating tables that contain **unsupported [data types](/sql/types/)** is
possible via the `TEXT COLUMNS` option. The specified columns will be
treated as `text`; i.e., will not have the expected PostgreSQL type
features. For example:

* [`enum`]: When decoded as `text`, the implicit ordering of the original
  PostgreSQL `enum` type is not preserved; instead, Materialize will sort values
  as `text`.

* [`money`]: When decoded as `text`, resulting `text` value cannot be cast
back to `numeric`, since PostgreSQL adds typical currency formatting to the
output.

[`enum`]: https://www.postgresql.org/docs/current/datatype-enum.html
[`money`]: https://www.postgresql.org/docs/current/datatype-money.html

## How ingestion from PostgreSQL works

### Replication slots

Each source ingests the raw replication stream data for all tables in the
specified publication using **a single** replication slot. To manage
replication slots:

- For PostgreSQL 13+, set a reasonable value
for [`max_slot_wal_keep_size`](https://www.postgresql.org/docs/13/runtime-config-replication.html#GUC-MAX-SLOT-WAL-KEEP-SIZE)
to limit the amount of storage used by replication slots.

- If you stop using Materialize, or if either the Materialize instance or
the PostgreSQL instance crash, delete any replication slots. You can query
the `mz_internal.mz_postgres_sources` table to look up the name of the
replication slot created for each source.

- If you delete all objects that depend on a source without also dropping
the source, the upstream replication slot remains and will continue to
accumulate data so that the source can resume in the future. To avoid
unbounded disk space usage, make sure to use [`DROP
SOURCE`](/sql/drop-source/) or manually delete the replication slot.

### Snapshotting

The PostgreSQL source performs parallel snapshotting of tables by distributing rows among
workers using ranges of
[`CTID`](https://www.postgresql.org/docs/current/ddl-system-columns.html#DDL-SYSTEM-COLUMNS-CTID).
Materialize uses
[PostgreSQL statistics to estimate](https://www.postgresql.org/docs/current/row-estimation-examples.html)
the amount of data and number of rows to read. Missing or stale statistics can result in uneven
work distribution, reducing snapshot performance. They can also cause incorrect snapshot
progress reporting in the Console.

To avoid this situation, before creating the source in Materialize, ensure statistics are up to
date by running PostgreSQL `ANALYZE` command.

### Publication membership

PostgreSQL's logical replication API does not provide a signal when users
remove tables from publications. Because of this, Materialize relies on
periodic checks to determine if a table has been removed from a publication,
at which time it generates an irrevocable error, preventing any values from
being read from the table.

However, it is possible to remove a table from a publication and then re-add
it before Materialize notices that the table was removed. In this case,
Materialize can no longer provide any consistency guarantees about the data
we present from the table and, unfortunately, is wholly unaware that this
occurred.

To mitigate this issue, if you need to drop and re-add a table to a
publication, ensure that you remove the table/subsource from the source
_before_ re-adding it using the [`DROP SOURCE`](/sql/drop-source/) command.

### Inherited tables

When using [PostgreSQL table inheritance](https://www.postgresql.org/docs/current/tutorial-inheritance.html),
PostgreSQL serves data from `SELECT`s as if the inheriting tables' data is
also present in the inherited table. However, both PostgreSQL's logical
replication and `COPY` only present data written to the tables themselves,
i.e. the inheriting data is _not_ treated as part of the inherited table.

PostgreSQL sources use logical replication and `COPY` to ingest table data,
so inheriting tables' data will only be ingested as part of the inheriting
table, i.e. in Materialize, the data will not be returned when serving
`SELECT`s from the inherited table.

- If using legacy syntax [`CREATE SOURCE ... FOR
  ...`](/sql/create-source/postgres/):

  You can mimic PostgreSQL's `SELECT` behavior with inherited tables by
  creating a materialized view that unions data from the inherited and
  inheriting tables (using `UNION ALL`). However, if new tables inherit from
  the table, data from the inheriting tables will not be available in the
  view. You will need to add the inheriting tables via `ADD SUBSOURCE` and
  create a new view (materialized or non-) that unions the new table.

- If using new [`CREATE TABLE FROM SOURCE`](/sql/create-table/) syntax:

  You can mimic PostgreSQL's `SELECT` behavior with inherited tables by
  creating a materialized view that unions data from the inherited and
  inheriting tables (using `UNION ALL`). However, if new tables inherit from
  the table, data from the inheriting tables will not be available in the
  view. You will need to add the inheriting tables via `CREATE TABLE .. FROM
  SOURCE` and create a new view (materialized or non-) that unions the new
  table.

### Partitioned tables

When you add a [declaratively partitioned
table](https://www.postgresql.org/docs/current/ddl-partitioning.html) to a
publication, PostgreSQL expands it to the table's leaf partitions; the parent
table is not itself replicated. Materialize ingests one table per partition,
which you can reassemble into the parent table using `UNION ALL`.

Materialize does **not** support ingesting from a publication created with
[`publish_via_partition_root =
true`](https://www.postgresql.org/docs/current/sql-createpublication.html),
and doing so can produce incorrect results.

See [Ingest from partitioned
tables](/ingest-data/postgres/partitioned-tables/) for the supported
approaches, including how to add and remove partitions over time.

### Modifying an existing source

When you add a new subsource to an existing source ([`ALTER SOURCE ... ADD
SUBSOURCE ...`](/sql/alter-source/)), Materialize starts the snapshotting
process for the new subsource. During this snapshotting, the data ingestion for
the existing subsources for the same source is temporarily blocked. As such, if
possible, you can resize the cluster to speed up the snapshotting process and
once the process finishes, resize the cluster for steady-state.

## Supported schema and table changes

The following table summarizes how Materialize handles changes to an upstream
table it is ingesting. See the details below the table for the remediation for
each syntax.

| Change | Effect |
| --- | --- |
| Foreign key, `CHECK`, or `EXCLUSION` constraint changes | No impact: Materialize ignores these changes. |
| Dropping a column that is not ingested | No impact. |
| Adding a `NOT NULL`, `UNIQUE`, or `PRIMARY KEY` constraint | No impact. |
| [Adding a column](#adding-a-column) | Handled automatically. Materialize keeps ingesting the existing columns. To pick up the new column, create a new table (current syntax) or re-add the subsource (legacy syntax). |
| [Dropping an ingested column](#dropping-a-column) | Table enters an error state. Re-create the table. |
| [Renaming an ingested column](#renaming-a-column) | Table enters an error state. Re-create the table. |
| [Changing an ingested column's data type](#changing-a-columns-data-type) | Table enters an error state, unless the column is ingested as `text` via `TEXT COLUMNS`. Re-create the table. |
| [Dropping a `NOT NULL`, `UNIQUE`, or `PRIMARY KEY` constraint](#changing-constraints) that existed when the table was created | Table enters an error state. Re-create the table. |
| [Dropping, renaming, or moving a table](#table-level-operations) | Table enters an error state. Re-create the table. |
| [Removing a table from the publication](#table-level-operations) | Table enters an error state. Re-create the table. |
| [Setting a replica identity other than `FULL`](#table-level-operations) | Table enters an error state. Re-create the table. |
| [Truncating a table](#table-level-operations) | Table enters an error state. Use an unqualified `DELETE FROM` instead. |

This section describes how changes to upstream tables that Materialize ingests
affect the corresponding Materialize tables.

### Adding a column

When you add a new column to your upstream table, Materialize continues to
ingest only the existing columns.

To incorporate the new column:

- If using the new [`CREATE SOURCE` and `CREATE TABLE FROM
SOURCE`](/sql/create-source/postgres-v2/) syntax, create a new table from
the source. See [Handle upstream column addition](/ingest-data/postgres/source-versioning/#handle-upstream-column-addition).

- If using the legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/postgres/) syntax that creates subsources, use [`DROP
SOURCE`](/sql/drop-source/) to drop the affected subsource, and then add the
table back to the source using [`ALTER SOURCE ... ADD
SUBSOURCE`](/sql/alter-source/). The re-added subsource includes the new column.

### Dropping a column

Dropping columns that Materialize does not ingest (for example, columns added
after the source was created, or columns that are excluded) is supported. As
these columns were never ingested, you can drop them without issue.

If your Materialize source ingests a column, dropping that column from your
upstream table puts the affected table into an error state.

- If using the new [`CREATE SOURCE` and `CREATE TABLE FROM
SOURCE`](/sql/create-source/postgres-v2/) syntax, you can safely drop a
column by first ignoring it in Materialize. See [Handle upstream column
drop](/ingest-data/postgres/source-versioning/#handle-upstream-column-drop).

- If using legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/postgres/) syntax, use [`DROP SOURCE`](/sql/drop-source/) to drop the affected
subsource, and then add the table back to the source using [`ALTER
SOURCE ... ADD SUBSOURCE`](/sql/alter-source/).

### Changing constraints

Materialize ignores the following constraint changes: foreign
key, `CHECK`, and `EXCLUSION`.
As such, you can add or drop them without affecting ingestion.

Materialize also ignores `NOT NULL`, `UNIQUE`, and `PRIMARY KEY` constraints that
are added after the Materialize table is created (that is, the table was created
without them). Adding such a constraint, and later dropping it, does not affect
ingestion.

Dropping a `NOT NULL`, `UNIQUE`, or `PRIMARY KEY` constraint that existed when
the table was created puts the affected table into an error state.

If using the new [`CREATE SOURCE` and `CREATE TABLE FROM
SOURCE`](/sql/create-source/postgres-v2/) syntax, you can safely drop such a
constraint by first excluding it in Materialize. See [Handle upstream
constraint drop](/ingest-data/postgres/source-versioning/#handle-upstream-constraint-drop).
### Changing a column's data type

Changing an ingested column's data type upstream puts the affected
Materialize table into an error state unless the column was ingested as `text`
via the `TEXT COLUMNS` option. Ingestion for that table stops, and you must
drop and recreate the table in Materialize to resume ingestion.

### Renaming a column

Renaming a column that Materialize ingests puts the affected table into an error
state. Ingestion for that table stops, and you must drop and recreate the table
in Materialize to resume ingestion.

### Table-level operations

The following upstream operations put the affected table into an error state.
Ingestion for that table stops, and you must drop and recreate the affected
table in Materialize to resume:

- Dropping a table (`DROP TABLE`), or removing it from the publication (`ALTER PUBLICATION ... DROP TABLE`).
- Renaming a table or moving it to a different schema.
- Setting a table's replica identity to anything other than `FULL` (`ALTER TABLE ... REPLICA IDENTITY`).
- Truncating a table (`TRUNCATE`). To clear a table without putting it into an error state, use an unqualified `DELETE FROM t;` instead.

## Supported database operations

The following table summarizes how Materialize handles operational events on
the upstream PostgreSQL database. See the details below the table for the error
text and any required configuration.

| Operation | Resolution |
| --- | --- |
| Restarting or patching PostgreSQL (including OS-level restarts) | Supported automatically. |
| Restarting Materialize | Supported automatically. |
| Transient network interruptions between Materialize and PostgreSQL | Supported automatically. |
| Resizing the source cluster or changing its replication factor | Supported automatically. |
| The upstream database running out of disk space | Supported automatically, once space is freed. |
| [High-availability failover](#high-availability-failovers) | Requires re-creating the source. On self-managed Materialize, a configuration change can avoid this. |
| [Point-in-time restore](#point-in-time-restore) | Requires re-creating the source. |
| [Restoring from a volume or disk snapshot](#restoring-from-a-volume-or-disk-snapshot) | Not detected. Requires re-creating the source even though it keeps running. |
| [Promoting a physical replica](#promotion-of-a-physical-replica) | Requires re-creating the source. |
| [Replication slot invalidated](#replication-slot-invalidated) by WAL retention | Requires re-creating the source. |
| [Replication slot dropped or rewound](#replication-slot-dropped-or-rewound) | Requires re-creating the source. |
| [Dropping the publication](#dropping-the-publication) | Requires re-creating the source. |
| [Major version upgrades](#major-version-upgrades) | Requires re-creating the source. |

### Operations that do not require re-creating the source

Materialize tracks a [log sequence number
(LSN)](https://www.postgresql.org/docs/current/wal-internals.html) as it
consumes the upstream write-ahead log (WAL), and the source's replication slot
retains the WAL that Materialize has not yet consumed. Because the slot outlives
the connection, routine operational events do not lose data: after a transient
interruption the source stalls, then resumes from its committed LSN and catches
up automatically. **No action is required** for the following operations:

- Restarting or patching PostgreSQL (including OS-level restarts).
- Restarting Materialize. The source resumes from its committed LSN and does
  **not** re-snapshot already-ingested data.
- Transient network interruptions between Materialize and PostgreSQL. These
  surface as [`connection closed`](/ingest-data/postgres/connection-closed/).
- Resizing the cluster that hosts the source, or changing its replication
  factor. Briefly, the source may report [`replication slot ... is
  active`](/ingest-data/postgres/replication-slot-active/) while the upstream
  releases the slot from the previous connection.
- The upstream database running out of disk space, once space is freed.

> **Note:** Recovery after an interruption depends on the WAL that the replication slot is
> holding still being available upstream. An interruption long enough for the slot
> to be invalidated, or for the slot to be dropped, is not recoverable. See
> [Replication slot invalidated](#replication-slot-invalidated) and [Replication
> slot dropped or rewound](#replication-slot-dropped-or-rewound).

> **Warning:** While a source is disconnected, the upstream WAL accumulates behind its
> replication slot and cannot be reclaimed. A long outage, an undersized source
> cluster, or a source cluster stuck in a restart loop can therefore consume
> significant upstream disk. Monitor `restart_lsn` in
> [`pg_replication_slots`](https://www.postgresql.org/docs/current/view-pg-replication-slots.html)
> during planned maintenance.

### Operations that require re-creating the source

A smaller set of events breaks LSN continuity or destroys the replication slot.
When this happens, Materialize cannot guarantee a correct, gap-free view of your
data. Most of these put the **entire source** into an error or permanently
stalled state. One, [restoring from a volume or disk
snapshot](#restoring-from-a-volume-or-disk-snapshot), cannot be detected at all,
so the source keeps running on diverged data. Every event in this section
requires **re-creating** the source. Upstream changes to an individual table's
schema are handled separately, and do not error the entire source.

In each case below, the remediation is to drop and re-create the source:

```mzsql
DROP SOURCE mz_source CASCADE;

CREATE SOURCE mz_source
  FROM POSTGRES CONNECTION pg_connection (PUBLICATION 'mz_source');

-- Re-create the tables you were ingesting.
CREATE TABLE table_1 FROM SOURCE mz_source (REFERENCE public.table_1);
```

If you are using the legacy `CREATE SOURCE ... FOR TABLES` syntax, re-create the
source with the same `FOR TABLES` list instead of adding tables separately.

Because a re-created source snapshots from the current state of the upstream
database, any changes it missed while it was in an error state are reflected in
the snapshot rather than replayed as individual updates.

> **Warning:** `CASCADE` drops every object that depends on the source, including its tables,
> views, materialized views, indexes, and sinks. Capture their definitions before
> you run it, and re-create them once the new source has finished snapshotting.

#### Point-in-time restore

Restoring the source database from a backup, including restoring to a different
server for disaster recovery, increments the PostgreSQL timeline and is detected
as a discontinuity. The source fails with an error of the form:

```
unsupported action: database restored from point-in-time backup. Expected
timeline ID 8 but got 9
```

The same error covers other events that change the timeline, such as a managed
failover between replicas. To see the timeline a source is pinned to, query
[`mz_internal.mz_postgres_sources`](/sql/system-catalog/mz_internal/#mz_postgres_sources):

```mzsql
SELECT s.name, p.replication_slot, p.timeline_id
FROM mz_internal.mz_postgres_sources p
JOIN mz_catalog.mz_sources s ON s.id = p.id;
```

If your upstream fails over between replicas as part of routine maintenance, see
[High-availability failovers](#high-availability-failovers).

#### Restoring from a volume or disk snapshot

Restoring the upstream data directory from a crash-consistent volume or disk
snapshot rolls the database back, but preserves the timeline ID and the
replication slot. Materialize cannot detect this kind of restore. The source
keeps running without an error, but its contents diverge from upstream. This can
surface later as incorrect results, or as negative-accumulation errors in
queries such as `Non-positive multiplicity`.

> **Warning:** After any restore of this kind, drop and re-create the source even if it reports
> as `running`. Do not wait for the source to enter an error state, because it
> will not.

#### Promotion of a physical replica

When a source reads from a physical standby (read replica) rather than the
primary, promoting that standby to a primary fails the source with:

```
unsupported action: upstream physical replica status changed (e.g. a physical
replica was promoted to a primary). Expected pg_is_in_recovery()=true but got
false
```

Materialize detects the promotion while the replication stream is live, without
waiting for a restart. Re-create the source against the promoted node.

#### Replication slot invalidated

PostgreSQL invalidates a replication slot once the WAL it holds exceeds
[`max_slot_wal_keep_size`](https://www.postgresql.org/docs/current/runtime-config-replication.html#GUC-MAX-SLOT-WAL-KEEP-SIZE).
This protects the upstream from running out of disk, at the cost of ending
replication. The source fails with:

```
replication slot has been invalidated because it exceeded the maximum reserved
size
```

To avoid this, size the source cluster so that it keeps up with the upstream
write rate, and set `max_slot_wal_keep_size` high enough to cover your longest
expected outage. Some hosted PostgreSQL services set this value for you and do
not allow it to be raised.

#### Replication slot dropped or rewound

If the slot Materialize is using is dropped upstream, or the upstream is rebuilt
from a base backup (which does not carry replication slots), a new slot starts
at the current LSN, past the point the source needs to resume from. The source
stalls with:

```
slot overcompacted. Requested LSN ... but only LSNs >= ... are available
```

For diagnosis steps, see [Slot
overcompacted](/ingest-data/postgres/slot-overcompacted/). PostgreSQL refuses to
drop a slot that is in use, so this generally happens only while the source is
paused or disconnected.

Not every rewind is caught this way. A rewind that leaves the slot able to serve
the LSN the source asks for, such as [restoring from a volume or disk
snapshot](#restoring-from-a-volume-or-disk-snapshot), raises no error at all.

#### Dropping the publication

Running `DROP PUBLICATION` upstream stalls the source, and all of its tables,
with:

```
publication "mz_source" does not exist
```

Re-create the publication upstream, then re-create the source.

#### Major version upgrades

A PostgreSQL major version upgrade rewrites the on-disk format and does not
preserve the replication slot, so there is no in-place recovery. To upgrade without a gap in your downstream views, run a second source
against the upgraded instance in parallel and cut over once it has hydrated. See
[Upgrade the major version of your PostgreSQL
source](/ingest-data/postgres/major-version-upgrade/).

### High-availability failovers

Some managed PostgreSQL services increment the timeline during routine
high-availability operations, such as maintenance, a machine-tier change, or an
automatic failover between replicas. Materialize cannot distinguish these from a
genuine restore, so by default they fail the source with the [`Expected timeline
ID`](#point-in-time-restore) error.

On self-managed Materialize, where the upstream service guarantees that a
failover is a contiguous fork of the WAL with no data loss, you can disable
timeline validation with the
[`pg_source_validate_timeline`](/sql/alter-system-set/) system parameter:

```mzsql
ALTER SYSTEM SET pg_source_validate_timeline = false;
```

This parameter is not available on Materialize Cloud. There, a
high-availability failover that changes the timeline requires re-creating the
source.

> **Warning:** Disabling this check is a trade-off. With it off, Materialize also does **not**
> detect a genuine [point-in-time restore](#point-in-time-restore) or any other
> discontinuous timeline change, and silently ingesting across one can corrupt the
> contents of the source. Only disable it when your provider documents that its
> failovers preserve WAL continuity for logical replication subscribers, and
> re-create the source manually after any operation that does not.

## Pages in this section

- [FAQ: PostgreSQL sources](/ingest-data/postgres/faq/index.md): Frequently asked questions about PostgreSQL sources in Materialize
- [Guide: Ingest from a dedicated PostgreSQL replica](/ingest-data/postgres/logical-replica/index.md): How to point a Materialize PostgreSQL source at a dedicated logical replica instead of your production primary.
- [Guide: Ingest from partitioned tables](/ingest-data/postgres/partitioned-tables/index.md): How to ingest data from a declaratively partitioned PostgreSQL table into Materialize.
- [Guide: Upgrade the major version of your PostgreSQL source](/ingest-data/postgres/major-version-upgrade/index.md): How to upgrade the major version of the PostgreSQL database behind a Materialize source with zero downtime.
- [Handle upstream schema changes](/ingest-data/postgres/source-versioning/index.md): How to add a column, drop a column, or drop a constraint in your source PostgreSQL database, without any downtime in Materialize
- [Ingest data from AlloyDB](/ingest-data/postgres/alloydb/index.md): How to stream data from AlloyDB to Materialize
- [Ingest data from Amazon Aurora](/ingest-data/postgres/amazon-aurora/index.md): How to stream data from Amazon Aurora for PostgreSQL to Materialize
- [Ingest data from Amazon RDS](/ingest-data/postgres/amazon-rds/index.md): How to stream data from Amazon RDS for PostgreSQL to Materialize
- [Ingest data from Azure DB](/ingest-data/postgres/azure-db/index.md): How to stream data from Azure DB for PostgreSQL to Materialize
- [Ingest data from Google Cloud SQL](/ingest-data/postgres/cloud-sql/index.md): How to stream data from Google Cloud SQL for PostgreSQL to Materialize
- [Ingest data from Neon](/ingest-data/postgres/neon/index.md): How to stream data from Neon to Materialize
- [Ingest data from self-hosted PostgreSQL](/ingest-data/postgres/self-hosted/index.md): How to stream data from self-hosted PostgreSQL database to Materialize
- [PostgreSQL CDC using Kafka and Debezium](/ingest-data/postgres/postgres-debezium/index.md): How to propagate Change Data Capture (CDC) data from a PostgreSQL database to Materialize using Kafka and Debezium
- [Troubleshooting](/ingest-data/postgres/troubleshooting/index.md): Troubleshooting guides for PostgreSQL source errors in Materialize
- [Troubleshooting: Connection closed](/ingest-data/postgres/connection-closed/index.md): How to troubleshoot and resolve the connection closed error with PostgreSQL sources in Materialize
- [Troubleshooting: Replication slot is active](/ingest-data/postgres/replication-slot-active/index.md): How to troubleshoot and resolve the replication slot is active error with PostgreSQL sources in Materialize
- [Troubleshooting: Slot overcompacted](/ingest-data/postgres/slot-overcompacted/index.md): How to troubleshoot and resolve the slot overcompacted error with PostgreSQL sources in Materialize
- [Troubleshooting: Stuck snapshot](/ingest-data/postgres/stuck-snapshot/index.md): How to diagnose a PostgreSQL source whose snapshot stops making progress in Materialize
