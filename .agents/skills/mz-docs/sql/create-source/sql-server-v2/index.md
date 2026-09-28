# CREATE SOURCE: SQL Server
Connecting Materialize to a SQL Server database for Change Data Capture (CDC).
> **Disambiguation:** This page reflects the new syntax which allows Materialize to handle upstream DDL changes, specifically adding or dropping columns, without downtime. For the deprecated syntax, see the [old reference page](/sql/create-source/sql-server/).

Creates a new source from SQL Server.  Materialize
supports creating sources from SQL Server version 2016&#43;.  Once a new source is created, you can <a href="/sql/create-table/" ><code>CREATE TABLE FROM SOURCE</code></a>
to create the corresponding tables in Materialize and start the data ingestion
process.

## Prerequisites

To create a source from SQL Server (2016+), you must first:

- Configure your SQL Server.
  - Enable [Change Data
Capture](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/enable-and-disable-change-data-capture-sql-server)
and [`SNAPSHOT` transaction
isolation](https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/sql/snapshot-isolation-in-sql-server)
for the database that you would like to replicate.
- [Create a connection to SQL
  Server](#prerequisite-creating-a-connection-to-sql-server) in Materialize.
  - The connection setup depends on your network security configuration.

> **Note:** The exact configuration steps depend on your SQL Server deployment. For
> step-by-step instructions, see the integration guides for
> [Azure SQL Database](/ingest-data/sql-server/azure-db/) and
> [self-hosted or managed SQL Server](/ingest-data/sql-server/self-hosted/).

## Syntax

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM SQL SERVER CONNECTION <connection_name>
[WITH ( <with_option> [, ...] )]

```

| Syntax element | Description |
| --- | --- |
| `<src_name>` | The name for the source.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a source with the same name already exists. Instead, issue a notice and skip the source creation.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this source.  |
| **CONNECTION** `<connection_name>` | The name of the SQL Server connection to use in the source. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection/#sql-server) documentation page.  |
| **WITH** (`<with_option>` [, ...]) | Optional. The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TIMESTAMP INTERVAL [=] <interval>` \| The interval at which timestamps are assigned to data read from this source. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). The value must be between the system parameters `min_timestamp_interval` and `max_timestamp_interval`. Default: the value of the `default_timestamp_interval` system parameter (`1s`). The interval can also be changed after creation with [`ALTER SOURCE`](/sql/alter-source/). \|  |

## Ingesting data

After a source is created, you can create tables from the source
upstream SQL Server database that have [Change Data Capture enabled](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server).
You can create multiple tables that reference the same table in the source.

See [`CREATE TABLE FROM SOURCE`](/sql/create-table/) for details.

#### Handling table schema changes

The use of the `CREATE SOURCE` with the new [`CREATE TABLE FROM
SOURCE`](/sql/create-table/) allows for the handling of certain upstream DDL
changes without downtime.

See [Handle upstream schema changes](/ingest-data/sql-server/source-versioning/) for details.

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

#### Supported types

With the new syntax, after a SQL Server source is created, you [`CREATE TABLE
FROM SOURCE`](/sql/create-table/) to create a corresponding table in
Matererialize and start ingesting data.

Materialize natively supports the following SQL Server types:

<ul style="column-count: 3"><li><code>tinyint</code></li><li><code>smallint</code></li><li><code>int</code></li><li><code>bigint</code></li><li><code>real</code></li><li><code>double precision</code></li><li><code>float</code></li><li><code>bit</code></li><li><code>decimal</code></li><li><code>numeric</code></li><li><code>money</code></li><li><code>smallmoney</code></li><li><code>char</code></li><li><code>nchar</code></li><li><code>varchar</code></li><li><code>varchar(max)</code></li><li><code>nvarchar</code></li><li><code>nvarchar(max)</code></li><li><code>sysname</code></li><li><code>binary</code></li><li><code>varbinary</code></li><li><code>json</code></li><li><code>date</code></li><li><code>time</code></li><li><code>smalldatetime</code></li><li><code>datetime</code></li><li><code>datetime2</code></li><li><code>datetimeoffset</code></li><li><code>uniqueidentifier</code></li></ul>

#### `char` and `nchar` columns

