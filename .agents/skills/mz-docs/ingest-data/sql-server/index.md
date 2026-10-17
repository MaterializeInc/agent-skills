# SQL Server

Connecting Materialize to a SQL Server database for Change Data Capture (CDC).

## Ingest from SQL Server via change data capture

Materialize supports SQL Server as a real-time data source. The [SQL Server source](/sql/create-source/sql-server/)
uses SQL Server's change data capture feature to **continually ingest changes**
resulting from CRUD operations in the upstream database. The native support for
SQL Server Change Data Capture (CDC) in Materialize gives you the following benefits:

* **No additional infrastructure:** Ingest SQL Server change data into Materialize in
    real-time with no architectural changes or additional operational overhead.
    In particular, you **do not need to deploy Kafka and Debezium** for SQL Server
    CDC.

* **Transactional consistency:** The SQL Server source ensures that transactions in
    the upstream SQL Server database are respected downstream. Materialize will
    **never show partial results** based on partially replicated transactions.

* **Incrementally updated materialized views:** Incrementally updated Materialized
    views are considerably **limited in SQL Server**, so you can use Materialize as
    a read-replica to build views on top of your SQL Server data that are
    efficiently maintained and always up-to-date.

### Supported versions

Materialize supports replicating data from SQL Server 2016 or higher with Change
Data Capture (CDC) support.

### Integration guides

- [Azure SQL Database](/ingest-data/sql-server/azure-db/)
- [Self-hosted SQL Server](/ingest-data/sql-server/self-hosted/)

## Supported data types

### Supported types

Materialize natively supports the following SQL Server types:

<ul style="column-count: 3"><li><code>tinyint</code></li><li><code>smallint</code></li><li><code>int</code></li><li><code>bigint</code></li><li><code>real</code></li><li><code>double precision</code></li><li><code>float</code></li><li><code>bit</code></li><li><code>decimal</code></li><li><code>numeric</code></li><li><code>money</code></li><li><code>smallmoney</code></li><li><code>char</code></li><li><code>nchar</code></li><li><code>varchar</code></li><li><code>varchar(max)</code></li><li><code>nvarchar</code></li><li><code>nvarchar(max)</code></li><li><code>sysname</code></li><li><code>binary</code></li><li><code>varbinary</code></li><li><code>json</code></li><li><code>date</code></li><li><code>time</code></li><li><code>smalldatetime</code></li><li><code>datetime</code></li><li><code>datetime2</code></li><li><code>datetimeoffset</code></li><li><code>uniqueidentifier</code></li></ul>

#### `char` and `nchar` columns

To preserve values exactly as SQL Server returns them, `char` and `nchar` columns
are replicated as `text` rather than fixed-length. SQL Server and Materialize
measure fixed-length character types differently, so replicating as text avoids
truncation and padding mismatches.

To replicate tables that contain the following unsupported data types, you can
use either the `TEXT COLUMNS` or the `EXCLUDE COLUMNS` option:

| Unsupported type | Supported option(s)                                         |
| ---------------- | ----------------------------------------------------------- |
| `text`           | `TEXT COLUMNS` (exposed as `varchar`) or `EXCLUDE COLUMNS`  |
| `ntext`          | `TEXT COLUMNS` (exposed as `nvarchar`) or `EXCLUDE COLUMNS` |
| `image`          | `EXCLUDE COLUMNS`                                           |
| `varbinary(max)` | `EXCLUDE COLUMNS`                                           |

### Timestamp rounding

The `time`, `datetime2`, and `datetimeoffset` types in SQL Server have a default
scale of 7 decimal places, or in other words a accuracy of 100 nanoseconds. But
the corresponding types in Materialize only support a scale of 6 decimal places.
If a column in SQL Server has a higher scale than what Materialize can support, it
will be rounded up to the largest scale possible.

```
-- In SQL Server
CREATE TABLE my_timestamps (a datetime2(7));
INSERT INTO my_timestamps VALUES
  ('2000-12-31 23:59:59.99999'),
  ('2000-12-31 23:59:59.999999'),
  ('2000-12-31 23:59:59.9999999');

-- Replicated into Materialize
SELECT * FROM my_timestamps;
'2000-12-31 23:59:59.999990'
'2000-12-31 23:59:59.999999'
'2001-01-01 00:00:00'
```

## How ingestion from SQL Server works

### Snapshot latency for inactive databases

