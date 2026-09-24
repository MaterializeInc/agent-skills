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
| **WITH** (`<with_option>` [, ...]) | Optional. The following `<with_option>`s are supported:  \| Option \| Description \| \|--------\|-------------\| \| `RETAIN HISTORY FOR <retention_period>` \| ***Private preview.** This option has known performance or stability issues and is under active development.* Duration for which Materialize retains historical data, which is useful to implement [durable subscriptions](/transform-data/patterns/durable-subscriptions/#history-retention-period). Accepts positive [interval](/sql/types/interval/) values (e.g. `'1hr'`). Default: `1s`. \| \| `TIMESTAMP INTERVAL [=] <interval>` \| The interval at which timestamps are assigned to data read from this source. Accepts positive [interval](/sql/types/interval/) values (e.g. `'500ms'`, `'1s'`). The value must be between the system parameters `min_timestamp_interval` and `max_timestamp_interval`. Default: the value of the `default_timestamp_interval` system parameter (`1s`). The interval can also be changed after creation with [`ALTER SOURCE`](/sql/alter-source/). \|  |

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

### Timestamp Rounding

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

### Modifying an existing source

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

### Table-level operations

The following upstream operations put the affected table into an error state.
Ingestion for that table stops, and you must drop and recreate the affected
table in Materialize to resume:

- Dropping a table (`DROP TABLE`).
- Renaming a table or moving it to a different schema.

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
