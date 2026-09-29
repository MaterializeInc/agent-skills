<!-- mz-docs page: sql/create-source/postgres-v2 -->

# CREATE SOURCE: PostgreSQL (New Syntax)
Creates a new source from PostgreSQL 11+.
> **Disambiguation:** This page reflects the new syntax which allows Materialize to handle upstream DDL changes, specifically adding or dropping columns, without downtime. For the deprecated syntax, see the [old reference page](/sql/create-source/postgres/).

Creates a new source from PostgreSQL.  Materialize
supports creating sources from PostgreSQL version 11&#43;.  Once a new source is created, you can <a href="/sql/create-table/postgres/" ><code>CREATE TABLE FROM SOURCE</code></a>
to create the corresponding tables in Materialize and start the data ingestion
process.

PostgreSQL 16+ is required for connecting Materialize to a physical replica.

## Prerequisites

To create a source from PostgreSQL 11+, you must first:

- **Configure upstream PostgreSQL instance**
  - Set up logical replication.
  - Create a publication.
  - Create a replication user and password for Materialize to use to connect.
- **Configure network security**
  - Ensure Materialize can connect to your PostgreSQL instance.
- **Create a connection to PostgreSQL in Materialize**
  - The connection setup depends on the network security configuration.

For details, see the [PostgreSQL integration
guides](/ingest-data/postgres/#integration-guides).

## Syntax

To create a source from an external PostgreSQL:

```mzsql
CREATE SOURCE [IF NOT EXISTS] <source_name>
[IN CLUSTER <cluster_name>]
FROM POSTGRES CONNECTION <connection_name> (PUBLICATION '<publication_name>')
[WITH ( <with_option> [, ...] )]
;

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if a source with the same name already exists. Instead, issue a notice and skip the source creation.  |
| `<source_name>` |  The name of the source to create. Names for sources must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| **IN CLUSTER** `<cluster_name>` | *Optional.* The [cluster](/sql/create-cluster) to maintain this source. Otherwise, the source will be created in the active cluster.  {{< tip >}} If possible, use a cluster dedicated just for sources. See also [Operational guidelines](/clusters/operational-guidelines/#sources). {{< /tip >}}  |
| `<connection_name>` | The name of the PostgreSQL connection to use for the source. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection/#postgresql) documentation page.  A connection is **reusable** across multiple `CREATE SOURCE` statements.  |
| `<publication_name>` | The name of the PostgreSQL publication to associate with the source. For details on creating a publication in your PostgreSQL database, see the [integration guides for your PostgreSQL](/ingest-data/postgres/#integration-guides).  |
| **WITH** (`<with_option>` [, ...]) | *Optional.* The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TIMESTAMP INTERVAL [=] <interval>` \| The interval at which timestamps are assigned to data read from this source. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). The value must be between the system parameters `min_timestamp_interval` and `max_timestamp_interval`. Default: the value of the `default_timestamp_interval` system parameter (`1s`). The interval can also be changed after creation with [`ALTER SOURCE`](/sql/alter-source/). \|  |

## Details

### Ingesting data

After a source is created, you can create tables from the source, referencing
the tables in the publication, to start ingesting data. You can create multiple
tables that reference the same table in the publication.

See [`CREATE TABLE FROM SOURCE`](/sql/create-table/) for details.

#### Handling table schema changes

The use of the `CREATE SOURCE` with the new [`CREATE TABLE FROM
SOURCE`](/sql/create-table/) allows for the handling of certain upstream DDL
changes without downtime.