When a new Source is created, Materialize performs a snapshotting operation to sync
the data. However, for a new SQL Server source, if none of the replicating tables
are receiving write queries, snapshotting may take up to an additional 5 minutes
to complete. The 5 minute interval is due to a hardcoded interval in the SQL Server
Change Data Capture (CDC) implementation which only notifies CDC consumers every
5 minutes when no changes are made to replicating tables.

See [Monitoring freshness status](/ingest-data/monitoring-data-ingestion/#monitoring-hydrationdata-freshness-status)

### Capture Instance Selection

When a new source is created, Materialize selects a capture instance for each
table. SQL Server permits at most two capture instances per table, which are
listed in the
[`sys.cdc_change_tables`](https://learn.microsoft.com/en-us/sql/relational-databases/system-tables/cdc-change-tables-transact-sql)
system table. For each table, Materialize picks the capture instance with the
most recent `create_date`.

If two capture instances for a table share the same timestamp (unlikely given the millisecond resolution), Materialize selects the `capture_instance` with the lexicographically larger name.

### Adding a table to an existing source

When you add a new subsource to an existing source ([`ALTER SOURCE ... ADD
SUBSOURCE ...`](/sql/alter-source/)), Materialize starts the snapshotting
process for the new subsource. During this snapshotting, the data ingestion for
the existing subsources for the same source is temporarily blocked. As such, if
possible, you can resize the cluster to speed up the snapshotting process and
once the process finishes, resize the cluster for steady-state.

## Supported schema and table changes

The following table summarizes how Materialize handles changes to an upstream
table it is ingesting. See the details below the table for recovery commands.

| Change | Effect |
| --- | --- |
| Foreign key or `CHECK` constraint changes | No impact: Materialize ignores these changes. |
| Dropping an excluded column | No impact. |
| [Adding a column](#adding-a-column) | Handled automatically. Materialize keeps ingesting the existing columns; incorporate the new column with a new table (current syntax) or by re-adding the subsource (legacy syntax). |
| [Dropping an ingested column](#dropping-a-column) | Table enters an error state. Re-create the table. |
| [Renaming an ingested column](#renaming-a-column) | Table enters an error state. Re-create the table. |
| Any [`ALTER COLUMN`](#changing-a-columns-data-type) (type, collation, sparseness, masking, nullability) | Table enters an error state. Re-create the table. |
| Dropping a `UNIQUE` constraint | Table enters an error state. Re-create the table. |
| [Disabling CDC on a table](#disabling-cdc-on-a-table) (`sys.sp_cdc_disable_table`) | Table enters an error state. Drop and re-create just that table; the rest of the source keeps replicating. |
| [Removing the in-use capture instance](#removing-a-capture-instance) | Table enters an error state. Re-create the table. |
| [Dropping or renaming a table, or moving it to another schema](#table-level-operations) | Table enters an error state. Re-create the table. |

This section describes how changes to upstream tables that Materialize ingests
affect the corresponding Materialize tables.

### Adding a column

When you add a new column to your upstream table, Materialize continues to
ingest only the existing columns.

To incorporate the new column:

- If using the new [`CREATE SOURCE` and `CREATE TABLE FROM
SOURCE`](/sql/create-source/sql-server-v2/) syntax, create a new table from
the source. See [Handle upstream column addition](/ingest-data/sql-server/source-versioning/#handle-upstream-column-addition).

- If using the legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/sql-server/) syntax that creates subsources, use [`DROP
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
SOURCE`](/sql/create-source/sql-server-v2/) syntax, you can safely drop a
column by first ignoring it in Materialize. See [Handle upstream column
drop](/ingest-data/sql-server/source-versioning/#handle-upstream-column-drop).

- If using legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/sql-server/) syntax, use [`DROP SOURCE`](/sql/drop-source/) to drop the affected
subsource, and then add the table back to the source using [`ALTER
SOURCE ... ADD SUBSOURCE`](/sql/alter-source/).

### Changing constraints

Materialize ignores foreign key and `CHECK` constraint changes. You can add or
drop them without affecting ingestion.

Adding a `UNIQUE` constraint does not affect ingestion. Dropping a `UNIQUE`
constraint puts the affected table into an error state.

SQL Server does not allow dropping a `PRIMARY KEY` from a table while change data
capture is enabled on it. A primary key that existed when Materialize began
ingesting the table therefore cannot be dropped upstream.

Adding or removing a `NOT NULL` constraint on an ingested column requires an
upstream `ALTER COLUMN`, which puts the affected table into an error state. See
[Changing a column's data type](#changing-a-columns-data-type).
### Changing a column's data type

Any upstream `ALTER COLUMN` on an ingested column puts the affected Materialize
table into an error state. This covers every `ALTER COLUMN` operation, not just
data-type changes. Changing a column's collation, sparseness, masking, or
nullability all error the table the same way. Ingestion for that table stops,
and you must drop and recreate the table in Materialize to resume ingestion.

### Renaming a column

Renaming a column that Materialize ingests puts the affected table into an error
state. Ingestion for that table stops, and you must drop and recreate the table
in Materialize to resume ingestion.

### Removing a capture instance

SQL Server allows up to two capture instances to exist for a table at once.
Materialize ingests from one of them.

Removing the capture instance that Materialize is using puts the affected table
into an error state. Removing a capture instance that Materialize is not using does not affect
ingestion.

### Disabling CDC on a table

Running `sys.sp_cdc_disable_table` removes the capture instance Materialize is
ingesting from, which puts the affected table into an error state. The other
tables in the source keep replicating. You can recover without re-creating the
whole source by dropping just the affected table in Materialize:

```mzsql
DROP TABLE table_1;
```

Then re-create it, optionally after re-enabling CDC on the upstream table with
`sys.sp_cdc_enable_table`.

### Table-level operations

The following upstream operations put the affected table into an error state.
Ingestion for that table stops, and you must drop and recreate the affected
table in Materialize to resume:

- Dropping a table (`DROP TABLE`).
- Renaming a table or moving it to a different schema.

## Supported database operations

The following table summarizes how Materialize handles operational events on
the upstream SQL Server database. See the details below the table for the
error text and any required configuration.

| Operation | Resolution |
| --- | --- |
| Restarting or patching SQL Server (including OS-level restarts) | Supported automatically. |
| Restarting Materialize | Supported automatically. |
| Transient network interruptions between Materialize and SQL Server | Supported automatically. |
| Taking the database `OFFLINE` and back `ONLINE` | Supported automatically. |
| Toggling `SINGLE_USER`/`MULTI_USER` or `READ_ONLY`/`READ_WRITE` | Supported automatically. |
| Data-file, filegroup, or index maintenance that rewrites data in place | Supported automatically. |
| [Availability group failover](#always-on-failovers) | Supported automatically, with a configuration change. |
| [Point-in-time restore](#point-in-time-restore) | Requires re-creating the source. |
| [CDC disabled at the database level](#cdc-disabled-at-the-database-level) | Requires re-creating the source. |
| [Change-table retention](#change-table-retention) exceeded during an outage | Requires re-creating the source. |

### Operations that do not require re-creating the source
For operations that are supported automatically, Materialize is able to resume
replication from a [log sequence number
(LSN)](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-log-architecture-and-management-guide)
that it tracks as it consumes the upstream change data capture (CDC) change
tables. Because LSNs live in the SQL Server transaction log, they survive
routine operational events: after a transient interruption the source stalls,
then resumes from its last committed LSN and catches up automatically. **No
action is required** for the operations in the first section below.

The source recovers on its own. It will briefly reports a `stalled` status while the
condition persists, then returns to `running` and catch up for all of the
following scenarios:

- Restarting or patching SQL Server (including OS-level restarts).
- Restarting Materialize. The source resumes from its tracked LSN and does
  **not** re-snapshot already-ingested data.
- Transient network interruptions between Materialize and SQL Server.
- Taking the database `OFFLINE` and back `ONLINE`.
- Toggling the database between `SINGLE_USER`/`MULTI_USER` or
  `READ_ONLY`/`READ_WRITE` (for example, during patching).
- Data-file, filegroup, or index maintenance that rewrites data in place.
- [Availability group failover](#always-on-failovers), with the
  configuration change described below.

> **Note:** Recovery after an interruption depends on the required LSNs still being present
> in the SQL Server CDC change tables. If the interruption lasts longer than the
> CDC **retention period** (3 days by default) and SQL Server's cleanup job
> removes change-table rows past the source's resume point, the source can no
> longer recover on its own. See [Change-table retention](#change-table-retention).

> **Warning:** If a maintenance script places the database into `SINGLE_USER` mode, note that an
> active Materialize source's reconnection attempts can occupy the single available
> connection and cause `ALTER DATABASE ... SET MULTI_USER` to fail with error 5064.
> Terminate the Materialize session (or use `SET MULTI_USER WITH ROLLBACK
> IMMEDIATE` after terminating it) before returning the database to multi-user
> mode.

### Operations that require re-creating the source
A smaller set of events breaks LSN or CDC-change-table continuity. When this
happens, Materialize cannot guarantee a correct, gap-free view of your data, so
it puts the **entire source** into an error state that requires **re-creating**
the source. Re-creating triggers a fresh [snapshot](/ingest-data/#snapshotting)
and rehydration of dependent objects. Upstream changes to an individual table's
schema are handled separately, and do not error the entire source.

The following events put the **entire source** into an error state. In each
case, the remediation is to drop and re-create the source:

```mzsql
DROP SOURCE mz_source CASCADE;

CREATE SOURCE mz_source
  FROM SQL SERVER CONNECTION sql_server_connection;

-- Re-create the tables you were ingesting.
CREATE TABLE table_1 FROM SOURCE mz_source (REFERENCE dbo.table_1);
```

#### Point-in-time restore

Restoring the source database from a backup — including restoring to a different
server for disaster recovery — is detected as a discontinuity. The source fails
with an error of the form:

```
source must be dropped and recreated due to failure: Restore history id changed
from None to Some(<n>)
```

Materialize detects the restore by reading `msdb.dbo.restorehistory`. (This check
does not apply to Azure SQL Database, which does not expose `msdb`.)

#### CDC disabled at the database level

Running `sys.sp_cdc_disable_db` drops all change tables. The source stalls with:

```
invalid SQL Server system setting 'database CDC'. Expected 'true'. Got 'Some(false)'.
```

Re-enable CDC on the database and on each table (`sys.sp_cdc_enable_db`,
`sys.sp_cdc_enable_table`), then re-create the source.

#### Change-table retention

SQL Server's CDC cleanup job removes change-table rows older than the retention
period (3 days by default). If Materialize is disconnected long enough that
cleanup removes rows past the source's resume LSN, the source stalls with:

```
the requested LSN '...' is less than the minimum '...' for `dbo_<table>`
```

To avoid this during a planned outage, keep the outage shorter than the retention
period, or increase retention beforehand with
[`sys.sp_cdc_change_job`](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-change-job-transact-sql)
(`@job_type = 'cleanup'`, `@retention`).

### Always-On failovers

Materialize supports SQL Server configured with Always On availability groups,
including failover between replicas, with one configuration change.

By default, an availability group failover is misdetected as a point-in-time
restore and fails the source with the `Restore history id changed` error
described above. This is a false positive: the LSN stream is continuous across an
availability group failover, but seeding a secondary replica writes rows to
`msdb.dbo.restorehistory`, which the restore-detection check reads as a restore.

To allow the source to survive failover, disable restore-history validation with
the [`sql_server_source_validate_restore_history`](/sql/alter-system-set/) system
parameter:

```mzsql
ALTER SYSTEM SET sql_server_source_validate_restore_history = false;
```

> **Warning:** Disabling this check is a trade-off: with it off, Materialize will also **not**
> detect a genuine [point-in-time restore](#point-in-time-restore) of the source
> database. Only disable it when the source connects to a database that fails over
> between availability group replicas.

With the check disabled, the source no longer fails on failover. Because `msdb`
is per-instance, the CDC capture and cleanup jobs do not move with the
availability group database — after a failover, confirm that CDC is healthy on
the new primary (the capture and cleanup jobs exist, SQL Server Agent is running,
and the change tables are advancing) so that replication continues. Adding the
jobs on a replica that lacks them is done with
[`sys.sp_cdc_add_job`](https://learn.microsoft.com/en-us/sql/relational-databases/system-stored-procedures/sys-sp-cdc-add-job-transact-sql).

## Pages in this section

- [Handle upstream schema changes](/ingest-data/sql-server/source-versioning/index.md): How to add a column, or drop a column, from your source SQL Server database, without any downtime in Materialize
- [Ingest data from Azure SQL Database](/ingest-data/sql-server/azure-db/index.md): How to stream data from Azure SQL Database to Materialize
- [Ingest data from self-hosted SQL Server](/ingest-data/sql-server/self-hosted/index.md): How to stream data from self-hosted SQL Server database to Materialize