To preserve values exactly as SQL Server returns them, `char` and `nchar` columns
are replicated as `text` rather than fixed-length. SQL Server and Materialize
measure fixed-length character types differently, so replicating as text avoids
truncation and padding mismatches.

For more information, including strategies for handling unsupported types,
see [`CREATE TABLE FROM SOURCE`](/sql/create-table/).

### Monitoring source progress

[//]: # "TODO(morsapaes) Replace this section with guidance using the new
progress metrics in mz_source_statistics + console monitoring, when available
(also for PostgreSQL)."

By default, SQL Server sources expose progress metadata as a subsource that you
can use to monitor source **ingestion progress**. The name of the progress
subsource can be specified when creating a source using the `EXPOSE PROGRESS
AS` clause; otherwise, it will be named `<src_name>_progress`.

The following metadata is available for each source as a progress subsource:

Field     | Type                          | Details
----------|-------------------------------|--------------
`lsn`     | [`bytea`](/sql/types/bytea/)  | The upper-bound [Log Sequence Number](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-transaction-log-architecture-and-management-guide) replicated thus far into Materialize.

And can be queried using:

```mzsql
SELECT lsn
FROM <src_name>_progress;
```

The reported `lsn` should increase as Materialize consumes **new** CDC events
from the upstream SQL Server database. For more details on monitoring source
ingestion progress and debugging related issues, see [Troubleshooting](/ops/troubleshooting/).

## Handling upstream operations

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

## Source failure states and recovery

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

## Example

> **Important:** Before creating a SQL Server source, you must enable Change Data Capture and
> `SNAPSHOT` transaction isolation in the upstream database.

### Creating a source {#create-source-example}

#### Prerequisite: Creating a connection to SQL Server

First, you must create a connection to your SQL Server database. A connection describes how to connect and authenticate to an external system you
want Materialize to read data from.

Once created, a connection is **reusable** across multiple `CREATE SOURCE`
statements. For more details on creating connections, check the
[`CREATE CONNECTION`](/sql/create-connection/#sql-server) documentation page.

```mzsql
CREATE SECRET sqlserver_pass AS '<SQL_SERVER_PASSWORD>';

CREATE CONNECTION sqlserver_connection TO SQL SERVER (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    PORT 1433,
    USER 'materialize',
    PASSWORD SECRET sqlserver_pass,
    DATABASE '<DATABASE_NAME>'
);
```

If your SQL Server instance is not exposed to the public internet, you can
[tunnel the connection](/sql/create-connection/#network-security-connections)
through and SSH bastion host.

**SSH tunnel:**
```mzsql
CREATE CONNECTION ssh_connection TO SSH TUNNEL (
    HOST 'bastion-host',
    PORT 22,
    USER 'materialize',
    DATABASE '<DATABASE_NAME>'
);
```

```mzsql
CREATE CONNECTION sqlserver_connection TO SQL SERVER (
    HOST 'instance.foo000.us-west-1.rds.amazonaws.com',
    SSH TUNNEL ssh_connection,
    DATABASE '<DATABASE_NAME>'
);
```

For step-by-step instructions on creating SSH tunnel connections and configuring
an SSH bastion server to accept connections from Materialize, check
[this guide](/ops/network-security/ssh-tunnel/).

#### Creating the source in Materialize

You **must** enable Change Data Capture. See the setup instructions for
[Azure SQL Database](/ingest-data/sql-server/azure-db/#a-configure-azure-sql-database)
or [self-hosted SQL Server](/ingest-data/sql-server/self-hosted/#a-configure-sql-server).

Once CDC is enabled for all of the tables you wish to create subsources for, you can create a `SOURCE` in
Materialize to begin replicating data!

_Create source from the connection we just created_

```mzsql
CREATE SOURCE mz_source
    FROM SQL SERVER CONNECTION sqlserver_connection;
```

After a source is created, you can create a table from the source, referencing specific table(s).

_Creates a table in Materialize from the upstream table dbo.items_
```mzsql
CREATE TABLE items FROM SOURCE mz_source(REFERENCE dbo.items);
```

## Related pages

- [`CREATE SECRET`](/sql/create-secret)
- [`CREATE CONNECTION`](/sql/create-connection)
- [`CREATE SOURCE`](../)