See [`CREATE TABLE FROM
SOURCE`](/sql/create-table/postgres/#handling-table-schema-changes) for details.

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

#### Supported types

With the new syntax, after a PostgreSQL source is created, you [`CREATE TABLE
FROM SOURCE`](/sql/create-table/) to create a corresponding table in
Materialize and start ingesting data.

<p>Materialize natively supports the following PostgreSQL types (including the
array type for each of the types):</p>
<ul style="column-count: 3"><li><code>bool</code></li><li><code>bpchar</code></li><li><code>bytea</code></li><li><code>char</code></li><li><code>date</code></li><li><code>daterange</code></li><li><code>float4</code></li><li><code>float8</code></li><li><code>int2</code></li><li><code>int2vector</code></li><li><code>int4</code></li><li><code>int4range</code></li><li><code>int8</code></li><li><code>int8range</code></li><li><code>interval</code></li><li><code>json</code></li><li><code>jsonb</code></li><li><code>numeric</code></li><li><code>numrange</code></li><li><code>oid</code></li><li><code>text</code></li><li><code>time</code></li><li><code>timestamp</code></li><li><code>timestamptz</code></li><li><code>tsrange</code></li><li><code>tstzrange</code></li><li><code>uuid</code></li><li><code>varchar</code></li></ul>

For more information, including strategies for handling unsupported types,
see [`CREATE TABLE FROM SOURCE`](/sql/create-table/).

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

### PostgreSQL replication slots

When you define a source, Materialize will automatically create a **replication
slot** in the upstream PostgreSQL database (see [PostgreSQL replication
slots](#postgresql-replication-slots)). Each source ingests the raw replication
stream data for all tables in the specified publication using **a single**
replication slot. This allows you to minimize the performance impact on the
upstream database as well as reuse the same source across multiple
materializations.

The name of the replication slot created by Materialize is prefixed with
`materialize_`. In Materialize, you can query the
`mz_internal.mz_postgres_sources` to find the replication slots created:

```mzsql
SELECT id, replication_slot FROM mz_internal.mz_postgres_sources;
```

```
    id   |             replication_slot
---------+----------------------------------------------
  u8     | materialize_7f8a72d0bf2a4b6e9ebc4e61ba769b71
```

> **Tip:** - For PostgreSQL 13+, set a reasonable value
> for [`max_slot_wal_keep_size`](https://www.postgresql.org/docs/13/runtime-config-replication.html#GUC-MAX-SLOT-WAL-KEEP-SIZE)
> to limit the amount of storage used by replication slots.
> - If you stop using Materialize, or if either the Materialize instance or
> the PostgreSQL instance crash, delete any replication slots. You can query
> the `mz_internal.mz_postgres_sources` table to look up the name of the
> replication slot created for each source.
> - If you delete all objects that depend on a source without also dropping
> the source, the upstream replication slot remains and will continue to
> accumulate data so that the source can resume in the future. To avoid
> unbounded disk space usage, make sure to use [`DROP
> SOURCE`](/sql/drop-source/) or manually delete the replication slot.

### Reading from a physical standby

Materialize can replicate from a PostgreSQL physical standby (read
replica) instead of the primary, using logical decoding on the standby.
This requires **PostgreSQL 16+** on both the primary and the standby, since
earlier versions do not support creating logical replication slots on a
standby.

When the upstream is a standby, the replication slot is created on the
standby and Materialize only connects to the standby. Note that slot
creation on a standby can block until the primary emits a standby snapshot
(a `RUNNING_XACTS` WAL record). On an idle primary, run
[`SELECT pg_log_standby_snapshot()`](https://www.postgresql.org/docs/16/functions-admin.html#FUNCTIONS-SNAPSHOT-SYNCHRONIZATION)
on the primary to unblock source creation.

## Handling upstream operations

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

## Source failure states and recovery

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

## Examples

### Prerequisites

To create a source from PostgreSQL 11+, you must first:

- **Configure upstream PostgreSQL instance**
  - Set up logical replication.
  - Create a publication.
  - Create a replication user and password for Materialize to use to connect.
- **Configure network security**
  - Ensure Materialize can connect to your PostgreSQL instance.
- **Create a connection to PostgreSQL in Materialize**
  - The connection setup depends on the network security configuration.

For details, see the [PostgreSQL integration
guides](/ingest-data/postgres/#integration-guides).

### Create a source {#create-source-example}

Once you have configured the upstream PostgreSQL, network security, and
created the connection, you can create the source. In this example, the
PostgreSQL publication is `mz_source` and the connection to PostgreSQL is
`pg_connection`.
```mzsql
/* This example assumes:
- In the upstream PostgreSQL, you have defined:
  - replication user and password with the appropriate access.
  - a publication named `mz_source` for the `public.items` and `public.orders` tables.
- In Materialize:
  - You have created a secret for the PostgreSQL password.
  - You have defined the connection to the upstream PostgreSQL.
  - You have used the connection to create a source.

  For example (substitute with your configuration):
    CREATE SECRET pgpass AS '<replication user password>'; -- substitute
    CREATE CONNECTION pg_connection TO POSTGRES (
      HOST '<hostname>',          -- substitute
      DATABASE <db>,              -- substitute
      USER <replication user>,    -- substitute
      PASSWORD SECRET pgpass
      -- [, <network security configuration> ]
    );
*/

CREATE SOURCE pg_source
FROM POSTGRES CONNECTION pg_connection (
  PUBLICATION 'mz_source'
);

```

After a source is created, you can create tables from the source,
referencing specific upstream table(s). Use a [DDL transaction block](/sql/begin/#ddl-only-transactions) to create multiple tables from the same source.
```mzsql
BEGIN;
CREATE TABLE items
FROM SOURCE pg_source(REFERENCE public.items)
;
CREATE TABLE orders
FROM SOURCE pg_source(REFERENCE public.orders)
;
COMMIT;

```
{{< note >}}

- Although the example creates the tables with the same name as the upstream tables, the tables in Materialize can have different names.
- You can create multiple tables that reference the same upstream table.
{{< /note >}}

For more information, see [`CREATE TABLE`](/sql/create-table/).

## Related pages

- [`CREATE TABLE`](/sql/create-table/)
- [`CREATE SECRET`](/sql/create-secret)
- [`CREATE CONNECTION`](/sql/create-connection)
- [PostgreSQL integration guides](/ingest-data/postgres/#integration-guides)

[`enum`]: https://www.postgresql.org/docs/current/datatype-enum.html
[`money`]: https://www.postgresql.org/docs/current/datatype-money.html

<!-- mz-docs page: sql/create-source/sql-server -->

# CREATE SOURCE: SQL Server (Legacy Syntax)
Connecting Materialize to a SQL Server database for Change Data Capture (CDC).
> **Disambiguation:** This page reflects the legacy syntax, which requires downtime to handle upstream DDL changes. For the new syntax which can handle adding or dropping columns to the upstream tables without downtime, see the [new reference page](/sql/create-source/sql-server-v2).

[`CREATE SOURCE`](/sql/create-source/) connects Materialize to an external system you want to read data from, and provides details about how to decode and interpret that data.

Materialize supports SQL Server (2016+) as a real-time data source. To connect to a
SQL Server database, you first need to tweak its configuration to enable [Change Data
Capture](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/enable-and-disable-change-data-capture-sql-server)
and [`SNAPSHOT` transaction isolation](https://learn.microsoft.com/en-us/dotnet/framework/data/adonet/sql/snapshot-isolation-in-sql-server)
for the database that you would like to replicate. Then [create a connection](#creating-a-connection)
in Materialize that specifies access and authentication parameters.

> **Note:** The exact configuration steps depend on your SQL Server deployment. For
> step-by-step instructions, see the integration guides for
> [Azure SQL Database](/ingest-data/sql-server/azure-db/) and
> [self-hosted or managed SQL Server](/ingest-data/sql-server/self-hosted/).

## Syntax

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM SQL SERVER CONNECTION <connection_name>
  [ ( EXCLUDE COLUMNS (<col1> [, ...]) ) ]
  [ ( TEXT COLUMNS (<col1> [, ...]) ) ]
<FOR ALL TABLES | FOR TABLES ( <table1> [AS <subsrc_name>] [, ...] )>
[WITH ( <with_option> [, ...] )]

```

| Syntax element | Description |
| --- | --- |
| `<src_name>` | The name for the source.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a source with the same name already exists. Instead, issue a notice and skip the source creation.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this source.  |
| **CONNECTION** `<connection_name>` | The name of the SQL Server connection to use in the source. For details on creating connections, check the [`CREATE CONNECTION`](/sql/create-connection/#sql-server) documentation page.  |
| **EXCLUDE COLUMNS** ( `<col1>` [, ...] ) | Optional. Exclude specific columns that cannot be decoded or should not be included in the subsources created in Materialize.  |
| **TEXT COLUMNS** ( `<col1>` [, ...] ) | Optional. If specified, decode data from the specified columns in the subsource(s) as `text` for the listed column(s), such as for unsupported data types.  |
| **FOR** `<table_schema_specification>` | Specifies which tables to create subsources for. The following `<table_schema_specification>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `ALL TABLES` \| Create subsources for all tables with CDC enabled in all schemas upstream. \| \| `TABLES ( <table1> [AS <subsrc_name>] [, ...] )` \| Create subsources for specific tables upstream. Requires fully-qualified table names (`<schema1>.<table1>`). \|  |
| **WITH** (`<with_option>` [, ...]) | Optional. The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `RETAIN HISTORY FOR <retention_period>` \| ***Private preview.** This option has known performance or stability issues and is under active development.* Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/serve-results/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`. \| \| `TIMESTAMP INTERVAL [=] <interval>` \| The interval at which timestamps are assigned to data read from this source. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). The value must be between the system parameters `min_timestamp_interval` and `max_timestamp_interval`. Default: the value of the `default_timestamp_interval` system parameter (`1s`). The interval can also be changed after creation with [`ALTER SOURCE`](/sql/alter-source/). \|  |

## Creating a source

Materialize ingests the CDC stream for all (or a specific set of) tables in your
upstream SQL Server database that have [Change Data Capture enabled](https://learn.microsoft.com/en-us/sql/relational-databases/track-changes/about-change-data-capture-sql-server).

```mzsql
CREATE SOURCE mz_source
  FROM SQL SERVER CONNECTION sql_server_connection
  FOR ALL TABLES;
```

When you define a source, Materialize will automatically:

1. Create a **subsource** for each capture instance upstream, and perform an
   initial, snapshot-based sync of the associated tables before it starts
   ingesting change events.

    ```mzsql
    SHOW SOURCES;
    ```

    ```nofmt
             name         |   type     |  cluster  |
    ----------------------+------------+------------
     mz_source            | sql-server |
     mz_source_progress   | progress   |
     table_1              | subsource  |
     table_2              | subsource  |
    ```

1. Incrementally update any materialized or indexed views that depend on the
   source as change events stream in, as a result of `INSERT`, `UPDATE` and
   `DELETE` operations in the upstream SQL Server database.

##### SQL Server schemas

`CREATE SOURCE` will attempt to create each upstream table in the same schema as
the source. This may lead to naming collisions if, for example, you are
replicating `schema1.table_1` and `schema2.table_1`. Use the `FOR TABLES`
clause to provide aliases for each upstream table, in such cases, or to specify
an alternative destination schema in Materialize.

```mzsql
CREATE SOURCE mz_source
  FROM SQL SERVER CONNECTION sql_server_connection
  FOR TABLES (schema1.table_1 AS s1_table_1, schema2.table_1 AS s2_table_1);
```

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

## Known limitations

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

## Examples

> **Important:** Before creating a SQL Server source, you must enable Change Data Capture and
> `SNAPSHOT` transaction isolation in the upstream database.

### Creating a connection

A connection describes how to connect and authenticate to an external system you
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

### Creating a source {#create-source-example}

You **must** enable Change Data Capture. See the setup instructions for
[Azure SQL Database](/ingest-data/sql-server/azure-db/#a-configure-azure-sql-database)
or [self-hosted SQL Server](/ingest-data/sql-server/self-hosted/#a-configure-sql-server).

Once CDC is enabled for all of the relevant tables, you can create a `SOURCE` in
Materialize to begin replicating data!

_Create subsources for all tables in SQL Server_

```mzsql
CREATE SOURCE mz_source
    FROM SQL SERVER CONNECTION sqlserver_connection
    FOR ALL TABLES;
```

_Create subsources for specific tables in SQL Server_

```mzsql
CREATE SOURCE mz_source
  FROM SQL SERVER CONNECTION sqlserver_connection
  FOR TABLES (mydb.table_1, mydb.table_2 AS alias_table_2);
```

#### Handling unsupported types

If you're replicating tables that use [data types unsupported](#supported-types)
by SQL Server's CDC feature, use the `EXCLUDE COLUMNS` option to exclude them from
replication. This option expects the upstream fully-qualified names of the
replicated table and column (i.e. as defined in your SQL Server database).

```mzsql
CREATE SOURCE mz_source
  FROM SQL SERVER CONNECTION sqlserver_connection (
    EXCLUDE COLUMNS (mydb.table_1.column_of_unsupported_type)
  )
  FOR ALL TABLES;
```

### Handling errors and schema changes

> **Note:** Work to more smoothly support ddl changes to upstream tables is currently in
> progress. The work introduces the ability to re-ingest the same upstream table
> under a new schema and switch over without downtime.

To handle upstream [schema changes](#handling-upstream-operations) or errored subsources, use
the [`DROP SOURCE`](/sql/alter-source/#context) syntax to drop the affected
subsource, and then [`ALTER SOURCE...ADD SUBSOURCE`](/sql/alter-source/) to add
the subsource back to the source.

```mzsql
-- List all subsources in mz_source
SHOW SUBSOURCES ON mz_source;

-- Get rid of an outdated or errored subsource
DROP SOURCE table_1;

-- Start ingesting the table with the updated schema or fix
ALTER SOURCE mz_source ADD SUBSOURCE table_1;
```

## Related pages

- [`CREATE SECRET`](/sql/create-secret)
- [`CREATE CONNECTION`](/sql/create-connection)
- [`CREATE SOURCE`](../)

<!-- mz-docs page: sql/create-source/sql-server-v2 -->

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

<!-- mz-docs page: sql/create-source/webhook -->

# CREATE SOURCE: Webhook
Ingesting data into Materialize with HTTP requests
[`CREATE SOURCE`](/sql/create-source/) connects Materialize to an external system you want to read data from, and provides details about how to decode and interpret that data.

Webhook sources expose a [public URL](#webhook-url) that allows your applications to push webhook events into Materialize.

## Syntax

```mzsql
CREATE SOURCE [IF NOT EXISTS] <src_name>
[IN CLUSTER <cluster_name>]
FROM WEBHOOK
  BODY FORMAT <TEXT | JSON [ARRAY] | BYTES>
  [INCLUDE HEADER <header_name> AS <column_alias> [BYTES] |
   INCLUDE HEADERS [ ( [NOT] <header_name> [, [NOT] <header_name> ... ] ) ]
  ][...]
  [CHECK (
      [WITH ( <BODY|HEADERS|SECRET <secret_name>> [AS <alias>] [BYTES] [, ...])]
      <check_expression>
    )
  ]

```

| Syntax element | Description |
| --- | --- |
| `<src_name>` | The name for the source.  |
| **IF NOT EXISTS** | Optional. If specified, do not throw an error if a source with the same name already exists. Instead, issue a notice and skip the source creation.  |
| **IN CLUSTER** `<cluster_name>` | Optional. The [cluster](/sql/create-cluster) to maintain this source.  |
| `BODY FORMAT <TEXT \| JSON [ARRAY] \| BYTES>` | **Required.** Specifies the format of the request body. Valid formats: - `TEXT`: Parses the body as UTF-8 text. If the body is not valid UTF-8, a response of `400` Bad Request will be returned. - `JSON`: Parses the body as JSON. Also accepts events batched as newline-delimited JSON (`NDJSON`). If the body is not valid JSON, a response of `400` Bad Request will be returned. - `JSON ARRAY`: Parses the body as a list of JSON objects, automatically expanding the list to individual rows. Also accepts a single JSON object. If the body is not valid JSON, a response of `400` Bad Request will be returned. - `BYTES`: Does no parsing of the request, and stores the body as it was received.  |
| `INCLUDE HEADER <header_name> AS <column_alias> [BYTES]` | Optional. Map a header value from a request into a column. The `bytea` value is automatically parsed into a UTF-8 string unless `BYTES` is specified. Header columns are nullable. If the header of a request does not contain a specified field, the `NULL` value will be used as a default.  |
| `INCLUDE HEADERS [ ( [NOT] <header_name> [, [NOT] <header_name> ... ] ) ]` | Optional. Include a column named `headers` of type `map[text => text]` containing the headers of the request. To exclude specific header fields from the mapping, use the `NOT` option. This can be useful if you need to accept a dynamic list of fields but want to exclude sensitive information like authorization.  |
| `CHECK ( [WITH ( ... )] <check_expression> )` | Optional. Specify a boolean expression that is used to validate each request received by the source. Without a `CHECK` statement, **all requests will be accepted**. To prevent bad actors from injecting data into your source, it is **strongly encouraged** that you define a `CHECK` statement with your webhook sources.  |
| `WITH ( <BODY\|HEADERS\|SECRET <secret_name>> [AS <alias>] [BYTES] [, ...])` | Optional. Provide columns to the check expression. The headers and body of the request are only subject to validation if `WITH ( BODY, HEADERS, ... )` is specified as part of the `CHECK` statement. By default, the type of `body` used for validation is `text`, regardless of the `BODY FORMAT` you specified for the source.  - `BODY`: Provide a `body` column to the check expression. The column can be renamed with the optional **AS** `<alias>` statement, and the data type can be changed to `bytea` with the optional **BYTES** keyword. - `HEADERS`: Provide a column `headers` to the check expression. The column can be renamed with the optional **AS** `<alias>` statement, and the data type can be changed to `map[text => bytea]` with the optional **BYTES** keyword. - `SECRET <secret_name>`: Securely provide a [`SECRET`](/sql/create-secret) to the check expression. The `constant_time_eq` validation function **does not support** fully qualified secret names: if the secret is in a different namespace to the source, the column can be renamed with the optional **AS** `<alias>` statement. The data type can also be changed to `bytea` using the optional **BYTES** keyword.  |

## Supported formats

|<div style="width:290px">Body format</div> | Type      | Description       |
--------------------------------------------| --------- |-------------------|
| `BYTES`                                   | `bytea`   | Does **no parsing** of the request, and stores the body of a request as it was received. |
| `JSON`                                    | `jsonb`   | Parses the body of a request as JSON. Also accepts events batched as newline-delimited JSON (`NDJSON`). If the body is not valid JSON, a response of `400` Bad Request will be returned. |
| `JSON ARRAY`                              | `jsonb`   | Parses the body of a request as a list of JSON objects, automatically expanding the list of objects to individual rows. Also accepts a single JSON object. If the body is not valid JSON, a response of `400` Bad Request will be returned. |
| `TEXT`                                    | `text`    | Parses the body of a request as `UTF-8` text. If the body is not valid `UTF-8`, a response of `400` Bad Request will be returned. |

## Output

If source creation is successful, you'll have a new source object with
name _src_name_ and, based on what you defined with `BODY FORMAT` and `INCLUDE
HEADERS`, the following columns:

Column     | Type                        | Optional?                                      |
-----------|-----------------------------|------------------------------------------------|
 `body`    | `bytea`, `jsonb`, or `text` |                                                |
 `headers` | `map[text => text]`         | ✓ . Present if `INCLUDE HEADERS` is specified. |

### Webhook URL

After source creation, the unique URL that allows you to **POST** events to the
source can be looked up in the [`mz_internal.mz_webhook_sources`](/sql/system-catalog/mz_internal/#mz_webhook_sources)
system catalog table. The URL will have the following format:

```
https://<HOST>/api/webhook/<database>/<schema>/<src_name>
```

A breakdown of each component is as follows:

- `<HOST>`: The Materialize instance URL, which can be found on the [Materialize console](/developer-tools/console/).
- `<database>`: The name of the database where the source is created (default is `materialize`).
- `<schema>`: The schema name where the source gets created (default is `public`).
- `<src_name>`: The name you provided for your source at the time of creation.

> **Note:** This is a public URL that is open to the internet and has no security. To
> validate that requests are legitimate, see [Validating requests](#validating-requests).
> For limits imposed on this endpoint, see [Request limits](#request-limits).

## Features

### Exposing headers

In addition to the request body, Materialize can expose headers to SQL. If a
request header exists, you can map its fields to columns using the `INCLUDE
HEADER` syntax.

```mzsql
CREATE SOURCE my_webhook_source FROM WEBHOOK
  BODY FORMAT JSON
  INCLUDE HEADER 'timestamp' as ts
  INCLUDE HEADER 'x-event-type' as event_type;
```

This example would have the following columns:

Column      | Type    | Nullable? |
------------|---------|-----------|
 body       | `jsonb` | No        |
 ts         | `text`  | Yes       |
 event_type | `text`  | Yes       |

All of the header columns are nullable. If the header of a request does not
contain a specified field, the `NULL` value will be used as a default.

#### Excluding header fields

To exclude specific header fields from the mapping, use the `INCLUDER HEADERS`
syntax in combination with the `NOT` option. This can be useful if, for
example, you need to accept a dynamic list of fields but want to exclude
sensitive information like authorization.

```mzsql
CREATE SOURCE my_webhook_source FROM WEBHOOK
  BODY FORMAT JSON
  INCLUDE HEADERS ( NOT 'authorization', NOT 'x-api-key' );
```

This example would have the following columns:

Column      | Type                | Nullable?  |
------------|---------------------|------------|
 body       | `jsonb`             | No         |
 headers    | `map[text => text]` | No         |

All header fields but `'authorization'` and `'x-api-key'` will get included in
the `headers` map column.

### Validating requests

> **Warning:** Without a `CHECK` statement, **all requests will be accepted**. To prevent bad
> actors from injecting data into your source, it is **strongly encouraged** that
> you define a `CHECK` statement with your webhook sources.

It's common for applications using webhooks to provide a method for validating a
request is legitimate. You can specify an expression to do this validation for
your webhook source using the `CHECK` clause.

For example, the following source HMACs the request body using the `sha256`
hashing algorithm, and asserts the result is equal to the value provided in the
`x-signature` header, decoded with `base64`.

```mzsql
CREATE SOURCE my_webhook_source FROM WEBHOOK
  BODY FORMAT JSON
  CHECK (
    WITH (
      HEADERS, BODY AS request_body,
      SECRET my_webhook_shared_secret AS validation_secret
    )
    -- The constant_time_eq validation function **does not support** fully
    -- qualified secret names. We recommend always aliasing the secret name
    -- for ease of use.
    constant_time_eq(
        decode(headers->'x-signature', 'base64'),
        hmac(request_body, validation_secret, 'sha256')
    )
  );
```

The headers and body of the request are only subject to validation if `WITH
( BODY, HEADERS, ... )` is specified as part of the `CHECK` statement. By
default, the type of `body` used for validation is `text`, regardless of the
`BODY FORMAT` you specified for the source. In the example above, the `body`
column for `my_webhook_source` has a type of `jsonb`, but `request_body` as
used in the validation expression has type `text`. Futher, the request headers
are not persisted as part of `my_webhook_source`, since `INCLUDE HEADERS` was
not specified — but they are provided to the validation expression.

#### Debugging validation

It can be difficult to get your `CHECK` statement correct, especially if your
application does not have a way to send test events. If you're having trouble
with your `CHECK` statement, we recommend creating a temporary source without
`CHECK` and using that to iterate more quickly.

```mzsql
CREATE SOURCE my_webhook_temporary_debug FROM WEBHOOK
  -- Specify the BODY FORMAT as TEXT or BYTES,
  -- which is how it's provided to CHECK.
  BODY FORMAT TEXT
  INCLUDE HEADERS;
```

Once you have a few events in _my_webhook_temporary_debug_, you can query it with your would-be
`CHECK` statement.

```mzsql
SELECT
  -- Your would-be CHECK statement.
  constant_time_eq(
    decode(headers->'signature', 'base64'),
    hmac(headers->'timestamp' || body, 'my key', 'sha512')
  )
FROM my_webhook_temporary_debug
LIMIT 10;
```

> **Note:** It's not possible to use secrets in a `SELECT` statement, so you'll need to
> provide these values as raw text for debugging.

### Handling duplicated and partial events

Given any number of conditions, e.g. a network hiccup, it's possible for your application to send
an event more than once. If your event contains a unique identifier, you can de-duplicate these events
using a [`MATERIALIZED VIEW`](/sql/create-materialized-view/) and the `DISTINCT ON` clause.

```mzsql
CREATE MATERIALIZED VIEW my_webhook_idempotent AS (
  SELECT DISTINCT ON (body->>'unique_id') *
  FROM my_webhook_source
  ORDER BY id
);
```

We can take this technique a bit further to handle partial events. Let's pretend our application
tracks the completion of build jobs, and it sends us JSON objects with following structure.

Key           | Value   | Optional? |
--------------|---------|-----------|
_id_          | `text`  | No
_started_at_  | `text`  | Yes
_finished_at_ | `text`  | Yes

When a build job starts we receive an event containing _id_ and the _started_at_ timestamp. When a
build finished, we'll receive a second event with the same _id_ but now a _finished_at_ timestamp.
To merge these events into a single row, we can again use the `DISTINCT ON` clause.

```mzsql
CREATE MATERIALIZED VIEW my_build_jobs_merged AS (
  SELECT DISTINCT ON (id) *
  FROM (
    SELECT
      body->>'id' as id,
      try_parse_monotonic_iso8601_timestamp(body->>'started_at') as started_at,
      try_parse_monotonic_iso8601_timestamp(body->>'finished_at') as finished_at
    FROM my_build_jobs_source
  )
  ORDER BY id, finished_at NULLS LAST, started_at NULLS LAST
);
```

> **Note:** When casting from `text` to `timestamp` you should prefer to use the [`try_parse_monotonic_iso8601_timestamp`](/sql/functions/pushdown/)
> function, which enables [temporal filter pushdown](/transform-data/patterns/temporal-filters/#temporal-filter-pushdown).

### Handling batch events

The application pushing events to your webhook source may batch multiple events
into a single HTTP request. The webhook source supports parsing batched events
in the following formats:

#### JSON arrays

You can automatically expand a batch of requests formatted as a JSON array into
separate rows using `BODY FORMAT JSON ARRAY`.

```mzsql
-- Webhook source that parses request bodies as a JSON array.
CREATE SOURCE webhook_source_json_array FROM WEBHOOK
  BODY FORMAT JSON ARRAY
  INCLUDE HEADERS;
```

If you `POST` a JSON array of three elements to `webhook_source_json_array`,
three rows will get appended to the source.

```bash
POST webhook_source_json_array
[
  { "event_type": "a" },
  { "event_type": "b" },
  { "event_type": "c" }
]
```

```mzsql
SELECT COUNT(body) FROM webhook_source_json_array;
----
3
```

You can also post a single object to the source, which will get appended as one
row.

```bash
POST webhook_source_json_array
{ "event_type": "d" }
```

```mzsql
SELECT body FROM webhook_source_json_array;
----
{ "event_type": "a" }
{ "event_type": "b" }
{ "event_type": "c" }
{ "event_type": "d" }
```

#### Newline-delimited JSON (NDJSON)

You can automatically expand a batch of requests formatted as NDJSON into
separate rows using `BODY FORMAT JSON`.

```mzsql
-- Webhook source that parses request bodies as NDJSON.
CREATE SOURCE webhook_source_ndjson FROM WEBHOOK
BODY FORMAT JSON;
```

If you `POST` two elements delimited by newlines to `webhook_source_ndjson`, two
rows will get appended to the source.

```bash
POST 'webhook_source_ndjson'
  { 'event_type': 'foo' }
  { 'event_type': 'bar' }
```

```mzsql
SELECT COUNT(body) FROM webhook_source_ndjson;
----
2
```

## Request limits

Webhook sources apply the following limits to received requests:

* The maximum size of the request body is **`5MB`**. Requests larger than this
  will fail with `413 Payload Too Large`.
* The maximum number of concurrent requests across **all** webhook sources
  is **500**. Trying to connect when the server is at capacity will fail with
  `429 Too Many Requests`.
* A `CHECK` expression may use at most **`20MB`** of temporary memory while
  validating a single request. A `CHECK` that needs more, for example one that
  builds a large string out of the request body, will fail with
  `400 Bad Request`.
* Requests that contain a header name specified more than once will be rejected
  with `401 Unauthorized`.

## Examples

### Using basic authentication

[Basic authentication](https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication#basic_authentication_scheme)
enables a simple and rudimentary way to grant authorization to your webhook
source.

To store the sensitive credentials and make them reusable across multiple
`CREATE SOURCE` statements, use [secrets](/sql/create-secret/).

```mzsql
CREATE SECRET basic_hook_auth AS 'Basic <base64_auth>';
```

### Creating a source

After a successful secret creation, you can use the same secret to create
different webhooks with the same basic authentication to check if a request is
valid.

```mzsql
CREATE SOURCE webhook_with_basic_auth
FROM WEBHOOK
    BODY FORMAT JSON
    CHECK (
      WITH (
        HEADERS,
        BODY AS request_body,
        SECRET basic_hook_auth AS validation_secret
      )
      -- The constant_time_eq validation function **does not support** fully
      -- qualified secret names. We recommend always aliasing the secret name
      -- for ease of use.
      constant_time_eq(headers->'authorization', validation_secret)
    );
```

Your new webhook is now up and ready to accept requests using basic
authentication.

#### JSON parsing

Webhook data is ingested as a JSON blob. We recommend creating a parsing view on
top of your webhook source that maps the individual fields to columns with the
required data types. To avoid doing this tedious task manually, you can use
[this **JSON parsing widget**](/sql/types/jsonb/#parsing)!

### Related pages

- [`CREATE SECRET`](/sql/create-secret)
- [`CREATE SOURCE`](../)
- [`SHOW SOURCES`](/sql/show-sources)
- [`DROP SOURCE`](/sql/drop-source)

<!-- mz-docs page: sql/create-table -->

# CREATE TABLE

`CREATE TABLE` creates a table that is persisted in durable storage.

`CREATE TABLE` defines a table that is persisted in durable storage.

In Materialize, you can create:

- [Read-write tables](/sql/create-table/user-populated/). With read-write
  tables, users can read ([`SELECT`]) and write to the tables ([`INSERT`],
  [`UPDATE`], [`DELETE`]).

- Read-only tables from sources that use the new syntax:
  [PostgreSQL](/sql/create-table/postgres/),
  [MySQL](/sql/create-table/mysql/),
  [SQL Server](/sql/create-table/sql-server/), and
  [Kafka/Redpanda](/sql/create-table/kafka/). Users cannot write ([`INSERT`],
  [`UPDATE`], [`DELETE`]) to these tables. These tables are populated by [data
  ingestion from a source](/ingest-data/).
  You must be on **v26+** to use the new syntax.

[//]: # "TODO(morsapaes) Bring back When to use a table? once there's more
clarity around best practices."

## Syntax summary

**Read-write table:**

To create a new read-write table (i.e., users can perform
[`SELECT`](/sql/select/), [`INSERT`](/sql/insert/),
[`UPDATE`](/sql/update/), and [`DELETE`](/sql/delete/) operations):
```mzsql
CREATE [TEMP|TEMPORARY] TABLE [IF NOT EXISTS] <table_name> (
  <column_name> <column_type> [NOT NULL][DEFAULT <default_expr>]
  [, ...]
)
[WITH (
  PARTITION BY (<column_name> [, ...]) |
  RETAIN HISTORY [=] FOR <duration>
)]
;

```

For details, see [CREATE TABLE: Read-write
table](/sql/create-table/user-populated/).

**PostgreSQL source table:**

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external PostgreSQL:
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | EXCLUDE CONSTRAINTS ('<constraint_name>' [, ...])
  | EXCLUDE ALL CONSTRAINTS
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```{{< include-md
file="content/headless/create-table-from-source-snapshotting.md"
>}}

For details, see [CREATE TABLE: PostgreSQL source
table](/sql/create-table/postgres/).

**MySQL source table:**

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external MySQL database:
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_schema>.<upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```{{< include-md
file="content/headless/create-table-from-source-snapshotting.md"
>}}

For details, see [CREATE TABLE: MySQL source table](/sql/create-table/mysql/).

**SQL Server source table:**

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external SQL Server database:
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```{{% include-headless "/headless/create-table-from-source-snapshotting.md"
%}}

For details, see [CREATE TABLE: SQL Server source
table](/sql/create-table/sql-server/).

**Kafka source table:**

**Format Avro:**

Materialize can decode Avro messages by integrating with a schema registry
to retrieve a schema, and automatically determine the columns and data types
to use in the table.
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT AVRO
    USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>
      [KEY STRATEGY <key_strategy>]
      [VALUE STRATEGY <value_strategy>]
  | USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name> (
      SCHEMA NAME = '<schema_name>'
    )
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | DEBEZIUM
  | UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]
];

```

**Format JSON:**

Materialize can decode JSON messages into a single column named `data` with
type `jsonb`. Refer to the [`jsonb` type](/sql/types/jsonb) documentation for
the supported operations on this type.
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT JSON
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE];

```

**Format TEXT/BYTES:**

Materialize can parse **new-line delimited** data as plain text, or read raw
bytes without applying any formatting or decoding. Text-formatted tables have
a single column, by default named `text`. Raw byte-formatted tables have a
single column, by default named `data`.
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT TEXT | BYTES
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE];

```

**Format CSV:**

Materialize can parse CSV-formatted data. The data in CSV tables is read as
[`text`](/sql/types/text).
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT CSV WITH <n> COLUMNS [DELIMITED BY <char>]
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE];

```

**Format Protobuf:**

Materialize can decode Protobuf messages by integrating with a schema
registry or parsing an inline schema to retrieve a `.proto` schema
definition. It can then automatically define the columns and data types to
use in the table.
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT PROTOBUF USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>
  | FORMAT PROTOBUF MESSAGE '<message_name>' USING SCHEMA '<schema_bytes>'
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]
];

```

**KEY FORMAT VALUE FORMAT:**

By default, the message key is decoded using the same format as the message
value. However, you can set the key and value encodings explicitly using
`KEY FORMAT ... VALUE FORMAT`.
```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
KEY FORMAT <key_format> VALUE FORMAT <value_format>
-- <key_format> and <value_format> can be:
-- AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION <conn_name>
--     [KEY STRATEGY <strategy>]
--     [VALUE STRATEGY <strategy>]
-- | AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_conn_name> (SCHEMA NAME = '<schema_name>')
-- | CSV WITH <num> COLUMNS DELIMITED BY <char>
-- | JSON | TEXT | BYTES
-- | PROTOBUF USING CONFLUENT SCHEMA REGISTRY CONNECTION <conn_name>
-- | PROTOBUF MESSAGE '<message_name>' USING SCHEMA '<schema_bytes>'
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | DEBEZIUM
  | UPSERT [(VALUE DECODING ERRORS = INLINE [AS name])]
];

```

For details, see [CREATE TABLE: Kafka source table](/sql/create-table/kafka/).

## Related pages

- [`INSERT`]
- [`DROP TABLE`](/sql/drop-table)

[`INSERT`]: /sql/insert/
[`SELECT`]: /sql/select/
[`UPDATE`]: /sql/update/
[`DELETE`]: /sql/delete/

<!-- mz-docs page: sql/create-table/kafka -->

# CREATE TABLE: Kafka source table
Create a read-only table from a Kafka/Redpanda source (new syntax).
In Materialize, you can create read-only tables from [Kafka/Redpanda sources
created using the new syntax](/sql/create-source/kafka-v2/).

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

**Format Avro:**

Materialize can decode Avro messages by integrating with a schema registry
to retrieve a schema, and automatically determine the columns and data types
to use in the table.

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT AVRO
    USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>
      [KEY STRATEGY <key_strategy>]
      [VALUE STRATEGY <value_strategy>]
  | USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_connection_name> (
      SCHEMA NAME = '<schema_name>'
    )
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | DEBEZIUM
  | UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]
];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| `<csr_connection_name>` | The [Confluent Schema Registry connection](/sql/create-connection/#confluent-schema-registry) to use in the source. Applies to both the key and value.  |
| `<glue_connection_name>` (**SCHEMA NAME** `'<schema_name>'`) | **Private preview.** This feature is under active development.  Decode Avro messages using a schema managed in AWS Glue Schema Registry. `<glue_connection_name>` is the [AWS Glue Schema Registry connection](/sql/create-connection/#aws-glue-schema-registry), and `SCHEMA NAME` (**required**) is the name of the schema to read from the connection's registry. The schema is pinned at the time the source is created.  A single `FORMAT AVRO USING AWS GLUE SCHEMA REGISTRY` clause resolves one schema. To set the key and value independently (for example, under `ENVELOPE UPSERT` or `ENVELOPE DEBEZIUM`), specify `KEY FORMAT ... VALUE FORMAT ...` explicitly.  |
| **KEY STRATEGY** `<key_strategy>` | Optional. Define how an Avro reader schema will be chosen for the message key. \| Strategy \| Description \| \|--------\|-------------\| \| **LATEST** \| (Default) Use the latest writer schema from the schema registry as the reader schema. \| \| **ID** \| Use a specific schema from the registry. \| \| **INLINE** \| Use the inline schema. \|  |
| **VALUE STRATEGY** `<value_strategy>` | Optional. Define how an Avro reader schema will be chosen for the message value. \| Strategy \| Description \| \|--------\|-------------\| \| **LATEST** \| (Default) Use the latest writer schema from the schema registry as the reader schema. \| \| **ID** \| Use a specific schema from the registry. \| \| **INLINE** \| Use the inline schema. \|  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** `<envelope>` | Optional. Specifies how Materialize interprets incoming records. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \| \| `DEBEZIUM` \| Decode Kafka messages produced by [Debezium](https://debezium.io/). \| \| `UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]` \| Use the standard key-value convention to support inserts, updates, and deletes. Required to consume [log compacted topics](https://docs.confluent.io/platform/current/kafka/design.html#log-compaction). \|  |

See also [Avro details](#avro).

**Format JSON:**

Materialize can decode JSON messages into a single column named `data` with
type `jsonb`. Refer to the [`jsonb` type](/sql/types/jsonb) documentation for
the supported operations on this type.

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT JSON
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** NONE | Optional. Specifies how Materialize interprets incoming records. Valid envelope type(s):  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \|  |

See also [JSON details](#json).

**Format TEXT/BYTES:**

Materialize can parse **new-line delimited** data as plain text, or read raw
bytes without applying any formatting or decoding. Text-formatted tables have
a single column, by default named `text`. Raw byte-formatted tables have a
single column, by default named `data`.

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT TEXT | BYTES
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** NONE | Optional. Specifies how Materialize interprets incoming records. Valid envelope type(s):  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \|  |

**Format CSV:**

Materialize can parse CSV-formatted data. The data in CSV tables is read as
[`text`](/sql/types/text).

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT CSV WITH <n> COLUMNS [DELIMITED BY <char>]
[INCLUDE
    PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE NONE];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| `<n>` **COLUMNS** | The number of columns in the CSV message.  |
| **DELIMITED BY** `<char>` | *Optional.* If specified, the delimiter character. By default, uses a comma `,` as the delimiter.  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** NONE | Optional. Specifies how Materialize interprets incoming records. Valid envelope type(s):  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \|  |

**Format Protobuf:**

Materialize can decode Protobuf messages by integrating with a schema
registry or parsing an inline schema to retrieve a `.proto` schema
definition. It can then automatically define the columns and data types to
use in the table.

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
FORMAT PROTOBUF USING CONFLUENT SCHEMA REGISTRY CONNECTION <csr_connection_name>
  | FORMAT PROTOBUF MESSAGE '<message_name>' USING SCHEMA '<schema_bytes>'
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]
];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| `<csr_connection_name>` | The [Confluent Schema Registry connection](/sql/create-connection/#confluent-schema-registry) to use to retrieve the `.proto` schema definition.  |
| **MESSAGE** `'<message_name>'` **USING SCHEMA** `'<schema_bytes>'` | Decode Protobuf messages using an inline schema instead of a schema registry. `<message_name>` is the top-level message name and `<schema_bytes>` is the encoded `FileDescriptorSet`.  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** `<envelope>` | Optional. Specifies how Materialize interprets incoming records. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \| \| `UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]` \| Use the standard key-value convention to support inserts, updates, and deletes. Required to consume [log compacted topics](https://docs.confluent.io/platform/current/kafka/design.html#log-compaction). \|  |

See also [Protobuf details](#protobuf).

**KEY FORMAT VALUE FORMAT:**

By default, the message key is decoded using the same format as the message
value. However, you can set the key and value encodings explicitly using
`KEY FORMAT ... VALUE FORMAT`.

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name>
FROM SOURCE <src_name>
KEY FORMAT <key_format> VALUE FORMAT <value_format>
-- <key_format> and <value_format> can be:
-- AVRO USING CONFLUENT SCHEMA REGISTRY CONNECTION <conn_name>
--     [KEY STRATEGY <strategy>]
--     [VALUE STRATEGY <strategy>]
-- | AVRO USING AWS GLUE SCHEMA REGISTRY CONNECTION <glue_conn_name> (SCHEMA NAME = '<schema_name>')
-- | CSV WITH <num> COLUMNS DELIMITED BY <char>
-- | JSON | TEXT | BYTES
-- | PROTOBUF USING CONFLUENT SCHEMA REGISTRY CONNECTION <conn_name>
-- | PROTOBUF MESSAGE '<message_name>' USING SCHEMA '<schema_bytes>'
[INCLUDE
    KEY [AS <name>]
  | PARTITION [AS <name>]
  | OFFSET [AS <name>]
  | TIMESTAMP [AS <name>]
  | HEADERS [AS <name>]
  | HEADER '<key>' AS <name> [BYTES]
  [, ...]
]
[ENVELOPE
    NONE
  | DEBEZIUM
  | UPSERT [(VALUE DECODING ERRORS = INLINE [AS name])]
];

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="shared-content/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<src_name>` |  The name of the [Kafka source](/sql/create-source/kafka-v2/) to read from.  |
| **KEY FORMAT** `<key_format>` **VALUE FORMAT** `<value_format>` | Set the key and value encodings explicitly, instead of decoding both with a single `FORMAT`. Each of `<key_format>` and `<value_format>` can be `AVRO`, `JSON`, `TEXT`, `BYTES`, `CSV`, or `PROTOBUF`. See [supported formats](/sql/create-table/kafka/#syntax).  |
| **INCLUDE** `<include_option>` | Optional. If specified, include the additional information as column(s) in the table. The following `<include_option>`s are supported:  {{% include-headless "/headless/kafka-include-metadata-options" %}}  |
| **ENVELOPE** `<envelope>` | Optional. Specifies how Materialize interprets incoming records. Valid envelope types:  \| Envelope \| Description \| \|----------\|-------------\| \| `NONE` \| Append-only envelope (default). Each message is inserted as a new row. \| \| `DEBEZIUM` \| Decode Kafka messages produced by [Debezium](https://debezium.io/). \| \| `UPSERT [ ( VALUE DECODING ERRORS = INLINE [AS <name>] ) ]` \| Use the standard key-value convention to support inserts, updates, and deletes. Required to consume [log compacted topics](https://docs.confluent.io/platform/current/kafka/design.html#log-compaction). \|  |

## Envelopes

In addition to determining how to decode incoming records, Materialize also
needs to understand how to interpret them. Whether a new record inserts,
updates, or deletes existing data in Materialize depends on the `ENVELOPE`
specified. For where the `ENVELOPE` clause goes, see [Syntax](#syntax).

### Append-only envelope

<p style="font-size:14px"><b>Syntax:</b> <code>ENVELOPE NONE</code></p>

The append-only envelope treats all records as inserts. This is the **default** envelope, if no envelope is specified.

### Upsert envelope

<p style="font-size:14px"><b>Syntax:</b> <code>ENVELOPE UPSERT</code></p>

The upsert envelope uses the standard key-value convention to support inserts,
updates, and deletes within Materialize. It treats all records as having a
**key** and a **value**:

- If the key does not match a preexisting record, it inserts the record's key and value.

- If the key matches a preexisting record and the value is _non-null_, Materialize updates
  the existing record with the new value.

- If the key matches a preexisting record and the value is _null_, Materialize deletes the record.

> **Note:** - Using this envelope is required to consume [log compacted topics](https://docs.confluent.io/platform/current/kafka/design.html#log-compaction).
> - This envelope can lead to high memory and disk utilization in the cluster
>   maintaining the source. We recommend using a standard-sized cluster, rather
>   than a legacy-sized cluster, to automatically spill the workload to disk. See
>   [spilling to disk](/sql/create-source/kafka/#spilling-to-disk) for details.

#### Null keys

If a message with a `NULL` key is detected, Materialize sets the source into an
error state. To recover an errored source, you must produce a record with a
`NULL` value and a `NULL` key to the topic, to force a retraction.

As an example, you can use [`kcat`](https://docs.confluent.io/platform/current/clients/kafkacat-usage.html)
to produce an empty message:

```bash
echo ":" | kcat -b $BROKER -t $TOPIC -Z -K: \
  -X security.protocol=SASL_SSL \
  -X sasl.mechanisms=SCRAM-SHA-256 \
  -X sasl.username=$KAFKA_USERNAME \
  -X sasl.password=<KAFKA_PASSWORD>
```

#### Value decoding errors

By default, if an error happens while decoding the value of a message for a
specific key, Materialize sets the source into an error state. You can
configure the source to continue ingesting data in the presence of value
decoding errors using the `VALUE DECODING ERRORS = INLINE` option:

```mzsql
ENVELOPE UPSERT (VALUE DECODING ERRORS = INLINE)
```

When this option is specified the source will include an additional column named
`error` with type `record(description: text)`.

This column and all value columns will be nullable, such that if the most recent value
for the given Kafka message key cannot be decoded, this `error` column will contain
the error message. If the most recent value for a key has been successfully decoded,
this column will be `NULL`.

To use an alternative name for the error column, use `INLINE AS ..` to specify the
column name to use:

```mzsql
ENVELOPE UPSERT (VALUE DECODING ERRORS = (INLINE AS my_error_col))
```

It might be convenient to implement a parsing view on top of your Kafka upsert source that
excludes keys with decoding errors:

```mzsql
CREATE VIEW kafka_upsert_parsed
SELECT *
FROM kafka_upsert
WHERE error IS NULL;
```

### Debezium envelope

<p style="font-size:14px"><b>Syntax:</b> <code>ENVELOPE DEBEZIUM</code></p>

<div class="note">
  <strong class="gutter">NOTE:</strong> Currently, Materialize only supports Avro-encoded Debezium records. If you're interested in JSON support, please reach out in the community Slack or submit a <a href="https://github.com/MaterializeInc/materialize/discussions/new?category=feature-requests">feature request</a>.
</div>

Materialize provides a dedicated envelope (`ENVELOPE DEBEZIUM`) to decode Kafka
messages produced by [Debezium](https://debezium.io/).

Any materialized view defined on top of a Debezium source will be incrementally
updated as new change events stream in through Kafka, as a result of `INSERT`,
`UPDATE` and `DELETE` operations in the original database.

This envelope treats all records as [change events](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-events) with a diff structure that indicates whether each record should be interpreted as an insert, update or delete within Materialize:

|    |   |
 ----|---
 **Insert** | If the `before` field is _null_, the record represents an upstream [`create` event](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-create-events), and Materialize inserts the record's key and value.
 **Update** | If the `before` and `after` fields are _non-null_, the record represents an upstream [`update` event](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-update-events), and Materialize updates the existing record with the new value.
 **Delete** | If the `after` field is _null_, the record represents an upstream [`delete` event](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-delete-events), and Materialize deletes the record.

> **Note:** - This envelope can lead to high memory utilization in the cluster maintaining
>   the source. Materialize can automatically offload processing to
>   disk as needed. See [spilling to disk](/sql/create-source/kafka/#spilling-to-disk) for details.
> - Materialize expects a specific message structure that includes the row data
>   before and after the change event, which is **not guaranteed** for every
>   Debezium connector. For more details, check the [Debezium integration
>   guide](/integrations/debezium/).

#### Truncation

The Debezium envelope does not support upstream [`truncate` events](https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-truncate-events).

#### Debezium metadata

The envelope exposes the `before` and `after` value fields from change events.

#### Duplicate handling

Debezium may produce duplicate records if the connector is interrupted. Materialize makes a best-effort attempt to detect and filter out duplicates.

## Details

### Avro

#### Schema registries

Materialize can retrieve Avro schemas from either of two schema registries,
selected by the `USING` clause:

- **[Confluent Schema Registry](/sql/create-connection/#confluent-schema-registry)**
  (`USING CONFLUENT SCHEMA REGISTRY`): schemas are looked up by topic using the
  `TopicNameStrategy`, and the message's embedded schema ID resolves the writer
  schema at decode time.

- **[AWS Glue Schema Registry](/sql/create-connection/#aws-glue-schema-registry)**
  (`USING AWS GLUE SCHEMA REGISTRY`) <a class="private-preview-inline" href="https://materialize.com/preview-terms/">(feature in private preview)</a>
: schemas are
  looked up by the `SCHEMA NAME` you provide, and the message's embedded schema
  version ID resolves the writer schema at decode time. Each `FORMAT AVRO USING
  AWS GLUE` clause resolves a single schema. To decode keys and values from
  different schemas (for example, under `ENVELOPE UPSERT` or `ENVELOPE
  DEBEZIUM`), you must specify `KEY FORMAT ... VALUE FORMAT ...` explicitly.

#### Schema versioning

The schema is resolved when the source or table is created. With
[Confluent Schema Registry](/sql/create-connection/#confluent-schema-registry),
the _latest_ schema is retrieved using the
[`TopicNameStrategy`](https://docs.confluent.io/current/schema-registry/serdes-develop/index.html)
strategy. With [AWS Glue Schema
Registry](/sql/create-connection/#aws-glue-schema-registry), the latest version
of the schema named by `SCHEMA NAME` is retrieved.

#### Schema evolution

As long as the writer schema changes in a [compatible way](https://avro.apache.org/docs/++version++/specification/#schema-resolution), Materialize will continue using the original reader schema definition by mapping values from the new to the old schema version. This applies to both Confluent Schema Registry and AWS Glue Schema Registry.

To pick up the new version of the writer schema, the approach depends on the syntax you used:

- **Legacy syntax** (`CREATE SOURCE ... FORMAT AVRO ...`): you need to **drop and recreate** the source, which incurs downtime.
- **New syntax** (`CREATE SOURCE` plus [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/)): you can create a new table that reads the evolved schema and cut over without downtime. See [Handle upstream schema changes with zero downtime](/ingest-data/kafka/source-versioning/).

#### Name collision

To avoid [case-sensitivity](/sql/identifiers/#case-sensitivity) conflicts with Materialize identifiers, we recommend double-quoting all field names when working with Avro-formatted sources.

#### Supported types

Materialize supports all [Avro
types](https://avro.apache.org/docs/++version++/specification/), _except for_
recursive types and union types in arrays.

### JSON

If your JSON messages have a consistent shape, we recommend creating a parsing
[view](/fundamentals/concepts/views) that maps the individual fields to
columns with the required data types:

```mzsql
-- extract jsonb into typed columns
CREATE VIEW my_typed_source AS
  SELECT
    (data->>'field1')::boolean AS field_1,
    (data->>'field2')::int AS field_2,
    (data->>'field3')::float AS field_3
  FROM my_jsonb_source;
```

To avoid doing this task manually, you can use [this **JSON parsing
widget**](/sql/types/jsonb/#parsing).

#### Schema registry integration

Retrieving schemas from a schema registry is not supported yet for JSON-formatted sources. This means that Materialize cannot decode messages serialized using the [JSON Schema](https://docs.confluent.io/platform/current/schema-registry/serdes-develop/serdes-json.html#json-schema-serializer-and-deserializer) serialization format (`JSON_SR`).

### Protobuf

Unlike Avro, Protobuf does not serialize a schema with the message, so Materialize expects:

* A `FileDescriptorSet` that encodes the Protobuf message schema. You can generate the `FileDescriptorSet` with [`protoc`](https://grpc.io/docs/protoc-installation/), for example:

  ```shell
  protoc --include_imports --descriptor_set_out=SCHEMA billing.proto
  ```

* A top-level message name and its package name, so Materialize knows which message from the `FileDescriptorSet` is the top-level message to decode, in the following format:

  ```shell
  <package name>.<top-level message>
  ```

  For example, if the `FileDescriptorSet` were from a `.proto` file in the
    `billing` package, and the top-level message was called `Batch`, the
    _message&lowbar;name_ value would be `billing.Batch`.

#### Schema versioning

The _latest_ schema is retrieved using the [`TopicNameStrategy`](https://docs.confluent.io/current/schema-registry/serdes-develop/index.html) strategy at the time the source or table is created.

#### Schema evolution

As long as the `.proto` schema definition changes in a [compatible way](https://developers.google.com/protocol-buffers/docs/overview#updating-defs), Materialize will continue using the original schema definition by mapping values from the new to the old schema version. To pick up the new version of the schema with the legacy syntax (`CREATE SOURCE ... FORMAT PROTOBUF ...`), you need to **drop and recreate** the source. With the new syntax (`CREATE SOURCE` plus [`CREATE TABLE ... FROM SOURCE`](/sql/create-table/)), you can instead create a new table that reads the evolved schema and cut over without downtime, following the approach in [Handle upstream schema changes with zero downtime](/ingest-data/kafka/source-versioning/).

#### Supported types

Materialize supports all [well-known](https://developers.google.com/protocol-buffers/docs/reference/google.protobuf) Protobuf types from the `proto2` and `proto3` specs, _except for_ recursive `Struct` values and map types.

#### Multiple message schemas

When using a schema registry with Protobuf sources, the registered schemas must contain exactly one `Message` definition.

### Exposing source metadata

In addition to the message value, Materialize can expose the message key,
headers and other source metadata fields to SQL through the `INCLUDE` clause.
For where the `INCLUDE` clause goes, see [Syntax](#syntax).

#### Key

The message key is exposed via the `INCLUDE KEY` option. Composite keys are also
supported.

```mzsql
INCLUDE KEY AS renamed_id
```

Note that:

- This option requires specifying the key and value encodings explicitly using the `KEY FORMAT ... VALUE FORMAT` [syntax](#syntax).

- The `UPSERT` envelope always includes keys.

- The `DEBEZIUM` envelope is incompatible with this option.

#### Headers

Message headers can be retained in Materialize and exposed as part of the source data.

Note that:
- The `DEBEZIUM` envelope is incompatible with this option.

**All headers**

All of a message's headers can be exposed using `INCLUDE HEADERS`, followed by
an `AS <header_col>`.

This introduces column with the name specified or `headers` if none was
specified. The column has the type `record(key: text, value: bytea?) list`,
i.e. a list of records containing key-value pairs, where the keys are `text`
and the values are nullable `bytea`s.

```mzsql
INCLUDE HEADERS
```

To simplify turning the headers column into a `map` (so individual headers can
be searched), you can use the [`map_build`](/sql/functions/#map_build) function:

```mzsql
SELECT
    id,
    seller,
    item,
    convert_from(map_build(headers)->'client_id', 'utf-8') AS client_id,
    map_build(headers)->'encryption_key' AS encryption_key,
FROM kafka_metadata;
```

<p></p>

```nofmt
 id | seller |        item        | client_id |    encryption_key
----+--------+--------------------+-----------+----------------------
  2 |   1592 | Custom Art         |        23 | \x796f75207769736821
  3 |   1411 | City Bar Crawl     |        42 | \x796f75207769736821
```

**Individual headers**

Individual message headers can be exposed via the `INCLUDE HEADER key AS name`
option.

The `bytea` value of the header is automatically parsed into an UTF-8 string. To
expose the raw `bytea` instead, the `BYTES` option can be used.

```mzsql
INCLUDE HEADER 'c_id' AS client_id, HEADER 'key' AS encryption_key BYTES
```

Headers can be queried as any other column in the source:

```mzsql
SELECT
    id,
    seller,
    item,
    client_id::numeric,
    encryption_key
FROM kafka_metadata;
```

<p></p>

```nofmt
 id | seller |        item        | client_id |    encryption_key
----+--------+--------------------+-----------+----------------------
  2 |   1592 | Custom Art         |        23 | \x796f75207769736821
  3 |   1411 | City Bar Crawl     |        42 | \x796f75207769736821
```

Note that:

- Messages that do not contain all header keys as specified in the source DDL
  will cause an error that prevents further querying the source.

- Header values containing badly formed UTF-8 strings will cause an error in the
  source that prevents querying it, unless the `BYTES` option is specified.

#### Partition, offset, timestamp

These metadata fields are exposed via the `INCLUDE PARTITION`, `INCLUDE OFFSET`
and `INCLUDE TIMESTAMP` options.

```mzsql
INCLUDE PARTITION, OFFSET, TIMESTAMP AS ts
```

```mzsql
SELECT "offset" FROM kafka_metadata WHERE ts > '2021-01-01';
```

<p></p>

```nofmt
offset
------
15
14
13
```

### Excluding or recasting a field

A Kafka table's columns are determined entirely by its format (for Avro, the
reader schema). To exclude or recast a field, project or cast it in a view on
top of the table.

### DDL transaction block

For performance, when issuing multiple `CREATE TABLE FROM SOURCE...` statements,
use within a [transaction block](/sql/begin/#ddl-only-transactions).

### Source-populated tables and snapshotting

Creating a table from a source starts the
[snapshotting](/ingest-data/#snapshotting) process.

Snapshotting is the initial sync of a table's data. It reads from the upstream
system and writes the data into Materialize's storage. The initial snapshot is
committed to storage atomically, with all records assigned the same ingestion
timestamp.

You cannot query the table until its snapshot completes.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream schema changes, specifically adding or dropping
columns, without downtime. For details, see [Kafka: Handling upstream schema
changes with zero downtime](/ingest-data/kafka/source-versioning/).

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.
- For `CREATE TABLE ... FROM SOURCE`, `SELECT` privileges on the source and
  `USAGE` privileges on its schema. `SELECT` on a source permits attaching any
  reference that source ingests, so grant it only to roles that should be able
  to read all of the source's data.

## Examples

### Create a table

To create a **read-only** table from a Kafka source, use the `CREATE TABLE
... FROM SOURCE` statement. Unlike other source types, a Kafka source
exposes a single topic, so the statement does **not** take a `(REFERENCE
...)` clause. The following example creates a **read-only** table `orders`
that decodes the topic as [JSON](/sql/create-table/kafka/#json).

{{< note >}}

- You can create multiple tables from the same Kafka source, each decoding
the topic with a different format or envelope.

- For `JSON`-formatted topics, we recommend creating a
[parsing view](/sql/create-table/kafka/#json) on top of the table to map the
individual fields to columns with the appropriate data types.

{{< /note >}}
```mzsql
/* This example assumes:
  - In Materialize:
    - You have defined a connection to the upstream Kafka broker.
    - You have used the connection to create a source.

   For example (substitute with your configuration):
      CREATE CONNECTION kafka_connection TO KAFKA (
        BROKER '<broker>',            -- substitute
        SECURITY PROTOCOL = SASL_SSL,
        SASL MECHANISMS = 'SCRAM-SHA-256',
        SASL USERNAME = '<user>',     -- substitute
        SASL PASSWORD = SECRET kafka_password
      );

      CREATE SOURCE orders_src
      FROM KAFKA CONNECTION kafka_connection (
        TOPIC 'orders'                -- substitute
      );
*/

CREATE TABLE orders
FROM SOURCE orders_src
FORMAT JSON
;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

To verify that the table has been created, you can run [`SHOW
TABLES`](/sql/show-tables/) to list all tables in the current
[schema](/sql/namespaces/#namespace-hierarchy):
```mzsql
SHOW TABLES;

```The results should include the `orders` table:

```hc {hl_lines="3"}
| name    | comment |
| ------- | ------- |
| orders  |         |
```

Inspect the table columns using the [`SHOW COLUMNS`](/sql/show-columns/)
command:
```mzsql
SHOW COLUMNS FROM orders;

```Because the table decodes the topic as `JSON`, the message value is exposed
as a single `data` column of type [`jsonb`](/sql/types/jsonb/):

```hc
| name | nullable | type  | comment |
| ---- | -------- | ----- | ------- |
| data | false    | jsonb |         |
```

Once the snapshotting process completes and the table is in the running
state, you can query the table. For `JSON`-formatted data, use the
[`jsonb` operators](/sql/types/jsonb/#operators) to extract individual
fields:
```mzsql
SELECT
    (data->>'id')::bigint AS id,
    data->>'item' AS item,
    (data->>'quantity')::bigint AS quantity
FROM orders
ORDER BY id;

``````hc
| id | item   | quantity |
| -- | ------ | -------- |
| 1  | widget | 5        |
| 2  | gadget | 2        |
```

## Related pages

- [`CREATE SOURCE: Kafka/Redpanda (New Syntax)`](/sql/create-source/kafka-v2/)
- [`DROP TABLE`](/sql/drop-table)

<!-- mz-docs page: sql/create-table/mysql -->

# CREATE TABLE: MySQL source table
Create a read-only table from a MySQL source (new syntax).
In Materialize, you can create read-only tables from [MySQL sources created
using the new syntax](/sql/create-source/mysql-v2/).

> **Note:** You must be on **v26.25+** to use the new syntax.

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external MySQL database:

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_schema>.<upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<source_name>` |  The name of the [source](/sql/create-source/) associated with the reference object from which to create the table.  |
| **(REFERENCE <upstream_schema>.<upstream_table>)** |  The fully-qualified name of the upstream MySQL table from which to create the table. You can create multiple tables from the same upstream table.  To find the upstream tables available in your [source](/sql/create-source/), you can use the following query, substituting your source name for `<source_name>`:  <br>  ```mzsql SELECT refs.* FROM mz_internal.mz_source_references refs, mz_sources s WHERE s.name = '<source_name>' -- substitute with your source name AND refs.source_id = s.id; ```  This list is recorded when the source is created. To update the list with tables added to the upstream since source creation, run [`ALTER SOURCE <source_name> REFRESH REFERENCES`](/sql/alter-source/#refreshing-available-upstream-references).  |
| **WITH (<with_option>[,...])** | The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TEXT COLUMNS (<column_name> [, ...])` \| *Optional.* If specified, decode data as `text` for the listed column(s), such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `EXCLUDE COLUMNS (<column_name> [, ...])` \| *Optional.* If specified, exclude the listed column(s) from the table, such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `PARTITION BY (<column_name> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \|  |

## Details

### DDL transaction block

For performance, when issuing multiple `CREATE TABLE FROM SOURCE...` statements,
use within a [transaction block](/sql/begin/#ddl-only-transactions).

### Source-populated tables and snapshotting

Creating a table from a source starts the
[snapshotting](/ingest-data/#snapshotting) process.

Snapshotting is the initial sync of a table's data. It reads from the upstream
system and writes the data into Materialize's storage. The initial snapshot is
committed to storage atomically, with all records assigned the same ingestion
timestamp.

You cannot query the table until its snapshot completes.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### Supported data types

<p>Materialize natively supports the following MySQL types:</p>
<ul style="column-count: 3"><li><code>bigint</code></li><li><code>binary</code></li><li><code>bit</code></li><li><code>blob</code></li><li><code>boolean</code></li><li><code>char</code></li><li><code>date</code></li><li><code>datetime</code></li><li><code>decimal</code></li><li><code>double</code></li><li><code>float</code></li><li><code>int</code></li><li><code>json</code></li><li><code>longblob</code></li><li><code>longtext</code></li><li><code>mediumblob</code></li><li><code>mediumint</code></li><li><code>mediumtext</code></li><li><code>numeric</code></li><li><code>real</code></li><li><code>smallint</code></li><li><code>text</code></li><li><code>time</code></li><li><code>timestamp</code></li><li><code>tinyblob</code></li><li><code>tinyint</code></li><li><code>tinytext</code></li><li><code>varbinary</code></li><li><code>varchar</code></li></ul>

When replicating tables that contain the **unsupported [data
types](/sql/types/)**, you can:

- Use [`TEXT COLUMNS`
  option](/sql/create-source/mysql/#handling-unsupported-types) for the
  following unsupported  MySQL types:

  - `enum`
  - `year`

  The specified columns will be treated as `text` and will not offer the
  expected MySQL type features.

- Use the [`EXCLUDE COLUMNS`](/sql/create-source/mysql/#excluding-columns)
option to exclude any columns that contain unsupported data types.

#### Zero values for `date`, `datetime`, and `timestamp`

MySQL allows the special "zero" values `0000-00-00`, `0000-00-00
00:00:00` in `date`, `datetime`, and `timestamp` columns when the server
`sql_mode` does not include `NO_ZERO_DATE` or `NO_ZERO_IN_DATE`. These
values are not representable in Materialize's corresponding native types,
so they will cause ingestion to fail for the affected column.

To ingest columns that contain zero values, use [`TEXT
COLUMNS`](/sql/create-source/mysql/#handling-unsupported-types) to
decode the affected columns as `text`. The zero values for `date`,
`datetime`, `timestamp`, and `year` are preserved verbatim as strings
(e.g. `"0000-00-00 00:00:00"`, `"0000"`).

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream DDL changes, specifically adding or dropping
columns in the upstream tables, without downtime. For details, see [MySQL:
Handle upstream schema
changes](/ingest-data/mysql/source-versioning/).

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

## Handling upstream operations

This section describes how changes to upstream tables that Materialize ingests
affect the corresponding Materialize tables.

### Adding a column

When you add a new column to your upstream table, Materialize continues to
ingest only the existing columns.

To incorporate the new column:

- If using the new [`CREATE SOURCE` and `CREATE TABLE FROM
SOURCE`](/sql/create-source/mysql-v2/) syntax, create a new table from
the source. See [Handle upstream column addition](/ingest-data/mysql/source-versioning/#handle-upstream-column-addition).

- If using the legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/mysql/) syntax that creates subsources, use [`DROP
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
SOURCE`](/sql/create-source/mysql-v2/) syntax, you can safely drop a
column by first ignoring it in Materialize. See [Handle upstream column
drop](/ingest-data/mysql/source-versioning/#handle-upstream-column-drop).

- If using legacy [`CREATE SOURCE ... FOR ...`](/sql/create-source/mysql/) syntax, use [`DROP SOURCE`](/sql/drop-source/) to drop the affected
subsource, and then add the table back to the source using [`ALTER
SOURCE ... ADD SUBSOURCE`](/sql/alter-source/).

### Changing constraints

Materialize ignores the following constraint changes: foreign
key and `CHECK`.
As such, you can add or drop them without affecting ingestion.

Materialize also ignores `NOT NULL`, `UNIQUE`, and `PRIMARY KEY` constraints that
are added after the Materialize table is created (that is, the table was created
without them). Adding such a constraint, and later dropping it, does not affect
ingestion.

Dropping a `NOT NULL`, `UNIQUE`, or `PRIMARY KEY` constraint that existed when
the table was created puts the affected table into an error state.

### Changing a column's data type

Changing an ingested column's data type upstream so that it maps to a different
Materialize type than before puts the affected Materialize table into an
error state. Ingestion for that table stops, and you must drop and recreate the
table in Materialize to resume ingestion.

Changing an ingested column's upstream data type so that it continues to map to
the same Materialize type does not interrupt ingestion. For example, changing
`tinyint` to `smallint`, changing within the
`text`/`tinytext`/`mediumtext`/`longtext` family, and adjusting `bit(n)`
precision are all safe.

Appending new values to the **end** of an existing enum does not put the table
into an error state. However, the newly-added values are not recognized, so rows
that use them fail to decode until you drop and recreate the table. Existing
enum values remain recognized, and rows that use them continue to decode
successfully.

Any other enum change puts the affected Materialize table into an
error state, including inserting a value before the end, reordering or renaming
values, and removing values.

### Renaming a column

Renaming a column that Materialize ingests puts the affected table into an error
state. Ingestion for that table stops, and you must drop and recreate the table
in Materialize to resume ingestion.

### Table-level operations

The following upstream operations put the affected table into an error state.
Ingestion for that table stops, and you must drop and recreate the affected
table in Materialize to resume:

- Dropping a table (`DROP TABLE`).
- Renaming a table or moving it to a different schema.
- Truncating a table (`TRUNCATE`). To clear a table without putting it into an error state, use an unqualified `DELETE FROM t;` instead.

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.
- For `CREATE TABLE ... FROM SOURCE`, `SELECT` privileges on the source and
  `USAGE` privileges on its schema. `SELECT` on a source permits attaching any
  reference that source ingests, so grant it only to roles that should be able
  to read all of the source's data.

## Examples

### Create a table

To create new **read-only** tables from a source table, use the `CREATE
TABLE ... FROM SOURCE ... (REFERENCE <upstream_schema>.<upstream_table>)`
statement in a [DDL transaction
block](/sql/begin/#ddl-only-transactions). The following example creates
**read-only** tables `items` and `orders` from the MySQL source's
`mydb.items` and `mydb.orders` tables.

{{< note >}}

- Although the example creates the tables with the same names as the
upstream tables, the tables in Materialize can have names that differ from
the referenced table names.

- For supported MySQL data types, refer to [supported
types](/sql/create-table/mysql/#supported-data-types).

{{< /note >}}
```mzsql
/* This example assumes:
  - In the upstream MySQL, you have configured:
    - GTID-based binary log replication.
    - `binlog_row_metadata = FULL`.
    - A replication user and password with the appropriate access.
  - In Materialize:
    - You have created a secret for the MySQL password.
    - You have defined the connection to the upstream MySQL.
    - You have used the connection to create a source.

   For example (substitute with your configuration):
      CREATE SECRET mysqlpass AS '<replication user password>'; -- substitute
      CREATE CONNECTION mysql_connection TO MYSQL (
        HOST '<hostname>',          -- substitute
        PORT 3306,
        USER <replication user>,    -- substitute
        PASSWORD SECRET mysqlpass
        -- [, <network security configuration> ]
      );

      CREATE SOURCE mysql_source
      FROM MYSQL CONNECTION mysql_connection;
*/

BEGIN;
CREATE TABLE items
FROM SOURCE mysql_source (REFERENCE mydb.items)
;
CREATE TABLE orders
FROM SOURCE mysql_source (REFERENCE mydb.orders)
;
COMMIT;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

## Related pages

- [`CREATE SOURCE: MySQL (New Syntax)`](/sql/create-source/mysql-v2/)
- [`DROP TABLE`](/sql/drop-table)

<!-- mz-docs page: sql/create-table/postgres -->

# CREATE TABLE: PostgreSQL source table
Create a read-only table from a PostgreSQL source (new syntax).
In Materialize, you can create read-only tables from [PostgreSQL sources created
using the new syntax](/sql/create-source/postgres-v2/).

> **Note:** You must be on **v26+** to use the new syntax.

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external PostgreSQL:

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | EXCLUDE CONSTRAINTS ('<constraint_name>' [, ...])
  | EXCLUDE ALL CONSTRAINTS
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<source_name>` |  The name of the [source](/sql/create-source/) associated with the reference object from which to create the table.  |
| **(REFERENCE <upstream_table>)** |  The name of the upstream table from which to create the table. You can create multiple tables from the same upstream table.  To find the upstream tables available in your [source](/sql/create-source/), you can use the following query, substituting your source name for `<source_name>`:  <br>  ```mzsql SELECT refs.* FROM mz_internal.mz_source_references refs, mz_sources s WHERE s.name = '<source_name>' -- substitute with your source name AND refs.source_id = s.id; ```  This list is recorded when the source is created. To update the list with tables added to the upstream since source creation, run [`ALTER SOURCE <source_name> REFRESH REFERENCES`](/sql/alter-source/#refreshing-available-upstream-references).  The statement returns an error if the source's publication is empty.  |
| **WITH (<with_option>[,...])** | The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TEXT COLUMNS (<column_name> [, ...])` \|*Optional.* If specified, decode data as `text` for the listed column(s),such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `EXCLUDE COLUMNS (<column_name> [, ...])`\| *Optional.* If specified,exclude the listed column(s) from the table, such as for unsupported data types. See also [supported types](#supported-data-types).\| \| `EXCLUDE CONSTRAINTS ('<constraint_name>' [, ...])` \| ***Public preview.** This option is under active development and may have stability or performance issues.* *Optional.* If specified, do not record the listed upstream `PRIMARY KEY` or `UNIQUE` constraint(s) as keys of the table, so that dropping them upstream does not put the table into an error state. Constraint names are string literals matched exactly, including case. `NOT NULL` constraints cannot be excluded by name, use `EXCLUDE ALL CONSTRAINTS` instead. See [Handle upstream constraint drop](/ingest-data/postgres/source-versioning/#handle-upstream-constraint-drop). \| \| `EXCLUDE ALL CONSTRAINTS` \| ***Public preview.** This option is under active development and may have stability or performance issues.* *Optional.* If specified, record no upstream constraints: the table has no keys and every column is nullable, so dropping any `PRIMARY KEY`, `UNIQUE`, or `NOT NULL` constraint upstream does not put the table into an error state. Cannot be combined with `EXCLUDE CONSTRAINTS`. \| \| `PARTITION BY (<column_name> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \|  |

## Details

### DDL transaction block

For performance, when issuing multiple `CREATE TABLE FROM SOURCE...` statements,
use within a [transaction block](/sql/begin/#ddl-only-transactions).

### Source-populated tables and snapshotting

Creating a table from a source starts the
[snapshotting](/ingest-data/#snapshotting) process.

Snapshotting is the initial sync of a table's data. It reads from the upstream
system and writes the data into Materialize's storage. The initial snapshot is
committed to storage atomically, with all records assigned the same ingestion
timestamp.

You cannot query the table until its snapshot completes.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### Supported data types

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

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream DDL changes, specifically adding or dropping
columns in the upstream tables, without downtime. For details, see [PostgreSQL:
Handle upstream schema
changes](/ingest-data/postgres/source-versioning/).

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

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

You can mimic PostgreSQL's `SELECT` behavior with inherited tables by
creating a materialized view that unions data from the inherited and
inheriting tables (using `UNION ALL`). However, if new tables inherit from
the table, data from the inheriting tables will not be available in the
view. You will need to add the inheriting tables via `CREATE TABLE .. FROM
SOURCE` and create a new view (materialized or non-) that unions the new
table.

## Handling upstream operations

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

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.
- For `CREATE TABLE ... FROM SOURCE`, `SELECT` privileges on the source and
  `USAGE` privileges on its schema. `SELECT` on a source permits attaching any
  reference that source ingests, so grant it only to roles that should be able
  to read all of the source's data.

## Examples

### Create a table

> **Note:** You must be on **v26+** to use the new syntax.
> The example assumes you have configured your upstream PostgreSQL 11+ (i.e.,
> enabled logical replication, created the publication for the various tables and
> replication user, and updated the network configuration).
> For details about configuring your upstream system, see the [PostgreSQL
> integration guides](/ingest-data/postgres/#supported-versions-and-services).

To create new **read-only** tables from a source table, use the `CREATE
TABLE ... FROM SOURCE ... (REFERENCE <upstream_table>)` statement in a [DDL
transaction block](/sql/begin/#ddl-only-transactions). The following example
creates **read-only** tables `items` and `orders` from the PostgreSQL
source's `public.items` and `public.orders` tables (the schema is `public`).

{{< note >}}

- Although the example creates the tables with the same names as the
upstream tables, the tables in Materialize can have names that differ from
the referenced table names.

- For supported PostgreSQL data types, refer to [supported
types](/sql/create-table/postgres/#supported-data-types).

{{< /note >}}
```mzsql
/* This example assumes:
  - In the upstream PostgreSQL, you have defined:
    - replication user and password with the appropriate access.
    - a publication named `mz_source` for the `items` and `orders` tables.
  - In Materialize:
    - You have created a secret for the PostgreSQL password.
    - You have defined the connection to the upstream PostgreSQL.
    - You have used the connection to create a source.

   For example (substitute with your configuration):
      CREATE SECRET pgpass AS '<replication user password>'; -- substitute
      CREATE CONNECTION pg_connection TO POSTGRES (
        HOST '<hostname>',          -- substitute
        DATABASE <db>,              -- substitute
        USER <replication user>,    -- substitute
        PASSWORD SECRET pgpass
        -- [, <network security configuration> ]
      );

      CREATE SOURCE pg_source
      FROM POSTGRES CONNECTION pg_connection (
        PUBLICATION 'mz_source'       -- substitute
      );
*/

BEGIN;
CREATE TABLE items
FROM SOURCE pg_source(REFERENCE public.items)
;
CREATE TABLE orders
FROM SOURCE pg_source(REFERENCE public.orders)
;
COMMIT;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

Once the snapshotting process completes and the table is in the running state, you can query the table:
```mzsql
SELECT * FROM items;

```

## Related pages

- [`CREATE SOURCE: PostgreSQL (New Syntax)`](/sql/create-source/postgres-v2/)
- [`DROP TABLE`](/sql/drop-table)

<!-- mz-docs page: sql/create-table/sql-server -->

# CREATE TABLE: SQL Server source table
Create a read-only table from a SQL Server source (new syntax).
In Materialize, you can create read-only tables from [SQL Server sources created
using the new syntax](/sql/create-source/sql-server-v2/).

> **Note:** You must be on **v26.14.1+** to use the syntax.

## Syntax

> **Note:** Source-populated tables are **read-only** tables. Users **cannot** perform write
> operations
> ([`INSERT`](/sql/insert/)/[`UPDATE`](/sql/update/)/[`DELETE`](/sql/delete/)) on
> these tables.

To create a read-only table from a [source](/sql/create-source/) connected
(via native connector) to an external SQL Server database:

```mzsql
CREATE TABLE [IF NOT EXISTS] <table_name> FROM SOURCE <source_name> (REFERENCE <upstream_table>)
[WITH (
    TEXT COLUMNS (<column_name> [, ...])
  | EXCLUDE COLUMNS (<column_name> [, ...])
  | PARTITION BY (<column_name> [, ...])
  [, ...]
)]
;

```

| Syntax element | Description |
| --- | --- |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  {{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<source_name>` |  The name of the [source](/sql/create-source/) associated with the reference object from which to create the table.  |
| **(REFERENCE <upstream_table>)** |  The name of the upstream table from which to create the table. You can create multiple tables from the same upstream table.  To find the upstream tables available in your [source](/sql/create-source/), you can use the following query, substituting your source name for `<source_name>`:  <br>  ```mzsql SELECT refs.* FROM mz_internal.mz_source_references refs, mz_sources s WHERE s.name = '<source_name>' -- substitute with your source name AND refs.source_id = s.id; ```  This list is recorded when the source is created. To update the list with tables added to the upstream since source creation, run [`ALTER SOURCE <source_name> REFRESH REFERENCES`](/sql/alter-source/#refreshing-available-upstream-references).  |
| **WITH (<with_option>[,...])** | The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `TEXT COLUMNS (<column_name> [, ...])` \|*Optional.* If specified, decode data as `text` for the listed column(s),such as for unsupported data types. See also [supported types](#supported-data-types). \| \| `EXCLUDE COLUMNS (<column_name> [, ...])`\| *Optional.* If specified,exclude the listed column(s) from the table, such as for unsupported data types. See also [supported types](#supported-data-types).\| \| `PARTITION BY (<column_name> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \|  |

## Details

### DDL transaction block

For performance, when issuing multiple `CREATE TABLE FROM SOURCE...` statements,
use within a [transaction block](/sql/begin/#ddl-only-transactions).

### Source-populated tables and snapshotting

Creating a table from a source starts the
[snapshotting](/ingest-data/#snapshotting) process.

Snapshotting is the initial sync of a table's data. It reads from the upstream
system and writes the data into Materialize's storage. The initial snapshot is
committed to storage atomically, with all records assigned the same ingestion
timestamp.

You cannot query the table until its snapshot completes.

> **Note:** During the snapshotting, the data ingestion for the existing tables for the same
> source is temporarily blocked. As such, if possible, you can resize the cluster
> to speed up the snapshotting process and once the process finishes, resize the
> cluster for steady-state. You can monitor the snapshot progress on the overview
> page for the source in the Materialize console.

### Supported data types

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

### Handling table schema changes

The use of `CREATE SOURCE` (new syntax) with `CREATE TABLE FROM SOURCE` allows
for the handling of the upstream DDL changes, specifically adding or dropping
columns in the upstream tables, without downtime. For details, see [SQL Server:
Handle upstream schema
changes](/ingest-data/sql-server/source-versioning/).

See also [Handling upstream operations](#handling-upstream-operations) for
additional upstream operation considerations.

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

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.
- For `CREATE TABLE ... FROM SOURCE`, `SELECT` privileges on the source and
  `USAGE` privileges on its schema. `SELECT` on a source permits attaching any
  reference that source ingests, so grant it only to roles that should be able
  to read all of the source's data.

## Examples

### Create a table

To create new **read-only** tables from a source table, use the `CREATE
TABLE ... FROM SOURCE ... (REFERENCE <upstream_table>)` statement in a [DDL
transaction block](/sql/begin/#ddl-only-transactions). The following example
creates **read-only** tables `items` and `orders` from the SQL Server
source's `dbo.items` and `dbo.orders` tables.

{{< note >}}

- Although the example creates the tables with the same names as the
upstream tables, the tables in Materialize can have names that differ from
the referenced table names.

- The upstream table must have [Change Data Capture
(CDC)](/ingest-data/sql-server/) enabled.

- For supported SQL Server data types, refer to [supported
types](/sql/create-table/sql-server/#supported-data-types).

{{< /note >}}
```mzsql
/* This example assumes:
  - In the upstream SQL Server, you have:
    - Enabled Change Data Capture (CDC) on the database and the tables.
    - A user and password with the appropriate access.
  - In Materialize:
    - You have created a secret for the SQL Server password.
    - You have defined the connection to the upstream SQL Server.
    - You have used the connection to create a source.

   For example (substitute with your configuration):
      CREATE SECRET sqlserver_pass AS '<password>'; -- substitute
      CREATE CONNECTION sql_server_connection TO SQL SERVER (
        HOST '<hostname>',          -- substitute
        PORT 1433,
        DATABASE <db>,              -- substitute
        USER <user>,                -- substitute
        PASSWORD SECRET sqlserver_pass
        -- [, <network security configuration> ]
      );

      CREATE SOURCE sql_server_source
      FROM SQL SERVER CONNECTION sql_server_connection;
*/

BEGIN;
CREATE TABLE items
FROM SOURCE sql_server_source (REFERENCE dbo.items)
;
CREATE TABLE orders
FROM SOURCE sql_server_source (REFERENCE dbo.orders)
;
COMMIT;

```
{{< include-md
file="content/headless/create-table-from-source-snapshotting.md" >}}

{{< include-md file="content/headless/create-table-if-not-exists-tip.md" >}}

To verify that the tables have been created, you can run [`SHOW
TABLES`](/sql/show-tables/) to list all tables in the current
[schema](/sql/namespaces/#namespace-hierarchy):
```mzsql
SHOW TABLES;

```The results should include the tables `items` and `orders`:

```hc {hl_lines="3-4"}
| name   | comment |
| ------ | ------- |
| items  |         |
| orders |         |
```

Inspect the table columns using the [`SHOW COLUMNS`](/sql/show-columns/)
command:
```mzsql
SHOW COLUMNS FROM items;

```The results should display the table columns, with types mapped from the
upstream SQL Server table. For the list of supported SQL Server data types,
refer to [supported
types](/sql/create-table/sql-server/#supported-data-types).

```hc
| name     | nullable | type              | comment |
| -------- | -------- | ----------------- | ------- |
| id       | false    | integer           |         |
| item     | true     | character varying |         |
| quantity | true     | integer           |         |
```

Once the snapshotting process completes and the tables are in the running
state, you can query them:
```mzsql
SELECT * FROM items ORDER BY id;

``````hc
| id | item   | quantity |
| -- | ------ | -------- |
| 1  | widget | 5        |
| 2  | gadget | 2        |
```

## Related pages

- [`CREATE SOURCE: SQL Server (New Syntax)`](/sql/create-source/sql-server-v2/)
- [`DROP TABLE`](/sql/drop-table)

<!-- mz-docs page: sql/create-table/user-populated -->

# CREATE TABLE: Read-write table
Create a read-write, user-populated table in Materialize.
Read-write tables let you read ([`SELECT`](/sql/select/)) and write
([`INSERT`](/sql/insert/), [`UPDATE`](/sql/update/), [`DELETE`](/sql/delete/))
to the table.

## Syntax

To create a new read-write table (i.e., users can perform
[`SELECT`](/sql/select/), [`INSERT`](/sql/insert/),
[`UPDATE`](/sql/update/), and [`DELETE`](/sql/delete/) operations):

```mzsql
CREATE [TEMP|TEMPORARY] TABLE [IF NOT EXISTS] <table_name> (
  <column_name> <column_type> [NOT NULL][DEFAULT <default_expr>]
  [, ...]
)
[WITH (
  PARTITION BY (<column_name> [, ...]) |
  RETAIN HISTORY [=] FOR <duration>
)]
;

```

| Syntax element | Description |
| --- | --- |
| **TEMP** / **TEMPORARY** | *Optional.* If specified, mark the table as temporary.  Temporary tables are: - Automatically dropped at the end of the session; - Not visible to other connections; - Created in the special `mz_temp` schema.  Temporary tables may depend upon other temporary database objects, but non-temporary tables may not depend on temporary objects.  |
| **IF NOT EXISTS** | *Optional.* If specified, do not throw an error if the table with the same name already exists. Instead, issue a notice and skip the table creation.  |
| `<table_name>` |  The name of the table to create. Names for tables must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<column_name>` |  The name of a column to be created in the new table. Names for columns must follow the [naming guidelines](/sql/identifiers/#naming-restrictions).  |
| `<column_type>` |  The type of the column. For supported types, see [SQL data types](/sql/types/).  |
| **NOT NULL** | *Optional.* If specified, disallow  _NULL_ values for the column. Columns without this constraint can contain _NULL_ values.  |
| **DEFAULT <default_expr>** | *Optional.* If specified, use the `<default_expr>` as the default value for the column. If not specified, `NULL` is used as the default value.  |
| **WITH (<with_option>[,...])** |  The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `PARTITION BY (<column> [, ...])` \| {{< include-md file="content/headless/partition-by-option-description.md" >}} \| \| `RETAIN HISTORY <duration>` \| *Optional.* ***Private preview.** This option has known performance or stability issues and is under active development.* <br>If specified, Materialize retains historical data for the specified duration, which is useful to implement [durable subscriptions](/serve-results/durable-subscriptions/#history-retention-period).<br>Accepts positive [interval](/sql/types/interval/) values (e.g., `'1hr'`).\|  |

## Table names and column names

Names for tables and column(s) must follow the [naming
guidelines](/sql/identifiers/#naming-restrictions).

## Known limitations

Tables do not currently support:

- Primary keys
- Unique constraints
- Check constraints

See also the known limitations for [`INSERT`](/sql/insert#known-limitations),
[`UPDATE`](/sql/update#known-limitations), and [`DELETE`](/sql/delete#known-limitations).

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the table definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.
- For `CREATE TABLE ... FROM SOURCE`, `SELECT` privileges on the source and
  `USAGE` privileges on its schema. `SELECT` on a source permits attaching any
  reference that source ingests, so grant it only to roles that should be able
  to read all of the source's data.

## Examples

### Create a table

The following example uses `CREATE TABLE` to create a new read-write table
`mytable` with two columns `a` (of type `int`) and `b` (of type `text` and
not nullable):
```mzsql
CREATE TABLE mytable (a int, b text NOT NULL);

```

Once a user-populated table is created, you can perform CRUD
(Create/Read/Update/Delete) operations on it.

The following example uses [`INSERT`](/sql/insert/) to write two rows to the table:
```mzsql
INSERT INTO mytable VALUES
(1, 'hello'),
(2, 'goodbye')
;

```

The following example uses [`SELECT`](/sql/select/) to read all rows from the table:
```mzsql
SELECT * FROM mytable;

```The results should display the two rows inserted:

```hc {hl_lines="3-4"}
| a | b       |
| - | ------- |
| 1 | hello   |
| 2 | goodbye |
```

## Related pages

- [`INSERT`](/sql/insert/)
- [`DROP TABLE`](/sql/drop-table)

<!-- mz-docs page: sql/create-type -->

# CREATE TYPE
`CREATE TYPE` defines a new data type.
`CREATE TYPE` defines a custom data type, which let you create named versions of
anonymous types or provide a shorthand for other types. For more information,
see [SQL Data Types: Custom types](../types/#custom-types).

## Syntax

**Row type:**

```mzsql
CREATE TYPE <type_name> AS (<field_name> <field_type>, ...);

```

| Syntax element | Description |
| --- | --- |
| `<type_name>` | A name for the type.  |
| `<field_name>` | The name of a field in a row type.  |
| `<field_type>` | The data type of a field indicated by `field_name`.  |

**List type:**

```mzsql
CREATE TYPE <type_name> AS LIST (ELEMENT TYPE = <element_type>);

```

| Syntax element | Description |
| --- | --- |
| `<type_name>` | A name for the type.  |
| `<element_type>` | Creates a custom [`list`](/sql/types/list) whose elements are of `<element_type>`.  |

**Map type:**

```mzsql
CREATE TYPE <type_name> AS MAP (KEY TYPE = <key_type>, VALUE TYPE = <value_type>);

```

| Syntax element | Description |
| --- | --- |
| `<type_name>` | A name for the type.  |
| `<key_type>` | Creates a custom [`map`](/sql/types/map) whose keys are of `<key_type>`. Must resolve to [`text`](/sql/types/text).  |
| `<value_type>` | Creates a custom [`map`](/sql/types/map) whose values are of `<value_type>`.  |

## Details

For details about the custom types `CREATE TYPE` creates, see [SQL Data Types:
Custom types](../types/#custom-types).

### Properties

All custom type properties' values must refer to [named types](/sql/types), e.g.
`integer`.

To create a custom nested `list` or `map`, you must first create a custom `list`
or `map`. This creates a named type, which can then be referred to in another
custom type's properties.

## Examples

### Custom `list`

```mzsql
CREATE TYPE int4_list AS LIST (ELEMENT TYPE = int4);

SELECT '{1,2}'::int4_list::text AS custom_list;
```
```
 custom_list
-------------
 {1,2}
```

### Nested custom `list`

```mzsql
CREATE TYPE int4_list_list AS LIST (ELEMENT TYPE = int4_list);

SELECT '{{1,2}}'::int4_list_list::text AS custom_nested_list;
```
```
 custom_nested_list
--------------------
 {{1,2}}
```

### Custom `map`

```mzsql
CREATE TYPE int4_map AS MAP (KEY TYPE = text, VALUE TYPE = int4);

SELECT '{a=>1}'::int4_map::text AS custom_map;
```
```
 custom_map
------------
 {a=>1}
```

### Nested custom `map`

```mzsql
CREATE TYPE int4_map_map AS MAP (KEY TYPE = text, VALUE TYPE = int4_map);

SELECT '{a=>{a=>1}}'::int4_map_map::text AS custom_nested_map;
```
```
 custom_nested_map
-------------------
{a=>{a=>1}}
```

### Custom `row` type
```mzsql
CREATE TYPE row_type AS (a int, b text);
SELECT ROW(1, 'a')::row_type as custom_row_type;
```
```
custom_row_type
-----------------
(1,a)
```

### Nested `row` type
```mzsql
CREATE TYPE nested_row_type AS (a row_type, b float8);
SELECT ROW(ROW(1, 'a'), 2.3)::nested_row_type AS custom_nested_row_type;
```
```
custom_nested_row_type
------------------------
("(1,a)",2.3)
```

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the type definition.
- `USAGE` privileges on the schemas that all types in the statement are
  contained in.

## Related pages

* [`DROP TYPE`](../drop-type)
* [`SHOW TYPES`](../show-types)

<!-- mz-docs page: sql/create-view -->

# CREATE VIEW
`CREATE VIEW` defines view, which provides an alias for the embedded `SELECT` statement.
Use `CREATE VIEW` to define a view, which simply provides an alias for the
embedded `SELECT` statement. The results of a view can be incrementally
maintained **in memory** within a [cluster](/fundamentals/concepts/clusters/) by creating an
[index](../create-index). This allows you to serve queries without the overhead
of materializing the view.

## Syntax

**CREATE VIEW:**
To create a view:

```mzsql
CREATE [TEMP|TEMPORARY] VIEW [IF NOT EXISTS] <view_name>[(<col_ident>, ...)] AS
<select_stmt>;

```

| Syntax element | Description |
| --- | --- |
| `TEMP` / `TEMPORARY` | Optional. Mark the view as [temporary](/sql/create-view/#temporary-views). Temporary views are: - Created in the `mz_temp` schema. - Not visible to other connections. - Automatically dropped at the end of the SQL session  |
| `IF NOT EXISTS` | Optional. If specified, do not generate an error if a view with the same name already exists. If not specified, an error is generated if a view with the same name already exists.  |
| `<view_name>` | A name for the view.  |
| `(<col_ident>, ...)` | Optional if the `SELECT` statement return columns with unique names; else, is required if the `SELECT` statement returns multiple columns with the same identifier. If specified, renames the `SELECT` statement's columns to the list of identifiers. Both must be the same length.  |
| `<select_stmt>` | The [`SELECT` statement](/sql/select) that defines the view.  |

**CREATE OR REPLACE VIEW:**
To create, or if a view exists with the same name, replace it with the view
defined in this statement:

> **Note:** You cannot replace views that other views depend on,
> nor can you replace a non-view object with a view.

```mzsql
CREATE OR REPLACE VIEW <view_name> [(<col_ident>, ...)] AS <select_stmt>;

```

| Syntax element | Description |
| --- | --- |
| `<view_name>` | A name for the view.  |
| `(<col_ident>, ...)` | Optional if the `SELECT` statement return columns with unique names; else, is required if the `SELECT` statement returns multiple columns with the same identifier. If specified, renames the `SELECT` statement's columns to the list of identifiers. Both must be the same length.  |
| `<select_stmt>` | The [`SELECT` statement](/sql/select) that defines the view.  |

## Details

[//]: # "TODO(morsapaes) Add short usage patterns section + point to relevant
architecture patterns once these exist."

### Temporary views

The `TEMP`/`TEMPORARY` keyword creates a temporary view. Temporary views are
automatically dropped at the end of the SQL session and are not visible to other
connections. They are always created in the special `mz_temp` schema.

Temporary views may depend upon other temporary database objects, but non-temporary
views may not depend on temporary objects.

## Examples

### Creating a view

```mzsql
CREATE VIEW purchase_sum_by_region
AS
    SELECT sum(purchase.amount) AS region_sum,
           region.id AS region_id
    FROM region
    INNER JOIN user
        ON region.id = user.region_id
    INNER JOIN purchase
        ON purchase.user_id = user.id
    GROUP BY region.id;
```

## Privileges

The privileges required to execute this statement are:

- `CREATE` privileges on the containing schema.
- `USAGE` privileges on all types used in the view definition.
- `USAGE` privileges on the schemas for the types in the statement.
- Ownership of the existing view if replacing an existing
  view with the same name (i.e., `OR REPLACE` is specified in `CREATE VIEW` command).

## Additional information

- Views can be monotonic; that is, views can be recognized as append-only.

## Related pages

- [`SHOW VIEWS`](../show-views)
- [`SHOW CREATE VIEW`](../show-create-view)
- [`DROP VIEW`](../drop-view)
- [`CREATE MATERIALIZED VIEW`](../create-materialized-view)
- [`CREATE INDEX`](../create-index)

<!-- mz-docs page: sql/deallocate -->

# DEALLOCATE
`DEALLOCATE` clears a prepared statement.
`DEALLOCATE` clears [prepared statements](../prepare) that have been created during the current session. Even without an explicit `DEALLOCATE` command, all prepared statements will be cleared at the end of a session.

## Syntax

```mzsql
DEALLOCATE <name>|ALL ;
```

Syntax element | Description
---------------|------------
`<name>`  | The name of the prepared statement to clear.
**ALL**  |  Clear all prepared statements from this session.

## Example

```mzsql
DEALLOCATE a;
```

## Related pages

- [`PREPARE`]
- [`EXECUTE`]

[`PREPARE`]:../prepare
[`EXECUTE`]:../execute

<!-- mz-docs page: sql/declare -->

# DECLARE
`DECLARE` creates a cursor.
`DECLARE` creates a cursor, which can be used with
[`FETCH`](/sql/fetch), to retrieve a limited number of rows at a time
from a larger query. Large queries or queries that don't ever complete
([`SUBSCRIBE`](/sql/subscribe)) can be difficult to use with many PostgreSQL drivers
that wait until all rows are returned before returning control to an
application. Using `DECLARE` and [`FETCH`](/sql/fetch) allows you to
fetch only some of the rows at a time.

## Syntax

```mzsql
DECLARE <cursor_name> CURSOR FOR <query>;
```

Syntax element | Description
---------------|------------
`<cursor_name>` | The name of the cursor to be created.
`<query>` | The query ([`SELECT`](/sql/select) or [`SUBSCRIBE`](/sql/subscribe)) that will provide the rows to be returned by the cursor.

<!-- mz-docs page: sql/delete -->

# DELETE
`DELETE` removes values stored in tables.
`DELETE` removes values stored in [user-created tables](../create-table).

## Syntax

```mzsql
DELETE FROM <table_name> [AS <alias>]
[USING <from_item> [, ...]]
[WHERE <condition>]
;
```

Syntax element | Description
---------------|------------
`<table_name>` | The table whose values you want to remove.
**AS** `<alias>` | Optional. The alias for the table. If specified, only permit references to `<table_name>` as `<alias>`.
**USING** _from_item_ | Optional. Table expressions whose columns you want to reference in the `WHERE` clause. This supports the same syntax as the **FROM** clause in [`SELECT`](../select) statements, e.g. supporting aliases.
**WHERE** `<condition>` | Optional. Only remove rows which evaluate to `true` for _condition_.

## Details

### Known limitations

* `DELETE` cannot be used inside [transactions](../begin).
* `DELETE` can reference [read-write tables](../create-table) but not
  [sources](../create-source) or read-only tables.
* **Low performance.** While processing a `DELETE` statement, Materialize cannot
  process other `INSERT`, `UPDATE`, or `DELETE` statements.

## Examples

```mzsql
CREATE TABLE delete_me (a int, b text);
INSERT INTO delete_me
    VALUES
    (1, 'hello'),
    (2, 'goodbye'),
    (3, 'ok');
DELETE FROM delete_me WHERE b = 'hello';
SELECT * FROM delete_me ORDER BY a;
```
```
 a |    b
---+---------
 2 | goodbye
 3 | ok
```
```mzsql
CREATE TABLE delete_using (b text);
INSERT INTO delete_using VALUES ('goodbye'), ('ciao');
DELETE FROM delete_me
    USING delete_using
    WHERE delete_me.b = delete_using.b;
SELECT * FROM delete_me;
```
```
 a | b
---+----
 3 | ok
```
```mzsql
DELETE FROM delete_me;
SELECT * FROM delete_me;
```
```
 a | b
---+---
```

## Privileges

The privileges required to execute this statement are:

- `USAGE` privileges on the schemas that all relations and types in the query are contained in.
- `DELETE` privileges on `table_name`.
- `SELECT` privileges on all relations in the query.
  - NOTE: if any item is a view, then the view owner must also have the necessary privileges to
    execute the view definition. Even if the view owner is a _superuser_, they still must explicitly be
    granted the necessary privileges.
- `USAGE` privileges on all types used in the query.
- `USAGE` privileges on the active cluster.

## Related pages

- [`CREATE TABLE`](../create-table)
- [`INSERT`](../insert)
- [`SELECT`](../select)

<!-- mz-docs page: sql/discard -->

# DISCARD
Discard resets state associated with the current session.
`DISCARD` resets state associated with the current session.

## Syntax

```mzsql
DISCARD TEMP|TEMPORARY|ALL ;
```

Syntax element | Description
---------------|------------
**TEMP**  | Drops any temporary objects created by the current session.
**TEMPORARY** | Alias for `TEMP`.
**ALL** | Drops any temporary objects, deallocates any extant prepared statements, and closes any extant cursors that were created by the current session.

<!-- mz-docs page: sql/drop-cluster -->

# DROP CLUSTER
`DROP CLUSTER` removes an existing cluster from Materialize.
`DROP CLUSTER` removes an existing cluster from Materialize. If there are indexes or materialized views depending on the cluster, you must explicitly drop them first, or use the `CASCADE` option.

## Syntax

```mzsql
DROP CLUSTER [IF EXISTS] <cluster_name> [CASCADE|RESTRICT];
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional.  If specified, do not return an error if the specified cluster does not exist.
`<cluster_name>` | The cluster you want to drop. For available clusters, see [`SHOW CLUSTERS`](../show-clusters).
**CASCADE** | Optional. If specified, remove the cluster and its dependent objects.
**RESTRICT** | Optional. Do not drop the cluster if it has dependencies. _(Default)_

## Examples

### Dropping a cluster with no dependencies

To drop an existing cluster, run:

```mzsql
DROP CLUSTER auction_house;
```

To avoid issuing an error if the specified cluster does not exist, use the `IF EXISTS` option:

```mzsql
DROP CLUSTER IF EXISTS auction_house;
```

### Dropping a cluster with dependencies

If the cluster has dependencies, Materialize will throw an error similar to:

```mzsql
DROP CLUSTER auction_house;
```

```nofmt
ERROR:  cannot drop cluster with active indexes or materialized views
```

, and you'll have to explicitly ask to also remove any dependent objects using the `CASCADE` option:

```mzsql
DROP CLUSTER auction_house CASCADE;
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped cluster.

## Related pages

- [`SHOW CLUSTERS`](../show-clusters)
- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-cluster-replica -->

# DROP CLUSTER REPLICA
`DROP CLUSTER REPLICA` removes an existing replica for the specified cluster.
`DROP CLUSTER REPLICA` deprovisions an existing replica of the specified
[unmanaged cluster](/sql/create-cluster/#unmanaged-clusters). To remove
the cluster itself, use the [`DROP CLUSTER`](/sql/drop-cluster) command.

> **Tip:** When getting started with Materialize, we recommend starting with managed
> clusters.

## Syntax

```mzsql
DROP CLUSTER REPLICA [IF EXISTS] <cluster_name>.<replica_name>;
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the specified cluster replica does not exist.
`<cluster_name>` | The cluster you want to remove a replica from. For available clusters, see [`SHOW CLUSTERS`](../show-clusters).
`<replica_name>` | The cluster replica you want to drop. For available cluster replicas, see [`SHOW CLUSTER REPLICAS`](../show-cluster-replicas).

## Examples

```mzsql
SHOW CLUSTER REPLICAS WHERE cluster = 'auction_house';
```

```nofmt
    cluster    | replica
---------------+---------
 auction_house | bigger
```

```mzsql
DROP CLUSTER REPLICA auction_house.bigger;
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped cluster replica.
- `USAGE` privileges on the containing cluster.

## Related pages

- [`CREATE CLUSTER REPLICA`](../create-cluster-replica)
- [`SHOW CLUSTER REPLICAS`](../show-cluster-replicas)
- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-connection -->

# DROP CONNECTION
`DROP CONNECTION` removes a connection from Materialize.
`DROP CONNECTION` removes a connection from Materialize. If there are sources
depending on the connection, you must explicitly drop them first, or use the
`CASCADE` option.

## Syntax

```mzsql
DROP CONNECTION [IF EXISTS] <connection_name> [CASCADE|RESTRICT];
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the specified connection does not exist.
`connection_name>` | The connection you want to drop. For available connections, see [`SHOW CONNECTIONS`](../show-connections).
**CASCADE** | Optional. If specified, remove the connection and its dependent objects.
**RESTRICT** | Optional. Do not drop the connection if it has dependencies. _(Default)_

## Examples

### Dropping a connection with no dependencies

To drop an existing connection, run:

```mzsql
DROP CONNECTION kafka_connection;
```

To avoid issuing an error if the specified connection does not exist, use the `IF EXISTS` option:

```mzsql
DROP CONNECTION IF EXISTS kafka_connection;
```

### Dropping a connection with dependencies

If the connection has dependencies, Materialize will throw an error similar to:

```mzsql
DROP CONNECTION kafka_connection;
```

```nofmt
ERROR:  cannot drop materialize.public.kafka_connection: still depended upon by catalog item
'materialize.public.kafka_source'
```

, and you'll have to explicitly ask to also remove any dependent objects using the `CASCADE` option:

```mzsql
DROP CONNECTION kafka_connection CASCADE;
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped connection.
- `USAGE` privileges on the containing schema.

## Related pages

- [`SHOW CONNECTIONS`](../show-connections)
- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-database -->

# DROP DATABASE
`DROP DATABASE` removes a database from Materialize.
`DROP DATABASE` removes a database from Materialize.

> **Warning:** `DROP DATABASE` immediately removes all objects within the
> database without confirmation. Use with care!

## Syntax

```mzsql
DROP DATABASE [IF EXISTS] <database_name> [CASCADE|RESTRICT];
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional.  If specified, do not return an error if the specified database does not exist.
`<database_name>` | The database you want to drop. For available databases, see [`SHOW DATABASES`](../show-databases).
**CASCADE** | Optional. Remove the database and its dependent objects. _(Default)_
**RESTRICT** | Optional. If specified, do not remove this database if it contains any schemas.

## Example

### Remove a database containing schemas
You can use either of the following commands:

- ```mzsql
  DROP DATABASE my_db;
  ```
- ```mzsql
  DROP DATABASE my_db CASCADE;
  ```

### Remove a database only if it contains no schemas
```mzsql
DROP DATABASE my_db RESTRICT;
```

### Do not issue an error if attempting to remove a nonexistent database
```mzsql
DROP DATABASE IF EXISTS my_db;
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped database.

## Related pages

- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-index -->

# DROP INDEX
DROP INDEX removes an index
`DROP INDEX` removes an index from Materialize.

## Syntax

```mzsql
DROP INDEX [IF EXISTS] <index_name> [CASCADE|RESTRICT];
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the specified index does not exist.
`<index_name>` | Index to drop.
**CASCADE** | Optional. If specified, remove the index and its dependent objects.
**RESTRICT** | Optional. Remove the index. _(Default.)_

> **Note:** Since indexes do not have dependent objects, `DROP INDEX`, `DROP INDEX
> RESTRICT`, and `DROP INDEX CASCADE` are equivalent.

## Privileges

To execute the `DROP INDEX` statement, you need:

- Ownership of the dropped index.
- `USAGE` privileges on the containing schema.

## Examples

### Remove an index

> **Tip:** In the **Materialize Console**, you can view existing indexes in the [**Database
> object explorer**](/developer-tools/console/data/). Alternatively, you can use the
> [`SHOW INDEXES`](/sql/show-indexes) command.

Using the  `DROP INDEX` commands, the following example drops an index named `q01_geo_idx`.

```mzsql
DROP INDEX q01_geo_idx;
```

If the index `q01_geo_idx` does not exist, the above operation returns an error.

### Remove an index without erroring if the index does not exist

You can specify the `IF EXISTS` option so that the `DROP INDEX` command does
not return an error if the index to drop does not exist.

```mzsql
DROP INDEX IF EXISTS q01_geo_idx;
```

## Related pages

- [`CREATE INDEX`](/sql/create-index)
- [`SHOW VIEWS`](/sql/show-views)
- [`SHOW INDEXES`](/sql/show-indexes)
- [`DROP OWNED`](/sql/drop-owned)

<!-- mz-docs page: sql/drop-materialized-view -->

# DROP MATERIALIZED VIEW
`DROP MATERIALIZED VIEW` removes a materialized view from Materialize.
`DROP MATERIALIZED VIEW` removes a materialized view from Materialize. If there
are other views depending on the materialized view, you must explicitly drop
them first, or use the `CASCADE` option.

## Syntax

```mzsql
DROP MATERIALIZED VIEW [IF EXISTS] <view_name> [RESTRICT|CASCADE];
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the named materialized view does not exist.
`<view_name>` | The materialized view you want to drop. For available materialized views, see [`SHOW MATERIALIZED VIEWS`](../show-materialized-views).
**RESTRICT** | Optional. Do not drop this materialized view if any other views depend on it. _(Default)_
**CASCADE** | Optional. If specified, drop the materialized view and all views that depend on this materialized view.

## Examples

### Dropping a materialized view with no dependencies

```mzsql
DROP MATERIALIZED VIEW winning_bids;
```
```nofmt
DROP MATERIALIZED VIEW
```

### Dropping a materialized view with dependencies

```mzsql
DROP MATERIALIZED VIEW winning_bids;
```

```nofmt
ERROR:  cannot drop materialize.public.winning_bids: still depended
upon by catalog item 'materialize.public.wb_custom_art'
```

## Privileges

The privileges required to execute this statement are:

- Ownership of the dropped materialized view.
- `USAGE` privileges on the containing schema.

## Related pages

- [`CREATE MATERIALIZED VIEW`](../create-materialized-view)
- [`SHOW MATERIALIZED VIEWS`](../show-materialized-views)
- [`SHOW CREATE MATERIALIZED VIEW`](../show-create-materialized-view)
- [`DROP OWNED`](../drop-owned)

<!-- mz-docs page: sql/drop-network-policy -->

# DROP NETWORK POLICY (Cloud)
`DROP NETWORK POLICY` removes an existing network policy from Materialize.
*Available for Materialize Cloud only*

`DROP NETWORK POLICY` removes an existing network policy from Materialize.
Network policies are part of Materialize's framework for [access control](/security/cloud/).

To alter the rules in a network policy, use the [`ALTER NETWORK POLICY`](../alter-network-policy)
command.

## Syntax

```mzsql
DROP NETWORK POLICY [IF EXISTS] <name>;
```

Syntax element | Description
---------------|------------
**IF EXISTS** | Optional. If specified, do not return an error if the specified network policy does not exist.
`<name>`        | The network policy you want to drop. For available network policies, see [`SHOW NETWORK POLICIES`](../show-network-policies).

## Privileges

The privileges required to execute this statement are:

- `CREATENETWORKPOLICY` privileges on the system.

## Related pages

- [`SHOW NETWORK POLICIES`](../show-network-policies)
- [`ALTER NETWORK POLICY`](../alter-network-policy)
- [`CREATE NETWORK POLICY`](../create-network-policy)

